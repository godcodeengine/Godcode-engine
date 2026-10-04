"""Tests for tongue-aware editor tooling (godcode/lsp.py + VS Code files).

The language server reads the ``# tongue:`` pragma of the open scroll: it
offers the tongue's keywords beside the English ones and answers hover for
tongue words with the English keyword's documentation. The VS Code grammar
paints Setswana keywords, and the snippet file ships Setswana starters.
"""
from __future__ import annotations

import json
import queue
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from godcode import lsp

TN_DOC = (
    "# tongue: tn\n"
    "SIMOLOLA TLHOLEGO\n"
    '  SENOLA("Dumela")\n'
    "  FA x GONE\n"
    '    SENOLA("go")\n'
    "  FEDISA FA\n"
    "FEDISA TLHOLEGO\n"
)

EN_DOC = 'BEGIN CREATION\n  REVEAL("light")\nEND CREATION\n'


# ---------------------------------------------------------------------------
# tongue helpers
# ---------------------------------------------------------------------------

def test_tongue_of_reads_pragma() -> None:
    assert lsp.tongue_of(TN_DOC) == "tn"
    assert lsp.tongue_of(EN_DOC) is None
    assert lsp.tongue_of("# tongue: xx\n") == "xx"


def test_tongue_table_empty_for_english_and_unknown() -> None:
    assert lsp.tongue_table(None) == {}
    assert lsp.tongue_table("en") == {}
    assert lsp.tongue_table("xx") == {}


def test_tongue_table_setswana_has_aliases() -> None:
    table = lsp.tongue_table("tn")
    assert table["name"] == "Setswana"
    assert table["aliases"]["SENOLA"] == "REVEAL"
    assert table["compounds"][("FEDISA", "FA")] == "ENDIF"


def test_tongue_keyword_items_label_and_detail() -> None:
    items = lsp.tongue_keyword_items("tn")
    labels = {i["label"]: i for i in items}
    assert labels["SENOLA (REVEAL)"]["insertText"] == "SENOLA"
    assert "Setswana" in labels["SENOLA (REVEAL)"]["detail"]
    assert labels["FEDISA FA (ENDIF)"]["insertText"] == "FEDISA FA"
    assert labels["FEDISA LEKA (ENDTRY)"]["insertText"] == "FEDISA LEKA"


def test_tongue_snippet_items_carry_setswana_name() -> None:
    items = lsp.tongue_snippet_items(lsp.tongue_table("tn"))
    assert len(items) == 3
    assert all("Setswana" in i["detail"] for i in items)
    labels = [i["label"] for i in items]
    assert "SIMOLOLA TLHOLEGO … FEDISA TLHOLEGO" in labels


# ---------------------------------------------------------------------------
# completions
# ---------------------------------------------------------------------------

def test_completion_english_doc_has_no_tongue_words() -> None:
    labels = [i["label"] for i in lsp.completion_items(EN_DOC)]
    assert "BEGIN CREATION" in labels
    assert not any("SENOLA" in label for label in labels)
    assert not any("Setswana" in (i.get("detail") or "") for i in lsp.completion_items(EN_DOC))


def test_completion_setswana_doc_adds_tongue_words() -> None:
    items = lsp.completion_items(TN_DOC)
    labels = [i["label"] for i in items]
    assert "SENOLA (REVEAL)" in labels
    assert "FA (IF)" in labels
    assert "FEDISA FA (ENDIF)" in labels
    assert "FEDISA LEKA (ENDTRY)" in labels
    # English stays: mixed scrolls are welcome
    assert "REVEAL" in labels
    assert "SIMOLOLA TLHOLEGO … FEDISA TLHOLEGO" in labels


def test_completion_unknown_tongue_falls_back_to_english() -> None:
    english = lsp.completion_items(EN_DOC)
    unknown = lsp.completion_items("# tongue: xx\n")
    assert [i["label"] for i in unknown] == [i["label"] for i in english]


def test_completion_default_signature_unchanged() -> None:
    # callers that pass no document keep the old behaviour
    assert lsp.completion_items() == lsp.completion_items("")


# ---------------------------------------------------------------------------
# hover
# ---------------------------------------------------------------------------

def test_hover_key_single_word() -> None:
    assert lsp.tongue_hover_key('  SENOLA("hi")', 4, "tn") == "REVEAL"
    assert lsp.tongue_hover_key("  FA x GONE", 3, "tn") == "IF"


def test_hover_key_two_word_closers() -> None:
    assert lsp.tongue_hover_key("  FEDISA FA", 4, "tn") == "ENDIF"
    assert lsp.tongue_hover_key("  FEDISA LEKA", 4, "tn") == "ENDTRY"
    # hovering the second word still resolves the second word itself
    assert lsp.tongue_hover_key("  FEDISA LEKA", 10, "tn") == "TRY"


def test_hover_key_two_word_openers() -> None:
    assert lsp.tongue_hover_key("SIMOLOLA TLHOLEGO", 2, "tn") == "BEGIN CREATION"
    assert lsp.tongue_hover_key("FEDISA TLHOLEGO", 2, "tn") == "END CREATION"
    assert lsp.tongue_hover_key("TLHALOSA TIRO x", 3, "tn") == "DEFINE RITE"


def test_hover_key_returns_none_off_tongue_words() -> None:
    assert lsp.tongue_hover_key("  xxxxx", 4, "tn") is None
    assert lsp.tongue_hover_key('  REVEAL("hi")', 4, "tn") is None  # English: normal path
    assert lsp.tongue_hover_key("  SENOLA", 4, "en") is None


def test_hover_key_points_at_documented_keys() -> None:
    for line, char in [('  SENOLA("hi")', 4), ("  FEDISA FA", 4),
                       ("SIMOLOLA TLHOLEGO", 2)]:
        key = lsp.tongue_hover_key(line, char, "tn")
        assert key is not None
        assert lsp.hover_markdown(key) is not None, f"no hover doc for {key}"


# ---------------------------------------------------------------------------
# end to end over stdio
# ---------------------------------------------------------------------------

CMD = [sys.executable, "-m", "godcode", "lsp"]
TIMEOUT = 10


def frame(message: dict) -> bytes:
    body = json.dumps(message).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body


class ServerHarness:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            CMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)
        self.inbox: queue.Queue = queue.Queue()
        self._reader = threading.Thread(target=self._pump, daemon=True)
        self._reader.start()
        self._next_id = 0

    def _pump(self) -> None:
        out = self.proc.stdout
        assert out is not None
        while True:
            headers: dict[str, str] = {}
            while True:
                line = out.readline()
                if not line:
                    self.inbox.put(None)
                    return
                line = line.decode("latin-1").strip()
                if not line:
                    break
                name, _, value = line.partition(":")
                headers[name.strip().lower()] = value.strip()
            try:
                length = int(headers["content-length"])
            except (KeyError, ValueError):
                continue
            body = b""
            while len(body) < length:
                chunk = out.read(length - len(body))
                if not chunk:
                    self.inbox.put(None)
                    return
                body += chunk
            self.inbox.put(json.loads(body.decode("utf-8")))

    def send(self, message: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(frame(message))
        self.proc.stdin.flush()

    def request(self, method: str, params: dict | None = None) -> int:
        self._next_id += 1
        self.send({"jsonrpc": "2.0", "id": self._next_id,
                   "method": method, "params": params or {}})
        return self._next_id

    def notify(self, method: str, params: dict | None = None) -> None:
        self.send({"jsonrpc": "2.0", "method": method,
                   "params": params or {}})

    def wait_for(self, predicate, timeout: float = TIMEOUT) -> dict:
        import time
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                pytest.fail("timed out waiting for server message")
            try:
                message = self.inbox.get(timeout=remaining)
            except queue.Empty:
                pytest.fail("timed out waiting for server message")
            if message is None:
                pytest.fail("server closed stdout unexpectedly")
            if predicate(message):
                return message

    def wait_response(self, msg_id: int) -> dict:
        return self.wait_for(lambda m: m.get("id") == msg_id)

    def wait_notification(self, method: str) -> dict:
        return self.wait_for(lambda m: m.get("method") == method)

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.notify("exit")
            self.proc.wait(timeout=TIMEOUT)
        except (BrokenPipeError, OSError):
            pass
        finally:
            if self.proc.poll() is None:
                self.proc.kill()


@pytest.fixture()
def server():
    harness = ServerHarness()
    yield harness
    harness.close()


def did_open(uri: str, text: str) -> dict:
    return {"jsonrpc": "2.0", "method": "textDocument/didOpen",
            "params": {"textDocument": {"uri": uri, "text": text}}}


def test_server_completion_serves_setswana_for_tn_document(server) -> None:
    uri = "file:///dumela.god"
    server.send(did_open(uri, TN_DOC))
    server.wait_notification("textDocument/publishDiagnostics")
    msg_id = server.request("textDocument/completion",
                            {"textDocument": {"uri": uri}})
    response = server.wait_response(msg_id)
    labels = [i["label"] for i in response["result"]]
    assert "SENOLA (REVEAL)" in labels
    assert "FEDISA FA (ENDIF)" in labels
    assert "REVEAL" in labels  # English stays


def test_server_completion_stays_english_without_pragma(server) -> None:
    uri = "file:///plain.god"
    server.send(did_open(uri, EN_DOC))
    server.wait_notification("textDocument/publishDiagnostics")
    msg_id = server.request("textDocument/completion",
                            {"textDocument": {"uri": uri}})
    response = server.wait_response(msg_id)
    labels = [i["label"] for i in response["result"]]
    assert "REVEAL" in labels
    assert not any("SENOLA" in label for label in labels)


def test_server_hover_explains_setswana_word(server) -> None:
    uri = "file:///dumela.god"
    server.send(did_open(uri, TN_DOC))
    server.wait_notification("textDocument/publishDiagnostics")
    msg_id = server.request("textDocument/hover", {
        "textDocument": {"uri": uri},
        "position": {"line": 2, "character": 4},  # on SENOLA
    })
    response = server.wait_response(msg_id)
    value = response["result"]["contents"]["value"]
    assert "**REVEAL**" in value


# ---------------------------------------------------------------------------
# VS Code files
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parent.parent


def _grammar_patterns() -> dict[str, "re.Pattern"]:
    grammar = json.loads(
        (REPO / "editors/vscode/syntaxes/godcode.tmLanguage.json").read_text())
    patterns = {}
    for key, entry in grammar["repository"].items():
        if "match" not in entry:
            continue
        patterns[key] = re.compile(entry["match"].replace("(?i)", ""),
                                    re.IGNORECASE)
    return patterns


def test_vscode_grammar_paints_setswana_keywords() -> None:
    patterns = _grammar_patterns()
    assert patterns["keyword-spirit"].search("SENOLA")
    assert patterns["keyword-spirit"].search("POROFETA")
    assert patterns["keyword-control"].search("FA")
    assert patterns["keyword-control"].search("GONE")
    assert patterns["keyword-control"].search("FEDISA FA")
    assert patterns["keyword-control"].search("FEDISA LEKA")
    assert patterns["keyword-control"].search("LEKA")
    assert patterns["keyword-control"].search("TSHWARA")
    assert patterns["keyword-control"].search("KGAOLA")
    assert patterns["keyword-control"].search("TSWELELA")
    assert patterns["keyword-control"].search("BITSA")
    assert patterns["keyword-control"].search("BUSETSA")
    assert patterns["keyword-control"].search("TSENYA")
    assert patterns["keyword-declaration"].search("BOLELA")
    assert patterns["keyword-declaration"].search("JAKA")
    assert patterns["keyword-logic"].search("KE")
    assert patterns["keyword-logic"].search("LE")
    assert patterns["keyword-logic"].search("KGOTSA")
    assert patterns["keyword-structure"].search("SIMOLOLA TLHOLEGO")
    assert patterns["keyword-structure"].search("FEDISA TLHOLEGO")
    assert patterns["keyword-structure"].search("TLHALOSA TIRO")
    assert patterns["constant-language"].search("NNETE")
    assert patterns["constant-language"].search("MAAKA")
    assert patterns["constant-language"].search("SEPE")


def test_vscode_grammar_keeps_english_and_new_control_words() -> None:
    patterns = _grammar_patterns()
    for word in ("IF", "THEN", "ENDIF", "FOR", "WHILE", "BEGIN CREATION",
                 "TRY", "CATCH", "ENDTRY", "BREAK", "CONTINUE"):
        assert patterns["keyword-control"].search(word) or \
            patterns["keyword-structure"].search(word), word


def test_vscode_snippets_setswana_starters_run() -> None:
    from godcode.tongues import parse_source
    from godcode.interpreter import Interpreter
    snippets = json.loads(
        (REPO / "editors/vscode/snippets/godcode.json").read_text())
    assert len(snippets) == 27
    assert "Setswana creation block" in snippets
    assert "Setswana if" in snippets
    creation = snippets["Setswana creation block"]
    assert creation["prefix"] == "simolola"
    body = "\n".join(creation["body"])
    body = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", body).replace("$0", "")
    tree = parse_source(body)
    out: list[str] = []
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().run(tree)
    assert "ascended in peace" in buf.getvalue()  # TLHATLOGA ends the run
    cond = snippets["Setswana if"]
    assert cond["prefix"] == "fa"
    cond_body = "\n".join(cond["body"])
    # placeholders 1 and 2 get equal names so the condition holds true;
    # placeholder 3 keeps its SENOLA("heaven") default
    cond_body = re.sub(r"\$\{[12]:[^}]*\}", "heaven", cond_body)
    cond_body = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", cond_body).replace("$0", "")
    wrapped = "# tongue: tn\nSIMOLOLA TLHOLEGO\n" + cond_body + "\nFEDISA TLHOLEGO\n"
    tree = parse_source(wrapped)
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().run(tree)
    assert "heaven" in buf.getvalue()


# ---------------------------------------------------------------------------
# house style: no em dashes in user-facing engine strings
# ---------------------------------------------------------------------------

def test_no_em_dash_in_user_facing_strings() -> None:
    """Error/notice strings the user can see must not carry em dashes."""
    import io
    from contextlib import redirect_stdout
    from godcode.errors import GodRuntimeError
    from godcode.tongues import parse_source
    from godcode.interpreter import Interpreter
    endless = "BEGIN CREATION\nWHILE 1 IS 1 DO REVEAL(1)\nEND CREATION\n"
    tree = parse_source(endless)
    with pytest.raises(GodRuntimeError) as exc:
        Interpreter().run(tree)
    assert "—" not in str(exc.value)
    assert "endless" in str(exc.value).lower()
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().run(parse_source(
            'BEGIN CREATION\nPROPHESY("q")\nSEAL(1)\nEND CREATION\n'))
    assert "—" not in buf.getvalue()


def test_help_text_has_no_em_dash() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "godcode", "--help"],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "—" not in result.stdout
