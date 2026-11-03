"""The God Code MCP server -- ``godcode mcp``.

Speaks the Model Context Protocol over stdio (one JSON-RPC 2.0 message
per line, the standard stdio transport) so any MCP client -- Claude Code,
Cursor, Codex, or any other agent host -- can check, run, explain,
format, and list God Code scrolls, and verify ledgers, without learning
a bespoke protocol.

The tools are the same eleven the agent bridge offers, plus one rule
that only holds here: **runs are always sandboxed**. An MCP client
talks to scrolls it did not write, so the server ignores any request
to run outside the sandbox and says so in the result. The plain
``godcode bridge`` keeps its own convention for hosts that already
trust their scrolls; this server never trusts them.

No third-party dependencies. Protocol versions are negotiated the way
MCP asks: the client names the version it speaks, and the server
answers with that version when it knows it, or with the newest version
it speaks when it does not.
"""
from __future__ import annotations

import json

from godcode import tools as _tools

#: Newest first. A client version outside this list gets the newest.
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")

_PARSE_ERROR = -32700
_INVALID_REQUEST = -32600
_METHOD_NOT_FOUND = -32601
_INVALID_PARAMS = -32602
_INTERNAL_ERROR = -32603


class _McpError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _response_ok(req_id, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _response_err(req_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def negotiate_protocol_version(client_version) -> str:
    """Answer an MCP initialize with a version both sides speak."""
    if isinstance(client_version, str) \
            and client_version in SUPPORTED_PROTOCOL_VERSIONS:
        return client_version
    return SUPPORTED_PROTOCOL_VERSIONS[0]


def _handle_initialize(params: dict) -> dict:
    from godcode import __version__

    return {
        "protocolVersion": negotiate_protocol_version(
            params.get("protocolVersion")),
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "godcode", "version": __version__},
    }


def call_mcp_tool(name: str, arguments: dict) -> dict:
    """Run one tool the MCP way: runs are always sandboxed.

    Any ``sandbox: false`` on a run request is overruled, and the
    result says the run was sandboxed, so a client can never mistake
    an MCP run for an unsandboxed one.
    """
    if name == "run":
        arguments = dict(arguments)
        arguments["sandbox"] = True
        result = _tools.call_tool(name, arguments)
        result["sandbox"] = True
        return result
    return _tools.call_tool(name, arguments)


def _handle_tools_call(params: dict) -> dict:
    name = params.get("name")
    arguments = params.get("arguments", {})
    if not isinstance(name, str):
        raise _McpError(_INVALID_PARAMS, "tools/call needs 'name' as a string")
    if not isinstance(arguments, dict):
        raise _McpError(_INVALID_PARAMS, "'arguments' must be an object")
    result = call_mcp_tool(name, arguments)
    payload = {"content": [{"type": "text",
                            "text": json.dumps(result, ensure_ascii=False)}]}
    if not result.get("ok", True):
        payload["isError"] = True
    return payload


def _dispatch(method: str, params: dict):
    if method == "initialize":
        return _handle_initialize(params)
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": _tools.TOOL_SCHEMAS}
    if method == "tools/call":
        return _handle_tools_call(params)
    if method == "resources/list":
        return {"resources": []}
    if method == "prompts/list":
        return {"prompts": []}
    raise _McpError(_METHOD_NOT_FOUND, f"no such method '{method}'")


def handle_message(message: dict):
    """Answer one parsed MCP message, or None when no answer is owed.

    Notifications (no ``id``) never get an answer, whatever method
    they carry. Anything malformed raises _McpError.
    """
    if not isinstance(message, dict) or "method" not in message:
        raise _McpError(_INVALID_REQUEST, "a request needs a 'method'")
    if "id" not in message:
        return None
    params = message.get("params", {})
    if not isinstance(params, dict):
        raise _McpError(_INVALID_PARAMS, "'params' must be an object")
    return _dispatch(message["method"], params)


def cmd_mcp(args) -> int:  # noqa: ARG001
    """Serve the MCP server: JSON-RPC 2.0 over stdio, one message per line.

    Stdout carries exactly one protocol message per line. Tool work
    runs muted, so an engine print can never land in the stream: the
    response is written only after handling returns.
    """
    import contextlib
    import io
    import sys

    stdin, stdout = sys.stdin, sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps(_response_err(None, _PARSE_ERROR,
                                                 "the request was not JSON"))
                         + "\n")
            stdout.flush()
            continue
        req_id = request.get("id") if isinstance(request, dict) else None
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                result = handle_message(request)
        except _McpError as err:
            response = _response_err(req_id, err.code, err.message)
        except Exception as exc:  # pragma: no cover - defensive
            response = _response_err(req_id, _INTERNAL_ERROR,
                                     f"the server faltered: {exc!r}")
        else:
            if result is None:
                continue
            response = _response_ok(req_id, result)
        stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        stdout.flush()
    return 0
