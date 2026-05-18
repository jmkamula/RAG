"""
Integration test: posture_writer emits posture_status_log rows on every
status change driven by document intake (schema_v21, Stage 3).

Pre-change behaviour:
  posture_writer upserts posture_controls but writes nothing to
  posture_status_log. The "how did A.5.18 evolve?" question has no
  underlying data — current state is the only state.

Post-change behaviour exercised here:
  - First aggregation for a new (control_ref, standard_id) → INSERT
    creates a posture_controls row AND a posture_status_log row with
    status_before=NULL.
  - Subsequent aggregation that changes the finding → UPDATE rewrites
    posture_controls AND appends a posture_status_log row with
    status_before=previous, status_after=new.
  - Aggregation that does NOT change the finding → posture_controls
    timestamps move forward but NO new history row (we only log
    transitions, not snapshots).
  - source_upload_id on each history row matches the driving upload_id.

This test stubs DocumentFinding objects directly rather than running the
full pipeline — the contract under test is _write_posture_controls, not
the end-to-end extractor.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_posture_history.py
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

import psycopg2

from rag.intake.posture_writer import _write_posture_controls
from rag.intake.models         import DocumentFinding


TENANT_ID = "00000000-0000-0000-0000-000000000001"


def _set_tenant(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SET app.tenant_id = %s", (TENANT_ID,))


def _make_finding(
    control_ref: str,
    finding:     str,
    *,
    evidence:    str = "Sample evidence text.",
    standard_id: str = "ISO27001:2022",
    upload_id:   Optional[str] = None,
) -> DocumentFinding:
    return DocumentFinding(
        upload_id     = upload_id or str(uuid.uuid4()),
        tenant_id     = TENANT_ID,
        document_name = "test_posture_history_fixture.docx",
        control_ref   = control_ref,
        standard_id   = standard_id,
        finding       = finding,
        evidence_text = evidence,
        confidence    = "high",
        section       = "Test section",
        id            = str(uuid.uuid4()),
    )


def _insert_upload_stub(conn, upload_id: str) -> None:
    """Create a minimal document_uploads row so posture_status_log FK
    constraints are satisfied. Filename uses the upload_id suffix so the
    sha256 unique index isn't tripped across parallel test runs."""
    sha = uuid.uuid4().hex + uuid.uuid4().hex   # 64 chars
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO document_uploads (
                id, tenant_id, filename, storage_path,
                extraction_status, sha256, byte_size
            ) VALUES (%s::uuid, %s::uuid, %s, %s, 'pending', %s, %s)
            """,
            (upload_id, TENANT_ID, f"_hist_{upload_id[:8]}.docx",
             f"/tmp/_hist_{upload_id[:8]}.docx", sha, 100),
        )
    conn.commit()


def _cleanup_upload(conn, upload_id: str) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM document_uploads WHERE id=%s::uuid", (upload_id,))
        conn.commit()
    except Exception:
        conn.rollback()


def _cleanup(conn, control_ref: str) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM posture_status_log "
                " WHERE tenant_id=%s::uuid AND control_ref=%s",
                (TENANT_ID, control_ref),
            )
            cur.execute(
                "DELETE FROM posture_controls "
                " WHERE tenant_id=%s::uuid AND control_ref=%s AND source='document'",
                (TENANT_ID, control_ref),
            )
        conn.commit()
    except Exception:
        conn.rollback()


def test_create_emits_history(db_url: str) -> tuple[bool, str]:
    """First write for a new control: posture_controls.INSERT plus one
    posture_status_log row with status_before=NULL."""
    ref     = f"X.{uuid.uuid4().hex[:4].upper()}.99"
    upload  = str(uuid.uuid4())

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)
        _insert_upload_stub(conn, upload)
        groups = {(ref, "ISO27001:2022"): [_make_finding(ref, "OFI", evidence="Initial draft.")]}
        updated, created, skipped = _write_posture_controls(
            groups, TENANT_ID, conn, upload_id=upload,
        )
        conn.commit()

        if (updated, created, skipped) != (0, 1, 0):
            return False, f"expected (updated, created, skipped)=(0,1,0), got ({updated},{created},{skipped})"

        with conn.cursor() as cur:
            cur.execute(
                "SELECT status_before, status_after, source, source_upload_id::text, "
                "       evidence_citation, confidence "
                "  FROM posture_status_log "
                " WHERE tenant_id=%s::uuid AND control_ref=%s "
                " ORDER BY changed_at",
                (TENANT_ID, ref),
            )
            rows = cur.fetchall()
        if len(rows) != 1:
            return False, f"expected 1 history row, got {len(rows)}"
        sb, sa, src, src_up, evd, conf = rows[0]
        if sb is not None:
            return False, f"status_before={sb!r}, expected NULL on create"
        if sa != "OFI":
            return False, f"status_after={sa!r}, expected 'OFI'"
        if src != "document":
            return False, f"source={src!r}, expected 'document'"
        if src_up != upload:
            return False, f"source_upload_id={src_up}, expected {upload}"
        if not evd or "Initial draft" not in evd:
            return False, f"evidence_citation missing evidence text: {evd!r}"
        return True, f"create emitted 1 history row (status_before=NULL → 'OFI')"
    finally:
        _cleanup(conn, ref)
        _cleanup_upload(conn, upload)
        conn.close()


def test_transition_emits_history(db_url: str) -> tuple[bool, str]:
    """Second write with a different finding: appends one history row
    with status_before=previous, status_after=new."""
    ref      = f"X.{uuid.uuid4().hex[:4].upper()}.99"
    upload_1 = str(uuid.uuid4())
    upload_2 = str(uuid.uuid4())

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)
        _insert_upload_stub(conn, upload_1)
        _insert_upload_stub(conn, upload_2)

        groups_1 = {(ref, "ISO27001:2022"): [_make_finding(ref, "OFI")]}
        _write_posture_controls(groups_1, TENANT_ID, conn, upload_id=upload_1)
        conn.commit()

        groups_2 = {(ref, "ISO27001:2022"): [_make_finding(ref, "Comply", evidence="Now compliant.")]}
        updated, created, skipped = _write_posture_controls(
            groups_2, TENANT_ID, conn, upload_id=upload_2,
        )
        conn.commit()

        if (updated, created, skipped) != (1, 0, 0):
            return False, f"expected (updated, created, skipped)=(1,0,0), got ({updated},{created},{skipped})"

        with conn.cursor() as cur:
            cur.execute(
                "SELECT status_before, status_after, source_upload_id::text "
                "  FROM posture_status_log "
                " WHERE tenant_id=%s::uuid AND control_ref=%s "
                " ORDER BY changed_at",
                (TENANT_ID, ref),
            )
            rows = cur.fetchall()
        if len(rows) != 2:
            return False, f"expected 2 history rows, got {len(rows)}"
        if (rows[0][0], rows[0][1]) != (None, "OFI"):
            return False, f"row[0] should be (NULL, 'OFI'), got {rows[0][:2]}"
        if (rows[1][0], rows[1][1]) != ("OFI", "Comply"):
            return False, f"row[1] should be ('OFI', 'Comply'), got {rows[1][:2]}"
        if rows[1][2] != upload_2:
            return False, f"row[1] source_upload_id={rows[1][2]}, expected {upload_2}"
        return True, "transition emitted (OFI → Comply) with correct source_upload_id"
    finally:
        _cleanup(conn, ref)
        _cleanup_upload(conn, upload_1)
        _cleanup_upload(conn, upload_2)
        conn.close()


def test_unchanged_status_emits_nothing(db_url: str) -> tuple[bool, str]:
    """Second write with same finding: posture_controls is updated
    (timestamps shift) but NO new history row is appended."""
    ref      = f"X.{uuid.uuid4().hex[:4].upper()}.99"
    upload_1 = str(uuid.uuid4())
    upload_2 = str(uuid.uuid4())

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)
        _insert_upload_stub(conn, upload_1)
        _insert_upload_stub(conn, upload_2)

        groups = {(ref, "ISO27001:2022"): [_make_finding(ref, "NC")]}
        _write_posture_controls(groups, TENANT_ID, conn, upload_id=upload_1)
        conn.commit()

        # Same finding, different upload — should NOT emit a new history row.
        groups_2 = {(ref, "ISO27001:2022"): [_make_finding(ref, "NC", evidence="Reconfirmed.")]}
        _write_posture_controls(groups_2, TENANT_ID, conn, upload_id=upload_2)
        conn.commit()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM posture_status_log "
                " WHERE tenant_id=%s::uuid AND control_ref=%s",
                (TENANT_ID, ref),
            )
            (n,) = cur.fetchone()
        if n != 1:
            return False, f"expected 1 history row (no new transition), got {n}"
        return True, "no-op upsert did not append a redundant history row"
    finally:
        _cleanup(conn, ref)
        _cleanup_upload(conn, upload_1)
        _cleanup_upload(conn, upload_2)
        conn.close()


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[FAIL] DATABASE_URL not set")
        return 1

    print("─" * 70)
    print("  Posture history — Stage 3 (schema_v21 / posture_status_log)")
    print("─" * 70)

    failures = 0
    for name, fn in [
        ("Create emits one history row (NULL → status)",  test_create_emits_history),
        ("Transition emits a second history row",         test_transition_emits_history),
        ("Unchanged status does not append a row",        test_unchanged_status_emits_nothing),
    ]:
        ok, msg = fn(db_url)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {msg}")
        if not ok:
            failures += 1

    print("─" * 70)
    print(f"  {3 - failures}/3 passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
