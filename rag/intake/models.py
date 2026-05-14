"""
ArionComply — Intake Pipeline Models
Shared dataclasses used across all pipeline stages.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ExtractionPath(str, Enum):
    FULL_DOCUMENT  = "full"       # ≤ 100k tokens — one LLM call
    SECTION_BASED  = "sections"   # 100k-500k tokens — one call per section
    MANUAL_REVIEW  = "manual"     # > 500k tokens — human required
    STRUCTURED     = "structured" # XLSX/CSV with compliance columns — no LLM


class DocType(str, Enum):
    POLICY           = "policy"
    PROCEDURE        = "procedure"
    RISK_REGISTER    = "risk_register"
    EVIDENCE         = "evidence"
    AUDIT_REPORT     = "audit_report"
    ASSET_INVENTORY  = "asset_inventory"
    OTHER            = "other"


@dataclass
class RawSection:
    """One logical section extracted from a document."""
    section_id:   str             # e.g. "page_3", "heading_4.2", "sheet_Access"
    heading:      Optional[str]   # section heading if detected
    text:         str             # full text of this section
    page_start:   Optional[int]   # for PDFs
    page_end:     Optional[int]
    level:        int = 0         # heading level (0 = no heading, 1 = H1, 2 = H2, ...)
    metadata:     dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """
    Output of Stage 1 (reader) + Stage 2 (enricher).
    Contains full document text, detected structure, and extraction metadata.
    """
    # File identity
    source_file:      str
    file_type:        str           # pdf | docx | xlsx | txt | csv | api
    original_name:    str
    upload_id:        Optional[str] = None  # document_uploads.id

    # Raw structure (Stage 1)
    raw_sections:     list[RawSection] = field(default_factory=list)
    full_text:        str = ""
    token_estimate:   int = 0       # rough token count (chars / 4)
    page_count:       int = 0

    # Enrichment (Stage 2)
    doc_type:         Optional[str] = None
    doc_type_confidence: float = 0.0
    standard_ids:     list[str] = field(default_factory=list)
    scope_statement:  Optional[str] = None  # "this policy applies to..."
    explicit_refs:    list[str] = field(default_factory=list)  # control refs found by regex

    # Branching decision
    extraction_path:  ExtractionPath = ExtractionPath.FULL_DOCUMENT


@dataclass
class DocumentChunk:
    """
    One unit of text passed to the LLM extractor.
    For FULL_DOCUMENT path: one chunk = entire document.
    For SECTION_BASED path: one chunk = one section.
    """
    chunk_id:       str
    text:           str
    section:        Optional[str]   # section heading
    page_start:     Optional[int]
    page_end:       Optional[int]
    control_hints:  list[str]       # control refs this chunk likely covers
    doc_context:    str             # document title + scope — injected into every LLM call
    token_estimate: int = 0


@dataclass
class DocumentFinding:
    """
    One extracted compliance finding.
    Written to document_findings table.
    Multiple findings aggregate to one posture_controls row.
    """
    # Identity
    upload_id:       str            # document_uploads.id
    tenant_id:       str
    document_name:   str

    # Finding
    control_ref:     str            # normalized: A.5.18
    standard_id:     str            # ISO27001:2022
    finding:         str            # Comply | OFI | NC | not_addressed
    evidence_text:   str            # excerpt from document
    confidence:      str            # high | medium | low

    # Location
    section:         Optional[str] = None
    page_number:     Optional[int] = None

    # Extraction metadata
    extraction_path: str = "full"
    chunk_id:        Optional[str] = None

    # Set on write
    id:              Optional[str] = None


@dataclass
class PipelineResult:
    """Summary returned by the pipeline orchestrator."""
    upload_id:        str
    tenant_id:        str
    document_name:    str
    doc_type:         Optional[str]
    standard_ids:     list[str]
    extraction_path:  str
    findings_count:   int
    controls_assessed: list[str]
    controls_updated:  list[str]   # controls where posture_controls was updated
    status:           str          # extracted | failed | manual_review
    error:            Optional[str] = None
    duration_ms:      int = 0
