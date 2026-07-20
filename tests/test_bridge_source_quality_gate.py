"""
Unit tests for rag/intake/xfw_proposer._bridge_worthy_check
— Ship 11'.b (2026-07-20) bridge source-quality gate.

Motivation from the Ship 10 HITL review:
17 of 49 rejected stage-1 findings (35%) were cross-framework
bridges propagated from weak source findings. The gate blocks
three failure modes:
  (a) bridge-of-bridge — an xfw source seeding another bridge
  (b) low-confidence sources amplifying noise
  (c) fragment sources (short excerpts, no MUST binding) —
      field-labels + bare section headers

See [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] for
the full 5-pattern taxonomy.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_bridge_source_quality_gate.py
"""
from __future__ import annotations

import sys

from rag.intake.xfw_proposer import (
    _BRIDGE_MIN_EXCERPT_CHARS,
    _bridge_worthy_check,
)


def _check(label: str, got, want) -> bool:
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}  got={got!r} want={want!r}")
    return ok


def test_positive_must_bound() -> int:
    """A MUST-bound source with any medium+ confidence is worthy
    regardless of excerpt length. The critic-verifier already
    picked the MUST — treat it as vetted."""
    print("\npositive: MUST-bound source with short excerpt still worthy")
    r = _bridge_worthy_check(
        inference_source="extracted",
        confidence="medium",
        checklist_item_id="item:A.5.15:policy_owner",
        excerpt="",  # even empty excerpt OK when MUST-bound
    )
    return 0 if _check("MUST-bound + medium", r, (True, "ok")) else 1


def test_positive_substantive_excerpt() -> int:
    """No MUST binding but long substantive excerpt — worthy."""
    print("\npositive: substantive excerpt without MUST is worthy")
    r = _bridge_worthy_check(
        inference_source="extracted",
        confidence="high",
        checklist_item_id=None,
        excerpt="The organisation shall implement RBAC controls at "
                "role-provisioning time with quarterly reviews.",
    )
    return 0 if _check("long excerpt + high conf", r, (True, "ok")) else 1


def test_negative_bridge_of_bridge() -> int:
    """No bridge-of-bridge cascade: a source with
    inference_source='xfw_bridge' can't seed further bridges."""
    print("\nnegative: bridge-of-bridge blocked")
    r = _bridge_worthy_check(
        inference_source="xfw_bridge",
        confidence="high",
        checklist_item_id="item:A.5.15:xyz",
        excerpt="Substantive excerpt content that would otherwise pass",
    )
    return 0 if _check("xfw_bridge source", r, (False, "source_is_bridge")) else 1


def test_negative_low_confidence() -> int:
    """Low confidence sources are dropped even when MUST-bound."""
    print("\nnegative: low confidence blocked")
    r = _bridge_worthy_check(
        inference_source="extracted",
        confidence="low",
        checklist_item_id="item:A.5.15:xyz",
        excerpt="Substantive excerpt content, but low confidence",
    )
    return 0 if _check("low conf", r, (False, "low_confidence:low")) else 1


def test_negative_missing_confidence() -> int:
    """A source with no confidence at all is treated as unset — drop."""
    print("\nnegative: missing confidence blocked")
    r = _bridge_worthy_check(
        inference_source="extracted",
        confidence=None,
        checklist_item_id="item:A.5.15:xyz",
        excerpt="Substantive excerpt content",
    )
    return 0 if _check("None conf", r, (False, "low_confidence:unset")) else 1


def test_negative_fragment_source() -> int:
    """Short excerpt AND no MUST binding = fragment. Drop.
    This catches the RoPA field-label pattern (Pattern 1 from
    Ship 11'.a) — 'Subprocessors' as a stand-alone quote."""
    print("\nnegative: fragment source (short + no MUST) blocked")
    r = _bridge_worthy_check(
        inference_source="extracted",
        confidence="medium",
        checklist_item_id=None,
        excerpt="Subprocessors",   # 13 chars, no MUST
    )
    return 0 if _check("fragment, no MUST",
                       r, (False, "fragment_source:13c_no_must")) else 1


def test_boundary_at_min_excerpt_chars() -> int:
    """Confirm the boundary at _BRIDGE_MIN_EXCERPT_CHARS.
    Excerpts just under fail; at-or-over pass (when no MUST)."""
    print(f"\nboundary: excerpt length threshold = {_BRIDGE_MIN_EXCERPT_CHARS}")
    fails = 0
    # Just under → drop
    just_under = "x" * (_BRIDGE_MIN_EXCERPT_CHARS - 1)
    r = _bridge_worthy_check(
        inference_source="extracted", confidence="medium",
        checklist_item_id=None, excerpt=just_under,
    )
    fails += 0 if _check(
        f"len={len(just_under)} (under threshold)",
        r, (False, f"fragment_source:{len(just_under)}c_no_must"),
    ) else 1
    # At threshold → pass
    at_threshold = "x" * _BRIDGE_MIN_EXCERPT_CHARS
    r = _bridge_worthy_check(
        inference_source="extracted", confidence="medium",
        checklist_item_id=None, excerpt=at_threshold,
    )
    fails += 0 if _check(
        f"len={len(at_threshold)} (at threshold)", r, (True, "ok"),
    ) else 1
    return fails


def test_ship10_reject_replay() -> int:
    """Replay the actual Ship 10 rejects that Pattern 4 identified.
    Each of these 4 source-shape signatures produced multiple bridge
    rejects in the Ship 10 HITL review; the gate should now suppress
    them all."""
    print("\nreplay: Ship 10 rejects that this gate targets")
    fails = 0

    # Case A — Pattern 1: field label "Subprocessors / Any third parties involved"
    # (from RoPA doc). Was source for 3 bridges → A.5.19/20/22.
    r = _bridge_worthy_check(
        inference_source="extracted", confidence="medium",
        checklist_item_id=None,
        excerpt="Subprocessors   Any third parties involved",
    )
    # ~40 chars — right at threshold. This particular excerpt is 44 chars
    # so it would pass length check but has no MUST. Actually 44 >= 40 so
    # it would PASS by our current gate. Let me verify by counting:
    # "Subprocessors   Any third parties involved" — count chars.
    # That's 42 chars — just over threshold. Gate lets it through.
    # This shows the gate is not perfect for Pattern 1 alone; Pattern 1
    # will need the content-shape filter from Ship 11'.c.
    fails += 0 if _check(
        "Pattern 1 label just over 40c — passes gate (needs Ship 11'.c)",
        r, (True, "ok"),
    ) else 1

    # Case B — Pattern 3: fingerprint fragment section header
    # "This procedure outlines how Arion Networks s.r.o." (49 chars but
    # fragment). Actually this is 49 chars long. The gate is agnostic to
    # semantic; it only checks LENGTH. This will pass unless we combine
    # with content-shape filter. Verify.
    r = _bridge_worthy_check(
        inference_source="extracted", confidence="medium",
        checklist_item_id=None,
        excerpt="This procedure outlines how Arion Networks s.r.o.",
    )
    fails += 0 if _check(
        "Pattern 3 sentence fragment — passes gate (needs Ship 11'.c)",
        r, (True, "ok"),
    ) else 1

    # Case C — The core Pattern 4 target: bridge-of-bridge.
    # None of the Ship 10 rejects actually had inference_source='xfw_bridge'
    # (that would require two hops), but the gate future-proofs against it.
    r = _bridge_worthy_check(
        inference_source="xfw_bridge", confidence="high",
        checklist_item_id="item:x", excerpt="substantive content here",
    )
    fails += 0 if _check(
        "Pattern 4 bridge-of-bridge blocked", r, (False, "source_is_bridge"),
    ) else 1

    # Case D — Real fragment: "obtains, records, and manages consent"
    # (37 chars, no MUST, verb-fragment mid-sentence). Fingerprint match
    # in Consent Management. Gate blocks — under 40 chars.
    r = _bridge_worthy_check(
        inference_source="extracted", confidence="medium",
        checklist_item_id=None,
        excerpt="obtains, records, and manages consent",
    )
    fails += 0 if _check(
        "Pattern 3 short fragment (<40c) blocked",
        r, (False, "fragment_source:37c_no_must"),
    ) else 1

    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/intake/xfw_proposer._bridge_worthy_check (Ship 11'.b)")
    print("─" * 70)
    fails = (
        test_positive_must_bound()
        + test_positive_substantive_excerpt()
        + test_negative_bridge_of_bridge()
        + test_negative_low_confidence()
        + test_negative_missing_confidence()
        + test_negative_fragment_source()
        + test_boundary_at_min_excerpt_chars()
        + test_ship10_reject_replay()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
