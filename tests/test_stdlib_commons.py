"""Tests for the commons stdlib: everyday tools for words, lists, maps,
and numbers (godcode.stdlib_commons).

Every test runs real God Code source through the real pipeline
(Lexer -> Parser -> Interpreter) and asserts on revealed output, in the
style of tests/test_stdlib_hashes.py.
"""

import pytest

from godcode.errors import GodRuntimeError
from godcode.interpreter import Interpreter
from godcode.lexer import Lexer
from godcode.parser import Parser
from godcode.sandbox import SandboxPolicy, apply_policy
from godcode import stdlib_commons


def run(src, interp=None):
    """Parse src, run it, return the revealed lines."""
    prog = Parser(Lexer(src).lex()).parse()
    interp = interp if interp is not None else Interpreter()
    interp.run(prog)
    return interp.output


def run_err(src):
    """Run src and return the GodRuntimeError it raises."""
    prog = Parser(Lexer(src).lex()).parse()
    interp = Interpreter()
    with pytest.raises(GodRuntimeError) as excinfo:
        interp.run(prog)
    return excinfo.value


# A map literal for the tests, built the way the language builds maps.
MAP_SRC = 'JSON_PARSE("{{\\"a\\": 1, \\"b\\": 2}}")'


# ------------------------------------------------------------------ words


def test_trim():
    assert run('REVEAL(TRIM("  grace  "))') == ["grace"]
    assert run('REVEAL(TRIM("grace"))') == ["grace"]
    assert run('REVEAL(TRIM(""))') == [""]


def test_trim_refuses_lists():
    err = run_err("REVEAL(TRIM([1]))")
    assert "works on words" in str(err)


def test_replace():
    assert run('REVEAL(REPLACE("manna manna", "manna", "bread"))') == ["bread bread"]
    assert run('REVEAL(REPLACE("dawn", "x", "y"))') == ["dawn"]


def test_replace_refuses_empty_needle():
    err = run_err('REVEAL(REPLACE("dawn", "", "y"))')
    assert "needs something to find" in str(err)


def test_starts_with_ends_with():
    assert run('REVEAL(STARTS_WITH("dawn", "da"))') == ["true"]
    assert run('REVEAL(STARTS_WITH("dawn", "wn"))') == ["false"]
    assert run('REVEAL(ENDS_WITH("dawn", "wn"))') == ["true"]
    assert run('REVEAL(ENDS_WITH("dawn", "da"))') == ["false"]
    assert run('REVEAL(STARTS_WITH("dawn", ""))') == ["true"]


def test_substring():
    assert run('REVEAL(SUBSTRING("blessing", 2, 6))') == ["essi"]
    assert run('REVEAL(SUBSTRING("blessing", 4))') == ["sing"]
    assert run('REVEAL(SUBSTRING("blessing", 0, 100))') == ["blessing"]
    assert run('REVEAL(SUBSTRING("blessing", 6, 2))') == [""]


def test_substring_refuses_fractions():
    err = run_err('REVEAL(SUBSTRING("blessing", 1.5))')
    assert "whole numbers" in str(err)


def test_contains_word():
    assert run('REVEAL(CONTAINS("blessing", "sing"))') == ["true"]
    assert run('REVEAL(CONTAINS("blessing", "curse"))') == ["false"]


def test_contains_list():
    assert run("REVEAL(CONTAINS([1, 2, 3], 2))") == ["true"]
    assert run("REVEAL(CONTAINS([1, 2, 3], 9))") == ["false"]
    assert run('REVEAL(CONTAINS(["a", "b"], "a"))') == ["true"]


def test_contains_refuses_numbers():
    err = run_err("REVEAL(CONTAINS(42, 4))")
    assert "searches a word or a list" in str(err)


def test_count():
    assert run('REVEAL(COUNT("banana", "an"))') == ["2"]
    assert run('REVEAL(COUNT("banana", "z"))') == ["0"]


def test_count_refuses_empty_part():
    err = run_err('REVEAL(COUNT("banana", ""))')
    assert "needs something to count" in str(err)


# ------------------------------------------------------------------ lists


def test_sort_numbers():
    assert run("REVEAL(SORT([3, 1, 2]))") == ["[1, 2, 3]"]
    assert run("REVEAL(SORT([]))") == ["[]"]


def test_sort_words():
    assert run('REVEAL(SORT(["c", "a", "b"]))') == ["[a, b, c]"]


def test_sort_does_not_mutate():
    src = (
        "DECLARE xs AS [3, 1, 2]\n"
        "DECLARE ys AS SORT(xs)\n"
        "REVEAL(xs)\n"
        "REVEAL(ys)"
    )
    assert run(src) == ["[3, 1, 2]", "[1, 2, 3]"]


def test_sort_refuses_mixed_kinds():
    err = run_err('REVEAL(SORT([1, "a"]))')
    assert "mixed kinds" in str(err)


def test_min_max_of():
    assert run("REVEAL(MIN_OF([3, 1, 2]))") == ["1"]
    assert run("REVEAL(MAX_OF([3, 1, 2]))") == ["3"]
    assert run('REVEAL(MIN_OF(["c", "a"]))') == ["a"]
    assert run('REVEAL(MAX_OF(["c", "a"]))') == ["c"]


def test_min_max_of_empty():
    err = run_err("REVEAL(MIN_OF([]))")
    assert "empty gathering" in str(err)
    err = run_err("REVEAL(MAX_OF([]))")
    assert "empty gathering" in str(err)


def test_sum_of():
    assert run("REVEAL(SUM_OF([1, 2, 3]))") == ["6"]
    assert run("REVEAL(SUM_OF([]))") == ["0"]
    assert run("REVEAL(SUM_OF([1.5, 2]))") == ["3.5"]


def test_sum_of_refuses_words():
    err = run_err('REVEAL(SUM_OF(["a"]))')
    assert "weighs a number" in str(err)


def test_sum_of_refuses_truths():
    err = run_err("REVEAL(SUM_OF([TRUE]))")
    assert "weighs a number" in str(err)


def test_first_last():
    assert run('REVEAL(FIRST(["a", "b"]))') == ["a"]
    assert run('REVEAL(LAST(["a", "b"]))') == ["b"]


def test_first_last_empty():
    err = run_err("REVEAL(FIRST([]))")
    assert "empty gathering" in str(err)
    err = run_err("REVEAL(LAST([]))")
    assert "empty gathering" in str(err)


def test_unique():
    assert run("REVEAL(UNIQUE([1, 2, 2, 3, 1]))") == ["[1, 2, 3]"]
    assert run('REVEAL(UNIQUE(["a", "a", "b"]))') == ["[a, b]"]
    assert run("REVEAL(UNIQUE([]))") == ["[]"]


def test_index_of():
    assert run('REVEAL(INDEX_OF(["a", "b"], "b"))') == ["1"]
    assert run('REVEAL(INDEX_OF(["a", "b"], "z"))') == ["-1"]
    assert run("REVEAL(INDEX_OF([], 1))") == ["-1"]


# ------------------------------------------------------------------- maps


def test_keys_values():
    assert run(f"REVEAL(KEYS({MAP_SRC}))") == ["[a, b]"]
    assert run(f"REVEAL(VALUES({MAP_SRC}))") == ["[1, 2]"]


def test_has_key():
    assert run(f'REVEAL(HAS_KEY({MAP_SRC}, "a"))') == ["true"]
    assert run(f'REVEAL(HAS_KEY({MAP_SRC}, "z"))') == ["false"]


def test_has_key_refuses_non_word_key():
    err = run_err(f"REVEAL(HAS_KEY({MAP_SRC}, 1))")
    assert "looks up a word" in str(err)


def test_merge():
    src = (
        'DECLARE m AS MERGE(JSON_PARSE("{{\\"a\\": 1}}"), '
        'JSON_PARSE("{{\\"b\\": 2, \\"a\\": 9}}"))\n'
        "REVEAL(m)"
    )
    assert run(src) == ["{a: 9, b: 2}"]


def test_merge_does_not_mutate():
    src = (
        'DECLARE m AS JSON_PARSE("{{\\"a\\": 1}}")\n'
        'DECLARE n AS MERGE(m, JSON_PARSE("{{\\"b\\": 2}}"))\n'
        "REVEAL(KEYS(m))\n"
        "REVEAL(KEYS(n))"
    )
    assert run(src) == ["[a]", "[a, b]"]


def test_map_rites_refuse_non_maps():
    err = run_err("REVEAL(KEYS([1]))")
    assert "reads a map" in str(err)
    err = run_err('REVEAL(VALUES("nope"))')
    assert "reads a map" in str(err)


# ---------------------------------------------------------------- numbers


def test_abs():
    assert run("REVEAL(ABS(0 - 4))") == ["4"]
    assert run("REVEAL(ABS(4))") == ["4"]
    assert run("REVEAL(ABS(0 - 2.5))") == ["2.5"]


def test_abs_refuses_truths():
    err = run_err("REVEAL(ABS(TRUE))")
    assert "weighs a number" in str(err)


def test_round_half_away_from_zero():
    assert run("REVEAL(ROUND(2.5))") == ["3"]
    assert run("REVEAL(ROUND(0 - 2.5))") == ["-3"]
    assert run("REVEAL(ROUND(2.4))") == ["2"]


def test_round_with_places():
    assert run("REVEAL(ROUND(3.14159, 2))") == ["3.14"]
    assert run("REVEAL(ROUND(3.145, 2))") == ["3.15"]


def test_round_refuses_negative_places():
    err = run_err("REVEAL(ROUND(3.14, 0 - 1))")
    assert "from zero upward" in str(err)


def test_floor_ceil():
    assert run("REVEAL(FLOOR(3.9))") == ["3"]
    assert run("REVEAL(FLOOR(0 - 3.1))") == ["-4"]
    assert run("REVEAL(CEIL(3.1))") == ["4"]
    assert run("REVEAL(CEIL(0 - 3.9))") == ["-3"]
    assert run("REVEAL(FLOOR(4))") == ["4"]


def test_sqrt():
    assert run("REVEAL(SQRT(144))") == ["12"]
    assert run("REVEAL(SQRT(0))") == ["0"]


def test_sqrt_refuses_negatives():
    err = run_err("REVEAL(SQRT(0 - 1))")
    assert "cannot root a negative number" in str(err)


def test_pow():
    assert run("REVEAL(POW(2, 10))") == ["1024"]
    assert run("REVEAL(POW(2, 0 - 1))") == ["0.5"]
    assert run("REVEAL(POW(9, 0.5))") == ["3"]


def test_pow_refuses_imaginary():
    err = run_err("REVEAL(POW(0 - 1, 0.5))")
    assert "leaves the real numbers" in str(err)


# ------------------------------------------------- arity, wiring, sandbox


def test_arity_is_gentle():
    err = run_err('REVEAL(TRIM("a", "b"))')
    assert "asks for 1 offering(s)" in str(err)
    err = run_err("REVEAL(SORT())")
    assert "asks for 1 offering(s)" in str(err)


def test_register_returns_all_builtins():
    interp = Interpreter()
    assert set(stdlib_commons.register(interp)) == {
        "TRIM", "REPLACE", "STARTS_WITH", "ENDS_WITH", "SUBSTRING",
        "CONTAINS", "COUNT", "SORT", "MIN_OF", "MAX_OF", "SUM_OF",
        "FIRST", "LAST", "UNIQUE", "INDEX_OF", "KEYS", "VALUES",
        "HAS_KEY", "MERGE", "ABS", "ROUND", "FLOOR", "CEIL",
        "SQRT", "POW",
    }


def test_builtins_present_on_fresh_interpreter():
    interp = Interpreter()
    for name in ("TRIM", "SORT", "KEYS", "ABS", "ROUND"):
        assert name in interp._builtins


def test_commons_run_unchanged_under_sandbox():
    policy = SandboxPolicy()
    src = (
        'REVEAL(TRIM("  grace  "))\n'
        "REVEAL(SORT([3, 1, 2]))\n"
        f"REVEAL(KEYS({MAP_SRC}))\n"
        "REVEAL(ABS(0 - 4))\n"
        "REVEAL(POW(2, 10))\n"
    )
    prog = Parser(Lexer(src).lex()).parse()
    interp = Interpreter()
    apply_policy(interp, policy)
    interp.run(prog)
    assert interp.output == ["grace", "[1, 2, 3]", "[a, b]", "4", "1024"]


def test_no_em_dashes_in_commons_errors():
    for src in (
        "REVEAL(TRIM([1]))",
        'REVEAL(SORT([1, "a"]))',
        "REVEAL(MIN_OF([]))",
        'REVEAL(REPLACE("a", "", "b"))',
        "REVEAL(SQRT(0 - 1))",
        "REVEAL(SUM_OF([TRUE]))",
    ):
        assert "\u2014" not in str(run_err(src))
