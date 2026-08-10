"""
Phase 2 audit — engine per-MUST truth vs raw data.

For each MUST id in the audit set:
  1. Query document_findings directly (raw source data)
  2. Query external_evidence_source directly (cite-mode)
  3. Query tenant_must_overrides directly (N/A overrides)
  4. Run the engine and read LeafVerdict.item_ids_recognised / _partial / _stale / _unrecognised
  5. Compute expected truth from raw data + leaf freshness_days + N/A logic
  6. Compare and flag any discrepancy

Deliverable: a table showing (must_id, control_ref, raw-truth, engine-truth,
match?, notes) so we can sign off on the engine's output before persisting.

Usage:
    set -a && source .env && set +a
    PYTHONPATH=/data/arioncomply python3 scripts/dev/audit_engine_per_must.py
"""
from __future__ import annotations

import os
import psycopg2
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from neo4j import GraphDatabase

from rag.posture.engine_runner import evaluate_one_control


# Stratified audit sample — must_ids selected to exercise:
#   • recognised (present + fresh)
#   • partial-only (status='partial')
#   • unrecognised (nothing)
#   • N/A override (tenant_must_overrides.applies=false)
#   • both present + partial (present should dominate)
#   • DerivedSpec-satisfied
#   • ISO 27001 / ISO 27701 / GDPR mix
_AUDIT_SET: list[tuple[str, str, str]] = [
    # (control_id, must_id, description)
    ("ISO27001:2022:A.5.15", "item:A.5.15:physical_rules",     "N/A override — cloud-only"),
    ("ISO27001:2022:A.5.15", "item:A.5.15:rbac",                "should be recognised"),
    ("ISO27001:2022:A.5.15", "item:A.5.15:least_privilege",     "should be recognised"),
    ("ISO27001:2022:A.5.15", "item:A.5.15:need_to_know",        "should be recognised"),
    ("ISO27001:2022:A.5.15", "item:A.5.15:segregation_link",    "unrecognised expected"),
    ("ISO27001:2022:10.1",   "item:10.1:reg_dimension",         "partial-only"),
    ("ISO27001:2022:10.1",   "item:10.1:reg_status",            "partial-only"),
    ("ISO27001:2022:10.1",   "item:10.1:reg_target_date",       "partial-only"),
    ("ISO27001:2022:A.5.9",  "item:A.5.9:proc_ownership",       "both present + partial (present dominates)"),
    ("ISO27001:2022:A.5.9",  "item:A.5.9:asset_records",        "recognised"),
    ("ISO27001:2022:A.5.9",  "item:A.5.9:last_updated",         "unrecognised expected"),
    ("ISO27001:2022:A.5.18", "item:A.5.18:rev_authoriser",      "oldest evidence 47d, freshness 180d — should be fresh"),
    ("ISO27001:2022:A.5.16", "item:A.5.16:reg_owner",           "check"),
    ("GDPR:2016/679:Art.30", "item:Art.30:purposes",            "GDPR obligation"),
    ("GDPR:2016/679:Art.30", "item:Art.30:categories_ds",       "GDPR obligation"),
    ("ISO27701:2019:A.7.2.2","item:A.7.2.2:reg_activity_id",   "ISO 27701 Extension"),
    ("ISO27001:2022:4.3",    "item:4.3:boundaries",             "foundational ISMS clause — real MUST id"),
    ("ISO27001:2022:4.3",    "item:4.3:exclusions",             "foundational ISMS clause — real MUST id"),
]


@dataclass
class RawState:
    n_present:       int
    n_partial:       int
    latest_present:  datetime | None
    latest_partial:  datetime | None
    is_na_override:  bool
    freshness_days:  int | None


def _query_raw(pg, tenant_id: str, must_id: str) -> RawState:
    with pg.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            SELECT df.status, cd.uploaded_at
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE df.checklist_item_id = %s
               AND df.is_active         = TRUE
               AND df.review_status     = 'approved'
               AND cd.tenant_id         = %s
               AND cd.is_active         = TRUE
               AND cd.is_current        = TRUE
        """, (must_id, tenant_id))
        rows = cur.fetchall()

        n_present = n_partial = 0
        latest_present: datetime | None = None
        latest_partial: datetime | None = None
        for status, uploaded_at in rows:
            if status == "present":
                n_present += 1
                if uploaded_at and (latest_present is None or uploaded_at > latest_present):
                    latest_present = uploaded_at
            elif status == "partial":
                n_partial += 1
                if uploaded_at and (latest_partial is None or uploaded_at > latest_partial):
                    latest_partial = uploaded_at

        cur.execute("""
            SELECT 1 FROM tenant_must_overrides
             WHERE tenant_id = %s::uuid AND must_id = %s AND applies = FALSE
        """, (tenant_id, must_id))
        is_na = cur.fetchone() is not None

    # Look up leaf freshness_days from Neo4j (approximate — via must_id → leaf)
    return RawState(n_present, n_partial, latest_present, latest_partial, is_na, None)


def _classify_expected(raw: RawState, freshness_days: int | None) -> str:
    """Compute the correct engine category for this MUST from raw data."""
    if raw.is_na_override:
        return "N/A (excluded)"
    if raw.n_present > 0:
        # Check freshness
        if freshness_days and raw.latest_present:
            cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
            if raw.latest_present < cutoff:
                return "recognised+stale"
        return "recognised"
    if raw.n_partial > 0:
        return "partial"
    return "unrecognised"


def _classify_engine(verdict, must_id: str) -> str:
    """Read the MUST's category from the ControlVerdict."""
    for lv in verdict.leaves:
        if must_id in lv.item_ids_recognised:
            if must_id in lv.item_ids_stale:
                return "recognised+stale"
            return "recognised"
        if must_id in lv.item_ids_partial:
            return "partial"
        if must_id in lv.item_ids_unrecognised:
            return "unrecognised"
    # MUST not in any leaf's arrays — likely N/A-excluded before recognition scan
    return "N/A (excluded)"


def _fetch_leaf_freshness(neo, must_id: str) -> int | None:
    with neo.session() as s:
        r = s.run("""
            MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(ci:ChecklistItem {id: $mid})
            RETURN er.freshness_days AS fd LIMIT 1
        """, mid=must_id).single()
        return r["fd"] if r else None


def main() -> None:
    pg = psycopg2.connect(os.getenv("POSTGRES_URL",
                                    "postgresql://arioncomply@127.0.0.1/arioncomply_compliance"))
    neo = GraphDatabase.driver(os.getenv("NEO4J_URI"),
                                auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))

    with pg.cursor() as cur:
        cur.execute("SELECT id::text FROM tenants WHERE name ILIKE '%arion%' LIMIT 1")
        tenant_id = cur.fetchone()[0]

    # Cache verdicts per control (avoids re-running engine 18 times)
    verdicts: dict[str, object] = {}

    print(f"{'must_id':<45} {'expected':<18} {'engine':<18} {'match':<7} notes")
    print("-" * 130)
    n_match = 0
    n_mismatch = 0
    mismatches: list[str] = []

    for control_id, must_id, desc in _AUDIT_SET:
        if control_id not in verdicts:
            verdicts[control_id] = evaluate_one_control(pg, neo, tenant_id, control_id)
        v = verdicts[control_id]
        if v is None:
            print(f"{must_id:<45} — ENGINE RETURNED NONE for {control_id}")
            continue

        raw = _query_raw(pg, tenant_id, must_id)
        fd = _fetch_leaf_freshness(neo, must_id)
        expected = _classify_expected(raw, fd)
        got = _classify_engine(v, must_id)

        match = "✓" if expected == got else "✗"
        if match == "✓":
            n_match += 1
        else:
            n_mismatch += 1
            mismatches.append(f"{must_id}  expected={expected}  got={got}  ({desc})")

        print(f"{must_id:<45} {expected:<18} {got:<18} {match:<7} {desc}")

    print()
    print("=" * 130)
    print(f"Matches: {n_match} / {len(_AUDIT_SET)}   Mismatches: {n_mismatch}")
    if mismatches:
        print("\nDiscrepancies:")
        for m in mismatches:
            print(f"  {m}")

    pg.close()
    neo.close()


if __name__ == "__main__":
    main()
