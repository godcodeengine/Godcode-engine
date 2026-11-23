"""Permission manifests for God Code.

A scroll may declare what it is allowed to touch:

    DECLARE PERMISSION TO READ "data/"
    DECLARE PERMISSION TO WRITE "out/"
    DECLARE PERMISSION TO SPEAK WITH "api.example.com"
    DECLARE PERMISSION TO ASK THE WORLD
    DECLARE PERMISSION TO SUMMON "reports.weekly"
    DECLARE PERMISSION TO SEAL THE COVENANT

The manifest is collected from the scroll's top-level decrees before the
run begins. It never widens what the host allows: the effective grant is
always *host policy intersect manifest*. A scroll that reaches for a
power it did not declare is counselled and stopped with a
``SandboxViolation``.

Imported scrolls may narrow the lead scroll's manifest, never widen it:
an imported scroll whose declarations reach beyond the lead scroll's is
refused before it runs. Relative path patterns are resolved against the
directory of the scroll that declares them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

__all__ = [
    "PermissionManifest",
    "collect_manifest",
    "POWERS",
]

# The six declared powers, in the order they read in counsel.
POWERS = ("read", "write", "network", "stdin", "summon", "seal")

# AST node class name we collect from, so this module never imports the
# parser or interpreter (no import cycles).
_DECLARE_PERMISSION_NODE = "DeclarePermission"


def _node_is_permission(stmt: Any) -> bool:
    return type(stmt).__name__ == _DECLARE_PERMISSION_NODE


@dataclass
class PermissionManifest:
    """The declared powers of one scroll or one whole run.

    Path patterns are stored as absolute directory prefixes. A pattern
    naming a file grants that exact file; a pattern naming a directory
    grants everything beneath it.
    """

    read_paths: tuple[str, ...] = ()
    write_paths: tuple[str, ...] = ()
    hosts: tuple[str, ...] = ()
    stdin: bool = False
    summons: tuple[str, ...] = ()
    seal: bool = False

    def __bool__(self) -> bool:
        return bool(
            self.read_paths
            or self.write_paths
            or self.hosts
            or self.stdin
            or self.summons
            or self.seal
        )

    # -- composition ----------------------------------------------------

    def merge(self, other: "PermissionManifest") -> "PermissionManifest":
        """Union two manifests.

        Composition is only ever applied after :meth:`excess_over` has
        proved ``other`` fits inside ``self``, so in a run the union can
        narrow the lead scroll's grants or restate them, never widen
        them beyond what the lead scroll declared.
        """
        def _union(a: tuple[str, ...], b: tuple[str, ...]) -> tuple[str, ...]:
            seen: list[str] = []
            for item in (*a, *b):
                if item not in seen:
                    seen.append(item)
            return tuple(seen)

        return PermissionManifest(
            read_paths=_union(self.read_paths, other.read_paths),
            write_paths=_union(self.write_paths, other.write_paths),
            hosts=_union(self.hosts, other.hosts),
            stdin=self.stdin or other.stdin,
            summons=_union(self.summons, other.summons),
            seal=self.seal or other.seal,
        )

    def excess_over(self, ceiling: "PermissionManifest") -> list[str]:
        """Powers this manifest declares beyond ``ceiling``, in counsel.

        One entry per widening declaration, spoken the way the scroll
        would declare it (paths in their resolved form). An empty list
        means this manifest fits inside the ceiling: it narrows the
        ceiling or restates it, and may be breathed in beneath it.
        """
        excess: list[str] = []
        for path in self.read_paths:
            if not self._under(path, ceiling.read_paths):
                excess.append(f'READ "{path}"')
        for path in self.write_paths:
            if not self._under(path, ceiling.write_paths):
                excess.append(f'WRITE "{path}"')
        for host in self.hosts:
            if not any(host == granted or host.endswith("." + granted)
                       for granted in ceiling.hosts):
                excess.append(f'SPEAK WITH "{host}"')
        if self.stdin and not ceiling.stdin:
            excess.append("ASK THE WORLD")
        for verb in self.summons:
            if not ceiling.allows_summon(verb):
                excess.append(f'SUMMON "{verb}"')
        if self.seal and not ceiling.seal:
            excess.append("SEAL THE COVENANT")
        return excess

    # -- enforcement ----------------------------------------------------

    @staticmethod
    def _under(path: str, granted: tuple[str, ...]) -> bool:
        try:
            resolved = os.path.realpath(path)
        except OSError:
            return False
        for base in granted:
            if resolved == base or resolved.startswith(base + os.sep):
                return True
        return False

    def allows_read(self, path: str) -> bool:
        return self._under(path, self.read_paths)

    def allows_write(self, path: str) -> bool:
        return self._under(path, self.write_paths)

    def allows_host(self, url: str) -> bool:
        try:
            host = (urlparse(url).hostname or "").lower()
        except (ValueError, AttributeError):
            return False
        return any(host == granted or host.endswith("." + granted)
                   for granted in self.hosts)

    def allows_summon(self, verb: str) -> bool:
        return any(verb == name or verb.startswith(name + ".")
                   for name in self.summons)

    # -- machine interfaces ----------------------------------------------

    def to_json(self) -> dict:
        """Stable shape for agents: `godcode permissions --json`."""
        return {
            "read": list(self.read_paths),
            "write": list(self.write_paths),
            "network": list(self.hosts),
            "stdin": self.stdin,
            "summon": list(self.summons),
            "seal": self.seal,
        }

    def describe(self) -> list[str]:
        """One human line per granted power, for counsel and CLI output."""
        lines: list[str] = []
        for path in self.read_paths:
            lines.append(f"may read from {path}")
        for path in self.write_paths:
            lines.append(f"may write to {path}")
        for host in self.hosts:
            lines.append(f"may speak with {host}")
        if self.stdin:
            lines.append("may ask the outer world")
        for name in self.summons:
            lines.append(f"may summon {name}")
        if self.seal:
            lines.append("may seal the covenant")
        return lines


def collect_manifest(statements: list, base_dir: str | Path | None) -> PermissionManifest:
    """Gather DECLARE PERMISSION decrees from top-level statements.

    Looks at the scroll's top level and inside any top-level creation
    blocks. ``base_dir`` resolves relative path patterns to absolute
    prefixes; ``None`` resolves them against the current working
    directory.
    """
    base = Path(base_dir) if base_dir else Path.cwd()
    reads: list[str] = []
    writes: list[str] = []
    hosts: list[str] = []
    stdin = False
    summons: list[str] = []
    seal = False

    def _resolve(pattern: str) -> str:
        candidate = Path(pattern)
        if not candidate.is_absolute():
            candidate = base / candidate
        try:
            return os.path.realpath(candidate)
        except OSError:  # pragma: no cover - defensive
            return str(candidate)

    def _visit(stmts: list, inside_block: bool) -> None:
        nonlocal stdin, seal
        for stmt in stmts:
            if _node_is_permission(stmt):
                power = getattr(stmt, "power", "")
                target = getattr(stmt, "target", None)
                if power == "read" and target:
                    reads.append(_resolve(target))
                elif power == "write" and target:
                    writes.append(_resolve(target))
                elif power == "network" and target:
                    hosts.append(target.strip().lower())
                elif power == "stdin":
                    stdin = True
                elif power == "summon" and target:
                    summons.append(target.strip())
                elif power == "seal":
                    seal = True
            elif (not inside_block
                    and type(stmt).__name__ == "CreationBlock"):
                _visit(getattr(stmt, "statements", []), True)

    _visit(statements, False)

    def _dedupe(items: list[str]) -> tuple[str, ...]:
        seen: list[str] = []
        for item in items:
            if item not in seen:
                seen.append(item)
        return tuple(seen)

    return PermissionManifest(
        read_paths=_dedupe(reads),
        write_paths=_dedupe(writes),
        hosts=_dedupe(hosts),
        stdin=stdin,
        summons=_dedupe(summons),
        seal=seal,
    )
