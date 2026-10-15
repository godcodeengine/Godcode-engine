# God Code language essentials

Tiny examples throughout. Every one of them is shaped to pass `godcode check --json`.

## The shape of a program

```godcode
BEGIN CREATION
  REVEAL("In the beginning was the Word.")
END CREATION
```

Everything runs between `BEGIN CREATION` and `END CREATION`. Comments start with `#`.

## Names and assignment

```godcode
DECLARE name AS "Ruth"
DECLARE harvest AS 40 + 2
```

Comparisons use `IS` and `IS NOT`. Assignment is always `DECLARE x AS ...`.

```godcode
IF harvest IS 42 THEN
  REVEAL("the harvest is full")
ENDIF
```

## Strings that breathe

```godcode
DECLARE name AS "Ruth"
REVEAL("grace upon {name}")          # grace upon Ruth
REVEAL("twice the harvest: {harvest * 2}")
REVEAL("a plain brace looks like {{this}}")
```

Any expression breathes inside `{...}`. Double a brace to write one literally.

## Decisions

```godcode
IF heart IS pure THEN
  REVEAL("heaven")
ELSE
  REVEAL("mercy")
ENDIF
```

`ELSE` may be omitted. Single-line form: `IF n IS 3 THEN REVEAL("three")`.

## Cycles

```godcode
FOR n IN RANGE(1, 4)
  REVEAL("count {n}")
ENDFOR

FOR tribe IN ["Judah", "Reuben", "Gad"]
  REVEAL("bless {tribe}")
ENDFOR

WHILE river IS flowing
  REVEAL("it flows")
ENDWHILE
```

`FOR` walks a list, a string's characters, or `RANGE(start, stop)`. `BREAK` and `CONTINUE` work inside.

## Rites and intent

```godcode
DECLARE INTENT "bring peace to the household" ON evening_blessing

DEFINE RITE evening_blessing()
  REVEAL("peace upon this house")
END RITE

INVOKE evening_blessing()
```

`DECLARE INTENT` names a rite's purpose in plain words. When invoked, the Spirit discerns the rite's actual intent and compares. Aligned gets a blessing notice, drift gets gentle counsel. Drift can never fail a run.

## Seals and anchors

```godcode
SEAL("the covenant is sealed")          # tamper-evident covenant block
DECLARE receipt AS ANCHOR("the covenant is sealed")
REVEAL(receipt["anchor_hash"])          # the chain's fingerprint
```

`ANCHOR` returns a receipt map: `chain`, `anchor_hash`, `height`, `timestamp`, `payload_hash`.

## Pure works (no import, sandbox-safe)

```godcode
REVEAL(SHA256("manna"))                 # 64 hex characters
REVEAL(HMAC("key", "message"))          # sealed under a key
REVEAL(BASE64_ENCODE("hidden"))         # veiled
REVEAL(BASE64_DECODE("aGlkZGVu"))       # unveiled
REVEAL(REPEAT("Pula! ", 3))             # "Pula! Pula! Pula! "
REVEAL(SUM_OF([1, 2, 3, 4]))            # 10
REVEAL(SORT([3, 1, 2]))                 # [1, 2, 3] (a new list)
```

Words: `TRIM`, `REPLACE`, `STARTS_WITH`, `ENDS_WITH`, `SUBSTRING`, `CONTAINS`, `COUNT`, `REPEAT`. Lists: `SORT`, `MIN_OF`, `MAX_OF`, `SUM_OF`, `FIRST`, `LAST`, `UNIQUE`, `INDEX_OF`. Maps: `KEYS`, `VALUES`, `HAS_KEY`, `MERGE`. Numbers: `ABS`, `ROUND`, `FLOOR`, `CEIL`, `SQRT`, `POW`.

## The oracle

```godcode
DECLARE word AS CONSULT("what is the first step of faith?")
REVEAL(word)
```

`CONSULT` asks the local Spirit oracle. It answers in a few sentences, works in the sandbox, and never fails a run.

## Ending in peace

```godcode
ASCEND   # ends the run peacefully; not an error
```

## Gotchas that bite generators

- An unbound name evaluates to a Symbol. It does not raise. `BREATHE LIFE INTO` an undeclared name *does* raise.
- Division by zero is rejected: "division by nothing is not permitted".
- Keywords are case-insensitive. Canonical style is UPPER.
- `REPEAT(s, n)` is a word function, not a loop.
- Every block needs its closer: `ENDIF`, `ENDFOR`, `ENDWHILE`, `END RITE`.
- Error messages may end with `Did you mean 'X'?`. Trust it.

## Tongues

A scroll can speak Setswana, isiZulu, Igbo, or Nigerian Pidgin with one pragma line. English keywords still work in the same file.

```godcode
# tongue: tn
BEGIN CREATION
  SENOLA("Dumela, lefatshe")   # SENOLA is REVEAL in Setswana
END CREATION
```

```godcode
# tongue: zu
BEGIN CREATION
  VEZA("Sawubona, mhlaba")     # VEZA is REVEAL in isiZulu
END CREATION
```

`# tongue: tn` gives `SIMOLOLA`/`BEGIN`, `SENOLA`/`REVEAL`, `FA`/`IF`, and more. `# tongue: zu` gives `QALA`/`BEGIN`, `VEZA`/`REVEAL`, `UMA`/`IF`, and more. `# tongue: ig` gives `BIDO`/`BEGIN`, `GOSI` (or `GOSI`)/`REVEAL`, `Ọ BỤRỤ`/`IF`, and `# tongue: pg` gives `OYA`/`BEGIN`, `SHOW`/`REVEAL`, `FINISH IF`/`ENDIF`. Named tools like `SHA256` never translate.

## Permission manifests

At the top inside `BEGIN CREATION`, declare what the scroll may touch:

```godcode
BEGIN CREATION
  DECLARE PERMISSION TO READ "data/"
  DECLARE PERMISSION TO WRITE "out/"
  DECLARE PERMISSION TO SPEAK WITH "api.example.com"
  DECLARE PERMISSION TO ASK THE WORLD
  DECLARE PERMISSION TO SUMMON "reports.weekly"
END CREATION
```

Anything reaching for an undeclared power is stopped. The manifest never widens the host policy.
