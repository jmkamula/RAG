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

    # ── Node accessors — Layer 1 / Layer 2 ───────────────────────────

    def primary_nodes(self) -> list:
        """Layer 1 nodes from the resolved graph. Filters out
        informational-only rows (obligation nodes without content)."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "primary_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    def secondary_nodes(self) -> list:
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "secondary_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    def xfw_nodes(self) -> list:
        """Layer 2 (cross-framework) nodes. Filters out informational
        rows. Does NOT filter unlinked xfw — that's rank_and_answer's
        anti-hallucination guard, applied when rendering."""
        gn = getattr(self.resolved, "graph_nodes", None)
        if gn is None:
            return []
        return [n for n in getattr(gn, "xfw_nodes", []) or []
                if not getattr(n, "is_informational", False)]

    def all_nodes(self) -> list:
        """Every non-informational node — Layer 1 + secondary + Layer 2."""
        return self.primary_nodes() + self.secondary_nodes() + self.xfw_nodes()

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
        out: dict[str, dict] = {}
        for nid, rec in self.posture_nodes.items():
            ref = rec.get("control_ref") or nid.split(":")[-1]
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
        """Return {xfw_ref: [primary_ref, ...], ...} — for each Layer 2
        node, the primary refs it bridges to via IMPLEMENTS/SUPPORTS
        edges.

        This is the single most-compressible signal in the current
        prompt. Instead of the LLM re-deriving from per-node blocks,
        we hand it a one-line mapping.
        """
        out: dict[str, list[str]] = {}
        for n in self.xfw_nodes():
            linked: set[str] = set()
            for edge in getattr(n, "xfw_edges", []) or []:
                # Edge points one way; extract the *other* end's ref.
                nid = n.node_id
                if nid == getattr(edge, "target_id", None):
                    other = getattr(edge, "source_id", "")
                else:
                    other = getattr(edge, "target_id", "")
                if other:
                    linked.add(other.split(":")[-1])
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
