"""God Code standard library, part 3: the scrollhouse of hashes and veils.

This module holds builtins that fingerprint and seal words: SHA-256
digests, HMAC-SHA-256 signatures, and the veils of base64. They are kept
apart from the interpreter core so the language's heart stays small.

Wiring
------
``register(interp)`` adds the builtins to ``interp._builtins``. Each
builtin is a plain callable ``(args, line)`` in the style of the core
builtins (arity through ``interp._arity``, plain-word GodRuntimeError
messages).

Sandbox honesty
---------------
SHA256, HMAC, BASE64_ENCODE, and BASE64_DECODE are pure computation:
they touch no files, no network, and no host resources. They need no
sandbox grant and behave the same under ``godcode run --sandbox``.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any, Callable

from godcode.errors import GodRuntimeError

__all__ = ["register"]


# ------------------------------------------------------------ value helpers


def _as_text(interp, name: str, value: Any, line) -> str:
    """Take a God Code word, number, or truth as plain text.

    Lists, maps, void, rites, and contracts have no plain-text shape
    for a fingerprint, so they are refused with a gentle error.
    """
    from godcode.values import Symbol

    if not isinstance(value, (str, bool, int, float, Symbol)):
        raise GodRuntimeError(
            f"{name} can fingerprint a word, a number, or a truth, "
            f"but a {interp.type_name(value)} was offered.",
            line,
        )
    return interp.stringify(value)


def sha256(args, line, interp):
    interp._arity("SHA256", args, 1, line)
    text = _as_text(interp, "SHA256", args[0], line)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hmac_sha256(args, line, interp):
    interp._arity("HMAC", args, 2, line)
    key = _as_text(interp, "HMAC", args[0], line)
    message = _as_text(interp, "HMAC", args[1], line)
    digest = hmac.new(
        key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    )
    return digest.hexdigest()


def base64_encode(args, line, interp):
    interp._arity("BASE64_ENCODE", args, 1, line)
    text = _as_text(interp, "BASE64_ENCODE", args[0], line)
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def base64_decode(args, line, interp):
    interp._arity("BASE64_DECODE", args, 1, line)
    value = args[0]
    from godcode.values import Symbol

    if not isinstance(value, (str, Symbol)):
        raise GodRuntimeError(
            "BASE64_DECODE needs a veiled word to lift, "
            f"but a {interp.type_name(value)} was offered.",
            line,
        )
    veiled = str(value)
    try:
        raw = base64.b64decode(veiled, validate=True)
        return raw.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        raise GodRuntimeError(
            "BASE64_DECODE met a veil it cannot lift: the word is not "
            "well-formed base64.",
            line,
        ) from None


def register(interp) -> dict[str, Callable[..., Any]]:
    """Add the hash builtins to ``interp._builtins``; return them."""
    arity = interp._arity

    def _sha256(args, line):
        return sha256(args, line, interp)

    def _hmac(args, line):
        return hmac_sha256(args, line, interp)

    def _b64e(args, line):
        return base64_encode(args, line, interp)

    def _b64d(args, line):
        return base64_decode(args, line, interp)

    builtins: dict[str, Callable[..., Any]] = {
        "SHA256": _sha256,
        "HMAC": _hmac,
        "BASE64_ENCODE": _b64e,
        "BASE64_DECODE": _b64d,
    }
    interp._builtins.update(builtins)
    return builtins
