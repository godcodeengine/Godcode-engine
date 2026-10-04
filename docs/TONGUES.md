# 🕊️ Tongues — God Code in other languages

God Code began in English, but its heart was born in Botswana. A *tongue*
lets you write the language's keywords in another language. The first
tongue is **Setswana** (`tn`), spoken across Botswana. The second tongue
is **isiZulu** (`zu`), spoken across South Africa and beyond.

## How it works

Put a pragma comment in your scroll, and the grammar crosses over:

```godcode
# tongue: tn
SIMOLOLA TLHOLEGO
BOLELA leina JAAKA "Lefatshe"
SENOLA("Dumela, {leina}.")
FEDISA TLHOLEGO
```

Run it like any scroll: `godcode run dumela.god`. Every tool honours the
pragma: `check`, `lint`, `fmt`, `test`, the debugger, the language server,
the agent bridge, and the web playground.

Mixed scrolls are welcome. English keywords keep working beside tongue
words in the same file, so you can cross over one word at a time.

## The Setswana word table

| English | Setswana | English | Setswana |
|---|---|---|---|
| BEGIN | SIMOLOLA | IF | FA |
| CREATION | TLHOLEGO | THEN | TLOGA |
| END | FEDISA | TRY | LEKA |
| DECLARE | BOLELA | CATCH | TSHWARA |
| AS | JAAKA | DEFINE | TLHALOSA |
| BREATHE | HEMA | RITE | TIRO |
| LIFE | BOTSHELO | INVOKE | BITSA |
| INTO | TENG | RETURN | BUSETSA |
| REVEAL | SENOLA | IMPORT | TSENYA |
| PROPHESY | POROFETA | IS | KE |
| ASCEND | TLHATLOGA | NOT | GA |
| REFLECT | AKANYA | AND | LE |
| BLESS | SEGOFATSA | OR | KGOTSA |
| ANOINT | TLOTSA | IN | MO |
| SEAL | TSWALA | DO | DIRA |
| TESTIFY | PAKA | TRUE | NNETE |
| BREAK | KGAOLA | FALSE | MAAKA |
| CONTINUE | TSWELELA | VOID | SEPE |

Two closers are spoken as two words on one line: `FEDISA FA` closes an
`IF` (ENDIF), and `FEDISA LEKA` closes a `TRY` (ENDTRY).

## The isiZulu word table

Open a scroll with `# tongue: zu` and the same grammar speaks isiZulu:

```godcode
# tongue: zu
QALA INDALO
MEMEZELA igama NJENGA "Umhlaba"
VEZA("Sawubona, {igama}.")
QEDA INDALO
```

| English | isiZulu | English | isiZulu |
|---|---|---|---|
| BEGIN | QALA | IF | UMA |
| CREATION | INDALO | THEN | KHONA |
| END | QEDA | TRY | ZAMA |
| DECLARE | MEMEZELA | CATCH | BAMBA |
| AS | NJENGA | DEFINE | CHAZA |
| BREATHE | PHEFUMULA | RITE | ISIKO |
| LIFE | IMPILO | INVOKE | BIZA |
| INTO | PHAKATHI | RETURN | BUYISA |
| REVEAL | VEZA | IMPORT | NGENISA |
| PROPHESY | PROFETA | IS | NGU |
| ASCEND | ENYUKA | NOT | HHAYI |
| REFLECT | ZINDLA | AND | KANYE |
| BLESS | BUSISA | OR | NOMA |
| ANOINT | GCOBA | IN | KU |
| SEAL | VALA | DO | ENZA |
| TESTIFY | FAKAZA | TRUE | IQINISO |
| BREAK | PHULA | FALSE | AMANGA |
| CONTINUE | QHUBEKA | VOID | LUTHO |

Two closers are spoken as two words on one line: `QEDA UMA` closes an
`IF` (ENDIF), and `QEDA ZAMA` closes a `TRY` (ENDTRY). A worked example
lives at `examples/first_blessing_zu.god`, and the playground boots a
"Sawubona (isiZulu)" creation ready to run.

## Honest first-edition notes

A few words stay English in these first editions: `ELSE`, `FOR`,
`WHILE`, `ENDFOR`, and `ENDWHILE`. They will cross over as speakers bless
better words. The named tools (`SHA256`, `UPPER`, `RANGE`, and the rest)
keep their names in every tongue, by design: the grammar speaks your
language, the tools stay shared, and a scroll written in Setswana runs
beside one written in isiZulu or English without translation.

Corrected 2026-10-04, against Matumo's *Setswana-English-Setswana
Dictionary*: `AS` in Setswana is `JAAKA` (like, similar to). The first
edition had written `JAKA`, which the dictionary knows only as a verb
meaning "to sojourn". `THEN` is `TLOGA` (then, thereupon, as an
auxiliary verb). The first edition had written `GONE`, which is not a
Setswana word at all. And `NOT` crosses over at last as `GA`, the
dictionary's negative form. Scrolls written with `JAKA` or `GONE`
under `# tongue: tn` should cross over to `JAAKA` and `TLOGA`.

Corrected 2026-10-04, by a native speaker's eye: `BEGIN` in Setswana is
`SIMOLOLA` (to begin, to start). The first edition had borrowed `QALA`,
which is isiZulu, where it rightly remains. Scrolls written with `QALA`
under `# tongue: tn` should cross over to `SIMOLOLA`.

`godcode fmt` always renders the canonical English tongue. Inside
`{...}` interpolation, the tongue's keywords work too.

If you speak Setswana or isiZulu and a word here rings wrong, say so:
open an issue on the repo. These tables are first editions, and native
speakers are their rightful editors.

## The editors speak the tongues too

The language server reads the pragma in the open scroll. When it sees
`# tongue: tn` it offers the tongue's keywords beside the English ones
(`SENOLA (REVEAL)`, `FEDISA FA (ENDIF)`), plus block snippets that
unfold in that tongue. `# tongue: zu` brings `VEZA (REVEAL)` and
`QEDA UMA (ENDIF)` the same way. Hovering a tongue word shows the
English keyword's own documentation, so `SENOLA` explains itself as
`REVEAL`, `VEZA` explains itself as `REVEAL`, and `SIMOLOLA TLHOLEGO` opens
the `BEGIN CREATION` notes. The VS Code extension paints Setswana and
isiZulu keywords in their colors too (always on, so mixed scrolls glow
in every tongue), and ships starter snippets for both: type `simolola` or
`fa` for Setswana blocks, `sawubona` or `uma` for isiZulu ones. The
named tools stay English everywhere, and `godcode fmt` still renders
the canonical English tongue.

## For tongue builders

A tongue is one table in `godcode/tongues.py`: word-to-keyword aliases
plus optional two-word compounds. To propose a new tongue, open an issue
with the language name, its code, and a word table like the one above;
keep builtins untranslated and leave any word you are unsure of in
English. The playground, the docs, and the tests cross over with it.

Roadmap: more tongues by community proposal, and spoken-word audio for
the learn page.
