---
name: godcode
description: Write, run, check, and debug God Code scrolls (.god files). Use this skill whenever someone asks for God Code, a scroll, scripture-flavored code, or help with the God Code language, its CLI, its permission manifests, or its agent tools.
---

# God Code

God Code is a programming language that reads like scripture. Write real software in words of faith, in your own language, and watch it run. Human-readable, safe, and built for humans and AI creating together. Created in Botswana, open to the world.

A God Code program is a **scroll** (a `.god` file). Your job: generate scrolls, validate them with the CLI, fix from machine-readable diagnostics, and run them safely.

## Install

```bash
pip install godcode-engine
```

Then confirm the CLI answers:

```bash
godcode --help
```

## The agent workflow

Follow this loop every time. Never skip `check`, never run an untrusted scroll without `--sandbox`.

1. **Generate** the scroll. Every scroll needs `BEGIN CREATION` ... `END CREATION`. Nothing outside the block runs.
2. **Check** it:
   ```bash
   godcode check --json scroll.god
   ```
   Exit 0 means pure. Exit 1 means diagnostics. Exit 2 is a usage error. Fix every diagnostic before running. Each diagnostic carries `line`, `col`, `code`, `severity`, `message`, and a `hint`.
3. **Run it safely**:
   ```bash
   godcode run --sandbox --json scroll.god
   ```
   Read `output` (every REVEALed line, plus engine notices like `[SEAL]` and `[INTENT]`), `error` (line, col, code, message on failure), `intents` (one entry per invoked rite carrying `DECLARE INTENT`), and `permissions` (the run's manifest). Under `--sandbox`, ledger writes are confined, so `seals` stays empty. That is the sandbox doing its job.
4. **Iterate** until check is clean and the run reveals what you intended.

A minimal scroll, to prove the loop:

```godcode
BEGIN CREATION
  DECLARE name AS "world"
  REVEAL("Hello, {name}. Grace upon grace.")
END CREATION
```

```bash
godcode check --json hello.god      # expect ok: true
godcode run --sandbox --json hello.god   # expect "Hello, world. Grace upon grace."
```

## Permission manifests

Generated scrolls should declare what they may touch, at the top inside `BEGIN CREATION`:

```godcode
BEGIN CREATION
  DECLARE PERMISSION TO READ "data/"
  DECLARE PERMISSION TO WRITE "out/"
  DECLARE PERMISSION TO SPEAK WITH "api.example.com"
  DECLARE PERMISSION TO ASK THE WORLD
  DECLARE PERMISSION TO SUMMON "reports.weekly"
  ...
END CREATION
```

A rite that reaches for an undeclared power is stopped. The manifest never widens the host policy. Before running a scroll you did not write, read its manifest without running anything:

```bash
godcode permissions --json scroll.god
```

## Safety

- Never run untrusted scrolls without `--sandbox`.
- The manifest is a promise, the sandbox is the wall. Keep both.
- Production moves (real credentials, real money, signed contracts) belong to the human. Demo in the sandbox.

## Language gotchas

Condensed. Full detail lives in `references/language.md`.

- Assignment is `DECLARE x AS ...`. Comparisons use `IS` / `IS NOT`. Output is `REVEAL(expr)`. There is no stdin.
- Strings breathe values in: `"grace upon {name}"` interpolates any expression. Double a brace to write one: `"{{"`.
- Keywords are case-insensitive. Canonical style is UPPER.
- Blocks close explicitly: `ENDIF`, `ENDFOR`, `ENDWHILE`, `END RITE`. `IF` takes `THEN`: `IF n IS 3 THEN`.
- `FOR` walks a list or `RANGE(1, 6)`. A rite is `DEFINE RITE name()` ... `END RITE`, invoked with `INVOKE name()`.
- `DECLARE INTENT "plain words" ON rite_name` names a rite's purpose. Drift can counsel, never fail a run.
- `SEAL(expr)` writes to the covenant ledger. `ANCHOR(expr)` returns a receipt map. `SHA256`, `HMAC`, `BASE64_ENCODE`, `BASE64_DECODE` are pure and sandbox-safe.
- `CONSULT("question")` asks the local oracle. `ASCEND` ends a run peacefully. `REPEAT(s, n)` is a word function, not a loop.
- An unbound name evaluates to a Symbol and does not raise. `BREATHE LIFE INTO` an undeclared name raises.
- Division by zero is rejected: "division by nothing is not permitted".
- Tongues: `# tongue: tn` writes keywords in Setswana, `# tongue: zu` in isiZulu, `# tongue: ig` in Igbo, `# tongue: pg` in Nigerian Pidgin. English keywords still work in the same file.

## When you need more

- `references/cli.md`: the full CLI reference with JSON shapes.
- `references/language.md`: language essentials with tiny examples.
- `references/examples.md`: three complete runnable scrolls. Steal their shape.
- `references/troubleshooting.md`: error codes and fixes.

When in doubt, run `godcode check --json` and read the hint. The engine teaches as it corrects.
