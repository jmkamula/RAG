"""
Unit tests for rag/posture/fulfilment_engine.py — the composition engine.

Standalone script. Each test returns (ok, message). main() prints PASS/FAIL
and returns exit code 0 iff all pass. The engine is driven by in-memory
SpecDescriptor fixtures and mock leaf evaluators — no Neo4j or Postgres.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_fulfilment_engine.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.posture.applies_when import EvalContext
from rag.posture.fulfilment_engine import (
    Edge,
    LeafSpec,
    LeafVerdict,
    SpecDescriptor,
    evaluate_control,
    not_yet_implemented_leaf_evaluator,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ec(**overrides) -> EvalContext:
    facts = {
        "uses_cloud_services":  True,
        "public_authority":     False,
        "high_risk_processing": False,
        "sector":               "technology",
    }
    facts.update(overrides.get("facts", {}))
    se = overrides.get("supply_exists_fn", lambda t: False)
    sc = overrides.get("supply_count_fn",  lambda t: 0)
    return EvalContext(facts=facts, supply_exists_fn=se, supply_count_fn=sc)


def _make_satisfying_evaluator(satisfies: dict[str, bool], fresh: dict[str, bool] | None = None):
    """Build a leaf_evaluator that returns verdicts based on per-leaf-id maps."""
    fresh = fresh or {}
    def evaluator(leaf: LeafSpec, ctx: EvalContext) -> LeafVerdict:
        ok = satisfies.get(leaf.leaf_id, False)
        is_fresh = fresh.get(leaf.leaf_id, True)
        return LeafVerdict(
            leaf_id=leaf.leaf_id,
            role="",
            evidence_type=leaf.evidence_type,
            satisfied=ok,
            fresh=is_fresh,
            reason="ok" if ok else "missing",
            items_recognised=leaf.must_items if ok else [],
            items_unrecognised=[] if ok else list(leaf.must_items),
        )
    return evaluator


def _leaf(name: str, type_: str = "policy", must=None) -> LeafSpec:
    return LeafSpec(
        leaf_id=name,
        evidence_type=type_,
        must_items=must or [f"{name}-item-1", f"{name}-item-2"],
        title=name,
    )


# ── curation_status routing ───────────────────────────────────────────────────

def test_uncurated_returns_UNKNOWN():
    spec = SpecDescriptor(spec_id="s", op="ALL", curation_status="uncurated", control_id="c")
    v = evaluate_control(spec, not_yet_implemented_leaf_evaluator, _ec())
    if v.posture != "UNKNOWN":
        return False, f"expected UNKNOWN, got {v.posture}"
    if not v.applies:
        return False, "applies should be True (the spec applies, we just don't know what it requires)"
    return True, "uncurated → UNKNOWN, applies=True"

def test_deferred_to_findings_returns_deferred():
    spec = SpecDescriptor(spec_id="s", op="ALL", curation_status="deferred_to_findings", control_id="c")
    v = evaluate_control(spec, not_yet_implemented_leaf_evaluator, _ec())
    if v.posture != "deferred":
        return False, f"expected deferred, got {v.posture}"
    return True, "deferred_to_findings → deferred"

def test_explicit_empty_returns_Comply():
    spec = SpecDescriptor(spec_id="s", op="ALL", curation_status="explicit_empty", control_id="c")
    v = evaluate_control(spec, not_yet_implemented_leaf_evaluator, _ec())
    if v.posture != "Comply":
        return False, f"expected Comply, got {v.posture}"
    return True, "explicit_empty → Comply (intentional decision)"


# ── ALL/ANY/AT_LEAST_N composition ────────────────────────────────────────────

def test_ALL_all_satisfied_is_Comply():
    leaves = [_leaf("L1"), _leaf("L2")]
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        children=[Edge(role="r1", applies_when=None, target=leaves[0]),
                  Edge(role="r2", applies_when=None, target=leaves[1])],
    )
    ev = _make_satisfying_evaluator({"L1": True, "L2": True})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "Comply":
        return False, f"expected Comply, got {v.posture}"
    if v.gap_list:
        return False, f"expected no gaps, got {v.gap_list}"
    return True, "ALL with both satisfied → Comply"

def test_ALL_one_missing_is_OFI():
    leaves = [_leaf("L1"), _leaf("L2")]
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        children=[Edge(role="r1", applies_when=None, target=leaves[0]),
                  Edge(role="r2", applies_when=None, target=leaves[1])],
    )
    ev = _make_satisfying_evaluator({"L1": True, "L2": False})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "OFI":
        return False, f"expected OFI, got {v.posture}"
    if not v.gap_list:
        return False, "expected at least one gap"
    return True, f"ALL with 1/2 satisfied → OFI ({len(v.gap_list)} gaps)"

def test_ANY_one_satisfied_is_Comply():
    leaves = [_leaf("L1"), _leaf("L2")]
    spec = SpecDescriptor(
        spec_id="s", op="ANY", curation_status="curated", control_id="c",
        children=[Edge(role="r1", applies_when=None, target=leaves[0]),
                  Edge(role="r2", applies_when=None, target=leaves[1])],
    )
    ev = _make_satisfying_evaluator({"L1": False, "L2": True})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "Comply":
        return False, f"expected Comply, got {v.posture}"
    return True, "ANY with 1/2 satisfied → Comply"

def test_ANY_none_satisfied_is_OFI():
    leaves = [_leaf("L1"), _leaf("L2")]
    spec = SpecDescriptor(
        spec_id="s", op="ANY", curation_status="curated", control_id="c",
        children=[Edge(role="r1", applies_when=None, target=leaves[0]),
                  Edge(role="r2", applies_when=None, target=leaves[1])],
    )
    ev = _make_satisfying_evaluator({"L1": False, "L2": False})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "OFI":
        return False, f"expected OFI, got {v.posture}"
    return True, "ANY with 0/2 satisfied → OFI"

def test_AT_LEAST_N_threshold():
    leaves = [_leaf("L1"), _leaf("L2"), _leaf("L3")]
    spec = SpecDescriptor(
        spec_id="s", op="AT_LEAST_N", n=2, curation_status="curated", control_id="c",
        children=[Edge(role="r", applies_when=None, target=leaves[i]) for i in range(3)],
    )
    # 2 of 3 satisfied — meets threshold
    ev = _make_satisfying_evaluator({"L1": True, "L2": True, "L3": False})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "Comply":
        return False, f"2/3 should meet AT_LEAST_2, got {v.posture}"
    # 1 of 3 — below
    ev2 = _make_satisfying_evaluator({"L1": True, "L2": False, "L3": False})
    v2 = evaluate_control(spec, ev2, _ec())
    if v2.posture != "OFI":
        return False, f"1/3 should fail AT_LEAST_2, got {v2.posture}"
    return True, "AT_LEAST_N respects threshold"


# ── applies_when at spec level ────────────────────────────────────────────────

def test_spec_level_applies_when_false_is_NotApplicable():
    leaf = _leaf("L")
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        applies_when='fact("public_authority")',  # False for our tenant
        children=[Edge(role="r", applies_when=None, target=leaf)],
    )
    ev = _make_satisfying_evaluator({})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "NotApplicable":
        return False, f"expected NotApplicable, got {v.posture}"
    if v.applies:
        return False, "applies should be False"
    if v.leaves:
        return False, "no leaves should be evaluated when spec doesn't apply"
    return True, "spec-level applies_when=False → NotApplicable, no leaves walked"


def test_spec_level_applies_when_true_does_walk():
    leaf = _leaf("L")
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        applies_when='fact("uses_cloud_services")',  # True for our tenant
        children=[Edge(role="r", applies_when=None, target=leaf)],
    )
    ev = _make_satisfying_evaluator({"L": True})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "Comply":
        return False, f"expected Comply, got {v.posture}"
    if not v.applies:
        return False, "applies should be True"
    return True, "spec-level applies_when=True walks the tree"


# ── Edge-level applies_when ───────────────────────────────────────────────────

def test_edge_level_applies_when_false_skips_leaf():
    # Two leaves, second gated off — should NOT be a gap, and should not block
    # the ALL from being Comply if the only un-gated leaf is satisfied.
    leaves = [_leaf("L1"), _leaf("L2")]
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        children=[
            Edge(role="r1", applies_when=None, target=leaves[0]),
            Edge(role="r2", applies_when='fact("public_authority")', target=leaves[1]),
        ],
    )
    ev = _make_satisfying_evaluator({"L1": True})  # L2 not satisfied — but gated off
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "Comply":
        return False, f"L2 should be gated off and ignored — expected Comply, got {v.posture}"
    if any("L2" in g for g in v.gap_list):
        return False, "L2 should not appear in gap list"
    return True, "edge applies_when=False makes the leaf invisible"


# ── Nested specs ──────────────────────────────────────────────────────────────

def test_nested_spec_child_rolls_up():
    # Outer ALL containing one leaf AND one nested ANY (with 1/2 satisfied → Comply)
    inner_leaves = [_leaf("inner1"), _leaf("inner2")]
    inner_spec = SpecDescriptor(
        spec_id="s.inner", op="ANY", curation_status="curated", control_id="c.inner",
        children=[Edge(role="ir", applies_when=None, target=inner_leaves[i]) for i in range(2)],
    )
    outer_leaf = _leaf("outer1")
    outer = SpecDescriptor(
        spec_id="s.outer", op="ALL", curation_status="curated", control_id="c.outer",
        children=[
            Edge(role="or", applies_when=None, target=outer_leaf),
            Edge(role="branch", applies_when=None, target=inner_spec),
        ],
    )
    ev = _make_satisfying_evaluator({"outer1": True, "inner1": False, "inner2": True})
    v = evaluate_control(outer, ev, _ec())
    if v.posture != "Comply":
        return False, f"outer should be Comply (outer1 satisfied + inner ANY-1/2 = Comply); got {v.posture}"
    return True, "nested ANY contributes a Comply branch to the outer ALL"


# ── Empty after applicability ─────────────────────────────────────────────────

def test_empty_children_after_gates_is_Comply():
    leaf = _leaf("L")
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        children=[Edge(role="r", applies_when='fact("public_authority")', target=leaf)],
    )
    ev = _make_satisfying_evaluator({})
    v = evaluate_control(spec, ev, _ec())
    # The only child was gated off — nothing left to fulfil at this moment.
    # This is the defensible Comply branch (vs explicit_empty which is the
    # curator's explicit "no evidence needed" decision).
    if v.posture != "Comply":
        return False, f"empty-after-gates should be Comply, got {v.posture}"
    return True, "all children gated off → Comply (defensible)"


# ── Freshness ─────────────────────────────────────────────────────────────────

def test_stale_leaf_reports_gap():
    leaf = _leaf("L")
    spec = SpecDescriptor(
        spec_id="s", op="ALL", curation_status="curated", control_id="c",
        children=[Edge(role="policy", applies_when=None, target=leaf)],
    )
    # Satisfied but stale → counts as gap
    ev = _make_satisfying_evaluator({"L": True}, fresh={"L": False})
    v = evaluate_control(spec, ev, _ec())
    if v.posture != "OFI":
        return False, f"stale leaf should produce OFI, got {v.posture}"
    if not any("stale" in g for g in v.gap_list):
        return False, f"expected a 'stale' gap, got {v.gap_list}"
    return True, "stale leaf surfaces as a refresh-suggestion gap"


# ── Test runner ───────────────────────────────────────────────────────────────

TESTS = [
    # curation_status
    test_uncurated_returns_UNKNOWN,
    test_deferred_to_findings_returns_deferred,
    test_explicit_empty_returns_Comply,
    # composition
    test_ALL_all_satisfied_is_Comply,
    test_ALL_one_missing_is_OFI,
    test_ANY_one_satisfied_is_Comply,
    test_ANY_none_satisfied_is_OFI,
    test_AT_LEAST_N_threshold,
    # applies_when
    test_spec_level_applies_when_false_is_NotApplicable,
    test_spec_level_applies_when_true_does_walk,
    test_edge_level_applies_when_false_skips_leaf,
    # nesting
    test_nested_spec_child_rolls_up,
    # corner cases
    test_empty_children_after_gates_is_Comply,
    test_stale_leaf_reports_gap,
]


def main() -> int:
    print("─" * 70)
    print("  Fulfilment Engine — unit tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            ok, msg = False, f"raised {type(e).__name__}: {e}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        print(f"         {msg}")
        if not ok:
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
