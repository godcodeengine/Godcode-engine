# 🕊️ Tongues — God Code in other languages

God Code began in English, but its heart was born in Botswana. A *tongue*
lets you write the language's keywords in another language. The first
tongue is **Setswana** (`tn`), spoken across Botswana. The second tongue
is **isiZulu** (`zu`), spoken across South Africa and beyond. The third
is **Igbo** (`ig`), spoken across south-eastern Nigeria, and the fourth is
**Nigerian Pidgin** (`pg`, or the standard code `pcm`), the shared tongue
of Nigeria and much of West Africa.

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

## The Igbo word table

Open a scroll with `# tongue: ig` and the grammar speaks Igbo:

```godcode
# tongue: ig
BIDO OKIKE
KWUSAA aha DỊKA "Ụwa"
GOSI("Ndewo, {aha}.")
NJEDEBE OKIKE
```

| English | Igbo | English | Igbo |
|---|---|---|---|
| BEGIN | BIDO | IF | MA, or Ọ BỤRỤ |
| CREATION | OKIKE | THEN | MGBE, or MGBE AHỤ |
| END | NJEDEBE | TRY | NWAA |
| DECLARE | KWUSAA | CATCH | JIDE |
| AS | DỊKA | DEFINE | KỌWAA |
| BREATHE | KUO | RITE | EMUME |
| LIFE | NDỤ | INVOKE | KPỌỌ |
| INTO | BANYE | RETURN | WEGHACHI |
| REVEAL | GOSI | IMPORT | WEBATA |
| PROPHESY | AMỤMA | IS | BỤ |
| ASCEND | RỊGOO | NOT | MBA |
| REFLECT | TỤGHARỊA | AND | NA |
| BLESS | GỌZIE | OR | MAỌBỤ |
| ANOINT | TEE | IN | IME |
| SEAL | MECHIE | DO | MEE |
| TESTIFY | AKAEBE | TRUE | EZIOKWU |
| BREAK | KWỤSỊ | FALSE | ỤGHA |
| CONTINUE | GABA | VOID | EFU |

Igbo is written with dotted vowels, but many keyboards cannot type them,
so every word also works without its marks: `DỊKA` and `DIKA`
both speak, as do `Ọ BỤRỤ` and `O BURU`. Four phrases are spoken as two
words on one line: `Ọ BỤRỤ` opens an `IF`, `MGBE AHỤ` is its `THEN`,
`NJEDEBE MA` closes the `IF` (ENDIF), and `NJEDEBE NWAA` closes a `TRY`
(ENDTRY). A worked example lives at `examples/first_blessing_ig.god`,
counting the four market days, Eke, Orie, Afọ, and Nkwọ.

## The Nigerian Pidgin word table

Open a scroll with `# tongue: pg` (or `# tongue: pcm`) and the grammar
speaks Naija:

```godcode
# tongue: pg
OYA KREASHON
TALK name BE "my padi"
SHOW("How far, {name}?")
FINISH KREASHON
```

| English | Pidgin | English | Pidgin |
|---|---|---|---|
| BEGIN | OYA | THEN | DEN |
| CREATION | KREASHON | CATCH | HOLD |
| END | FINISH | DEFINE | ARRANGE |
| DECLARE | TALK | RITE | JOB |
| AS | BE | INVOKE | CALL |
| BREATHE | BLOW | IMPORT | CARRY |
| INTO | INSIDE | IS | NA |
| REVEAL | SHOW | NOT | NO |
| ASCEND | COMOT | OR | ABI |
| REFLECT | REASON | VOID | NOTHING |
| ANOINT | ROB | BREAK | STOP |
| SEAL | LOCK | CONTINUE | MOVE |
| TESTIFY | WITNESS | | |

Pidgin shares many words with English, and those simply stay as they
are: `IF`, `TRY`, `AND`, `IN`, `DO`, `BLESS`, `LIFE`, `TRUE`, `FALSE`,
`RETURN`, and `PROPHESY`. The closers read the way Naija speaks:
`FINISH IF` closes an `IF`, `FINISH TRY` closes a `TRY`, and `FINISH JOB`
closes a rite. `IS NOT` is spoken `NA NO`. A worked example lives at
`examples/first_blessing_pg.god`.

## Honest first-edition notes

A few words stay English in these first editions: `ELSE`, `FOR`,
`WHILE`, `ENDFOR`, and `ENDWHILE` (Pidgin keeps a few more, the words it
shares with English). They will cross over as speakers bless
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

If you speak Setswana, isiZulu, Igbo, or Pidgin and a word here rings
wrong, say so: open an issue on the repo. These tables are first
editions, and native speakers are their rightful editors.

Added 2026-10-15, as first editions awaiting a native speaker's review:
the Igbo and Nigerian Pidgin tables. Igbo marks negation with a suffix
rather than a word, so `MBA` (no) stands in for `NOT` until speakers
bless a better form. Pidgin has no settled spelling; these tables follow
everyday written Naija, and `KREASHON` is the one coined spelling. A
tongue word becomes a keyword only under its own pragma, so a Pidgin
scroll cannot name a variable `show` or `job`, while an English scroll
still can.

Checked 2026-10-15, word by word, against two sources. For Igbo,
Williamson and Blench, *Dictionary of Ònìchà Igbo* (2nd edition, edited
by Roger Blench, 2006). For Pidgin, Faraclas, *Nigerian Pidgin*
(Routledge, 1996), through the example sentences quoted in APiCS Online.
Naijalingo could not be reached. The Igbo dictionary is of Onitsha Igbo,
where Standard Igbo `r` is often `l` (`-tụghalị` for `tụgharị`), and it
lists verbs by root (`-gọzi`), so the table writes the command form or
the Standard spelling. The check corrected five Igbo words, each now the
dictionary's own: `BIDO` (`-bi-do`, begin) for `MALITE`, `KWUSAA`
(`-kwusà`, proclaim; declare) for `KWUPỤTA`, `GOSI` (`-go-si`, show)
for `GOSIPỤTA`, `GỌZIE` (`-gọzi`, bless) for `GỌỌZIE`, and `GABA`
(`-gaba`, go on; continue) for `NỌGIDE`.

These words the sources do not settle. Native speakers decide them:

| Tongue | Word | Keyword | Why it is open |
|---|---|---|---|
| Igbo | `WEGHACHI` | RETURN | Not in the dictionary; Standard Igbo for "bring back" |
| Igbo | `WEBATA` | IMPORT | Built from `-wè` (take) and `-bàta` (come in), not listed whole |
| Igbo | `MAỌBỤ` | OR | Not in the dictionary, which has no word for "or" |
| Igbo | `MBA` | NOT | The dictionary's `mbà!` is "no!"; Igbo negates with a suffix |
| Igbo | `AKAEBE` | TESTIFY | The dictionary writes `aka ebē` (witness) as two words |
| Pidgin | `OYA`, `TALK`, `BLOW`, `INSIDE`, `SHOW`, `DEN`, `HOLD`, `ARRANGE`, `JOB`, `CALL`, `REASON`, `ROB`, `LOCK`, `WITNESS`, `NOTHING`, `STOP`, `MOVE` | | Not in the Faraclas sentences available; Naijalingo unreachable |
| Pidgin | `KREASHON` | CREATION | A coined spelling |

Settled 2026-10-15 in the review of this edition. Three words the
sources had left open were explained by the contributor, and the keeper
accepted them as written:

| Tongue | Word | Keyword | Settled |
|---|---|---|---|
| Igbo | `MGBE`, `MGBE AHỤ` | THEN | `mgbe` answers to time: it is both "then" and "when". The dictionary records the "when" sense |
| Igbo | `RỊGOO` | ASCEND | `rịgoo` is general Igbo. The dictionary's `-rọgo` is the Owerri form, and its `-lịgo` is the Onitsha one |
| Pidgin | `ABI` | OR | Without a question mark, `abi` is "or". With one, `abi?` is "right?", the question use Faraclas records |

Confirmed in the sources: every other Igbo word, and the Pidgin `COMOT`
(Faraclas `kò̱mót`, leave), `CARRY` (`kari`, carry), `BE` (`bì`), `NA`
(`Ìm nà ticha`, s/he is a teacher), `NO` (negation), and `FINISH`, which
Faraclas records as a completion marker (`cho̱p dì nyam finish`, eat the
yams completely).

## The editors speak the tongues too

The language server reads the pragma in the open scroll. When it sees
`# tongue: tn` it offers the tongue's keywords beside the English ones
(`SENOLA (REVEAL)`, `FEDISA FA (ENDIF)`), plus block snippets that
unfold in that tongue. `# tongue: zu` brings `VEZA (REVEAL)` and
`QEDA UMA (ENDIF)` the same way, `# tongue: ig` brings
`GOSI (REVEAL)` and `NJEDEBE MA (ENDIF)`, and `# tongue: pg` brings
`SHOW (REVEAL)` and `FINISH IF (ENDIF)`. Hovering a tongue word shows the
English keyword's own documentation, so `SENOLA` explains itself as
`REVEAL`, `VEZA` explains itself as `REVEAL`, and `SIMOLOLA TLHOLEGO` opens
the `BEGIN CREATION` notes. The VS Code extension paints Setswana and
isiZulu keywords in their colors too (always on, so mixed scrolls glow
in every tongue), and ships starter snippets for each: type `simolola` or
`fa` for Setswana blocks, `sawubona` or `uma` for isiZulu ones, `ndewo`
or `oburu` for Igbo, and `howfar` or `ifden` for Pidgin. The
named tools stay English everywhere, and `godcode fmt` still renders
the canonical English tongue.

## For tongue builders

A tongue is one table in `godcode/tongues.py`: word-to-keyword aliases
plus optional two-word phrases (either word may be an English keyword or
a plain name, as in `FINISH IF` and `Ọ BỤRỤ`). To propose a new tongue, open an issue
with the language name, its code, and a word table like the one above;
keep builtins untranslated and leave any word you are unsure of in
English. The playground, the docs, and the tests cross over with it.

Roadmap: more tongues by community proposal, and spoken-word audio for
the learn page.
