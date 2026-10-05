"""Spec tests for the syntax layer (docs/spec/syntax.md).

Each test keeps one SX rule honest: if the engine's parsing changes, the
failing test names the rule that broke. Tests are grouped by the rule
they guard; the rule number sits in every docstring.
"""

import pytest

from godcode import ast as A
from godcode.errors import ParseError
from godcode.tongues import parse_source


def parse(source):
    return parse_source(source)


def stmts(source):
    """Top-level statements of a parsed scroll."""
    return parse(source).statements


def creation_stmts(body):
    """Statements inside the scroll's single creation block (body is wrapped)."""
    prog = parse(wrap(body))
    assert len(prog.statements) == 1
    assert isinstance(prog.statements[0], A.CreationBlock)
    return prog.statements[0].statements


def wrap(body):
    return "BEGIN CREATION\n" + body + "\nEND CREATION"


# -- SX-1: the shape of a scroll ------------------------------------------------

def test_sx1_creation_block_parses_to_program_with_one_creation():
    """SX-1: BEGIN CREATION ... END CREATION parses to a Program holding one CreationBlock."""
    prog = parse(wrap('REVEAL("blessed")'))
    assert isinstance(prog, A.Program)
    assert len(prog.statements) == 1
    block = prog.statements[0]
    assert isinstance(block, A.CreationBlock)
    assert len(block.statements) == 1
    assert isinstance(block.statements[0], A.Reveal)


def test_sx1_bare_sequence_parses_to_program_of_statements():
    """SX-1: a bare sequence of statements is also a Program (the fragment form)."""
    prog = parse('REVEAL(1)\nREVEAL(2)')
    assert isinstance(prog, A.Program)
    assert [type(s).__name__ for s in prog.statements] == ["Reveal", "Reveal"]


# -- SX-2: one creation per scroll ----------------------------------------------

def test_sx2_text_after_end_creation_is_rejected():
    """SX-2: a scroll holds only one creation; trailing decrees are rejected."""
    with pytest.raises(ParseError, match="one creation"):
        parse(wrap('REVEAL(1)') + '\nREVEAL(2)')


# -- SX-3: phrases stay on one line ----------------------------------------------

def test_sx3_end_and_creation_must_share_a_line():
    """SX-3: END and CREATION split across lines are rejected."""
    with pytest.raises(ParseError):
        parse("BEGIN CREATION\nREVEAL(1)\nEND\nCREATION")


def test_sx3_begin_and_creation_must_share_a_line():
    """SX-3: BEGIN and CREATION split across lines are rejected."""
    with pytest.raises(ParseError):
        parse("BEGIN\nCREATION\nREVEAL(1)\nEND CREATION")


def test_sx3_end_and_rite_must_share_a_line():
    """SX-3: END and RITE split across lines are rejected."""
    with pytest.raises(ParseError):
        parse(wrap("DEFINE RITE f()\nREVEAL(1)\nEND\nRITE"))


# -- SX-4: unclosed blocks name the missing closer --------------------------------

def test_sx4_unclosed_if_names_endif_and_opening_line():
    """SX-4: an unclosed block names the missing closer and the opening line."""
    with pytest.raises(ParseError, match="ENDIF"):
        parse(wrap("IF 1 IS 1 THEN\nREVEAL(1)"))


def test_sx4_unclosed_creation_names_end_creation():
    """SX-4: a scroll that ends inside the creation names END CREATION."""
    with pytest.raises(ParseError, match="END CREATION"):
        parse("BEGIN CREATION\nREVEAL(1)")


# -- SX-5: a wrong closer is named -------------------------------------------------

def test_sx5_end_creation_before_endif_is_rejected():
    """SX-5: END CREATION arriving where ENDIF was owed is rejected."""
    with pytest.raises(ParseError, match="before ENDIF"):
        parse("BEGIN CREATION\nIF 1 IS 1 THEN\nREVEAL(1)\nEND CREATION")


def test_sx5_end_rite_before_endwhile_is_rejected():
    """SX-5: END RITE arriving where ENDWHILE was owed is rejected."""
    with pytest.raises(ParseError, match="before ENDWHILE"):
        parse(wrap("DEFINE RITE f()\nWHILE 1 IS 2 DO\nREVEAL(1)\nEND RITE"))


# -- SX-6: stray closers ----------------------------------------------------------------

def test_sx6_lone_endif_is_rejected():
    """SX-6: a closer with no open block is rejected as an unexpected word."""
    with pytest.raises(ParseError, match="Unexpected"):
        parse("ENDIF")


def test_sx6_lone_endfor_is_rejected():
    """SX-6: a lone ENDFOR is rejected too."""
    with pytest.raises(ParseError, match="Unexpected"):
        parse(wrap("ENDFOR"))


# -- SX-7: line breaks separate statements ----------------------------------------------

def test_sx7_blank_lines_are_ignored():
    """SX-7: blank lines between statements change nothing."""
    assert len(creation_stmts("\n\nREVEAL(1)\n\n\nREVEAL(2)\n\n")) == 2


# -- SX-8: two statements may share a line -------------------------------------------------

def test_sx8_two_statements_on_one_line():
    """SX-8: two statements may share one line; both are kept."""
    prog = parse("REVEAL(1) REVEAL(2)")
    assert len(prog.statements) == 2
    assert all(isinstance(s, A.Reveal) for s in prog.statements)


# -- SX-9: emptiness is not an error ---------------------------------------------------------

def test_sx9_empty_scroll_is_a_program_with_no_statements():
    """SX-9: an empty scroll parses to a Program with no statements."""
    prog = parse("")
    assert isinstance(prog, A.Program)
    assert prog.statements == []


def test_sx9_empty_creation_is_allowed():
    """SX-9: BEGIN CREATION END CREATION is a creation with no works."""
    (block,) = stmts("BEGIN CREATION END CREATION")
    assert isinstance(block, A.CreationBlock)
    assert block.statements == []


# -- SX-10: DECLARE one name -------------------------------------------------------------------

def test_sx10_declare_binds_one_name_to_one_value():
    """SX-10: DECLARE name AS expr binds the name to the value."""
    (d,) = creation_stmts("DECLARE x AS 1 + 2")
    assert isinstance(d, A.Declare)
    assert d.name == "x"
    assert isinstance(d.value, A.BinaryOp)


def test_sx10_declare_needs_as():
    """SX-10: DECLARE without AS is rejected."""
    with pytest.raises(ParseError):
        parse(wrap("DECLARE x 5"))


def test_sx10_declare_needs_a_plain_name():
    """SX-10: DECLARE needs a plain identifier for the name."""
    with pytest.raises(ParseError):
        parse(wrap("DECLARE 1 AS 2"))


def test_sx10_declare_needs_a_value():
    """SX-10: DECLARE with nothing after AS is rejected."""
    with pytest.raises(ParseError):
        parse(wrap("DECLARE x AS"))


# -- SX-11: DECLARE a list -----------------------------------------------------------------------

def test_sx11_declare_many_values_binds_a_list():
    """SX-11: DECLARE name AS e1, e2, ... binds the name to a list, in order."""
    (d,) = creation_stmts("DECLARE x AS 1, 2, 3")
    assert isinstance(d, A.Declare)
    assert isinstance(d.value, A.ListLiteral)
    assert [i.value for i in d.value.items] == [1, 2, 3]


# -- SX-12: DECLARE INTENT -------------------------------------------------------------------------

def test_sx12_declare_intent_names_a_rite_purpose():
    """SX-12: DECLARE INTENT "words" ON rite_name declares a rite's purpose."""
    (d,) = creation_stmts('DECLARE INTENT "bring peace" ON evening_blessing')
    assert isinstance(d, A.DeclareIntent)
    assert d.text == "bring peace"
    assert d.rite == "evening_blessing"


def test_sx12_intent_is_a_soft_word():
    """SX-12: DECLARE intent AS 5 still declares an ordinary name."""
    (d,) = creation_stmts("DECLARE intent AS 5")
    assert isinstance(d, A.Declare)
    assert d.name == "intent"


# -- SX-13: REVEAL -----------------------------------------------------------------------------------

def test_sx13_reveal_carries_one_expression_in_parens():
    """SX-13: REVEAL(expr) carries exactly one expression."""
    (r,) = creation_stmts("REVEAL(1 + 2)")
    assert isinstance(r, A.Reveal)
    assert isinstance(r.expr, A.BinaryOp)


def test_sx13_reveal_without_parens_is_rejected():
    """SX-13: the parentheses are required."""
    with pytest.raises(ParseError):
        parse(wrap("REVEAL 1"))


def test_sx13_reveal_with_two_expressions_is_rejected():
    """SX-13: REVEAL takes exactly one expression."""
    with pytest.raises(ParseError):
        parse(wrap("REVEAL(1, 2)"))


# -- SX-14: SEAL and TESTIFY ---------------------------------------------------------------------------

def test_sx14_seal_takes_a_bare_expression():
    """SX-14: SEAL expr takes a bare expression."""
    (s,) = creation_stmts("SEAL x")
    assert isinstance(s, A.SealStmt)
    assert isinstance(s.expr, A.Identifier)


def test_sx14_seal_parens_are_grouping():
    """SX-14: SEAL(x) is the same decree as SEAL x."""
    (s,) = creation_stmts("SEAL(x)")
    assert isinstance(s, A.SealStmt)
    assert isinstance(s.expr, A.Identifier)


def test_sx14_testify_takes_a_bare_expression():
    """SX-14: TESTIFY expr takes a bare expression."""
    (t,) = creation_stmts("TESTIFY 1 + 1")
    assert isinstance(t, A.Testify)
    assert isinstance(t.expr, A.BinaryOp)


# -- SX-15: BLESS, ANOINT, BREATHE, ASCEND, REFLECT -----------------------------------------------------

def test_sx15_bless_and_anoint_take_one_name():
    """SX-15: BLESS name and ANOINT name take exactly one name."""
    b, a = creation_stmts("BLESS grace\nANOINT peace")
    assert isinstance(b, A.Bless) and b.name == "grace"
    assert isinstance(a, A.Anoint) and a.name == "peace"


def test_sx15_bless_without_a_name_is_rejected():
    """SX-15: BLESS with no name is rejected."""
    with pytest.raises(ParseError):
        parse(wrap("BLESS"))


def test_sx15_breathe_life_into_takes_one_name():
    """SX-15: BREATHE LIFE INTO name takes the three words and one name."""
    (b,) = creation_stmts("BREATHE LIFE INTO seeker")
    assert isinstance(b, A.Breathe)
    assert b.name == "seeker"


def test_sx15_ascend_and_reflect_stand_alone():
    """SX-15: ASCEND and REFLECT stand alone."""
    a, r = creation_stmts("ASCEND\nREFLECT")
    assert isinstance(a, A.Ascend)
    assert isinstance(r, A.Reflect)


# -- SX-16: PROPHESY -------------------------------------------------------------------------------------

def test_sx16_prophesy_takes_the_rest_of_the_line():
    """SX-16: PROPHESY takes the rest of the line as text, token values joined with spaces."""
    (p,) = creation_stmts("PROPHESY the lord is good, truly")
    assert isinstance(p, A.Prophesy)
    assert p.text == "the lord IS good , truly"


def test_sx16_empty_prophesy_is_empty_text():
    """SX-16: an empty PROPHESY line prophesies the empty text."""
    (p,) = creation_stmts("PROPHESY")
    assert p.text == ""


# -- SX-17: IF forms ----------------------------------------------------------------------------------------

def test_sx17_block_if_with_else():
    """SX-17: IF ... THEN on its own line opens a block closed by ENDIF, with an optional ELSE."""
    (i,) = creation_stmts("IF 1 IS 1 THEN\nREVEAL(1)\nELSE\nREVEAL(2)\nENDIF")
    assert isinstance(i, A.IfStmt)
    assert i.has_else is True
    assert len(i.then_body) == 1 and len(i.else_body) == 1


def test_sx17_inline_if():
    """SX-17: IF cond THEN stmt on one line is the short form."""
    (i,) = creation_stmts("IF 1 IS 1 THEN REVEAL(1)")
    assert isinstance(i, A.IfStmt)
    assert len(i.then_body) == 1
    assert i.has_else is False


def test_sx17_inline_if_else():
    """SX-17: IF cond THEN stmt ELSE stmt on one line carries both."""
    (i,) = creation_stmts("IF 1 IS 1 THEN REVEAL(1) ELSE REVEAL(2)")
    assert isinstance(i, A.IfStmt)
    assert i.has_else is True
    assert len(i.else_body) == 1


# -- SX-18: IF needs THEN and ENDIF ------------------------------------------------------------------------------

def test_sx18_if_needs_then():
    """SX-18: every IF needs its THEN."""
    with pytest.raises(ParseError, match="THEN"):
        parse(wrap("IF 1 IS 1\nREVEAL(1)\nENDIF"))


def test_sx18_block_if_needs_endif():
    """SX-18: a block IF needs its ENDIF."""
    with pytest.raises(ParseError, match="before ENDIF"):
        parse("BEGIN CREATION\nIF 1 IS 1 THEN\nREVEAL(1)\nEND CREATION")


# -- SX-19: FOR ------------------------------------------------------------------------------------------------------

def test_sx19_for_walks_a_gathering():
    """SX-19: FOR name IN expr walks each value; the block closes with ENDFOR."""
    (f,) = creation_stmts("FOR x IN [1, 2]\nREVEAL(x)\nENDFOR")
    assert isinstance(f, A.ForLoop)
    assert f.var == "x"
    assert len(f.body) == 1


def test_sx19_for_one_line_form():
    """SX-19: the one-line form carries a single statement."""
    (f,) = creation_stmts("FOR x IN [1, 2] REVEAL(x)")
    assert isinstance(f, A.ForLoop)
    assert len(f.body) == 1


def test_sx19_for_needs_a_plain_name():
    """SX-19: the traveler's name must be a plain identifier."""
    with pytest.raises(ParseError):
        parse(wrap("FOR 1 IN [2]\nENDFOR"))


# -- SX-20: WHILE ------------------------------------------------------------------------------------------------------

def test_sx20_while_repeats_until_the_condition_falls():
    """SX-20: WHILE cond DO ... ENDWHILE repeats while the condition holds."""
    (w,) = creation_stmts("WHILE 1 IS 2 DO\nREVEAL(1)\nENDWHILE")
    assert isinstance(w, A.WhileLoop)
    assert len(w.body) == 1


def test_sx20_while_one_line_form():
    """SX-20: the one-line form carries a single statement."""
    (w,) = creation_stmts("WHILE 1 IS 2 DO REVEAL(1)")
    assert isinstance(w, A.WhileLoop)


def test_sx20_while_closer_is_always_required():
    """SX-20: unlike FOR, WHILE is always closed with ENDWHILE."""
    with pytest.raises(ParseError, match="before ENDWHILE"):
        parse("BEGIN CREATION\nWHILE 1 IS 2 DO\nREVEAL(1)\nEND CREATION")


# -- SX-21: FOR keeps the old open form -------------------------------------------------------------------------------------

def test_sx21_for_may_end_open_at_end_creation():
    """SX-21: a FOR without ENDFOR ends where END CREATION arrives (the kept legacy form)."""
    prog = parse("BEGIN CREATION\nFOR x IN [1, 2]\nREVEAL(x)\nEND CREATION")
    (block,) = prog.statements
    assert isinstance(block, A.CreationBlock)
    (f,) = block.statements
    assert isinstance(f, A.ForLoop)
    assert len(f.body) == 1


# -- SX-22: BREAK and CONTINUE ----------------------------------------------------------------------------

def test_sx22_break_outside_a_loop_is_rejected():
    """SX-22: BREAK with no loop to release is rejected at parse time."""
    with pytest.raises(ParseError, match="BREAK"):
        parse(wrap("BREAK"))


def test_sx22_continue_outside_a_loop_is_rejected():
    """SX-22: CONTINUE with no loop to turn is rejected at parse time."""
    with pytest.raises(ParseError, match="CONTINUE"):
        parse(wrap("CONTINUE"))


def test_sx22_break_inside_a_loop_is_kept():
    """SX-22: BREAK inside a loop parses."""
    (f,) = creation_stmts("FOR x IN [1, 2]\nBREAK\nENDFOR")
    assert isinstance(f.body[0], A.Break)


def test_sx22_break_does_not_cross_a_rite_boundary():
    """SX-22: a BREAK inside a rite never answers to the caller's loop."""
    with pytest.raises(ParseError, match="BREAK"):
        parse(wrap("FOR x IN [1]\nDEFINE RITE f()\nBREAK\nEND RITE\nENDFOR"))


# -- SX-23: TRY is always a block --------------------------------------------------------------------------------

def test_sx23_try_opens_a_block_with_catch_and_endtry():
    """SX-23: TRY works on the following lines, then CATCH, then ENDTRY."""
    (t,) = creation_stmts("TRY\nREVEAL(1)\nCATCH\nREVEAL(ERROR)\nENDTRY")
    assert isinstance(t, A.TryStmt)
    assert t.error_name == "ERROR"
    assert len(t.try_body) == 1 and len(t.catch_body) == 1


def test_sx23_catch_may_name_the_error():
    """SX-23: CATCH may bind the error to a name of the author's choosing."""
    (t,) = creation_stmts("TRY\nREVEAL(1)\nCATCH trouble\nREVEAL(trouble)\nENDTRY")
    assert t.error_name == "trouble"


def test_sx23_try_has_no_one_line_form():
    """SX-23: TRY on one line is rejected; it always opens a block."""
    with pytest.raises(ParseError, match="TRY opens a block"):
        parse(wrap("TRY REVEAL(1) CATCH ENDTRY"))


# -- SX-24: DEFINE RITE --------------------------------------------------------------------------------------------

def test_sx24_rite_names_params():
    """SX-24: DEFINE RITE name(p1, p2, ...) names the rite and its parameters."""
    (r,) = creation_stmts("DEFINE RITE greet(name, times)\nREVEAL(name)\nEND RITE")
    assert isinstance(r, A.DefineRite)
    assert r.name == "greet"
    assert r.params == ["name", "times"]


def test_sx24_rite_may_take_no_params():
    """SX-24: empty parentheses mean the rite takes no parameters."""
    (r,) = creation_stmts("DEFINE RITE rest()\nREVEAL(1)\nEND RITE")
    assert r.params == []


# -- SX-25: rite bodies ------------------------------------------------------------------------------------------------

def test_sx25_rite_one_line_form():
    """SX-25: a rite body may be one statement on the same line; END RITE is still required."""
    (r,) = creation_stmts("DEFINE RITE f(x) SEAL x END RITE")
    assert isinstance(r, A.DefineRite)
    assert len(r.body) == 1
    assert isinstance(r.body[0], A.SealStmt)


def test_sx25_empty_one_line_rite_body_is_rejected():
    """SX-25: an empty one-line rite body is rejected."""
    with pytest.raises(ParseError, match="Unexpected"):
        parse(wrap("DEFINE RITE f() END RITE"))


# -- SX-26: RETURN ------------------------------------------------------------------------------------------------------------

def test_sx26_return_carries_a_value():
    """SX-26: RETURN expr carries a value out of the rite."""
    (r,) = creation_stmts("DEFINE RITE f()\nRETURN 1 + 2\nEND RITE")
    ret = r.body[0]
    assert isinstance(ret, A.Return)
    assert isinstance(ret.expr, A.BinaryOp)


def test_sx26_return_may_be_bare():
    """SX-26: a bare RETURN carries nothing."""
    (r,) = creation_stmts("DEFINE RITE f()\nRETURN\nEND RITE")
    ret = r.body[0]
    assert isinstance(ret, A.Return)
    assert ret.expr is None


# -- SX-27: calls ----------------------------------------------------------------------------------------------------------------

def test_sx27_call_as_expression():
    """SX-27: name(args) calls wherever a value is expected."""
    (d,) = creation_stmts('DECLARE x AS greet("hi", 3)')
    call = d.value
    assert isinstance(call, A.CallExpr)
    assert call.callee == "greet"
    assert len(call.args) == 2


def test_sx27_invoke_as_statement():
    """SX-27: INVOKE name(args) calls as a statement."""
    (e,) = creation_stmts('INVOKE greet("hi")')
    assert isinstance(e, A.ExprStmt)
    assert isinstance(e.expr, A.CallExpr)
    assert e.expr.callee == "greet"


def test_sx27_call_with_no_args():
    """SX-27: empty parentheses call with no arguments."""
    (e,) = creation_stmts("INVOKE greet()")
    assert e.expr.args == []


# -- SX-28: IMPORT -------------------------------------------------------------------------------------------------------------------

def test_sx28_import_names_a_scroll_in_quotes():
    """SX-28: IMPORT "path" names a scroll in quotes."""
    (i,) = creation_stmts('IMPORT "other.god"')
    assert isinstance(i, A.Import)
    assert i.path == "other.god"


def test_sx28_import_rejects_a_bare_value():
    """SX-28: anything but a quoted string is rejected."""
    with pytest.raises(ParseError):
        parse(wrap("IMPORT 42"))


# -- SX-29: precedence -------------------------------------------------------------------------------------------------------------------

def test_sx29_multiplication_binds_tighter_than_addition():
    """SX-29: 1 + 2 * 3 is 1 + (2 * 3)."""
    (d,) = creation_stmts("DECLARE x AS 1 + 2 * 3")
    assert d.value.op == "+"
    assert d.value.right.op == "*"


def test_sx29_and_binds_tighter_than_or():
    """SX-29: a OR b AND c is a OR (b AND c)."""
    (d,) = creation_stmts("DECLARE x AS a OR b AND c")
    assert d.value.op == "or"
    assert d.value.right.op == "and"


def test_sx29_parens_overrule():
    """SX-29: parentheses overrule the binding order."""
    (d,) = creation_stmts("DECLARE x AS (1 + 2) * 3")
    assert d.value.op == "*"
    assert d.value.left.op == "+"


# -- SX-30: IS spellings -------------------------------------------------------------------------------------------------------------------

def test_sx30_is_is_equality():
    """SX-30: a IS b is a == b."""
    (d,) = creation_stmts("DECLARE x AS a IS b")
    assert d.value.op == "=="


def test_sx30_is_not_is_inequality():
    """SX-30: a IS NOT b is a != b."""
    (d,) = creation_stmts("DECLARE x AS a IS NOT b")
    assert d.value.op == "!="


def test_sx30_single_equals_is_equality():
    """SX-30: a = b spells equality just like a == b."""
    (d1,) = creation_stmts("DECLARE x AS a = b")
    (d2,) = creation_stmts("DECLARE x AS a == b")
    assert d1.value.op == "==" == d2.value.op


# -- SX-31: comparison chains -----------------------------------------------------------------------------------------------------------------

def test_sx31_comparisons_chain_left_to_right():
    """SX-31: a IS b IS c is read as (a IS b) IS c."""
    (d,) = creation_stmts("DECLARE x AS a IS b IS c")
    assert d.value.op == "=="
    assert d.value.left.op == "=="


# -- SX-32: NOT levels --------------------------------------------------------------------------------------------------------------------------------

def test_sx32_not_binds_looser_than_comparison():
    """SX-32: NOT a IS b is NOT (a IS b)."""
    (d,) = creation_stmts("DECLARE x AS NOT a IS b")
    assert isinstance(d.value, A.UnaryOp)
    assert d.value.op == "not"
    assert isinstance(d.value.operand, A.BinaryOp)


def test_sx32_tight_not_binds_to_what_follows():
    """SX-32: a * NOT b is a * (NOT b)."""
    (d,) = creation_stmts("DECLARE x AS a * NOT b")
    assert d.value.op == "*"
    assert isinstance(d.value.right, A.UnaryOp)


# -- SX-33: unary minus -------------------------------------------------------------------------------------------------------------------------------------

def test_sx33_unary_minus_binds_tighter_than_multiplication():
    """SX-33: -2 * 3 is (-2) * 3."""
    (d,) = creation_stmts("DECLARE x AS -2 * 3")
    assert d.value.op == "*"
    assert isinstance(d.value.left, A.UnaryOp)


# -- SX-34: indexing ---------------------------------------------------------------------------------------------------------------------------------------------

def test_sx34_indexing_chains():
    """SX-34: a[0][1] indexes the result of a[0]."""
    (d,) = creation_stmts("DECLARE x AS a[0][1]")
    assert isinstance(d.value, A.Index)
    assert isinstance(d.value.obj, A.Index)


def test_sx34_index_is_any_expression():
    """SX-34: the index is any expression."""
    (d,) = creation_stmts("DECLARE x AS a[1 + 2]")
    assert isinstance(d.value.index, A.BinaryOp)


# -- SX-35: lists and grouping ---------------------------------------------------------------------------------------------------------------------------------------

def test_sx35_list_literal():
    """SX-35: [e1, e2, ...] gathers the values."""
    (d,) = creation_stmts("DECLARE x AS [1, 2]")
    assert isinstance(d.value, A.ListLiteral)
    assert len(d.value.items) == 2


def test_sx35_empty_list():
    """SX-35: [] is the empty gathering."""
    (d,) = creation_stmts("DECLARE x AS []")
    assert d.value.items == []


def test_sx35_parens_group():
    """SX-35: (a + b) is one grouped value."""
    (d,) = creation_stmts("DECLARE x AS (a + b)")
    assert isinstance(d.value, A.BinaryOp)


# -- SX-36: truth literals -------------------------------------------------------------------------------------------------------------------------------------------------

def test_sx36_truth_literals_in_any_case():
    """SX-36: TRUE, FALSE, and VOID are literal values in any letter case."""
    t, f, v = creation_stmts("DECLARE a AS true\nDECLARE b AS False\nDECLARE c AS VOID")
    assert t.value.value is True
    assert f.value.value is False
    assert v.value.value is None


# -- SX-37: interpolation ---------------------------------------------------------------------------------------------------------------------------------------------------------

def test_sx37_braces_breathe_an_expression_into_the_string():
    """SX-37: {expr} places one expression's value into the words."""
    (d,) = creation_stmts('DECLARE s AS "grace upon {name}"')
    val = d.value
    assert isinstance(val, A.InterpolatedString)
    assert val.parts[0] == "grace upon "
    assert isinstance(val.parts[1], A.Identifier)


def test_sx37_doubled_braces_write_plain_braces():
    """SX-37: {{ and }} write plain braces."""
    (d,) = creation_stmts('DECLARE s AS "{{blessed}}"')
    val = d.value
    assert isinstance(val, A.InterpolatedString)
    assert "".join(p for p in val.parts if isinstance(p, str)) == "{blessed}"


def test_sx37_lone_closing_brace_stays_plain():
    """SX-37: a lone } stays a plain brace, and the string is no interpolation."""
    (d,) = creation_stmts('DECLARE s AS "a } b"')
    assert isinstance(d.value, A.Literal)
    assert d.value.value == "a } b"


# -- SX-38: brace errors ---------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_sx38_empty_braces_are_rejected():
    """SX-38: {} breathes nothing and is rejected."""
    with pytest.raises(ParseError, match="empty braces"):
        parse(wrap('DECLARE s AS "a {}"'))


def test_sx38_unclosed_brace_is_rejected():
    """SX-38: an unclosed { is rejected where it opened."""
    with pytest.raises(ParseError, match="never sealed"):
        parse(wrap('DECLARE s AS "a {b"'))


# -- SX-39: one expression per brace pair ------------------------------------------------------------------------------------------------------------------------------------------------------

def test_sx39_nested_braces_and_quotes_are_honoured():
    """SX-39: nested braces and quoted strings inside { } are honoured."""
    (d,) = creation_stmts('DECLARE s AS "{greet(\\"hi {name}\\")}"')
    val = d.value
    assert isinstance(val, A.InterpolatedString)
    (call,) = [p for p in val.parts if not isinstance(p, str)]
    assert isinstance(call, A.CallExpr)
    assert isinstance(call.args[0], A.InterpolatedString)


def test_sx39_two_expressions_in_braces_are_rejected():
    """SX-39: only one expression may dwell between { and }."""
    with pytest.raises(ParseError, match="only one expression"):
        parse(wrap('DECLARE s AS "a {b c}"'))
