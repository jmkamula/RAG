"""
Unit tests for rag/posture/engine_runner._resolve_target_to_evidence_type
and the surrounding ER:<leaf_id> resolution path.

Locks the behaviour that an `ER:<leaf_id>` target in an applies_when
expression resolves via the pre-loaded EvidenceRequirement map, and that
an unknown / mis-typed leaf id raises EvalError rather than silently
evaluating to False (which would invert the curator's intent).

Standalone script. Each test returns (ok, message). main() prints
PASS/FAIL and returns exit code 0 iff all pass.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_engine_runner_resolver.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.posture.applies_when import EvalError
from rag.posture.engine_runner import (
    _load_er_evidence_types,
    _make_supply_count_fn,
    _make_supply_exists_fn,
    _resolve_target_to_evidence_type,
)


# ── Fakes ─────────────────────────────────────────────────────────────────────

class _FakeResult:
    def __init__(self, rows):
        self._rows = rows
    def __iter__(self):
        return iter(self._rows)

class _FakeSession:
    def __init__(self, rows):
        self._rows = rows
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def run(self, *_args, **_kwargs):
        return _FakeResult([dict(r) for r in self._rows])

class _FakeDriver:
    def __init__(self, rows):
        self._rows = rows
    def session(self):
        return _FakeSession(self._rows)


class _FakeCursor:
    """Minimal cursor: records SQL calls; returns rows from a queue."""
    def __init__(self, rows_queue):
        self._rows_queue = rows_queue
        self.calls = []
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def execute(self, sql, params=()):
        self.calls.append((sql.strip().split()[0].upper(), params))
    def fetchone(self):
        return self._rows_queue.pop(0) if self._rows_queue else None


class _FakePgConn:
    def __init__(self, rows_queue):
        self._cursor = _FakeCursor(rows_queue)
    def cursor(self):
        return self._cursor


# ── Resolver tests ────────────────────────────────────────────────────────────

def test_resolve_non_er_passes_through():
    er = {"req:5.2:information_security_policy": "policy"}
    result = _resolve_target_to_evidence_type("policy", er)
    if result != "policy":
        return False, f"expected 'policy', got {result!r}"
    return True, "non-ER target passes through unchanged"

def test_resolve_known_er_returns_evidence_type():
    er = {"req:5.2:information_security_policy": "policy"}
    result = _resolve_target_to_evidence_type(
        "ER:req:5.2:information_security_policy", er
    )
    if result != "policy":
        return False, f"expected 'policy', got {result!r}"
    return True, "ER:<known-id> resolves to evidence_type"

def test_resolve_unknown_er_raises_eval_error():
    er = {"req:5.2:information_security_policy": "policy"}
    try:
        _resolve_target_to_evidence_type("ER:totally_bogus_leaf", er)
    except EvalError as e:
        msg = str(e)
        if "unknown leaf id" not in msg:
            return False, f"EvalError raised but message unexpected: {msg!r}"
        return True, f"EvalError raised: {msg}"
    return False, "expected EvalError, got silent return — regression"

def test_resolve_er_with_empty_evidence_type_raises():
    er = {"req:foo:bar": None}  # leaf exists but evidence_type is missing
    try:
        _resolve_target_to_evidence_type("ER:req:foo:bar", er)
    except EvalError as e:
        if "evidence_type" not in str(e):
            return False, f"EvalError raised but message unexpected: {e}"
        return True, "EvalError raised for leaf with no evidence_type"
    return False, "expected EvalError for empty evidence_type"


# ── Loader tests ──────────────────────────────────────────────────────────────

def test_load_er_evidence_types_builds_dict():
    rows = [
        {"id": "req:5.2:information_security_policy", "evidence_type": "policy"},
        {"id": "req:6.1.2:risk_assessment",            "evidence_type": "risk_assessment"},
    ]
    er = _load_er_evidence_types(_FakeDriver(rows))
    if er != {
        "req:5.2:information_security_policy": "policy",
        "req:6.1.2:risk_assessment":            "risk_assessment",
    }:
        return False, f"unexpected dict: {er!r}"
    return True, "loader builds id→evidence_type dict from Neo4j rows"


# ── Supply function propagation tests ─────────────────────────────────────────

def test_supply_exists_propagates_eval_error_for_unknown_leaf():
    """Unknown ER:<leaf> must propagate as EvalError instead of returning
    False — silent-False is the exact foot-gun this fix removes."""
    er = {"req:5.2:information_security_policy": "policy"}
    pg = _FakePgConn(rows_queue=[])
    fn = _make_supply_exists_fn(pg, "tenant-A", er)
    try:
        fn("ER:does_not_exist")
    except EvalError:
        return True, "supply_exists raises EvalError for unknown ER:<leaf>"
    return False, "supply_exists silently returned for unknown leaf — regression"

def test_supply_count_propagates_eval_error_for_unknown_leaf():
    er = {"req:5.2:information_security_policy": "policy"}
    pg = _FakePgConn(rows_queue=[])
    fn = _make_supply_count_fn(pg, "tenant-A", er)
    try:
        fn("ER:does_not_exist")
    except EvalError:
        return True, "supply_count raises EvalError for unknown ER:<leaf>"
    return False, "supply_count silently returned for unknown leaf — regression"

def test_supply_exists_queries_postgres_for_known_er():
    """Happy path: ER: target resolves and the Postgres lookup runs against
    the resolved evidence_type (not the raw ER: string)."""
    er = {"req:5.2:information_security_policy": "policy"}
    # Two execute() calls expected: set_config + SELECT. Return a row on
    # fetchone() so supply_exists returns True.
    pg = _FakePgConn(rows_queue=[(1,)])
    fn = _make_supply_exists_fn(pg, "tenant-A", er)
    result = fn("ER:req:5.2:information_security_policy")
    if result is not True:
        return False, f"expected True, got {result!r}"
    # Verify the second SQL call carried the resolved evidence_type
    second_call = pg._cursor.calls[1]
    if "policy" not in second_call[1]:
        return False, f"expected 'policy' in query params, got {second_call!r}"
    return True, "ER:<known> resolved and queried as evidence_type='policy'"


# ── Test runner ───────────────────────────────────────────────────────────────

TESTS = [
    test_resolve_non_er_passes_through,
    test_resolve_known_er_returns_evidence_type,
    test_resolve_unknown_er_raises_eval_error,
    test_resolve_er_with_empty_evidence_type_raises,
    test_load_er_evidence_types_builds_dict,
    test_supply_exists_propagates_eval_error_for_unknown_leaf,
    test_supply_count_propagates_eval_error_for_unknown_leaf,
    test_supply_exists_queries_postgres_for_known_er,
]


def main() -> int:
    print("─" * 70)
    print("  engine_runner — ER:<leaf_id> resolver tests")
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
