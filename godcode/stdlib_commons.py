"""God Code standard library, part 4: the commons.

This module holds the everyday tools a working language needs: trimming
and searching words, sorting and gathering lists, reading maps, and
rounding numbers. They are kept apart from the interpreter core so the
language's heart stays small.

Wiring
------
``register(interp)`` adds the builtins to ``interp._builtins``. Each
builtin is a plain callable ``(args, line)`` in the style of the core
builtins (arity through ``interp._arity``, plain-word GodRuntimeError
messages).

Sandbox honesty
---------------
Every rite here is pure computation: words, lists, maps, and numbers
in, new values out. They touch no files, no network, and no host
resources. They need no sandbox grant and behave the same under
``godcode run --sandbox``.
"""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable

from godcode.errors import GodRuntimeError

__all__ = ["register"]


# ------------------------------------------------------------ value helpers


def _as_word(interp, name: str, value: Any, line) -> str:
    """Take a God Code word, number, or truth as plain text.

    Lists, maps, void, rites, and contracts have no plain-text shape
    for a word tool, so they are refused with a gentle error.
    """
    from godcode.values import Symbol

    if not isinstance(value, (str, bool, int, float, Symbol)):
        raise GodRuntimeError(
            f"{name} works on words, but a {interp.type_name(value)} "
            "was offered.",
            line,
        )
    return interp.stringify(value)


def _need_list(interp, name: str, value: Any, line) -> list:
    if not isinstance(value, list):
        raise GodRuntimeError(
            f"{name} gathers a list, but a {interp.type_name(value)} "
            "was offered.",
            line,
        )
    return value


def _need_map(interp, name: str, value: Any, line) -> dict:
    if not isinstance(value, dict):
        raise GodRuntimeError(
            f"{name} reads a map, but a {interp.type_name(value)} "
            "was offered.",
            line,
        )
    return value


def _need_number(interp, name: str, value: Any, line) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GodRuntimeError(
            f"{name} weighs a number, but a {interp.type_name(value)} "
            "was offered.",
            line,
        )
    return value


def _need_int(interp, name: str, value: Any, line) -> int:
    number = _need_number(interp, name, value, line)
    if isinstance(number, float) and not number.is_integer():
        raise GodRuntimeError(
            f"{name} counts in whole numbers, but {interp.stringify(value)} "
            "was offered.",
            line,
        )
    return int(number)


def _sort_key(interp, name: str, value: Any, line):
    """A sortable key for one list member: numbers, words, or truths.

    Mixed kinds cannot be ordered against each other, so they are
    refused with a gentle error.
    """
    if isinstance(value, bool):
        return (2, int(value))
    if isinstance(value, (int, float)):
        return (0, value)
    if isinstance(value, str):
        return (1, value)
    raise GodRuntimeError(
        f"{name} can order numbers, words, and truths together, but "
        f"a {interp.type_name(value)} was found among them.",
        line,
    )


def _ordered(interp, name: str, values: list, line) -> list:
    """Check every member is orderable; refuse mixed kinds gently."""
    kinds = set()
    for value in values:
        if isinstance(value, bool):
            kinds.add("truth")
        elif isinstance(value, (int, float)):
            kinds.add("number")
        elif isinstance(value, str):
            kinds.add("word")
        else:
            raise GodRuntimeError(
                f"{name} can order numbers, words, and truths, but a "
                f"{interp.type_name(value)} was found among them.",
                line,
            )
    if len(kinds) > 1:
        raise GodRuntimeError(
            f"{name} cannot order a gathering of mixed kinds "
            f"({', '.join(sorted(kinds))}).",
            line,
        )
    return values


# ------------------------------------------------------------------ words


def trim(args, line, interp):
    interp._arity("TRIM", args, 1, line)
    return _as_word(interp, "TRIM", args[0], line).strip()


def replace(args, line, interp):
    interp._arity("REPLACE", args, 3, line)
    word = _as_word(interp, "REPLACE", args[0], line)
    old = _as_word(interp, "REPLACE", args[1], line)
    new = _as_word(interp, "REPLACE", args[2], line)
    if old == "":
        raise GodRuntimeError(
            "REPLACE needs something to find: an empty word hides "
            "everywhere at once.",
            line,
        )
    return word.replace(old, new)


def starts_with(args, line, interp):
    interp._arity("STARTS_WITH", args, 2, line)
    word = _as_word(interp, "STARTS_WITH", args[0], line)
    prefix = _as_word(interp, "STARTS_WITH", args[1], line)
    return word.startswith(prefix)


def ends_with(args, line, interp):
    interp._arity("ENDS_WITH", args, 2, line)
    word = _as_word(interp, "ENDS_WITH", args[0], line)
    suffix = _as_word(interp, "ENDS_WITH", args[1], line)
    return word.endswith(suffix)


def substring(args, line, interp):
    interp._arity("SUBSTRING", args, (2, 3), line)
    word = _as_word(interp, "SUBSTRING", args[0], line)
    start = _need_int(interp, "SUBSTRING", args[1], line)
    end = _need_int(interp, "SUBSTRING", args[2], line) if len(args) == 3 else len(word)
    start = max(0, min(start, len(word)))
    end = max(0, min(end, len(word)))
    return word[start:end]


def contains(args, line, interp):
    interp._arity("CONTAINS", args, 2, line)
    haystack, needle = args[0], args[1]
    if isinstance(haystack, str):
        return _as_word(interp, "CONTAINS", needle, line) in haystack
    if isinstance(haystack, list):
        return any(item == needle for item in haystack)
    raise GodRuntimeError(
        "CONTAINS searches a word or a list, but a "
        f"{interp.type_name(haystack)} was offered.",
        line,
    )


def count(args, line, interp):
    interp._arity("COUNT", args, 2, line)
    word = _as_word(interp, "COUNT", args[0], line)
    part = _as_word(interp, "COUNT", args[1], line)
    if part == "":
        raise GodRuntimeError(
            "COUNT needs something to count: an empty word hides "
            "everywhere at once.",
            line,
        )
    return word.count(part)


# ------------------------------------------------------------------ lists


def sort_list(args, line, interp):
    interp._arity("SORT", args, 1, line)
    values = _ordered(interp, "SORT", _need_list(interp, "SORT", args[0], line), line)
    return sorted(values, key=lambda v: _sort_key(interp, "SORT", v, line)[1:])


def min_of(args, line, interp):
    interp._arity("MIN_OF", args, 1, line)
    values = _ordered(interp, "MIN_OF", _need_list(interp, "MIN_OF", args[0], line), line)
    if not values:
        raise GodRuntimeError(
            "MIN_OF found an empty gathering: there is no least among nothing.",
            line,
        )
    return min(values, key=lambda v: _sort_key(interp, "MIN_OF", v, line)[1:])


def max_of(args, line, interp):
    interp._arity("MAX_OF", args, 1, line)
    values = _ordered(interp, "MAX_OF", _need_list(interp, "MAX_OF", args[0], line), line)
    if not values:
        raise GodRuntimeError(
            "MAX_OF found an empty gathering: there is no greatest among nothing.",
            line,
        )
    return max(values, key=lambda v: _sort_key(interp, "MAX_OF", v, line)[1:])


def sum_of(args, line, interp):
    interp._arity("SUM_OF", args, 1, line)
    values = _need_list(interp, "SUM_OF", args[0], line)
    total: int | float = 0
    for value in values:
        number = _need_number(interp, "SUM_OF", value, line)
        total += number
    return total


def first(args, line, interp):
    interp._arity("FIRST", args, 1, line)
    values = _need_list(interp, "FIRST", args[0], line)
    if not values:
        raise GodRuntimeError(
            "FIRST found an empty gathering: nothing stands at its head.",
            line,
        )
    return values[0]


def last(args, line, interp):
    interp._arity("LAST", args, 1, line)
    values = _need_list(interp, "LAST", args[0], line)
    if not values:
        raise GodRuntimeError(
            "LAST found an empty gathering: nothing stands at its end.",
            line,
        )
    return values[-1]


def unique(args, line, interp):
    interp._arity("UNIQUE", args, 1, line)
    values = _need_list(interp, "UNIQUE", args[0], line)
    seen: list = []
    for value in values:
        if not any(value == other for other in seen):
            seen.append(value)
    return seen


def index_of(args, line, interp):
    interp._arity("INDEX_OF", args, 2, line)
    values = _need_list(interp, "INDEX_OF", args[0], line)
    for position, value in enumerate(values):
        if value == args[1]:
            return position
    return -1


# ------------------------------------------------------------------- maps


def keys(args, line, interp):
    interp._arity("KEYS", args, 1, line)
    return list(_need_map(interp, "KEYS", args[0], line).keys())


def values_of(args, line, interp):
    interp._arity("VALUES", args, 1, line)
    return list(_need_map(interp, "VALUES", args[0], line).values())


def has_key(args, line, interp):
    interp._arity("HAS_KEY", args, 2, line)
    mapping = _need_map(interp, "HAS_KEY", args[0], line)
    key = args[1]
    if not isinstance(key, str):
        raise GodRuntimeError(
            "HAS_KEY looks up a word, but a "
            f"{interp.type_name(key)} was offered as the key.",
            line,
        )
    return str(key) in mapping


def merge(args, line, interp):
    interp._arity("MERGE", args, 2, line)
    first_map = _need_map(interp, "MERGE", args[0], line)
    second_map = _need_map(interp, "MERGE", args[1], line)
    merged = dict(first_map)
    merged.update(second_map)
    return merged


# ---------------------------------------------------------------- numbers


def absolute(args, line, interp):
    interp._arity("ABS", args, 1, line)
    return abs(_need_number(interp, "ABS", args[0], line))


def round_number(args, line, interp):
    interp._arity("ROUND", args, (1, 2), line)
    number = _need_number(interp, "ROUND", args[0], line)
    places = _need_int(interp, "ROUND", args[1], line) if len(args) == 2 else 0
    if places < 0:
        raise GodRuntimeError(
            "ROUND counts places from zero upward: a negative count "
            "was offered.",
            line,
        )
    rounded = Decimal(str(number)).quantize(
        Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP
    )
    if places == 0:
        return int(rounded)
    return float(rounded)


def floor_number(args, line, interp):
    interp._arity("FLOOR", args, 1, line)
    return math.floor(_need_number(interp, "FLOOR", args[0], line))


def ceil_number(args, line, interp):
    interp._arity("CEIL", args, 1, line)
    return math.ceil(_need_number(interp, "CEIL", args[0], line))


def sqrt_number(args, line, interp):
    interp._arity("SQRT", args, 1, line)
    number = _need_number(interp, "SQRT", args[0], line)
    if number < 0:
        raise GodRuntimeError(
            "SQRT cannot root a negative number: no real answer lives there.",
            line,
        )
    rooted = math.sqrt(number)
    if float(rooted).is_integer():
        return int(rooted)
    return rooted


def power(args, line, interp):
    interp._arity("POW", args, 2, line)
    base = _need_number(interp, "POW", args[0], line)
    exp = _need_number(interp, "POW", args[1], line)
    try:
        result = math.pow(base, exp)
    except (ValueError, OverflowError):
        raise GodRuntimeError(
            "POW cannot raise that pair: the answer leaves the real numbers.",
            line,
        ) from None
    if float(result).is_integer() and abs(result) < 1e15:
        return int(result)
    return result


# ---------------------------------------------------------------- wiring


def register(interp) -> dict[str, Callable[..., Any]]:
    """Add the commons builtins to ``interp._builtins``; return them."""
    names_funcs = [
        ("TRIM", trim),
        ("REPLACE", replace),
        ("STARTS_WITH", starts_with),
        ("ENDS_WITH", ends_with),
        ("SUBSTRING", substring),
        ("CONTAINS", contains),
        ("COUNT", count),
        ("SORT", sort_list),
        ("MIN_OF", min_of),
        ("MAX_OF", max_of),
        ("SUM_OF", sum_of),
        ("FIRST", first),
        ("LAST", last),
        ("UNIQUE", unique),
        ("INDEX_OF", index_of),
        ("KEYS", keys),
        ("VALUES", values_of),
        ("HAS_KEY", has_key),
        ("MERGE", merge),
        ("ABS", absolute),
        ("ROUND", round_number),
        ("FLOOR", floor_number),
        ("CEIL", ceil_number),
        ("SQRT", sqrt_number),
        ("POW", power),
    ]
    builtins: dict[str, Callable[..., Any]] = {}
    for name, func in names_funcs:

        def _builtin(args, line, _func=func):
            return _func(args, line, interp)

        builtins[name] = _builtin
    interp._builtins.update(builtins)
    return builtins
