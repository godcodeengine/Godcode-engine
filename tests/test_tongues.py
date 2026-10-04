"""Tests for tongues: God Code keywords in other languages (godcode.tongues).

Setswana (``tn``) is the first tongue. Every test runs real God Code
source through the real pipeline and asserts on revealed output. The
pragma ``# tongue: tn`` opts a scroll in; without it, tongue words are
ordinary identifiers and English stays the only grammar.
"""

import pytest

from godcode.errors import GodCodeError, LexerError
from godcode.interpreter import Interpreter
from godcode.lexer import Lexer
from godcode.tongues import (
    detect_tongue,
    known_tongues,
    parse_source,
    resolve,
)


def run(src):
    """Parse src (honouring any tongue pragma), run it, return output lines."""
    interp = Interpreter()
    interp.run(parse_source(src))
    return interp.output


TN_HELLO = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA leina JAKA "Lefatshe"
SENOLA("Dumela, " + leina)
FEDISA TLHOLEGO
"""


# ------------------------------------------------------- pragma detection


def test_detect_tongue_pragma():
    assert detect_tongue("# tongue: tn\nSIMOLOLA TLHOLEGO\n") == "tn"
    assert detect_tongue("#tongue:TN\n") == "tn"
    assert detect_tongue("  #   Tongue  :  tn  \n") == "tn"
    assert detect_tongue("SIMOLOLA TLHOLEGO\n") is None


def test_known_tongues_lists_setswana():
    assert known_tongues()["tn"] == "Setswana"
    assert known_tongues()["en"] == "English"


def test_unknown_tongue_is_a_gentle_error():
    with pytest.raises(LexerError) as excinfo:
        resolve("xx")
    assert "not known yet" in str(excinfo.value)
    assert "tn (Setswana)" in str(excinfo.value)


def test_unknown_tongue_pragma_fails_lexing():
    with pytest.raises(LexerError):
        Lexer("# tongue: xx\nSIMOLOLA TLHOLEGO\n").lex()


def test_explicit_tongue_argument_beats_pragma():
    lx = Lexer("# tongue: tn\nSIMOLOLA TLHOLEGO\n", tongue="en")
    lx.lex()
    assert lx.tongue == "en"


# ------------------------------------------------------------------ lexing


def test_alias_words_become_canonical_tokens():
    from godcode.tokens import TokenType

    toks = [t for t in Lexer(TN_HELLO).lex() if t.type.name not in ("NEWLINE", "EOF")]
    kinds = [t.type for t in toks]
    assert kinds[0] is TokenType.BEGIN
    assert kinds[1] is TokenType.CREATION
    assert kinds[2] is TokenType.DECLARE
    # Token values stay canonical so fmt renders English.
    assert toks[0].value == "BEGIN"
    assert toks[2].value == "DECLARE"


def test_two_word_closers():
    from godcode.tokens import TokenType

    src = "# tongue: tn\nSIMOLOLA TLHOLEGO\nFA x GONE\nFEDISA FA\nFEDISA TLHOLEGO\n"
    kinds = [t.type for t in Lexer(src).lex()]
    assert TokenType.ENDIF in kinds
    assert kinds.count(TokenType.END) == 1  # only END CREATION's END


def test_compound_closer_needs_one_line():
    src = "# tongue: tn\nSIMOLOLA TLHOLEGO\nFEDISA\nFA\nFEDISA TLHOLEGO\n"
    with pytest.raises(GodCodeError):
        parse_source(src)


def test_endtry_compound():
    from godcode.tokens import TokenType

    src = "# tongue: tn\nSIMOLOLA TLHOLEGO\nLEKA\nTSHWARA\nFEDISA LEKA\nFEDISA TLHOLEGO\n"
    kinds = [t.type for t in Lexer(src).lex()]
    assert TokenType.ENDTRY in kinds


def test_without_pragma_tongue_words_are_identifiers():
    from godcode.tokens import TokenType

    src = "SIMOLOLA TLHOLEGO\n"
    kinds = [t.type for t in Lexer(src).lex()]
    assert TokenType.IDENT in kinds
    assert TokenType.BEGIN not in kinds


# ----------------------------------------------------------------- running


def test_setswana_hello_runs():
    assert run(TN_HELLO) == ["Dumela, Lefatshe"]


def test_if_then_endif_compound_runs():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA pula JAKA NNETE
FA pula GONE
    SENOLA("pula e na")
ELSE
    SENOLA("letsatsi le tjhaba")
FEDISA FA
FEDISA TLHOLEGO
"""
    assert run(src) == ["pula e na"]


def test_try_catch_endtry_compound_runs():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
LEKA
    BOLELA x JAKA 1 / 0
TSHWARA phoso
    SENOLA("go tshwerwe")
FEDISA LEKA
FEDISA TLHOLEGO
"""
    assert run(src) == ["go tshwerwe"]


def test_breathe_life_into_and_loops():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA motse JAKA "Gaborone"
HEMA BOTSHELO TENG motse
BOLELA palogotlhe JAKA 0
BOLELA n JAKA 1
WHILE n < 4 DO
    BOLELA palogotlhe JAKA palogotlhe + n
    BOLELA n JAKA n + 1
ENDWHILE
SENOLA("{motse} {palogotlhe}")
FEDISA TLHOLEGO
"""
    assert run(src) == ["Gaborone 6"]


def test_mixed_english_and_setswana():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
DECLARE x AS 40 + 2
SENOLA(x)
END CREATION
"""
    assert run(src) == ["42"]


def test_interpolation_speaks_the_tongue():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA leina JAKA "tsala"
SENOLA("Dumela {leina}: {NNETE LE NNETE}")
FEDISA TLHOLEGO
"""
    assert run(src) == ["Dumela tsala: true"]


def test_while_and_break_stay_english_in_first_edition():
    src = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA n JAKA 0
WHILE NNETE DO
    BOLELA n JAKA n + 1
    IF n IS 3 THEN
        KGAOLA
    ENDIF
ENDWHILE
SENOLA(n)
FEDISA TLHOLEGO
"""
    assert run(src) == ["3"]


def test_fmt_renders_canonical_english():
    from godcode.cli import CanonicalFormatter

    src = """# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA x JAKA 1
SENOLA(x)
FEDISA TLHOLEGO
"""
    # fmt works from the AST, which only knows canonical keywords.
    out = CanonicalFormatter().format(parse_source(src))
    assert "DECLARE x AS 1" in out
    assert "REVEAL(x)" in out
    assert "SIMOLOLA" not in out and "SENOLA" not in out
    # And the canonical rendering runs as plain English.
    assert run(out) == ["1"]


def test_lint_accepts_a_setswana_scroll():
    from godcode.linter import lint_source

    findings = lint_source(TN_HELLO, source_name="hello_tn.god")
    assert findings == []


def test_check_tool_accepts_a_setswana_scroll(tmp_path):
    from godcode.tools import tool_check

    p = tmp_path / "hello_tn.god"
    p.write_text(TN_HELLO, encoding="utf-8")
    assert tool_check({"file": str(p)})["ok"] is True


def test_sandbox_run_speaks_setswana():
    from godcode.sandbox import SandboxPolicy, apply_policy

    interp = Interpreter()
    apply_policy(
        interp,
        SandboxPolicy(allow_read_paths=(), allow_write=False, allow_network=False),
    )
    interp.run(parse_source(TN_HELLO))
    assert interp.output == ["Dumela, Lefatshe"]
