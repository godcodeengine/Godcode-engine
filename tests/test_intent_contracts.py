"""Tests for the contract clauses: REQUIRE / ENSURE / NEVER.

The checkable half of a rite's promise. DECLARE INTENT speaks a rite's
purpose in prose and the Spirit counsels on drift; a clause binds.
REQUIRE is weighed at the rite's door (parameters bound, body not yet
run), ENSURE as the work ends (the body's names still in scope), NEVER
at both doors. A broken clause raises ContractError and fails the run;
every clause weighed leaves a record in the run report's `contracts`
array. Spec rules SX-40 to SX-45 (docs/spec/syntax.md) name the law
these tests keep.
"""

import json

import pytest

from godcode import cli
from godcode.ast import ContractClause, DefineRite
from godcode.errors import ContractError, GodRuntimeError, ParseError
from godcode.interpreter import Interpreter
from godcode.lexer import Lexer
from godcode.parser import Parser
from godcode.spirit import SpiritEngine


def _parse(src):
    return Parser(Lexer(src).lex()).parse()


def _creation(src):
    program = _parse(src)
    return program.statements[0].statements


def _interp(spirit=False):
    return Interpreter(
        spirit=SpiritEngine() if spirit else None, log_path=None)


def _run(src, spirit=False):
    interp = _interp(spirit=spirit)
    interp.run_source(src)
    return interp


BAKE = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    REQUIRE loaves > 0
    ENSURE loaves IS 5
    NEVER loaves < 0
    REVEAL("the oven holds {{loaves}} loaves")
  END RITE
  INVOKE bake({n})
END CREATION
"""


# ------------------------------------------------------------------ parsing

class TestClauseParsing:
    def test_clauses_are_collected_into_the_contract(self):
        """SX-40: clauses leave the body and gather into the contract."""
        (rite,) = [s for s in _creation(BAKE.format(n=5))
                   if isinstance(s, DefineRite)]
        assert [c.kind for c in rite.contract] == ["REQUIRE", "ENSURE", "NEVER"]
        assert all(isinstance(c, ContractClause) for c in rite.contract)
        # The body holds only the work, never the clauses.
        assert len(rite.body) == 1

    def test_clause_order_is_the_written_order(self):
        src = """\
BEGIN CREATION
  DEFINE RITE guarded(x)
    NEVER x IS 99
    REQUIRE x > 0
    ENSURE x > 1
    REVEAL(x)
  END RITE
END CREATION
"""
        (rite,) = [s for s in _creation(src) if isinstance(s, DefineRite)]
        assert [c.kind for c in rite.contract] == ["NEVER", "REQUIRE", "ENSURE"]

    def test_clause_written_after_return_is_still_collected(self):
        """SX-40: a clause is a declaration, not a step; position is free."""
        src = """\
BEGIN CREATION
  DEFINE RITE guarded(x)
    RETURN x
    REQUIRE x > 0
  END RITE
  INVOKE guarded(0)
END CREATION
"""
        with pytest.raises(ContractError):
            _run(src)

    def test_clause_outside_a_rite_is_a_parse_error(self):
        """SX-41: a clause at the top level of a creation is refused."""
        with pytest.raises(ParseError) as excinfo:
            _parse("BEGIN CREATION\n  REQUIRE 1 IS 1\nEND CREATION\n")
        assert "inside a rite body" in str(excinfo.value)

    def test_clause_in_a_bare_fragment_is_a_parse_error(self):
        with pytest.raises(ParseError):
            _parse("ENSURE 1 IS 1\n")

    def test_clause_nested_in_an_if_is_a_parse_error(self):
        """SX-41: clauses belong to the rite, not to a branch within it."""
        src = """\
BEGIN CREATION
  DEFINE RITE guarded(x)
    IF x > 0 THEN
      REQUIRE x > 1
    ENDIF
  END RITE
END CREATION
"""
        with pytest.raises(ParseError):
            _parse(src)

    def test_keywords_are_case_insensitive(self):
        src = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    require loaves > 0
    REVEAL(loaves)
  END RITE
  INVOKE bake(2)
END CREATION
"""
        interp = _run(src)
        assert interp.output == ["2"]
        assert interp.contract_checks[0]["kind"] == "REQUIRE"


# ------------------------------------------------------------------ REQUIRE

class TestRequire:
    def test_require_failure_stops_the_body_and_fails_the_run(self):
        """SX-42 / proof 1: bake(0) breaks REQUIRE; the body never speaks."""
        interp = _interp()
        with pytest.raises(ContractError) as excinfo:
            interp.run_source(BAKE.format(n=0))
        assert interp.output == []  # the oven line was never revealed
        err = excinfo.value
        assert "bake" in str(err)
        assert "REQUIRE loaves > 0" in str(err)
        assert "loaves = 0" in str(err)
        (record,) = interp.contract_checks
        assert record == {"rite": "bake", "kind": "REQUIRE",
                          "text": "loaves > 0", "passed": False}

    def test_require_passes_and_the_rite_runs(self):
        interp = _run(BAKE.format(n=5))
        assert interp.output == ["the oven holds 5 loaves"]

    def test_require_reads_the_closure(self):
        src = """\
BEGIN CREATION
  DECLARE threshold AS 3
  DEFINE RITE weigh(n)
    REQUIRE n >= threshold
    RETURN n
  END RITE
  REVEAL(weigh(2))
END CREATION
"""
        with pytest.raises(ContractError):
            _run(src)


# ------------------------------------------------------------------ ENSURE

class TestEnsure:
    def test_ensure_failure_fails_the_run_after_the_work(self):
        """SX-43 / proof 3a: the body ran, then the promise was weighed."""
        src = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    ENSURE loaves IS 5
    REVEAL("the oven holds {loaves} loaves")
  END RITE
  INVOKE bake(3)
END CREATION
"""
        interp = _interp()
        with pytest.raises(ContractError) as excinfo:
            interp.run_source(src)
        # The work happened; the run still fails.
        assert interp.output == ["the oven holds 3 loaves"]
        assert "ENSURE loaves == 5" in str(excinfo.value)
        assert "loaves = 3" in str(excinfo.value)

    def test_ensure_sees_names_the_body_declared(self):
        """SX-43: ENSURE is weighed in the rite's frame, body names in scope."""
        src = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    DECLARE total AS loaves * 2
    ENSURE total IS 10
    RETURN total
  END RITE
  REVEAL(bake(5))
END CREATION
"""
        interp = _run(src)
        assert interp.output == ["10"]

    def test_ensure_is_weighed_after_a_return(self):
        src = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    ENSURE loaves > 100
    RETURN loaves
  END RITE
  REVEAL(bake(5))
END CREATION
"""
        with pytest.raises(ContractError):
            _run(src)


# ------------------------------------------------------------------ NEVER

class TestNever:
    def test_never_failure_at_the_door(self):
        """SX-44 / proof 3b: what was sworn never to be, already was."""
        src = """\
BEGIN CREATION
  DEFINE RITE lend(debt)
    NEVER debt > 0
    REVEAL("lent in peace")
  END RITE
  INVOKE lend(5)
END CREATION
"""
        interp = _interp()
        with pytest.raises(ContractError) as excinfo:
            interp.run_source(src)
        assert interp.output == []
        assert "NEVER debt > 0" in str(excinfo.value)
        assert "as the rite began" in str(excinfo.value)

    def test_never_failure_at_the_exit(self):
        """SX-44: NEVER is weighed again as the work ends."""
        src = """\
BEGIN CREATION
  DEFINE RITE lend(debt)
    NEVER debt > 0
    DECLARE debt AS 5
    REVEAL("lent")
  END RITE
  INVOKE lend(0)
END CREATION
"""
        interp = _interp()
        with pytest.raises(ContractError) as excinfo:
            interp.run_source(src)
        assert interp.output == ["lent"]  # the work happened first
        assert "as the rite ended" in str(excinfo.value)
        # Weighed at both doors: passed at entry, failed at exit.
        assert [c["passed"] for c in interp.contract_checks] == [True, False]

    def test_never_holds_at_both_doors(self):
        interp = _run(BAKE.format(n=5))
        nevers = [c for c in interp.contract_checks if c["kind"] == "NEVER"]
        assert len(nevers) == 2
        assert all(c["passed"] for c in nevers)


# ------------------------------------------------------------- the report

class TestContractsReport:
    def test_all_clauses_recorded_in_threshold_order(self):
        """Proof 2: the passing run's contracts array shows every clause."""
        interp = _run(BAKE.format(n=5))
        assert interp.contract_checks == [
            {"rite": "bake", "kind": "REQUIRE", "text": "loaves > 0",
             "passed": True},
            {"rite": "bake", "kind": "NEVER", "text": "loaves < 0",
             "passed": True},
            {"rite": "bake", "kind": "ENSURE", "text": "loaves == 5",
             "passed": True},
            {"rite": "bake", "kind": "NEVER", "text": "loaves < 0",
             "passed": True},
        ]

    def _write(self, tmp_path, text):
        path = tmp_path / "scroll.god"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def _main_json(self, argv, capsys):
        try:
            rc = cli.main(argv)
        except SystemExit as exc:
            rc = exc.code
        return rc, json.loads(capsys.readouterr().out)

    def test_run_json_carries_contracts_and_contract_error(self, tmp_path, capsys):
        path = self._write(tmp_path, BAKE.format(n=0))
        rc, doc = self._main_json(["run", "--json", path], capsys)
        assert rc == 1
        assert doc["ok"] is False
        assert doc["error"]["code"] == "CONTRACT_ERROR"
        assert doc["output"] == []
        assert doc["contracts"] == [
            {"rite": "bake", "kind": "REQUIRE", "text": "loaves > 0",
             "passed": False},
        ]

    def test_run_json_passing_contracts(self, tmp_path, capsys):
        path = self._write(tmp_path, BAKE.format(n=5))
        rc, doc = self._main_json(["run", "--json", path], capsys)
        assert rc == 0
        assert doc["ok"] is True
        assert len(doc["contracts"]) == 4
        assert all(c["passed"] for c in doc["contracts"])

    def test_sandbox_json_matches(self, tmp_path, capsys):
        """SX-45: the sandbox weighs clauses exactly as the open run does."""
        path = self._write(tmp_path, BAKE.format(n=0))
        rc, doc = self._main_json(["run", "--sandbox", "--json", path], capsys)
        assert rc == 1
        assert doc["error"]["code"] == "CONTRACT_ERROR"
        assert doc["contracts"][0]["passed"] is False

        path = self._write(tmp_path, BAKE.format(n=5))
        rc, doc = self._main_json(["run", "--sandbox", "--json", path], capsys)
        assert rc == 0
        assert len(doc["contracts"]) == 4

    def test_check_json_names_the_clause_parse_error(self, tmp_path, capsys):
        path = self._write(
            tmp_path, "BEGIN CREATION\n  REQUIRE 1 IS 1\nEND CREATION\n")
        rc, doc = self._main_json(["check", "--json", path], capsys)
        assert rc == 1
        assert doc["ok"] is False
        assert doc["diagnostics"][0]["code"] == "PARSE_ERROR"


# ------------------------------------------------------------------ sandbox

class TestSandbox:
    def test_sandbox_weighs_clauses_the_same(self):
        from godcode.sandbox import run_sandboxed_with_interpreter

        output, interp = run_sandboxed_with_interpreter(BAKE.format(n=5))
        assert output == ["the oven holds 5 loaves"]
        assert len(interp.contract_checks) == 4

        with pytest.raises(ContractError):
            run_sandboxed_with_interpreter(BAKE.format(n=0))


# ------------------------------------------------------------------ tongues

class TestTongues:
    def test_english_clauses_beside_tongue_keywords(self):
        """SX-45: clause words are English in every tongue, for now.

        The tongue equivalents of REQUIRE / ENSURE / NEVER are the
        founder's to vet and are not yet spoken.
        """
        src = """\
# tongue: tn
SIMOLOLA TLHOLEGO
  TLHALOSA TIRO bake(loaves)
    REQUIRE loaves > 0
    SENOLA("the oven holds {loaves} loaves")
  FEDISA TIRO
  INVOKE bake(3)
FEDISA TLHOLEGO
"""
        interp = _run(src)
        assert interp.output == ["the oven holds 3 loaves"]
        assert interp.contract_checks[0]["kind"] == "REQUIRE"


# ------------------------------------------------------- intent interplay

class TestIntentInterplay:
    def test_a_broken_clause_marks_the_intent_unaligned(self):
        src = """\
BEGIN CREATION
  DECLARE INTENT "bring peace to the household" ON evening_blessing
  DEFINE RITE evening_blessing()
    ENSURE 1 IS 2
    REVEAL("peace upon this house")
  END RITE
  INVOKE evening_blessing()
END CREATION
"""
        interp = _interp(spirit=True)
        with pytest.raises(ContractError):
            interp.run_source(src)
        (check,) = interp.intent_checks
        assert check["rite"] == "evening_blessing"
        assert check["aligned"] is False

    def test_intent_alone_still_never_fails_a_run(self):
        # DECLARE INTENT without clauses keeps its old law: counsel only.
        src = """\
BEGIN CREATION
  DECLARE INTENT "bring peace to the household" ON war_drum
  DEFINE RITE war_drum()
    DECLARE tally AS 1 + 2
    REVEAL(tally)
  END RITE
  INVOKE war_drum()
END CREATION
"""
        interp = _run(src, spirit=True)
        assert interp.output == ["3"]
        assert interp.contract_checks == []


# ------------------------------------------------------------------ fmt

class TestFormatter:
    def test_fmt_reemits_clauses_at_the_head_of_the_body(self):
        from godcode.cli import CanonicalFormatter
        from godcode.tongues import parse_source

        formatted = CanonicalFormatter().format(parse_source(BAKE.format(n=5)))
        lines = [line.strip() for line in formatted.splitlines()]
        rite_at = lines.index("DEFINE RITE bake(loaves)")
        assert lines[rite_at + 1] == "REQUIRE loaves > 0"
        assert lines[rite_at + 2] == "ENSURE loaves == 5"
        assert lines[rite_at + 3] == "NEVER loaves < 0"
        # And the formatted scroll parses back to the same contract.
        (rite,) = [s for s in _creation(formatted)
                   if isinstance(s, DefineRite)]
        assert [c.kind for c in rite.contract] == ["REQUIRE", "ENSURE", "NEVER"]

    def test_contract_error_is_a_runtime_error(self):
        # TRY/CATCH at a call site may shelter a broken clause, as it
        # shelters any runtime failure.
        assert issubclass(ContractError, GodRuntimeError)
        src = """\
BEGIN CREATION
  DEFINE RITE bake(loaves)
    REQUIRE loaves > 0
    REVEAL("baked")
  END RITE
  TRY
    INVOKE bake(0)
  CATCH
    REVEAL("the covenant was broken, and we are sheltered")
  ENDTRY
END CREATION
"""
        interp = _run(src)
        assert interp.output == ["the covenant was broken, and we are sheltered"]
