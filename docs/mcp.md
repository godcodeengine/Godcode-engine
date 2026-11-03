# The MCP server

`godcode mcp` serves God Code to any agent host that speaks the Model
Context Protocol: Claude Code, Cursor, Codex, or any other MCP client.
It runs over stdio, one JSON-RPC 2.0 message per line, with no
third-party dependencies.

```bash
godcode mcp
```

Point a client at it the usual way:

```json
{
  "mcpServers": {
    "godcode": {
      "command": "godcode",
      "args": ["mcp"]
    }
  }
}
```

## The handshake

The client opens with `initialize`, naming the protocol version it
speaks. The server answers with that version when it knows it, or
with the newest version it speaks when it does not. Supported
versions, newest first: `2025-06-18`, `2025-03-26`, `2024-11-05`.
The answer also carries the server's capabilities (tools) and its
name, `godcode`. The client then sends `notifications/initialized`,
which gets no answer: notifications never do.

After that, the methods that matter are `ping`, `tools/list`, and
`tools/call`. `resources/list` and `prompts/list` answer with empty
lists: this server offers tools, nothing else. Unknown methods are
refused with code `-32601`; malformed JSON is refused with `-32700`.

## The tools

Eleven tools, the same set `godcode tools` lists. `tools/call`
wraps each result as MCP content (one text block holding the result
as JSON) and marks failed results with `isError`.

| Tool | What it does |
| --- | --- |
| `check` | Lex and parse a scroll without running it. Diagnostics carry line, column, error code, and a fix hint. |
| `run` | Run a scroll and capture its output. Always sandboxed (see below). |
| `consult` | Ask the local Spirit oracle a question. No external calls. |
| `intent` | Resolve the intent behind words with the Spirit Engine. |
| `anchor_verify` | Verify an `ANCHOR` receipt against its chain. |
| `ledger_verify` | Verify the covenant chain and the anchor chain for tampering. |
| `permissions` | Read a scroll's permission manifest without running it. |
| `explain` | Read a scroll without running it: tongue, rites and their declared intents, names, reveals, seals, summons, consults, imports, manifest. |
| `get_schema` | Fetch one dated machine-interface schema (`check`, `run`, `explain`, `ledger-verify`) as parsed JSON. |
| `format` | Re-emit a scroll in canonical form without running it, the shape `godcode fmt` prints. |
| `list_scrolls` | List the scrolls installed in the local scroll registry. |

## Runs are always sandboxed

An MCP client talks to scrolls it did not write, so this server
never trusts them. A `run` call with `sandbox` set to false is run
in the sandbox anyway, and the result says `sandbox` is true, so a
client can never mistake an MCP run for an unsandboxed one. A scroll
that reaches for a power the sandbox withholds, such as writing a
file it never declared, fails instead of touching the outer world.

The plain `godcode bridge` keeps its own convention for hosts that
already trust their scrolls. Prefer `godcode mcp` for anything new.

## Stdout stays pure

Stdout carries exactly one protocol message per line. Tool work
runs muted: an engine notice can never land in the stream and break
a client's parsing. That is also why a sandboxed run through the
server reports only the collected output, the same shape the CLI's
`run --sandbox --json` reports.
