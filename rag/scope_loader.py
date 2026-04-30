"""
ArionComply — Scope Loader

Derives a tenant's evaluation scope automatically from:
  1. Standards they have enrolled in (tenant_standards table)
  2. Standard relationships (standard_relationships table)
  3. Which standards are loaded in the graph (standards.loaded_in_graph)

This replaces the hardcoded applicable_standards list in chat.py.

Key concept:
  direct_standards    — standards the tenant directly implements
                        (ISO27001:2022, ISO27701:2019)
  inferred_standards  — standards reachable via maps_to/satisfies
                        (GDPR:2016/679 via ISO27701 Annex D)
  queryable_standards — direct + inferred, filtered to what's in the graph
  evaluation_scope    — what can be used for posture/compliance questions

Usage:
  from rag.scope_loader import load_tenant_scope

  scope = load_tenant_scope(pg_conn, tenant_id)
  print(scope.queryable_standards)    # ["ISO27001:2022"]
  print(scope.inferred_standards)     # ["GDPR:2016/679"]
  print(scope.can_evaluate_gdpr)      # True (via ISO 27701 → GDPR)
  print(scope.gdpr_bridge)            # "ISO27701:2019 Annex D"
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StandardInfo:
    id:             str
    short_name:     str
    standard_type:  str       # management_system | regulation | framework
    certifiable:    bool
    loaded_in_graph: bool
    status:         str       # tenant enrollment status
    scope_source:   str       # direct | inferred
    via_standard:   str       # which standard provides inference
    relationship:   str | None
    cert_body:      str | None = None
    cert_date:      str | None = None


@dataclass
class TenantScope:
    tenant_id:              str
    direct_standards:       list[StandardInfo]   # directly enrolled
    inferred_standards:     list[StandardInfo]   # reachable via relationships
    queryable_standards:    list[str]            # standard IDs in graph → use for search
    all_standard_ids:       list[str]            # direct + inferred IDs

    # Convenience flags
    @property
    def has_iso27001(self) -> bool:
        return any("27001" in s.id for s in self.direct_standards)

    @property
    def has_iso27701(self) -> bool:
        return any("27701" in s.id for s in self.direct_standards)

    @property
    def can_evaluate_gdpr(self) -> bool:
        """True if GDPR evaluation is possible via an implemented standard."""
        return any(
            s.id == "GDPR:2016/679"
            for s in self.inferred_standards
        )

    @property
    def gdpr_bridge(self) -> str | None:
        """Which standard provides the GDPR mapping, and via what."""
        for s in self.inferred_standards:
            if s.id == "GDPR:2016/679":
                std = s.via_standard
                src = s.relationship
                return f"{std} ({src})"
        return None

    @property
    def certified_standards(self) -> list[StandardInfo]:
        return [s for s in self.direct_standards if s.status == "certified"]

    def can_answer_standard(self, standard_id: str) -> tuple[bool, str]:
        """
        Returns (can_answer, explanation).
        Used by classifier to decide if a query is in scope.
        """
        # Direct implementation
        for s in self.direct_standards:
            if s.id == standard_id:
                return True, f"direct ({s.status})"

        # Inferred via relationship
        for s in self.inferred_standards:
            if s.id == standard_id:
                return True, f"via {s.via_standard} {s.relationship}"

        return False, "not in scope"

    def describe(self) -> str:
        """Human-readable scope description for system prompt injection."""
        lines = []
        for s in self.direct_standards:
            cert = f" — {s.cert_body}" if s.cert_body else ""
            lines.append(f"  {s.short_name} ({s.status}{cert})")

        if self.inferred_standards:
            lines.append("Evaluable via mapping:")
            for s in self.inferred_standards:
                lines.append(f"  {s.short_name} — via {s.via_standard} "
                            f"[{s.relationship}]")
        return "\n".join(lines)


def load_tenant_scope(pg_conn, tenant_id: str) -> TenantScope:
    """
    Load and derive the full evaluation scope for a tenant.
    Uses tenant_evaluation_scope view for automatic inference.
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("""
                SELECT
                    tes.standard_id,
                    s.short_name,
                    s.standard_type,
                    s.certifiable,
                    s.loaded_in_graph,
                    tes.status,
                    tes.scope_source,
                    tes.via_standard,
                    tes.relationship,
                    ts.cert_body,
                    ts.cert_date::text
                FROM tenant_evaluation_scope tes
                JOIN standards s ON s.id = tes.standard_id
                LEFT JOIN tenant_standards ts
                    ON ts.tenant_id = tes.tenant_id
                    AND ts.standard_id = tes.standard_id
                WHERE tes.tenant_id = %s
                ORDER BY
                    tes.scope_source,      -- direct first
                    s.standard_type,       -- management_system before regulation
                    tes.standard_id
            """, (tenant_id,))

            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

    except Exception as e:
        logger.error(f"load_tenant_scope failed for {tenant_id}: {e}")
        # Fall back to ISO 27001 only
        return TenantScope(
            tenant_id            = tenant_id,
            direct_standards     = [],
            inferred_standards   = [],
            queryable_standards  = ["ISO27001:2022"],
            all_standard_ids     = ["ISO27001:2022"],
        )

    direct   = []
    inferred = []

    for row in rows:
        rec = dict(zip(cols, row))
        info = StandardInfo(
            id              = rec["standard_id"],
            short_name      = rec["short_name"],
            standard_type   = rec["standard_type"],
            certifiable     = rec["certifiable"],
            loaded_in_graph = rec["loaded_in_graph"],
            status          = rec["status"] or "implementing",
            scope_source    = rec["scope_source"],
            via_standard    = rec["via_standard"],
            relationship    = rec["relationship"],
            cert_body       = rec["cert_body"],
            cert_date       = rec["cert_date"],
        )
        if rec["scope_source"] == "direct":
            direct.append(info)
        else:
            inferred.append(info)

    # Queryable = standards that have nodes in the graph
    # For direct standards: use if loaded_in_graph = True
    # For inferred (e.g. GDPR): use if loaded_in_graph = True
    # This automatically expands as standards are loaded
    queryable = [
        s.id for s in (direct + inferred)
        if s.loaded_in_graph
    ]

    # Deduplicate while preserving order
    seen = set()
    queryable = [x for x in queryable if not (x in seen or seen.add(x))]

    all_ids = [s.id for s in direct] + [s.id for s in inferred]
    all_ids = list(dict.fromkeys(all_ids))

    scope = TenantScope(
        tenant_id           = tenant_id,
        direct_standards    = direct,
        inferred_standards  = inferred,
        queryable_standards = queryable,
        all_standard_ids    = all_ids,
    )

    logger.info(
        f"load_tenant_scope: tenant={tenant_id} "
        f"direct={[s.id for s in direct]} "
        f"inferred={[s.id for s in inferred]} "
        f"queryable={queryable}"
    )
    return scope
