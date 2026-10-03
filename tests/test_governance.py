"""The governance documents stay complete, linked, and house-styled.

GOVERNANCE.md names who keeps God Code and who decides what enters it.
These tests keep the document present, cross-linked from the README and
CONTRIBUTING, and faithful to the house rules: no em dashes between
sentences, no version numbers in anything a human reads.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOVERNANCE = ROOT / "GOVERNANCE.md"
README = ROOT / "README.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"

EXPECTED_LINKS = [
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "docs/VERSIONING.md",
    "docs/TONGUES.md",
]


def test_governance_document_exists():
    assert GOVERNANCE.is_file(), "GOVERNANCE.md is missing from the repo root"


def test_governance_links_the_other_documents():
    text = GOVERNANCE.read_text(encoding="utf-8")
    missing = [doc for doc in EXPECTED_LINKS if doc not in text]
    assert not missing, f"GOVERNANCE.md does not mention: {missing}"


def test_governance_names_the_keeper_and_their_holdings():
    text = GOVERNANCE.read_text(encoding="utf-8")
    assert "Alakanani Itireleng" in text
    for word in ("brand", "direction", "home"):
        assert word in text.lower(), f"keeper holdings should mention '{word}'"


def test_governance_follows_the_house_style():
    text = GOVERNANCE.read_text(encoding="utf-8")
    assert "—" not in text, "em dashes are not used in user-facing text"
    for pattern in (r"\bv\d+\b", r"version \d", r"v2\.0", r"v3\.0", r"v4\.0", r"v5\.0"):
        assert not re.search(pattern, text, re.IGNORECASE), (
            f"governance prose carries a version label ({pattern})"
        )


def test_readme_points_at_governance():
    text = README.read_text(encoding="utf-8")
    assert "GOVERNANCE.md" in text, "README should point contributors at GOVERNANCE.md"


def test_contributing_points_at_governance():
    text = CONTRIBUTING.read_text(encoding="utf-8")
    assert "GOVERNANCE.md" in text, "CONTRIBUTING should point builders at GOVERNANCE.md"
