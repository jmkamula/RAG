"""
Integration test: confirm uploads are date-versioned under schema_v20.

Series semantics under test:

  • Same filename, different content → same series_id, version_no
    increments by 1 per upload.
  • The unique index uniq_document_uploads_series_version blocks two rows
    from claiming the same (series_id, version_no).
  • Duplicate uploads (extraction_status='duplicate') do not appear in the
    series — Layer 1 duplicates are rejected at the endpoint before any row
    is written; Layer 2 duplicates have series_id/version_no nulled out
    when the pipeline marks them.

This test exercises the SQL contract directly. The endpoint flow that
computes (series_id, version_no) is the same logic embedded here, so a
mismatch between the two would surface as a constraint violation.

Pre-change (pre-v20) behaviour:
  Two uploads of the same filename → no relationship between rows; no
  version sequence; "show me the history of policy.docx" is unanswerable.

Post-change behaviour exercised here:
  • Two same-filename inserts share series_id, version_no = 1, 2.
  • Third insert with same filename → version_no = 3.
  • Direct attempt to claim an existing (series_id, version_no) → blocked
    by uniq_document_uploads_series_version.
  • A row marked 'duplicate' with NULL series_id frees its slot — next
    insert reuses that version_no.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_upload_versioning.py
"""
from __future__ import annotations

import os
import sys
import hashlib
import uuid
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

import psycopg2
from psycopg2 import errors as pg_errors


TENANT_ID = "00000000-0000-0000-0000-000000000001"   # Arion Networks


def _set_tenant(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SET app.tenant_id = %s", (TENANT_ID,))


def _cleanup(conn, filename: str) -> None:
    """Remove all rows (canonical + dup-tombstones) sharing this filename."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM document_text "
                " WHERE upload_id IN (SELECT id FROM document_uploads "
                "                      WHERE tenant_id=%s::uuid AND filename=%s)",
                (TENANT_ID, filename),
            )
            cur.execute(
                "DELETE FROM document_uploads "
                " WHERE tenant_id=%s::uuid AND filename=%s",
                (TENANT_ID, filename),
            )
        conn.commit()
    except Exception:
        conn.rollback()


def _assign_series(cur, filename: str) -> tuple[str, int]:
    """Mirror of the upload-endpoint logic in api_server.py. If this drifts
    from the endpoint, the test stops being a contract check."""
    cur.execute(
        """
        SELECT series_id, MAX(version_no)
          FROM document_uploads
         WHERE tenant_id = %s::uuid
           AND filename  = %s
           AND extraction_status <> 'duplicate'
           AND series_id IS NOT NULL
         GROUP BY series_id
         LIMIT 1
        """,
        (TENANT_ID, filename),
    )
    row = cur.fetchone()
    if row:
        return str(row[0]), int(row[1]) + 1
    return str(uuid.uuid4()), 1


def _insert_upload(
    conn,
    filename: str,
    sha256:   str,
    upload_id: Optional[str] = None,
) -> tuple[str, str, int]:
    """Insert one upload row using the same (series_id, version_no)
    assignment the endpoint uses. Returns (upload_id, series_id, version_no)."""
    uid = upload_id or str(uuid.uuid4())
    with conn.cursor() as cur:
        series_id, version_no = _assign_series(cur, filename)
        cur.execute(
            """
            INSERT INTO document_uploads (
                id, tenant_id, filename, storage_path,
                extraction_status, sha256, byte_size,
                series_id, version_no
            ) VALUES (%s::uuid, %s::uuid, %s, %s, 'pending', %s, %s,
                      %s::uuid, %s)
            """,
            (uid, TENANT_ID, filename, f"/tmp/{uid}.docx",
             sha256, 100, series_id, version_no),
        )
    conn.commit()
    return uid, series_id, version_no


def test_sequential_versions(db_url: str) -> tuple[bool, str]:
    """Three same-filename inserts with different sha256 → v1, v2, v3 in
    a single series."""
    run_marker = uuid.uuid4().hex[:8]
    filename   = f"_ver_seq_{run_marker}.docx"

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)

        _, s1, v1 = _insert_upload(conn, filename, hashlib.sha256(b"a" + run_marker.encode()).hexdigest())
        _, s2, v2 = _insert_upload(conn, filename, hashlib.sha256(b"b" + run_marker.encode()).hexdigest())
        _, s3, v3 = _insert_upload(conn, filename, hashlib.sha256(b"c" + run_marker.encode()).hexdigest())

        if not (s1 == s2 == s3):
            return False, f"series_id drifted across versions: {s1}, {s2}, {s3}"
        if (v1, v2, v3) != (1, 2, 3):
            return False, f"version_no sequence wrong: got ({v1}, {v2}, {v3}), expected (1, 2, 3)"

        # Verify what /versions would see.
        with conn.cursor() as cur:
            cur.execute(
                "SELECT version_no, extraction_status "
                "  FROM document_uploads "
                " WHERE series_id = %s::uuid "
                " ORDER BY version_no",
                (s1,),
            )
            rows = cur.fetchall()
        if [r[0] for r in rows] != [1, 2, 3]:
            return False, f"series query returned wrong sequence: {rows}"

        return True, f"3 same-filename inserts → series={s1[:8]} versions=[1,2,3]"
    finally:
        _cleanup(conn, filename)
        conn.close()


def test_duplicate_version_no_blocked(db_url: str) -> tuple[bool, str]:
    """Two rows claiming the same (series_id, version_no) must violate
    uniq_document_uploads_series_version."""
    run_marker = uuid.uuid4().hex[:8]
    filename   = f"_ver_uniq_{run_marker}.docx"

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)
        # First insert via the normal path → v1.
        _, series_id, _ = _insert_upload(conn, filename, hashlib.sha256(uuid.uuid4().bytes).hexdigest())

        # Second insert hand-rolled to collide on (series_id, version_no=1).
        raised = False
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO document_uploads (
                        id, tenant_id, filename, storage_path,
                        extraction_status, sha256, byte_size,
                        series_id, version_no
                    ) VALUES (%s::uuid, %s::uuid, %s, %s, 'pending', %s, %s,
                              %s::uuid, %s)
                    """,
                    (str(uuid.uuid4()), TENANT_ID, filename, "/tmp/x",
                     hashlib.sha256(b"different").hexdigest(), 100,
                     series_id, 1),
                )
            conn.commit()
        except pg_errors.UniqueViolation:
            conn.rollback()
            raised = True
        except Exception as e:
            conn.rollback()
            return False, f"unexpected exception: {type(e).__name__}: {e}"

        if not raised:
            return False, "duplicate (series_id, version_no) was not blocked"
        return True, "duplicate (series_id, version_no) blocked by unique index"
    finally:
        _cleanup(conn, filename)
        conn.close()


def test_dup_tombstone_frees_version_slot(db_url: str) -> tuple[bool, str]:
    """A row marked 'duplicate' with NULL series_id+version_no should free
    its slot for a subsequent upload. Mirrors the Layer 2 pipeline path."""
    run_marker = uuid.uuid4().hex[:8]
    filename   = f"_ver_dup_{run_marker}.docx"

    conn = psycopg2.connect(db_url)
    try:
        _set_tenant(conn)

        # v1: real upload.
        uid_a, series_id, v_a = _insert_upload(
            conn, filename, hashlib.sha256(b"a" + run_marker.encode()).hexdigest()
        )

        # v2: starts as v2, then the pipeline finds a markdown dup of v1 →
        # marks the row 'duplicate' and nulls series_id + version_no.
        uid_b, _, v_b = _insert_upload(
            conn, filename, hashlib.sha256(b"b" + run_marker.encode()).hexdigest()
        )
        if (v_a, v_b) != (1, 2):
            return False, f"pre-dup-mark versions wrong: ({v_a}, {v_b}) != (1, 2)"

        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE document_uploads
                   SET extraction_status = 'duplicate',
                       dup_of_upload_id  = %s::uuid,
                       series_id         = NULL,
                       version_no        = NULL
                 WHERE id = %s::uuid
                """,
                (uid_a, uid_b),
            )
        conn.commit()

        # v3 logically: new upload with different content. Since the
        # tombstone freed version_no=2, this should reuse it.
        _, s_c, v_c = _insert_upload(
            conn, filename, hashlib.sha256(b"c" + run_marker.encode()).hexdigest()
        )
        if s_c != series_id:
            return False, f"third insert got different series_id: {s_c} != {series_id}"
        if v_c != 2:
            return False, f"third insert got version_no={v_c}, expected 2 (freed by tombstone)"

        # Versions list (active only) should be [1, 2].
        with conn.cursor() as cur:
            cur.execute(
                "SELECT version_no FROM document_uploads "
                " WHERE series_id = %s::uuid ORDER BY version_no",
                (series_id,),
            )
            active = [r[0] for r in cur.fetchall()]
        if active != [1, 2]:
            return False, f"active version list wrong: {active}, expected [1, 2]"

        return True, "tombstone freed version slot; next insert reused version_no=2"
    finally:
        _cleanup(conn, filename)
        conn.close()


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[FAIL] DATABASE_URL not set")
        return 1

    print("─" * 70)
    print("  Upload versioning — Stage 2 (schema_v20)")
    print("─" * 70)

    failures = 0

    for name, fn in [
        ("Sequential versions (v1, v2, v3)",        test_sequential_versions),
        ("Duplicate (series_id, version_no) blocked", test_duplicate_version_no_blocked),
        ("Dup tombstone frees version slot",        test_dup_tombstone_frees_version_slot),
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
