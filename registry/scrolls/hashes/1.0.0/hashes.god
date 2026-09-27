# The Scroll of Hashes -- fingerprints of words, sealed signatures, and veils.
# Rites: FINGERPRINT, SIGN, VERIFY_SIGNATURE, VEIL, UNVEIL.

DEFINE RITE FINGERPRINT(word)
  RETURN SHA256(word)
END RITE

DEFINE RITE SIGN(message, key)
  RETURN HMAC(key, message)
END RITE

DEFINE RITE VERIFY_SIGNATURE(message, key, sig)
  RETURN SIGN(message, key) IS sig
END RITE

DEFINE RITE VEIL(word)
  RETURN BASE64_ENCODE(word)
END RITE

DEFINE RITE UNVEIL(veiled)
  RETURN BASE64_DECODE(veiled)
END RITE
