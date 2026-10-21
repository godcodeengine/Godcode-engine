# Machine interfaces: the contract for agents

God Code speaks JSON as fluently as it speaks in tongues. Four commands
emit one JSON document each on stdout, shaped by four dated schemas. An
agent parses every output without guessing: read the schema first, then
trust the shape.

## The four commands

```bash
godcode check --json scroll.god
godcode run --sandbox --json scroll.god
godcode explain scroll.god --json
godcode ledger verify --json
```

`check --json` lexes and parses without running: `ok` plus a
`diagnostics` array (`line`, `col`, `code`, `severity`, `message`,
`hint`). `run --sandbox --json` runs inside the deny-by-default
sandbox and reports `output`, `seals`, `intents`, `permissions`, and
`error` (null on a clean run; `line`, `col`, `code`, `message`, and a
rite call `trace` on failure), with `stats` timing the run. `explain
--json` reads the scroll's static facts without running it: tongue,
rites and their declared intents, declared names, reveals, seals,
summoned verbs, consults, imports, and the permission manifest.
`ledger verify --json` attests the covenant chain and the anchor chain
for tampering, reporting each with `ok` and a human `message`.

`godcode explain scroll.god` without `--json` says the same facts in
warm plain words, for humans.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | ok, or pure (check), or both chains verify (ledger) |
| 1 | diagnostics present, run failed, explain could not read the scroll, or a chain failed verification |
| 2 | usage error (argparse: bad flags, missing file argument) |

## The four schemas

| Command | Schema |
|---------|--------|
| `check --json` | https://getgodcode.com/schemas/2026-10/check.json |
| `run --sandbox --json` | https://getgodcode.com/schemas/2026-10/run.json |
| `explain --json` | https://getgodcode.com/schemas/2026-10/explain.json |
| `ledger verify --json` | https://getgodcode.com/schemas/2026-10/ledger-verify.json |

God Code releases by date, not by numbers, so the machine interfaces
are dated, not versioned. Fetch any schema from the engine itself:

```bash
godcode schema            # list the four schema names
godcode schema explain    # print the explain schema as JSON
```

The same schemas ride the agent bridge: `godcode tools --json` lists
nine tools (`check`, `run`, `consult`, `intent`, `anchor_verify`,
`ledger_verify`, `permissions`, `explain`, `get_schema`), and
`get_schema` returns any schema as parsed JSON. The schemas also ship
inside the installed package, so an agent can resolve them without the
CLI.

## The stability promise

These shapes are frozen under their dated schema. Additive fields may
appear but required fields never change meaning, and validation allows
extras so a newer engine never breaks an older agent. Any breaking
change ships under a new dated schema, and the old one stays published
and keeps validating what it always validated.
