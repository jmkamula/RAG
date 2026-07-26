#!/usr/bin/env python3
"""Ship 46'.b — backfill evidence_group_id on pre-Ship-42 document_findings rows.

Ship 42'.b stamped evidence_group_id on fresh writes; legacy rows have
NULL. Surface layer filters use `COALESCE(evidence_group_id, id::text)`
so legacy rows still show (each as its own group). Retroactively
computing the group_id lets legacy rows dedupe correctly in Stage-1
queue counts + related-card renders.

Idempotent: only updates rows where evidence_group_id IS NULL.
Silent no-op on rows with empty excerpt (matches writer behavior).

Usage:
    python3 scripts/backfill_evidence_group_id.py [--tenant UUID] [--dry-run]

Reuses the same normalisation + hash function as posture_writer so
backfilled rows collide with fresh-writer rows on identical
(document_id, control_ref, normalized_excerpt) tuples.
"""
from __future__ import annotations

import argparse
import os
import sys

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, "/data/arioncomply")
from rag.intake.posture_writer import _evidence_group_id


def backfill(dsn: str, tenant_filter: str | None = None, dry_run: bool = False) -> None:
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    where = "df.evidence_group_id IS NULL AND df.excerpt IS NOT NULL AND df.excerpt <> ''"
    params: list = []
    if tenant_filter:
        where += " AND df.tenant_id = %s::uuid"
        params.append(tenant_filter)

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""SELECT df.id::text, df.document_id::text,
                          df.control_ref, df.excerpt
                     FROM document_findings df
                    WHERE {where}""",
                params,
            )
            rows = cur.fetchall()
        print(f"scanning {len(rows)} rows with NULL evidence_group_id")

        by_id: dict[str, str] = {}
        for finding_id, doc_id, control_ref, excerpt in rows:
            gid = _evidence_group_id(doc_id, control_ref, excerpt)
            if gid:
                by_id[finding_id] = gid
        print(f"computed group_id for {len(by_id)} rows")

        if dry_run:
            # Sample a couple + report
            for i, (fid, gid) in enumerate(list(by_id.items())[:5]):
                print(f"  {fid} -> {gid}")
            distinct_groups = len(set(by_id.values()))
            print(f"distinct groups: {distinct_groups}")
            print(f"collapse ratio: "
                  f"{100 * (1 - distinct_groups / len(by_id)):.1f}% "
                  f"({len(by_id)} rows -> {distinct_groups} groups)")
            return

        with conn.cursor() as cur:
            for fid, gid in by_id.items():
                cur.execute(
                    "UPDATE document_findings SET evidence_group_id = %s "
                    "WHERE id = %s::uuid AND evidence_group_id IS NULL",
                    (gid, fid),
                )
        conn.commit()
        print(f"COMMITTED — {len(by_id)} rows updated")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    load_dotenv("/data/arioncomply/.env")
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise SystemExit("DATABASE_URL not set")

    p = argparse.ArgumentParser(description="Backfill evidence_group_id on legacy findings.")
    p.add_argument("--tenant", help="restrict to this tenant UUID")
    p.add_argument("--dry-run", action="store_true", help="report without writing")
    args = p.parse_args()

    backfill(dsn, tenant_filter=args.tenant, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
