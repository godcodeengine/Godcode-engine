# AGENTS.md — God Code, for AI agents

God Code is a small divine-flavored programming language ("scrolls", `.god`
files). This file tells an AI agent how to generate, validate, and run it
safely. Prefer these commands over scraping prose output.

## Validate first, always

```bash
godcode check --json scroll.god
```

Returns one JSON document: `{"tool":"godcode","command":"check","file":…,
"ok":true|false,"diagnostics":[{line,col,code,severity,message,hint}]}`.
Exit 0 = pure, 1 = diagnostics, 2 = usage error. Fix every diagnostic
before running. `line`/`col` are 1-based; `col` may be null.

## Execute safely

```bash
godcode run --sandbox --json scroll.god
```

Same exit-code convention. JSON shape: `{"tool","command","file","ok",
"output":[…],"seals":[{block,hash}],"error":{…}|null,"stats":{"ms":…}}`.
`output` = every line printed during the run (REVEAL lines plus engine
notices like `[SEAL]`); on runtime error it holds lines revealed *before*
the error, and `error` carries `line`/`col`/`code`/`message`. `--sandbox`
confines execution; `--json` composes with plain `run`/`check` too.

## Share scrolls

```bash
godcode new my-scroll      # raise a project: main.god, test_main.god,
                           # scroll.toml, README.md (--json for agents)
godcode scroll …          # install / publish / verify scrolls in the registry
godcode ledger verify     # verify the covenant chain
```

## Language gotchas (check these before "fixing" generated code)

- Every program needs `BEGIN CREATION` … `END CREATION`. Nothing runs outside it.
- Comments start with `#` and run to end of line.
- Comparisons use `IS` / `IS NOT` (`==`/`!=` also work). Assignment is `DECLARE x AS …`.
- Keywords are case-insensitive; canonical style is UPPER.
- Output: `REVEAL(expr)`. Input-free; there is no stdin.
- Strings breathe values in: `"grace upon {name}"` interpolates any expression (`{a * b}`, `{UPPER(name)}`); `{{` and `}}` write a plain brace.
- Blocks close explicitly: `ENDIF`, `ENDFOR`, `ENDWHILE`, `END RITE`.
- `SEAL(expr)` appends a tamper-evident covenant block to the ledger.
- `ANCHOR(expr [, chain])` anchors a value's hash on a chain (default
  `simulated`, a local genesis-anchored chain) and returns a receipt map
  `{chain, anchor_hash, height, timestamp, payload_hash}` — index it like
  `receipt["anchor_hash"]`; `TYPE(receipt)` is `"map"`.
- `SHA256(x)` fingerprints a word, number, or truth as 64 hex characters.
  `HMAC(key, message)` seals a message under a key (HMAC-SHA-256).
  `BASE64_ENCODE(x)` / `BASE64_DECODE(s)` veil and unveil words. All four
  are pure: they need no import and run unchanged under `--sandbox`.
- The commons: everyday tools, always present, pure and sandbox-safe.
  Words: `TRIM`, `REPLACE`, `STARTS_WITH`, `ENDS_WITH`, `SUBSTRING`,
  `CONTAINS`, `COUNT`, `REPEAT`. Lists: `SORT` (returns a new list), `MIN_OF`,
  `MAX_OF`, `SUM_OF`, `FIRST`, `LAST`, `UNIQUE`, `INDEX_OF` (-1 when
  absent). Maps: `KEYS`, `VALUES`, `HAS_KEY`, `MERGE` (returns a new
  map). Numbers: `ABS`, `ROUND` (half away from zero), `FLOOR`, `CEIL`,
  `SQRT`, `POW`. To write a literal `{` inside a string, double it:
  `"{{"` (a lone `{` opens interpolation).
- `CONSULT("question")` asks the local Spirit oracle; answers in 2-3
  sentences, works in the sandbox, never fails the run.
- `DECLARE INTENT "words..." ON rite_name` names a rite's purpose; at
  invocation the Spirit checks alignment and counsels gently on drift.
  Drift can never fail a run.
- `ASCEND` ends the run peacefully (not an error).
- An unbound name evaluates to a Symbol. It does not raise. `BREATHE LIFE INTO`
  an undeclared name *does* raise at runtime.
- Error messages may end with `Did you mean 'X'?` (misspelled rite, variable,
  bless target, or map key). The human CLI (`run`, `run --sandbox`, `check`,
  `fmt`) prints the offending source line beneath the message, with a caret at
  the column when known.
- Tongues: a scroll with `# tongue: tn` writes keywords in Setswana
  (`SIMOLOLA`/`BEGIN`, `SENOLA`/`REVEAL`, `FA`/`IF`...), and a scroll with
  `# tongue: zu` writes them in isiZulu (`QALA`/`BEGIN`, `VEZA`/`REVEAL`,
  `UMA`/`IF`...). `# tongue: ig` is Igbo (`BIDO`/`BEGIN`,
  `GOSI`/`REVEAL`, `Ọ BỤRỤ`/`IF`), and `# tongue: pg`
  (or `pcm`) is Nigerian Pidgin (`OYA`/`BEGIN`, `SHOW`/`REVEAL`,
  `FINISH IF`/`ENDIF`); see `docs/TONGUES.md` for every word table.
  English keywords still work in the same file. `fmt` renders canonical
  English; the named tools (`SHA256`, `UPPER`, ...) never translate. The
  language server reads the pragma: completions offer `SENOLA (REVEAL)`
  for Setswana or `VEZA (REVEAL)` for isiZulu, plus block snippets in the
  tongue, and hover shows the English keyword's docs for a tongue word.
  The VS Code grammar highlights Setswana and isiZulu keywords too.
- Division by zero is rejected: "division by nothing is not permitted".

## Error codes (`--json`)

| Code | Meaning | Typical fix |
|---|---|---|
| `LEXER_ERROR` | bad characters / unterminated string | check quotes on the reported line |
| `PARSE_ERROR` | grammar violation | missing BEGIN/END CREATION or block closer |
| `RUNTIME_ERROR` | failed while running | DECLARE names before use; re-read the line |
| `FILE_ERROR` | scroll unreadable | check the path |

## Agent workflow

generate → `explain --json` (on an unfamiliar scroll) → `check --json` →
fix from diagnostics → `run --sandbox --json` → inspect
`output`/`error`/`intents` → iterate. Never run untrusted scrolls without
`--sandbox`. Keep the human's production checklist (provider contracts,
real credentials, Bank of Botswana sandbox submission) out of the way.
Demo in sandbox mode.

## Read before you run

```bash
godcode explain scroll.god            # plain words, for humans
godcode explain scroll.god --json     # static facts: tongue, rites and
                                      # their intents, names, reveals,
                                      # seals, summons, consults, imports,
                                      # permissions. Nothing executes.
```

Explaining a scroll is always safe: the walk is read-only over the
parsed AST. Use it on any scroll you did not write before running it.

## Machine interface schemas

The four `--json` shapes are frozen under dated schemas (God Code
releases by date, not by numbers):

```bash
godcode schema            # list: check, run, explain, ledger-verify
godcode schema explain    # print one schema as JSON
```

Schema IDs live under `https://getgodcode.com/schemas/2026-10/`. The
full contract (commands, exit codes, stability promise) is in
`docs/machine-interfaces.md`. Required fields never change meaning;
additive fields may appear. A breaking change would ship under a new
dated schema, with the old one staying published.

## Agent tool bridge

Nine MCP-compatible tool schemas for agent frameworks, plus a JSON-RPC
bridge over stdio:

```bash
godcode tools --json     # check, run, consult, intent, anchor_verify,
                         # ledger_verify, permissions, explain, get_schema
godcode bridge           # serve the tools to an agent host over stdio
godcode intent "words"   # resolve the intent behind words with the Spirit
godcode ledger verify    # attest the covenant chain AND the anchor chain
godcode permissions scroll.god   # read a scroll's permission manifest (runs nothing)
```

`run --json` reports now carry an `intents` array: one entry per invoked
rite carrying a `DECLARE INTENT`, with `declared`, `discerned`,
`confidence`, and `aligned`. Declare the intent of generated rites and
check `intents` for drift after each run. They also carry a
`permissions` block: the run's permission manifest.

## Permission manifests

Generated scrolls should declare what they may touch, at the top of
the scroll:

```
DECLARE PERMISSION TO READ "data/"
DECLARE PERMISSION TO WRITE "out/"
DECLARE PERMISSION TO SPEAK WITH "api.example.com"
DECLARE PERMISSION TO ASK THE WORLD
DECLARE PERMISSION TO SUMMON "reports.weekly"
```

Any rite that reaches for an undeclared power is stopped. The manifest
never widens the host policy: `--sandbox` still narrows everything.
Read a scroll's manifest safely with `godcode permissions --json`
before running it.

## House rules for agents working on God Code

- **Rebuild the playground bundle after touching `godcode/`.** The live
  playground runs the real engine from `site/playground/engine.json`.
  Run `python3 site/playground/build_engine.py` and commit the result;
  `tests/test_webrun.py` fails while the bundle is stale.
- **No version numbers in anything a human reads.** God Code releases by date now, not by numbers. Never write a version label in a commit
  message, a doc, a site page, a README, a changelog header, or a Discord
  announcement. Changelog entries are headed by date. The future is commits,
  not versions.
- Structural versions stay but stay invisible: `pyproject.toml`,
  `godcode/__init__.py` `__version__`, scroll manifest `version` fields,
  registry dependency versions, `/v1/` API paths, and the VS Code
  `package.json` version are machine-readable packaging facts. Never mention
  them in prose, headings, or announcements.
- Never use em dashes (—) or spaced en dashes between sentences in
  user-facing text. Use a full stop instead.
