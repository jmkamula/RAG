"""
Ship 78'.e — regression test for _extraction_mode() env-var semantics.

Locks the interpretation of USE_CONSENSUS_EXTRACTION as
introduced in Ship 78'.b + hardened in Ship 78'.e. Pre-Ship-78
consumers used `os.getenv("USE_CONSENSUS_EXTRACTION") == "1"` to
detect "consensus mode" — under Ship 78' union default that check
became stale. The helper _extraction_mode() + is_consensus_active()
replace those reads.

Three modes:
  - "union" (default when unset / "1" / "true" / "yes" / "on")
  - "consensus_only" (or "only")
  - "critic_only" (or "0" / "false" / "no" / "off")
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.intake.extractor import _extraction_mode, is_consensus_active


def _with_env(value):
    """Return a context-manager-ish that sets USE_CONSENSUS_EXTRACTION."""
    class _Ctx:
        def __enter__(self):
            self.prev = os.environ.get("USE_CONSENSUS_EXTRACTION")
            if value is None:
                os.environ.pop("USE_CONSENSUS_EXTRACTION", None)
            else:
                os.environ["USE_CONSENSUS_EXTRACTION"] = value
        def __exit__(self, *_):
            if self.prev is None:
                os.environ.pop("USE_CONSENSUS_EXTRACTION", None)
            else:
                os.environ["USE_CONSENSUS_EXTRACTION"] = self.prev
    return _Ctx()


def test_unset_is_union():
    with _with_env(None):
        assert _extraction_mode() == "union"
        assert is_consensus_active() is True


def test_empty_string_is_union():
    with _with_env(""):
        assert _extraction_mode() == "union"
        assert is_consensus_active() is True


def test_legacy_1_is_union():
    """Pre-Ship-78 `USE_CONSENSUS_EXTRACTION=1` used to mean consensus-only.
    Under Ship 78' it maps to union — both paths run. Semantics
    preserved for anyone still setting =1: consensus IS active, just
    now alongside critic."""
    with _with_env("1"):
        assert _extraction_mode() == "union"
        assert is_consensus_active() is True


def test_true_yes_on_map_to_union():
    for v in ("true", "yes", "on", "TRUE", "Yes"):
        with _with_env(v):
            assert _extraction_mode() == "union", f"expected union for {v!r}"


def test_only_and_consensus_only():
    for v in ("only", "consensus_only", "ONLY", "Consensus_Only"):
        with _with_env(v):
            assert _extraction_mode() == "consensus_only"
            assert is_consensus_active() is True


def test_critic_only_variants():
    """`critic_only` + legacy false-ish values all mean consensus disabled."""
    for v in ("critic_only", "0", "false", "no", "off",
              "FALSE", "No", "Off", "Critic_Only"):
        with _with_env(v):
            assert _extraction_mode() == "critic_only", f"expected critic_only for {v!r}"
            assert is_consensus_active() is False


def test_unknown_value_is_union():
    """Unrecognised values fail-open to the default (union). Prevents
    hard failure on typo; production still gets both paths."""
    for v in ("banana", "consensus", "critic", "both", "1.0"):
        with _with_env(v):
            assert _extraction_mode() == "union", f"expected union for {v!r}"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
    print("OK — extraction_mode env-var semantics locked")
