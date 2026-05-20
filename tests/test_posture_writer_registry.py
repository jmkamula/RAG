"""
Regression test: registry-placeholder filename should not survive an upload.

The document registry pre-seeds client_documents rows with placeholder filenames
of the form `DOC###_Title_Words.pdf` — always assuming PDF. When a user uploads
a real file (often a .docx) whose title fuzzy-matches the placeholder row, the
upload must overwrite the placeholder filename with the actual upload name —
otherwise auditors see a `.pdf` filename for bytes that are a .docx.

Pre-fix behaviour (posture_writer.py:247):
  SET filename = COALESCE(NULLIF(filename, ''), %s)
  → placeholder was non-empty → COALESCE preserved it → upload's real name dropped.

Post-fix behaviour:
  SET filename = CASE
                   WHEN filename ~ '^DOC[0-9]+_.*\\.pdf$' THEN %s   -- overwrite placeholder
                   ELSE COALESCE(NULLIF(filename, ''), %s)          -- preserve non-placeholder
                 END

This test covers three cases on the same code path:
  1. Placeholder filename is overwritten by the upload's real name.
  2. A non-placeholder filename is preserved (the COALESCE branch still wins).
  3. An empty filename is filled by the upload's name (COALESCE NULLIF semantics).

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_posture_writer_registry.py
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

import psycopg2

from rag.intake.posture_writer import _ensure_client_document


TENANT_ID = "00000000-0000-0000-0000-000000000001"   # Arion Networks
EXT_REF_PREFIX = "TEST_REGEXFIX_"


def _set_tenant(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (TENANT_ID,))


def _insert_registry_row(conn, doc_id: str, ext_ref: str, title: str, filename: str) -> None:
    """Pre-seed a 'registered' row exactly as the registry bootstrap would."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO client_documents (
                id, tenant_id, filename, document_title, external_ref,
                document_status, is_active, is_metadata_only,
                retention_class
            ) VALUES (
                %s::uuid, %s::uuid, %s, %s, %s,
                'registered', TRUE, TRUE,
                'compliance'
            )
            """,
            (doc_id, TENANT_ID, filename, title, ext_ref),
        )
    conn.commit()


def _read_row(conn, doc_id: str) -> tuple[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT filename, document_status FROM client_documents WHERE id = %s::uuid",
            (doc_id,),
        )
        return cur.fetchone()


def _cleanup(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM client_documents "
            " WHERE tenant_id = %s::uuid "
            "   AND external_ref LIKE %s",
            (TENANT_ID, EXT_REF_PREFIX + "%"),
        )
    conn.commit()


def test_placeholder_overwritten(conn) -> tuple[bool, str]:
    """The DOC###_*.pdf placeholder must be replaced by the upload's filename."""
    doc_id = str(uuid.uuid4())
    _insert_registry_row(
        conn, doc_id,
        ext_ref  = EXT_REF_PREFIX + "001",
        title    = "Regex Policy Document",
        filename = "DOC999_Regex_Policy_Document.pdf",   # placeholder pattern
    )
    matched_id = _ensure_client_document(TENANT_ID, "Regex Policy Document.docx", conn)
    conn.commit()
    if str(matched_id) != doc_id:
        return False, f"matched wrong row: got {matched_id}, expected {doc_id}"
    fname, status = _read_row(conn, doc_id)
    if fname != "Regex Policy Document.docx":
        return False, f"placeholder not overwritten: filename={fname!r}"
    if status != "uploaded":
        return False, f"status not transitioned to 'uploaded': got {status!r}"
    return True, "DOC999_*.pdf placeholder overwritten by 'Regex Policy Document.docx'"


def test_non_placeholder_preserved(conn) -> tuple[bool, str]:
    """A filename that doesn't match the placeholder pattern must survive."""
    doc_id = str(uuid.uuid4())
    _insert_registry_row(
        conn, doc_id,
        ext_ref  = EXT_REF_PREFIX + "002",
        title    = "Regex Sample Procedure",
        filename = "custom_filename_kept.docx",   # non-placeholder
    )
    matched_id = _ensure_client_document(TENANT_ID, "Regex Sample Procedure.pdf", conn)
    conn.commit()
    if str(matched_id) != doc_id:
        return False, f"matched wrong row: got {matched_id}, expected {doc_id}"
    fname, _ = _read_row(conn, doc_id)
    if fname != "custom_filename_kept.docx":
        return False, f"non-placeholder filename overwritten: got {fname!r}"
    return True, "non-placeholder filename 'custom_filename_kept.docx' preserved"


def test_empty_filename_filled(conn) -> tuple[bool, str]:
    """An empty filename must be filled by the upload's name (COALESCE NULLIF)."""
    doc_id = str(uuid.uuid4())
    _insert_registry_row(
        conn, doc_id,
        ext_ref  = EXT_REF_PREFIX + "003",
        title    = "Regex Empty Filename Spec",
        filename = "",
    )
    matched_id = _ensure_client_document(TENANT_ID, "Regex Empty Filename Spec.docx", conn)
    conn.commit()
    if str(matched_id) != doc_id:
        return False, f"matched wrong row: got {matched_id}, expected {doc_id}"
    fname, _ = _read_row(conn, doc_id)
    if fname != "Regex Empty Filename Spec.docx":
        return False, f"empty filename not filled: got {fname!r}"
    return True, "empty filename filled by 'Regex Empty Filename Spec.docx'"


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("[FAIL] DATABASE_URL not set")
        return 1

    conn = psycopg2.connect(db_url)
    _set_tenant(conn)
    _cleanup(conn)   # remove leftovers from any prior interrupted run

    tests = [
        test_placeholder_overwritten,
        test_non_placeholder_preserved,
        test_empty_filename_filled,
    ]

    print("─" * 70)
    print("  posture_writer registry — placeholder filename overwrite")
    print("─" * 70)
    failures = 0
    try:
        for fn in tests:
            ok, msg = fn(conn)
            print(f"  [{'PASS' if ok else 'FAIL'}] {fn.__name__}")
            print(f"         {msg}")
            if not ok:
                failures += 1
    finally:
        _cleanup(conn)
        conn.close()

    print("─" * 70)
    print(f"  {len(tests) - failures}/{len(tests)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
