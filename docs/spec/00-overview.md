# The God Code Specification

**The layered specification of the language.** This folder holds the promise the Direction names: the spec is what lets the engine change without silently changing the language.

## Why layers

The old `docs/LANGUAGE_SPEC.md` was one long document that described the language in one breath. These layers say the same things with edges: each layer names the exact claims that hold, and each claim carries a rule number like **LX-14**. The test suite keeps every rule honest. If a rule's test fails, the engine changed or the rule is wrong, and one of them must be fixed before the release moves.

## The layers, in order

1. **Lexical** (`lexical.md`): how source text becomes tokens. What counts as a word, a number, a string, a comment, a line break. Nothing about meaning yet.
2. **Syntax** (`syntax.md`): how tokens become a scroll's shape. The grammar, the closers, the one-line forms.
3. **Static meaning** (`static-meaning.md`): what can be known before a scroll runs. Names, scopes, the linter's counsel, check-time warnings, the Symbol Rule's classic face.
4. **Dynamic meaning** (coming): what happens when a scroll runs. Values, truth, rites, errors, the ledger.
5. **Standard library** (coming): the built-in rites and scrolls, and what they promise.
6. **Interfaces** (coming): the machine faces of the language. CLI JSON shapes, exit codes, the bridge.

## How to read a rule

- **LX** rules are the lexical layer. **SX** rules are the syntax layer. **ST** rules are the static meaning layer. **DY**, **SL**, **IF** follow for the remaining layers.
- A rule states what the language guarantees. Probes in the text show it breathing.
- Every normative rule is backed by a test in `tests/test_spec_lexical.py`, named after the rule it keeps honest. The comments in that file map each test back to its rule.

## The promise underneath

A scroll that runs today must run tomorrow. When a rule needs to change, the change is named, dated, and the old behavior is kept working or is announced with a clear crossing-over path, the way `JAKA` crossed to `JAAKA` and `GONE` to `TLOGA` in the tongues. No silent changes. That is what this folder is for.
