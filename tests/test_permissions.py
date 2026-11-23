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
        "stdin": True, "summon": [], "seal": False,
    }


def test_parse_seal_power(tmp_path):
    manifest = _manifest_of(
        "DECLARE PERMISSION TO SEAL THE COVENANT\n", tmp_path)
    assert manifest.seal is True
    assert bool(manifest)
    assert manifest.to_json()["seal"] is True
    assert manifest.describe() == ["may seal the covenant"]


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
    # Without a manifest, a library run behaves exactly as before.
    # (A plain `godcode run` is a different door: it is manifest-
    # enforced, and silence grants nothing there. See below.)
    lines, interp = _run('REVEAL(40 + 2)\n', tmp_path)
    assert lines == ["42"]
    assert getattr(interp, "_sandbox_guard", None) is None
    assert not interp.manifest


# -------------------------------- deny by default on plain `godcode run`

def _run_cli_json(tmp_path, source: str, capsys):
    from godcode import cli

    scroll = tmp_path / "scroll.god"
    scroll.write_text(source, encoding="utf-8")
    args = cli.build_parser().parse_args(["run", str(scroll), "--json"])
    code = cli.cmd_run(args)
    payload = json.loads(capsys.readouterr().out)
    return code, payload


def test_plain_run_without_manifest_is_granted_nothing(
        tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vault").mkdir()
    (tmp_path / "vault" / "secret.txt").write_text(
        "decoy", encoding="utf-8")
    code, payload = _run_cli_json(
        tmp_path, 'REVEAL(READ_FILE("vault/secret.txt"))\n', capsys)
    assert code == 1
    assert payload["ok"] is False
    assert "did not declare" in payload["error"]["message"]
    assert "decoy" not in json.dumps(payload["output"])


def test_plain_run_without_manifest_still_reveals(tmp_path, capsys):
    # Deny by default withholds powers, not speech: a scroll that only
    # computes and reveals runs untouched.
    code, payload = _run_cli_json(tmp_path, "REVEAL(40 + 2)\n", capsys)
    assert code == 0
    assert payload["ok"] is True
    assert payload["output"] == ["42"]


def test_plain_run_human_path_is_enforced_too(tmp_path, monkeypatch):
    from godcode import cli

    monkeypatch.chdir(tmp_path)
    (tmp_path / "vault").mkdir()
    (tmp_path / "vault" / "secret.txt").write_text(
        "decoy", encoding="utf-8")
    scroll = tmp_path / "scroll.god"
    scroll.write_text('REVEAL(READ_FILE("vault/secret.txt"))\n',
                      encoding="utf-8")
    args = cli.build_parser().parse_args(["run", str(scroll)])
    assert cli.cmd_run(args) == 1


def test_manifest_enforced_run_denies_undeclared_write(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    interp = Interpreter(log_path=None)
    interp.manifest_enforced = True
    scroll = tmp_path / "scroll.god"
    source = 'WRITE_FILE("out/evil.txt", "nope")\n'
    scroll.write_text(source, encoding="utf-8")
    with pytest.raises(SandboxViolation):
        interp.run_source(source, source_name=str(scroll))
    assert not (tmp_path / "out" / "evil.txt").exists()


def test_manifest_enforced_run_denies_undeclared_ask(
        tmp_path, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt="": "x")
    interp = Interpreter(log_path=None)
    interp.manifest_enforced = True
    scroll = tmp_path / "scroll.god"
    source = 'REVEAL(ASK("who goes there?"))\n'
    scroll.write_text(source, encoding="utf-8")
    with pytest.raises(SandboxViolation):
        interp.run_source(source, source_name=str(scroll))


def test_manifest_enforced_run_denies_undeclared_summon(tmp_path):
    interp = Interpreter(log_path=None)
    interp.manifest_enforced = True
    interp._plugin_verbs["reports.weekly"] = lambda args, line: "ok"
    scroll = tmp_path / "scroll.god"
    source = 'SUMMON("reports.weekly")\n'
    scroll.write_text(source, encoding="utf-8")
    with pytest.raises(SandboxViolation):
        interp.run_source(source, source_name=str(scroll))


# ------------------------------------------------------- SEAL is gated

def test_seal_without_declaration_is_refused(tmp_path):
    # The scroll declares a manifest, so the manifest binds; SEAL is
    # not among its powers, and the ledger stays untouched.
    with pytest.raises(SandboxViolation) as exc:
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'SEAL("an uninvited block")\n', tmp_path)
    assert "SEAL THE COVENANT" in str(exc.value)


def test_seal_with_declaration_is_granted(tmp_path, capsys):
    lines, interp = _run(
        "DECLARE PERMISSION TO SEAL THE COVENANT\n"
        'SEAL("a promised block")\n'
        'REVEAL("sealed")\n',
        tmp_path,
    )
    assert lines == ["sealed"]
    assert interp.manifest.seal is True


def test_seal_refused_when_manifest_enforced_and_silent(tmp_path):
    interp = Interpreter(log_path=None)
    interp.manifest_enforced = True
    scroll = tmp_path / "scroll.god"
    source = 'SEAL("an uninvited block")\n'
    scroll.write_text(source, encoding="utf-8")
    with pytest.raises(SandboxViolation) as exc:
        interp.run_source(source, source_name=str(scroll))
    assert "SEAL THE COVENANT" in str(exc.value)


def test_seal_without_manifest_keeps_legacy_freedom(tmp_path):
    # A library run that declared nothing and was not asked to enforce
    # seals as it always has (no ledger is bound here, so the seal is
    # spoken but not recorded, and the run goes on).
    lines, _ = _run('SEAL("a free block")\nREVEAL("sealed")\n', tmp_path)
    assert lines == ["sealed"]


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

def test_imported_scroll_may_narrow_grants(tmp_path, monkeypatch, god_word):
    # The lead scroll declares the read; the breathed-in scroll declares
    # the same read for itself and uses it. Narrowing is blessed.
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
        'DECLARE PERMISSION TO READ "data/"\n'
        'IMPORT "helper.god"\nREVEAL("narrowed: " + helper_text)\n',
        tmp_path)
    assert lines == ["narrowed: psalm"]
    assert interp.manifest.read_paths == (
        os.path.realpath(tmp_path / "data"),)


def test_imported_scroll_widening_is_refused_and_named(
        tmp_path, monkeypatch):
    # The lead scroll's manifest is locked; the breathed-in scroll
    # declares a read over the vault. The import itself is refused,
    # naming the widening power, before the scroll can run.
    (tmp_path / "data").mkdir()
    (tmp_path / "vault").mkdir()
    (tmp_path / "vault" / "secret.txt").write_text(
        "decoy", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helper.god").write_text(
        'DECLARE PERMISSION TO READ "vault/"\n'
        'REVEAL("the helper ran")\n',
        encoding="utf-8",
    )
    with pytest.raises(SandboxViolation) as exc:
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'IMPORT "helper.god"\n', tmp_path)
    message = str(exc.value)
    assert "did not declare" in message
    assert "READ" in message
    assert os.path.realpath(tmp_path / "vault") in message
    assert "never widen" in message


def test_imported_scroll_widening_ask_is_refused(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helper.god").write_text(
        "DECLARE PERMISSION TO ASK THE WORLD\n"
        'REVEAL("the helper ran")\n',
        encoding="utf-8",
    )
    with pytest.raises(SandboxViolation) as exc:
        _run('DECLARE PERMISSION TO READ "data/"\n'
             'IMPORT "helper.god"\n', tmp_path)
    assert "ASK THE WORLD" in str(exc.value)


def test_import_of_manifestless_scroll_is_blessed(tmp_path, monkeypatch):
    # A breathed-in scroll that declares nothing widens nothing.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "helper.god").write_text(
        'DECLARE greeting AS "peace"\n', encoding="utf-8")
    lines, _ = _run(
        'DECLARE PERMISSION TO READ "data/"\n'
        'IMPORT "helper.god"\nREVEAL(greeting)\n', tmp_path)
    assert lines == ["peace"]


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

    # The bridge runs sandboxed whatever the caller asks, so the scroll
    # declares its manifest and reveals a word; the run's manifest is
    # still reported in full.
    scroll = tmp_path / "scroll.god"
    scroll.write_text(
        'DECLARE PERMISSION TO READ "data/"\n'
        'REVEAL("the promise is read")\n', encoding="utf-8")
    result = call_tool("run", {"file": str(scroll), "sandbox": False})
    assert result["ok"] is True
    assert result["sandbox"] is True
    assert result["output"] == ["the promise is read"]
    assert result["permissions"]["read"] == [
        os.path.realpath(tmp_path / "data")]
    assert result["permissions"]["seal"] is False
