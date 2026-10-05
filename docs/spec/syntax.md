# The Syntax Layer

**How God Code tokens become a scroll's shape.** This is the second layer of the specification: it says how tokens join into statements, blocks, rites, and expressions. It says nothing about what a scroll means when it runs. That is the next layer's work. Every rule below is kept honest by a test in `tests/test_spec_syntax.py` that carries the rule's number.

The probes show source the way an author writes it. `BEGIN CREATION` and `END CREATION` wrap the examples, the way every shared program is wrapped.

---

## The shape of a scroll

**SX-1.** A scroll parses to one `Program`: either exactly one `BEGIN CREATION ... END CREATION` block, or a bare sequence of statements. The creation block is the form every shared program uses. The bare form serves fragments.

```
BEGIN CREATION
REVEAL("blessed")
END CREATION
```

parses to a `Program` holding one `CreationBlock`, which holds the `REVEAL`.

**SX-2.** A scroll holds only one creation. Anything but blank lines after `END CREATION` is rejected, naming the leftover: a scroll holds only one creation.

**SX-3.** The words of a phrase stay on one line. `BEGIN` and `CREATION` must share a line, and so must `END` and `CREATION`, and `END` and `RITE`. A line break between them is rejected.

**SX-4.** An unclosed block is rejected with counsel: the error names the missing closer and the line where the block opened, so the author knows where to look.

**SX-5.** A closer that arrives before its block's own closer is rejected and named: `END CREATION` appearing where `ENDIF` was owed is an error, and every opened block must be closed in its own time.

**SX-6.** A closer with no open block is rejected as an unexpected word. A lone `ENDIF` is not a statement.

## Lines and statements

**SX-7.** Statements are separated by line breaks, and blank lines are ignored. The parser skips any run of empty lines between statements.

**SX-8.** Two statements may share one line. `REVEAL(1) REVEAL(2)` is two statements, and both run.

**SX-9.** An empty scroll is a program with no statements, and `BEGIN CREATION END CREATION` is a creation with no works. Neither is an error.

## Declarations

**SX-10.** `DECLARE name AS expr` binds one name to one value. `AS` is required, the name must be a plain identifier, and a missing value is rejected where the line ends.

**SX-11.** `DECLARE name AS e1, e2, ...` binds the name to a list of the values, in order. `DECLARE x AS 1, 2, 3` binds `x` to the gathering `[1, 2, 3]`.

**SX-12.** `DECLARE INTENT "words" ON rite_name` declares a rite's purpose. `INTENT` and `ON` are soft words, not reserved: only `DECLARE` followed by the word `INTENT` and then a quoted string takes this path, so `DECLARE intent AS 5` still declares an ordinary name called `intent`.

## The small decrees

**SX-13.** `REVEAL(expr)` carries exactly one expression, and the parentheses are required. `REVEAL 1` is rejected.

**SX-14.** `SEAL expr` and `TESTIFY expr` take a bare expression. Parentheses around it are the ordinary grouping kind, so `SEAL(x)` is the same decree as `SEAL x`.

**SX-15.** `BLESS name`, `ANOINT name`, and `BREATHE LIFE INTO name` take exactly one name each. `ASCEND` and `REFLECT` stand alone with nothing after them.

**SX-16.** `PROPHESY` takes the rest of the line as text: the line's token values joined with single spaces. Keywords keep their canonical UPPER spelling, so `PROPHESY the lord is good, truly` prophesies `the lord IS good , truly`. An empty `PROPHESY` line prophesies the empty text.

## Conditionals

**SX-17.** `IF cond THEN` on its own line opens a block closed by `ENDIF`, with an optional `ELSE` part between them. `IF cond THEN stmt` on one line is the short form, and `ELSE stmt` may follow it on the same line.

**SX-18.** Every `IF` needs its `THEN`, and a block `IF` needs its `ENDIF`. A missing closer is rejected under SX-4 and SX-5.

## Loops

**SX-19.** `FOR name IN expr` walks each value of the gathering, binding the traveler's name in turn. The name must be a plain identifier. The block form closes with `ENDFOR`; the one-line form carries a single statement.

**SX-20.** `WHILE cond DO` repeats its works while the condition holds true, closed by `ENDWHILE`; the one-line form carries a single statement. Unlike `FOR`, the closer is always required.

**SX-21.** `FOR` keeps the old open form from the earliest sample scrolls: if `END CREATION`, `END RITE`, or the end of the scroll arrives before `ENDFOR`, the loop simply ends there. New scrolls should close their loops.

**SX-22.** `BREAK` and `CONTINUE` are rejected at parse time when no loop holds them. They never cross a rite boundary: a `BREAK` inside a rite answers only to loops inside that rite, never to a caller's loop.

## Shelter

**SX-23.** `TRY` always opens a block. Its works go on the following lines, then `CATCH` with an optional error name, then `ENDTRY`. With no name the error is bound to `ERROR`. There is no one-line `TRY`.

## Rites

**SX-24.** `DEFINE RITE name(p1, p2, ...)` names a rite and its parameters, closed by `END RITE`. Parameters are plain names separated by commas; empty parentheses mean the rite takes none.

**SX-25.** A rite body is either a block on the following lines or a single statement on the same line, as in `DEFINE RITE f(x) SEAL x END RITE`. The one-line form still needs `END RITE`, and an empty one-line body is rejected.

**SX-26.** `RETURN` ends a rite's work carrying an optional value: `RETURN expr`, or bare `RETURN` with nothing carried.

**SX-27.** A call names a rite directly: `name(args)` wherever a value is expected, or `INVOKE name(args)` as a statement. Arguments are comma-separated expressions; empty parentheses call with none. There are no method calls: a call's target is always a plain name.

## Imports

**SX-28.** `IMPORT "path"` names a scroll in quotes. Anything but a quoted string is rejected where it stands.

## Expressions

**SX-29.** Operators bind in this order, loosest first: `OR`, then `AND`, then `NOT`, then the comparisons, then `+` and `-`, then `*`, `/`, and `%`, then unary `-` and `NOT`, then indexing, then the primaries (names, numbers, strings, truths, calls, lists, grouped expressions). Parentheses overrule everything.

**SX-30.** `IS` is `==` and `IS NOT` is `!=`. The single `=` and the double `==` both spell equality.

**SX-31.** Comparisons chain left to right: `a IS b IS c` is read as `(a IS b) IS c`.

**SX-32.** `NOT` binds tighter than `AND` and `OR` but looser than the comparisons, so `NOT a IS b` is `NOT (a IS b)`. Beside unary minus sits a tighter `NOT` that binds to what follows it, so `a * NOT b` is `a * (NOT b)`.

**SX-33.** Unary minus binds tighter than multiplication: `-2 * 3` is `(-2) * 3`. There are no negative number tokens (see LX-14): `-5` is minus applied to `5`.

**SX-34.** Indexing is postfix and chains: `a[0][1]` indexes the result of `a[0]`. The index is any expression.

**SX-35.** Lists are `[e1, e2, ...]`, and `[]` is the empty gathering. Parentheses group an expression: `(a + b)` is one value.

**SX-36.** `TRUE`, `FALSE`, and `VOID` are literal values in any letter case.

## Interpolation

**SX-37.** A string holding `{` breathes: `{expr}` places one expression's value into the words. `{{` and `}}` write plain braces, and a lone `}` stays a plain brace.

**SX-38.** Empty braces are rejected: `{}` breathes nothing. An unclosed `{` is rejected where it opened.

**SX-39.** Between one pair of braces dwells exactly one expression. Nested braces and quoted strings inside are honoured, so `"{greet(\"hi {name}\")}"` seals correctly, but `{b c}` is rejected: only one expression may dwell there.

---

*Kept honest by `tests/test_spec_syntax.py`. The next layer is static meaning: what can be known about names and scopes before a scroll ever runs.*
