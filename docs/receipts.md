# Replayable receipts

A receipt is a checkable record of one sandboxed run. It answers the
question a funder, a reviewer, or a stranger on the internet would ask
about any God Code run: prove it happened, and prove this is what it
said.

## The idea in one paragraph

Record a run and you get a single JSON document holding the scroll's
source, the fingerprint of that source, the lines the run revealed,
whether it finished cleanly, the failure when it did not, the intents
it discerned, and the permission manifest it ran under. The document
also carries its own fingerprint, computed over everything else in it.
Hand the receipt to anyone. They run one command, the engine replays
the source in its sandbox, and the command says plainly whether the
replay matches the record. No trust in the person who handed it over
is required. The fingerprint is what makes that true: change one
revealed line after recording and the fingerprint no longer matches,
so verification stops before any replay and says the record was
changed.

## Commands

```bash
godcode receipt record scroll.god
godcode receipt record scroll.god my-receipt.json
godcode receipt verify scroll.receipt.json
godcode receipt verify scroll.receipt.json --json
```

`record` runs the scroll under the strict sandbox policy and writes
the receipt document. With no second argument it writes beside the
scroll, named after it: `scroll.god` becomes `scroll.receipt.json`.
With `--json` it also prints the receipt document on stdout. A failed
run still records, so the failure itself can be replayed and checked;
the human message says which failure code was recorded.

`verify` reads a receipt document and checks it in two steps. First
the seal: the source fingerprint must match the recorded source, and
the receipt fingerprint must match the rest of the document. Then the
replay: the recorded source runs again, sandboxed, and the outcome,
the revealed lines, and the failure code are compared with the
record. Exit 0 only when every comparison matches. With `--json` the
report is one JSON document with `verified`, `seal_intact`,
`replayed`, `differences`, and the full `replay`.

## What verify compares, and what it does not

Compared: the source fingerprint, the clean or failed outcome, the
revealed lines in order, and the failure code on a failed run. The
intents and the permission manifest are recorded for reading, not
compared, because discernment confidence is a reading of the run, not
its result.

Not compared, by design: how long the run took. Timing is not part of
a run's meaning.

## Honest limits

Receipts record sandboxed runs only. A sandboxed run writes nothing to
the host world, so a receipt never carries ledger blocks and never
touches a chain file. That is what makes a receipt safe to pass
around, and it is also the boundary of the claim.

Two kinds of scroll replay differently, and verify says so instead of
pretending otherwise:

- A scroll that reads a changing value, such as the clock or an
  anchor timestamp, reveals a different line on replay. Verify
  reports the revealed lines as differing.
- A scroll that imports a scroll from its own directory needs that
  directory named again at verify time, with `--import-dir`. The
  standard library scrolls are always available. Without the
  directory, the replay fails on the import and verify reports the
  failure code as differing.

## The shape

The receipt shape is frozen under the dated schema
`https://getgodcode.com/schemas/2026-11/receipt.json`, printed by
`godcode schema receipt`. Required fields never change meaning;
additive fields may appear, and a breaking change would ship under a
new dated schema, with this one staying published.

## A worked example

The repository carries `examples/receipt_demo.god`, a small harvest
count that fingerprints its own report:

```bash
godcode receipt record examples/receipt_demo.god
godcode receipt verify examples/receipt_demo.receipt.json
```

The second command prints that the receipt replays exactly as
recorded. Edit any revealed line in the receipt file and run verify
again: it stops at the fingerprint and says the record was changed
after it was recorded.
