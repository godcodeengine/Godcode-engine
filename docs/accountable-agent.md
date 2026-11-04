# The accountable agent

The first flagship demo: an agent given exactly one folder, and
nothing else. It is the wedge in miniature. The agent states its
intent, receives narrow permission, runs safely, and leaves a report
anyone can re-run and check.

## What it does

`examples/accountable_agent.god` reads every file in
`examples/accountable_agent_data`, fingerprints each file with
`SHA256`, and reveals one line per file, the file count, the total
characters, and a fingerprint of the whole report. Run it twice and
every revealed line matches, because the scroll reads no clock, no
network, and no changing value.

## The two locks

Accountability here is two locks that must both open, not one:

1. **The scroll's permission manifest.** The scroll declares a single
   power at the top:
   `DECLARE PERMISSION TO READ "accountable_agent_data"`. The path is
   relative to the scroll, so it means the folder beside the scroll.
   Anything the scroll did not declare is refused, even on a plain
   run where the host is open.
2. **The host grant.** A sandboxed run denies every file read until
   the invoker grants one. `--allow-read` names the folder the host
   allows, and it may be repeated for more than one folder. The
   scroll cannot widen its own cage: the effective read set is the
   host grant intersected with the manifest.

Read what a scroll may touch before running it. It runs nothing:

```bash
godcode permissions examples/accountable_agent.god
```

Run the demo from the repo root, sandboxed, with exactly the one
grant:

```bash
godcode run --sandbox --allow-read examples/accountable_agent_data examples/accountable_agent.god
```

## The three checks

Each check is kept honest by a test in
`tests/test_accountable_agent.py`:

- **With the grant, it runs.** The revealed report fingerprint is
  recomputed from the files in the test, not copied from a past run.
- **Without the grant, it is refused.** The same sandboxed run with
  no `--allow-read` exits nonzero and says the power is withheld.
- **Reaching past the folder is refused.** A scroll that keeps the
  same manifest but points at another folder is stopped, under the
  sandbox by the host grant and on a plain run by the manifest.

`--allow-read` without `--sandbox` is a usage error: a plain run is
unbound by the host, so a host grant there would mean nothing, and
the manifest is already doing the narrowing.

## The Spirit's counsel

The demo declares its intent on the `survey` rite. At invocation the
Spirit discerns the intent from what the rite does ("Controlled data
access") and counsels when it drifts from the declared words. That
counsel is printed, and it never fails the run: drift is advice, not
a verdict. The `--json` report carries the discernment in its
`intents` array, beside the `permissions` block, so an agent host can
read both without parsing prose.

## What this does not prove

- The sandbox is in-process, not operating-system isolation. It is a
  cooperative audit of the tree-walking interpreter. A hostile
  program that escapes the interpreter is not contained by it. See
  `docs/sandbox.md` for the honest limits.
- The host grant is the invoker's own act. Granting a folder the
  scroll should not see is the invoker's mistake, and no manifest
  can repair it, because the manifest can only narrow, never widen.
- The report fingerprint proves the report matches the files as read
  at run time. It does not prove the files themselves are true.
- The demo writes nothing and seals nothing, so its proof is the
  re-run: same folder, same lines. A sealed replayable receipt is
  the next step, and this scroll is built ready for it, with no
  changing values in its output.

## What comes next

The other two flagship demos follow the same shape: the covenant
contract (a savings circle expressed as rites with declared intent,
sealed on the ledger) and the first-program path (ten minutes in the
playground, from first line to shared link).
