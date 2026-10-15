"""Tests for the third and fourth tongues: Igbo (``ig``) and Nigerian
Pidgin (``pg``, also ``pcm``).

Every test runs real Igbo or Pidgin source through the real pipeline
(lexer, interpreter, formatter, sandbox, language server, VS Code files,
the shipped examples) and asserts on what comes out.
"""

import io
import json
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from godcode import lsp
from godcode.cli import CanonicalFormatter
from godcode.interpreter import Interpreter
from godcode.lexer import KEYWORDS, Lexer
from godcode.sandbox import run_sandboxed
from godcode.tokens import TokenType
from godcode.tongues import known_tongues, parse_source, resolve

REPO = Path(__file__).resolve().parent.parent


def run(src):
    """Parse src (honouring any tongue pragma), run it, return output lines."""
    interp = Interpreter(log_path=None)
    with redirect_stdout(io.StringIO()):
        interp.run(parse_source(src))
    return interp.output


def kinds(src):
    return [t.type for t in Lexer(src).lex()
            if t.type not in (TokenType.NEWLINE, TokenType.EOF)]


# ------------------------------------------------------- pragma and tables


def test_known_tongues_lists_igbo_and_pidgin():
    tongues = known_tongues()
    assert tongues["ig"] == "Igbo"
    assert tongues["pg"] == "Nigerian Pidgin"
    assert tongues["tn"] == "Setswana" and tongues["zu"] == "isiZulu"


def test_pcm_is_the_standard_code_for_pidgin():
    assert resolve("pcm") is resolve("pg")
    assert run('# tongue: pcm\nOYA KREASHON\nSHOW("abeg")\nFINISH KREASHON\n') == ["abeg"]


@pytest.mark.parametrize("code", ["ig", "pg"])
def test_every_word_maps_to_a_real_keyword(code):
    table = resolve(code)
    assert set(table["aliases"].values()) <= set(KEYWORDS)
    assert set(table["compounds"].values()) <= set(KEYWORDS)
    assert {"ENDIF", "ENDTRY"} <= set(table["compounds"].values())


def test_igbo_covers_the_setswana_keyword_set():
    """Igbo is a full tongue, like Setswana and isiZulu."""
    ig = resolve("ig")
    words = set(ig["aliases"].values()) | set(ig["compounds"].values())
    assert set(resolve("tn")["aliases"].values()) <= words


def test_pidgin_leaves_shared_english_words_alone():
    """Words Pidgin shares with English stay English, not aliases."""
    pg = resolve("pg")["aliases"]
    for shared in ("IF", "TRY", "AND", "IN", "DO", "BLESS", "LIFE", "TRUE",
                   "FALSE", "RETURN", "PROPHESY"):
        assert shared not in pg


# ------------------------------------------------------------------ lexing


def test_igbo_dotted_and_plain_spellings_both_speak():
    dotted = '# tongue: ig\nBIDO OKIKE\nKWUSAA x DỊKA ỤGHA\nGOSI(x)\nNJEDEBE OKIKE\n'
    plain = '# tongue: ig\nBIDO OKIKE\nKWUSAA x DIKA UGHA\nGOSI(x)\nNJEDEBE OKIKE\n'
    assert kinds(dotted) == kinds(plain)
    assert run(dotted) == run(plain) == ["false"]


def test_igbo_two_word_phrases():
    src = "# tongue: ig\nỌ BỤRỤ x MGBE AHỤ\nNJEDEBE MA\nNJEDEBE NWAA\nO BURU\n"
    assert kinds(src) == [TokenType.IF, TokenType.IDENT, TokenType.THEN,
                          TokenType.ENDIF, TokenType.ENDTRY, TokenType.IF]


def test_pidgin_closers_join_an_english_keyword():
    src = "# tongue: pg\nFINISH IF\nFINISH TRY\nFINISH KREASHON\nFINISH JOB\n"
    assert kinds(src) == [TokenType.ENDIF, TokenType.ENDTRY,
                          TokenType.END, TokenType.CREATION,
                          TokenType.END, TokenType.RITE]


def test_phrases_need_one_line_and_side_by_side_words():
    assert kinds("# tongue: pg\nFINISH\nIF\n") == [TokenType.END, TokenType.IF]
    assert kinds("# tongue: pg\nFINISH(IF") == [TokenType.END, TokenType.LPAREN,
                                                 TokenType.IF]


def test_without_pragma_the_words_are_names():
    assert kinds("SHOW TALK NJEDEBE GOSI") == [TokenType.IDENT] * 4
    assert kinds("FINISH IF") == [TokenType.IDENT, TokenType.IF]


def test_english_and_older_tongues_are_unchanged():
    assert kinds("# tongue: tn\nFEDISA FA\nFEDISA LEKA\n") == [TokenType.ENDIF,
                                                               TokenType.ENDTRY]
    assert kinds("# tongue: zu\nQEDA UMA\n") == [TokenType.ENDIF]
    assert kinds("END CREATION\nEND RITE\n") == [TokenType.END, TokenType.CREATION,
                                                 TokenType.END, TokenType.RITE]


# ----------------------------------------------------------------- running


def test_igbo_runs_conditions_rites_loops_and_try():
    src = """# tongue: ig
BIDO OKIKE
KỌWAA EMUME ekele(onye)
    WEGHACHI "Ndewo, " + onye
NJEDEBE EMUME
GOSI(KPỌỌ ekele("Ada"))
MA 2 BỤ 2 MGBE GOSI(EZIOKWU)
Ọ BỤRỤ MBA (1 BỤ 2) NA EZIOKWU MGBE AHỤ
    GOSI("ọ dị iche")
NJEDEBE MA
FOR n IN RANGE(5)
    MA n BỤ 1 MGBE GABA
    MA n BỤ 3 MGBE KWỤSỊ
    GOSI(n)
ENDFOR
NWAA
    KWUSAA x DỊKA 1 / 0
JIDE
    GOSI("jidere")
NJEDEBE NWAA
NJEDEBE OKIKE
"""
    assert run(src) == ["Ndewo, Ada", "true", "ọ dị iche", "0", "2", "jidere"]


def test_pidgin_runs_conditions_rites_loops_and_try():
    src = """# tongue: pg
OYA KREASHON
ARRANGE JOB greet(who)
    RETURN "How far, " + who
FINISH JOB
SHOW(CALL greet("Emeka"))
IF 1 NA 2 ABI NO FALSE DEN SHOW("true talk")
TALK n BE 0
WHILE n < 5 DO
    TALK n BE n + 1
    IF n NA 2 DEN MOVE
    IF n NA 4 DEN STOP
    SHOW(n)
ENDWHILE
TRY
    TALK x BE 1 / 0
HOLD
    SHOW("wahala")
FINISH TRY
COMOT
FINISH KREASHON
"""
    assert run(src) == ["How far, Emeka", "true talk", "1", "3", "wahala"]


def test_interpolation_speaks_the_tongue():
    assert run('# tongue: pg\nOYA KREASHON\nSHOW("{1 NA 1}")\nFINISH KREASHON\n') == ["true"]
    assert run('# tongue: ig\nBIDO OKIKE\nGOSI("{1 BU 1}")\nNJEDEBE OKIKE\n') == ["true"]


def test_fmt_renders_canonical_english():
    src = (REPO / "examples" / "first_blessing_pg.god").read_text(encoding="utf-8")
    out = CanonicalFormatter().format(parse_source(src))
    assert out.startswith("BEGIN CREATION\n")
    assert 'REVEAL("How far, {name}?")' in out
    assert "ENDIF" in out and "ENDTRY" in out and "OYA" not in out


@pytest.mark.parametrize("name, first", [
    ("first_blessing_ig.god", "Ndewo, enyi m."),
    ("first_blessing_pg.god", "How far, my padi?"),
])
def test_shipped_examples_run_in_the_sandbox(name, first):
    src = (REPO / "examples" / name).read_text(encoding="utf-8")
    with redirect_stdout(io.StringIO()):
        output = run_sandboxed(src)
    assert output[0] == first
    assert len(output) == 5


# ------------------------------------------------------------- the editors


@pytest.mark.parametrize("code, word, canonical", [
    ("ig", "GOSI", "REVEAL"),
    ("ig", "KPỌỌ", "INVOKE"),
    ("pg", "SHOW", "REVEAL"),
])
def test_lsp_offers_the_tongue_words(code, word, canonical):
    items = lsp.completion_items(f"# tongue: {code}\n")
    labels = {item["label"] for item in items}
    assert f"{word} ({canonical})" in labels
    assert lsp.tongue_hover_key(f"{word}(x)", 1, code) == canonical


def test_lsp_snippets_travel_with_each_tongue():
    ig = lsp.tongue_snippet_items(lsp.tongue_table("ig"))
    pg = lsp.tongue_snippet_items(lsp.tongue_table("pg"))
    assert any("NJEDEBE MA" in item["insertText"] for item in ig)
    assert any("FINISH IF" in item["insertText"] for item in pg)
    assert all("(Igbo)" in item["detail"] for item in ig)


def _grammar_patterns():
    grammar = json.loads(
        (REPO / "editors/vscode/syntaxes/godcode.tmLanguage.json").read_text(encoding="utf-8"))
    return {key: re.compile(entry["match"].replace("(?i)", ""), re.IGNORECASE)
            for key, entry in grammar["repository"].items() if "match" in entry}


def test_vscode_grammar_paints_igbo_and_pidgin():
    p = _grammar_patterns()
    for word in ("GOSI", "TỤGHARỊA", "TUGHARIA", "SHOW", "COMOT"):
        assert p["keyword-spirit"].search(word), word
    for word in ("NJEDEBE MA", "MGBE AHỤ", "Ọ BỤRỤ", "NWAA", "FINISH IF", "DEN", "HOLD"):
        assert p["keyword-control"].search(word), word
    for word in ("BIDO OKIKE", "NJEDEBE OKIKE", "OYA KREASHON", "FINISH JOB"):
        assert p["keyword-structure"].search(word), word
    assert p["keyword-declaration"].search("KWUSAA")
    assert p["keyword-declaration"].search("TALK")
    assert p["constant-language"].search("EZIOKWU")


def _expand(body):
    text = "\n".join(body)
    text = re.sub(r"\$\{\d+:([^}]*)\}", r"\1", text)
    return text.replace("$0", "")


@pytest.mark.parametrize("block, cond, code, opener, closer", [
    ("Igbo creation block", "Igbo if", "ig", "BIDO OKIKE", "NJEDEBE OKIKE"),
    ("Pidgin creation block", "Pidgin if", "pg", "OYA KREASHON", "FINISH KREASHON"),
])
def test_vscode_starter_snippets_run(block, cond, code, opener, closer):
    snippets = json.loads(
        (REPO / "editors/vscode/snippets/godcode.json").read_text(encoding="utf-8"))
    buf = io.StringIO()
    with redirect_stdout(buf):
        Interpreter(log_path=None).run(parse_source(_expand(snippets[block]["body"])))
    assert "ascended in peace" in buf.getvalue()
    cond_body = re.sub(r"\$\{[12]:[^}]*\}", '"same"', "\n".join(snippets[cond]["body"]))
    wrapped = f"# tongue: {code}\n{opener}\n{_expand([cond_body])}\n{closer}\n"
    assert run(wrapped) == ["eluigwe" if code == "ig" else "heaven"]
