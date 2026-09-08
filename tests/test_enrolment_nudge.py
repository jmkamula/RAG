"""
Integration tests for Ship 129'.d — enrolment-nudge notification producer.

Locks:
  - Nudge fires when driving facts are declared AND framework not enrolled
  - Nudge does NOT fire when driving facts are at 'default' source
    (conservative-in-doubt per Ship 110'.d)
  - Nudge does NOT fire when the framework IS enrolled
  - Nudge is deduped within _NUDGE_DEDUP_DAYS window
  - Discovery-count enrichment appears in body but is NOT the trigger

See [[feedback-discovery-vs-surfacing-separation]].

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_enrolment_nudge.py
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

import psycopg2  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")

from rag.notifications.enrolment_nudge import (  # noqa: E402
    sweep_enrolment_nudge, emit_enrolment_nudge, _NUDGES,
)


TEST_TENANT_ID = "99999999-9999-9999-9999-999999999955"
TEST_TENANT_NAME = "ArionComply Enrolment-Nudge Test Tenant"

GDPR_STANDARD = "GDPR:2016/679"
ISO_STANDARD  = "ISO27001:2022"


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return url


def _connect():
    return psycopg2.connect(_db_url())


@contextmanager
def _test_state(
    eu_data_subjects=False, uk_data_subjects=False,
    processes_personal_data=False,
    eu_facts_declared=False,
    process_facts_declared=False,
    enrol_iso=True, enrol_gdpr=False, enrol_pims=False,
    seed_gdpr_findings=0,
):
    """Seed a tenant with configurable fact + enrolment shape."""
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
            """, (TEST_TENANT_ID, TEST_TENANT_NAME, "enrolment-nudge-test"))

            # Seed enrolment
            if enrol_iso:
                cur.execute("""
                    INSERT INTO tenant_standards (tenant_id, standard_id, status)
                    VALUES (%s::uuid, %s, 'implementing')
                    ON CONFLICT (tenant_id, standard_id) DO NOTHING
                """, (TEST_TENANT_ID, ISO_STANDARD))
            if enrol_gdpr:
                cur.execute("""
                    INSERT INTO tenant_standards (tenant_id, standard_id, status)
                    VALUES (%s::uuid, %s, 'implementing')
                    ON CONFLICT (tenant_id, standard_id) DO NOTHING
                """, (TEST_TENANT_ID, GDPR_STANDARD))
            if enrol_pims:
                cur.execute("""
                    INSERT INTO tenant_standards (tenant_id, standard_id, status)
                    VALUES (%s::uuid, %s, 'implementing')
                    ON CONFLICT (tenant_id, standard_id) DO NOTHING
                """, (TEST_TENANT_ID, "ISO27701:2019"))

            # posture_controls row so tenant iteration (sweep uses
            # posture_controls to find tenants) picks it up
            cur.execute("""
                INSERT INTO posture_controls (
                    tenant_id, standard_id, control_ref, finding, is_active
                ) VALUES (%s::uuid, %s, 'A.5.1', 'Not assessed', TRUE)
                ON CONFLICT DO NOTHING
            """, (TEST_TENANT_ID, ISO_STANDARD))

            # client_facts row with declared facts + fact_source
            import json as _json
            fact_source = {}
            if eu_facts_declared:
                fact_source["eu_data_subjects"] = "declared"
                fact_source["uk_data_subjects"] = "declared"
            if process_facts_declared:
                fact_source["processes_personal_data"] = "declared"

            cur.execute("""
                INSERT INTO client_facts (
                    tenant_id, eu_data_subjects, uk_data_subjects,
                    processes_personal_data, fact_source
                ) VALUES (%s::uuid, %s, %s, %s, %s::jsonb)
                ON CONFLICT (tenant_id) DO UPDATE SET
                    eu_data_subjects        = EXCLUDED.eu_data_subjects,
                    uk_data_subjects        = EXCLUDED.uk_data_subjects,
                    processes_personal_data = EXCLUDED.processes_personal_data,
                    fact_source             = EXCLUDED.fact_source
            """, (TEST_TENANT_ID, eu_data_subjects, uk_data_subjects,
                  processes_personal_data, _json.dumps(fact_source)))

            # Optional: seed GDPR discovery findings for enrichment test
            if seed_gdpr_findings > 0:
                cur.execute("""
                    INSERT INTO client_documents (
                        id, tenant_id, filename, storage_path,
                        checksum_sha256, file_size_bytes,
                        document_status, is_active, is_metadata_only,
                        retention_class
                    ) VALUES (gen_random_uuid(), %s::uuid, 'seed.md', '/tmp/nowhere',
                              'testenrolment', 1, 'uploaded', TRUE, FALSE, 'compliance')
                    RETURNING id
                """, (TEST_TENANT_ID,))
                doc_id = cur.fetchone()[0]
                for i in range(seed_gdpr_findings):
                    cur.execute("""
                        INSERT INTO document_findings (
                            id, tenant_id, document_id, control_ref, standard_id,
                            status, confidence, excerpt, review_status, is_active,
                            inference_source
                        ) VALUES (gen_random_uuid(), %s::uuid, %s::uuid, 'Art.30', %s,
                                  'present', 'high', 'excerpt', 'pending', TRUE,
                                  'templated')
                    """, (TEST_TENANT_ID, doc_id, GDPR_STANDARD))
        conn.commit()
        yield conn
    finally:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM document_findings WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM client_documents WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM tenant_notification WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM posture_controls WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM client_facts WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM tenant_standards WHERE tenant_id = %s::uuid",
                        (TEST_TENANT_ID,))
            cur.execute("DELETE FROM tenants WHERE id = %s::uuid",
                        (TEST_TENANT_ID,))
        conn.commit()
        conn.close()


def _nudges_for(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    (TEST_TENANT_ID,))
        cur.execute("""
            SELECT title, body, severity FROM tenant_notification
             WHERE tenant_id = %s::uuid
               AND kind = 'unenrolled_framework_applicable'
             ORDER BY fired_at
        """, (TEST_TENANT_ID,))
        return [{"title": r[0], "body": r[1], "severity": r[2]}
                for r in cur.fetchall()]


# ── Tests ────────────────────────────────────────────────────────────────

def test_nudge_fires_when_eu_subjects_and_gdpr_not_enrolled():
    """The core case: eu_data_subjects=TRUE (declared), GDPR not enrolled
    → nudge lands."""
    with _test_state(
        eu_data_subjects=True, uk_data_subjects=False,
        eu_facts_declared=True,
        enrol_iso=True, enrol_gdpr=False,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000001")
        rows = _nudges_for(conn)
        assert len(rows) == 1, \
            f"expected 1 GDPR nudge, got {len(rows)}: {rows}"
        assert "GDPR" in rows[0]["title"]
        assert GDPR_STANDARD in rows[0]["body"]
        assert rows[0]["severity"] == "low"


def test_nudge_skipped_when_facts_not_declared():
    """eu_data_subjects=TRUE but fact_source='default' → skip
    (conservative-in-doubt)."""
    with _test_state(
        eu_data_subjects=True,           # value True but...
        eu_facts_declared=False,          # ...never explicitly declared
        enrol_iso=True, enrol_gdpr=False,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000002")
        rows = _nudges_for(conn)
        assert rows == [], \
            f"nudge fired despite facts being at default source: {rows}"


def test_nudge_skipped_when_framework_already_enrolled():
    """eu_data_subjects=TRUE declared AND GDPR enrolled → no nudge
    (nothing to prompt)."""
    with _test_state(
        eu_data_subjects=True,
        eu_facts_declared=True,
        enrol_iso=True, enrol_gdpr=True,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000003")
        rows = _nudges_for(conn)
        assert rows == [], \
            f"nudge fired despite GDPR already enrolled: {rows}"


def test_nudge_deduped_within_window():
    """Two sweep runs back-to-back → one notification only."""
    with _test_state(
        eu_data_subjects=True, eu_facts_declared=True,
        enrol_iso=True, enrol_gdpr=False,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-00000000004a")
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-00000000004b")
        rows = _nudges_for(conn)
        assert len(rows) == 1, \
            f"dedup broke — got {len(rows)} nudges after 2 sweeps"


def test_discovery_count_enriches_body_but_not_trigger():
    """seed 4 GDPR findings → body mentions count. The trigger is still
    facts; the count is supporting evidence."""
    with _test_state(
        eu_data_subjects=True, eu_facts_declared=True,
        enrol_iso=True, enrol_gdpr=False,
        seed_gdpr_findings=4,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000005")
        rows = _nudges_for(conn)
        assert len(rows) == 1
        assert "4 GDPR" in rows[0]["body"] or "4 " in rows[0]["body"], \
            f"discovery count not in body: {rows[0]['body']}"


def test_no_findings_still_fires_nudge():
    """Zero discovery findings but jurisdiction applicable → nudge still
    fires (trigger is jurisdiction, not counts)."""
    with _test_state(
        eu_data_subjects=True, eu_facts_declared=True,
        enrol_iso=True, enrol_gdpr=False,
        seed_gdpr_findings=0,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000006")
        rows = _nudges_for(conn)
        assert len(rows) == 1, \
            "nudge should fire even with 0 discovery findings"
        # Body should NOT contain the count sentence
        assert "ready to activate" not in rows[0]["body"], \
            "body incorrectly claims discovery-count enrichment when N=0"


def test_pims_nudge_fires_on_personal_data():
    """Processes personal data + ISO 27701 not enrolled → PIMS nudge."""
    with _test_state(
        processes_personal_data=True,
        process_facts_declared=True,
        enrol_iso=True, enrol_pims=False,
    ) as conn:
        sweep_enrolment_nudge(conn, tick_id="00000000-0000-0000-1000-000000000007")
        rows = _nudges_for(conn)
        pims_rows = [r for r in rows if "ISO 27701" in r["title"]]
        assert len(pims_rows) == 1, \
            f"expected 1 PIMS nudge, got {len(pims_rows)}: {rows}"


# ── Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("nudge fires: EU subjects + GDPR not enrolled",
         test_nudge_fires_when_eu_subjects_and_gdpr_not_enrolled),
        ("nudge skipped: facts not declared (default source)",
         test_nudge_skipped_when_facts_not_declared),
        ("nudge skipped: framework already enrolled",
         test_nudge_skipped_when_framework_already_enrolled),
        ("nudge deduped within window",
         test_nudge_deduped_within_window),
        ("discovery count enriches body but not trigger",
         test_discovery_count_enriches_body_but_not_trigger),
        ("nudge fires even with 0 discovery findings",
         test_no_findings_still_fires_nudge),
        ("PIMS nudge fires on personal-data processing",
         test_pims_nudge_fires_on_personal_data),
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
            import traceback
            print(f"ERROR {name}\n      {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{passed + failed} PASS")
    sys.exit(0 if failed == 0 else 1)
