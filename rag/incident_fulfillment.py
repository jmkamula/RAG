"""
ArionComply — Incident Obligation Fulfillment Checker

Flips `incident_obligations.is_met` to TRUE when a document linked to the
incident satisfies the obligation's :DocumentRequirement.

Architecture:
  Per-obligation, look up Neo4j :DocumentRequirement(s) for the obligation's
  (standard_id, control_ref) pair. The DocumentRequirement carries a
  `document_type` (e.g. 'breach_notification', 'risk_assessment'). Then check
  Postgres incident_documents → client_documents: is there a linked document
  with matching client_documents.document_type? If yes → mark obligation met.

Behavioural rules:
  - Additive only: never flip met=TRUE back to FALSE. Matches
    [[incident-obligations-model]]: obligations are an audit-defensible record.
  - Skip obligations with no :DocumentRequirement in Neo4j — these stay
    manual-only; a curator confirms them via separate workflow (e.g.,
    A.5.26 'Invoke incident response procedure' has no doc-type to match).
  - Idempotent: re-running is a no-op if state is already consistent.
  - Cross-vocabulary match: obligation.control_ref is the full ref like
    'ISO27001:2022:6.1.2' or 'GDPR:2016/679:Art.33'; the DocumentRequirement
    holds the suffix ('6.1.2', 'Art.33') and standard separately. We split
    on the last ':' to bridge.

Usage:
  python3 rag/incident_fulfillment.py --tenant <UUID>             # all incidents
  python3 rag/incident_fulfillment.py --tenant <UUID> --incident <UUID>
  python3 rag/incident_fulfillment.py --tenant <UUID> --dry-run
  python3 rag/incident_fulfillment.py --tenant <UUID> --verify    # status only

Library use:
  from rag.incident_fulfillment import IncidentFulfillmentChecker
  result = IncidentFulfillmentChecker(pg, neo4j).check_for_incident(inc_id, tenant_id)
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# =============================================================================
# Result reporting
# =============================================================================

@dataclass
class FulfillmentResult:
    incident_id:          UUID
    obligations_checked:  int  = 0
    obligations_newly_met: int = 0
    obligations_already_met: int = 0
    obligations_no_doc_req: int = 0   # no :DocumentRequirement in Neo4j — manual only
    obligations_pending:  int  = 0    # has doc-req, but no matching document linked
    errors:               list[str] = field(default_factory=list)

    def merged_with(self, other: "FulfillmentResult") -> None:
        self.obligations_checked     += other.obligations_checked
        self.obligations_newly_met   += other.obligations_newly_met
        self.obligations_already_met += other.obligations_already_met
        self.obligations_no_doc_req  += other.obligations_no_doc_req
        self.obligations_pending     += other.obligations_pending
        self.errors                  += other.errors


# =============================================================================
# Fulfillment checker
# =============================================================================

class IncidentFulfillmentChecker:
    """Updates `incident_obligations.is_met` from linked documents."""

    def __init__(self, pg_conn, neo4j_driver):
        self._pg    = pg_conn
        self._neo4j = neo4j_driver

    # ── Public API ──────────────────────────────────────────────────────────

    def check_for_incident(
        self,
        incident_id: UUID,
        tenant_id:   UUID,
        dry_run:     bool = False,
    ) -> FulfillmentResult:
        """Walk all obligations on one incident; flip is_met where applicable."""
        result = FulfillmentResult(incident_id=incident_id)

        # Set RLS tenant context — TRUE = transaction-local, auto-clears
        # on commit/rollback. Required when the connection is not via a
        # superuser/BYPASSRLS role (e.g. arioncomply_app from pg pool).
        with self._pg.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (str(tenant_id),))

        obligations = self._fetch_obligations(incident_id, tenant_id)
        result.obligations_checked = len(obligations)
        if not obligations:
            return result

        for o in obligations:
            if o['is_met']:
                result.obligations_already_met += 1
                continue

            doc_types = self._fetch_required_doc_types(
                o['control_ref'], o['standard_id'])
            if not doc_types:
                result.obligations_no_doc_req += 1
                continue

            satisfied = self._has_linked_doc(
                incident_id, tenant_id, doc_types)
            if not satisfied:
                result.obligations_pending += 1
                continue

            if not dry_run:
                self._mark_met(
                    incident_id, tenant_id,
                    o['control_ref'], o['standard_id'])
            result.obligations_newly_met += 1

        if not dry_run:
            self._pg.commit()

        return result

    def check_for_tenant(
        self,
        tenant_id: UUID,
        dry_run:   bool = False,
    ) -> dict[UUID, FulfillmentResult]:
        """Walk all incidents in a tenant; return per-incident results."""
        # _list_incidents reads incidents (tenant-scoped) so it also
        # needs the RLS context. check_for_incident sets it per call
        # because each call may be on a fresh transaction.
        with self._pg.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (str(tenant_id),))
        results: dict[UUID, FulfillmentResult] = {}
        for incident_id in self._list_incidents(tenant_id):
            results[incident_id] = self.check_for_incident(
                incident_id, tenant_id, dry_run=dry_run)
        return results

    # ── Postgres reads ──────────────────────────────────────────────────────

    def _fetch_obligations(self, incident_id: UUID, tenant_id: UUID) -> list[dict]:
        with self._pg.cursor() as cur:
            cur.execute("""
                SELECT control_ref, standard_id, is_met
                FROM incident_obligations
                WHERE incident_id = %s AND tenant_id = %s
            """, (str(incident_id), str(tenant_id)))
            return [
                {'control_ref': r[0], 'standard_id': r[1], 'is_met': r[2]}
                for r in cur.fetchall()
            ]

    def _list_incidents(self, tenant_id: UUID) -> list[UUID]:
        with self._pg.cursor() as cur:
            cur.execute("""
                SELECT id FROM incidents
                WHERE tenant_id = %s AND is_active = TRUE
                ORDER BY occurred_at NULLS LAST
            """, (str(tenant_id),))
            return [r[0] for r in cur.fetchall()]

    def _has_linked_doc(
        self,
        incident_id: UUID,
        tenant_id:   UUID,
        doc_types:   list[str],
    ) -> bool:
        with self._pg.cursor() as cur:
            cur.execute("""
                SELECT 1
                FROM incident_documents id
                JOIN client_documents  cd ON cd.id = id.document_id
                WHERE id.incident_id = %s
                  AND id.tenant_id   = %s
                  AND id.is_active   = TRUE
                  AND cd.document_type = ANY(%s)
                LIMIT 1
            """, (str(incident_id), str(tenant_id), doc_types))
            return cur.fetchone() is not None

    def _mark_met(
        self,
        incident_id: UUID,
        tenant_id:   UUID,
        control_ref: str,
        standard_id: str,
    ) -> None:
        with self._pg.cursor() as cur:
            cur.execute("""
                UPDATE incident_obligations
                   SET is_met = TRUE,
                       met_at = NOW()
                 WHERE incident_id = %s
                   AND tenant_id   = %s
                   AND control_ref = %s
                   AND standard_id = %s
                   AND is_met      = FALSE
            """, (str(incident_id), str(tenant_id), control_ref, standard_id))

    # ── Neo4j read ──────────────────────────────────────────────────────────

    def _fetch_required_doc_types(
        self,
        control_ref: str,        # e.g., "ISO27001:2022:6.1.2"
        standard_id: str,        # e.g., "ISO27001:2022"
    ) -> list[str]:
        """
        :DocumentRequirement.standard_id holds the full standard
        (e.g. 'ISO27001:2022'), and .control_ref holds only the suffix
        (e.g. '6.1.2', 'Art.33'). Split the obligation's full ref to bridge.
        """
        if not control_ref or ':' not in control_ref:
            return []
        # Split rightmost ':' — keeps versioned standard_ids like
        # 'GDPR:2016/679' intact and gives us 'Art.33' as the suffix.
        ref_std, _, ctl_suffix = control_ref.rpartition(':')
        if ref_std != standard_id:
            # Sanity check — obligation table has both; if they disagree,
            # the obligation row is malformed. Skip rather than guess.
            return []

        with self._neo4j.session() as s:
            r = s.run("""
                MATCH (rd:DocumentRequirement {
                        standard_id: $std,
                        control_ref: $suffix
                      })
                WHERE rd.document_type IS NOT NULL
                RETURN DISTINCT rd.document_type AS dt
            """, std=standard_id, suffix=ctl_suffix)
            return [row['dt'] for row in r if row['dt']]


# =============================================================================
# CLI
# =============================================================================

def _connect_pg():
    from rag.posture_loader import build_pg_conn
    return build_pg_conn()


def _connect_neo4j():
    from neo4j import GraphDatabase
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')),
    )


def _print_result(incident_id: UUID, r: FulfillmentResult) -> None:
    print(f"\nIncident {incident_id}")
    print(f"  obligations checked:      {r.obligations_checked}")
    print(f"  already met:              {r.obligations_already_met}")
    print(f"  newly met:                {r.obligations_newly_met}")
    print(f"  pending (doc not linked): {r.obligations_pending}")
    print(f"  no doc requirement:       {r.obligations_no_doc_req} (manual only)")
    for e in r.errors:
        print(f"  ✗ {e}")


def _verify(pg_conn, tenant_id: UUID) -> None:
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    (str(tenant_id),))
        cur.execute("""
            SELECT
              i.external_ref, i.title,
              count(o.*)                          AS total_obligations,
              count(o.*) FILTER (WHERE o.is_met)  AS met_obligations,
              count(id.*)                         AS linked_documents
            FROM incidents i
            LEFT JOIN incident_obligations o ON o.incident_id = i.id
            LEFT JOIN incident_documents id ON id.incident_id = i.id AND id.is_active
            WHERE i.tenant_id = %s AND i.is_active
            GROUP BY i.id, i.external_ref, i.title
            ORDER BY i.external_ref
        """, (str(tenant_id),))
        rows = cur.fetchall()
    print("\nTenant fulfillment status:")
    print(f"  {'ref':10s} {'title':28s} {'oblig.':>6s} {'met':>4s} {'docs':>5s}")
    for r in rows:
        print(f"  {r[0]:10s} {(r[1] or '')[:28]:28s} {r[2]:>6d} {r[3]:>4d} {r[4]:>5d}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tenant',   required=True, help='tenant UUID')
    parser.add_argument('--incident', help='single incident UUID (default: all in tenant)')
    parser.add_argument('--dry-run',  action='store_true', help='preview without writing')
    parser.add_argument('--verify',   action='store_true',
                        help='print fulfillment status; no writes')
    args = parser.parse_args()

    pg     = _connect_pg()
    neo4j  = _connect_neo4j()
    tenant = UUID(args.tenant)

    try:
        if args.verify:
            _verify(pg, tenant)
            return

        c = IncidentFulfillmentChecker(pg, neo4j)
        if args.incident:
            r = c.check_for_incident(UUID(args.incident), tenant, dry_run=args.dry_run)
            _print_result(UUID(args.incident), r)
        else:
            results = c.check_for_tenant(tenant, dry_run=args.dry_run)
            agg = FulfillmentResult(incident_id=tenant)
            for inc_id, r in results.items():
                _print_result(inc_id, r)
                agg.merged_with(r)
            print(f"\n{'─'*55}")
            print(f"Total incidents: {len(results)}")
            print(f"  checked:           {agg.obligations_checked}")
            print(f"  newly met:         {agg.obligations_newly_met}"
                  + (" (dry-run)" if args.dry_run else ""))
            print(f"  already met:       {agg.obligations_already_met}")
            print(f"  pending:           {agg.obligations_pending}")
            print(f"  no doc req:        {agg.obligations_no_doc_req}")
    finally:
        pg.close()
        neo4j.close()


if __name__ == "__main__":
    main()
