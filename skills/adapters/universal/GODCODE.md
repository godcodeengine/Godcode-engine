# GODCODE.md: drop-in rules for any AI agent

Paste this into your agent's instructions (OpenCode, Gemini, Zed, Copilot, or any harness) to teach it God Code.

---

God Code is a programming language that reads like scripture. Write real software in words of faith, in your own language, and watch it run. Human-readable, safe, and built for humans and AI creating together. Created in Botswana, open to the world.

A God Code program is a **scroll** (`.god` file). Install the CLI with `pip install godcode-engine`.

## The loop

1. Generate the scroll. Everything lives between `BEGIN CREATION` and `END CREATION`.
2. `godcode check --json scroll.god`: exit 0 is pure, 1 is diagnostics. Fix every diagnostic from its `hint`.
3. `godcode run --sandbox --json scroll.god`: inspect `output`, `error`, `intents`, `permissions`. Iterate.

Never run an untrusted scroll without `--sandbox`.

## The language

- `DECLARE x AS ...` assigns. `IS` / `IS NOT` compare. `REVEAL(expr)` prints. No stdin.
- `"grace upon {name}"` interpolates. `"{{"` writes a literal brace.
- `IF cond THEN` ... `ENDIF`. `FOR x IN RANGE(1, 4)` or a list ... `ENDFOR`. `WHILE` ... `ENDWHILE`.
- `DEFINE RITE name()` ... `END RITE`, invoked with `INVOKE name()`.
- `DECLARE INTENT "plain words" ON rite_name` names a rite's purpose. Drift counsels, never fails a run.
- `SEAL(expr)` writes a covenant block. `ANCHOR(expr)` returns a receipt map. `CONSULT("q")` asks the oracle. `ASCEND` ends peacefully.
- Pure, no import: `SHA256`, `HMAC`, `BASE64_ENCODE`, `BASE64_DECODE`, `REPEAT(s, n)`, `TRIM`, `SORT`, `SUM_OF`, `FIRST`, `LAST`, `UNIQUE`, `INDEX_OF`, `KEYS`, `VALUES`, `HAS_KEY`, `MERGE`, `ABS`, `ROUND`, `SQRT`, `POW`.
- Permission manifests sit at the top inside `BEGIN CREATION`: `DECLARE PERMISSION TO READ "data/"`, `TO WRITE "out/"`, `TO SPEAK WITH "host"`, `TO ASK THE WORLD`, `TO SUMMON "verb"`. Undeclared powers are stopped. Read a foreign manifest with `godcode permissions --json scroll.god`.
- `# tongue: tn` for Setswana, `# tongue: zu` for isiZulu. English still works.
- Gotchas: reading an undeclared name raises a gentle error (a bare word needs its mark, `:word`, to be a Symbol); division by zero is rejected; keywords are case-insensitive.
