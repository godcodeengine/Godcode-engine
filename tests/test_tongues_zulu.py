"""Tests for the second tongue: isiZulu (godcode.tongues, code ``zu``).

isiZulu joins Setswana as a tongue of God Code: a scroll that opens with
``# tongue: zu`` writes its keywords in isiZulu. Every test runs real
isiZulu source through the real pipeline (lexer, interpreter, formatter,
language server, VS Code files, the shipped example) and asserts on what
comes out. Without the pragma, Zulu words are ordinary identifiers.
"""

import json
import re
from pathlib import Path

import pytest

from godcode import lsp
from godcode.errors import GodCodeError, LexerError
from godcode.interpreter import Interpreter
from godcode.lexer import Lexer
from godcode.tongues import (
    detect_tongue,
    known_tongues,
    parse_source,
    resolve,
)

REPO = Path(__file__).resolve().parent.parent


def run(src):
    """Parse src (honouring any tongue pragma), run it, return output lines."""
    interp = Interpreter()
    interp.run(parse_source(src))
    return interp.output


ZU_HELLO = """# tongue: zu
QALA INDALO
MEMEZELA igama NJENGA "Umhlaba"
VEZA("Sawubona, " + igama)
QEDA INDALO
"""


# ------------------------------------------------------- pragma and tables


def test_detect_zulu_pragma():
    assert detect_tongue("# tongue: zu\nQALA INDALO\n") == "zu"
    assert detect_tongue("#tongue:ZU\n") == "zu"


def test_known_tongues_lists_isizulu_beside_setswana():
    assert known_tongues()["zu"] == "isiZulu"
    assert known_tongues()["tn"] == "Setswana"
    assert known_tongues()["en"] == "English"


def test_unknown_tongue_error_names_isizulu():
    with pytest.raises(LexerError) as excinfo:
        resolve("xx")
    assert "zu (isiZulu)" in str(excinfo.value)
    assert "tn (Setswana)" in str(excinfo.value)


def test_zulu_table_covers_the_setswana_keyword_set():
    """The second tongue is a full tongue: same canonical coverage as tn."""
    tn = resolve("tn")["aliases"]
    zu = resolve("zu")["aliases"]
    assert set(zu.values()) == set(tn.values())
    assert set(resolve("zu")["compounds"].values()) == {"ENDIF", "ENDTRY"}
    # No Zulu word may shadow an English keyword token name by accident:
    # every alias value is a canonical keyword the lexer knows.
    from godcode.lexer import KEYWORDS

    assert set(zu.values()) <= set(KEYWORDS)


# ------------------------------------------------------------------ lexing


def test_zulu_alias_words_become_canonical_tokens():
    from godcode.tokens import TokenType

    toks = [t for t in Lexer(ZU_HELLO).lex()
            if t.type.name not in ("NEWLINE", "EOF")]
    kinds = [t.type for t in toks]
    assert kinds[0] is TokenType.BEGIN
    assert kinds[1] is TokenType.CREATION
    assert kinds[2] is TokenType.DECLARE
    assert toks[0].value == "BEGIN"
    assert toks[2].value == "DECLARE"


def test_zulu_two_word_closers():
    from godcode.tokens import TokenType

    src = "# tongue: zu\nQALA INDALO\nUMA x KHONA\nQEDA UMA\nQEDA INDALO\n"
    kinds = [t.type for t in Lexer(src).lex()]
    assert TokenType.ENDIF in kinds
    assert kinds.count(TokenType.END) == 1  # only END CREATION's END

    src = "# tongue: zu\nQALA INDALO\nZAMA\nBAMBA\nQEDA ZAMA\nQEDA INDALO\n"
    kinds = [t.type for t in Lexer(src).lex()]
    assert TokenType.ENDTRY in kinds


def test_zulu_compound_closer_needs_one_line():
    src = "# tongue: zu\nQALA INDALO\nQEDA\nUMA\nQEDA INDALO\n"
    with pytest.raises(GodCodeError):
        parse_source(src)


def test_without_pragma_zulu_words_are_identifiers():
    from godcode.tokens import TokenType

    kinds = [t.type for t in Lexer("QALA INDALO\n").lex()]
    assert TokenType.IDENT in kinds
    assert TokenType.BEGIN not in kinds


# ----------------------------------------------------------------- running


def test_zulu_hello_runs():
    assert run(ZU_HELLO) == ["Sawubona, Umhlaba"]


def test_zulu_if_then_endif_compound_runs():
    src = """# tongue: zu
QALA INDALO
MEMEZELA imvula NJENGA IQINISO
UMA imvula KHONA
    VEZA("imvula iyana")
ELSE
    VEZA("ilanga liphumile")
QEDA UMA
QEDA INDALO
"""
    assert run(src) == ["imvula iyana"]


def test_zulu_try_catch_endtry_compound_runs():
    src = """# tongue: zu
QALA INDALO
ZAMA
    MEMEZELA x NJENGA 1 / 0
BAMBA iphutha
    VEZA("kubanjwe")
QEDA ZAMA
QEDA INDALO
"""
    assert run(src) == ["kubanjwe"]


def test_zulu_rite_define_invoke_return():
    src = """# tongue: zu
QALA INDALO
CHAZA ISIKO ukubusisa(igama)
    BUYISA "isibusiso ku " + igama
END RITE
BIZA ukubusisa("Umhlaba")
MEMEZELA umphumela NJENGA ukubusisa("Umhlaba")
VEZA(umphumela)
QEDA INDALO
"""
    assert run(src) == ["isibusiso ku Umhlaba"]


def test_zulu_breathe_life_into_and_loops():
    src = """# tongue: zu
QALA INDALO
MEMEZELA idolobha NJENGA "IGoli"
PHEFUMULA IMPILO PHAKATHI idolobha
MEMEZELA isamba NJENGA 0
MEMEZELA n NJENGA 1
WHILE n < 4 DO
    MEMEZELA isamba NJENGA isamba + n
    MEMEZELA n NJENGA n + 1
ENDWHILE
VEZA("{idolobha} {isamba}")
QEDA INDALO
"""
    assert run(src) == ["IGoli 6"]


def test_mixed_english_and_zulu():
    src = """# tongue: zu
QALA INDALO
DECLARE x AS 40 + 2
VEZA(x)
END CREATION
"""
    assert run(src) == ["42"]


def test_zulu_interpolation_speaks_the_tongue():
    src = """# tongue: zu
QALA INDALO
MEMEZELA igama NJENGA "mngane"
VEZA("Sawubona {igama}: {IQINISO KANYE IQINISO}")
QEDA INDALO
"""
    assert run(src) == ["Sawubona mngane: true"]


def test_zulu_break_and_continue():
    src = """# tongue: zu
QALA INDALO
MEMEZELA n NJENGA 0
WHILE IQINISO DO
    MEMEZELA n NJENGA n + 1
    IF n IS 3 THEN
        PHULA
    ENDIF
ENDWHILE
VEZA(n)
QEDA INDALO
"""
    assert run(src) == ["3"]


def test_fmt_renders_canonical_english_for_zulu():
    from godcode.cli import CanonicalFormatter

    src = """# tongue: zu
QALA INDALO
MEMEZELA x NJENGA 1
VEZA(x)
QEDA INDALO
"""
    out = CanonicalFormatter().format(parse_source(src))
    assert "DECLARE x AS 1" in out
    assert "REVEAL(x)" in out
    assert "QALA" not in out and "VEZA" not in out
    assert run(out) == ["1"]


def test_sandbox_run_speaks_zulu():
    from godcode.sandbox import SandboxPolicy, apply_policy

    interp = Interpreter()
    apply_policy(
        interp,
        SandboxPolicy(allow_read_paths=(), allow_write=False,
                      allow_network=False),
    )
    interp.run(parse_source(ZU_HELLO))
    assert interp.output == ["Sawubona, Umhlaba"]


def test_shipped_zulu_example_runs():
    src = (REPO / "examples" / "first_blessing_zu.god").read_text(
        encoding="utf-8")
    out = run(src)
    assert out[0] == "Sawubona, mngane wami."
    assert any("Imvula iyana" in line for line in out)


# ------------------------------------------------------- language server


ZU_DOC = (
    "# tongue: zu\n"
    "QALA INDALO\n"
    '  VEZA("Sawubona")\n'
    "  UMA x KHONA\n"
    '    VEZA("hamba")\n'
    "  QEDA UMA\n"
    "QEDA INDALO\n"
)


def test_lsp_tongue_table_zulu():
    table = lsp.tongue_table("zu")
    assert table["name"] == "isiZulu"
    assert table["aliases"]["VEZA"] == "REVEAL"
    assert table["compounds"][("QEDA", "UMA")] == "ENDIF"


def test_lsp_completion_zulu_doc_adds_tongue_words():
    items = lsp.completion_items(ZU_DOC)
    labels = [i["label"] for i in items]
    assert "VEZA (REVEAL)" in labels
    assert "UMA (IF)" in labels
    assert "QEDA UMA (ENDIF)" in labels
    assert "QEDA ZAMA (ENDTRY)" in labels
    assert "REVEAL" in labels  # English stays: mixed scrolls are welcome
    assert "QALA INDALO … QEDA INDALO" in labels


def test_lsp_snippet_items_carry_isizulu_name():
    items = lsp.tongue_snippet_items(lsp.tongue_table("zu"))
    assert len(items) == 3
    assert all("isiZulu" in i["detail"] for i in items)
    assert "UMA … KHONA … QEDA UMA" in [i["label"] for i in items]


def test_lsp_snippet_items_setswana_unchanged():
    items = lsp.tongue_snippet_items(lsp.tongue_table("tn"))
    assert len(items) == 3
    assert all("Setswana" in i["detail"] for i in items)


def test_lsp_hover_key_zulu_words():
    assert lsp.tongue_hover_key('VEZA("x")', 1, "zu") == "REVEAL"
    assert lsp.tongue_hover_key("QEDA UMA", 2, "zu") == "ENDIF"
    assert lsp.tongue_hover_key("QEDA UMA", 6, "zu") == "IF"
    assert lsp.tongue_hover_key("QALA INDALO", 1, "zu") == "BEGIN CREATION"


# ------------------------------------------------------------- VS Code files


def _grammar_patterns():
    grammar = json.loads(
        (REPO / "editors/vscode/syntaxes/godcode.tmLanguage.json")
        .read_text())
    patterns = {}
    for key, entry in grammar["repository"].items():
        if "match" not in entry:
            continue
        patterns[key] = re.compile(entry["match"].replace("(?i)", ""),
                                   re.IGNORECASE)
    return patterns


def test_vscode_grammar_paints_zulu_keywords():
    patterns = _grammar_patterns()
    assert patterns["keyword-spirit"].search("VEZA")
    assert patterns["keyword-spirit"].search("PROFETA")
    assert patterns["keyword-control"].search("UMA")
    assert patterns["keyword-control"].search("KHONA")
    assert patterns["keyword-control"].search("QEDA UMA")
    assert patterns["keyword-control"].search("QEDA ZAMA")
    assert patterns["keyword-control"].search("ZAMA")
    assert patterns["keyword-control"].search("BAMBA")
    assert patterns["keyword-control"].search("PHULA")
    assert patterns["keyword-control"].search("QHUBEKA")
    assert patterns["keyword-control"].search("BIZA")
    assert patterns["keyword-control"].search("BUYISA")
    assert patterns["keyword-control"].search("NGENISA")
    assert patterns["keyword-declaration"].search("MEMEZELA")
    assert patterns["keyword-declaration"].search("NJENGA")
    assert patterns["keyword-logic"].search("NGU")
    assert patterns["keyword-logic"].search("KANYE")
    assert patterns["keyword-logic"].search("NOMA")
    assert patterns["keyword-structure"].search("QALA INDALO")
    assert patterns["keyword-structure"].search("QEDA INDALO")
    assert patterns["keyword-structure"].search("CHAZA ISIKO")
    assert patterns["constant-language"].search("IQINISO")
    assert patterns["constant-language"].search("AMANGA")
    assert patterns["constant-language"].search("LUTHO")


def test_vscode_snippets_zulu_starters_run():
    import io
    from contextlib import redirect_stdout

    snippets = json.loads(
        (REPO / "editors/vscode/snippets/godcode.json").read_text())
    assert "Zulu creation block" in snippets
    assert "Zulu if" in snippets
    creation = snippets["Zulu creation block"]
    assert creation["prefix"] == "sawubona"
    body = "\n".join(creation["body"])
    body = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", body).replace("$0", "")
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().run(parse_source(body))
    assert "ascended in peace" in buf.getvalue()  # ENYUKA ends the run
    cond = snippets["Zulu if"]
    assert cond["prefix"] == "uma"
    cond_body = "\n".join(cond["body"])
    cond_body = re.sub(r"\$\{[12]:[^}]*\}", "izulu", cond_body)
    cond_body = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", cond_body)
    cond_body = cond_body.replace("$0", "")
    wrapped = "# tongue: zu\nQALA INDALO\n" + cond_body + "\nQEDA INDALO\n"
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter().run(parse_source(wrapped))
    assert "izulu" in buf.getvalue()
