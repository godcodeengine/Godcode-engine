"""Tests for the October 2026 machine interfaces.

Four dated JSON schemas freeze the --json shapes of check, run, explain,
and ledger verify; `godcode schema` serves them; the bridge carries
`explain` and `get_schema`. Everything stays inside tmp_path fixtures;
the repo's real chain files are never touched.
"""

import json

import pytest

from godcode.cli import main
from godcode.tools import SCHEMA_NAMES, call_tool, read_schema

jsonschema = pytest.importorskip("jsonschema")

SCHEMA_DIR = "godcode/schemas/2026-10"


def _scroll(tmp_path, name, *lines):
    path = tmp_path / name
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run_json(capsys, *argv):
    """Run the CLI in-process, return (exit_code, parsed stdout JSON)."""
    try:
        code = main(list(argv))
    except SystemExit as exc:
        code = exc.code
    doc = json.loads(capsys.readouterr().out)
    return code, doc


def _run_cli(*argv):
    """Run the CLI in-process, return the exit code."""
    try:
        return main(list(argv))
    except SystemExit as exc:
        return exc.code


def _validate(name, doc):
    from pathlib import Path

    schema = json.loads(
        (Path(SCHEMA_DIR) / f"{name}.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(doc)
    return schema


RICH_SCROLL = (
    "BEGIN CREATION",
    'DECLARE PERMISSION TO READ "data/"',
    'DECLARE greeting AS "Pula"',
    "DEFINE RITE greet(name)",
    '  DECLARE word AS "hello"',
    '  REVEAL("{word} {name}")',
    "END RITE",
    'DECLARE INTENT "to greet the day warmly" ON greet',
    "SEAL(greeting)",
    "DECLARE receipt AS ANCHOR(greeting)",
    'DECLARE counsel AS CONSULT("What is my work today?")',
    'SUMMON("clockwork.now")',
    'IMPORT "blessings"',
    "END CREATION",
)

TONGUE_SCROLL = (
    "# tongue: tn",
    "SIMOLOLA TLHOLEGO",
    "BOLELA x JAAKA 3",
    "SENOLA(x)",
    'SENOLA(CONSULT("bless"))',
    "FEDISA TLHOLEGO",
)


# ---------------------------------------------------------------- schemas

def test_schema_files_are_valid_draft_2020_12():
    from pathlib import Path

    for name in ("check", "run", "explain", "ledger-verify"):
        text = (Path(SCHEMA_DIR) / f"{name}.json").read_text(encoding="utf-8")
        schema = json.loads(text)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        jsonschema.Draft202012Validator.check_schema(schema)


def test_schema_ids_are_date_based_and_documented():
    from pathlib import Path

    doc = (Path("docs") / "machine-interfaces.md").read_text(encoding="utf-8")
    for name in ("check", "run", "explain", "ledger-verify"):
        schema = json.loads(
            (Path(SCHEMA_DIR) / f"{name}.json").read_text(encoding="utf-8"))
        assert "2026-10" in schema["$id"], name
        assert schema["$id"] in doc, f"{name} $id missing from docs"


# ---------------------------------------------------------------- check

def test_check_ok_validates(tmp_path, capsys):
    scroll = _scroll(tmp_path, "pure.god", "BEGIN CREATION",
                     'REVEAL("Pula")', "END CREATION")
    code, doc = _run_json(capsys, "check", "--json", str(scroll))
    assert code == 0
    assert doc["ok"] is True
    _validate("check", doc)


def test_check_diagnostic_validates(tmp_path, capsys):
    scroll = _scroll(tmp_path, "broken.god", "BEGIN CREATION",
                     'REVEAL("unclosed', "END CREATION")
    code, doc = _run_json(capsys, "check", "--json", str(scroll))
    assert code == 1
    assert doc["ok"] is False
    assert doc["diagnostics"] and doc["diagnostics"][0]["code"] == "LEXER_ERROR"
    _validate("check", doc)


# ---------------------------------------------------------------- run

def test_run_sandbox_ok_validates(tmp_path, capsys):
    scroll = _scroll(tmp_path, "calm.god", *TONGUE_SCROLL)
    code, doc = _run_json(capsys, "run", "--sandbox", "--json", str(scroll))
    assert code == 0
    assert doc["ok"] is True
    assert doc["error"] is None
    _validate("run", doc)


def test_run_sandbox_runtime_error_validates(tmp_path, capsys):
    scroll = _scroll(tmp_path, "void.god", "BEGIN CREATION",
                     "DECLARE x AS 1 / 0", "REVEAL(x)", "END CREATION")
    code, doc = _run_json(capsys, "run", "--sandbox", "--json", str(scroll))
    assert code == 1
    assert doc["ok"] is False
    assert doc["error"]["code"] == "RUNTIME_ERROR"
    _validate("run", doc)


# ---------------------------------------------------------------- explain

def test_explain_rich_scroll_validates(tmp_path, capsys):
    scroll = _scroll(tmp_path, "morning.god", *RICH_SCROLL)
    code, doc = _run_json(capsys, "explain", "--json", str(scroll))
    assert code == 0
    assert doc["ok"] is True
    assert doc["tongue"] == {"code": "en", "name": "English"}
    assert [r["name"] for r in doc["rites"]] == ["greet"]
    assert doc["rites"][0]["params"] == ["name"]
    assert doc["rites"][0]["intent"] == "to greet the day warmly"
    assert doc["intents"] == [
        {"rite": "greet", "text": "to greet the day warmly", "line": 8}]
    assert {d["name"] for d in doc["declarations"]} >= {
        "greeting", "word", "receipt", "counsel"}
    assert len(doc["reveals"]) == 1
    assert sorted(s["kind"] for s in doc["seals"]) == ["ANCHOR", "SEAL"]
    assert doc["summons"] == [{"verb": "clockwork.now", "line": 12}]
    assert len(doc["consults"]) == 1
    assert doc["imports"] == [{"path": "blessings", "line": 13}]
    assert doc["permissions"]["read"] != []
    _validate("explain", doc)


def test_explain_tongue_scroll_reports_tongue(tmp_path, capsys):
    scroll = _scroll(tmp_path, "tn.god", *TONGUE_SCROLL)
    code, doc = _run_json(capsys, "explain", "--json", str(scroll))
    assert code == 0
    assert doc["tongue"] == {"code": "tn", "name": "Setswana"}
    assert len(doc["consults"]) == 1
    _validate("explain", doc)


def test_explain_missing_file_exit_1(tmp_path, capsys):
    code, doc = _run_json(capsys, "explain", "--json",
                          str(tmp_path / "nope.god"))
    assert code == 1
    assert doc["ok"] is False
    assert doc["diagnostics"][0]["code"] == "FILE_ERROR"
    _validate("explain", doc)


def test_explain_human_words(tmp_path, capsys):
    scroll = _scroll(tmp_path, "morning.god", *RICH_SCROLL)
    assert _run_cli("explain", str(scroll)) == 0
    out = capsys.readouterr().out
    assert "in plain words" in out
    assert "greet" in out and "to greet the day warmly" in out
    assert "—" not in out


# ---------------------------------------------------------------- ledger verify

def test_ledger_verify_json_ok(tmp_path, capsys):
    code, doc = _run_json(
        capsys, "ledger", "verify",
        "--file", str(tmp_path / "covenant.chain"),
        "--anchor-file", str(tmp_path / "anchors.chain"),
        "--json")
    assert code == 0
    assert doc == {
        "tool": "godcode", "command": "ledger", "subcommand": "verify",
        "ok": True,
        "covenant": {"ok": True, "message": doc["covenant"]["message"]},
        "anchors": {"ok": True, "message": doc["anchors"]["message"]},
    }
    _validate("ledger-verify", doc)


def test_ledger_verify_json_tampered(tmp_path, capsys):
    from godcode.ledger import CovenantLedger

    chain = tmp_path / "covenant.chain"
    CovenantLedger(str(chain)).seal({"word": "test"})
    block = json.loads(chain.read_text(encoding="utf-8").splitlines()[0])
    block["record"]["word"] = "forged"
    chain.write_text(json.dumps(block) + "\n", encoding="utf-8")
    code, doc = _run_json(
        capsys, "ledger", "verify",
        "--file", str(chain),
        "--anchor-file", str(tmp_path / "anchors.chain"),
        "--json")
    assert code == 1
    assert doc["ok"] is False
    assert doc["covenant"]["ok"] is False
    assert doc["anchors"]["ok"] is True
    _validate("ledger-verify", doc)


# ---------------------------------------------------------------- schema command

def test_schema_lists_four_names(capsys):
    assert _run_cli("schema") == 0
    out = capsys.readouterr().out
    for name in ("check", "run", "explain", "ledger-verify"):
        assert name in out


def test_schema_explain_prints_matching_id(capsys):
    code_text, error = read_schema("explain")
    assert error is None
    assert _run_cli("schema", "explain") == 0
    doc = json.loads(capsys.readouterr().out)
    assert doc["$id"] == "https://getgodcode.com/schemas/2026-10/explain.json"
    assert doc["$id"] == json.loads(code_text)["$id"]


def test_schema_bogus_exits_1(capsys):
    assert _run_cli("schema", "bogus") == 1
    err = capsys.readouterr().err
    assert "no schema named 'bogus'" in err


def test_schema_bogus_json_envelope(capsys):
    code, doc = _run_json(capsys, "schema", "bogus", "--json")
    assert code == 1
    assert doc == {"tool": "godcode", "command": "schema", "ok": False,
                   "error": "no schema named 'bogus'"}


# ---------------------------------------------------------------- bridge

def test_bridge_explain(tmp_path):
    scroll = _scroll(tmp_path, "morning.god", *RICH_SCROLL)
    result = call_tool("explain", {"file": str(scroll)})
    assert result["ok"] is True
    assert result["tongue"] == {"code": "en", "name": "English"}
    assert [r["name"] for r in result["rites"]] == ["greet"]
    assert "tool" not in result  # facts only, no envelope


def test_bridge_explain_missing_file():
    result = call_tool("explain", {"file": "/tmp/no-such-scroll.god"})
    assert result["ok"] is False
    assert "error" in result


def test_bridge_get_schema():
    result = call_tool("get_schema", {"name": "run"})
    assert result["ok"] is True
    assert result["schema"]["$id"] == \
        "https://getgodcode.com/schemas/2026-10/run.json"


def test_bridge_get_schema_unknown():
    result = call_tool("get_schema", {"name": "bogus"})
    assert result["ok"] is False
    assert "error" in result


def test_bridge_lists_nine_tools():
    assert SCHEMA_NAMES == ("check", "run", "explain", "ledger-verify")
    from godcode.tools import TOOL_SCHEMAS

    assert [t["name"] for t in TOOL_SCHEMAS] == [
        "check", "run", "consult", "intent", "anchor_verify",
        "ledger_verify", "permissions", "explain", "get_schema",
    ]
