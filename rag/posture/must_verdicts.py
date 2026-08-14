"""
Canonical reader for `posture_must_verdicts` (per-MUST fulfillment SSoT).

Every consumer that needs per-MUST truth reads through this module — no
consumer runs its own SQL against posture_must_verdicts, and no consumer
runs the engine directly to compute per-MUST recognition (that's what the
SSoT is for).

Ship 58' (2026-08-10) established the writer + refresh cycle;
Ship 58'.s-u hardened the wiring; this module is the read-side canonical
API introduced to unify the ~9 consumer sites.

Scope selectors (combinable):
    must_ids       — specific list of MUST ids (template renderer path)
    control_ref +  — all MUSTs under one control (advisory / Dashboard /
    standard_id      SPA leaf-detail / chat markdown)
    (neither)      — all MUSTs for the tenant (journey wizard coverage)

Filters:
    only_satisfied — restrict to satisfied=TRUE rows

Return shape: `dict[must_id, MustVerdict]`. Missing rows (N/A-excluded
MUSTs, tenants not yet populated) simply don't appear in the dict.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class BridgeSource:
    """One row of posture_must_bridge_coverage — a direct-satisfied MUST
    in another framework contributing coverage to the current MUST via
    a curator-authored xfw bridge edge. Ship 59'.c (2026-08-11)."""
    source_must_id:     str
    source_control_ref: str
    source_standard_id: str
    source_role:        str    # 'PROGRAM' | 'EXTENSION' | 'OBLIGATION' | 'OTHER'
    edge_type:          str    # 'IMPLEMENTS' | 'SUPPORTS' | 'ENABLES' | 'GOVERNANCE'
    # Ship 69'.b — the ACTUAL target ref this edge points at in Neo4j.
    # May be a sub-clause narrower than the caller's control_ref
    # (e.g. Art.32.1.b when caller queried Art.32). Metadata lookups
    # (edge rationale / role in Neo4j) must use this narrower id.
    target_control_ref: str = ""


@dataclass(frozen=True)
class MustVerdict:
    """One row of posture_must_verdicts as a Python object."""
    must_id:        str
    control_ref:    str
    standard_id:    str
    framework_role: str    # Ship 59'.c — 'PROGRAM' | 'EXTENSION' | 'OBLIGATION' | 'OTHER'
    satisfied:      bool   # DIRECT satisfaction only (present + fresh cite)
    stale:          bool
    partial:        bool
    reason:         str
    # Ship 59'.c — attribution: MUSTs in other frameworks that
    # bridge-cover this MUST via curator-authored xfw edges.
    # Empty tuple when no bridge coverage exists.
    bridge_sources: tuple[BridgeSource, ...] = ()

    @property
    def covered(self) -> bool:
        """True if this MUST has ANY coverage — direct OR via bridges.

        Distinct from `.satisfied` (which stays strict direct-only for
        backward compat with engine semantics + existing consumers).
        Consumers that want the 'covered somehow' view opt into `.covered`
        explicitly; the default `.satisfied` check reflects engine truth.
        """
        return self.satisfied or bool(self.bridge_sources)

    @property
    def state(self) -> str:
        """Convenience one-word category (Ship 59'.c adds 'bridged'):
          'present' — direct-satisfied and fresh
          'stale'   — direct-satisfied but past freshness_days
          'partial' — partial-status finding, no present
          'bridged' — NOT directly satisfied, but has bridge coverage
                      (auditor attribution — signals "covered via other
                      framework's evidence, but no framework-native artefact")
          'missing' — no evidence of any kind
        """
        if self.satisfied:
            return "stale" if self.stale else "present"
        if self.partial:
            return "partial"
        if self.bridge_sources:
            return "bridged"
        return "missing"


def read_must_verdicts(
    pg_conn,
    tenant_id: str,
    *,
    must_ids:       Optional[Iterable[str]] = None,
    control_ref:    Optional[str] = None,
    standard_id:    Optional[str] = None,
    only_satisfied: bool = False,
) -> dict[str, MustVerdict]:
    """Read per-MUST verdicts from posture_must_verdicts.

    Scope selectors combine with AND. Passing no scope returns all rows
    for the tenant. RLS-scoped via `set_config('app.tenant_id', ...)` on
    the caller's connection — mandatory even though we also filter on
    tenant_id explicitly (arioncomply_app has no BYPASSRLS).

    Returns {must_id: MustVerdict}. Empty dict when scope has no matches
    or SSoT isn't populated yet (silent fallback — caller handles missing
    rows however it sees fit).
    """
    where_parts = ["tenant_id = %s::uuid"]
    params: list = [tenant_id]

    if must_ids is not None:
        ids_list = list(must_ids)
        if not ids_list:
            return {}
        where_parts.append("must_id = ANY(%s)")
        params.append(ids_list)
        # Ship 59'.e — same must_id can appear under multiple
        # control_refs (canonical owner + stub-context rollup rows).
        # When scoped by must_ids, consumers want the CANONICAL row
        # (one per must_id, tied to the MUST's owning control). Every
        # ChecklistItem id has shape `item:<control_ref>:<slot>`, so
        # split_part(must_id, ':', 2) yields the owner. This filter
        # drops stub_rollup rows so the {must_id: MustVerdict} return
        # shape stays 1:1 without ambiguity.
        where_parts.append("control_ref = split_part(must_id, ':', 2)")
    if control_ref is not None:
        where_parts.append("control_ref = %s")
        params.append(control_ref)
    if standard_id is not None:
        where_parts.append("standard_id = %s")
        params.append(standard_id)
    if only_satisfied:
        where_parts.append("satisfied = TRUE")

    q = f"""
        SELECT must_id, control_ref, standard_id,
               COALESCE(framework_role, 'OTHER'),
               satisfied, stale, partial, COALESCE(reason, '')
          FROM posture_must_verdicts
         WHERE {' AND '.join(where_parts)}
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(q, params)
            base_rows = cur.fetchall()

            # Ship 59'.c — fetch bridge sources for the same target MUST
            # ids in one query. Bridge rows joined into MustVerdict on
            # the Python side (dataclass tuples) rather than SQL JSON
            # aggregation — keeps the reader portable and predictable.
            #
            # Ship 59'.e — key bridges by (target_must_id, target_control_ref)
            # instead of just target_must_id. The same MUST can appear
            # in bridge_coverage under multiple target_control_refs
            # (canonical + stub attributions). Matching each row's
            # (must_id, control_ref) preserves self-contained attribution:
            # a query for Art.32.1.b returns only bridges targeting
            # Art.32.1.b, not bridges targeting the parent Art.32.
            pairs = [(r[0], r[1]) for r in base_rows]
            bridges_by_pair: dict[tuple[str, str], list[BridgeSource]] = {}
            if pairs:
                target_ids  = [p[0] for p in pairs]
                target_crfs = list({p[1] for p in pairs})
                # Ship 69'.b — union descendant sub-clause bridges into the
                # parent control's must_verdicts. Ship 69'.b retargets edges
                # like A.5.18 -[IMPLEMENTS]-> Art.32 to Art.32.1.b (narrower
                # attribution). Under Ship 59'.e stub roll-down, the same
                # target_must_id lives under both Art.32 and Art.32.1.b in
                # bridge_coverage. The Art.32 EP caller passes control_ref
                # ='Art.32' and expects the sub-clause attributions to
                # appear. Match either exact ref OR any descendant
                # `{ref}.%`. Sub-clause callers still match themselves
                # exactly (their `{ref}.%` matches deeper leaves that
                # don't yet exist — harmless).
                like_patterns = [f"{r}.%" for r in target_crfs]
                cur.execute("""
                    SELECT target_must_id, target_control_ref,
                           source_must_id, source_control_ref,
                           source_standard_id, source_role, edge_type
                      FROM posture_must_bridge_coverage
                     WHERE tenant_id = %s::uuid
                       AND target_must_id = ANY(%s)
                       AND (target_control_ref = ANY(%s)
                            OR target_control_ref LIKE ANY(%s))
                """, (tenant_id, target_ids, target_crfs, like_patterns))
                # Ship 69'.b — key bridges by target_must_id ONLY. The
                # sub-clause target_control_ref is preserved on each
                # BridgeSource attribution row (edge_type / rationale) but
                # verdict lookup uses must_id alone so parent + descendant
                # bridges roll up into the parent MUST's verdict.
                for row in cur.fetchall():
                    # Use caller's control_ref (from base_rows) as the
                    # verdict key; sub-clause target_control_ref carried
                    # only on the BridgeSource row.
                    caller_crf = None
                    for pid, pcrf in pairs:
                        if pid == row[0]:
                            caller_crf = pcrf
                            break
                    bridges_by_pair.setdefault(
                        (row[0], caller_crf or row[1]), []
                    ).append(BridgeSource(
                        source_must_id     = row[2],
                        source_control_ref = row[3],
                        source_standard_id = row[4],
                        source_role        = row[5],
                        edge_type          = row[6],
                        target_control_ref = row[1],
                    ))

            return {
                r[0]: MustVerdict(
                    must_id        = r[0],
                    control_ref    = r[1],
                    standard_id    = r[2],
                    framework_role = r[3],
                    satisfied      = r[4],
                    stale          = r[5],
                    partial        = r[6],
                    reason         = r[7],
                    bridge_sources = tuple(bridges_by_pair.get((r[0], r[1]), [])),
                )
                for r in base_rows
            }
    except Exception:
        # Silent fallback — schema not applied, or transient issue.
        # Consumers treat empty dict as "no signal", which is safe.
        return {}


def read_satisfied_must_ids(pg_conn, tenant_id: str) -> set[str]:
    """Convenience: set of must_ids satisfied for this tenant.

    Fast-path for membership checks (journey wizard coverage progress,
    chat footer template-suggestion logic). Uses only_satisfied=TRUE
    filter so the query stays cheap on tenants with mostly-unmet posture.
    """
    verdicts = read_must_verdicts(pg_conn, tenant_id, only_satisfied=True)
    return set(verdicts.keys())


def read_must_verdicts_by_control(
    pg_conn,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
) -> dict[str, MustVerdict]:
    """Convenience wrapper — all MUSTs under one control."""
    return read_must_verdicts(
        pg_conn, tenant_id,
        control_ref=control_ref, standard_id=standard_id,
    )


def read_bridge_contributions(
    pg_conn,
    tenant_id: str,
    *,
    source_must_id:     Optional[str] = None,
    source_control_ref: Optional[str] = None,
    source_standard_id: Optional[str] = None,
) -> list[tuple[str, str, str, str, str, str]]:
    """Reverse-direction query: what does this MUST/control contribute to?

    Ship 59'.c — for auditor UIs that show *"my ISO A.5.15:rbac evidence
    contributes to GDPR Art.32.1.b (IMPLEMENTS), Art.5.1.f (IMPLEMENTS)"*.
    Consumers pass either a specific source_must_id or a source_control_ref
    (+ standard_id) to get all its outbound bridge contributions.

    Returns list of tuples:
      (target_must_id, target_control_ref, target_standard_id,
       target_role, edge_type, source_must_id)
    """
    where_parts = ["tenant_id = %s::uuid"]
    params: list = [tenant_id]
    if source_must_id is not None:
        where_parts.append("source_must_id = %s")
        params.append(source_must_id)
    if source_control_ref is not None:
        where_parts.append("source_control_ref = %s")
        params.append(source_control_ref)
    if source_standard_id is not None:
        where_parts.append("source_standard_id = %s")
        params.append(source_standard_id)

    q = f"""
        SELECT target_must_id, target_control_ref, target_standard_id,
               target_role, edge_type, source_must_id
          FROM posture_must_bridge_coverage
         WHERE {' AND '.join(where_parts)}
         ORDER BY target_standard_id, target_control_ref, target_must_id
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(q, params)
            return cur.fetchall()
    except Exception:
        return []
