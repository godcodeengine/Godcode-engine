"""Tests for the God Code MCP server (godcode/mcp.py).

The server speaks the Model Context Protocol over stdio: initialize
with version negotiation, tools/list, tools/call, and silence for
notifications. Runs through it are always sandboxed, whatever the
client asks for, and stdout carries exactly one protocol message per
line, never an engine print.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from godcode.mcp import (
    SUPPORTED_PROTOCOL_VERSIONS,
    call_mcp_tool,
    negotiate_protocol_version,
)

PURE = "BEGIN CREATION\n  DECLARE answer AS 40 + 2\n  REVEAL(answer)\nEND CREATION\n"

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def _session(messages, cwd=None):
    """Run `godcode mcp` as a subprocess; return parsed response lines."""
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "godcode", "mcp"],
        input="\n".join(json.dumps(m) for m in messages) + "\n",
        capture_output=True, text=True, cwd=cwd or str(REPO_ROOT),
        env=env, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == "", proc.stderr
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def _content_text(response):
    payload = json.loads(response["result"]["content"][0]["text"])
    return payload


class TestNegotiation:
    def test_known_version_is_echoed(self):
        for version in SUPPORTED_PROTOCOL_VERSIONS:
            assert negotiate_protocol_version(version) == version

    def test_unknown_version_gets_the_newest(self):
        assert negotiate_protocol_version("1999-01-01") == \
            SUPPORTED_PROTOCOL_VERSIONS[0]
        assert negotiate_protocol_version(None) == \
            SUPPORTED_PROTOCOL_VERSIONS[0]


class TestSession:
    def test_full_handshake_and_tools(self, tmp_path):
        scroll = _write(tmp_path, "pure.god", PURE)
        responses = _session([
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-03-26",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "ping"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "check", "arguments": {"file": scroll}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "run", "arguments": {"file": scroll}}},
            {"jsonrpc": "2.0", "id": 6, "method": "resources/list"},
            {"jsonrpc": "2.0", "id": 7, "method": "prompts/list"},
        ])
        # Seven requests, one notification: exactly seven answers, and
        # every line parsed as JSON above, so no engine print leaked.
        assert [r["id"] for r in responses] == [1, 2, 3, 4, 5, 6, 7]
        assert responses[0]["result"]["protocolVersion"] == "2025-03-26"
        assert responses[0]["result"]["serverInfo"]["name"] == "godcode"
        assert responses[1]["result"] == {}
        names = {t["name"] for t in responses[2]["result"]["tools"]}
        assert names == {"check", "run", "consult", "intent", "anchor_verify",
                         "ledger_verify", "permissions", "explain",
                         "get_schema", "format", "list_scrolls"}
        assert _content_text(responses[3])["ok"] is True
        run = _content_text(responses[4])
        assert run["ok"] is True
        assert run["output"] == ["42"]
        assert run["sandbox"] is True
        assert responses[5]["result"] == {"resources": []}
        assert responses[6]["result"] == {"prompts": []}

    def test_run_ignores_sandbox_false(self, tmp_path):
        """Behavioural proof, not just a flag: a WRITE_FILE the sandbox
        withholds must fail and leave no file, even when the client
        asks for sandbox false."""
        target = tmp_path / "escape.txt"
        scroll = _write(tmp_path, "writer.god",
                        "BEGIN CREATION\n"
                        f"  WRITE_FILE(\"{target}\", \"nope\")\n"
                        "END CREATION\n")
        responses = _session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "run",
                        "arguments": {"file": scroll, "sandbox": False}}},
        ])
        result = _content_text(responses[0])
        assert result["ok"] is False
        assert result["sandbox"] is True
        assert not target.exists()
        assert responses[0]["result"]["isError"] is True

    def test_format_tool(self, tmp_path):
        messy = "begin creation\n  declare answer as 40 + 2\n  reveal(answer)\nend creation\n"
        scroll = _write(tmp_path, "messy.god", messy)
        responses = _session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "format", "arguments": {"file": scroll}}},
        ])
        result = _content_text(responses[0])
        assert result["ok"] is True
        assert result["formatted"] == PURE

    def test_list_scrolls_tool(self):
        responses = _session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "list_scrolls", "arguments": {}}},
        ])
        result = _content_text(responses[0])
        assert result["ok"] is True
        assert isinstance(result["scrolls"], list)

    def test_unknown_method_and_bad_json(self):
        responses = _session([
            {"jsonrpc": "2.0", "id": 1, "method": "bogus/method",
             "params": {}},
        ])
        assert responses[0]["error"]["code"] == -32601
        proc_input = "this is not json\n"
        import os

        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT)
        proc = subprocess.run(
            [sys.executable, "-m", "godcode", "mcp"],
            input=proc_input, capture_output=True, text=True,
            cwd=str(REPO_ROOT), env=env, timeout=60,
        )
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["error"]["code"] == -32700


class TestCallMcpTool:
    def test_run_forces_sandbox_at_the_tool_layer(self, monkeypatch):
        seen = {}

        def fake_call(name, arguments):
            seen.update(arguments)
            return {"ok": True}

        monkeypatch.setattr("godcode.mcp._tools.call_tool", fake_call)
        result = call_mcp_tool("run", {"file": "x.god", "sandbox": False})
        assert seen["sandbox"] is True
        assert result["sandbox"] is True

    def test_other_tools_pass_arguments_through(self, monkeypatch):
        seen = {}

        def fake_call(name, arguments):
            seen.update(arguments)
            return {"ok": True}

        monkeypatch.setattr("godcode.mcp._tools.call_tool", fake_call)
        call_mcp_tool("check", {"file": "x.god"})
        assert seen == {"file": "x.god"}
