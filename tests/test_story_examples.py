"""The Market Day interactive story, told in English, Pidgin, and Igbo.

The reader makes three choices at the top of the scroll. These tests walk
every path through all three tellings under the sandbox and check that
the tellings agree: the same choices reach the same ending with the same
coins, whatever the tongue.
"""
import io
import itertools
import re
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from godcode.linter import lint_source
from godcode.sandbox import run_sandboxed

REPO = Path(__file__).resolve().parent.parent

# file, the three choice variables, (path, heart, buy) options, fate word,
# and the three ending titles in story order.
TELLINGS = {
    "market_day_story.god": (
        ("path_choice", "heart_choice", "buy_choice"),
        (("river", "road"), ("help", "hurry"), ("yams", "cloth")), "fate",
        ("The Blessed Road", "The Wise Trader", "The Long Walk")),
    "market_day_story_pg.god": (
        ("path_choice", "heart_choice", "buy_choice"),
        (("river", "road"), ("help", "rush"), ("yam", "cloth")), "fate",
        ("The Blessed Road", "The Sharp Trader", "The Long Waka")),
    "market_day_story_ig.god": (
        ("uzo_nhoro", "obi_nhoro", "ihe_nhoro"),
        (("osimiri", "uzo"), ("nyere", "oso"), ("ji", "akwa")), "chi",
        ("Ụzọ Ngọzi", "Onye Ahịa Maara Ihe", "Njem Dị Anya")),
}

COMBOS = list(itertools.product(range(2), repeat=3))


def _source(name):
    return (REPO / "examples" / name).read_text(encoding="utf-8")


def _with_choices(src, names, values):
    for name, value in zip(names, values):
        src, n = re.subn(rf'({name} (?:AS|BE|DỊKA) )"[^"]*"', rf'\1"{value}"', src)
        assert n == 1, name
    return src


def _tell(src):
    with redirect_stdout(io.StringIO()):
        return run_sandboxed(src)


def _ending(name, output):
    titles = TELLINGS[name][3]
    [line] = [line for line in output if any(t in line for t in titles)]
    index = next(i for i, t in enumerate(titles) if t in line)
    digits = re.findall(r"\d+", line)
    # Igbo says one coin in words: "otu mkpụrụ ego".
    coins = int(digits[-1]) if digits else (1 if "otu mkpụrụ ego" in line else None)
    return index, coins


def _expected(path, heart, buy):
    """The story's own arithmetic: 10 coins, +1 by the river, yams 6,
    cloth 9 or 5 for a helper; blessed and >= 5 coins, else >= 4."""
    coins = 10 + (1 if path == 0 else 0)
    blessed = heart == 0
    price = 6 if buy == 0 else (5 if blessed else 9)
    coins -= price
    ending = 0 if blessed and coins >= 5 else (1 if coins >= 4 else 2)
    return ending, coins


@pytest.mark.parametrize("name", TELLINGS)
def test_story_is_lint_clean(name):
    assert lint_source(_source(name), source_name=name) == []


@pytest.mark.parametrize("name", TELLINGS)
@pytest.mark.parametrize("combo", COMBOS)
def test_every_path_reaches_the_right_ending(name, combo):
    names, options, _, _ = TELLINGS[name]
    values = [opts[i] for opts, i in zip(options, combo)]
    output = _tell(_with_choices(_source(name), names, values))
    assert _ending(name, output) == _expected(*combo)
    assert len([line for line in output if line.startswith("  * ")]) == 3


@pytest.mark.parametrize("name", TELLINGS)
def test_fate_and_unknown_choices_still_tell_a_story(name):
    names, _, fate, titles = TELLINGS[name]
    for values in ([fate] * 3, ["somewhere", fate, fate]):
        output = _tell(_with_choices(_source(name), names, values))
        assert any(any(t in line for t in titles) for line in output)
    assert "(" in output[0]  # the gentle note about the unknown choice


def test_shipped_choices_agree_across_tellings():
    """As shipped, all three start by the river with a helping heart."""
    for name, (names, options, _, _) in TELLINGS.items():
        src = _source(name)
        for var, opts in zip(names[:2], options[:2]):
            assert re.search(rf'{var} (?:AS|BE|DỊKA) "{opts[0]}"', src), (name, var)
