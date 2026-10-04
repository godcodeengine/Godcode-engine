# The Lexical Layer

**How God Code source text becomes tokens.** This is the first layer of the specification, and the narrowest: it says nothing about what a scroll means, only about what a scroll is made of. Every rule below is kept honest by a test in `tests/test_spec_lexical.py` that carries the rule's number.

---

## Source text and lines

**LX-1.** A scroll is text. The lexer reads characters and turns them into a list of tokens. The token list always ends with exactly one `EOF` token.

**LX-2.** Each line break becomes one `NEWLINE` token. A Windows-style `\r\n` pair collapses to a single `NEWLINE`; a lone `\r` is tolerated and becomes one `NEWLINE` too.

```
REVEAL 1
REVEAL 2
```

lexes as `REVEAL 1 NEWLINE REVEAL 2 EOF`. The language is line-oriented, and the line breaks are part of the token stream on purpose: later layers read them to know where each statement ends.

## Whitespace

**LX-3.** Spaces and tabs separate tokens and are otherwise ignored. They never become tokens themselves.

## Comments

**LX-4.** A `#` starts a comment that runs to the end of the line. The line break itself is still lexed, so a comment never swallows the newline.

**LX-5.** A `#` inside a double-quoted string is just a character, not a comment. `"psalm #23"` is one string.

## Keywords

**LX-6.** Keywords are matched case-insensitively, and every keyword token carries its canonical UPPER name. `declare`, `Declare`, and `DECLARE` are all the same word, and the token says `DECLARE`.

**LX-7.** The keywords are these, and only these:

`BEGIN` `CREATION` `END` `DECLARE` `AS` `BREATHE` `LIFE` `INTO` `REVEAL` `PROPHESY` `ASCEND` `IF` `THEN` `ELSE` `ENDIF` `FOR` `IN` `ENDFOR` `WHILE` `DO` `ENDWHILE` `BREAK` `CONTINUE` `TRY` `CATCH` `ENDTRY` `DEFINE` `RITE` `INVOKE` `RETURN` `IMPORT` `IS` `NOT` `AND` `OR` `REFLECT` `BLESS` `ANOINT` `SEAL` `TESTIFY` `TRUE` `FALSE` `VOID`

Multi-word phrases like `BEGIN CREATION`, `END RITE`, and `BREATHE LIFE INTO` are separate keyword tokens at this layer. Joining them into phrases is the syntax layer's work. `TRUE`, `FALSE`, and `VOID` are keywords, so they work in any letter case.

## Identifiers

**LX-8.** A name starts with a letter or an underscore and continues with letters, digits, or underscores: `seeker`, `_x9`, `psalm23`. Identifiers keep the author's casing exactly.

**LX-9.** Identifiers are case-sensitive. `seeker` and `Seeker` are two different names.

## Numbers

**LX-10.** Numbers are integers or floats. `3` is the number 3. Leading zeros are accepted, so `007` is the number 7. `4.5` is the number 4.5.

**LX-11.** A decimal point must be followed by digits. `5.` is rejected with a gentle error that says a decimal point must be followed by digits.

**LX-12.** There is no scientific notation and no leading-dot form. `1e5` lexes as the number `1` followed by the name `e5`. `.5` is rejected, because `.` is not a character the language recognizes.

**LX-13.** A number next to a word splits cleanly: `12abc` is the number `12` followed by the name `abc`.

**LX-14.** Negative numbers are not a lexer's business. `-5` is the minus operator followed by the number `5`; the syntax layer reads it as one negative number.

## Strings

**LX-15.** Strings use double quotes only. The token's value is the unescaped text: `"a\nb"` is the two lines `a` and `b` joined by a newline.

**LX-16.** Four escapes are recognized: `\"` for a quote, `\\` for a backslash, `\n` for a newline, `\t` for a tab. Any other escape is a lexer error naming the escape and the line and column.

**LX-17.** A string cannot span lines. If the line ends before the closing quote, the lexer rejects the string and names the line and column where the string opened.

**LX-18.** A string that is never closed at all is rejected the same way, naming the line and column of the opening quote.

**LX-19.** Braces inside a string are ordinary characters to the lexer. `"grace upon {name}"` is one `STRING` token holding `grace upon {name}`. Deciding what `{...}` means is the syntax layer's work, and interpolating it is the dynamic layer's.

## Operators and punctuation

**LX-20.** The operators are:

| Written | Token | Written | Token |
|---|---|---|---|
| `+` | PLUS | `-` | MINUS |
| `*` | STAR | `/` | SLASH |
| `%` | PERCENT | `=` | EQ |
| `==` | EQ | `!=` | NEQ |
| `<` | LT | `>` | GT |
| `<=` | LTE | `>=` | GTE |

Both `=` and `==` spell equality. Multi-character operators are matched before single-character ones, so `<=` is one token, never `<` followed by `=`.

**LX-21.** The punctuation is `(`, `)`, `[`, `]`, and `,`. Each is its own token.

**LX-22.** Any other character is a lexer error that names the character and its line and column. In particular, `{` and `}` outside a string are not tokens: braces only ever appear inside strings, where LX-19 applies.

## Tongues at the lexical layer

**LX-23.** A scroll may choose a tongue with a pragma comment, for example `# tongue: tn` for Setswana. The pragma is a comment line matching the shape `# tongue: xx` (spaces are forgiving, the case is not strict), and it is searched for anywhere in the source: a pragma on line 3 still sets the tongue for line 1.

**LX-24.** An explicitly chosen tongue wins over the pragma. When no tongue is chosen, the tongue is English, and English has no aliases.

**LX-25.** A tongue word maps onto the same keyword token as its English twin, matched case-insensitively. Under `# tongue: tn`, `SENOLA` and `senola` both become the `REVEAL` token. The parser downstream never knows which tongue was written; it only sees the tokens.

**LX-26.** Two-word closers like `FEDISA FA` must share one line. On one line they become a single `ENDIF` token, positioned where the first word stood. Split across two lines they lex as two separate tokens (`END` then `IF`), and the syntax layer will not join them.

**LX-27.** A tongue code the language does not know is a gentle lexer error that names the unknown code and lists the tongues God Code speaks. No scroll can be read in an unknown tongue.

**LX-28.** The named tools keep their names in every tongue. `SHA256`, `UPPER`, and the other built-in rites are not keywords, so under `# tongue: tn` they lex as ordinary identifiers, exactly as in English.

## Positions

**LX-29.** Lines and columns are 1-based. A token's position is the line and column of its first character. Errors name the position where the trouble started: a runaway string names its opening quote.

---

*Kept honest by `tests/test_spec_lexical.py`. The next layer is syntax: how these tokens become a scroll's shape.*
