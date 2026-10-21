"""`godcode explain` -- say what a scroll does, without running it.

Static facts for humans and agents: the tongue, the rites and their
declared intents, the names it declares, the lines it reveals, the
seals it keeps, the verbs it summons, the questions it lays before the
Spirit, the scrolls it brings in, and the powers it declares. Nothing
executes; the walk is read-only over the parsed AST, so explaining a
scroll is always safe.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path


# ---------------------------------------------------------------------------
# walking
# ---------------------------------------------------------------------------
def _iter_child(value):
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        yield from _iter_nodes(value)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_child(item)


def _iter_nodes(node):
    """Yield an AST node and every AST node nested inside it, at any depth.

    Statements may sit inside a creation block, an IF, a loop, a TRY, or
    a rite body; call expressions may sit inside any expression. The
    generic walk finds them all without enumerating every node kind.
    """
    yield node
    if dataclasses.is_dataclass(node) and not isinstance(node, type):
        for field in dataclasses.fields(node):
            yield from _iter_child(getattr(node, field.name))


# ---------------------------------------------------------------------------
# facts
# ---------------------------------------------------------------------------
def explain_facts(source: str, base_dir: str | Path | None) -> dict:
    """Collect the static facts of a scroll.

    Raises the same GodCodeError ``parse_source`` raises on a broken
    scroll. ``base_dir`` resolves the manifest's relative paths, as in
    `godcode permissions`.
    """
    from godcode.ast import (
        CallExpr,
        Declare,
        DeclareIntent,
        DefineRite,
        Import,
        Literal,
        Reveal,
        SealStmt,
    )
    from godcode.permissions import collect_manifest
    from godcode.tongues import _CODE_ALIASES, detect_tongue, parse_source, resolve

    program = parse_source(source)
    raw_tongue = detect_tongue(source)
    tongue_code = _CODE_ALIASES.get(raw_tongue, raw_tongue) if raw_tongue else "en"
    tongue_name = resolve(raw_tongue)["name"]

    rites: list[dict] = []
    intents: list[dict] = []
    declarations: list[dict] = []
    reveals: list[dict] = []
    seals: list[dict] = []
    summons: list[dict] = []
    consults: list[dict] = []
    imports: list[dict] = []
    intent_by_rite: dict[str, str] = {}

    for node in _iter_nodes(program):
        if isinstance(node, DeclareIntent):
            intents.append(
                {"rite": node.rite, "text": node.text, "line": node.line}
            )
            intent_by_rite.setdefault(node.rite, node.text)
        elif isinstance(node, DefineRite):
            rites.append(
                {
                    "name": node.name,
                    "params": list(node.params),
                    "line": node.line,
                    "intent": intent_by_rite.get(node.name),
                }
            )
        elif isinstance(node, Declare):
            declarations.append({"name": node.name, "line": node.line})
        elif isinstance(node, Reveal):
            reveals.append({"line": node.line})
        elif isinstance(node, SealStmt):
            seals.append({"line": node.line, "kind": "SEAL"})
        elif isinstance(node, CallExpr):
            if node.callee == "ANCHOR":
                seals.append({"line": node.line, "kind": "ANCHOR"})
            elif node.callee == "CONSULT":
                consults.append({"line": node.line})
            elif node.callee == "SUMMON":
                verb = node.args[0] if node.args else None
                summons.append(
                    {
                        "verb": verb.value if isinstance(verb, Literal) else None,
                        "line": node.line,
                    }
                )
        elif isinstance(node, Import):
            imports.append({"path": node.path, "line": node.line})

    manifest = collect_manifest(program.statements, base_dir)

    # Intents may be declared after their rites; attach them now that
    # every DECLARE INTENT has been seen.
    for rite in rites:
        if rite["intent"] is None:
            rite["intent"] = intent_by_rite.get(rite["name"])

    return {
        "tongue": {"code": tongue_code, "name": tongue_name},
        "rites": rites,
        "intents": intents,
        "declarations": declarations,
        "permissions": manifest.to_json(),
        "reveals": reveals,
        "seals": seals,
        "summons": summons,
        "consults": consults,
        "imports": imports,
    }


def explain_payload(file: str, ok: bool, diagnostics: list[dict],
                    facts: dict | None = None) -> dict:
    """The `godcode explain --json` envelope: the check/run envelope style."""
    payload = {
        "tool": "godcode",
        "command": "explain",
        "file": file,
        "ok": ok,
        "diagnostics": diagnostics,
    }
    if facts:
        payload.update(facts)
    return payload


# ---------------------------------------------------------------------------
# human words
# ---------------------------------------------------------------------------
def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one}" if n == 1 else f"{n} {many}"


def human_summary(filename: str, facts: dict) -> str:
    """The scroll in plain words, for `godcode explain` without --json."""
    from godcode.permissions import PermissionManifest

    lines = [f"The scroll {filename}, in plain words:"]

    tongue = facts["tongue"]
    if tongue["code"] != "en":
        lines.append(f"It speaks {tongue['name']}.")

    rites = facts["rites"]
    if not rites:
        lines.append("It defines no rites.")
    elif len(rites) == 1:
        rite = rites[0]
        params = ", ".join(rite["params"]) or "no names"
        lines.append(
            f"It defines 1 rite: {rite['name']} (line {rite['line']}), "
            f"taking {_count(len(rite['params']), 'name', 'names')}"
            + (f" ({params})." if rite["params"] else ".")
        )
        if rite["intent"]:
            lines.append(f'  Its declared purpose: "{rite["intent"]}".')
    else:
        lines.append(f"It defines {_count(len(rites), 'rite', 'rites')}:")
        for rite in rites:
            lines.append(
                f"  - {rite['name']} (line {rite['line']}), "
                f"taking {_count(len(rite['params']), 'name', 'names')}."
            )
            if rite["intent"]:
                lines.append(f'    Its declared purpose: "{rite["intent"]}".')

    declarations = facts["declarations"]
    if not declarations:
        lines.append("It declares no names.")
    else:
        names = ", ".join(f"{d['name']} (line {d['line']})" for d in declarations)
        lines.append(f"It declares {_count(len(declarations), 'name', 'names')}: {names}.")

    reveals = facts["reveals"]
    if not reveals:
        lines.append("It reveals nothing.")
    else:
        at = ", ".join(f"line {r['line']}" for r in reveals)
        lines.append(f"It reveals {_count(len(reveals), 'line', 'lines')}: {at}.")

    seals = facts["seals"]
    kept = [s for s in seals if s["kind"] == "SEAL"]
    anchored = [s for s in seals if s["kind"] == "ANCHOR"]
    if not seals:
        lines.append("It seals nothing.")
    else:
        if kept:
            at = ", ".join(f"line {s['line']}" for s in kept)
            lines.append(f"It seals {_count(len(kept), 'covenant', 'covenants')}: {at}.")
        if anchored:
            at = ", ".join(f"line {s['line']}" for s in anchored)
            lines.append(f"It anchors {_count(len(anchored), 'seal', 'seals')} on a chain: {at}.")

    consults = facts["consults"]
    if not consults:
        lines.append("It asks the Spirit nothing.")
    else:
        at = ", ".join(f"line {c['line']}" for c in consults)
        lines.append(f"It asks the Spirit {_count(len(consults), 'question', 'questions')}: {at}.")

    summons = facts["summons"]
    if not summons:
        lines.append("It summons nothing.")
    else:
        verbs = ", ".join(
            f"{s['verb'] or 'an unnamed verb'} (line {s['line']})" for s in summons
        )
        lines.append(f"It summons {_count(len(summons), 'verb', 'verbs')}: {verbs}.")

    imports = facts["imports"]
    if not imports:
        lines.append("It brings in nothing.")
    else:
        paths = ", ".join(f"{i['path']} (line {i['line']})" for i in imports)
        lines.append(f"It brings in {_count(len(imports), 'scroll', 'scrolls')}: {paths}.")

    perms = facts["permissions"]
    manifest = PermissionManifest()
    manifest.read_paths = list(perms.get("read", []))
    manifest.write_paths = list(perms.get("write", []))
    manifest.hosts = list(perms.get("network", []))
    manifest.stdin = bool(perms.get("stdin", False))
    manifest.summons = list(perms.get("summon", []))
    described = manifest.describe()
    if not described:
        lines.append(
            "It declares no permissions, so it touches nothing of the outer world."
        )
    else:
        lines.append(f"It declares {_count(len(described), 'permission', 'permissions')}:")
        for grant in described:
            lines.append(f"  - it {grant}")

    return "\n".join(lines)
