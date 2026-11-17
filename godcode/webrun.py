"""The web door: run and check God Code for the browser playground.

The playground loads this very engine into the browser (through Pyodide,
Python compiled to WebAssembly) and calls the two functions below. Each
returns one JSON-ready dict, shaped like the ``run --json`` and
``check --json`` payloads of :mod:`godcode.agentics`, so the page and an
agent read the same answers.

Every run is sandboxed under the strict policy: no files, no network, no
subprocesses, no stdin, a wall-clock grant and a step budget. Scroll
imports are blessed from the bundled stdlib and from ``library_dir``,
where the playground lays the registry scrolls, so ``IMPORT "blessings"``
works in the browser as it does after ``godcode scroll install``.

Nothing here is browser-only. It is plain Python, kept honest by
``tests/test_webrun.py``, and any host may call it.
"""

from __future__ import annotations

import contextlib
import io
import os
import time
from pathlib import Path

from godcode import __version__
from godcode.agentics import TOOL_NAME, diagnostic, error_trace

#: The name the creation carries in the playground's error messages.
CREATION_NAME = "creation.god"


def _finding(f) -> dict:
    return {
        "line": f.line,
        "col": f.col,
        "code": f.rule,
        "severity": "warning",
        "message": f.message,
        "hint": None,
    }


def check_creation(source: str) -> dict:
    """Parse and lint ``source``; return a ``check`` payload.

    A parse error is one ``error`` diagnostic and the creation is impure.
    A clean parse adds the linter's gentle counsel as ``warning``
    diagnostics; counsel never makes the creation impure.
    """
    from godcode.errors import GodCodeError
    from godcode.linter import lint_source

    diagnostics: list[dict] = []
    ok = True
    try:
        findings = lint_source(source, source_name=CREATION_NAME)
    except GodCodeError as err:
        diagnostics.append(diagnostic(err))
        ok = False
    else:
        diagnostics.extend(_finding(f) for f in findings)
    return {
        "tool": TOOL_NAME,
        "command": "check",
        "file": CREATION_NAME,
        "version": __version__,
        "ok": ok,
        "diagnostics": diagnostics,
    }


def run_creation(
    source: str,
    *,
    library_dir: str | os.PathLike | None = None,
    timeout_seconds: float = 5.0,
    max_steps: int | None = None,
) -> dict:
    """Run ``source`` under the strict sandbox; return a ``run`` payload.

    ``output`` holds every line the creation spoke, REVEAL lines and
    engine notices (``🕊 Creation ascended in peace.``) alike. On failure
    it holds the lines spoken before the error, and ``error`` carries the
    diagnostic plus the rite ``trace``. A failure outside the divine
    errors is reported, never raised, so the page always has an answer.
    """
    from godcode.errors import GodCodeError
    from godcode.sandbox import SandboxPolicy, run_sandboxed_with_interpreter

    source_name = "<creation>"
    if library_dir is not None:
        # The creation rests beside the library so bare-name imports
        # resolve there, and the strict policy blesses that directory.
        library = Path(library_dir)
        library.mkdir(parents=True, exist_ok=True)
        creation = library / CREATION_NAME
        creation.write_text(source, encoding="utf-8")
        source_name = str(creation)
    policy = SandboxPolicy.strict(
        source_dir=str(library_dir) if library_dir is not None else None,
        timeout_seconds=timeout_seconds,
    )
    if max_steps is not None:
        policy.max_steps = max_steps

    buf = io.StringIO()
    error: dict | None = None
    intents: list[dict] = []
    contracts: list[dict] = []
    start = time.perf_counter()
    with contextlib.redirect_stdout(buf):
        try:
            _, interp = run_sandboxed_with_interpreter(
                source, policy, source_name=source_name)
            intents = list(getattr(interp, "intent_checks", []) or [])
            contracts = list(getattr(interp, "contract_checks", []) or [])
        except GodCodeError as err:
            error = diagnostic(err)
            error["trace"] = error_trace(err)
            contracts = list(getattr(err, "contracts", []) or [])
        except Exception as exc:  # a host failure outside the divine errors
            error = {
                "line": None,
                "col": None,
                "code": "HOST_ERROR",
                "severity": "error",
                "message": f"the outer world faltered: {exc!r}",
                "hint": None,
                "trace": [],
            }
    ms = int((time.perf_counter() - start) * 1000)
    return {
        "tool": TOOL_NAME,
        "command": "run",
        "file": CREATION_NAME,
        "version": __version__,
        "ok": error is None,
        "output": buf.getvalue().splitlines(),
        "intents": intents,
        "contracts": contracts,
        "error": error,
        "stats": {"ms": ms},
    }


__all__ = ["CREATION_NAME", "check_creation", "run_creation"]
