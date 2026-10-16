import pytest


@pytest.fixture
def god_word():
    """Quote host text as a God Code word literal."""
    def quote(raw):
        return (
            '"'
            + raw.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("{", "{{")
            .replace("}", "}}")
            + '"'
        )

    return quote
