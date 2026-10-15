"""Tongues: the grammar of God Code in other languages.

A *tongue* lets the keywords of God Code be written in another language.
English is the canonical tongue; every other tongue maps its words onto the
same tokens, so the parser, the interpreter, the linter, and all the tools
work unchanged. A scroll chooses its tongue with a pragma comment on one of
its early lines::

    # tongue: tn

``tn`` is Setswana, the first tongue, spoken in Botswana. ``zu`` is
isiZulu, the second tongue, spoken across South Africa and beyond. Mixed
scrolls are welcome: English keywords keep working beside tongue words in
the same file, so a learner can cross over one word at a time.

Design notes, kept honest:

- Only keywords are translated. The named tools (``SHA256``, ``UPPER``,
  ``RANGE`` ...) keep their names in every tongue, so scrolls stay
  interoperable and the standard library is learned once.
- ``godcode fmt`` always renders the canonical English tongue.
- These first editions leave a few words in English (``ELSE``, ``FOR``,
  ``WHILE``, ``ENDFOR``, ``ENDWHILE``); they are documented in
  ``docs/TONGUES.md`` and will cross over as speakers bless better words.
- The Setswana words were audited 2026-10-04 against Matumo's
  *Setswana-English-Setswana Dictionary* (Botswana Book Centre, 1993):
  ``JAAKA`` (like, similar to) is the true word for ``AS`` (the headword
  ``jaka`` is a verb, "to sojourn"), and ``TLOGA`` (then, thereupon) is
  the true word for ``THEN`` (``gone`` is not a Setswana word at all).
  ``GA`` (not) is blessed for ``NOT``.
"""

from __future__ import annotations

import re

# A tongue pragma looks like:  # tongue: tn
_PRAGMA = re.compile(
    r"^[ \t]*#[ \t]*tongue[ \t]*:[ \t]*([A-Za-z]{2,8})[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

# Setswana (tn) word -> canonical English keyword name.
_TN_ALIASES = {
    "SIMOLOLA": "BEGIN",    # begin, start
    "TLHOLEGO": "CREATION",  # creation
    "FEDISA": "END",        # end
    "BOLELA": "DECLARE",    # say, announce
    "JAAKA": "AS",          # like, similar to (Matumo: jaaka)
    "HEMA": "BREATHE",      # breathe
    "BOTSHELO": "LIFE",     # life
    "TENG": "INTO",         # inside (MO is taken by IN)
    "SENOLA": "REVEAL",     # reveal
    "POROFETA": "PROPHESY",  # prophesy
    "TLHATLOGA": "ASCEND",  # go up
    "FA": "IF",             # if
    "TLOGA": "THEN",        # then, thereupon (Matumo: tloga, auxiliary)
    "GA": "NOT",            # not (Matumo: ga, negative form)
    "LEKA": "TRY",          # try
    "TSHWARA": "CATCH",     # catch
    "TLHALOSA": "DEFINE",   # define, explain
    "TIRO": "RITE",         # work
    "BITSA": "INVOKE",      # call
    "BUSETSA": "RETURN",    # return (something)
    "TSENYA": "IMPORT",     # bring in
    "KE": "IS",             # is
    "LE": "AND",            # and
    "KGOTSA": "OR",         # or
    "MO": "IN",             # in
    "DIRA": "DO",           # do
    "AKANYA": "REFLECT",    # think, reflect
    "SEGOFATSA": "BLESS",   # bless
    "TLOTSA": "ANOINT",     # anoint
    "TSWALA": "SEAL",       # close (a seal closes the covenant)
    "PAKA": "TESTIFY",      # testify
    "NNETE": "TRUE",        # truth
    "MAAKA": "FALSE",       # lies
    "SEPE": "VOID",         # nothing
    "KGAOLA": "BREAK",      # break, cut
    "TSWELELA": "CONTINUE",  # continue
}

# Two-word closers, e.g. "FEDISA FA" -> ENDIF. Kept in the lexer so the
# parser never changes; only recognised on a single line.
_TN_COMPOUNDS = {
    ("FEDISA", "FA"): "ENDIF",
    ("FEDISA", "LEKA"): "ENDTRY",
}

# Editor block snippets for Setswana, offered by the language server when
# a scroll speaks the tongue: (label, insert text, plain description).
_TN_SNIPPETS = (
    ("SIMOLOLA TLHOLEGO … FEDISA TLHOLEGO",
     "SIMOLOLA TLHOLEGO\\n\\t$0\\nFEDISA TLHOLEGO",
     "Open a new scroll"),
    ("FA … GONE … FEDISA FA",
     "FA ${1:condition} GONE\\n\\t$0\\nFEDISA FA",
     "Weigh a condition"),
    ("LEKA … TSHWARA … FEDISA LEKA",
     "LEKA\\n\\t${1:works}\\nTSHWARA\\n\\t${2:refuge}$0\\nFEDISA LEKA",
     "Shelter a fragile work"),
)

# isiZulu (zu) word -> canonical English keyword name.
_ZU_ALIASES = {
    "QALA": "BEGIN",          # begin
    "INDALO": "CREATION",     # creation
    "QEDA": "END",            # finish, complete
    "MEMEZELA": "DECLARE",    # announce, proclaim
    "NJENGA": "AS",           # as, like
    "PHEFUMULA": "BREATHE",   # breathe
    "IMPILO": "LIFE",         # life
    "PHAKATHI": "INTO",       # inside, into
    "VEZA": "REVEAL",         # show, reveal
    "PROFETA": "PROPHESY",    # prophesy
    "ENYUKA": "ASCEND",       # go up
    "UMA": "IF",              # if, when
    "KHONA": "THEN",          # then, at that point
    "ZAMA": "TRY",            # try, attempt
    "BAMBA": "CATCH",         # catch, hold
    "CHAZA": "DEFINE",        # explain, define
    "ISIKO": "RITE",          # a rite, a custom
    "BIZA": "INVOKE",         # call
    "BUYISA": "RETURN",       # return, give back
    "NGENISA": "IMPORT",      # bring in
    "NGU": "IS",              # is
    "HHAYI": "NOT",          # no, not (first edition; native speakers decide)
    "KANYE": "AND",           # and, together
    "NOMA": "OR",             # or
    "KU": "IN",               # in, at
    "ENZA": "DO",             # do, make
    "ZINDLA": "REFLECT",      # meditate, reflect
    "BUSISA": "BLESS",        # bless
    "GCOBA": "ANOINT",        # anoint with oil
    "VALA": "SEAL",           # close (a seal closes the covenant)
    "FAKAZA": "TESTIFY",      # testify, bear witness
    "IQINISO": "TRUE",        # the truth
    "AMANGA": "FALSE",        # lies
    "LUTHO": "VOID",          # nothing
    "PHULA": "BREAK",         # break
    "QHUBEKA": "CONTINUE",    # continue
}

# Two-word closers, e.g. "QEDA UMA" -> ENDIF.
_ZU_COMPOUNDS = {
    ("QEDA", "UMA"): "ENDIF",
    ("QEDA", "ZAMA"): "ENDTRY",
}

# Editor block snippets for isiZulu.
_ZU_SNIPPETS = (
    ("QALA INDALO … QEDA INDALO",
     "QALA INDALO\\n\\t$0\\nQEDA INDALO",
     "Open a new scroll"),
    ("UMA … KHONA … QEDA UMA",
     "UMA ${1:condition} KHONA\\n\\t$0\\nQEDA UMA",
     "Weigh a condition"),
    ("ZAMA … BAMBA … QEDA ZAMA",
     "ZAMA\\n\\t${1:works}\\nBAMBA\\n\\t${2:refuge}$0\\nQEDA ZAMA",
     "Shelter a fragile work"),
)

def _with_plain_spellings(table: dict) -> dict:
    """Add each word's spelling without tone and dot marks (Ọ -> O, Ụ -> U).

    Igbo is written with dotted vowels, but many keyboards cannot type
    them, so ``DỊKA`` and ``DIKA`` both speak. Keys may be single
    words or two-word pairs.
    """
    import unicodedata

    def plain(word: str) -> str:
        decomposed = unicodedata.normalize("NFD", word)
        return "".join(ch for ch in decomposed if not unicodedata.combining(ch))

    out = dict(table)
    for key, canon in table.items():
        bare = tuple(plain(w) for w in key) if isinstance(key, tuple) else plain(key)
        out.setdefault(bare, canon)
    return out


# Igbo (ig) word -> canonical English keyword name. Checked 2026-10-15
# against Williamson & Blench, *Dictionary of Ònìchà Igbo* (2nd edn, 2006),
# "WB" below. WB is Onitsha Igbo, where Standard Igbo r is often l, and it
# lists verbs by root (-gọzi); the words here are the command forms, or
# the Standard spelling where Onitsha differs. A "?" marks a word WB does
# not settle; docs/TONGUES.md lists them for native speakers to decide.
# Native speakers are this table's rightful editors.
_IG_ALIASES = _with_plain_spellings({
    "BIDO": "BEGIN",          # WB -bi-do 'begin'
    "OKIKE": "CREATION",      # WB Òkìke 'Creator', òkìkè 'process of creation'
    "NJEDEBE": "END",         # WB njedebe 'end; finish; terminus'
    "KWUSAA": "DECLARE",      # WB -kwusà(sị) 'proclaim; declare'
    "DỊKA": "AS",             # WB, in use: dịkà 'like' (Na-àgafè dịkà ...)
    "KUO": "BREATHE",         # WB -kù 'blow; breathe' (-kù ume 'breathe')
    "NDỤ": "LIFE",            # WB ndụ 'life'
    "BANYE": "INTO",          # WB -bànye 'enter; go in'
    "GOSI": "REVEAL",         # WB -go-si 'show'
    "AMỤMA": "PROPHESY",      # WB amụma 'prophecy' (a noun)
    "RỊGOO": "ASCEND",        # general Igbo; WB -lịgo (Onitsha), -rọgo (Owerri)
    "MA": "IF",               # WB mà 'but; if; whether'
    "MGBE": "THEN",           # mgbe answers to time: 'then' and 'when' (WB m̀gbè 'when')
    "NWAA": "TRY",            # WB -nwà 'attempt; try' (nwà kene! 'just try!')
    "JIDE": "CATCH",          # WB -jide 'hold' (Jìde ... 'take, hold')
    "KỌWAA": "DEFINE",        # WB -kọwa 'explain; introduce'
    "EMUME": "RITE",          # WB emume 'custom; observance'
    "KPỌỌ": "INVOKE",         # WB -kpọ 'call' (-kpọ afà 'call by name')
    "WEGHACHI": "RETURN",     # ? not in WB; Standard Igbo 'bring back'
    "WEBATA": "IMPORT",       # ? WB -wè 'take' + -bàta 'come in'
    "BỤ": "IS",               # WB -bụ 'be'
    "MBA": "NOT",             # ? WB mbà! 'no!' (Igbo negates with a suffix)
    "NA": "AND",              # WB nà 'and'
    "MAỌBỤ": "OR",            # ? not in WB; Standard Igbo ma ọ bụ 'or'
    "IME": "IN",              # WB imē 'inside; interior'
    "MEE": "DO",              # WB Mèe yā ... 'Do it ...'
    "TỤGHARỊA": "REFLECT",    # WB -tụghalị uchè 'reflect' (Onitsha l)
    "GỌZIE": "BLESS",         # WB -gọzi 'bless; invoke a blessing'
    "TEE": "ANOINT",          # WB -te 'anoint'; -te mmanụ 'anoint with oil'
    "MECHIE": "SEAL",         # WB -mechi 'shut, close'
    "AKAEBE": "TESTIFY",      # ? WB aka ebē 'witness' (written as two words)
    "EZIOKWU": "TRUE",        # WB ezi okwū 'truth' (Standard: eziokwu)
    "ỤGHA": "FALSE",          # WB àma ụghā 'false witness'
    "EFU": "VOID",            # WB efù 'emptiness'
    "KWỤSỊ": "BREAK",         # WB -kwụsị 'stop'
    "GABA": "CONTINUE",       # WB -gaba 'go on; continue to go'
})

# Two-word phrases: closers, plus the natural Igbo "Ọ bụrụ" (if; WB has
# the Onitsha form "Ọ bụlụ nà ...") and "mgbe ahụ" (then; Onitsha says
# "afù" for "that").
_IG_COMPOUNDS = _with_plain_spellings({
    ("NJEDEBE", "MA"): "ENDIF",
    ("NJEDEBE", "NWAA"): "ENDTRY",
    ("Ọ", "BỤRỤ"): "IF",
    ("MGBE", "AHỤ"): "THEN",
})

_IG_SNIPPETS = (
    ("BIDO OKIKE … NJEDEBE OKIKE",
     "BIDO OKIKE\\n\\t$0\\nNJEDEBE OKIKE",
     "Open a new scroll"),
    ("Ọ BỤRỤ … MGBE AHỤ … NJEDEBE MA",
     "Ọ BỤRỤ ${1:condition} MGBE AHỤ\\n\\t$0\\nNJEDEBE MA",
     "Weigh a condition"),
    ("NWAA … JIDE … NJEDEBE NWAA",
     "NWAA\\n\\t${1:works}\\nJIDE\\n\\t${2:refuge}$0\\nNJEDEBE NWAA",
     "Shelter a fragile work"),
)

# Nigerian Pidgin (pg) word -> canonical English keyword name. Pidgin
# shares many words with English (IF, TRY, AND, IN, DO, BLESS, LIFE,
# TRUE, FALSE, RETURN, PROPHESY), so those simply stay as they are.
# Checked 2026-10-15 against Faraclas, *Nigerian Pidgin* (1996), through
# the example sentences quoted in APiCS Online ("F" below); Naijalingo
# could not be reached. Faraclas writes Pidgin phonetically (kò̱mót for
# comot); the spellings here are everyday written Naija. A "?" marks a
# word these sources do not settle; see docs/TONGUES.md.
_PG_ALIASES = {
    "OYA": "BEGIN",           # ? come on, let's go
    "KREASHON": "CREATION",   # ? a coined spelling of "creation"
    "FINISH": "END",          # F finish, a completion marker ('completely')
    "TALK": "DECLARE",        # ? say it
    "BE": "AS",               # F bì 'be' (copula)
    "BLOW": "BREATHE",        # ? blow (breath)
    "INSIDE": "INTO",         # ? inside
    "SHOW": "REVEAL",         # ? show
    "COMOT": "ASCEND",        # F kò̱mót 'leave'
    "DEN": "THEN",            # ? then
    "HOLD": "CATCH",          # ? hold am
    "ARRANGE": "DEFINE",      # ? arrange, set up
    "JOB": "RITE",            # ? a job of work
    "CALL": "INVOKE",         # ? call
    "CARRY": "IMPORT",        # F kari 'carry, take away'; carry come: bring
    "NA": "IS",               # F nà (Ìm nà ticha 's/he is a teacher')
    "NO": "NOT",              # F no (negation)
    "ABI": "OR",              # abi: 'or'; abi?: 'right?' (F records the question use)
    "REASON": "REFLECT",      # ? reason am: think it over
    "ROB": "ANOINT",          # ? rub on
    "LOCK": "SEAL",           # ? lock
    "WITNESS": "TESTIFY",     # ? bear witness
    "NOTHING": "VOID",        # ? nothing
    "STOP": "BREAK",          # ? stop
    "MOVE": "CONTINUE",       # ? move on
}

_PG_COMPOUNDS = {
    ("FINISH", "IF"): "ENDIF",
    ("FINISH", "TRY"): "ENDTRY",
}

_PG_SNIPPETS = (
    ("OYA KREASHON … FINISH KREASHON",
     "OYA KREASHON\\n\\t$0\\nFINISH KREASHON",
     "Open a new scroll"),
    ("IF … DEN … FINISH IF",
     "IF ${1:condition} DEN\\n\\t$0\\nFINISH IF",
     "Weigh a condition"),
    ("TRY … HOLD … FINISH TRY",
     "TRY\\n\\t${1:works}\\nHOLD\\n\\t${2:refuge}$0\\nFINISH TRY",
     "Shelter a fragile work"),
)

TONGUES: dict[str, dict] = {
    "tn": {
        "name": "Setswana",
        "aliases": _TN_ALIASES,
        "compounds": _TN_COMPOUNDS,
        "snippets": _TN_SNIPPETS,
    },
    "zu": {
        "name": "isiZulu",
        "aliases": _ZU_ALIASES,
        "compounds": _ZU_COMPOUNDS,
        "snippets": _ZU_SNIPPETS,
    },
    "ig": {
        "name": "Igbo",
        "aliases": _IG_ALIASES,
        "compounds": _IG_COMPOUNDS,
        "snippets": _IG_SNIPPETS,
    },
    "pg": {
        "name": "Nigerian Pidgin",
        "aliases": _PG_ALIASES,
        "compounds": _PG_COMPOUNDS,
        "snippets": _PG_SNIPPETS,
    },
}

# Other codes a scroll may use for a tongue: ``pcm`` is the standard
# (ISO 639-3) code for Nigerian Pidgin.
_CODE_ALIASES = {"pcm": "pg"}

_CANONICAL = {"en": {"name": "English", "aliases": {}, "compounds": {}}}


def known_tongues() -> dict[str, str]:
    """Map of tongue code -> language name, canonical English included."""
    return {"en": "English", **{c: t["name"] for c, t in TONGUES.items()}}


def detect_tongue(source: str) -> str | None:
    """Return the tongue code from a ``# tongue: xx`` pragma, or None."""
    m = _PRAGMA.search(source)
    return m.group(1).lower() if m else None


def resolve(code: str | None) -> dict:
    """Return the tongue table for a code; raises a gentle error if unknown."""
    if code is None or code == "en":
        return _CANONICAL["en"]
    code = _CODE_ALIASES.get(code, code)
    if code in TONGUES:
        return TONGUES[code]
    from .errors import LexerError

    names = ", ".join(f"{c} ({n})" for c, n in known_tongues().items())
    raise LexerError(
        f"The tongue '{code}' is not known yet; no scroll can be read in it. "
        f"The tongues God Code speaks are: {names}.",
    )


def parse_source(source: str, tongue: str | None = None):
    """Lex (honouring any ``# tongue:`` pragma) and parse God Code source.

    This is the one doorway every tool should use instead of calling the
    Lexer and Parser directly, so tongues work the same in ``run``,
    ``check``, ``lint``, ``fmt``, the debugger, the language server, and
    the agent bridge.
    """
    from .lexer import Lexer
    from .parser import Parser

    lx = Lexer(source, tongue=tongue)
    return Parser(lx.lex(), tongue=lx.tongue).parse()
