"""
CaseFile dataclass — the ground-truth record for one chat turn.

Holds ResolvedContext + SessionContext + intent as-is. Provides
convenience views over that data (posture_by_ref, xfw_bridges, etc.)
so downstream digest / preservation code doesn't reimplement the
same joins.

Nothing in this module renders text for the LLM — see `digest.py`.
Nothing here extracts a preservation spec — see `preservation.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any


# Findings that indicate a substantive verdict — used by helpers
# below when computing "assessed" postures. N/A + None + '' all
# mean unassessed for the case-file's purposes.
_ASSESSED_FINDINGS = {"NC", "OFI", "Comply"}

# Confirmation states that DO NOT need a [DRAFT] tag on presentation.
# See rank_and_answer for the canonical set — kept in sync manually,
# as changes here affect preservation.
_CONFIRMED_STATES = {
    "confirmed", "overridden", "document_confirmed", "engine_confirmed",
}

# Process-cached fallback for {standard_id: role} lookups when the
# tenant scope doesn't carry role-grouped accessors. Populated on
# first CaseFile.role_of() call. Standards.role is globally stable
# (not tenant-specific), so a single cache serves every tenant.
_STANDARDS_ROLE_CACHE: dict[str, str] | None = None


def _load_standards_role_map() -> dict[str, str]:
    """Read {standard_id: role} from Postgres `standards.role` once
    per process. Empty on failure — falls back gracefully."""
    global _STANDARDS_ROLE_CACHE
    if _STANDARDS_ROLE_CACHE is not None:
        return _STANDARDS_ROLE_CACHE
    try:
        import os
        import psycopg2
        conn = psycopg2.connect(
            host     = os.getenv("PGHOST",     "127.0.0.1"),
            dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
            user     = os.getenv("PGUSER",     "arioncomply_app"),
            password = os.getenv("PGPASSWORD", ""),
        )
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, role FROM standards WHERE role IS NOT NULL")
                _STANDARDS_ROLE_CACHE = {sid: role for sid, role in cur.fetchall()}
        finally:
            conn.close()
    except Exception:
        _STANDARDS_ROLE_CACHE = {}
    return _STANDARDS_ROLE_CACHE


@dataclass
class CaseFile:
    """The full ground-truth for one chat turn.

    Attributes:
        query:        Raw user query for this turn.
        intent:       QueryIntent (or intent-dict from consensus) —
                       carries question_type, cited_refs, standards_scope.
        resolved:     ResolvedContext from the resolver — has
                       posture_nodes + graph_nodes + doc_contexts.
        session:      SessionContext for the conversation, or None on
                       first turn / non-conversational callers.
        tenant:       TenantContext (or duck-typed with .tenant_id +
                       .scope). Used for tenant_name + queryable_standards.
        last_entity:  Optional prior-turn entity dict for deictic
                       follow-ups. See rank_and_answer's use.
        incidents:    Optional list of IncidentObligationContext for
                       incident-open queries.

    All attributes are references to existing objects — the CaseFile
    does not copy or reshape data. Mutation of the underlying objects
    IS visible through the CaseFile (matches ResolvedContext's own
    read-only contract downstream).
    """
    query:        str
    intent:       Any                          # QueryIntent | dict
    resolved:     Any                          # ResolvedContext
    session:      Optional[Any] = None         # SessionContext | None
    tenant:       Optional[Any] = None         # TenantContext-like | None
    last_entity:  Optional[dict] = None
    incidents:    list = field(default_factory=list)
    # Ship 14'.e — risk-register data for posture_risk question_type.
    # Optional: only populated when the classifier routes a risk
    # query. Digest renders a fixed-slot RISKS section from this
    # field (≤300-token budget); preservation-check extracts the
    # top-N external_refs as required_risk_refs for the repair pass.
    # Framework role model discipline: RiskSummary entries carry
    # linked controls with role + subject metadata pre-attached, so
    # digest can render program/extension/obligation refs
    # side-by-side without a second lookup.
    risks:        list = field(default_factory=list)  # list[dict] — compact RiskSummary view
    # Ship 60'.j — bridge-coverage counts per obligation ref, precomputed
    # in llm_answer.py before build_structured_prompt_pair. Consumed by
    # digest's XFW BRIDGES section to append "(N/M MUSTs bridge-covered)"
    # on each line. Empty dict = no coverage data; digest omits the
    # suffix (backward-compat with any test path that doesn't populate).
    # Shape: {control_ref: (n_bridge_covered, n_total_musts)}. Only refs
    # that are xfw targets get populated; keeps compute + digest cost
    # bounded to the section already rendered.
    bridge_counts: dict = field(default_factory=dict)

    # ── Basic identity + scope ────────────────────────────────────────

    @property
    def tenant_name(self) -> str:
        if self.tenant is None:
            return ""
        return getattr(self.tenant, "tenant_name", "") or ""

    @property
    def tenant_id(self) -> str:
        if self.tenant is None:
            return ""
        return getattr(self.tenant, "tenant_id", "") or ""

    @property
    def scope_standards(self) -> list[str]:
        """Tenant's enrolled/queryable standards. Empty when unknown —
        callers must handle that (widening rather than assuming ISO)."""
        if self.tenant is None:
            return []
        scope = getattr(self.tenant, "scope", None)
        if scope is None:
            return []
        std = getattr(scope, "queryable_standards", None)
        return list(std) if std else []

    # ── Intent shortcuts ─────────────────────────────────────────────

    @property
    def question_type(self) -> str:
        """Question type as a plain string — accepts both QueryIntent
        (which has .question_type as an enum) and intent-dict (which
        stores it as .intent_type / .question_type)."""
        it = self.intent
        if it is None:
            return "unknown"
        qt = getattr(it, "question_type", None)
        if qt is None and isinstance(it, dict):
            qt = it.get("intent_type") or it.get("question_type")
        if qt is None:
            return "unknown"
        # QuestionType enum → its .value
        return getattr(qt, "value", None) or str(qt)

    @property
    def cited_refs(self) -> list[str]:
        it = self.intent
        if it is None:
            return []
        v = getattr(it, "cited_refs", None)
        if v is None and isinstance(it, dict):
            v = it.get("cited_refs") or it.get("focus_refs")
        return [r for r in (v or []) if r]

    # ── Session shortcuts ────────────────────────────────────────────

    @property
    def active_session_refs(self) -> list[str]:
        if self.session is None:
            return []
        return list(getattr(self.session, "active_refs", []) or [])

    @property
    def active_cluster(self) -> Optional[str]:
        if self.session is None:
            return None
        return getattr(self.session, "active_cluster", None)

    # ── Node accessors ────────────────────────────────────────────────
    #
    # Ship 2'.i (2026-07-16): the primary_nodes/xfw_nodes split is a
    # legacy artifact from before the role model (framework_role_model_arc,
    # 2026-07-05). All obligations from all enrolled programs / extensions
    # / obligations-role standards are first-class citizens. Bridges are
    # relationships between obligations, not a classification of them.
    #
    # The three role-based accessors below (obligations_of_program,
    # obligations_of_extension, obligations_of_obligation) let downstream
    # code structure the digest by role instead of by "layer".
    #
    # primary_nodes() / secondary_nodes() / xfw_nodes() are kept for
    # backward compat with pre-Ship-2'.i callers (legacy rank_and_answer
    # path); new code should use all_nodes() + role_of() instead.

    def _all_graph_nodes(self) -> list:
        """Internal: every non-informational node the resolver surfaced,
        pooled across primary/secondary/xfw. Ship 2'.i replaces layer-
        based split with this single pool."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        pooled = (
            list(getattr(gn, "primary_nodes",   []) or [])
            + list(getattr(gn, "secondary_nodes", []) or [])
            + list(getattr(gn, "xfw_nodes",     []) or [])
        )
        # De-duplicate on node_id — the same node can land in multiple
        # buckets when the resolver's expansion overlaps.
        seen: set[str] = set()
        out: list = []
        for n in pooled:
            nid = getattr(n, "node_id", None)
            if nid in seen or getattr(n, "is_informational", False):
                continue
            if nid:
                seen.add(nid)
            out.append(n)
        return out

    def all_nodes(self) -> list:
        """Every non-informational obligation across all enrolled
        programs / extensions / obligations. Deduplicated."""
        return self._all_graph_nodes()

    # ── Legacy accessors — do not extend (see framework-role-model-arc) ──

    def primary_nodes(self) -> list:
        """LEGACY (do not use in new code): the resolver's primary_nodes
        list. Ship 2'.i deprecates this in favour of all_nodes() +
        role_of(). Retire-by: after legacy rank_and_answer path is
        removed (retire-by 2026-08-15)."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "primary_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    def secondary_nodes(self) -> list:
        """LEGACY (do not use in new code): see primary_nodes."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "secondary_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    def xfw_nodes(self) -> list:
        """LEGACY (do not use in new code): the resolver's xfw_nodes
        list. Ship 2'.i deprecates this — bridges are edges, not a
        node identity. See framework-role-model-arc."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "xfw_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    # ── Role model accessors (framework-role-model-arc, 2026-07-05) ─────
    #
    # Every enrolled standard has a role: program / extension /
    # obligation / guidance. Nodes inherit their standard's role. The
    # digest structures its layout by role — no more primary/xfw split.

    def _role_map(self) -> dict[str, str]:
        """Return {standard_id: role} for every enrolled standard.

        Preferred source: `tenant.scope` (TenantScope). When the scope
        has role-grouped accessors (`.programs / .extensions /
        .obligations` — Phase 1 of framework-role-model-arc), use them.

        Fallback: read `standards.role` from Postgres. Cached per-
        process since standards.role is globally stable (not tenant-
        specific).
        """
        scope = getattr(self.tenant, "scope", None) if self.tenant else None
        if scope is not None:
            out: dict[str, str] = {}
            for group_name in ("programs", "extensions", "obligations"):
                role = group_name.rstrip("s")  # "programs" → "program"
                group = getattr(scope, group_name, None) or []
                for s in group:
                    sid = getattr(s, "id", None)
                    if sid:
                        out[sid] = role
            if out:
                return out
        # Fallback: process-cached Postgres lookup.
        return _load_standards_role_map()

    def role_of(self, ref: str) -> Optional[str]:
        """Return the role of the standard that owns this ref, or None
        if the ref isn't in any enrolled standard.

        Roles: "program" | "extension" | "obligation".

        Look-up path: find the ref among all_nodes(), read its
        standard_id, check the tenant's role map. Falls back to None
        when the ref is off-scope.
        """
        for n in self.all_nodes():
            if n.ref == ref:
                sid = getattr(n, "standard_id", None)
                if sid:
                    return self._role_map().get(sid)
                break
        # Not on any node — try posture record
        posture = self.posture_by_ref()
        rec = posture.get(ref)
        if rec:
            sid = rec.get("standard_id")
            if sid:
                return self._role_map().get(sid)
        return None

    def obligations_of_role(self, role: str) -> list:
        """All non-informational nodes whose owning standard has this
        role. role ∈ {"program", "extension", "obligation"}."""
        rmap = self._role_map()
        return [
            n for n in self.all_nodes()
            if rmap.get(getattr(n, "standard_id", "")) == role
        ]

    def demonstrated_by(self, ref: str) -> list[dict]:
        """Return the demonstrated_by list for an OBLIGATION ref, or []
        if the ref isn't an obligation OR has no demonstrators. Each
        entry: {src_id, src_std, via_edge, finding, strength}.

        Populated by posture_loader._apply_demonstrates_overlay (Phase 2b,
        2026-07-05). See framework-role-model-arc.
        """
        rec = self.posture_by_ref().get(ref)
        if not rec:
            return []
        return list(rec.get("demonstrated_by") or [])

    # ── Posture accessors ────────────────────────────────────────────

    @property
    def posture_nodes(self) -> dict:
        """Raw posture dict from resolver — {node_id: {finding, gap,
        control_ref, confirmation_status, evidence_text, ...}}."""
        return getattr(self.resolved, "posture_nodes", {}) or {}

    def posture_by_ref(self) -> dict[str, dict]:
        """Reindex posture_nodes by control_ref (e.g. "A.5.18", "Art.32")
        so downstream code can look up findings without knowing node_id.

        When multiple node_ids map to the same ref (rare — mostly cross-
        standard collisions), the last one wins. That matches the
        posture_by_ref build in rank_and_answer today.
        """
        from rag.id_types import ref_of
        out: dict[str, dict] = {}
        for nid, rec in self.posture_nodes.items():
            ref = rec.get("control_ref") or ref_of(nid)
            if ref:
                out[ref] = rec
        return out

    def posture_for(self, ref: str) -> Optional[dict]:
        """Return the posture record for a control ref, or None."""
        return self.posture_by_ref().get(ref)

    def is_assessed(self, ref: str) -> bool:
        """True if the ref has a substantive finding (NC/OFI/Comply)."""
        rec = self.posture_for(ref)
        if not rec:
            return False
        return rec.get("finding") in _ASSESSED_FINDINGS

    def needs_draft_tag(self, ref: str) -> bool:
        """True if the ref's posture is assessed but NOT confirmed —
        the [DRAFT] tag on output is required in this case (see
        rank_and_answer's confirm_label logic)."""
        rec = self.posture_for(ref)
        if not rec:
            return False
        if rec.get("finding") not in _ASSESSED_FINDINGS:
            return False
        return rec.get("confirmation_status") not in _CONFIRMED_STATES

    # ── Cross-framework bridges ──────────────────────────────────────

    def xfw_bridges(self) -> dict[str, list[str]]:
        """Return {ref: [linked_ref, ...], ...} — for every node with
        cross-framework edges, list the refs it links to via
        IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE.

        Ship 2'.i: iterates all_nodes() instead of xfw_nodes(). Bridges
        are relationships between obligations, not a classification of
        the node itself. See framework-role-model-arc.
        """
        out: dict[str, list[str]] = {}
        for n in self.all_nodes():
            edges = getattr(n, "xfw_edges", None)
            if not edges:
                continue
            linked: set[str] = set()
            for edge in edges:
                nid = n.node_id
                if nid == getattr(edge, "target_id", None):
                    other = getattr(edge, "source_id", "")
                else:
                    other = getattr(edge, "target_id", "")
                if other:
                    from rag.id_types import ref_of
                    linked.add(ref_of(other))
            if linked:
                out[n.ref] = sorted(linked)
        return out

    # ── Document contexts ────────────────────────────────────────────

    @property
    def doc_contexts(self) -> dict:
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return {}
        return getattr(gn, "doc_contexts", {}) or {}

    def doc_refs(self) -> list[str]:
        """Control refs that have a DocumentContext attached."""
        return [ctx.control_ref for ctx in self.doc_contexts.values()
                if getattr(ctx, "control_ref", None)]

    # ── Diagnostics (for logging / debugging) ────────────────────────

    def summary(self) -> dict:
        """Compact self-description — useful for logs + tests."""
        posture_counts = {"NC": 0, "OFI": 0, "Comply": 0, "N/A": 0, "unassessed": 0}
        for rec in self.posture_nodes.values():
            f = rec.get("finding")
            if f in posture_counts:
                posture_counts[f] += 1
            else:
                posture_counts["unassessed"] += 1
        return {
            "query_len":         len(self.query or ""),
            "question_type":     self.question_type,
            "cited_refs":        list(self.cited_refs),
            "tenant":            self.tenant_name,
            "scope_standards":   self.scope_standards,
            "primary_nodes":     len(self.primary_nodes()),
            "secondary_nodes":   len(self.secondary_nodes()),
            "xfw_nodes":         len(self.xfw_nodes()),
            "xfw_bridges":       len(self.xfw_bridges()),
            "doc_contexts":      len(self.doc_contexts),
            "posture_counts":    posture_counts,
            "active_session_refs": self.active_session_refs,
            "incidents":         len(self.incidents),
        }
