"""
Integration tests for Ship 129'.a — Stage-1 queue subscription filter.

Locks the discovery-vs-surfacing separation rule:
  - Discovery persists findings for any framework (universal universe)
  - Stage-1 queue surfaces findings ONLY for enrolled frameworks
  - Enrolling a framework instantly unblocks its findings (no re-extract)
  - Lapsing a framework re-hides its findings

See [[feedback-discovery-vs-surfacing-separation]] +
    [[ship-129-prime-arc-retrospective-2026-09-08]]

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_stage_queue_subscription_filter.py
"""
from __future__ import annotations

import os
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")

from rag.posture.stage1_review_chat import list_queue, list_pending_for_control  # noqa: E402
from rag.posture.stage2_approval_chat import list_pending_proposals, get_proposal_for_control  # noqa: E402


TEST_TENANT_ID = "99999999-9999-9999-9999-999999999977"
TEST_TENANT_NAME = "ArionComply Stage1-Filter Test Tenant"
TEST_DOC_ID = "99999999-9999-9999-9999-999999999966"

# Two enrolled standards + one deliberately-not-enrolled to prove the filter.
IN_SCOPE_STANDARD  = "ISO27001:2022"
IN_SCOPE_CONTROL   = "A.5.1"
OUT_SCOPE_STANDARD = "ISO27701:2019"
OUT_SCOPE_CONTROL  = "A.7.2.1"


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set — needed for Stage-1 filter test")
    return url


def _connect():
    return psycopg2.connect(_db_url())


@contextmanager
def _test_state():
    """Seed: tenant + enrolment for ISO 27001 only + 2 pending findings
    (one in-scope, one out-of-scope). Yields the connection.

    Cleanup deletes all seeded rows on exit — idempotent across leaks.
    """
    conn = _connect()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))

            cur.execute("""
                INSERT INTO tenants (id, name, slug, is_active)
                VALUES (%s::uuid, %s, %s, TRUE)
                ON CONFLICT (id) DO NOTHING
            """, (TEST_TENANT_ID, TEST_TENANT_NAME, "stage1-filter-test-tenant"))

            # Enrol IN_SCOPE only. OUT_SCOPE deliberately absent.
            cur.execute("""
                INSERT INTO tenant_standards (tenant_id, standard_id, status)
                VALUES (%s::uuid, %s, 'implementing')
                ON CONFLICT (tenant_id, standard_id) DO NOTHING
            """, (TEST_TENANT_ID, IN_SCOPE_STANDARD))

            # A client_documents row so the finding FK resolves.
            cur.execute("""
                INSERT INTO client_documents (
                    id, tenant_id, filename, storage_path,
                    checksum_sha256, file_size_bytes,
                    document_status, is_active, is_metadata_only,
                    retention_class
                ) VALUES (%s::uuid, %s::uuid, 'test.md', '/tmp/nowhere',
                          'testsha', 1,
                          'uploaded', TRUE, FALSE, 'compliance')
                ON CONFLICT DO NOTHING
            """, (TEST_DOC_ID, TEST_TENANT_ID))

            # Two pending findings: one in each standard.
            cur.execute("""
                INSERT INTO document_findings (
                    id, tenant_id, document_id, control_ref, standard_id,
                    status, confidence, excerpt, review_status, is_active,
                    inference_source
                ) VALUES
                (gen_random_uuid(), %s::uuid, %s::uuid, %s, %s,
                 'present', 'high', 'in-scope excerpt', 'pending', TRUE, 'templated'),
                (gen_random_uuid(), %s::uuid, %s::uuid, %s, %s,
                 'present', 'high', 'out-scope excerpt', 'pending', TRUE, 'templated')
                ON CONFLICT DO NOTHING
            """, (
                TEST_TENANT_ID, TEST_DOC_ID, IN_SCOPE_CONTROL, IN_SCOPE_STANDARD,
                TEST_TENANT_ID, TEST_DOC_ID, OUT_SCOPE_CONTROL, OUT_SCOPE_STANDARD,
            ))

            # Stage-2 fixture: a posture_controls row + a pending engine
            # PA for the OUT_SCOPE_STANDARD. Locks that Stage-2 filter
            # hides out-of-scope proposals too.
            cur.execute("""
                INSERT INTO posture_controls (
                    tenant_id, standard_id, control_ref, finding,
                    is_active, engine_proposal_status
                ) VALUES
                (%s::uuid, %s, %s, 'Not assessed', TRUE, 'proposed'),
                (%s::uuid, %s, %s, 'Not assessed', TRUE, 'proposed')
                ON CONFLICT DO NOTHING
            """, (
                TEST_TENANT_ID, IN_SCOPE_STANDARD, IN_SCOPE_CONTROL,
                TEST_TENANT_ID, OUT_SCOPE_STANDARD, OUT_SCOPE_CONTROL,
            ))
            cur.execute("""
                INSERT INTO posture_assertions (
                    tenant_id, standard_id, control_ref, source,
                    finding, gap_description, set_by, status
                ) VALUES
                (%s::uuid, %s, %s, 'engine',
                 'NC', 'in-scope engine reason', 'test:129a', 'pending'),
                (%s::uuid, %s, %s, 'engine',
                 'NC', 'out-scope engine reason', 'test:129a', 'pending')
                ON CONFLICT DO NOTHING
            """, (
                TEST_TENANT_ID, IN_SCOPE_STANDARD, IN_SCOPE_CONTROL,
                TEST_TENANT_ID, OUT_SCOPE_STANDARD, OUT_SCOPE_CONTROL,
            ))
        conn.commit()
        yield conn
    finally:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM document_findings WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM posture_assertions WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM posture_controls WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM client_documents WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM tenant_standards WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM tenants WHERE id = %s::uuid",
                        (TEST_TENANT_ID,))
        conn.commit()
        conn.close()


def _stds_in_queue(rows: list[dict]) -> set[str]:
    return {r["standard_id"] for r in rows}


def _controls_in_queue(rows: list[dict]) -> set[str]:
    return {r["control_ref"] for r in rows}


# ── Tests ────────────────────────────────────────────────────────────────

def test_list_queue_hides_out_of_scope_standard():
    """Baseline invariant: OUT_SCOPE_STANDARD has a pending finding but
    is not enrolled → must not appear in list_queue."""
    with _test_state() as conn:
        rows = list_queue(conn, TEST_TENANT_ID)
        stds = _stds_in_queue(rows)
        assert IN_SCOPE_STANDARD in stds, \
            f"in-scope standard {IN_SCOPE_STANDARD} missing from queue: {stds}"
        assert OUT_SCOPE_STANDARD not in stds, \
            f"out-of-scope standard {OUT_SCOPE_STANDARD} leaked into queue: {stds}"


def test_list_pending_for_control_hides_out_of_scope_standard():
    """Per-control detail view must also enforce the filter."""
    with _test_state() as conn:
        rows_out = list_pending_for_control(conn, TEST_TENANT_ID, OUT_SCOPE_CONTROL)
        assert rows_out == [], \
            f"per-control view leaked {len(rows_out)} out-of-scope findings"
        rows_in = list_pending_for_control(conn, TEST_TENANT_ID, IN_SCOPE_CONTROL)
        assert len(rows_in) == 1, \
            f"in-scope control should have 1 finding, got {len(rows_in)}"


def test_instant_flip_on_enrolment():
    """Enrolling OUT_SCOPE_STANDARD mid-session must immediately surface
    its previously-hidden findings. No re-extract needed — the discovery
    data was there the whole time."""
    with _test_state() as conn:
        # Before enrolment: only in-scope visible.
        before = list_queue(conn, TEST_TENANT_ID)
        assert OUT_SCOPE_STANDARD not in _stds_in_queue(before)

        # Enrol.
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenant_standards (tenant_id, standard_id, status)
                VALUES (%s::uuid, %s, 'implementing')
                ON CONFLICT (tenant_id, standard_id) DO NOTHING
            """, (TEST_TENANT_ID, OUT_SCOPE_STANDARD))
        conn.commit()

        # After enrolment: both surface, same underlying rows.
        after = list_queue(conn, TEST_TENANT_ID)
        assert OUT_SCOPE_STANDARD in _stds_in_queue(after), \
            f"instant-flip failed: {OUT_SCOPE_STANDARD} not visible after enrolment"
        assert OUT_SCOPE_CONTROL in _controls_in_queue(after)

        # Per-control view also flips.
        rows = list_pending_for_control(conn, TEST_TENANT_ID, OUT_SCOPE_CONTROL)
        assert len(rows) == 1, \
            f"per-control view didn't flip: got {len(rows)} findings"


# ── Stage-2 tests ───────────────────────────────────────────────────────

def test_stage2_list_pending_proposals_hides_out_of_scope():
    """Ship 129'.b — Stage-2 engine-proposal queue must not surface
    proposals for standards the tenant hasn't enrolled."""
    with _test_state() as conn:
        rows = list_pending_proposals(conn, TEST_TENANT_ID)
        stds = {r["standard_id"] for r in rows}
        ctrls = {r["control_ref"] for r in rows}
        assert IN_SCOPE_STANDARD in stds, \
            f"in-scope standard {IN_SCOPE_STANDARD} missing: {stds}"
        assert IN_SCOPE_CONTROL in ctrls
        assert OUT_SCOPE_STANDARD not in stds, \
            f"out-of-scope standard {OUT_SCOPE_STANDARD} leaked: {stds}"
        assert OUT_SCOPE_CONTROL not in ctrls


def test_stage2_get_proposal_returns_none_for_out_of_scope():
    """Deep-link to an out-of-scope control returns None (→ API 404).
    Symmetric with list — no way to reach the proposal via any surface."""
    with _test_state() as conn:
        out = get_proposal_for_control(conn, TEST_TENANT_ID, OUT_SCOPE_CONTROL)
        assert out is None, \
            f"out-of-scope proposal leaked via get_proposal_for_control: {out!r}"
        # In-scope still resolves.
        inv = get_proposal_for_control(conn, TEST_TENANT_ID, IN_SCOPE_CONTROL)
        assert inv is not None
        assert inv["standard_id"] == IN_SCOPE_STANDARD


def test_stage2_instant_flip_on_enrolment():
    """Enrolling the standard mid-session surfaces the previously-hidden
    engine proposal without re-running the engine."""
    with _test_state() as conn:
        before = list_pending_proposals(conn, TEST_TENANT_ID)
        assert OUT_SCOPE_STANDARD not in {r["standard_id"] for r in before}

        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenant_standards (tenant_id, standard_id, status)
                VALUES (%s::uuid, %s, 'implementing')
                ON CONFLICT (tenant_id, standard_id) DO NOTHING
            """, (TEST_TENANT_ID, OUT_SCOPE_STANDARD))
        conn.commit()

        after = list_pending_proposals(conn, TEST_TENANT_ID)
        assert OUT_SCOPE_STANDARD in {r["standard_id"] for r in after}
        assert OUT_SCOPE_CONTROL in {r["control_ref"] for r in after}


def test_lapsed_standard_is_hidden():
    """Setting an enrolled standard's status to 'lapsed' re-hides its
    findings — matches 'was certified, dropped it, don't want the noise'
    semantics of the status vocabulary."""
    with _test_state() as conn:
        # Enrol OUT_SCOPE then lapse it.
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("""
                INSERT INTO tenant_standards (tenant_id, standard_id, status)
                VALUES (%s::uuid, %s, 'lapsed')
                ON CONFLICT (tenant_id, standard_id)
                DO UPDATE SET status = 'lapsed'
            """, (TEST_TENANT_ID, OUT_SCOPE_STANDARD))
        conn.commit()

        rows = list_queue(conn, TEST_TENANT_ID)
        assert OUT_SCOPE_STANDARD not in _stds_in_queue(rows), \
            "lapsed standard leaked into queue — filter should exclude 'lapsed'"


# ── Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("list_queue hides out-of-scope standard",
         test_list_queue_hides_out_of_scope_standard),
        ("list_pending_for_control hides out-of-scope standard",
         test_list_pending_for_control_hides_out_of_scope_standard),
        ("instant flip on enrolment",
         test_instant_flip_on_enrolment),
        ("stage-2 list_pending_proposals hides out-of-scope",
         test_stage2_list_pending_proposals_hides_out_of_scope),
        ("stage-2 get_proposal returns None for out-of-scope",
         test_stage2_get_proposal_returns_none_for_out_of_scope),
        ("stage-2 instant flip on enrolment",
         test_stage2_instant_flip_on_enrolment),
        ("lapsed standard is hidden",
         test_lapsed_standard_is_hidden),
    ]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}\n      {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {name}\n      {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed + failed} PASS")
    sys.exit(0 if failed == 0 else 1)
