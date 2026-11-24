"""ANCHOR answers to the permission manifest.

ANCHOR persists a block to a local chain file, so persisting it is a
write like any other. Before the mending it was the one file-writing
power the manifest did not govern: a scroll under a locked manifest that
granted no write still wrote `anchors.chain` to its run directory. These
tests pin the mended behaviour, the binding rule that matches SEAL, and
the legacy freedom of an unguarded direct run.
"""
import os

import pytest

from godcode.chain import MemoryChainAdapter, SimulatedChainAdapter
from godcode.interpreter import Interpreter

LOCKED = """\
BEGIN CREATION
  DECLARE PERMISSION TO READ "data/"
  DECLARE PERMISSION TO WRITE "out/"
  DECLARE r AS ANCHOR("under a locked manifest")
  REVEAL(r["chain"])
  REVEAL(r["height"])
END CREATION
"""

GRANTS_THE_CHAIN = """\
BEGIN CREATION
  DECLARE PERMISSION TO WRITE "anchors.chain"
  DECLARE r AS ANCHOR("under a write grant over the chain")
  REVEAL(r["height"])
END CREATION
"""

BARE = """\
BEGIN CREATION
  DECLARE r AS ANCHOR("no manifest declared")
  REVEAL(r["height"])
END CREATION
"""


def _enforced_interp():
    """An interpreter set up the way a plain `godcode run` sets it up:
    manifest-enforced, with the real file-backed default adapters."""
    interp = Interpreter(log_path=None)
    interp.manifest_enforced = True
    return interp


def test_locked_manifest_writes_no_chain_file(tmp_path, monkeypatch):
    """The break, closed: a locked manifest granting no write over the
    chain leaves no anchors.chain on disk, and the receipt still returns."""
    monkeypatch.chdir(tmp_path)
    interp = _enforced_interp()
    interp.run_source(LOCKED)
    assert interp.output == ["simulated", "0"]      # the rite kept its meaning
    assert not (tmp_path / "anchors.chain").exists()  # ...but wrote nothing
    assert list(tmp_path.iterdir()) == []


def test_empty_enforced_manifest_writes_no_chain_file(tmp_path, monkeypatch):
    """Deny by default: an enforced run that declares nothing persists
    nothing, the same rule Finding 1 set for every other power."""
    monkeypatch.chdir(tmp_path)
    interp = _enforced_interp()
    interp.run_source(BARE)
    assert interp.output == ["0"]
    assert not (tmp_path / "anchors.chain").exists()


def test_write_grant_over_the_chain_persists_to_disk(tmp_path, monkeypatch):
    """The control: a scroll that declares write over the chain file
    persists to disk, so the power still works when it is declared."""
    monkeypatch.chdir(tmp_path)
    interp = _enforced_interp()
    interp.run_source(GRANTS_THE_CHAIN)
    assert interp.output == ["0"]
    assert (tmp_path / "anchors.chain").exists()
    blocks = SimulatedChainAdapter(tmp_path / "anchors.chain").read_all()
    assert len(blocks) == 1


def test_unguarded_direct_run_keeps_legacy_reach(tmp_path, monkeypatch):
    """A direct run_source with no manifest and no enforcement installs
    no guard, so ANCHOR persists as before. The mending binds only where
    a manifest binds, exactly as SEAL does."""
    monkeypatch.chdir(tmp_path)
    interp = Interpreter(log_path=None)  # manifest_enforced stays False
    interp.run_source(BARE)
    assert (tmp_path / "anchors.chain").exists()


def test_repeated_anchors_share_one_memory_chain(tmp_path, monkeypatch):
    """When degraded to memory, repeated anchors in the run share one
    chain, so heights still increase and no disk file appears."""
    monkeypatch.chdir(tmp_path)
    interp = _enforced_interp()
    interp.run_source(
        "BEGIN CREATION\n"
        '  DECLARE PERMISSION TO READ "data/"\n'
        '  DECLARE a AS ANCHOR("first")\n'
        '  DECLARE b AS ANCHOR("second")\n'
        '  REVEAL(a["height"])\n'
        '  REVEAL(b["height"])\n'
        "END CREATION\n"
    )
    assert interp.output == ["0", "1"]
    assert not (tmp_path / "anchors.chain").exists()
    assert isinstance(interp.chain_adapters["simulated"], MemoryChainAdapter)
