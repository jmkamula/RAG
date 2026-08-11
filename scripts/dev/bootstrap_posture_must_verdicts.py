"""
Bootstrap posture_must_verdicts for all tenants.

Ship 58'.t (2026-08-11) — one-shot to populate the SSoT table for tenants
that haven't yet triggered load_posture (e.g. no uploads, no Stage-1
approvals) since schema_v94 landed. Ordinary flows populate as soon as
a tenant triggers any load_posture path; this script closes the gap for
long-idle tenants.

Idempotent: re-running for a tenant that already has rows is safe — the
writer replaces the tenant's rows atomically inside load_posture.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/bootstrap_posture_must_verdicts.py
"""
from __future__ import annotations

import os
import sys
import time

import psycopg2


def main() -> int:
    db_url = os.getenv(
        "POSTGRES_URL",
        "postgresql://arioncomply@127.0.0.1/arioncomply_compliance",
    )

    conn = psycopg2.connect(db_url)
    with conn.cursor() as cur:
        cur.execute("SELECT id::text, name FROM tenants ORDER BY name")
        tenants = cur.fetchall()

    print(f"Bootstrapping posture_must_verdicts for {len(tenants)} tenants")
    print("-" * 70)

    from rag.posture_loader import load_posture

    ok = fail = 0
    for tid, name in tenants:
        t0 = time.time()
        eng_conn = psycopg2.connect(db_url)
        try:
            with eng_conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tid,),
                )
            load_posture(eng_conn, tid)
            with eng_conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tid,),
                )
                cur.execute(
                    "SELECT count(*) FROM posture_must_verdicts "
                    "WHERE tenant_id = %s::uuid",
                    (tid,),
                )
                n_rows = cur.fetchone()[0]
            dt_ms = int((time.time() - t0) * 1000)
            print(f"  ✓ {name[:40]:<40}  {n_rows:>5} rows  {dt_ms:>5}ms")
            ok += 1
        except Exception as e:
            dt_ms = int((time.time() - t0) * 1000)
            print(f"  ✗ {name[:40]:<40}  FAILED  {dt_ms:>5}ms  {type(e).__name__}: {e}")
            fail += 1
        finally:
            eng_conn.close()

    print("-" * 70)
    print(f"Done. ok={ok}  fail={fail}")

    conn.close()
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
