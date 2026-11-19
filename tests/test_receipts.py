"""Tests for replayable receipts (`godcode receipt record|verify`).

A receipt records one sandboxed run with its source and a fingerprint
of its own, so a third party holding only the receipt file can replay
the run and confirm the recorded result. Everything stays inside
tmp_path fixtures; the sandboxed runs write nothing to the host world.
"""

import hashlib
import json

import pytest

from godcode.cli import main
from godcode.receipt import SCHEMA_ID, receipt_hash, record, verify
from godcode.tools import read_schema

jsonschema = pytest.importorskip("jsonschema")

GOOD_SCROLL = (
    "BEGIN CREATION",
    'DECLARE greeting AS "Pula"',
    'REVEAL("blessing: " + greeting)',
    'REVEAL("fingerprint: " + SHA256(greeting))',
    "END CREATION",
)

FAILING_SCROLL = (
    "BEGIN CREATION",
    "BREATHE LIFE INTO missing_name",
    "END CREATION",
)


def _run_cli(*argv, capsys):
    """Run the CLI in-process, return (exit_code, stdout, stderr)."""
    try:
        code = main(list(argv))
    except SystemExit as exc:
        code = exc.code
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_record_holds_source_and_fingerprint():
    source = "\n".join(GOOD_SCROLL) + "\n"
    doc = record(source, source_name="morning.god")
    assert doc["tool"] == "godcode"
    assert doc["command"] == "receipt"
    assert doc["schema"] == SCHEMA_ID
    assert doc["source"] == source
    assert doc["source_sha256"] == hashlib.sha256(
        source.encode("utf-8")).hexdigest()
    assert doc["sandbox"] is True
    assert doc["ok"] is True
    assert doc["output"][0] == "blessing: Pula"
    assert doc["error"] is None
    assert doc["receipt_hash"] == receipt_hash(doc)


def test_record_validates_against_its_schema():
    source = "\n".join(GOOD_SCROLL) + "\n"
    doc = record(source)
    schema = json.loads(read_schema("receipt")[0])
    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(doc)


def test_verify_passes_on_an_untouched_receipt():
    doc = record("\n".join(GOOD_SCROLL) + "\n")
    report = verify(doc)
    assert report["verified"] is True
    assert report["seal_intact"] is True
    assert report["replayed"] is True
    assert report["differences"] == []


def test_verify_refuses_a_tampered_receipt_before_replaying():
    doc = record("\n".join(GOOD_SCROLL) + "\n")
    doc["output"] = ["blessing: changed"]
    report = verify(doc)
    assert report["verified"] is False
    assert report["seal_intact"] is False
    assert report["replayed"] is False
    assert any("fingerprint" in d for d in report["differences"])


def test_verify_catches_a_replay_that_differs():
    doc = record("\n".join(GOOD_SCROLL) + "\n")
    other = "\n".join(GOOD_SCROLL).replace("Pula", "Rain") + "\n"
    doc["source"] = other
    doc["source_sha256"] = hashlib.sha256(other.encode("utf-8")).hexdigest()
    doc["receipt_hash"] = receipt_hash(doc)
    report = verify(doc)
    assert report["verified"] is False
    assert report["seal_intact"] is True
    assert report["replayed"] is True
    assert any("revealed lines differ" in d for d in report["differences"])


def test_verify_rejects_a_receipt_missing_fields():
    report = verify({"command": "receipt", "source": "BEGIN CREATION"})
    assert report["verified"] is False
    assert any("missing" in d for d in report["differences"])


def test_failed_run_records_and_replays_its_failure():
    doc = record("\n".join(FAILING_SCROLL) + "\n")
    assert doc["ok"] is False
    assert doc["error"]["code"] == "RUNTIME_ERROR"
    report = verify(doc)
    assert report["verified"] is True


def test_receipt_example_replays(tmp_path):
    import shutil

    src = tmp_path / "receipt_demo.god"
    shutil.copy("examples/receipt_demo.god", src)
    doc = record(src.read_text(encoding="utf-8"),
                 source_name=str(src), source_dir=str(tmp_path))
    assert doc["ok"] is True
    assert verify(doc)["verified"] is True


def test_cli_record_and_verify_end_to_end(tmp_path, capsys):
    scroll = tmp_path / "morning.god"
    scroll.write_text("\n".join(GOOD_SCROLL) + "\n", encoding="utf-8")
    receipt_path = tmp_path / "morning.receipt.json"
    code, out, _ = _run_cli("receipt", "record", str(scroll),
                            str(receipt_path), capsys=capsys)
    assert code == 0
    assert "Receipt recorded" in out
    doc = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert doc["source_name"] == str(scroll)
    code, out, _ = _run_cli("receipt", "verify", str(receipt_path),
                            capsys=capsys)
    assert code == 0
    assert "replays exactly" in out


def test_cli_record_uses_default_receipt_name(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scroll = tmp_path / "morning.god"
    scroll.write_text("\n".join(GOOD_SCROLL) + "\n", encoding="utf-8")
    code, _, _ = _run_cli("receipt", "record", str(scroll), capsys=capsys)
    assert code == 0
    assert (tmp_path / "morning.receipt.json").is_file()


def test_cli_verify_json_reports_verdict(tmp_path, capsys):
    scroll = tmp_path / "morning.god"
    scroll.write_text("\n".join(GOOD_SCROLL) + "\n", encoding="utf-8")
    receipt_path = tmp_path / "morning.receipt.json"
    _run_cli("receipt", "record", str(scroll), str(receipt_path),
             capsys=capsys)
    code, out, _ = _run_cli("receipt", "verify", str(receipt_path),
                            "--json", capsys=capsys)
    assert code == 0
    report = json.loads(out)
    assert report["verified"] is True
    assert report["command"] == "receipt-verify"
    doc = json.loads(receipt_path.read_text(encoding="utf-8"))
    doc["output"] = ["tampered"]
    receipt_path.write_text(json.dumps(doc), encoding="utf-8")
    code, out, _ = _run_cli("receipt", "verify", str(receipt_path),
                            "--json", capsys=capsys)
    assert code == 1
    assert json.loads(out)["verified"] is False


def test_cli_verify_missing_file_exits_1(capsys):
    code, _, err = _run_cli("receipt", "verify", "/tmp/no-such-receipt.json",
                            capsys=capsys)
    assert code == 1
    assert "cannot read" in err


def test_schema_command_serves_receipt(capsys):
    code, out, _ = _run_cli("schema", capsys=capsys)
    assert code == 0
    assert "receipt" in out
    code, out, _ = _run_cli("schema", "receipt", capsys=capsys)
    assert code == 0
    assert json.loads(out)["$id"] == SCHEMA_ID


def test_schema_names_include_receipt():
    from pathlib import Path

    from godcode.tools import SCHEMA_DATES, SCHEMA_NAMES

    assert SCHEMA_NAMES == ("check", "run", "explain", "ledger-verify",
                            "receipt")
    assert SCHEMA_DATES["receipt"] == "2026-11"
    text, error = read_schema("receipt")
    assert error is None
    assert json.loads(text)["$id"] == SCHEMA_ID
    doc = (Path("docs") / "machine-interfaces.md").read_text(encoding="utf-8")
    assert SCHEMA_ID in doc
