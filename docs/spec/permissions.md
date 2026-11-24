# Permission manifests — the spec

*God Code spec layer: permissions. Companion to `sandbox.md`.*

## The rule

A scroll may declare what it is allowed to touch, at the top of the
scroll:

```
DECLARE PERMISSION TO READ "data/"
DECLARE PERMISSION TO WRITE "out/"
DECLARE PERMISSION TO SPEAK WITH "api.example.com"
DECLARE PERMISSION TO ASK THE WORLD
DECLARE PERMISSION TO SUMMON "reports.weekly"
DECLARE PERMISSION TO SEAL THE COVENANT
```

The declaration is a promise and a boundary. Any rite that reaches for
a power the scroll did not declare is counselled and stopped. The
manifest never widens what the host allows: the effective grant is
always **host policy intersect manifest**. Deny by default; the host
may approve more, never less.

## The six powers

| Declaration | Grants | Policed rites |
|---|---|---|
| `READ "dir/"` | Read files under the directory (or the one file, if the path names a file) | `READ_FILE`, `LIST_DIR`, `FILE_EXISTS` |
| `WRITE "dir/"` | Write files under the directory | `WRITE_FILE` |
| `SPEAK WITH "host"` | Reach the host over the web (the host and its subdomains) | `HTTP_GET` |
| `ASK THE WORLD` | Speak with the outer world | `ASK` |
| `SUMMON "verb"` | Call upon the named plugin verb (and its namespaced children) | `SUMMON` |
| `SEAL THE COVENANT` | Write to the covenant ledger | `SEAL` |

## Static meaning

- `DECLARE PERMISSION TO` is a top-level decree. It is also gathered
  from inside top-level creation blocks. A decree anywhere else is
  ignored: manifests live at the top of the scroll.
- `PERMISSION`, `TO`, `READ`, `WRITE`, `SPEAK`, `WITH`, `ASK`, `THE`,
  `WORLD`, `SUMMON`, `COVENANT` are soft words: `DECLARE permission AS
  x` still declares an ordinary name. (`SEAL` is a keyword in its own
  right, borrowed here from the rite it names.)
- An unknown power is a parse-time counsel naming the six legal forms.

## Dynamic meaning

1. Before the run begins, the engine gathers every permission decree
   into the scroll's manifest. Relative path patterns resolve against
   the scroll's own directory.
2. A plain `godcode run` is manifest-enforced. The guard is bound for
   the run whether or not the scroll declared anything: a declared
   manifest narrows the run to its grants, and a scroll that declared
   nothing is granted nothing at all. Silence means nothing granted.
   The host policy for such a run is permissive; the manifest does the
   narrowing. (A library embedding that was not asked to enforce keeps
   the older freedom: no manifest, no guard.)
3. Every side-effecting rite is checked against the manifest before it
   runs. Path targets are resolved exactly the way the rite will open
   them (relative to the invocation directory), so the check can never
   bless a different file than the rite will touch. `SEAL` is a
   statement rather than a call, so the interpreter puts the question
   to the guard directly before the seal is weighed.
4. `ANCHOR` persists a block to a local chain file, which is a write,
   but it is never refused: where a manifest binds and grants no
   `WRITE` over the chain's own file, the anchor is kept in an
   ephemeral in-memory chain instead, the same answer the strict
   sandbox gives, so the rite keeps its meaning and persists nothing it
   did not declare. It adds no seventh power: a scroll persists its
   chain by declaring `WRITE` over the chain file, like any other write.
5. Imported scrolls may narrow the lead scroll's manifest, never
   widen it. Before an imported scroll runs, its declarations are
   measured against the lead scroll's manifest; any declaration beyond
   it refuses the import with a `SandboxViolation` naming the widening
   power. A library scroll that reads its data declares that read, and
   the lead scroll declares it too, at its own top.
6. A violation raises `SandboxViolation` with counsel naming the
   withheld power and the decree that would grant it.

## Machine interfaces

- `godcode permissions scroll.god [--json]` reads the manifest without
  running any code. Safe to call on untrusted scrolls.
- `godcode run --json` reports the run's manifest under `permissions`.
- The agent bridge offers a `permissions` tool with the same reading,
  and every `run` result carries the manifest. Bridge runs are always
  sandboxed, on the MCP server's rule: a caller's `sandbox: false` is
  overruled, and the result says so.

## Honest limits

- The manifest polices the *invocation* of powers, not what trusted
  host code does after invocation: plugin verbs are host code and run
  outside the guard. Grant `SUMMON` only to verbs you trust.
- There is no approval hook yet: a denied power fails the run rather
  than asking the human. Interactive approval is the road ahead.
- The manifest does not police `IMPORT` paths; the host sandbox policy
  does (`--sandbox` confines imports to the stdlib and the scroll's
  own directory).
