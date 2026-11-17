# Troubleshooting

`godcode check --json` is the first doctor. Read the `hint` on every diagnostic. It usually names the fix.

## Error codes

| Code | Meaning | Typical fix |
|---|---|---|
| `LEXER_ERROR` | bad characters or an unterminated string | check the quotes on the reported line; strings use double quotes |
| `PARSE_ERROR` | grammar violation | missing `BEGIN CREATION` / `END CREATION`, or a block closer (`ENDIF`, `ENDFOR`, `ENDWHILE`, `END RITE`) |
| `RUNTIME_ERROR` | failed while running | declare names before use; re-read the reported line |
| `FILE_ERROR` | the scroll is unreadable | check the path |

## The usual suspects

**"Nothing runs."** Every statement must live between `BEGIN CREATION` and `END CREATION`. Nothing outside the block runs.

**"Unexpected 'BEGIN'."** A permission manifest goes *inside* `BEGIN CREATION`, at the top. It is not a preamble above it.

**"Malformed number."** A decimal point must be followed by digits. `1..3` is not a range. Use `RANGE(1, 4)` to walk 1, 2, 3.

**A block that never closes.** `IF` needs `ENDIF`, `FOR` needs `ENDFOR`, `WHILE` needs `ENDWHILE`, a rite needs `END RITE`. One missing closer breaks everything below it.

**`IF` without `THEN`.** The block form is `IF condition THEN` on its own line. The single-line form is `IF condition THEN REVEAL("...")`.

**Forgetting `INVOKE`.** `DEFINE RITE` only teaches the rite. `INVOKE name()` is what calls it.

**A name that was never declared.** Reading one is loud now: the run stops with "There is no 'name' in this creation. It was never spoken into being", and a `Did you mean 'X'?` when a declared name stands near. Trust the suggestion. If the bare word itself was the value you wanted, mark it: `:name`.

**Division by zero.** Rejected outright: "division by nothing is not permitted". Guard the divisor first.

**A lone `{` in a string.** `{` opens interpolation. To print a plain brace, double it: `"{{"`.

**`seals` is empty in JSON.** Under `--sandbox` the ledger is confined, so no covenant blocks are recorded. The scroll still ran. Run without `--sandbox` only on scrolls you trust.

**A tongue pragma that does nothing.** The pragma is a comment on its own line before the creation block: `# tongue: tn` for Setswana, `# tongue: zu` for isiZulu. Named tools like `SHA256` never translate.

**Exit code 2.** That is a usage error, not a scroll error. Check the command line: a missing file argument, an unknown flag.

## When the check is clean but the run surprises you

1. Read `error` first: `line`, `col`, `code`, `message`.
2. Read `output`: on failure it holds the lines revealed *before* the error, which tells you how far the scroll walked.
3. Read `intents`: a rite that drifted from its declared intent gets gentle counsel, never a failure. Drift is information, not an error.
4. Read `permissions`: the manifest the run carried. If a power was refused, it was not declared.
