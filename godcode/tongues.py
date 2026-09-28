"""Tongues: the grammar of God Code in other languages.

A *tongue* lets the keywords of God Code be written in another language.
English is the canonical tongue; every other tongue maps its words onto the
same tokens, so the parser, the interpreter, the linter, and all the tools
work unchanged. A scroll chooses its tongue with a pragma comment on one of
its early lines::

    # tongue: tn

``tn`` is Setswana, the first tongue, spoken in Botswana. Mixed scrolls are
welcome: English keywords keep working beside tongue words in the same file,
so a learner can cross over one word at a time.

Design notes, kept honest:

- Only keywords are translated. The named tools (``SHA256``, ``UPPER``,
  ``RANGE`` ...) keep their names in every tongue, so scrolls stay
  interoperable and the standard library is learned once.
- ``godcode fmt`` always renders the canonical English tongue.
- This first edition leaves a few words in English (``ELSE``, ``NOT``,
  ``FOR``, ``WHILE``, ``ENDFOR``, ``ENDWHILE``); they are documented in
  ``docs/TONGUES.md`` and will cross over as speakers bless better words.
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
    "QALA": "BEGIN",        # begin
    "TLHOLEGO": "CREATION",  # creation
    "FEDISA": "END",        # end
    "BOLELA": "DECLARE",    # say, announce
    "JAKA": "AS",           # as, like
    "HEMA": "BREATHE",      # breathe
    "BOTSHELO": "LIFE",     # life
    "TENG": "INTO",         # inside (MO is taken by IN)
    "SENOLA": "REVEAL",     # reveal
    "POROFETA": "PROPHESY",  # prophesy
    "TLHATLOGA": "ASCEND",  # go up
    "FA": "IF",             # if
    "GONE": "THEN",         # then
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

TONGUES: dict[str, dict] = {
    "tn": {
        "name": "Setswana",
        "aliases": _TN_ALIASES,
        "compounds": _TN_COMPOUNDS,
    },
}

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
