# 🕊️ Tongues — God Code in other languages

God Code began in English, but its heart was born in Botswana. A *tongue*
lets you write the language's keywords in another language. The first
tongue is **Setswana** (`tn`), spoken across Botswana.

## How it works

Put a pragma comment in your scroll, and the grammar crosses over:

```godcode
# tongue: tn
QALA TLHOLEGO
BOLELA leina JAKA "Lefatshe"
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
| BEGIN | QALA | IF | FA |
| CREATION | TLHOLEGO | THEN | GONE |
| END | FEDISA | TRY | LEKA |
| DECLARE | BOLELA | CATCH | TSHWARA |
| AS | JAKA | DEFINE | TLHALOSA |
| BREATHE | HEMA | RITE | TIRO |
| LIFE | BOTSHELO | INVOKE | BITSA |
| INTO | TENG | RETURN | BUSETSA |
| REVEAL | SENOLA | IMPORT | TSENYA |
| PROPHESY | POROFETA | IS | KE |
| ASCEND | TLHATLOGA | AND | LE |
| REFLECT | AKANYA | OR | KGOTSA |
| BLESS | SEGOFATSA | IN | MO |
| ANOINT | TLOTSA | DO | DIRA |
| SEAL | TSWALA | TRUE | NNETE |
| TESTIFY | PAKA | FALSE | MAAKA |
| BREAK | KGAOLA | VOID | SEPE |
| CONTINUE | TSWELELA | | |

Two closers are spoken as two words on one line: `FEDISA FA` closes an
`IF` (ENDIF), and `FEDISA LEKA` closes a `TRY` (ENDTRY).

## Honest first-edition notes

A few words stay English in this first edition: `ELSE`, `NOT`, `FOR`,
`WHILE`, `ENDFOR`, and `ENDWHILE`. They will cross over as speakers bless
better words. The named tools (`SHA256`, `UPPER`, `RANGE`, and the rest)
keep their names in every tongue, by design: the grammar speaks your
language, the tools stay shared, and a scroll written in Setswana runs
beside one written in English without translation.

`godcode fmt` always renders the canonical English tongue. Inside
`{...}` interpolation, the tongue's keywords work too.

If you speak Setswana and a word here rings wrong, say so: open an issue
on the repo. This table is a first edition, and native speakers are its
rightful editors.

## The editors speak Setswana

The language server reads the pragma in the open scroll. When it sees
`# tongue: tn`, completions offer the tongue's keywords beside the
English ones (`SENOLA (REVEAL)`, `FEDISA FA (ENDIF)`), plus block
snippets that unfold in Setswana. Hovering a tongue word shows the
English keyword's own documentation, so `SENOLA` explains itself as
`REVEAL`, and `QALA TLHOLEGO` opens the `BEGIN CREATION` notes. The
VS Code extension paints Setswana keywords in their colors too (always
on, so mixed scrolls glow in both tongues), and ships two starter
snippets: type `qala` for a Setswana creation block, `fa` for a
Setswana conditional. The named tools stay English everywhere, and
`godcode fmt` still renders the canonical English tongue.

## For tongue builders

A tongue is one table in `godcode/tongues.py`: word-to-keyword aliases
plus optional two-word compounds. To propose a new tongue, open an issue
with the language name, its code, and a word table like the one above;
keep builtins untranslated and leave any word you are unsure of in
English. The playground, the docs, and the tests cross over with it.

Roadmap: more tongues by community proposal, and spoken-word audio for
the learn page.
