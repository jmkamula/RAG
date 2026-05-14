"""
ArionComply — Incident Obligations Materializer

Reads incident classifications from Postgres, resolves them through Neo4j
(:ClassificationValue -[:MANIFESTS_AS]-> :Event -[:TRIGGERS_OBLIGATION]->
:RequirementNode), and writes one obligation row per
(incident, control_ref, standard_id) into incident_obligations.

Architecture:
  Postgres incidents + incident_classifications → Neo4j (definitions) →
  Postgres incident_obligations
  See memory/incident_obligations_model.md for the locked design.

Behavioural rules:
  - Idempotent: ON CONFLICT (incident_id, control_ref, standard_id) DO NOTHING.
    Re-running adds new obligations from newly-added classifications without
    duplicating existing ones.
  - Additive-only: never deletes obligations. If a classification is removed,
    its obligations remain (multiple classifications may produce the same
    obligation). Manual cleanup is a curator operation.
  - Status-agnostic: materializes for closed incidents too. The materializer
    only records the obligation set; whether obligations were met is a
    separate concern handled by the fulfillment check (step 6).
  - Deadline precedence: TRIGGERS_OBLIGATION edge `deadline` (per-control)
    takes precedence over Event.legal_deadline (event-level headline).

Usage:
  python3 rag/incident_materializer.py --tenant <UUID>              # all incidents
  python3 rag/incident_materializer.py --tenant <UUID> --incident <UUID>
  python3 rag/incident_materializer.py --tenant <UUID> --dry-run    # preview
  python3 rag/incident_materializer.py --tenant <UUID> --verify     # count check

Library use:
  from rag.incident_materializer import IncidentMaterializer
  result = IncidentMaterializer(pg, neo4j).materialize_for_incident(inc_id, tenant_id)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# =============================================================================
# Deadline parsing
# =============================================================================

_HOURS_RE  = re.compile(r'^(\d+)\s*(h|hr|hrs|hour|hours)\s*$',  re.IGNORECASE)
_DAYS_RE   = re.compile(r'^(\d+)\s*(d|day|days)\s*$',           re.IGNORECASE)
_WEEKS_RE  = re.compile(r'^(\d+)\s*(w|week|weeks)\s*$',         re.IGNORECASE)
_MONTHS_RE = re.compile(r'^(\d+)\s*(mo|month|months)\s*$',      re.IGNORECASE)
_YEARS_RE  = re.compile(r'^(\d+)\s*(y|yr|yrs|year|years)\s*$',  re.IGNORECASE)


def compute_deadline_at(
    deadline_str: str | None,
    occurred_at:  datetime | None,
) -> datetime | None:
    """
    Parse a deadline string like '72h' or '1 month' and add it to occurred_at.

    Returns None if either input is missing or the string is semantic-only
    (e.g. 'before', 'scheduled', 'agreed with auditor'). The raw string is
    still preserved in `incident_obligations.deadline` for human display.
    """
    if not deadline_str or not occurred_at:
        return None
    s = deadline_str.strip()
    if not s:
        return None

    try:
        from dateutil.relativedelta import relativedelta
    except ImportError:
        relativedelta = None  # months/years degrade to 30/365 days

    if m := _HOURS_RE.match(s):
        return occurred_at + timedelta(hours=int(m.group(1)))
    if m := _DAYS_RE.match(s):
        return occurred_at + timedelta(days=int(m.group(1)))
    if m := _WEEKS_RE.match(s):
        return occurred_at + timedelta(weeks=int(m.group(1)))
    if m := _MONTHS_RE.match(s):
        n = int(m.group(1))
        return (occurred_at + relativedelta(months=n)) if relativedelta \
                else (occurred_at + timedelta(days=30 * n))
    if m := _YEARS_RE.match(s):
        n = int(m.group(1))
        return (occurred_at + relativedelta(years=n)) if relativedelta \
                else (occurred_at + timedelta(days=365 * n))

    # Semantic-only ('before', 'scheduled', 'varies by inquiry', etc.)
    return None


# =============================================================================
# Result reporting
# =============================================================================

@dataclass
class MaterializeResult:
    incident_id:                UUID
    classifications_seen:       int  = 0
    events_resolved:            int  = 0
    obligations_inserted:       int  = 0
    obligations_skipped:        int  = 0   # already existed (ON CONFLICT DO NOTHING)
    unresolved_classifications: list[tuple[str, str, str]] = field(default_factory=list)
    errors:                     list[str] = field(default_factory=list)

    def merged_with(self, other: "MaterializeResult") -> None:
        self.classifications_seen       += other.classifications_seen
        self.events_resolved            += other.events_resolved
        self.obligations_inserted       += other.obligations_inserted
        self.obligations_skipped        += other.obligations_skipped
        self.unresolved_classifications += other.unresolved_classifications
        self.errors                     += other.errors


# =============================================================================
# Materializer
# =============================================================================

class IncidentMaterializer:
    """Resolves incident classifications to obligation rows."""

    def __init__(self, pg_conn, neo4j_driver):
        self._pg     = pg_conn
        self._neo4j  = neo4j_driver

    # ── Public API ──────────────────────────────────────────────────────────

    def materialize_for_incident(
        self,
        incident_id: UUID,
        tenant_id:   UUID,
        dry_run:     bool = False,
    ) -> MaterializeResult:
        """Materialize obligations for one incident from its classifications."""
        result = MaterializeResult(incident_id=incident_id)

        # Set RLS tenant context — TRUE = transaction-local, auto-clears
        # on commit/rollback. Required for non-superuser connections.
        with self._pg.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (str(tenant_id),))

        incident = self._fetch_incident(incident_id, tenant_id)
        if not incident:
            result.errors.append(f"Incident {incident_id} not found or inactive")
            return result

        classifications = self._fetch_classifications(incident_id, tenant_id)
        result.classifications_seen = len(classifications)
        if not classifications:
            return result

        # Resolve via Neo4j: each classification → list of (control_ref, std,
        # deadline, rationale). Dedup by (control_ref, std); the materialiser
        # produces one row per unique key even if multiple classifications
        # binding to the same event reproduce the same obligation.
        obligations: dict[tuple[str, str], dict] = {}
        events_seen: set[str] = set()
        for cls in classifications:
            rows = self._resolve_classification(cls)
            if not rows:
                result.unresolved_classifications.append(
                    (cls['standard_id'], cls['dimension'], cls['value']))
                continue
            for row in rows:
                events_seen.add(row['event_id'])
                key = (row['control_ref'], row['req_standard_id'])
                if key not in obligations:
                    obligations[key] = row
        result.events_resolved = len(events_seen)

        # Compute deadline_at + write
        for (control_ref, std), row in obligations.items():
            deadline_at = compute_deadline_at(row['deadline'], incident['occurred_at'])
            if dry_run:
                result.obligations_inserted += 1
                continue
            inserted = self._upsert_obligation(
                incident_id  = incident_id,
                tenant_id    = tenant_id,
                control_ref  = control_ref,
                standard_id  = std,
                deadline     = row['deadline'],
                deadline_at  = deadline_at,
                rationale    = row['rationale'],
            )
            if inserted:
                result.obligations_inserted += 1
            else:
                result.obligations_skipped += 1

        if not dry_run:
            self._pg.commit()

        return result

    def materialize_for_tenant(
        self,
        tenant_id: UUID,
        dry_run:   bool = False,
    ) -> dict[UUID, MaterializeResult]:
        """Backfill: materialize obligations for every incident in the tenant."""
        with self._pg.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                        (str(tenant_id),))
        results: dict[UUID, MaterializeResult] = {}
        for incident_id in self._list_incidents(tenant_id):
            results[incident_id] = self.materialize_for_incident(
                incident_id, tenant_id, dry_run=dry_run)
        return results

    # ── Postgres reads ──────────────────────────────────────────────────────

    def _fetch_incident(self, incident_id: UUID, tenant_id: UUID) -> dict | None:
        with self._pg.cursor() as cur:
            cur.execute("""
                SELECT id, tenant_id, occurred_at, status
                FROM incidents
                WHERE id = %s AND tenant_id = %s AND is_active = TRUE
            """, (str(incident_id), str(tenant_id)))
            row = cur.fetchone()
            if not row:
                return None
            return {
                'id':          row[0],
                'tenant_id':   row[1],
                'occurred_at': row[2],
                'status':      row[3],
            }

    def _fetch_classifications(self, incident_id: UUID, tenant_id: UUID) -> list[dict]:
        with self._pg.cursor() as cur:
            cur.execute("""
                SELECT standard_id, dimension, value
                FROM incident_classifications
                WHERE incident_id = %s AND tenant_id = %s AND is_active = TRUE
            """, (str(incident_id), str(tenant_id)))
            return [
                {'standard_id': r[0], 'dimension': r[1], 'value': r[2]}
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

    # ── Neo4j resolution ────────────────────────────────────────────────────

    def _resolve_classification(self, cls: dict) -> list[dict]:
        """
        For one (standard_id, dimension, value) triple, return all obligations
        triggered by the bound Event(s). Edge-level `deadline` takes precedence
        over Event.legal_deadline.
        """
        with self._neo4j.session() as s:
            result = s.run("""
                MATCH (v:ClassificationValue {
                        standard_id: $std,
                        dimension:   $dim,
                        value:       $val
                      })
                      -[:MANIFESTS_AS]->(e:Event)
                      -[t:TRIGGERS_OBLIGATION]->(n:RequirementNode)
                RETURN
                    e.id                                AS event_id,
                    n.id                                AS control_ref,
                    n.standard_id                       AS req_standard_id,
                    coalesce(t.deadline, '')            AS edge_deadline,
                    coalesce(e.legal_deadline, '')      AS event_deadline,
                    t.rationale                         AS rationale
            """,
                std = cls['standard_id'],
                dim = cls['dimension'],
                val = cls['value'],
            )

            rows = []
            for r in result:
                edge_dl  = r['edge_deadline']  or None
                event_dl = r['event_deadline'] or None
                # Edge wins; fall back to event's legal_deadline only if the
                # edge itself is silent (the headline applies broadly).
                deadline = edge_dl or event_dl
                rows.append({
                    'event_id':        r['event_id'],
                    'control_ref':     r['control_ref'],
                    'req_standard_id': r['req_standard_id'],
                    'deadline':        deadline,
                    'rationale':       r['rationale'],
                })
            return rows

    # ── Postgres write ──────────────────────────────────────────────────────

    def _upsert_obligation(
        self,
        incident_id: UUID,
        tenant_id:   UUID,
        control_ref: str,
        standard_id: str,
        deadline:    str | None,
        deadline_at: datetime | None,
        rationale:   str | None,
    ) -> bool:
        """Insert one obligation. Returns True if inserted, False if it
        already existed (ON CONFLICT DO NOTHING)."""
        with self._pg.cursor() as cur:
            cur.execute("""
                INSERT INTO incident_obligations
                    (incident_id, tenant_id, control_ref, standard_id,
                     deadline, deadline_at, rationale, is_met)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
                ON CONFLICT (incident_id, control_ref, standard_id) DO NOTHING
                RETURNING control_ref
            """, (
                str(incident_id), str(tenant_id),
                control_ref, standard_id,
                deadline, deadline_at, rationale,
            ))
            return cur.fetchone() is not None


# =============================================================================
# CLI
# =============================================================================

def _connect_pg():
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    return psycopg2.connect(
        host     = os.getenv('POSTGRES_HOST', '127.0.0.1'),
        dbname   = os.getenv('POSTGRES_DB',   'arioncomply_compliance'),
        user     = os.getenv('POSTGRES_USER', 'arioncomply'),
        password = os.getenv('POSTGRES_PASSWORD', ''),
    )


def _connect_neo4j():
    from neo4j import GraphDatabase
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    return GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')),
    )


def _print_result(incident_id: UUID, r: MaterializeResult) -> None:
    print(f"\nIncident {incident_id}")
    print(f"  classifications seen:   {r.classifications_seen}")
    print(f"  events resolved:        {r.events_resolved}")
    print(f"  obligations inserted:   {r.obligations_inserted}")
    print(f"  obligations skipped:    {r.obligations_skipped} (already existed)")
    if r.unresolved_classifications:
        print(f"  ⚠ unresolved classifications "
              f"(no MANIFESTS_AS to any Event): {r.unresolved_classifications}")
    if r.errors:
        for e in r.errors:
            print(f"  ✗ {e}")


def _verify(pg_conn, tenant_id: UUID) -> None:
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    (str(tenant_id),))
        cur.execute("""
            SELECT
                i.external_ref,
                i.title,
                i.status,
                (SELECT count(*) FROM incident_classifications c
                  WHERE c.incident_id = i.id AND c.is_active)            AS classifications,
                (SELECT count(*) FROM incident_obligations o
                  WHERE o.incident_id = i.id)                            AS obligations,
                (SELECT count(*) FROM incident_obligations o
                  WHERE o.incident_id = i.id AND o.is_met)               AS met
            FROM incidents i
            WHERE i.tenant_id = %s AND i.is_active
            ORDER BY i.external_ref
        """, (str(tenant_id),))
        rows = cur.fetchall()
    print("\nTenant materialization status:")
    print(f"  {'ref':10s} {'title':28s} {'status':10s} {'class.':>6s} {'oblig.':>6s} {'met':>4s}")
    for r in rows:
        print(f"  {r[0]:10s} {(r[1] or '')[:28]:28s} {r[2]:10s} "
              f"{r[3]:>6d} {r[4]:>6d} {r[5]:>4d}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tenant',   required=True, help='tenant UUID')
    parser.add_argument('--incident', help='single incident UUID (default: all in tenant)')
    parser.add_argument('--dry-run',  action='store_true', help='preview without writing')
    parser.add_argument('--verify',   action='store_true',
                        help='print materialization status; no writes')
    args = parser.parse_args()

    pg     = _connect_pg()
    neo4j  = _connect_neo4j()
    tenant = UUID(args.tenant)

    try:
        if args.verify:
            _verify(pg, tenant)
            return

        m = IncidentMaterializer(pg, neo4j)
        if args.incident:
            r = m.materialize_for_incident(UUID(args.incident), tenant, dry_run=args.dry_run)
            _print_result(UUID(args.incident), r)
        else:
            results = m.materialize_for_tenant(tenant, dry_run=args.dry_run)
            for inc_id, r in results.items():
                _print_result(inc_id, r)
            print(f"\n{'─'*55}")
            agg = MaterializeResult(incident_id=tenant)
            for r in results.values():
                agg.merged_with(r)
            print(f"Total incidents: {len(results)}")
            print(f"Total classifications seen:   {agg.classifications_seen}")
            print(f"Total obligations inserted:   {agg.obligations_inserted}"
                  + (" (dry-run preview)" if args.dry_run else ""))
            print(f"Total obligations skipped:    {agg.obligations_skipped}")
            if agg.unresolved_classifications:
                print(f"Unresolved triples:           {set(agg.unresolved_classifications)}")
    finally:
        pg.close()
        neo4j.close()


if __name__ == "__main__":
    main()
