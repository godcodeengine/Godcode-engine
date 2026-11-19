"""Replayable receipts: a checkable record of one sandboxed run.

A receipt is a single JSON document holding everything a third party
needs to re-run a scroll and confirm the recorded result: the source
itself, its fingerprint, the lines the run revealed, whether it finished
cleanly, the failure when it did not, the intents it discerned, and the
permission manifest it ran under. The document carries its own
fingerprint, so any edit to the recorded result breaks the seal and
``verify`` says so plainly instead of replaying a doctored record.

Recording and replaying both run under the strict sandbox policy, so a
receipt never writes to the host world: no ledger blocks, no files, no
network. A receipt is therefore a record of a sandboxed run only. That
is also its honest limit: a scroll that reads the clock, an anchor
timestamp, or any other changing value will replay differently, and
``verify`` reports the mismatch rather than pretending the run matched.
Scrolls that import from their own directory need that directory named
again at verify time with ``--import-dir``; the standard library scrolls
are always available.

The receipt shape is frozen under the dated schema
``https://getgodcode.com/schemas/2026-11/receipt.json``. Required fields
never change meaning; additive fields may appear, and a breaking change
would ship under a new dated schema.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path

SCHEMA_ID = "https://getgodcode.com/schemas/2026-11/receipt.json"


def _canonical(payload) -> bytes:
    """Canonical JSON bytes used for fingerprints (stable key order)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _json_safe(value):
    """Round a value through JSON so a receipt is always serializable."""
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def receipt_hash(receipt: dict) -> str:
    """Fingerprint of a receipt with its own hash field removed."""
    content = {k: v for k, v in receipt.items() if k != "receipt_hash"}
    return hashlib.sha256(_canonical(content)).hexdigest()


def _run_recorded(source: str, source_name: str,
                  source_dir: str | None) -> dict:
    """Run ``source`` sandboxed and muted; return the recorded facts."""
    from godcode import agentics
    from godcode.errors import GodCodeError
    from godcode.sandbox import SandboxPolicy, run_sandboxed_with_interpreter

    policy = SandboxPolicy.strict(source_dir=source_dir)
    output: list[str] = []
    intents: list[dict] = []
    permissions: dict = {}
    error = None
    trace: list[dict] = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            output, interp = run_sandboxed_with_interpreter(
                source, policy, source_name=source_name)
            intents = _json_safe(
                list(getattr(interp, "intent_checks", []) or []))
            manifest = getattr(interp, "manifest", None)
            permissions = manifest.to_json() if manifest else {}
        except GodCodeError as err:
            error = agentics.diagnostic(err)
            trace = agentics.error_trace(err)
    record = {
        "ok": error is None,
        "output": output,
        "error": error,
        "trace": trace,
        "intents": intents,
        "permissions": permissions,
    }
    return record


def record(source: str, source_name: str = "<scroll>",
           source_dir: str | None = None) -> dict:
    """Run ``source`` sandboxed and return its receipt document."""
    run = _run_recorded(source, source_name, source_dir)
    receipt = {
        "tool": "godcode",
        "command": "receipt",
        "schema": SCHEMA_ID,
        "source_name": source_name,
        "source": source,
        "source_sha256": _fingerprint(source),
        "sandbox": True,
        **run,
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    return _json_safe(receipt)


def verify(receipt: dict, import_dir: str | None = None) -> dict:
    """Check a receipt document and replay its source sandboxed.

    Returns a report with ``verified`` true only when the seal is intact
    and the replay matches the record on every compared field: the
    source fingerprint, the clean or failed outcome, the revealed lines,
    and the failure code. A mismatch names each differing field; a
    broken seal stops the check before any replay, so a doctored
    receipt is never laundered through a fresh run.
    """
    report = {
        "tool": "godcode",
        "command": "receipt-verify",
        "verified": False,
        "seal_intact": False,
        "replayed": False,
        "differences": [],
        "replay": None,
    }
    required = ("source", "source_sha256", "ok", "output", "error",
                "receipt_hash")
    missing = [field for field in required if field not in receipt]
    if missing:
        report["differences"] = [
            f"receipt is missing {field}" for field in missing]
        return report
    if receipt.get("source_sha256") != _fingerprint(receipt.get("source", "")):
        report["differences"] = [
            "source fingerprint does not match the recorded source"]
        return report
    if receipt.get("receipt_hash") != receipt_hash(receipt):
        report["differences"] = [
            "receipt fingerprint does not match: the record was changed "
            "after it was recorded"]
        return report
    report["seal_intact"] = True

    replay = _run_recorded(receipt["source"],
                           receipt.get("source_name", "<scroll>"),
                           import_dir)
    report["replayed"] = True
    report["replay"] = replay
    differences: list[str] = []
    if replay["ok"] != receipt["ok"]:
        differences.append(
            f"outcome differs: recorded ok is {receipt['ok']}, "
            f"replay ok is {replay['ok']}")
    if replay["output"] != receipt["output"]:
        differences.append(
            f"revealed lines differ: recorded {receipt['output']!r}, "
            f"replay {replay['output']!r}")
    recorded_code = (receipt["error"] or {}).get("code")
    replay_code = (replay["error"] or {}).get("code")
    if recorded_code != replay_code:
        differences.append(
            f"failure code differs: recorded {recorded_code}, "
            f"replay {replay_code}")
    report["differences"] = differences
    report["verified"] = not differences
    return report


def load_receipt(path: str | Path) -> tuple[dict | None, str | None]:
    """Read a receipt file; return (document, error message)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read '{path}': {exc.strerror or exc}"
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"'{path}' is not a receipt document: {exc}"
    if not isinstance(doc, dict) or doc.get("command") != "receipt":
        return None, f"'{path}' is not a receipt document"
    return doc, None
