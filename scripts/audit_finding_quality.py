#!/usr/bin/env python3
"""
Ship 27'.b — Finding-quality audit.

Read-only Postgres survey of extraction quality across specific
documents. Focus on the Ship 10 5-doc set (the corpus that
Ship 11'.e + Ship 17'.d measured extraction volume against) or any
custom set of client_documents by filename.

Signals reported:
  * ACTIVE-FINDING count per doc (post-supersession)
  * ALL-TIME finding count per doc (including soft-deleted)
  * Review status: approved / pending
  * Grounding method: extractor_verbatim / fingerprint / template /
                      workbook / leaf_scan / unknown
  * Inference source: extracted / templated / workbook / form
  * Deletion reasons for soft-deleted findings (surfaces
    development-time supersessions vs tenant-authored rejects)

Usage
    PYTHONPATH=/data/arioncomply python3 scripts/audit_finding_quality.py
    PYTHONPATH=/data/arioncomply python3 scripts/audit_finding_quality.py --tenant <uuid>
    PYTHONPATH=/data/arioncomply python3 scripts/audit_finding_quality.py --docs "doc1.docx" "doc2.docx"

Read-only; safe to run against production. No writes, no mutations.
"""
from __future__ import annotations
import argparse
import os
import psycopg2
from dotenv import load_dotenv


# Ship 10 5-doc corpus (identified by client_documents.filename)
SHIP10_5_DOC_CORPUS = [
    "Data Quality Accuracy Procedure.docx",
    "Data Protection Impact Assessment (DPIA) Procedure.docx",
    "Records of Processing Activities.docx",
    "Consent Management Procedure.docx",
    "Processor Operations Procedures.docx",
]

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _connect():
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    return psycopg2.connect(
        host     = os.getenv("PGHOST",     "127.0.0.1"),
        dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
        user     = os.getenv("PGUSER",     "arioncomply_app"),
        password = os.getenv("PGPASSWORD", ""),
    )


def _set_tenant(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute("SET LOCAL app.tenant_id = %s", (tenant_id,))


def per_doc_summary(conn, doc_filenames):
    """Active + all-time + review-status per doc."""
    with conn.cursor() as cur:
        cur.execute("""
          SELECT
            c.filename,
            count(f.*)                                                      AS all_time,
            count(*) FILTER (WHERE f.is_active = true)                      AS active,
            count(*) FILTER (WHERE f.is_active = false)                     AS soft_deleted,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.review_status = 'approved')             AS active_approved,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.review_status = 'pending')              AS active_pending
          FROM document_findings f
          JOIN client_documents  c ON c.id = f.document_id
          WHERE c.filename = ANY(%s)
          GROUP BY c.filename
          ORDER BY c.filename
        """, (doc_filenames,))
        return cur.fetchall()


def per_doc_grounding(conn, doc_filenames):
    """Active findings by grounding_method."""
    with conn.cursor() as cur:
        cur.execute("""
          SELECT
            c.filename,
            count(f.*)                                                                      AS active,
            count(*) FILTER (WHERE f.grounding_method = 'extractor_verbatim')               AS verbatim,
            count(*) FILTER (WHERE f.grounding_method = 'fingerprint')                      AS fingerprint,
            count(*) FILTER (WHERE f.grounding_method = 'template')                         AS template_gm,
            count(*) FILTER (WHERE f.grounding_method = 'workbook')                         AS workbook_gm,
            count(*) FILTER (WHERE f.grounding_method = 'leaf_scan')                        AS leaf_scan,
            count(*) FILTER (WHERE f.grounding_method IN ('unknown', 'manual', 'form')
                            OR f.grounding_method IS NULL)                                  AS other
          FROM document_findings f
          JOIN client_documents  c ON c.id = f.document_id
          WHERE c.filename = ANY(%s)
            AND f.is_active = true
          GROUP BY c.filename
          ORDER BY c.filename
        """, (doc_filenames,))
        return cur.fetchall()


def deletion_reason_hist(conn, doc_filenames):
    """Deletion reasons across all soft-deleted findings on the doc set.

    Surfaces development-time supersessions (critic_ab_run, wave*-fix)
    vs tenant-authored HITL rejects."""
    with conn.cursor() as cur:
        cur.execute("""
          SELECT
            coalesce(f.deletion_reason, '(null)') AS reason,
            count(*) AS n
          FROM document_findings f
          JOIN client_documents  c ON c.id = f.document_id
          WHERE c.filename = ANY(%s)
            AND f.is_active = false
          GROUP BY f.deletion_reason
          ORDER BY count(*) DESC
          LIMIT 15
        """, (doc_filenames,))
        return cur.fetchall()


def totals(conn, doc_filenames):
    """Corpus-level rollup."""
    with conn.cursor() as cur:
        cur.execute("""
          SELECT
            count(f.*)                                                    AS all_time,
            count(*) FILTER (WHERE f.is_active = true)                    AS active,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.review_status = 'approved')           AS active_approved,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.review_status = 'pending')            AS active_pending,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.grounding_method = 'extractor_verbatim') AS verbatim,
            count(*) FILTER (WHERE f.is_active = true
                              AND f.grounding_method = 'fingerprint')     AS fingerprint,
            count(*) FILTER (WHERE f.is_active = true
                              AND (f.grounding_method IS NULL
                                   OR f.grounding_method = 'unknown'))    AS unknown_ground
          FROM document_findings f
          JOIN client_documents  c ON c.id = f.document_id
          WHERE c.filename = ANY(%s)
        """, (doc_filenames,))
        return cur.fetchone()


def print_report(conn, doc_filenames):
    print("═" * 76)
    print(" Ship 27 — Finding-quality audit")
    print("═" * 76)
    print(f" Corpus: {len(doc_filenames)} document(s)")
    for d in doc_filenames:
        print(f"   • {d}")
    print()

    # Per-doc summary
    print("── Per-doc: all-time / active / soft-deleted / approved / pending ────")
    rows = per_doc_summary(conn, doc_filenames)
    print(f"  {'doc':60s}  {'all':>5s}  {'act':>4s}  {'del':>5s}  {'apr':>4s}  {'pend':>4s}")
    for r in rows:
        fname, all_t, active, deleted, approved, pending = r
        print(f"  {fname[:60]:60s}  {all_t:5d}  {active:4d}  {deleted:5d}  {approved:4d}  {pending:4d}")
    print()

    # Per-doc grounding
    print("── Active findings by grounding method ─────────────────────────────────")
    rows = per_doc_grounding(conn, doc_filenames)
    print(f"  {'doc':60s}  {'act':>4s}  {'vrb':>4s}  {'fp':>4s}  {'tpl':>4s}  {'wb':>4s}  {'ls':>4s}  {'oth':>4s}")
    for r in rows:
        fname, active, vrb, fp, tpl, wb, ls, oth = r
        print(f"  {fname[:60]:60s}  {active:4d}  {vrb:4d}  {fp:4d}  {tpl:4d}  {wb:4d}  {ls:4d}  {oth:4d}")
    print()

    # Corpus totals
    t = totals(conn, doc_filenames)
    all_t, active, apr, pend, verb, fp, unk = t
    reviewed = apr + 0   # rejected doesn't exist in review_status distinct set
    apr_pct = (apr / active * 100) if active else 0
    verb_pct = (verb / active * 100) if active else 0
    fp_pct   = (fp / active * 100) if active else 0
    unk_pct  = (unk / active * 100) if active else 0
    print("── Corpus rollup ────────────────────────────────────────────────────────")
    print(f"  All-time finding rows:       {all_t}")
    print(f"  Currently active:            {active}")
    print(f"  Approved (of active):        {apr}  ({apr_pct:.1f}%)")
    print(f"  Pending review:              {pend}")
    print(f"  Grounding: verbatim:         {verb}  ({verb_pct:.1f}%)")
    print(f"  Grounding: fingerprint:      {fp}  ({fp_pct:.1f}%)")
    print(f"  Grounding: unknown/null:     {unk}  ({unk_pct:.1f}%)")
    print(f"  Deterministic total:         {verb + fp}  ({(verb+fp)/active*100 if active else 0:.1f}%)")
    print()

    # Deletion reasons
    print("── Soft-deleted findings by reason ─────────────────────────────────────")
    print("   (dev-time supersessions vs tenant HITL rejects)")
    rows = deletion_reason_hist(conn, doc_filenames)
    total_del = sum(r[1] for r in rows)
    print(f"  {'reason':40s}  {'n':>5s}  {'%':>5s}")
    for reason, n in rows:
        pct = n / total_del * 100 if total_del else 0
        print(f"  {reason[:40]:40s}  {n:5d}  {pct:4.1f}%")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tenant", default=DEFAULT_TENANT,
                    help="Tenant UUID (default: Arion demo tenant)")
    ap.add_argument("--docs", nargs="+",
                    help="Custom list of document filenames (default: Ship 10 5-doc corpus)")
    args = ap.parse_args()

    docs = args.docs if args.docs else SHIP10_5_DOC_CORPUS

    conn = _connect()
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("BEGIN")
            cur.execute("SET LOCAL app.tenant_id = %s", (args.tenant,))
        print_report(conn, docs)
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
