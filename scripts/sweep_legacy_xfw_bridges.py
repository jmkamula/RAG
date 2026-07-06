"""
ArionComply — Sweep legacy PROGRAM/EXTENSION → OBLIGATION xfw_bridge findings

After Phase 5 of the framework role model refactor (2026-07-05),
xfw_proposer no longer writes NEW xfw_bridge findings for the
PROGRAM/EXTENSION → OBLIGATION direction — those are handled
deterministically by DEMONSTRATES propagation in the posture loader
(Phase 2b/2c). But existing pending xfw_bridge findings from before
Phase 5 still sit in the review queue.

This script marks those legacy rows rejected + is_active=false with
an audit-preserving rationale: "handled by DEMONSTRATES propagation
(Phase 2c)". Non-obligation-target bridges (EXTENSION↔PROGRAM,
OBLIGATION→PROGRAM reverse-nav) are LEFT ALONE — those still
represent legitimate cross-framework proposals in the new model.

Idempotent: only touches rows still review_status='pending' and
is_active=TRUE.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/sweep_legacy_xfw_bridges.py --tenant <uuid>
    PYTHONPATH=/data/arioncomply python3 scripts/sweep_legacy_xfw_bridges.py --tenant <uuid> --dry-run
"""
from __future__ import annotations
import argparse
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv("/data/arioncomply/.env")


_RATIONALE = (
    "sweep_legacy_xfw_bridges: handled by DEMONSTRATES propagation "
    "(framework role model Phase 2c); xfw_bridge for PROGRAM/EXTENSION "
    "→ OBLIGATION direction retired by Phase 5"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant", required=True,
                    help="Tenant UUID to sweep")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show counts only, don't write")
    args = ap.parse_args()

    conn = psycopg2.connect(
        host="127.0.0.1",
        user="arioncomply",
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname="arioncomply_compliance",
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (args.tenant,))

            # Sweep target: xfw_bridge findings where target standard is an
            # OBLIGATION (currently GDPR only, but the join keeps this
            # generalisable to future obligations like NIS2, DORA).
            cur.execute(
                """
                SELECT df.id, df.control_ref, df.standard_id,
                       df.inferred_from_control_ref,
                       df.inferred_from_standard_id
                  FROM document_findings df
                  JOIN standards s ON s.id = df.standard_id
                 WHERE df.tenant_id       = %s::uuid
                   AND df.is_active       = TRUE
                   AND df.review_status   = 'pending'
                   AND df.inference_source = 'xfw_bridge'
                   AND s.role             = 'obligation'
                """,
                (args.tenant,),
            )
            rows = cur.fetchall()
            print(f"Candidate rows to sweep: {len(rows)}")

            if not rows:
                return 0

            # Break down by (from_std, to_std) for the report
            groups: dict = {}
            for _, _, tgt_std, _, from_std in rows:
                key = (from_std, tgt_std)
                groups[key] = groups.get(key, 0) + 1
            for (from_std, tgt_std), n in sorted(groups.items()):
                print(f"  {from_std} → {tgt_std}: {n}")

            if args.dry_run:
                print("\n[dry-run] not writing")
                return 0

            ids = [r[0] for r in rows]
            cur.execute(
                """
                UPDATE document_findings
                   SET is_active        = FALSE,
                       review_status    = 'rejected',
                       rejection_reason = %s,
                       reviewed_at      = NOW()
                 WHERE tenant_id = %s::uuid
                   AND id = ANY(%s::uuid[])
                """,
                (_RATIONALE, args.tenant, ids),
            )
            print(f"\n✓ swept {cur.rowcount} rows (rationale: {_RATIONALE[:60]}...)")

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
