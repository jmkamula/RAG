"""
Ship 126'.b — backfill PII redaction on 3 diagnostic-log tables.

Runs the SAME `rag.posture.pii_redactor.redact_pii()` the write path
now applies at insert time, over existing rows that landed BEFORE
Ship 126'.b shipped. Idempotent — re-redaction of an already-redacted
row is a no-op (pii_redactor is idempotent by design; tested in
tests/test_pii_redactor.py::test_idempotent_default).

Runs as arioncomply owner (ARION_OWNER_PW) because the tables have
UPDATE revoked from arioncomply_app (Ship 4'.b addendum, verified
Ship 121').

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/ops/backfill_pii_redaction.py
    # or with a specific table:
    PYTHONPATH=/data/arioncomply python3 scripts/ops/backfill_pii_redaction.py --table ai_call_log

Loads .env via python-dotenv (Ship 111' canonical scheme — bash never
sources .env because customer .env can have bash-unsafe chars).
"""
from __future__ import annotations

import argparse
import os
import sys
import time

try:
    from dotenv import load_dotenv
    load_dotenv('/data/arioncomply/.env')
except ImportError:
    pass

import psycopg2

from rag.posture.pii_redactor import redact_pii


BATCH_SIZE = 500

# (table, id_col, [(col_name, is_json_null_ok)]) — columns that need
# redaction on each row. `is_json_null_ok` is unused today; kept as a
# forward hook if any of the redacted columns become JSONB later.
TABLES = {
    'ai_call_log': ('id', ['prompt_preview', 'response_preview']),
    'chat_consensus_log': ('id', ['query']),
    'chat_casefile_log': ('id', ['query', 'answer_text']),
}


def _connect():
    return psycopg2.connect(
        host=os.environ.get('PGHOST', '127.0.0.1'),
        port=int(os.environ.get('PGPORT', 5432)),
        dbname='arioncomply_compliance',
        user='arioncomply',
        password=os.environ['ARION_OWNER_PW'],
    )


def backfill_table(conn, table: str, id_col: str, cols: list[str]) -> tuple[int, int]:
    """Backfill one table. Returns (rows_scanned, rows_updated)."""
    sel_cols = ', '.join([id_col] + cols)
    scanned = 0
    updated = 0
    last_id = None

    while True:
        with conn.cursor() as cur:
            if last_id is None:
                cur.execute(
                    f"SELECT {sel_cols} FROM public.{table} "
                    f"ORDER BY {id_col} LIMIT %s",
                    (BATCH_SIZE,),
                )
            else:
                cur.execute(
                    f"SELECT {sel_cols} FROM public.{table} "
                    f"WHERE {id_col} > %s ORDER BY {id_col} LIMIT %s",
                    (last_id, BATCH_SIZE),
                )
            rows = cur.fetchall()

        if not rows:
            break

        with conn.cursor() as cur:
            for row in rows:
                scanned += 1
                row_id = row[0]
                originals = row[1:]

                # Redact each column; if none actually changed, skip UPDATE
                redacted = [
                    redact_pii(v) if isinstance(v, str) else v
                    for v in originals
                ]
                if redacted == list(originals):
                    last_id = row_id
                    continue

                set_clause = ', '.join(f"{c} = %s" for c in cols)
                cur.execute(
                    f"UPDATE public.{table} SET {set_clause} WHERE {id_col} = %s",
                    (*redacted, row_id),
                )
                updated += 1
                last_id = row_id

        conn.commit()
        if scanned % 5000 == 0:
            print(f"  {table}: scanned={scanned:,} updated={updated:,}", flush=True)

    return scanned, updated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', choices=list(TABLES.keys()) + ['all'], default='all')
    ap.add_argument('--dry-run', action='store_true',
                    help='Count changes without writing')
    args = ap.parse_args()

    if 'ARION_OWNER_PW' not in os.environ:
        print("ERROR: ARION_OWNER_PW not set (needed to UPDATE audit-log tables)",
              file=sys.stderr)
        return 78

    targets = [args.table] if args.table != 'all' else list(TABLES.keys())

    conn = _connect()
    try:
        start = time.time()
        for tbl in targets:
            id_col, cols = TABLES[tbl]
            print(f"\n=== {tbl} ({', '.join(cols)}) ===", flush=True)
            if args.dry_run:
                # Dry-run: sample 100 rows, count how many WOULD change
                sample_cols = ', '.join([id_col] + cols)
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT {sample_cols} FROM public.{tbl} "
                        f"ORDER BY {id_col} DESC LIMIT 100"
                    )
                    rows = cur.fetchall()
                would_change = sum(
                    1 for row in rows
                    if [redact_pii(v) if isinstance(v, str) else v for v in row[1:]]
                       != list(row[1:])
                )
                print(f"  DRY-RUN sample (100 recent): {would_change} rows would change")
            else:
                scanned, updated = backfill_table(conn, tbl, id_col, cols)
                elapsed = time.time() - start
                print(f"  {tbl}: scanned={scanned:,} updated={updated:,} "
                      f"({elapsed:.1f}s cumulative)", flush=True)
    finally:
        conn.close()

    print("\nBackfill complete.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
