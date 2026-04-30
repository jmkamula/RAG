"""
RequirementNode — universal compliance requirement model.

Replaces ControlNode and GDPRObligationNode.
One node type for all standards: ISO 27001/27002, GDPR,
NIS2, NIST CSF, ISO 27701, PCI DSS, HIPAA etc.

Key design decisions:
  - Flat: one node per requirement per standard
  - Parsed from a single source document
  - No cross-standard knowledge baked into the node
  - Cross-framework intelligence lives in graph edges
  - ISO-specific fields are null for non-ISO nodes
  - cross_framework_summary pre-computed at index time
  - Posture always anchors to ISO control req_ids

Author: Compliance Intelligence Platform
Date:   April 2026
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json


# ── Enumerations ─────────────────────────────────────────────────────────────

class NodeType(str, Enum):
    CONTROL      = "control"      # ISO 27001/27002, CIS Controls
    OBLIGATION   = "obligation"   # GDPR, NIS2 — legal obligations
    REQUIREMENT  = "requirement"  # NIST CSF subcategories, PCI DSS


class ObligationType(str, Enum):
    ABSOLUTE      = "absolute"      # fixed, no wiggle room ("72 hours")
    RISK_BASED    = "risk_based"    # "appropriate to the risk"
    CONDITIONAL   = "conditional"   # applies in certain circumstances
    INFORMATIONAL = "informational" # no direct obligation (scope, definitions)


class EdgeType(str, Enum):
    IMPLEMENTS    = "IMPLEMENTS"    # ISO control directly implements obligation
    EQUIVALENT_TO = "EQUIVALENT_TO" # different standards, same requirement
    SUPPORTS      = "SUPPORTS"      # partial/corroborating coverage
    ENABLES       = "ENABLES"       # creates capability needed to fulfil
    GOVERNANCE    = "GOVERNANCE"    # management system governs the obligation
    PART_OF       = "PART_OF"       # hierarchy (point → paragraph → article)
    RELATED_TO    = "RELATED_TO"    # operationally linked, same standard
    DEPENDS_ON    = "DEPENDS_ON"    # prerequisite relationship


class ParseConfidence(str, Enum):
    HIGH   = "high"    # parsed cleanly from PDF with clear structure
    MEDIUM = "medium"  # parsed but required some inference
    LOW    = "low"     # seed data only — PDF section not found


# ── Cross-framework summary entry ─────────────────────────────────────────────

@dataclass
class CrossFrameworkEntry:
    """
    Pre-computed at index time. Cached on the node to avoid
    graph traversal at query time.
    """
    related_req_id:    str        # e.g. "GDPR:2016/679:Art.32.1.a"
    related_title:     str        # e.g. "Encryption of personal data"
    related_standard:  str        # e.g. "GDPR:2016/679"
    relationship_type: EdgeType
    confidence:        str        # "HIGH" | "MEDIUM" | "LOW"
    rationale:         str        # why this mapping exists
    posture_lookup_ref: str       # ISO req_id to look up posture
                                  # (always an ISO ref — posture anchors to ISO)

    def to_dict(self) -> dict:
        return {
            "related_req_id":    self.related_req_id,
            "related_title":     self.related_title,
            "related_standard":  self.related_standard,
            "relationship_type": self.relationship_type.value,
            "confidence":        self.confidence,
            "rationale":         self.rationale,
            "posture_lookup_ref": self.posture_lookup_ref,
        }


# ── Graph edge ────────────────────────────────────────────────────────────────

@dataclass
class RequirementEdge:
    """A directed relationship between two RequirementNodes."""
    source_id:         str
    target_id:         str
    edge_type:         EdgeType
    confidence:        str = "HIGH"
    rationale:         str = ""

    def to_dict(self) -> dict:
        return {
            "source_id":   self.source_id,
            "target_id":   self.target_id,
            "edge_type":   self.edge_type.value,
            "confidence":  self.confidence,
            "rationale":   self.rationale,
        }


# ── The universal node ────────────────────────────────────────────────────────

@dataclass
class RequirementNode:
    """
    A single requirement from a single compliance standard.

    Represents one of:
    - An ISO 27001/27002 control (e.g. A.8.24)
    - A GDPR article/paragraph/point (e.g. Art.32.1.a)
    - A NIS2 obligation (e.g. Art.21.2.h)
    - A NIST CSF subcategory (e.g. PR.DS-01)
    - Any other framework requirement

    No tenant data lives here. Ever.
    """

    # ── Identity ──────────────────────────────────────────────────────────────
    id:          str    # globally unique: "ISO27001:2022:A.8.24"
                        #                  "GDPR:2016/679:Art.32.1.a"
                        #                  "NIS2:2022:Art.21.2.h"
                        #                  "NISTCSF:2.0:PR.DS-01"
    standard_id: str    # "ISO27001:2022" | "GDPR:2016/679" | "NIS2:2022"
    ref:         str    # standard-native ref: "A.8.24" | "Art.32.1.a"
    title:       str    # human-readable title

    # ── Classification ────────────────────────────────────────────────────────
    node_type:        NodeType
    obligation_type:  ObligationType
    applies_to:       list[str] = field(default_factory=list)
    # ISO: ["all"]
    # GDPR: ["controller", "processor"] or ["controller"] or ["processor"]
    # NIS2: ["essential_entity", "important_entity"] or one of them

    # ── Normative content — from PDF parser ───────────────────────────────────
    obligation_text: str = ""   # verbatim text from the standard/regulation
    intent:          str = ""   # why this requirement exists
    guidance:        str = ""   # implementation guidance (where standard provides)
    # Note: GDPR provides no implementation guidance in the text itself —
    # that comes from EDPB guidelines, ingested separately as a related node.

    # ── Assessment content ────────────────────────────────────────────────────
    evidence_requirements: list[str] = field(default_factory=list)
    # What proof looks like — both ISO audit evidence and regulatory evidence.
    # For GDPR nodes these reflect Art.5(2) accountability requirements.

    gap_indicators: list[str] = field(default_factory=list)
    # Specific, detectable gaps the LLM looks for in client evidence.
    # Not generic — "policy exists but doesn't explicitly scope personal data"
    # rather than "incomplete policy".

    audit_question_refs: list[str] = field(default_factory=list)
    # e.g. ["Q195-A.8.24"] for ISO, ["D1.0", "D2.1"] for GDPR assessment

    # ── Hierarchy ─────────────────────────────────────────────────────────────
    parent_ref: Optional[str] = None
    # "A.8.24" → parent "A.8", "Art.32.1.a" → parent "Art.32.1" → "Art.32"

    chapter:    Optional[str] = None
    # ISO: "Technological" | "Organisational" | "People" | "Physical"
    # GDPR: "IV" (Controller and Processor)
    # NIS2: "IV" (Cybersecurity Risk-Management Measures)

    theme: Optional[str] = None
    # ISO theme label where applicable

    # ── ISO-specific attributes — null for non-ISO nodes ──────────────────────
    # From ISO 27002:2022 attribute taxonomy (your spreadsheet)
    control_types:          Optional[list[str]] = None
    cia_properties:         Optional[list[str]] = None
    cybersecurity_concepts: Optional[list[str]] = None  # NIST CSF alignment
    operational_caps:       Optional[list[str]] = None
    security_domains:       Optional[list[str]] = None

    # ── Cross-framework summary — pre-computed at index time ──────────────────
    # Populated by the merge pipeline after all standards are ingested.
    # Keyed by related_req_id. Avoids graph traversal at query time.
    cross_framework_summary: dict[str, CrossFrameworkEntry] = field(
        default_factory=dict
    )

    # ── Graph edges — populated during ingestion ──────────────────────────────
    edges: list[RequirementEdge] = field(default_factory=list)

    # ── Provenance ────────────────────────────────────────────────────────────
    source_pdf:       str = ""
    source_pages:     list[int] = field(default_factory=list)
    parse_confidence: ParseConfidence = ParseConfidence.HIGH
    parse_notes:      str = ""

    # ── Tier 1 enrichment fields ──────────────────────────────────────────────
    # business_description: plain-English practitioner translation of the
    #   obligation. Written per-node, not inherited from parent.
    # query_keywords: structured keyword surface for hybrid reranking.
    #   Keys: exact, practitioner, scenario, confusion
    business_description: str  = ""
    query_keywords:       dict = field(default_factory=dict)

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def is_iso(self) -> bool:
        return "ISO27001" in self.standard_id or "ISO27002" in self.standard_id

    @property
    def is_gdpr(self) -> bool:
        return "GDPR" in self.standard_id

    @property
    def is_nis2(self) -> bool:
        return "NIS2" in self.standard_id

    @property
    def related_standards(self) -> list[str]:
        """Standards referenced in cross_framework_summary."""
        return list({
            e.related_standard
            for e in self.cross_framework_summary.values()
        })

    @property
    def iso_posture_ref(self) -> Optional[str]:
        """
        The ISO req_id to use for posture lookup.
        For ISO nodes: self.id
        For non-ISO nodes: the IMPLEMENTS edge target (an ISO control)
        """
        if self.is_iso:
            return self.id
        # Find the IMPLEMENTS relationship pointing to an ISO control
        for entry in self.cross_framework_summary.values():
            if (entry.relationship_type == EdgeType.IMPLEMENTS
                    and "ISO27001" in entry.posture_lookup_ref):
                return entry.posture_lookup_ref
        return None

    def is_complete(self) -> bool:
        """True if all core content fields are populated."""
        return all([
            self.obligation_text,
            self.title,
            self.ref,
            self.standard_id,
        ])

    def missing_fields(self) -> list[str]:
        missing = []
        if not self.obligation_text:     missing.append("obligation_text")
        if not self.intent:              missing.append("intent")
        if not self.guidance and self.is_iso: missing.append("guidance")
        if not self.evidence_requirements: missing.append("evidence_requirements")
        if not self.gap_indicators:      missing.append("gap_indicators")
        return missing

    def add_cross_framework_entry(self, entry: CrossFrameworkEntry):
        """Add a cross-framework relationship. Called at index time."""
        self.cross_framework_summary[entry.related_req_id] = entry

    def get_cross_framework_for_standard(
        self, standard_id: str
    ) -> list[CrossFrameworkEntry]:
        """Return all cross-framework entries for a given standard."""
        return [
            e for e in self.cross_framework_summary.values()
            if e.related_standard == standard_id
        ]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":                      self.id,
            "standard_id":             self.standard_id,
            "ref":                     self.ref,
            "title":                   self.title,
            "node_type":               self.node_type.value,
            "obligation_type":         self.obligation_type.value,
            "applies_to":              self.applies_to,
            "obligation_text":         self.obligation_text,
            "intent":                  self.intent,
            "guidance":                self.guidance,
            "evidence_requirements":   self.evidence_requirements,
            "gap_indicators":          self.gap_indicators,
            "audit_question_refs":     self.audit_question_refs,
            "parent_ref":              self.parent_ref,
            "chapter":                 self.chapter,
            "theme":                   self.theme,
            "control_types":           self.control_types,
            "cia_properties":          self.cia_properties,
            "cybersecurity_concepts":  self.cybersecurity_concepts,
            "operational_caps":        self.operational_caps,
            "security_domains":        self.security_domains,
            "cross_framework_summary": {
                k: v.to_dict()
                for k, v in self.cross_framework_summary.items()
            },
            "edges":          [e.to_dict() for e in self.edges],
            "source_pdf":     self.source_pdf,
            "source_pages":   self.source_pages,
            "parse_confidence": self.parse_confidence.value,
            "parse_notes":    self.parse_notes,
            "business_description": self.business_description,
            "query_keywords":  self.query_keywords or {},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "RequirementNode":
        """Deserialise from a dict produced by to_dict(). Handles enum prefixes gracefully."""
        def _ev(enum_cls, raw):
            if raw is None: return list(enum_cls)[0]
            s = str(raw).split('.')[-1].lower()
            try: return enum_cls(s)
            except ValueError:
                for m in enum_cls:
                    if m.name.lower() == s: return m
                return list(enum_cls)[0]

        edges = []
        for e in (d.get('edges') or []):
            try:
                edges.append(RequirementEdge(
                    source_id  = e['source_id'],
                    target_id  = e['target_id'],
                    edge_type  = _ev(EdgeType, e.get('edge_type', 'RELATED_TO')),
                    confidence = e.get('confidence', 'MEDIUM'),
                    rationale  = e.get('rationale', ''),
                ))
            except Exception: pass

        xfw = {}
        for k, v in (d.get('cross_framework_summary') or {}).items():
            try:
                xfw[k] = CrossFrameworkEntry(
                    related_req_id     = v.get('related_req_id', k),
                    related_title      = v.get('related_title', ''),
                    related_standard   = v.get('related_standard', ''),
                    relationship_type  = _ev(EdgeType, v.get('relationship_type', 'RELATED_TO')),
                    confidence         = v.get('confidence', 'MEDIUM'),
                    rationale          = v.get('rationale', ''),
                    posture_lookup_ref = v.get('posture_lookup_ref', ''),
                )
            except Exception: pass

        node = cls(
            id                     = d.get('id', ''),
            standard_id            = d.get('standard_id', ''),
            ref                    = d.get('ref', ''),
            title                  = d.get('title', ''),
            node_type              = _ev(NodeType,       d.get('node_type',       'control')),
            obligation_type        = _ev(ObligationType, d.get('obligation_type', 'risk_based')),
            applies_to             = d.get('applies_to') or ['all'],
            obligation_text        = d.get('obligation_text', ''),
            intent                 = d.get('intent', ''),
            guidance               = d.get('guidance', ''),
            evidence_requirements  = d.get('evidence_requirements') or [],
            gap_indicators         = d.get('gap_indicators') or [],
            audit_question_refs    = d.get('audit_question_refs') or [],
            parent_ref             = d.get('parent_ref') or None,
            chapter                = d.get('chapter', ''),
            theme                  = d.get('theme', ''),
            control_types          = d.get('control_types') or [],
            cia_properties         = d.get('cia_properties') or [],
            cybersecurity_concepts = d.get('cybersecurity_concepts') or [],
            operational_caps       = d.get('operational_caps') or [],
            security_domains       = d.get('security_domains') or [],
            source_pdf             = d.get('source_pdf', ''),
            source_pages           = d.get('source_pages') or [],
            parse_confidence       = _ev(ParseConfidence, d.get('parse_confidence', 'medium')),
            parse_notes            = d.get('parse_notes', ''),
            business_description   = d.get('business_description', ''),
            query_keywords         = d.get('query_keywords') or {},
        )
        node.edges                   = edges
        node.cross_framework_summary = xfw
        return node


    def to_vector_document(self) -> str:
        """
        Flat text representation for embedding.

        Layer order (most to least semantically important):
          1. Header — standard + ref + title
          2. Business description — practitioner language (Tier 1 enrichment)
          3. Obligation text — canonical legal text
          4. Intent / guidance — recital context
          5. Evidence requirements — what compliance looks like
          6. Gap indicators — what non-compliance looks like
          7. Query keywords — explicit vocabulary surface
          8. Cross-framework titles — bridges standards in embedding space
        """
        parts = [
            f"{self.standard_id} {self.ref}: {self.title}",
        ]

        # Layer 2 — business description (Tier 1 enrichment)
        if self.business_description:
            parts.append(self.business_description)

        # Layer 3 — canonical obligation text
        if self.obligation_text:
            parts.append(self.obligation_text)

        # Layer 4 — intent and guidance
        if self.intent:
            parts.append(self.intent)
        if self.guidance:
            parts.append(self.guidance)

        # Layer 5 — evidence requirements
        if self.evidence_requirements:
            parts.append("Evidence: " + "; ".join(self.evidence_requirements))

        # Layer 6 — gap indicators
        if self.gap_indicators:
            parts.append("Gaps: " + "; ".join(self.gap_indicators))

        # Layer 7 — keyword vocabulary surface
        if self.query_keywords:
            all_kw = []
            for category in ("exact", "practitioner", "scenario"):
                all_kw.extend(self.query_keywords.get(category, []))
            if all_kw:
                parts.append("Keywords: " + ", ".join(all_kw))

        # Layer 8 — cross-framework titles
        for entry in self.cross_framework_summary.values():
            parts.append(
                f"Related {entry.related_standard}: {entry.related_title}"
            )

        return "\n".join(p for p in parts if p and p.strip())

    def to_vector_metadata(self) -> dict:
        """
        Metadata for vector store filtering.
        No tenant data — shared knowledge index only.
        """
        return {
            "id":          self.id,
            "standard_id": self.standard_id,
            "ref":         self.ref,
            "node_type":   self.node_type.value,
            "chapter":     self.chapter or "",
            "theme":       self.theme or "",
            "applies_to":  ",".join(self.applies_to),
            "is_iso":      self.is_iso,
            "is_gdpr":     self.is_gdpr,
            "is_nis2":     self.is_nis2,
            # For filtering by applicable standard at query time
            "related_standards": ",".join(self.related_standards),
        }


# ── Parse result ──────────────────────────────────────────────────────────────

@dataclass
class ParseResult:
    """Output of a single standard parse run."""
    standard_id: str
    source_pdf:  str
    nodes:       list[RequirementNode] = field(default_factory=list)
    edges:       list[RequirementEdge] = field(default_factory=list)
    warnings:    list[str]            = field(default_factory=list)
    errors:      list[str]            = field(default_factory=list)

    @property
    def complete_nodes(self) -> list[RequirementNode]:
        return [n for n in self.nodes if n.is_complete()]

    @property
    def incomplete_nodes(self) -> list[RequirementNode]:
        return [n for n in self.nodes if not n.is_complete()]

    @property
    def iso_nodes(self) -> list[RequirementNode]:
        return [n for n in self.nodes if n.is_iso]

    @property
    def gdpr_nodes(self) -> list[RequirementNode]:
        return [n for n in self.nodes if n.is_gdpr]

    def summary(self) -> str:
        lines = [
            f"Standard:         {self.standard_id}",
            f"Source:           {self.source_pdf}",
            f"Total nodes:      {len(self.nodes)}",
            f"Complete nodes:   {len(self.complete_nodes)}",
            f"Incomplete nodes: {len(self.incomplete_nodes)}",
            f"Graph edges:      {len(self.edges)}",
            f"Warnings:         {len(self.warnings)}",
            f"Errors:           {len(self.errors)}",
        ]
        if self.incomplete_nodes:
            lines.append("\nIncomplete nodes:")
            for n in self.incomplete_nodes:
                lines.append(
                    f"  {n.ref:12s} [{n.standard_id}] "
                    f"missing: {n.missing_fields()}"
                )
        if self.warnings:
            lines.append(f"\nWarnings (first 10):")
            for w in self.warnings[:10]:
                lines.append(f"  {w}")
        return "\n".join(lines)
