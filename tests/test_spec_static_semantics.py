"""Spec tests for the static meaning layer (docs/spec/static-meaning.md).

Each test keeps one ST rule honest: if the engine's name binding, scoping,
or lint counsel changes, the failing test names the rule that broke. Tests
are grouped by the rule they guard; the rule number sits in every docstring.
"""

import pytest

from godcode import cli, run_source
from godcode.linter import lint_source


def wrap(body):
    return "BEGIN CREATION\n" + body + "\nEND CREATION"


def run(body):
    return run_source(wrap(body))


def out(body):
    """Revealed output lines of a run, as a list."""
    return run(body).output.split("\n")


def lint(body, source_name="<scroll>"):
    return lint_source(wrap(body), source_name)


def has_rule(findings, rule, text=None):
    return any(f.rule == rule and (text is None or text in f.message)
               for f in findings)


# -- ST-1: the creation block shares the top-level scope ---------------------

def test_st1_declare_in_creation_visible_after():
    """ST-1: a DECLARE inside BEGIN CREATION is visible to the rest of the scroll."""
    r = run('DECLARE gift AS 42\nREVEAL(gift)')
    assert r.error is None
    assert out('DECLARE gift AS 42\nREVEAL(gift)') == ["42"]


# -- ST-2: IF and WHILE bodies run in the current scope -----------------------

def test_st2_if_declare_visible_after():
    """ST-2: a DECLARE inside an IF body is visible after ENDIF."""
    r = run('IF 1 IS 1 THEN\nDECLARE gift AS 42\nENDIF\nREVEAL(gift)')
    assert r.error is None
    assert out('IF 1 IS 1 THEN\nDECLARE gift AS 42\nENDIF\nREVEAL(gift)') == ["42"]


def test_st2_while_declare_visible_after():
    """ST-2: a DECLARE inside a WHILE body is visible after ENDWHILE."""
    r = run('WHILE 1 IS 1 DO\nDECLARE w AS 7\nBREAK\nENDWHILE\nREVEAL(w)')
    assert r.error is None
    assert out('WHILE 1 IS 1 DO\nDECLARE w AS 7\nBREAK\nENDWHILE\nREVEAL(w)') == ["7"]


# -- ST-3: FOR runs its body in one child scope -------------------------------

def test_st3_loop_var_unbound_after_endfor():
    """ST-3: after ENDFOR the loop variable is bound nowhere, so it reads as a Symbol."""
    r = run('FOR i IN RANGE(1, 4)\nREVEAL(i)\nENDFOR\nREVEAL(i)')
    assert r.error is None
    assert out('FOR i IN RANGE(1, 4)\nREVEAL(i)\nENDFOR\nREVEAL(i)') == ["1", "2", "3", "i"]


def test_st3_linter_flags_loop_var_after_loop_as_undefined():
    """ST-3: the linter models the FOR body as a child scope, so the escaped name is GC002."""
    findings = lint('FOR i IN RANGE(1, 4)\nREVEAL(i)\nENDFOR\nREVEAL(i)')
    assert has_rule(findings, "GC002", "undefined name 'i'")


# -- ST-4: rite bodies run in one child scope ---------------------------------

def test_st4_rite_local_invisible_after_call():
    """ST-4: a DECLARE inside a rite body is not visible after the call returns."""
    r = run('DEFINE RITE f()\nDECLARE hidden AS 1\nEND RITE\nf()\nREVEAL(hidden)')
    assert r.error is None
    assert out('DEFINE RITE f()\nDECLARE hidden AS 1\nEND RITE\nf()\nREVEAL(hidden)') == ["hidden"]


def test_st4_params_live_in_the_child_scope():
    """ST-4: parameters are bound in the body scope and unbound outside the rite."""
    r = run('DEFINE RITE f(a)\nRETURN a\nEND RITE\nREVEAL(f(3))\nREVEAL(a)')
    assert r.error is None
    assert out('DEFINE RITE f(a)\nRETURN a\nEND RITE\nREVEAL(f(3))\nREVEAL(a)') == ["3", "a"]


# -- ST-5: closures capture the definition scope by reference -----------------

def test_st5_redeclare_after_definition_seen_inside():
    """ST-5: a name re-bound after the rite is defined is seen with its new value."""
    body = ('DECLARE x AS 10\nDEFINE RITE see()\nRETURN x\nEND RITE\n'
            'DECLARE x AS 99\nREVEAL(see())')
    r = run(body)
    assert r.error is None
    assert out(body) == ["99"]


# -- ST-6: the rite name is bound before its body runs ------------------------

def test_st6_rite_may_call_itself():
    """ST-6: recursion is well-formed; the rite name is visible inside its own body."""
    body = ('DEFINE RITE count(n)\nIF n IS 0 THEN RETURN 0\n'
            'RETURN 1 + count(n - 1)\nEND RITE\nREVEAL(count(3))')
    r = run(body)
    assert r.error is None
    assert out(body) == ["3"]


# -- ST-7: names are case-sensitive -------------------------------------------

def test_st7_case_mismatch_reads_as_symbol():
    """ST-7: DECLARE MyName does not bind myname; the read yields the bare word."""
    r = run('DECLARE MyName AS 5\nREVEAL(myname)')
    assert r.error is None
    assert out('DECLARE MyName AS 5\nREVEAL(myname)') == ["myname"]


def test_st7_case_mismatch_is_gc002():
    """ST-7: the linter flags the case-mismatched read as an undefined name."""
    findings = lint('DECLARE MyName AS 5\nREVEAL(myname)')
    assert has_rule(findings, "GC002", "undefined name 'myname'")


# -- ST-8: tongue words are canonicalized before checking ---------------------

def test_st8_setswana_scroll_runs():
    """ST-8: a tongue scroll runs through the same static meaning as English."""
    src = ("# tongue: tn\nSIMOLOLA TLHOLEGO\n"
           "SENOLA(\"dumela\")\nFEDISA TLHOLEGO")
    from godcode import run_source as rs
    r = rs(src)
    assert r.error is None
    assert r.output.split("\n") == ["dumela"]


# -- ST-9: one namespace for variables, rites, params, loop vars --------------

def test_st9_declare_over_rite_rebinds():
    """ST-9: DECLARE of a rite's name replaces the binding; calling it fails."""
    r = run('DEFINE RITE f()\nRETURN 1\nEND RITE\nDECLARE f AS 5\nREVEAL(f())')
    assert r.error is not None
    assert "'f' is number, not a rite" in r.error


# -- ST-10: DECLARE binds in the current scope, shadowing ---------------------

def test_st10_inner_shadow_leaves_outer_untouched():
    """ST-10: shadowing inside a rite body changes nothing for the caller."""
    body = ('DECLARE x AS 1\nDEFINE RITE f()\nDECLARE x AS 2\nRETURN x\nEND RITE\n'
            'REVEAL(f())\nREVEAL(x)')
    r = run(body)
    assert r.error is None
    assert out(body) == ["2", "1"]


# -- ST-11: the value is breathed before the name is bound --------------------

def test_st11_update_reads_old_value():
    """ST-11: in DECLARE x AS x + 1 the right-hand x reads the old binding."""
    r = run('DECLARE x AS 10\nDECLARE x AS x + 1\nREVEAL(x)')
    assert r.error is None
    assert out('DECLARE x AS 10\nDECLARE x AS x + 1\nREVEAL(x)') == ["11"]


def test_st11_self_read_with_no_prior_binding_is_symbol():
    """ST-11: with no prior binding the self-read yields the bare word."""
    r = run('DECLARE y AS y\nREVEAL(y)')
    assert r.error is None
    assert out('DECLARE y AS y\nREVEAL(y)') == ["y"]


# -- ST-12: the update idiom is never GC006 -----------------------------------

def test_st12_update_idiom_not_redeclare():
    """ST-12: DECLARE count AS count + 1 is the update idiom, not a re-declaration."""
    findings = lint('DECLARE count AS 0\nDECLARE count AS count + 1\nREVEAL(count)')
    assert not has_rule(findings, "GC006")


# -- ST-13: re-DECLARE counsels but runs, last binding wins -------------------

def test_st13_redeclare_runs_with_last_value():
    """ST-13: a plain re-DECLARE runs; the last binding wins."""
    r = run('DECLARE x AS 1\nDECLARE x AS 2\nREVEAL(x)')
    assert r.error is None
    assert out('DECLARE x AS 1\nDECLARE x AS 2\nREVEAL(x)') == ["2"]


def test_st13_redeclare_is_gc006():
    """ST-13: the same name declared twice in one scope is GC006 counsel."""
    findings = lint('DECLARE x AS 1\nDECLARE x AS 2\nREVEAL(x)')
    assert has_rule(findings, "GC006", "'x' is declared more than once")


# -- ST-14: unbound names read as Symbols -------------------------------------

def test_st14_unbound_name_reveals_bare_word():
    """ST-14: REVEAL of a name bound nowhere reveals the word, and never errors."""
    r = run('REVEAL(grace)')
    assert r.error is None
    assert out('REVEAL(grace)') == ["grace"]


# -- ST-15: use before declare ------------------------------------------------

def test_st15_read_before_declare_sees_symbol():
    """ST-15: a name read before its DECLARE sees the bare word, then the value."""
    r = run('REVEAL(grace)\nDECLARE grace AS 7\nREVEAL(grace)')
    assert r.error is None
    assert out('REVEAL(grace)\nDECLARE grace AS 7\nREVEAL(grace)') == ["grace", "7"]


# -- ST-16: Symbols are always truthy -----------------------------------------

def test_st16_symbol_is_truthy():
    """ST-16: an unbound name in a condition takes the THEN path."""
    r = run('IF grace THEN\nREVEAL("yes")\nELSE\nREVEAL("no")\nENDIF')
    assert r.error is None
    assert out('IF grace THEN\nREVEAL("yes")\nELSE\nREVEAL("no")\nENDIF') == ["yes"]


# -- ST-17: Symbols act like words, but the engine can tell -------------------

def test_st17_for_refuses_a_symbol():
    """ST-17: FOR will not walk a mere Symbol; the error names the bare spirit."""
    r = run('FOR x IN grace\nREVEAL(x)\nENDFOR')
    assert r.error is not None
    assert "not the bare spirit 'grace'" in r.error


# -- ST-18: arity is checked at call time -------------------------------------

def test_st18_wrong_offerings_error():
    """ST-18: calling with the wrong number of offerings names the rite and counts both."""
    r = run('DEFINE RITE add(a, b)\nRETURN a + b\nEND RITE\nREVEAL(add(1))')
    assert r.error is not None
    assert "asks for 2 offerings, but 1 was brought" in r.error


# -- ST-19: calling an unbound name -------------------------------------------

def test_st19_unbound_call_names_the_rite_and_line():
    """ST-19: calling a name bound nowhere is a gentle runtime error naming the line."""
    r = run('blessing(1, 2)')
    assert r.error is not None
    assert "There is no rite named 'blessing'" in r.error
    assert "line 2" in r.error


def test_st19_near_miss_carries_counsel():
    """ST-19: a near-miss rite name carries did-you-mean counsel."""
    r = run('REPEA("x")')
    assert r.error is not None
    assert "Did you mean 'REPEAT'" in r.error


# -- ST-20: check parses, lint counsels ---------------------------------------

def test_st20_check_asks_only_whether_it_parses():
    """ST-20: a scroll full of undefined names still parses; counsel is the linter's work."""
    from godcode.tongues import parse_source
    body = 'DECLARE x AS 1\nREVEAL(y)'
    parse_source(wrap(body))  # parses fine
    findings = lint(body)
    assert has_rule(findings, "GC002", "undefined name 'y'")


def test_st20_lint_findings_never_stop_a_run():
    """ST-20: counsel advises but never forbids; a flagged scroll still runs."""
    body = 'DECLARE x AS 1\nREVEAL("fine")'
    assert has_rule(lint(body), "GC001", "unused variable 'x'")
    r = run(body)
    assert r.error is None
    assert out(body) == ["fine"]


# -- ST-21: GC002, the undefined name ------------------------------------------

def test_st21_undefined_name_flagged():
    """ST-21: a name read but never declared is GC002 counsel."""
    findings = lint('REVEAL(y)')
    assert has_rule(findings, "GC002", "undefined name 'y'")


def test_st21_builtins_never_flagged():
    """ST-21: builtin names are always known to the linter."""
    findings = lint('REVEAL(UPPER("amen"))')
    assert not has_rule(findings, "GC002")


def test_st21_imported_names_harvested(tmp_path):
    """ST-21: names harvested from a resolvable IMPORT raise no GC002."""
    lib = tmp_path / "helpers.god"
    lib.write_text(wrap('DEFINE RITE helper()\nRETURN 1\nEND RITE'), encoding="utf-8")
    main_src = 'IMPORT "helpers.god"\nREVEAL(helper())'
    findings = lint_source(main_src, source_name=str(tmp_path / "main.god"))
    assert not has_rule(findings, "GC002")


def test_st21_unresolvable_import_withholds_counsel(tmp_path):
    """ST-21: when an import cannot be resolved, the linter stays silent on names."""
    main_src = 'IMPORT "not_here.god"\nREVEAL(whatever)'
    findings = lint_source(main_src, source_name=str(tmp_path / "main.god"))
    assert not has_rule(findings, "GC002")


# -- ST-22: GC001, the unused variable ------------------------------------------

def test_st22_unused_variable_flagged():
    """ST-22: a DECLAREd name never referenced is GC001 counsel."""
    findings = lint('DECLARE x AS 1\nREVEAL("fine")')
    assert has_rule(findings, "GC001", "unused variable 'x'")


def test_st22_closure_reference_counts_as_used():
    """ST-22: a reference inside a nested rite body marks the name used."""
    findings = lint('DECLARE x AS 10\nDEFINE RITE see()\nRETURN x\nEND RITE\nREVEAL(see())')
    assert not has_rule(findings, "GC001")


def test_st22_loop_var_used_in_body_not_flagged():
    """ST-22: a loop variable read in its own body is not unused."""
    findings = lint('FOR i IN RANGE(1, 4)\nREVEAL(i)\nENDFOR')
    assert not has_rule(findings, "GC001")


# -- ST-23: GC003, shadowing ---------------------------------------------------

def test_st23_shadow_flagged():
    """ST-23: a rite param reusing an outer name is shadowing counsel."""
    findings = lint('DECLARE x AS 1\nDEFINE RITE f(x)\nRETURN x\nEND RITE')
    assert has_rule(findings, "GC003", "shadows a name already visible")


# -- ST-24: GC004, the empty block ----------------------------------------------

def test_st24_empty_if_flagged():
    """ST-24: an IF with no statements is empty-block counsel."""
    findings = lint('IF 1 IS 1 THEN\nENDIF')
    assert has_rule(findings, "GC004", "empty IF body")


def test_st24_empty_rite_flagged():
    """ST-24: a rite with no statements is empty-block counsel."""
    findings = lint('DEFINE RITE f()\nEND RITE')
    assert has_rule(findings, "GC004", "empty rite body for 'f'")


# -- ST-25: GC005, unreachable code ----------------------------------------------

def test_st25_code_after_return_flagged():
    """ST-25: a statement after RETURN in the same block is unreachable counsel."""
    findings = lint('DEFINE RITE f()\nRETURN 1\nREVEAL("never")\nEND RITE')
    assert has_rule(findings, "GC005", "unreachable code after RETURN")


# -- ST-26: GC006, re-declare ----------------------------------------------------

def test_st26_redeclare_flagged_update_idiom_exempt():
    """ST-26: a plain re-DECLARE is GC006; the update idiom is exempt (see ST-12)."""
    assert has_rule(lint('DECLARE x AS 1\nDECLARE x AS 2\nREVEAL(x)'), "GC006")
    assert not has_rule(lint('DECLARE x AS 1\nDECLARE x AS x + 2\nREVEAL(x)'), "GC006")


# -- ST-27: the CATCH binding is implicit ----------------------------------------

def test_st27_catch_binding_never_unused():
    """ST-27: a CATCH that never reads its error name is not flagged as unused."""
    findings = lint('TRY\nREVEAL("safe")\nCATCH e\nREVEAL("caught")\nENDTRY')
    assert not has_rule(findings, "GC001")


def test_st27_empty_catch_flagged():
    """ST-27: an empty CATCH body is still GC004 counsel."""
    findings = lint('TRY\nREVEAL("safe")\nCATCH e\nENDTRY')
    assert has_rule(findings, "GC004", "empty CATCH body")


# -- ST-28: IMPORT brings top-level names into the importer's scope ---------------

def test_st28_imported_rite_callable(tmp_path):
    """ST-28: an imported scroll's rite runs in the importer's own scope."""
    lib = tmp_path / "helpers.god"
    lib.write_text(wrap('DEFINE RITE helper()\nRETURN "helped"\nEND RITE'), encoding="utf-8")
    main = tmp_path / "main.god"
    main.write_text('BEGIN CREATION\nIMPORT "helpers.god"\nREVEAL(helper())\nEND CREATION',
                    encoding="utf-8")
    rc = cli.main(["run", str(main)])
    assert rc == 0


# -- ST-29: the name contract is always available ----------------------------------

def test_st29_contract_needs_no_import():
    """ST-29: contract() is answered by the interpreter itself; the linter never flags it."""
    body = 'DECLARE c AS contract("vow")\nREVEAL(c)'
    assert not has_rule(lint(body), "GC002", "'contract'")
    r = run(body)
    assert r.error is None


# -- ST-30: gentle errors carry did-you-mean counsel -------------------------------

def test_st30_bless_target_counsel():
    """ST-30: a near-miss BLESS target suggests the nearest known name."""
    r = run('DECLARE blessing AS 1\nBLESS blessin')
    assert r.error is not None
    assert "Did you mean 'blessing'" in r.error


def test_st30_missing_map_key_counsel():
    """ST-30: a missing map key names the keys and suggests the nearest one."""
    r = run('DECLARE r AS ANCHOR("grace")\nREVEAL(r["chainn"])')
    assert r.error is not None
    assert "The map holds no 'chainn'" in r.error
    assert "Did you mean 'chain'" in r.error


# -- ST-31: the offending source line is printed ------------------------------------

def test_st31_run_shows_source_line_and_caret(tmp_path, capsys):
    """ST-31: an error prints the offending line, with a caret when the column is known."""
    scroll = tmp_path / "bad.god"
    scroll.write_text(wrap('DECLARE x AS @'), encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cli.main(["run", str(scroll)])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert 'DECLARE x AS @' in err
    assert "^" in err


# -- ST-32: the static promise ------------------------------------------------------

def test_st32_counsel_never_stops_a_run():
    """ST-32: nothing in the static layer stops a scroll; counsel only advises."""
    body = ('DECLARE unused AS 1\nDECLARE twice AS 1\nDECLARE twice AS 2\n'
            'IF 1 IS 1 THEN\nENDIF\nREVEAL("still runs")')
    findings = lint(body)
    assert {"GC001", "GC004", "GC006"} <= {f.rule for f in findings}
    r = run(body)
    assert r.error is None
    assert out(body) == ["still runs"]
