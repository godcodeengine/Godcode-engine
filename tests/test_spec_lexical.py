"""Spec tests for the lexical layer (docs/spec/lexical.md).

Each test keeps one LX rule honest: if the engine's lexing changes, the
failing test names the rule that broke. Tests are grouped by the rule
they guard; the rule number sits in every docstring.
"""

import pytest

from godcode.errors import LexerError
from godcode.lexer import KEYWORDS, Lexer
from godcode.tokens import TokenType


def lex(source, **kwargs):
    return Lexer(source, **kwargs).lex()


def types(source, **kwargs):
    return [t.type for t in lex(source, **kwargs)]


def values(source, **kwargs):
    return [t.value for t in lex(source, **kwargs)]


# -- LX-1: source text and lines ---------------------------------------------

def test_lx1_token_stream_ends_with_exactly_one_eof():
    """LX-1: the token list always ends with exactly one EOF token."""
    for src in ("", "REVEAL 1", "\n\n\n", "# only a comment"):
        toks = lex(src)
        assert toks[-1].type is TokenType.EOF
        assert sum(1 for t in toks if t.type is TokenType.EOF) == 1


def test_lx2_line_breaks_become_newline_tokens():
    """LX-2: every line break becomes one NEWLINE token."""
    assert types("REVEAL 1\nREVEAL 2") == [
        TokenType.REVEAL, TokenType.NUMBER, TokenType.NEWLINE,
        TokenType.REVEAL, TokenType.NUMBER, TokenType.EOF,
    ]


def test_lx2_crlf_collapses_to_one_newline():
    """LX-2: a CRLF pair collapses to a single NEWLINE."""
    assert types("REVEAL 1\r\nREVEAL 2") == [
        TokenType.REVEAL, TokenType.NUMBER, TokenType.NEWLINE,
        TokenType.REVEAL, TokenType.NUMBER, TokenType.EOF,
    ]


def test_lx2_lone_cr_becomes_one_newline():
    """LX-2: a lone CR is tolerated and becomes one NEWLINE."""
    assert types("REVEAL 1\rREVEAL 2") == [
        TokenType.REVEAL, TokenType.NUMBER, TokenType.NEWLINE,
        TokenType.REVEAL, TokenType.NUMBER, TokenType.EOF,
    ]


def test_lx2_trailing_newline_is_lexed():
    """LX-2: a trailing line break still becomes a NEWLINE before EOF."""
    assert types("REVEAL 1\n") == [
        TokenType.REVEAL, TokenType.NUMBER, TokenType.NEWLINE, TokenType.EOF,
    ]


# -- LX-3: whitespace ----------------------------------------------------------

def test_lx3_spaces_and_tabs_are_ignored():
    """LX-3: spaces and tabs separate tokens and become nothing."""
    assert types("REVEAL \t  1") == [TokenType.REVEAL, TokenType.NUMBER, TokenType.EOF]


# -- LX-4, LX-5: comments -------------------------------------------------------

def test_lx4_comment_runs_to_end_of_line():
    """LX-4: a comment ends at the line break, which is still lexed."""
    assert types("REVEAL 1 # bless the line\nREVEAL 2") == [
        TokenType.REVEAL, TokenType.NUMBER, TokenType.NEWLINE,
        TokenType.REVEAL, TokenType.NUMBER, TokenType.EOF,
    ]


def test_lx5_hash_inside_string_is_a_character():
    """LX-5: a # inside a double-quoted string is not a comment."""
    toks = lex('"psalm #23"')
    assert toks[0].type is TokenType.STRING
    assert toks[0].value == "psalm #23"
    assert toks[1].type is TokenType.EOF


# -- LX-6, LX-7: keywords --------------------------------------------------------

def test_lx6_keywords_are_case_insensitive_with_upper_canonical():
    """LX-6: any letter case lexes as the keyword; the token carries UPPER."""
    for spelling in ("declare", "Declare", "DECLARE", "dEcLaRe"):
        toks = lex(f"{spelling} x AS 1")
        assert toks[0].type is TokenType.DECLARE
        assert toks[0].value == "DECLARE"


def test_lx7_keyword_inventory_matches_the_spec_list():
    """LX-7: the lexer's keyword set is exactly the documented list."""
    documented = {
        "BEGIN", "CREATION", "END", "DECLARE", "AS", "BREATHE", "LIFE", "INTO",
        "REVEAL", "PROPHESY", "ASCEND", "IF", "THEN", "ELSE", "ENDIF", "FOR",
        "IN", "ENDFOR", "WHILE", "DO", "ENDWHILE", "BREAK", "CONTINUE", "TRY",
        "CATCH", "ENDTRY", "DEFINE", "RITE", "INVOKE", "RETURN", "IMPORT",
        "IS", "NOT", "AND", "OR", "REFLECT", "BLESS", "ANOINT", "SEAL",
        "TESTIFY", "TRUE", "FALSE", "VOID",
    }
    assert set(KEYWORDS) == documented


def test_lx7_multiword_phrases_are_separate_tokens():
    """LX-7: BEGIN CREATION and BREATHE LIFE INTO are separate keyword tokens."""
    assert types("BEGIN CREATION") == [TokenType.BEGIN, TokenType.CREATION, TokenType.EOF]
    assert types("BREATHE LIFE INTO x") == [
        TokenType.BREATHE, TokenType.LIFE, TokenType.INTO,
        TokenType.IDENT, TokenType.EOF,
    ]


def test_lx7_true_false_void_are_keywords():
    """LX-7: TRUE, FALSE, VOID are keywords, in any letter case."""
    assert types("true FALSE Void") == [
        TokenType.TRUE, TokenType.FALSE, TokenType.VOID, TokenType.EOF,
    ]


# -- LX-8, LX-9: identifiers -----------------------------------------------------

def test_lx8_identifier_shapes():
    """LX-8: names start with a letter or underscore, keep their casing."""
    toks = lex("seeker _x9 psalm23")
    assert [t.type for t in toks] == [
        TokenType.IDENT, TokenType.IDENT, TokenType.IDENT, TokenType.EOF,
    ]
    assert [t.value for t in toks[:3]] == ["seeker", "_x9", "psalm23"]


def test_lx9_identifiers_are_case_sensitive():
    """LX-9: seeker and Seeker are two different names."""
    toks = lex("seeker Seeker")
    assert toks[0].type is TokenType.IDENT and toks[1].type is TokenType.IDENT
    assert toks[0].value == "seeker"
    assert toks[1].value == "Seeker"


def test_lx8_unicode_letters_form_identifiers():
    """LX-8: as implemented, unicode letters are accepted in names."""
    toks = lex("θ")
    assert toks[0].type is TokenType.IDENT
    assert toks[0].value == "θ"


# -- LX-10 through LX-14: numbers -------------------------------------------------

def test_lx10_integers_and_floats():
    """LX-10: ints, leading zeros, and floats lex as numbers."""
    assert values("3")[0] == 3
    assert values("007")[0] == 7
    assert values("4.5")[0] == 4.5


def test_lx11_decimal_point_needs_digits():
    """LX-11: 5. is rejected, saying digits must follow the point."""
    with pytest.raises(LexerError, match="must be followed by digits"):
        lex("5.")


def test_lx12_no_scientific_or_leading_dot():
    """LX-12: 1e5 splits; .5 is rejected because . is not a character."""
    toks = lex("1e5")
    assert (toks[0].type, toks[0].value) == (TokenType.NUMBER, 1)
    assert (toks[1].type, toks[1].value) == (TokenType.IDENT, "e5")
    with pytest.raises(LexerError, match="do not recognize the character"):
        lex(".5")


def test_lx13_number_adjacent_to_word_splits():
    """LX-13: 12abc is the number 12 followed by the name abc."""
    toks = lex("12abc")
    assert (toks[0].type, toks[0].value) == (TokenType.NUMBER, 12)
    assert (toks[1].type, toks[1].value) == (TokenType.IDENT, "abc")


def test_lx14_negative_is_minus_plus_number():
    """LX-14: -5 is the minus operator followed by the number 5."""
    assert types("-5") == [TokenType.MINUS, TokenType.NUMBER, TokenType.EOF]


# -- LX-15 through LX-19: strings ---------------------------------------------------

def test_lx15_string_value_is_unescaped():
    """LX-15: the STRING token's value is the unescaped text."""
    toks = lex('"a\\nb"')
    assert toks[0].type is TokenType.STRING
    assert toks[0].value == "a\nb"


def test_lx16_all_four_escapes():
    """LX-16: the four escapes resolve; anything else is an error."""
    toks = lex(r'"\"\n\t\\"')
    assert toks[0].value == '"\n\t\\'
    with pytest.raises(LexerError, match="Unknown escape"):
        lex('"bad \\q escape"')


def test_lx17_string_cannot_span_lines():
    """LX-17: a newline inside a string names the opening line and column."""
    with pytest.raises(LexerError) as excinfo:
        lex('"abc\ndef"')
    assert "runs past the end of the line" in str(excinfo.value)
    assert excinfo.value.line == 1 and excinfo.value.col == 1
    with pytest.raises(LexerError, match="runs past the end of the line"):
        lex('"abc\rdef"')


def test_lx18_unterminated_string_names_the_opening_quote():
    """LX-18: a string never closed names the opening line and column."""
    with pytest.raises(LexerError) as excinfo:
        lex('"unterminated')
    assert "unterminated string" in str(excinfo.value)
    assert excinfo.value.line == 1 and excinfo.value.col == 1


def test_lx19_braces_inside_strings_are_ordinary():
    """LX-19: {name} inside a string is just characters in one STRING token."""
    toks = lex('"grace upon {name}"')
    assert toks[0].type is TokenType.STRING
    assert toks[0].value == "grace upon {name}"
    assert toks[1].type is TokenType.EOF


# -- LX-20 through LX-22: operators, punctuation, unknown characters -----------------

def test_lx20_operator_table():
    """LX-20: every operator lexes to its token; = and == both mean EQ."""
    cases = {
        "+": TokenType.PLUS, "-": TokenType.MINUS, "*": TokenType.STAR,
        "/": TokenType.SLASH, "%": TokenType.PERCENT, "=": TokenType.EQ,
        "==": TokenType.EQ, "!=": TokenType.NEQ, "<": TokenType.LT,
        ">": TokenType.GT, "<=": TokenType.LTE, ">=": TokenType.GTE,
    }
    for spelling, expected in cases.items():
        toks = lex(f"a {spelling} b")
        assert toks[1].type is expected, spelling
        assert toks[1].value == spelling


def test_lx20_multi_char_operators_win():
    """LX-20: <= is one token, never < followed by =."""
    assert types("a<=b") == [
        TokenType.IDENT, TokenType.LTE, TokenType.IDENT, TokenType.EOF,
    ]


def test_lx21_punctuation():
    """LX-21: parens, brackets, and commas are each their own token."""
    assert types("(x)") == [TokenType.LPAREN, TokenType.IDENT, TokenType.RPAREN, TokenType.EOF]
    assert types("[1, 2]") == [
        TokenType.LBRACKET, TokenType.NUMBER, TokenType.COMMA,
        TokenType.NUMBER, TokenType.RBRACKET, TokenType.EOF,
    ]


def test_lx22_unknown_character_is_named():
    """LX-22: an unknown character is a lexer error naming it and its place."""
    with pytest.raises(LexerError) as excinfo:
        lex("REVEAL @")
    assert "'@'" in str(excinfo.value)
    assert excinfo.value.line == 1 and excinfo.value.col == 8


def test_lx22_braces_outside_strings_are_not_tokens():
    """LX-22: braces only live inside strings; outside they are unknown."""
    with pytest.raises(LexerError, match="do not recognize the character"):
        lex("{name}")


# -- LX-23 through LX-28: tongues at the lexical layer ---------------------------------

def test_lx23_pragma_found_anywhere_in_source():
    """LX-23: a pragma on a later line still sets the tongue for line 1."""
    toks = lex("REVEAL 1\n# tongue: tn\nSENOLA 2")
    revealed = [t for t in toks if t.type is TokenType.REVEAL]
    assert len(revealed) == 2


def test_lx23_pragma_shape_is_forgiving():
    """LX-23: spacing and case around the pragma are forgiving."""
    assert types("#TONGUE:tn\nSENOLA 1")[1] is TokenType.REVEAL
    assert types("#  tongue :  tn  \nSENOLA 1")[1] is TokenType.REVEAL


def test_lx23_pragma_with_trailing_words_is_not_a_pragma():
    """LX-23: the pragma must be the whole comment, or it is ignored."""
    assert types("# tongue: tn extra\nSENOLA 1")[1] is TokenType.IDENT


def test_lx24_explicit_tongue_wins_over_pragma():
    """LX-24: an explicit tongue choice beats the pragma."""
    assert types("# tongue: tn\nSENOLA 1", tongue="en")[1] is TokenType.IDENT
    toks = lex("# tongue: tn\nSENOLA 1")
    assert toks[1].type is TokenType.REVEAL
    assert Lexer("# tongue: tn\nSENOLA 1").tongue == "tn"


def test_lx25_tongue_words_map_to_keyword_tokens_case_insensitively():
    """LX-25: SENOLA and senola both become the REVEAL token."""
    for spelling in ("SENOLA", "senola", "Senola"):
        toks = lex(f"# tongue: tn\n{spelling} 1")
        assert toks[1].type is TokenType.REVEAL
        assert toks[1].value == "REVEAL"


def test_lx26_two_word_closer_needs_one_line():
    """LX-26: FEDISA FA on one line is a single ENDIF; split, they are two."""
    toks = lex("# tongue: tn\nFEDISA FA")
    endif = [t for t in toks if t.type is TokenType.ENDIF]
    assert len(endif) == 1
    assert (endif[0].line, endif[0].col) == (2, 1)
    assert types("# tongue: tn\nFEDISA\nFA") == [
        TokenType.NEWLINE, TokenType.END, TokenType.NEWLINE,
        TokenType.IF, TokenType.EOF,
    ]


def test_lx27_unknown_tongue_is_gentle_and_lists_tongues():
    """LX-27: an unknown tongue names the code and lists the spoken tongues."""
    with pytest.raises(LexerError) as excinfo:
        lex("# tongue: xx\nREVEAL 1")
    message = str(excinfo.value)
    assert "'xx'" in message
    assert "tn" in message and "zu" in message


def test_lx28_named_tools_keep_their_names():
    """LX-28: SHA256 and UPPER are identifiers in every tongue."""
    assert types("# tongue: tn\nSHA256 UPPER") == [
        TokenType.NEWLINE, TokenType.IDENT, TokenType.IDENT, TokenType.EOF,
    ]


# -- LX-29: positions ------------------------------------------------------------------

def test_lx29_positions_are_one_based():
    """LX-29: token positions are 1-based; errors name the trouble's start."""
    toks = lex("  REVEAL")
    assert (toks[0].line, toks[0].col) == (1, 3)
    toks = lex("REVEAL 1\n  REVEAL 2")
    assert (toks[3].line, toks[3].col) == (2, 3)
