"""
ArionComply — Query Taxonomy Registry

The taxonomy is DATA, not code. Adding a new query type means adding one entry
to QUERY_TAXONOMY. The pipeline reads this registry — no if/elif chains to maintain.

Design principles:
  - Open/closed: open for extension, closed for modification
  - Each entry is self-contained: sources, answer shape, JFYI rules
  - Tier 1 (DB-first) types short-circuit the LLM where possible
  - Tier 4 (event-triggered) are not classifier-routed — they're detected separately

Adding a new type:
  1. Add a TaxonomyEntry to QUERY_TAXONOMY
  2. Add example phrases to CLASSIFIER_PHRASES[new_type]
  3. Add a handler to Resolver (resolver.py)
  4. Add JFYI rules to JFYIEngine (jfyi.py) if needed
  No other files need changing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TaxonomyEntry:
    """
    Complete specification for one query taxonomy type.
    Immutable — the registry is read-only at runtime.
    """

    # ── Identity ──────────────────────────────────────────────────────────
    type_id:       str        # unique identifier, e.g. "POSTURE_STATUS"
    display_name:  str        # human-readable, e.g. "Compliance Status"
    description:   str        # one-sentence description for documentation

    # ── Examples (used by classifier and documentation) ───────────────────
    examples:      tuple[str, ...]  # representative user queries

    # ── Answer shape ──────────────────────────────────────────────────────
    answer_shape:  str        # describes the expected output structure
    tier:          int        # 1=DB-first, 2=LLM-synthesis, 3=cross-cutting, 4=event

    # ── Data sources (legacy — used by _expand() QueryIntent) ───────────
    primary_source:   str     # "postgres" | "graph" | "postgres+graph"
    needs_posture:    bool    # requires posture_controls data
    needs_graph:      bool    # requires Neo4j graph traversal
    needs_chroma:     bool    # requires ChromaDB vector retrieval
    can_short_circuit:bool    # True = answer directly from DB without LLM

    # ── Retrieval Policy (Phase 2a) ───────────────────────────────────────
    # These fields are ENFORCED by the resolver dispatcher.
    # Each handler only calls the sources declared here.
    # Adding a new taxonomy type = set these fields + write one handler.
    use_posture:         bool = True   # query posture_controls (Postgres)
    use_vector:          bool = True   # query ChromaDB for semantic context
    use_graph:           bool = True   # query Neo4j for structured graph data
    use_doc_inventory:   bool = False  # call get_document_inventory (Neo4j)
    allow_short_circuit: bool = False  # return direct DB answer without LLM
    # vector_n:  how many vector results to fetch (default varies by handler)
    # expand_n:  how many nodes to pass to _expand() (default varies by handler)
    vector_n:            int  = 10
    expand_n:            int  = 8

    # ── JFYI rules (evaluated after primary answer) ───────────────────────
    jfyi_rules:    tuple[str, ...] = field(default_factory=tuple)

    # ── Clarification behaviour ───────────────────────────────────────────
    # When clarification is needed for this type, which facts to surface
    clarify_with:  tuple[str, ...] = field(default_factory=tuple)
    # "document_alerts" | "posture_findings" | "cert_status"


# =============================================================================
# THE TAXONOMY REGISTRY
# =============================================================================

QUERY_TAXONOMY: dict[str, TaxonomyEntry] = {

    # ── TIER 1: DB-first (deterministic, no LLM required) ────────────────
    # These types have definitive answers in Postgres.
    # The resolver short-circuits to DB and formats the result directly.

    "POSTURE_STATUS": TaxonomyEntry(
        type_id        = "POSTURE_STATUS",
        display_name   = "Compliance Status",
        description    = "Current compliance posture on a specific control or overall",
        tier           = 1,
        examples       = (
            "what is our A.5.18 status?",
            "what are our NC findings?",
            "what are our main compliance gaps?",
            "show me our OFI findings",
            "what is our ISO 27001 posture?",
            "are we certified?",
        ),
        answer_shape   = (
            "finding(NC|OFI|Comply|N/A) + gap_description + source + "
            "brief action_required from posture data"
        ),
        primary_source    = "postgres",
        needs_posture     = True,
        needs_graph       = False,
        needs_chroma      = False,
        can_short_circuit = False,   # needs LLM to synthesise multiple findings
        # ── Retrieval policy ──
        use_posture        = True,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = False,
        allow_short_circuit= False,
        vector_n           = 10,
        expand_n           = 5,
        jfyi_rules        = (
            "related_controls",
            "audit_timeline",
            "missing_evidence_docs",
        ),
        clarify_with = ("posture_findings",),
    ),

    "DOCUMENT_STATUS": TaxonomyEntry(
        type_id        = "DOCUMENT_STATUS",
        display_name   = "Document Upload Status",
        description    = "Whether a specific document has been uploaded to the platform",
        tier           = 1,
        examples       = (
            "have we uploaded our access control policy?",
            "is our IR playbook in the system?",
            "which documents have not been uploaded?",
            "show me missing documents",
            "what documents are registered but not uploaded?",
        ),
        answer_shape   = (
            "registered(yes|no) + uploaded(yes|no) + "
            "alert_type(CRITICAL|WARNING|INFO) + linked_controls"
        ),
        primary_source    = "postgres",
        needs_posture     = False,
        needs_graph       = False,
        needs_chroma      = False,
        can_short_circuit = True,    # pure DB lookup, no LLM needed
        # ── Retrieval policy ──
        use_posture        = False,
        use_vector         = False,
        use_graph          = False,
        use_doc_inventory  = False,
        allow_short_circuit= True,
        vector_n           = 0,
        expand_n           = 0,
        jfyi_rules        = (
            "linked_findings",
            "upload_instructions",
        ),
        clarify_with = ("document_alerts",),
    ),

    # ── TIER 2: LLM synthesis required ───────────────────────────────────
    # These types need the LLM to synthesise, explain, or guide.

    "REMEDIATION_GUIDE": TaxonomyEntry(
        type_id        = "REMEDIATION_GUIDE",
        display_name   = "Remediation Guide",
        description    = (
            "What to do to address a finding: policy pointer + "
            "step-by-step actions + required documents + timeline"
        ),
        tier           = 2,
        examples       = (
            "what should we do about A.5.18?",
            "how do we close the access rights NC?",
            "what steps are needed to address F001?",
            "how do we fix our incident response gap?",
            "what do we need to do to pass the next audit?",
            "how should we prepare for our next surveillance audit?",
        ),
        answer_shape   = (
            "gap_summary + policy_pointer + "
            "numbered_steps + documents_needed(existing+missing) + "
            "timeline + owner_suggestion"
        ),
        primary_source    = "postgres+graph",
        needs_posture     = True,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = True,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = True,   # fetches checklist for topic_ref
        allow_short_circuit= False,
        vector_n           = 12,
        expand_n           = 8,
        jfyi_rules        = (
            "related_findings",
            "document_alerts",
            "remediation_deadline",
            "cert_surveillance_date",
        ),
        clarify_with = ("posture_findings", "document_alerts"),
    ),

    "DOCUMENT_CONTENT": TaxonomyEntry(
        type_id        = "DOCUMENT_CONTENT",
        display_name   = "Document Content Requirements",
        description    = "What a specific policy or procedure document must contain",
        tier           = 2,
        examples       = (
            "what must our access control policy contain?",
            "what should be in an incident response plan?",
            "what does ISO 27001 require in a risk assessment?",
            "what are the required elements of a supplier security policy?",
        ),
        answer_shape   = (
            "must_contain_checklist + should_contain_checklist + "
            "gdpr_required_items + upload_status"
        ),
        primary_source    = "graph",
        needs_posture     = False,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = False,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = True,   # checklist is primary content source
        allow_short_circuit= False,
        vector_n           = 10,
        expand_n           = 6,
        jfyi_rules        = (
            "upload_status",
            "linked_controls",
            "our_posture_on_control",
        ),
        clarify_with = ("document_alerts",),
    ),

    "STANDARD_KNOWLEDGE": TaxonomyEntry(
        type_id        = "STANDARD_KNOWLEDGE",
        display_name   = "Standard Knowledge",
        description    = "Definition or explanation of a standard, clause, or control",
        tier           = 2,
        examples       = (
            "what is ISO 27001?",
            "what does A.5.18 require?",
            "what is a non-conformity?",
            "what does OFI mean?",
            "what is clause 9.2?",
            "explain GDPR Art.32",
        ),
        answer_shape   = (
            "definition + obligation_text + "
            "business_context + implementation_notes"
        ),
        primary_source    = "graph",
        needs_posture     = False,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = False,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = False,
        allow_short_circuit= False,
        vector_n           = 8,
        expand_n           = 6,
        jfyi_rules        = (
            "our_posture_on_this",
            "related_controls",
        ),
        clarify_with = (),
    ),

    # ── TIER 3: Cross-cutting (multi-source synthesis) ───────────────────

    "CROSS_FRAMEWORK": TaxonomyEntry(
        type_id        = "CROSS_FRAMEWORK",
        display_name   = "Cross-Framework Analysis",
        description    = "How standards relate to each other and combined posture",
        tier           = 3,
        examples       = (
            "are we GDPR compliant?",
            "how does ISO 27701 map to GDPR Art.32?",
            "what GDPR obligations does our ISO 27001 NC affect?",
            "how does our ISO 27001 posture affect GDPR compliance?",
        ),
        answer_shape   = (
            "bridge_explanation(via ISO27701) + "
            "posture_on_bridge_controls + "
            "gdpr_articles_affected + priority_actions"
        ),
        primary_source    = "postgres+graph",
        needs_posture     = True,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = True,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = False,
        allow_short_circuit= False,
        vector_n           = 12,
        expand_n           = 8,
        jfyi_rules        = (
            "iso27701_load_status",
            "missing_privacy_docs",
            "cert_status",
        ),
        clarify_with = ("posture_findings",),
    ),

    "EVIDENCE_CHECK": TaxonomyEntry(
        type_id        = "EVIDENCE_CHECK",
        display_name   = "Evidence Check",
        description    = "What evidence exists or is needed for a control",
        tier           = 3,
        examples       = (
            "what evidence do we have for A.5.18?",
            "what would an auditor look for on access rights?",
            "what is missing to evidence A.5.18 compliance?",
            "can we demonstrate compliance with A.5.26?",
        ),
        answer_shape   = (
            "uploaded_docs + checklist_coverage(items_met/missing) + "
            "posture_finding + auditor_perspective"
        ),
        primary_source    = "postgres+graph",
        needs_posture     = True,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = True,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = True,
        allow_short_circuit= False,
        vector_n           = 10,
        expand_n           = 6,
        jfyi_rules        = (
            "document_alerts",
            "audit_timeline",
            "related_controls",
        ),
        clarify_with = ("document_alerts", "posture_findings"),
    ),

    "ASSESSMENT": TaxonomyEntry(
        type_id        = "ASSESSMENT",
        display_name   = "Compliance Assessment",
        description    = "Overall compliance picture and prioritised action list",
        tier           = 3,
        examples       = (
            "give me an overall compliance assessment",
            "what should we prioritise?",
            "where are we most at risk?",
            "what is our compliance readiness?",
            "summarise our ISO 27001 status",
        ),
        answer_shape   = (
            "cert_status + posture_summary(NC+OFI+Comply counts) + "
            "priority_gaps(by severity+deadline) + "
            "recommended_next_steps"
        ),
        primary_source    = "postgres",
        needs_posture     = True,
        needs_graph       = False,
        needs_chroma      = False,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = True,
        use_vector         = False,
        use_graph          = False,
        use_doc_inventory  = False,
        allow_short_circuit= False,
        vector_n           = 0,
        expand_n           = 0,
        jfyi_rules        = (
            "cert_surveillance_date",
            "document_alerts",
            "upcoming_deadlines",
        ),
        clarify_with = (),
    ),

    # ── TIER 4: Event-triggered (future) ─────────────────────────────────
    # Not routed by the classifier — detected by event_detector.py (not yet built)
    # Included here so the taxonomy is complete and the resolver can handle them

    "EVENT_RESPONSE": TaxonomyEntry(
        type_id        = "EVENT_RESPONSE",
        display_name   = "Event Response",
        description    = "Obligations and actions triggered by a specific event",
        tier           = 4,
        examples       = (
            "we had a data breach",
            "a client wants their data deleted",
            "we received a SAR from a data subject",
            "we are being audited next week",
        ),
        answer_shape   = (
            "event_type + immediate_actions(T+0 to T+72h) + "
            "notification_obligations + timeline + contacts"
        ),
        primary_source    = "graph",
        needs_posture     = False,
        needs_graph       = True,
        needs_chroma      = True,
        can_short_circuit = False,
        # ── Retrieval policy ──
        use_posture        = False,
        use_vector         = True,
        use_graph          = True,
        use_doc_inventory  = False,
        allow_short_circuit= False,
        vector_n           = 10,
        expand_n           = 8,
        jfyi_rules        = (
            "notification_deadlines",
            "dpa_contact",
            "related_obligations",
        ),
        clarify_with = (),
    ),
}


# =============================================================================
# CLASSIFIER PHRASES
# Maps classifier type strings (from existing classifier.py) to taxonomy types
# Allows incremental migration: classifier still uses old strings internally,
# taxonomy provides the richer metadata
# =============================================================================

# Legacy classifier type → taxonomy type mapping
CLASSIFIER_TO_TAXONOMY: dict[str, str] = {
    "gap_analysis":       "POSTURE_STATUS",     # "what are our gaps?"
    "posture_check":      "POSTURE_STATUS",     # "what is our posture?"
    "implementation":     "REMEDIATION_GUIDE",  # "what should we do?"
    "document_inventory": "DOCUMENT_STATUS",    # "have we uploaded X?"
    "document_content":   "DOCUMENT_CONTENT",   # "what must X contain?"
    "definition":         "STANDARD_KNOWLEDGE", # "what is X?"
    "cross_framework":    "CROSS_FRAMEWORK",    # "are we GDPR compliant?"
    "free_assessment":    "ASSESSMENT",         # "overall assessment"
    "unknown":            "POSTURE_STATUS",     # default to posture for now
}


def get_taxonomy_type(classifier_type: str) -> TaxonomyEntry:
    """
    Map a classifier output string to a TaxonomyEntry.
    Falls back to POSTURE_STATUS for unknown types.
    """
    taxonomy_id = CLASSIFIER_TO_TAXONOMY.get(classifier_type, "POSTURE_STATUS")
    return QUERY_TAXONOMY[taxonomy_id]


def get_by_id(type_id: str) -> TaxonomyEntry:
    """Get a TaxonomyEntry by its type_id. Raises KeyError if not found."""
    return QUERY_TAXONOMY[type_id]


def list_types(tier: int = None) -> list[TaxonomyEntry]:
    """List all taxonomy types, optionally filtered by tier."""
    entries = list(QUERY_TAXONOMY.values())
    if tier is not None:
        entries = [e for e in entries if e.tier == tier]
    return sorted(entries, key=lambda e: (e.tier, e.type_id))
