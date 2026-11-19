# The Static Meaning Layer

**What God Code knows before a scroll runs.** This is the third layer of the specification: it says how names are bound, how scopes nest, what the linter counsels, and how the engine answers mistakes gently. It says nothing about what values are, what truth means, or what rites do when called. That is the next layer's work. Every rule below is kept honest by a test in `tests/test_spec_static_semantics.py` that carries the rule's number.

The probes show source the way an author writes it. `BEGIN CREATION` and `END CREATION` wrap the examples, the way every shared program is wrapped.

---

## The scope model

**ST-1.** The creation block shares the scroll's top-level scope. A `DECLARE` inside `BEGIN CREATION` is visible to everything after it in the scroll, and there is no barrier at the block's walls.

```
BEGIN CREATION
DECLARE gift AS 42
REVEAL(gift)
END CREATION
```

reveals `42`.

**ST-2.** `IF` and `WHILE` bodies run in the current scope. A name declared inside the body is visible after the block ends, in the scope that held the `IF` or `WHILE`.

```
BEGIN CREATION
IF 1 IS 1 THEN
DECLARE gift AS 42
ENDIF
REVEAL(gift)
END CREATION
```

reveals `42`. A `DECLARE` inside a `WHILE` body behaves the same way.

**ST-3.** `FOR` runs its body in one child scope, and the loop variable lives only there. After `ENDFOR` the loop variable is unbound again, and names declared in the body stay inside the loop.

```
BEGIN CREATION
FOR i IN RANGE(1, 4)
REVEAL(i)
ENDFOR
REVEAL(i)
END CREATION
```

reveals `1`, `2`, `3`, and then the last read stops the run: after the loop the name is bound nowhere, and a name bound nowhere is never read silently (see ST-14).

**ST-4.** `DEFINE RITE` binds the rite's name in the enclosing scope and gives the body one child scope holding the parameters. A `DECLARE` inside the body is not visible after the call returns.

```
BEGIN CREATION
DEFINE RITE f()
DECLARE hidden AS 1
END RITE
f()
REVEAL(hidden)
END CREATION
```

and the last read stops the run: `hidden` lived only inside the rite, and a name bound nowhere is never read silently (see ST-14).

**ST-5.** A rite's body is a closure over its definition scope, captured by reference, not by snapshot. If the enclosing scope re-binds a name after the rite is defined, the rite sees the new value when it runs.

```
BEGIN CREATION
DECLARE x AS 10
DEFINE RITE see()
RETURN x
END RITE
DECLARE x AS 99
REVEAL(see())
END CREATION
```

reveals `99`.

**ST-6.** The rite's name is bound in the enclosing scope before its body ever runs, so a rite may call itself. Recursion is well-formed static meaning. How deep it may go is a runtime matter, not this layer's.

## Names

**ST-7.** Names are case-sensitive. `DECLARE MyName AS 5` does not bind `myname`: `REVEAL(myname)` never reveals `5`, because the mismatched read is loud (see ST-14), and the linter flags the mismatch as an undefined name (GC002, see ST-21).

**ST-8.** Tongue words are mapped to their canonical keywords before static meaning applies. A Setswana `SENOLA` is `REVEAL` for every rule below, and `godcode fmt` renders the canonical English. Names the author invents keep the exact spelling they were given, in every tongue.

**ST-9.** Variables, rites, parameters, and loop variables share one namespace. A `DECLARE` of a name already held by a rite re-binds it in that scope: the old binding is replaced, and calling the name afterwards is answered with "'f' is number, not a rite. It cannot be invoked."

## Declaration and rebinding

**ST-10.** `DECLARE` binds in the current scope, shadowing any outer binding. The outer name is untouched: shadowing inside a rite body changes nothing for the caller.

```
BEGIN CREATION
DECLARE x AS 1
DEFINE RITE f()
DECLARE x AS 2
RETURN x
END RITE
REVEAL(f())
REVEAL(x)
END CREATION
```

reveals `2`, then `1`.

**ST-11.** The value is breathed before the name is bound. In `DECLARE x AS x + 1`, the `x` on the right reads whatever the name already held: the old value. If the name was bound nowhere, the read is loud and the declaration never lands (see ST-14).

**ST-12.** The update idiom is the language's way to change a variable. `DECLARE count AS count + 1` re-binds `count` in its scope, and the linter never flags it as a re-declaration: changing a variable this way is idiomatic, not mistaken.

**ST-13.** Declaring the same name twice in the same scope, outside the update idiom, is counselled as GC006 ("declared more than once in the same scope") but still runs: the last binding wins, because declaring overwrites.

## Reading names: loud by law, symbols by the mark

**ST-14.** A name that is bound nowhere is never read silently. Reading one stops the run with a gentle error that names the name and offers the two honest fixes: "There is no 'grace' in this creation. It was never spoken into being. DECLARE it first, or, if the bare word itself is meant, mark it as one: :grace". When a declared name stands near the reading, the error adds its counsel: "Did you mean 'worthy'?" A bare word is still a value when it is spoken on purpose: `:grace` is a Symbol literal, the word itself, written with its mark. The mark is punctuation, not a keyword, so it speaks the same in every tongue.

**ST-15.** Use before declare is loud at the read. A name read before its `DECLARE` stops the run at that read (ST-14); the declaration below it is never reached.

```
BEGIN CREATION
REVEAL(grace)
DECLARE grace AS 7
REVEAL(grace)
END CREATION
```

stops at the first `REVEAL`: when it is read, `grace` is bound nowhere.

**ST-16.** Symbols are always truthy. `IF :grace THEN REVEAL("yes") ENDIF` reveals `yes`.

**ST-17.** A Symbol behaves like a word everywhere a word does, but the engine can still tell the two apart: `FOR` refuses to walk a mere Symbol, answering "FOR needs a list or a word to walk through, not the bare spirit 'grace'." A Symbol reaches a `FOR` only by the mark or by declaration, and `FOR x IN :grace` is refused the same way.

## Calling rites

**ST-18.** A rite's arity is checked when it is called, not when it is defined. Calling with the wrong number of offerings is a runtime error that names the rite and counts both numbers: "Rite 'add' asks for 2 offerings, but 1 was brought."

**ST-19.** Calling a name that is bound nowhere is answered at run time with "There is no rite named 'x'. The heavens do not know it.", naming the line, with did-you-mean counsel toward the nearest known name when one is near enough.

## The linter's counsel

**ST-20.** `godcode check` answers one question: does the scroll parse. It runs no static counsel. The counsel lives in `godcode lint`, which reports findings as numbered rules GC001 through GC006. The findings never change what a scroll does when it runs: they advise, they do not forbid.

**ST-21.** GC002, the undefined name: a name read but never declared, defined, imported, or provided by a builtin is flagged ("undefined name 'y'"). The counsel walks beside a runtime law: when the scroll runs, the read itself stops the run (ST-14). The linter speaks first and gently; the engine speaks at the read and firmly. Builtin names never raise it. Names harvested from a resolvable `IMPORT` never raise it. If any import cannot be resolved, the linter withholds all undefined-name counsel rather than guessing.

**ST-22.** GC001, the unused variable: a `DECLARE`d name or `FOR` loop variable that is never referenced is flagged ("unused variable 'x'"). A reference inside a nested rite body counts as used, because closures capture (ST-5). A loop variable read in its own body counts as used.

**ST-23.** GC003, shadowing: declaring a name already visible from an outer scope is flagged at the inner declaration ("shadows a name already visible from an outer scope").

**ST-24.** GC004, the empty block: an `IF`, `ELSE`, `FOR`, `WHILE`, `TRY`, `CATCH`, or rite body with no statements is flagged ("empty IF body", "empty rite body for 'f'", and their kin).

**ST-25.** GC005, unreachable code: any statement after `RETURN`, `BREAK`, or `CONTINUE` in the same block is flagged ("unreachable code after RETURN").

**ST-26.** GC006, re-declare: the same name declared twice in one scope is flagged ("declared more than once in the same scope"), except for the update idiom (ST-12), which is never flagged.

**ST-27.** The `CATCH` error name is an implicit binding the engine provides. The linter marks it used from the start, so a `CATCH` that never reads the error is never flagged as an unused variable.

## Imports and the always-names

**ST-28.** `IMPORT` brings an imported scroll's top-level declared names and rites into the importer's own scope, because the interpreter runs imports in the importer's own environment. The linter harvests those names the same way, so calling an imported rite raises no undefined-name counsel.

**ST-29.** The name `contract` is always available: the interpreter answers it before builtin lookup, so the linter never flags it, and `DECLARE c AS contract("vow")` needs no import.

## Gentle errors at check and run time

**ST-30.** The engine answers mistakes with counsel that suggests the nearest known name. Unknown rite names, `BLESS` / `ANOINT` / `BREATHE LIFE INTO` / `RESHAPE` targets, and missing map keys all carry a "Did you mean ...?" suggestion when one is near enough: reading `r["chainn"]` from an anchor receipt is answered with "The map holds no 'chainn'. Its keys are: chain, anchor_hash, height, timestamp, payload_hash. Did you mean 'chain'?"

**ST-31.** `godcode run`, `godcode check`, `godcode fmt`, and the JSON diagnostics print the offending source line beneath the message, with a caret marking the column when one is known, so the author sees where to look.

## The static promise

**ST-32.** Little in this layer stops a scroll from running, and what stops it is named plainly. Parse errors stop it before it starts. Runtime errors stop it where they rise, and reading a name bound nowhere is one of them (ST-14): the Symbol Rule's old silent face is gone, and a bare word lives only where its mark is written. The linter's counsel and the gentle suggestions only ever advise. That honesty, counsel early and firmness at the read, is the promise this whole folder exists to keep.
