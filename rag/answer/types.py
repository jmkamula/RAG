"""
Data types for AnswerPayload — Ship 2 content-assembly layer.

Every taxonomy builder returns one of these payload variants. The
payload IS the truth for what refs, findings, and bridges must
appear in the answer. Downstream (Ship 3 polish) will preserve
these fields structurally; the LLM's role is prose only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any


# ══════════════════════════════════════════════════════════════════
# Supporting types — used across payload variants
# ══════════════════════════════════════════════════════════════════

@dataclass
class RefRecord:
    """A single control/article reference with its framework metadata."""
    ref:        str                        # "A.5.18" | "Art.32" | "9.1"
    framework:  str                        # "ISO27001:2022" | "GDPR:2016/679"
    title:      str = ""                   # from Neo4j RequirementNode.title
    node_id:    str = ""                   # full node_id for downstream lookups

    @property
    def is_gdpr(self) -> bool:
        return self.framework == "GDPR:2016/679"

    @property
    def is_iso(self) -> bool:
        return "ISO27001" in self.framework

    @property
    def is_27701(self) -> bool:
        return "ISO27701" in self.framework


@dataclass
class PostureFacet:
    """The tenant's posture for one control — deterministic from posture_controls."""
    ref:              RefRecord
    finding:          str                        # "NC" | "OFI" | "Comply" | "N/A" | "Not yet assessed"
    evidence_summary: str = ""                   # gap_description or similar
    engine_reason:    Optional[str] = None       # humanized ("2 of 4 requirements met")
    freshness_days:   Optional[int] = None
    updated_at:       Optional[str] = None
    partial_evidence: bool = False


@dataclass
class BridgeRecord:
    """One cross-framework bridge with its own posture (if available)."""
    from_ref:      RefRecord                     # the primary (e.g. Art.32)
    to_ref:        RefRecord                     # the bridge (e.g. A.5.15)
    relationship:  str = "IMPLEMENTS"            # IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE
    posture:       Optional[PostureFacet] = None
    direction:     str = "out"                   # out | in


@dataclass
class ChecklistItem:
    """A MUST/SHOULD item in a document requirement."""
    item_id:        str
    text:           str
    category:       str = "must"                 # "must" | "should"
    gdpr_required:  bool = False
    status:         Optional[str] = None         # "present" | "missing" | "partial" | None
    rationale:      str = ""


@dataclass
class DocumentRequirement:
    """Documents needed for a control — from doc_contexts / EvidenceRequirement."""
    control:         RefRecord
    doc_title:       str                         # "Access Control Policy"
    evidence_type:   str = ""                    # "policy" | "procedure" | "register"
    must_contain:    list[ChecklistItem] = field(default_factory=list)
    should_contain:  list[ChecklistItem] = field(default_factory=list)
    upload_status:   Optional[str] = None        # "uploaded" | "missing" | "outdated"
    freshness_days:  Optional[int] = None


@dataclass
class GapEntry:
    """One gap the tenant needs to address (for REMEDIATION_GUIDE)."""
    ref:            RefRecord
    severity:       str                          # "NC" | "OFI"
    what_missing:   str = ""
    why_matters:    str = ""
    what_to_do:     str = ""
    priority_rank:  int = 0                      # 1 = highest priority
    partial_evidence: bool = False


# ══════════════════════════════════════════════════════════════════
# Payload variants — one per QuestionType, plus freeform fallback
# ══════════════════════════════════════════════════════════════════

@dataclass
class AnswerPayloadBase:
    """Metadata common to all payload variants."""
    question_type:      str
    query:              str
    tenant_id:          str = ""
    tenant_name:        str = ""
    framework_primary:  str = ""
    frameworks_scope:   list[str] = field(default_factory=list)
    subject_refs:       list[RefRecord] = field(default_factory=list)
    signals_provenance: list[str] = field(default_factory=list)   # ["explicit_refs", "retrieval", ...]
    resolver_trace:     Optional[dict] = None
    build_latency_ms:   int = 0

    @property
    def variant_name(self) -> str:
        """Convenience — the class name is the variant identifier."""
        return self.__class__.__name__


@dataclass
class PostureStatusPayload(AnswerPayloadBase):
    """POSTURE_CHECK — 'is X compliant?', 'what is our A.5.18 status?'."""
    postures:            list[PostureFacet] = field(default_factory=list)
    xfw_bridges:         list[BridgeRecord] = field(default_factory=list)
    documents:           list[DocumentRequirement] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)


@dataclass
class DocumentStatusPayload(AnswerPayloadBase):
    """DOCUMENT_STATUS — 'have we uploaded X?', 'what docs are missing?'."""
    doc_alerts:     list[dict] = field(default_factory=list)     # {ref, title, alert_type}
    uploaded_docs:  list[dict] = field(default_factory=list)     # {ref, title, filename, uploaded_at}


@dataclass
class RemediationGuidePayload(AnswerPayloadBase):
    """REMEDIATION_GUIDE — 'how do we close the NC?', gap_analysis, implementation."""
    nc_gaps:         list[GapEntry] = field(default_factory=list)
    ofi_gaps:        list[GapEntry] = field(default_factory=list)
    xfw_context:     list[BridgeRecord] = field(default_factory=list)
    priority_order:  list[str] = field(default_factory=list)    # ordered refs by priority


@dataclass
class DocumentContentPayload(AnswerPayloadBase):
    """DOCUMENT_CONTENT — 'what must our X policy contain?'."""
    documents: list[DocumentRequirement] = field(default_factory=list)


@dataclass
class StandardKnowledgePayload(AnswerPayloadBase):
    """DEFINITION — 'what is OFI?', 'what does ISMS mean?', 'what is A.5.15?'."""
    acronym:               Optional[str] = None      # "OFI"
    expansion:             Optional[str] = None      # "Opportunity for Improvement"
    definition:            str = ""                  # plain-English one-liner
    business_description:  str = ""                  # from Chroma enrichment
    examples:              list[str] = field(default_factory=list)
    misconceptions:        list[str] = field(default_factory=list)


@dataclass
class CrossFrameworkPayload(AnswerPayloadBase):
    """CROSS_FRAMEWORK — 'GDPR compliance via ISO 27001', 'is Art.32 covered?'."""
    primary_posture:  Optional[PostureFacet] = None
    xfw_bridges:      list[BridgeRecord] = field(default_factory=list)
    framework_map:    dict[str, list[str]] = field(default_factory=dict)
                                                    # "ISO27001:2022": [refs...]


@dataclass
class FreeformPayload(AnswerPayloadBase):
    """Fallback for queries that don't fit a taxonomy. Passes through
    to today's rank_and_answer path with the payload as loose context.
    Explicit non-goal to scaffold freeform prose."""
    retrieved_nodes:  list[dict] = field(default_factory=list)
    posture_summary:  Optional[dict] = None
    reason_fallback:  str = ""                        # why we couldn't scaffold


# ══════════════════════════════════════════════════════════════════
# Validation result
# ══════════════════════════════════════════════════════════════════

@dataclass
class ValidationReport:
    """Output of validate() — invariants check on a payload."""
    passed:      bool = True
    violations:  list[str] = field(default_factory=list)   # hard failures
    warnings:    list[str] = field(default_factory=list)   # soft issues
    payload_variant: str  = ""

    def add_violation(self, msg: str) -> None:
        self.passed = False
        self.violations.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)
