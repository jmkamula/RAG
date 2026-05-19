"""
Unit tests for rag/posture/leaf_evaluators.py — per-evidence-type leaf
evaluators. Uses inline mocks for pg + neo4j to keep tests deterministic.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_leaf_evaluators.py
"""
from __future__ import annotations

import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.posture.applies_when import EvalContext
from rag.posture.fulfilment_engine import LeafSpec
from rag.posture.leaf_evaluators import PolicyLeafEvaluator


TENANT_ID = "00000000-0000-0000-0000-000000000001"


# ── Minimal mocks ─────────────────────────────────────────────────────────────

class _FakeRecord(dict):
    """Subclass of dict so both row['key'] and row.get('key') work like Neo4j Record."""

class _FakeCypherResult:
    def __init__(self, rows: list[dict]):
        self._rows = [_FakeRecord(r) for r in rows]
    def __iter__(self):
        return iter(self._rows)
    def single(self):
        return self._rows[0] if self._rows else None


class _FakeNeo4jSession:
    def __init__(self, must_items: list[tuple[str, str]]):
        self._must_items = must_items
    def run(self, query, **params):
        # Only one Cypher pattern is run by PolicyLeafEvaluator — return
        # the must-items rows.
        rows = [{"id": iid, "text": text} for iid, text in self._must_items]
        return _FakeCypherResult(rows)
    def __enter__(self): return self
    def __exit__(self, *a): pass


class _FakeNeo4jDriver:
    def __init__(self, must_items: list[tuple[str, str]] = ()):
        self._must_items = list(must_items)
    def session(self):
        return _FakeNeo4jSession(self._must_items)


class _FakeCursor:
    """SQL-agnostic cursor that returns canned data for fetchall.

    The evaluator runs two execute() calls: first the set_config, then the
    real query. We return [] for set_config and the canned rows for the
    second call.
    """
    def __init__(self, pg_rows):
        self._pg_rows = pg_rows
        self._last_was_set_config = False
    def execute(self, sql, params=None):
        self._last_was_set_config = "set_config" in sql
    def fetchall(self):
        if self._last_was_set_config:
            return []
        return self._pg_rows
    def __enter__(self): return self
    def __exit__(self, *a): pass


class _FakePg:
    def __init__(self, pg_rows: list[tuple]):
        self._pg_rows = pg_rows
    def cursor(self):
        return _FakeCursor(self._pg_rows)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _leaf(must_texts: Iterable[str], freshness_days: int | None = None) -> LeafSpec:
    return LeafSpec(
        leaf_id="req:A.5.1:isp_policy",
        evidence_type="policy",
        must_items=list(must_texts),
        freshness_days=freshness_days,
        title="ISP Policy (test fixture)",
    )

def _ec() -> EvalContext:
    return EvalContext(
        facts={},
        supply_exists_fn=lambda t: False,
        supply_count_fn=lambda t: 0,
    )

def _evaluator(must_items, pg_rows) -> PolicyLeafEvaluator:
    return PolicyLeafEvaluator(
        pg_conn=_FakePg(pg_rows),
        neo4j_driver=_FakeNeo4jDriver(must_items),
        tenant_id=TENANT_ID,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_all_items_recognised_is_satisfied():
    must_items = [("item:A.5.1:scope", "Scope of the policy defined"),
                  ("item:A.5.1:roles", "Roles and responsibilities for information security")]
    pg_rows = [
        ("item:A.5.1:scope", datetime.now(timezone.utc) - timedelta(days=30)),
        ("item:A.5.1:roles", datetime.now(timezone.utc) - timedelta(days=30)),
    ]
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"]), _ec())  # leaf.must_items text is irrelevant — evaluator uses Neo4j ids
    if not v.satisfied:
        return False, f"expected satisfied=True, got {v.satisfied}; reason={v.reason}"
    if not v.fresh:
        return False, f"expected fresh=True, got fresh={v.fresh}"
    if v.items_unrecognised:
        return False, f"expected no unrecognised, got {v.items_unrecognised}"
    if len(v.items_recognised) != 2:
        return False, f"expected 2 recognised, got {v.items_recognised}"
    return True, "all 2 MUST items recognised → satisfied + fresh"

def test_some_items_missing_is_not_satisfied():
    must_items = [("item:A.5.1:scope",      "Scope of the policy defined"),
                  ("item:A.5.1:roles",      "Roles and responsibilities for information security"),
                  ("item:A.5.1:principles", "InfoSec principles stated")]
    pg_rows = [
        ("item:A.5.1:scope", datetime.now(timezone.utc) - timedelta(days=10)),
    ]
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"]), _ec())
    if v.satisfied:
        return False, "expected satisfied=False (2/3 unrecognised)"
    if len(v.items_unrecognised) != 2:
        return False, f"expected 2 unrecognised, got {v.items_unrecognised}"
    if len(v.items_recognised) != 1:
        return False, f"expected 1 recognised, got {v.items_recognised}"
    return True, f"1/3 recognised → satisfied=False ({len(v.items_unrecognised)} unrecognised)"

def test_no_matching_documents_is_not_satisfied():
    must_items = [("item:A.5.1:scope", "Scope")]
    pg_rows = []   # no findings at all
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"]), _ec())
    if v.satisfied:
        return False, "expected satisfied=False when no documents match"
    if not v.fresh:
        return False, "expected fresh=True vacuously (no artifact to age)"
    if v.items_unrecognised != ["Scope"]:
        return False, f"expected ['Scope'] unrecognised, got {v.items_unrecognised}"
    return True, "no matching artifact → satisfied=False, fresh=True vacuously"

def test_stale_artifact_is_not_fresh():
    must_items = [("item:A.5.1:scope", "Scope")]
    pg_rows = [("item:A.5.1:scope", datetime.now(timezone.utc) - timedelta(days=400))]
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"], freshness_days=365), _ec())
    if not v.satisfied:
        return False, "expected satisfied=True (item recognised)"
    if v.fresh:
        return False, "expected fresh=False (400 days > 365)"
    if "older than 365 days" not in v.reason:
        return False, f"reason should mention staleness, got: {v.reason}"
    return True, "stale artifact → satisfied=True but fresh=False"

def test_fresh_artifact_passes_check():
    must_items = [("item:A.5.1:scope", "Scope")]
    pg_rows = [("item:A.5.1:scope", datetime.now(timezone.utc) - timedelta(days=30))]
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"], freshness_days=365), _ec())
    if not v.fresh:
        return False, "30 days < 365 should be fresh"
    return True, "30-day-old artifact within 365-day freshness window → fresh"

def test_no_freshness_constraint_always_fresh():
    must_items = [("item:A.5.1:scope", "Scope")]
    pg_rows = [("item:A.5.1:scope", datetime.now(timezone.utc) - timedelta(days=99999))]
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"], freshness_days=None), _ec())
    if not v.fresh:
        return False, "no freshness_days set should always be fresh"
    return True, "no freshness constraint → always fresh"

def test_no_must_items_is_vacuously_satisfied():
    must_items = []
    pg_rows = []
    ev = _evaluator(must_items, pg_rows)
    v = ev(_leaf(["x"]), _ec())
    if not v.satisfied:
        return False, "leaf with no MUST items should be vacuously satisfied"
    if not v.fresh:
        return False, "vacuously fresh too"
    return True, "no MUST items → satisfied + fresh (defensible Comply)"

def test_wrong_evidence_type_rejected():
    must_items = [("item:A.5.1:scope", "Scope")]
    pg_rows = []
    ev = _evaluator(must_items, pg_rows)
    bogus = LeafSpec(
        leaf_id="req:test:wrong",
        evidence_type="drill_record",
        must_items=["x"],
    )
    v = ev(bogus, _ec())
    if v.satisfied:
        return False, "wrong evidence_type should not be satisfied"
    if "handles 'policy' only" not in v.reason:
        return False, f"reason should explain mismatch, got: {v.reason}"
    return True, "wrong evidence_type → unsatisfied with diagnostic"


# ── Runner ────────────────────────────────────────────────────────────────────

TESTS = [
    test_all_items_recognised_is_satisfied,
    test_some_items_missing_is_not_satisfied,
    test_no_matching_documents_is_not_satisfied,
    test_stale_artifact_is_not_fresh,
    test_fresh_artifact_passes_check,
    test_no_freshness_constraint_always_fresh,
    test_no_must_items_is_vacuously_satisfied,
    test_wrong_evidence_type_rejected,
]


def main() -> int:
    print("─" * 70)
    print("  Leaf Evaluators (policy) — unit tests")
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
