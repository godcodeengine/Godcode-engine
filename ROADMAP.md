# God Code Roadmap

Where the language is headed, in plain words. This is a living document: it changes as the language grows.

## Just landed

- Performance benchmarks: published with the method. `python3 bench/bench.py`
  drives the real interpreter over seven workloads (lexing and parsing, deep
  rite recursion, a tight counting loop, string interpolation, list work,
  JSON round trips through the real `json-tools` registry scroll, and
  `ANCHOR` chain sealing) and reports the median of five timed runs after
  warmup. Fresh numbers recorded on current main live in `bench/RESULTS.md`
  with the machine they were taken on, and `tests/test_bench.py` keeps the
  suite green. Rerun on the same machine to measure improvements honestly.

- The second tongue: God Code speaks isiZulu. A scroll with the
  `# tongue: zu` pragma writes keywords in isiZulu (`VEZA` for `REVEAL`,
  `UMA` for `IF`, `ZAMA` for `TRY`, and the full table in
  `docs/TONGUES.md`); two-word closers `QEDA UMA` and `QEDA ZAMA` close
  blocks. Every tool honours it, the playground boots a "Sawubona
  (isiZulu)" sample, the language server offers isiZulu completions,
  hover docs, and block snippets, and the VS Code extension paints
  isiZulu keywords and ships `sawubona` and `uma` starter snippets.
  Editor snippets now travel with each tongue's own table, so the next
  tongue brings its snippets with it. New example:
  `examples/first_blessing_zu.god`.

- The commons: twenty-six everyday builtins, always present, in a fourth
  stdlib pillar (`godcode/stdlib_commons.py`). Words (`TRIM`, `REPLACE`,
  `STARTS_WITH`, `ENDS_WITH`, `SUBSTRING`, `CONTAINS`, `COUNT`, `REPEAT`),
  lists
  (`SORT`, `MIN_OF`, `MAX_OF`, `SUM_OF`, `FIRST`, `LAST`, `UNIQUE`,
  `INDEX_OF`), maps (`KEYS`, `VALUES`, `HAS_KEY`, `MERGE`), and numbers
  (`ABS`, `ROUND`, `FLOOR`, `CEIL`, `SQRT`, `POW`). Pure computation, so
  they run unchanged in the sandbox; misuse is answered with a gentle
  error. Documented in the language reference, the learn page, the
  language server, and the VS Code extension.

- Global editions begin: God Code speaks Setswana. A scroll with the
  `# tongue: tn` pragma writes keywords in Setswana (the full table is in
  `docs/TONGUES.md`); every tool honours it, the playground speaks it,
  and more tongues arrive by community proposal. The editors keep pace:
  the language server offers Setswana completions and hover docs when it
  sees the pragma, and the VS Code extension paints Setswana keywords and
  ships Setswana starter snippets.
- A scrollhouse of hashes: `SHA256`, `HMAC`, `BASE64_ENCODE`, and
  `BASE64_DECODE` as always-present builtins (pure, sandbox-safe), plus
  the `hashes` registry scroll with the friendly rites `FINGERPRINT`,
  `SIGN`, `VERIFY_SIGNATURE`, `VEIL`, and `UNVEIL`. Documented in
  `docs/LANGUAGE_REFERENCE.md` §13, the language server's hover docs, the
  VS Code extension (highlighting + two snippets), and the site learn page.
- The linter (`godcode lint`): six gentle rules that catch unused names, undefined names, shadowing, empty blocks, unreachable code, and duplicate declarations.
- A bigger standard library: JSON, file reading and writing, directory listing, dates and times, and fetching pages from the web.
- The test runner (`godcode test`): write rites named `TEST_*` and the runner finds them, runs them, and reports pass or fail.
- `BREAK` and `CONTINUE` for loops.
- `TRY` / `CATCH` error handling, plus stack traces that show the path through your rites when something fails.
- The formal language specification (`docs/LANGUAGE_SPEC.md`) and the EBNF grammar (`docs/GRAMMAR.ebnf`).
- The remote scroll registry: `godcode scroll search` queries the public
  catalog over HTTPS, `install` falls back to the remote registry when the
  local index has no answer (`--remote` prefers it), `publish --remote`
  pushes with a publish token (`GODCODE_PUBLISH_TOKEN`), `update` moves
  installed scrolls to the newest known version, `uninstall` removes them,
  manifests declare `dependencies` resolved recursively with cycle
  detection, and sha256 checksums are recorded on publish and verified on
  install. The versioning scheme, compatibility promise, and deprecation
  process are written down in `docs/VERSIONING.md`.

- How God Code is kept: `GOVERNANCE.md` writes down what was settled
  with the founder. There is no company behind the language, and none is
  needed: it is Apache 2.0 open source, and the founder (Alakanani
  Itireleng) is the keeper of the vision, holding the brand, the
  direction, the home, and the money when it comes. Anyone may propose,
  and the keeper gives the final verdict. The lines the language will
  not cross are written down: no wallets and no real chain calls, no
  breaking of the compatibility promise, no hype in the claims. Linked
  from the README and CONTRIBUTING, and kept honest by
  `tests/test_governance.py`.

## What is next

- More tongues: community-proposed editions beyond Setswana.
- More of the standard library: concurrency, and whatever everyday work
  remains beyond the commons.
- Editor tooling polish: the VS Code extension, the language server, and the playground keeping pace with the language.

## Deliberately not planned

- A compiler to native machine code. God Code is interpreted, and that is a choice, not a gap.
- Mobile targets. The language runs where Python runs.

No hype: items move from "next" to "landed" when they are built, tested, documented, and green.
