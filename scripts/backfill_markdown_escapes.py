#!/usr/bin/env python3
# ruff: noqa: W605
r"""
Ship 8'.a (2026-07-20) — one-shot backfill for backslash-escaped
markdown punctuation surviving in stored prose.

Motivation (see [[ship-7-prime-d-evaluation-checkpoint-2026-07-19]]):
Ship 7'.d added `strip_markdown_escapes` to the output gateway
so external API + Evidence Package + Stage-2 surfaces render
cleanly. But the DB rows themselves still contain the raw `\-`,
`\(`, `\.` artifacts. Any code path not routed through the
gateway (admin psql queries, older internal surfaces, log-lines,
support tooling) still sees them.

This script strips at write time so all downstream readers see
clean data, not just the migrated surfaces.

Tables touched:
  posture_controls  (gap_description, action_required)
  document_findings (excerpt)

Both use the same idempotent `strip_markdown_escapes` transform
from `rag.output.transforms`. Safe to re-run — post-scrub rows
match no more.

Usage:
  # Dry-run — report counts, no writes
  PYTHONPATH=/data/arioncomply python3 scripts/backfill_markdown_escapes.py --dry-run

  # Apply
  PYTHONPATH=/data/arioncomply python3 scripts/backfill_markdown_escapes.py

  # Scoped to one tenant
  PYTHONPATH=/data/arioncomply python3 scripts/backfill_markdown_escapes.py \\
    --tenant 00000000-0000-0000-0000-000000000001
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import psycopg2
import psycopg2.extras

from rag.output import strip_markdown_escapes


# Postgres regex matching the same character class as
# rag.output.transforms._MD_ESCAPE_RE. Used to filter which rows
# have work to do; the actual scrub uses the Python transform to
# guarantee identical semantics.
_PG_MATCH = r"\\[-().*+_\[\]!|<>#{}`~]"


def _connect():
    return psycopg2.connect(
        host     = os.getenv("PGHOST",     "127.0.0.1"),
        dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
        user     = os.getenv("PGUSER",     "arioncomply"),   # superuser to bypass RLS
        password = os.getenv("PGPASSWORD", ""),
    )


def _backfill_posture_controls(
    conn, tenant_filter: Optional[str], dry_run: bool,
) -> tuple[int, int]:
    """Scrub `gap_description` + `action_required`. Returns
    `(rows_scanned, rows_updated)`."""
    scanned = updated = 0
    where = f"(gap_description ~ %s OR action_required ~ %s)"
    params: list = [_PG_MATCH, _PG_MATCH]
    if tenant_filter:
        where += " AND tenant_id = %s::uuid"
        params.append(tenant_filter)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT tenant_id, control_ref, standard_id,
                   gap_description, action_required
              FROM posture_controls
             WHERE {where}
            """,
            tuple(params),
        )
        rows = cur.fetchall()
        scanned = len(rows)

        for r in rows:
            new_gap    = strip_markdown_escapes(r["gap_description"] or "")
            new_action = strip_markdown_escapes(r["action_required"] or "")
            if (new_gap    == (r["gap_description"] or "")
                and new_action == (r["action_required"] or "")):
                continue      # no-op — belt-and-braces against SQL regex FP
            if not dry_run:
                cur.execute(
                    """
                    UPDATE posture_controls
                       SET gap_description = %s,
                           action_required = %s
                     WHERE tenant_id   = %s::uuid
                       AND control_ref = %s
                       AND standard_id = %s
                    """,
                    (
                        new_gap    or None,
                        new_action or None,
                        r["tenant_id"], r["control_ref"], r["standard_id"],
                    ),
                )
            updated += 1

    return scanned, updated


def _backfill_document_findings(
    conn, tenant_filter: Optional[str], dry_run: bool,
) -> tuple[int, int]:
    """Scrub `excerpt`. Returns `(rows_scanned, rows_updated)`."""
    scanned = updated = 0
    where = "excerpt ~ %s"
    params: list = [_PG_MATCH]
    if tenant_filter:
        where += " AND tenant_id = %s::uuid"
        params.append(tenant_filter)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            f"SELECT id, excerpt FROM document_findings WHERE {where}",
            tuple(params),
        )
        rows = cur.fetchall()
        scanned = len(rows)

        for r in rows:
            new_excerpt = strip_markdown_escapes(r["excerpt"] or "")
            if new_excerpt == (r["excerpt"] or ""):
                continue
            if not dry_run:
                cur.execute(
                    "UPDATE document_findings SET excerpt = %s WHERE id = %s::uuid",
                    (new_excerpt or None, r["id"]),
                )
            updated += 1

    return scanned, updated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Report counts without writing.")
    ap.add_argument("--tenant", type=str, default=None,
                    help="Restrict to one tenant (UUID). Default: all tenants.")
    args = ap.parse_args()

    conn = _connect()
    try:
        pc_scanned, pc_updated = _backfill_posture_controls(
            conn, args.tenant, args.dry_run,
        )
        df_scanned, df_updated = _backfill_document_findings(
            conn, args.tenant, args.dry_run,
        )
        if args.dry_run:
            conn.rollback()
        else:
            conn.commit()
    finally:
        conn.close()

    print(f"posture_controls:  scanned={pc_scanned:5d}  "
          f"{'would_update' if args.dry_run else 'updated':>13s}={pc_updated:5d}")
    print(f"document_findings: scanned={df_scanned:5d}  "
          f"{'would_update' if args.dry_run else 'updated':>13s}={df_updated:5d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
