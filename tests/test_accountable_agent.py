"""Tests for the accountable agent flagship demo.

The demo is an agent given exactly one folder: it declares a single
read permission, the invoker grants the host read for that folder
only, and the run is sandboxed. Either layer refusing stops the run.
Everything runs inside a copied examples/ tree, so no real folder
outside the fixture is ever touched.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from godcode.sandbox import SandboxPolicy

REPO = Path(__file__).resolve().parent.parent
DATA = "examples/accountable_agent_data"
SCROLL = "examples/accountable_agent.god"


@pytest.fixture()
def examples_tree(tmp_path):
    """Copy the whole examples/ tree into tmp_path; return tmp_path."""
    shutil.copytree(REPO / "examples", tmp_path / "examples")
    return tmp_path


def _run_cli(*argv, cwd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "godcode", *argv],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _expected_fingerprint(tree):
    """The report fingerprint the demo must reveal, from first principles."""
    folder = tree / DATA
    ledger = ""
    for name in sorted(os.listdir(folder)):
        text = (folder / name).read_text(encoding="utf-8")
        ledger += name + "=" + hashlib.sha256(text.encode()).hexdigest() + ";"
    return hashlib.sha256(ledger.encode()).hexdigest()


def test_runs_sandboxed_with_one_grant(examples_tree):
    proc = _run_cli("run", "--sandbox", "--allow-read", DATA, SCROLL,
                    cwd=examples_tree)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    for name in ("field-notes-1.txt", "field-notes-2.txt",
                 "market-prices.txt"):
        assert name in out
    assert "Files counted: 3" in out
    assert "Total characters: 307" in out
    assert re.search(r"fingerprinted [0-9a-f]{64}\.", out)
    assert _expected_fingerprint(examples_tree) in out


def test_sandboxed_report_is_deterministic(examples_tree):
    """Two sandboxed runs reveal exactly the same lines: re-runnable proof."""
    argv = ["run", "--sandbox", "--allow-read", DATA, "--json", SCROLL]
    first = _run_cli(*argv, cwd=examples_tree)
    second = _run_cli(*argv, cwd=examples_tree)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert json.loads(first.stdout)["output"] == \
        json.loads(second.stdout)["output"]


def test_permissions_show_a_single_read_grant(examples_tree):
    proc = _run_cli("permissions", "--json", SCROLL, cwd=examples_tree)
    assert proc.returncode == 0, proc.stderr
    manifest = json.loads(proc.stdout)["manifest"]
    assert len(manifest["read"]) == 1
    assert manifest["read"][0].endswith("accountable_agent_data")
    assert manifest["write"] == []
    assert manifest["network"] == []
    assert manifest["stdin"] is False
    assert manifest["summon"] == []


def test_sandbox_without_grant_is_refused(examples_tree):
    proc = _run_cli("run", "--sandbox", SCROLL, cwd=examples_tree)
    assert proc.returncode == 1
    assert "withholds" in proc.stderr or "not granted" in proc.stderr


def test_reaching_outside_the_grant_is_refused(examples_tree):
    """A scroll that reaches past the granted folder is stopped."""
    scroll = examples_tree / SCROLL
    text = scroll.read_text(encoding="utf-8")
    text = text.replace(
        'DECLARE data_dir AS "examples/accountable_agent_data"',
        'DECLARE data_dir AS "examples/data"')
    scroll.write_text(text, encoding="utf-8")
    proc = _run_cli("run", "--sandbox", "--allow-read", DATA, SCROLL,
                    cwd=examples_tree)
    assert proc.returncode == 1
    assert "withholds" in proc.stderr or "did not declare" in proc.stderr


def test_manifest_alone_refuses_on_a_plain_run(examples_tree):
    """Even with an open host, the declared manifest narrows the run."""
    scroll = examples_tree / SCROLL
    text = scroll.read_text(encoding="utf-8")
    text = text.replace(
        'DECLARE data_dir AS "examples/accountable_agent_data"',
        'DECLARE data_dir AS "examples/data"')
    scroll.write_text(text, encoding="utf-8")
    proc = _run_cli("run", SCROLL, cwd=examples_tree)
    assert proc.returncode == 1
    assert "did not declare" in proc.stderr


def test_allow_read_without_sandbox_is_a_usage_error(examples_tree):
    proc = _run_cli("run", "--allow-read", DATA, SCROLL, cwd=examples_tree)
    assert proc.returncode == 2
    assert "--sandbox" in proc.stderr


def test_strict_policy_read_grant_defaults_to_denied():
    assert SandboxPolicy.strict().allow_read_paths is None
    policy = SandboxPolicy.strict(allow_read_paths=("some/folder",))
    assert policy.allow_read_paths == ("some/folder",)
