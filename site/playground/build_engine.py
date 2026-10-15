"""Bundle the real God Code engine for the browser playground.

The playground runs this repository's own interpreter in the browser
through Pyodide. This script gathers what the engine needs into one
file, ``site/playground/engine.json``:

- ``files``: the ``godcode`` package (every module and stdlib scroll)
  and the Spirit's training dataset, keyed by their path in the repo,
  so the worker can lay them out exactly as they rest here;
- ``library``: the newest version of each registry scroll, keyed
  ``<name>.god``, so ``IMPORT "blessings"`` works in the playground;
- ``samples``: the examples below, read from ``examples/``, so the
  playground's samples are the very scrolls the test suite runs.

Rebuild after changing the engine:

    python3 site/playground/build_engine.py

``--check`` rebuilds in memory and exits 1 if ``engine.json`` is stale.
``tests/test_webrun.py`` runs that check, so the playground can never
quietly drift from the engine again.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from godcode.registry import read_manifest  # noqa: E402  (after the path)

OUT = ROOT / "site" / "playground" / "engine.json"

#: Examples offered as playground samples: (file in examples/, label).
#: Each must run cleanly under the strict sandbox (tests/test_webrun.py).
SAMPLES = [
    ("commons_demo.god", "The Commons (everyday builtins)"),
    ("strings_demo.god", "The Scroll of Strings"),
    ("time_demo.god", "The Scroll of Hours (NOW, TODAY)"),
    ("intent_demo.god", "Declared Intent"),
    ("anchor_demo.god", "Anchored Seals (ANCHOR)"),
    ("consult_demo.god", "Consult the Oracle"),
    ("scroll_blessings_demo.god", "Scroll Registry (IMPORT \"blessings\")"),
    ("rites_demo.god", "Rites and Closures"),
    ("lots.god", "Casting Lots"),
    ("first_blessing_ig.god", "Ndewo (Igbo)"),
    ("first_blessing_pg.god", "How far (Nigerian Pidgin)"),
]


def _version() -> str:
    for line in (ROOT / "godcode" / "__init__.py").read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            return line.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("build_engine: no __version__ in godcode/__init__.py")


def _engine_files() -> dict[str, str]:
    package = ROOT / "godcode"
    paths = sorted(package.glob("*.py"))
    paths += sorted((package / "scrolls").glob("*.god"))
    paths += sorted((package / "scrolls").glob("*.toml"))
    paths.append(ROOT / "god_code_training_dataset.csv")
    return {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8") for p in paths}


def _version_key(version: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in version.split("."))


def _library() -> dict[str, str]:
    """The newest version of each registry scroll, by its bare name."""
    library: dict[str, str] = {}
    for scroll_dir in sorted((ROOT / "registry" / "scrolls").iterdir()):
        if not scroll_dir.is_dir():
            continue
        versions = [v for v in scroll_dir.iterdir() if (v / "scroll.toml").is_file()]
        if not versions:
            continue
        newest = max(versions, key=lambda v: _version_key(v.name))
        manifest = read_manifest(newest / "scroll.toml")
        entry = newest / manifest.get("entry", f"{scroll_dir.name}.god")
        library[f"{manifest.get('name', scroll_dir.name)}.god"] = entry.read_text(encoding="utf-8")
    return library


def _samples() -> list[dict[str, str]]:
    return [
        {"file": name, "label": label,
         "code": (ROOT / "examples" / name).read_text(encoding="utf-8")}
        for name, label in SAMPLES
    ]


def build() -> str:
    bundle = {
        "version": _version(),
        "files": _engine_files(),
        "library": _library(),
        "samples": _samples(),
    }
    return json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if site/playground/engine.json is stale")
    args = parser.parse_args(argv)
    fresh = build()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != fresh:
            print("site/playground/engine.json is stale: run python3 site/playground/build_engine.py",
                  file=sys.stderr)
            return 1
        print("site/playground/engine.json is current.")
        return 0
    OUT.write_text(fresh, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(fresh.encode()) // 1024} KB, engine {_version()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
