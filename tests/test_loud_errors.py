"""Loud errors and explicit symbols: the new law of names.

A name that was never declared is never read silently. Reading one stops
the run with a gentle error naming the name. A bare word spoken on
purpose carries its mark, ``:name``, and the word itself is the value.
"""

import pytest

from godcode import run_source
from godcode.cli import CanonicalFormatter
from godcode.errors import GodRuntimeError, LexerError
from godcode.interpreter import Interpreter
from godcode.linter import lint_source
from godcode.tongues import parse_source
from godcode.values import Symbol


def wrap(body: str) -> str:
    return "BEGIN CREATION\n" + body + "\nEND CREATION"


def run(body: str):
    return run_source(wrap(body))


# -- the explicit symbol -----------------------------------------------------


def test_symbol_literal_reveals_its_word():
    r = run("REVEAL(:worthy)")
    assert r.error is None
    assert r.output == "worthy"


def test_symbol_literal_is_a_symbol_value():
    interp = Interpreter(log_path=None)
    interp.run_source(wrap("DECLARE s AS :worthy"))
    assert type(interp.env.get("s")) is Symbol
    assert interp.env.get("s") == "worthy"


def test_symbol_type_name():
    r = run("REVEAL(TYPE(:worthy))")
    assert r.output == "symbol"


def test_symbol_compares_by_text():
    r = run(
        "DECLARE seeker AS :worthy\n"
        "REVEAL(seeker IS :worthy)\n"
        "REVEAL(seeker IS NOT :worthy)\n"
        "REVEAL(seeker IS :unworthy)\n"
        'REVEAL(:worthy IS "worthy")'
    )
    assert r.error is None
    assert r.output.split("\n") == ["true", "false", "false", "true"]


def test_symbol_is_truthy():
    r = run('IF :grace THEN\nREVEAL("yes")\nELSE\nREVEAL("no")\nENDIF')
    assert r.output == "yes"


def test_symbols_in_a_list():
    r = run("DECLARE tribes AS [:Judah, :Reuben]\nREVEAL(tribes[1])\nREVEAL(LEN(tribes))")
    assert r.error is None
    assert r.output.split("\n") == ["Reuben", "2"]


def test_symbol_in_interpolation():
    r = run('REVEAL("the way is {:worthy}")')
    assert r.output == "the way is worthy"


# -- the loud error ------------------------------------------------------------


def test_undeclared_name_is_loud_and_names_itself():
    r = run("REVEAL(worhty)")
    assert r.error is not None
    assert "There is no 'worhty' in this creation" in r.error
    assert "It was never spoken into being" in r.error
    assert "DECLARE it first" in r.error
    assert ":worhty" in r.error


def test_undeclared_name_error_carries_line_and_col():
    interp = Interpreter(log_path=None)
    with pytest.raises(GodRuntimeError) as exc:
        interp.run_source(wrap('DECLARE seeker AS "worthy"\nREVEAL(seeker IS worhty)'))
    assert exc.value.line == 3
    assert exc.value.col is not None


def test_did_you_mean_for_a_typo_of_a_declared_name():
    r = run("DECLARE worthy AS 7\nREVEAL(worhty)")
    assert r.error is not None
    assert "Did you mean 'worthy'?" in r.error


def test_use_before_declare_is_loud():
    r = run("REVEAL(grace)\nDECLARE grace AS 7\nREVEAL(grace)")
    assert r.error is not None
    assert "'grace'" in r.error


def test_the_proof_scroll_from_the_plan():
    bad = (
        "BEGIN CREATION\n"
        '  DECLARE seeker AS "worthy"\n'
        '  IF seeker IS worhty THEN\n'
        '    REVEAL("enter")\n'
        "  ENDIF\n"
        "END CREATION"
    )
    r = run_source(bad)
    assert r.error is not None
    assert "'worhty'" in r.error
    assert r.output == ""

    good = (
        "BEGIN CREATION\n"
        "  DECLARE seeker AS :worthy\n"
        "  IF seeker IS :worthy THEN\n"
        '    REVEAL("enter")\n'
        "  ENDIF\n"
        "END CREATION"
    )
    r = run_source(good)
    assert r.error is None
    assert r.output == "enter"


# -- tongues: the mark is punctuation -----------------------------------------


def test_symbol_in_a_setswana_scroll():
    src = (
        "# tongue: tn\n"
        "SIMOLOLA TLHOLEGO\n"
        "BOLELA tsela JAAKA :kagiso\n"
        "FA tsela KE :kagiso TLOGA\n"
        'SENOLA("Kagiso e teng.")\n'
        "FEDISA FA\n"
        "FEDISA TLHOLEGO"
    )
    r = run_source(src)
    assert r.error is None
    assert r.output == "Kagiso e teng."


def test_undeclared_name_is_loud_in_a_tongue_scroll():
    src = (
        "# tongue: tn\n"
        "SIMOLOLA TLHOLEGO\n"
        "SENOLA(tsela)\n"
        "FEDISA TLHOLEGO"
    )
    r = run_source(src)
    assert r.error is not None
    assert "'tsela'" in r.error


# -- the lexer and the formatter -----------------------------------------------


def test_a_lone_colon_is_a_gentle_lexer_error():
    with pytest.raises(LexerError) as exc:
        parse_source(wrap("REVEAL(:)"))
    assert ":worthy" in str(exc.value)


def test_fmt_round_trips_the_mark():
    program = parse_source(wrap("DECLARE seeker AS :worthy\nIF seeker IS :worthy THEN REVEAL(\"heaven\")"))
    text = CanonicalFormatter().format(program)
    assert "DECLARE seeker AS :worthy" in text
    assert "IF seeker == :worthy THEN" in text


def test_fmt_renders_a_tongue_scrolls_symbols_in_canonical_english():
    src = (
        "# tongue: tn\n"
        "SIMOLOLA TLHOLEGO\n"
        "BOLELA tsela JAAKA :kagiso\n"
        "FEDISA TLHOLEGO"
    )
    text = CanonicalFormatter().format(parse_source(src))
    assert "DECLARE tsela AS :kagiso" in text


# -- the counsel beside the law ---------------------------------------------------


def test_linter_still_counsels_gc002_for_the_undeclared_read():
    findings = lint_source(wrap("REVEAL(wanderer)"), source_name="<scroll>")
    assert any(f.rule == "GC002" and "undefined name 'wanderer'" in f.message
               for f in findings)


def test_linter_does_not_flag_an_explicit_symbol():
    findings = lint_source(wrap("REVEAL(:wanderer)"), source_name="<scroll>")
    assert not any(f.rule == "GC002" for f in findings)


def test_unknown_rite_call_keeps_its_gentle_error():
    r = run("blessing(1, 2)")
    assert r.error is not None
    assert "There is no rite named 'blessing'" in r.error
