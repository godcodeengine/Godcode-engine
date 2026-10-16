"""Tests for permission manifests (DECLARE PERMISSION TO ...).

A scroll declares what it may touch; the engine enforces it. The
manifest never widens the host policy: the effective grant is always
host policy intersect manifest. Everything stays inside tmp_path
fixtures; no real network is touched.
"""

import json
import os

import pytest

from godcode.errors import GodCodeError, SandboxViolation
from godcode.interpreter import Interpreter
from godcode.permissions import PermissionManifest, collect_manifest
from godcode.sandbox import SandboxPolicy, run_sandboxed
from godcode.tongues import parse_source


def _manifest_of(source: str, base_dir):
    return collect_manifest(parse_source(source).statements, base_dir)


def _run(source: str, tmp_path, **kwargs):
    """Run source with the scroll's directory as tmp_path."""
    scroll = tmp_path / "scroll.god"
    scroll.write_text(source, encoding="utf-8")
    interp = Interpreter(log_path=None, **kwargs)
    lines: list[str] = []
    interp.emit = lines.append
    interp.run_source(source, source_name=str(scroll))
    return lines, interp


# ---------------------------------------------------------------- parsing

def test_parse_all_five_powers(tmp_path):
    manifest = _manifest_of(
        'DECLARE PERMISSION TO READ "data/"\n'
        'DECLARE PERMISSION TO WRITE "out/"\n'
        'DECLARE PERMISSION TO SPEAK WITH "api.example.com"\n'
        "DECLARE PERMISSION TO ASK THE WORLD\n"
        'DECLARE PERMISSION TO SUMMON "reports.weekly"\n',
        tmp_path,
    )
    assert manifest.read_paths == (os.path.realpath(tmp_path / "data"),)
    assert manifest.write_paths == (os.path.realpath(tmp_path / "out"),)
    assert manifest.hosts == ("api.example.com",)
    assert manifest.stdin is True
    assert manifest.summons == ("reports.weekly",)


def test_parse_inside_creation_block(tmp_path):
    manifest = _manifest_of(
        'BEGIN CREATION\n  DECLARE PERMISSION TO READ "data/"\nEND CREATION\n',
        tmp_path,
    )
    assert manifest.read_paths == (os.path.realpath(tmp_path / "data"),)


def test_parse_unknown_power_is_counselled():
    with pytest.raises(GodCodeError) as exc:
        parse_source('DECLARE PERMISSION TO FLY "nowhere"\n')
    assert "READ" in str(exc.value) and "FLY" in str(exc.value)


def test_declare_permission_as_name_still_works():
    # Soft keywords must not steal ordinary declarations.
    program = parse_source('DECLARE permission AS "mine"\nREVEAL(permission)\n')
    assert program.statements[0].name == "permission"


def test_to_json_shape(tmp_path):
    manifest = _manifest_of(
        'DECLARE PERMISSION TO SPEAK WITH "API.Example.COM"\n'
        "DECLARE PERMISSION TO ASK THE WORLD\n",
        tmp_path,
    )
    assert manifest.to_json() == {
        "read": [], "write": [], "network": ["api.example.com"],
        "stdin": True, "summon": [],
    }


def test_merge_unions_grants(tmp_path):
    first = _manifest_of('DECLARE PERMISSION TO READ "a/"\n', tmp_path)
    second = _manifest_of(
        'DECLARE PERMISSION TO READ "a/"\nDECLARE PERMISSION TO WRITE "b/"\n',
        tmp_path,
    )
    merged = first.merge(second)
    assert merged.read_paths == first.read_paths
    assert merged.write_paths == second.write_paths
    assert not merged.stdin
    assert bool(merged) and not bool(PermissionManifest())


# ------------------------------------------------------------- enforcement

def test_declared_read_grants_access(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    lines, interp = _run(
        'DECLARE PERMISSION TO READ "data/"\n'
        'REVEAL(READ_FILE("data/note.txt"))\n',
        tmp_path,
    )
    assert lines == ["psalm"]
    assert interp.manifest.read_paths


def test_undeclared_read_is_withheld(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    with pytest.raises(SandboxViolation) as exc:
        _run('REVEAL(READ_FILE("data/note.txt"))\n'
             'DECLARE PERMISSION TO READ "elsewhere/"\n', tmp_path)
    assert "did not declare" in str(exc.value)


def test_undeclared_write_is_withheld(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SandboxViolation):
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'WRITE_FILE("out/evil.txt", "nope")\n', tmp_path)


def test_declared_write_grants_access(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "out").mkdir()
    lines, _ = _run(
        'DECLARE PERMISSION TO WRITE "out/"\n'
        'WRITE_FILE("out/blessing.txt", "amen")\n'
        'REVEAL("written")\n',
        tmp_path,
    )
    assert lines == ["written"]
    assert (tmp_path / "out" / "blessing.txt").read_text() == "amen"


def test_write_outside_declared_dir_is_withheld(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "out").mkdir()
    with pytest.raises(SandboxViolation):
        _run('DECLARE PERMISSION TO WRITE "out/"\n'
             'WRITE_FILE("escape.txt", "nope")\n', tmp_path)


def test_undeclared_ask_is_withheld(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "x")
    with pytest.raises(SandboxViolation):
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'REVEAL(ASK("who goes there?"))\n', tmp_path)


def test_declared_ask_grants_access(tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "ruth")
    lines, _ = _run(
        "DECLARE PERMISSION TO ASK THE WORLD\n"
        'REVEAL("well met, " + ASK("who goes there?"))\n',
        tmp_path,
    )
    assert lines == ["well met, ruth"]


def test_undeclared_summon_is_withheld(tmp_path):
    interp = Interpreter(log_path=None)
    interp._plugin_verbs["reports.weekly"] = lambda args, line: "ok"
    scroll = tmp_path / "scroll.god"
    source = ('DECLARE PERMISSION TO READ "data/"\n'
              'SUMMON("reports.weekly")\n')
    scroll.write_text(source, encoding="utf-8")
    with pytest.raises(SandboxViolation):
        interp.run_source(source, source_name=str(scroll))


def test_declared_summon_grants_access(tmp_path):
    interp = Interpreter(log_path=None)
    interp._plugin_verbs["reports.weekly"] = lambda args, line: "sealed"
    lines: list[str] = []
    interp.emit = lines.append
    scroll = tmp_path / "scroll.god"
    source = ('DECLARE PERMISSION TO SUMMON "reports.weekly"\n'
              'REVEAL(SUMMON("reports.weekly"))\n')
    scroll.write_text(source, encoding="utf-8")
    interp.run_source(source, source_name=str(scroll))
    assert lines == ["sealed"]


def test_network_grant_matches_host_not_path(tmp_path):
    manifest = _manifest_of(
        'DECLARE PERMISSION TO SPEAK WITH "api.example.com"\n', tmp_path)
    assert manifest.allows_host("https://api.example.com/v1/psalms")
    assert manifest.allows_host("https://sub.api.example.com/x")
    assert not manifest.allows_host("https://evil.com/?x=api.example.com")
    assert not manifest.allows_host("not a url")


def test_undeclared_http_get_is_withheld(tmp_path):
    with pytest.raises(SandboxViolation) as exc:
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'REVEAL(HTTP_GET("https://example.com/"))\n', tmp_path)
    assert "did not declare" in str(exc.value)


def test_no_manifest_means_no_guard_and_unbound_run(tmp_path):
    # Without a manifest, a plain run behaves exactly as before.
    lines, interp = _run('REVEAL(40 + 2)\n', tmp_path)
    assert lines == ["42"]
    assert getattr(interp, "_sandbox_guard", None) is None
    assert not interp.manifest


# --------------------------------------- host policy still narrows (sandbox)

def test_manifest_cannot_widen_strict_sandbox(tmp_path):
    (tmp_path / "out").mkdir()
    source = ('DECLARE PERMISSION TO WRITE "out/"\n'
              'WRITE_FILE("out/x.txt", "nope")\n')
    with pytest.raises(SandboxViolation) as exc:
        run_sandboxed(source, SandboxPolicy.strict(), source_name="s")
    # The host's denial speaks first; the manifest cannot overrule it.
    assert "sandbox withholds" in str(exc.value)


def test_manifest_narrows_sandbox_further(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    policy = SandboxPolicy.strict(
        source_dir=str(tmp_path),
        timeout_seconds=5.0,
    )
    object.__setattr__(
        policy, "allow_read_paths", (str(tmp_path),))  # host allows the dir
    scroll = tmp_path / "scroll.god"
    scroll.write_text('DECLARE PERMISSION TO READ "data/"\n'
                      'REVEAL(READ_FILE("data/note.txt"))\n',
                      encoding="utf-8")
    source = scroll.read_text(encoding="utf-8")
    output = run_sandboxed(source, policy, source_name=str(scroll))
    assert output == ["psalm"]


# ------------------------------------------------------- import composition

def test_imported_scroll_widens_grants_by_union(tmp_path, monkeypatch, god_word):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helper.god").write_text(
        "DECLARE PERMISSION TO READ "
        f"{god_word(str(tmp_path / 'data') + os.sep)}\n"
        'DECLARE helper_text AS READ_FILE("data/note.txt")\n',
        encoding="utf-8",
    )
    lines, interp = _run(
        'IMPORT "helper.god"\nREVEAL("union: " + helper_text)\n', tmp_path)
    assert lines == ["union: psalm"]
    assert interp.manifest.read_paths


def test_import_cannot_read_beyond_its_declaration(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helper.god").write_text(
        'DECLARE PERMISSION TO READ "elsewhere/"\n'
        'DECLARE helper_text AS READ_FILE("data/note.txt")\n',
        encoding="utf-8",
    )
    with pytest.raises(SandboxViolation):
        _run('IMPORT "helper.god"\nREVEAL(helper_text)\n', tmp_path)


# ------------------------------------------------------------------ CLI

def test_permissions_command_json(tmp_path, capsys):
    from godcode import cli

    scroll = tmp_path / "scroll.god"
    scroll.write_text(
        'DECLARE PERMISSION TO READ "data/"\n'
        "DECLARE PERMISSION TO ASK THE WORLD\n", encoding="utf-8")
    args = cli.build_parser().parse_args(
        ["permissions", str(scroll), "--json"])
    assert cli.cmd_permissions(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "permissions"
    assert payload["ok"] is True
    assert payload["manifest"]["stdin"] is True
    assert payload["manifest"]["read"] == [os.path.realpath(tmp_path / "data")]


def test_bridge_permissions_tool(tmp_path):
    from godcode.tools import call_tool

    scroll = tmp_path / "scroll.god"
    scroll.write_text('DECLARE PERMISSION TO WRITE "out/"\n', encoding="utf-8")
    result = call_tool("permissions", {"file": str(scroll)})
    assert result["ok"] is True
    assert result["permissions"]["write"] == [
        os.path.realpath(tmp_path / "out")]


def test_bridge_run_reports_manifest(tmp_path):
    from godcode.tools import call_tool

    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "note.txt").write_text("psalm", encoding="utf-8")
    scroll = tmp_path / "scroll.god"
    scroll.write_text(
        'DECLARE PERMISSION TO READ "data/"\n'
        'REVEAL(READ_FILE("data/note.txt"))\n', encoding="utf-8")
    import os as _os
    old = _os.getcwd()
    _os.chdir(tmp_path)
    try:
        result = call_tool("run", {"file": str(scroll), "sandbox": False})
    finally:
        _os.chdir(old)
    assert result["ok"] is True
    assert result["permissions"]["read"] == [
        os.path.realpath(tmp_path / "data")]
