"""Tests for the hashes stdlib: SHA-256, HMAC, and base64 (godcode.stdlib_hashes).

Every test runs real God Code source through the real pipeline
(Lexer -> Parser -> Interpreter) and asserts on revealed output, in the
style of tests/test_stdlib_vault.py. All test vectors are standard,
public, well-known values.
"""

import os

import pytest

from godcode.errors import GodRuntimeError
from godcode.interpreter import Interpreter
from godcode.lexer import Lexer
from godcode.parser import Parser
from godcode.sandbox import SandboxPolicy, apply_policy
from godcode import stdlib_hashes


def run(src, interp=None):
    """Parse src, run it, return the revealed lines."""
    prog = Parser(Lexer(src).lex()).parse()
    interp = interp if interp is not None else Interpreter()
    interp.run(prog)
    return interp.output


def run_err(src):
    """Run src and return the GodRuntimeError it raises."""
    prog = Parser(Lexer(src).lex()).parse()
    interp = Interpreter()
    with pytest.raises(GodRuntimeError) as excinfo:
        interp.run(prog)
    return excinfo.value


# ------------------------------------------------------------------ SHA-256


SHA256_ABC = (
    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
)
SHA256_EMPTY = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)


def test_sha256_of_abc():
    assert run('REVEAL(SHA256("abc"))') == [SHA256_ABC]


def test_sha256_empty_word():
    assert run('REVEAL(SHA256(""))') == [SHA256_EMPTY]


def test_sha256_returns_64_hex_chars():
    out = run('REVEAL(SHA256("grace upon grace"))')[0]
    assert len(out) == 64
    int(out, 16)  # every char is a hex digit


def test_sha256_deterministic():
    src = (
        'BEGIN CREATION\n'
        '  DECLARE a AS SHA256("manna")\n'
        '  DECLARE b AS SHA256("manna")\n'
        '  REVEAL(a IS b)\n'
        'END CREATION'
    )
    assert run(src) == ["true"]


def test_sha256_avalanche():
    src = (
        'BEGIN CREATION\n'
        '  REVEAL(SHA256("manna") IS SHA256("mannb"))\n'
        'END CREATION'
    )
    assert run(src) == ["false"]


def test_sha256_number_and_truth():
    out = run('REVEAL(SHA256(40) + " " + SHA256(TRUE))')
    assert len(out[0].split(" ")) == 2


def test_sha256_symbol():
    out = run('REVEAL(SHA256(peace))')
    assert out == run('REVEAL(SHA256("peace"))')


def test_sha256_refuses_list():
    err = run_err('REVEAL(SHA256([1, 2]))')
    assert "SHA256 can fingerprint" in str(err)
    assert "list" in str(err)


def test_sha256_refuses_map():
    err = run_err('REVEAL(SHA256(JSON_PARSE("{{\\"a\\": 1}}")))')
    assert "map" in str(err)


def test_sha256_arity():
    err = run_err('REVEAL(SHA256("a", "b"))')
    assert "SHA256" in str(err)


# --------------------------------------------------------------------- HMAC


HMAC_KNOWN = (
    "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8"
)


def test_hmac_known_vector():
    src = 'REVEAL(HMAC("key", "The quick brown fox jumps over the lazy dog"))'
    assert run(src) == [HMAC_KNOWN]


def test_hmac_returns_64_hex_chars():
    out = run('REVEAL(HMAC("salt", "word"))')[0]
    assert len(out) == 64
    int(out, 16)


def test_hmac_key_matters():
    src = (
        'BEGIN CREATION\n'
        '  REVEAL(HMAC("salt", "word") IS HMAC("pepper", "word"))\n'
        'END CREATION'
    )
    assert run(src) == ["false"]


def test_hmac_message_matters():
    src = (
        'BEGIN CREATION\n'
        '  REVEAL(HMAC("salt", "one") IS HMAC("salt", "two"))\n'
        'END CREATION'
    )
    assert run(src) == ["false"]


def test_hmac_deterministic():
    src = (
        'BEGIN CREATION\n'
        '  REVEAL(HMAC("k", "m") IS HMAC("k", "m"))\n'
        'END CREATION'
    )
    assert run(src) == ["true"]


def test_hmac_arity():
    err = run_err('REVEAL(HMAC("only-key"))')
    assert "HMAC" in str(err)


def test_hmac_refuses_list_key():
    err = run_err('REVEAL(HMAC(["k"], "m"))')
    assert "HMAC can fingerprint" in str(err)


# -------------------------------------------------------------------- base64


def test_base64_encode():
    assert run('REVEAL(BASE64_ENCODE("Hello"))') == ["SGVsbG8="]


def test_base64_decode():
    assert run('REVEAL(BASE64_DECODE("SGVsbG8="))') == ["Hello"]


def test_base64_round_trip():
    src = 'REVEAL(BASE64_DECODE(BASE64_ENCODE("grace upon grace")))'
    assert run(src) == ["grace upon grace"]


def test_base64_unicode_round_trip():
    src = 'REVEAL(BASE64_DECODE(BASE64_ENCODE("Shalom שלום")))'
    assert run(src) == ["Shalom שלום"]


def test_base64_decode_rejects_garbage():
    err = run_err('REVEAL(BASE64_DECODE("!!! not base64 !!!"))')
    assert "veil it cannot lift" in str(err)


def test_base64_decode_rejects_number():
    err = run_err("REVEAL(BASE64_DECODE(42))")
    assert "veiled word" in str(err)


def test_base64_encode_arity():
    err = run_err('REVEAL(BASE64_ENCODE("a", "b"))')
    assert "BASE64_ENCODE" in str(err)


# ------------------------------------------------------- sandbox + purity


def test_hashes_need_no_sandbox_grant():
    """The hash builtins are pure: they run inside the strictest sandbox."""
    interp = Interpreter()
    apply_policy(
        interp,
        SandboxPolicy(allow_read_paths=(), allow_write=False, allow_network=False),
    )
    src = (
        'BEGIN CREATION\n'
        '  REVEAL(SHA256("manna"))\n'
        '  REVEAL(HMAC("k", "m"))\n'
        '  REVEAL(BASE64_DECODE(BASE64_ENCODE("word")))\n'
        'END CREATION'
    )
    prog = Parser(Lexer(src).lex()).parse()
    interp.run(prog)
    assert len(interp.output) == 3


def test_hashes_registered_at_startup():
    interp = Interpreter()
    for name in ("SHA256", "HMAC", "BASE64_ENCODE", "BASE64_DECODE"):
        assert name in interp._builtins


def test_register_is_idempotent():
    interp = Interpreter()
    before = dict(interp._builtins)
    stdlib_hashes.register(interp)
    assert interp._builtins.keys() == before.keys()


# ------------------------------------------------- the hashes registry scroll


def _hashes_scroll_entry():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    return root / "registry" / "scrolls" / "hashes" / "1.0.0" / "hashes.god"


def test_hashes_scroll_exists_and_runs():
    from godcode import run_file

    result = run_file(_hashes_scroll_entry())
    assert result.ok


def test_hashes_scroll_rites():
    from godcode import run_source

    src = (
        'BEGIN CREATION\n'
        f'  IMPORT "{_hashes_scroll_entry()}"\n'
        '  REVEAL(FINGERPRINT("abc"))\n'
        '  REVEAL(SIGN("msg", "key"))\n'
        '  REVEAL(VERIFY_SIGNATURE("msg", "key", SIGN("msg", "key")))\n'
        '  REVEAL(VERIFY_SIGNATURE("msg", "wrong", SIGN("msg", "key")))\n'
        '  REVEAL(UNVEIL(VEIL("covered")))\n'
        'END CREATION'
    )
    result = run_source(src)
    assert result.ok, result.error
    lines = result.output.split("\n")
    assert lines[0] == SHA256_ABC
    assert lines[1] == run('REVEAL(HMAC("key", "msg"))')[0]
    assert lines[2] == "true"
    assert lines[3] == "false"
    assert lines[4] == "covered"
