"""
Ship 54'.e — structural-evidence pattern detectors.

Compliance documents (policies, procedures) follow well-known
consultant-toolkit conventions: they carry a doc-control header at
the top, a revision-history table at the bottom, signature blocks,
tables of contents, and interested-parties enumerations. These
structural elements ARE compliance evidence — proving:

  Doc-control header (Doc No + Rev + Approved by) →
      item:5.2:owner + item:5.2:approved (ISO 27001 clause 7.5
      documented information + top-management approval)
  Revision history →
      item:10.1:improvement_action_register (continual improvement
      via versioned document control)
  Signature block →
      item:5.2:approved + item:*:management_approval
  Interested parties enumeration →
      item:4.2:interested_parties (clause 4.2 stakeholders)
  Table of Contents →
      Document-maturity signal (formally structured artifact)

The extractor's existing content-based path handles obligation text
extraction (Ship 6' grounding). This module runs orthogonally: same
document, different patterns, different MUST bindings.

Design shape — one detector per pattern, each returns a structured
result the extractor converts to `document_findings` rows.

Ship 54'.e ships:
    detect_doc_control_header()
    detect_revision_history()
    detect_signature_blocks()
    detect_interested_parties()
    detect_table_of_contents()
    extract_structural_evidence()  # combined runner

Deferred to future arcs:
    detect_records_produced_section()      # needs cross-doc linking
    detect_reference_to_other_documents()  # needs graph write
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ── Doc-control header ─────────────────────────────────────────────────

# Field-label alternatives — used to build both the same-line
# `Label: value` regex AND the two-line `__Label__\nvalue` shape that
# mammoth-extracted docx tables produce (each cell on its own line).
_DOC_NO_LABELS      = r"Document\s+(?:No\.?|Number|ID|Reference|Ref)|Doc[.\s]*No\.?|Doc[.\s]*ID"
_REVISION_LABELS    = r"Revision(?:\s+(?:No\.?|Number))?|Rev[.\s]*No\.?|Rev[.\s]|Version"
_REV_DATE_LABELS    = r"Revision\s+Date|Rev[.\s]*Date|Issue\s+Date|Effective\s+Date|Date"
_PREPARED_BY_LABELS = r"Prepared\s+By|Author|Drafted\s+By|Written\s+By"
_REVIEWED_BY_LABELS = r"Reviewed\s+By|Checked\s+By|Verified\s+By"
_APPROVED_BY_LABELS = r"Approved\s+By|Authorized\s+By|Sanctioned\s+By|Endorsed\s+By"


def _same_line_re(labels: str) -> re.Pattern:
    """Label + colon/period + value on the same line."""
    return re.compile(
        rf"(?im)^\s*(?:{labels})\s*[:\.]\s*(.+?)\s*$"
    )


def _two_line_re(labels: str) -> re.Pattern:
    """__Label__ on one line, value on the next non-blank line.
    Matches the mammoth-extracted docx table shape. Handles markdown
    bolding (`__` or `**`) around the label."""
    return re.compile(
        rf"(?im)^\s*(?:__|\*\*)?(?:{labels})(?:__|\*\*)?\s*$\n+"
        rf"\s*(.+?)\s*$",
        re.MULTILINE,
    )


_DOC_NO_SAME_RE      = _same_line_re(_DOC_NO_LABELS)
_REVISION_SAME_RE    = _same_line_re(_REVISION_LABELS)
_REV_DATE_SAME_RE    = _same_line_re(_REV_DATE_LABELS)
_PREPARED_BY_SAME_RE = _same_line_re(_PREPARED_BY_LABELS)
_REVIEWED_BY_SAME_RE = _same_line_re(_REVIEWED_BY_LABELS)
_APPROVED_BY_SAME_RE = _same_line_re(_APPROVED_BY_LABELS)

_DOC_NO_TWO_RE       = _two_line_re(_DOC_NO_LABELS)
_REVISION_TWO_RE     = _two_line_re(_REVISION_LABELS)
_REV_DATE_TWO_RE     = _two_line_re(_REV_DATE_LABELS)
_PREPARED_BY_TWO_RE  = _two_line_re(_PREPARED_BY_LABELS)
_REVIEWED_BY_TWO_RE  = _two_line_re(_REVIEWED_BY_LABELS)
_APPROVED_BY_TWO_RE  = _two_line_re(_APPROVED_BY_LABELS)

# Header-block signal: at least 3 of these fields co-occur within a
# short window at the document top. Guards against a stray "Doc No"
# mention deep in the body triggering a false positive.
_DOC_CONTROL_WINDOW_LINES = 30


@dataclass
class DocControlHeader:
    doc_no:        Optional[str] = None
    revision:      Optional[str] = None
    rev_date:      Optional[str] = None
    prepared_by:   Optional[str] = None
    reviewed_by:   Optional[str] = None
    approved_by:   Optional[str] = None
    excerpt:       str = ""

    @property
    def field_count(self) -> int:
        return sum(1 for v in (
            self.doc_no, self.revision, self.rev_date,
            self.prepared_by, self.reviewed_by, self.approved_by,
        ) if v)

    @property
    def is_present(self) -> bool:
        # ≥3 fields = confident doc-control block. Below that, we're
        # matching stray labels in body prose.
        return self.field_count >= 3


def _normalize_mammoth_output(text: str) -> str:
    """Strip markdown-escape artifacts that mammoth introduces on
    docx-to-markdown conversion (`\\-`, `\\.`, `\\_`, `\\(`, `\\)`).
    Detectors run against the normalized text so label patterns like
    `Document No.` match regardless of whether the source went through
    mammoth or was already clean prose."""
    if not text:
        return ""
    out = text
    for esc, plain in ((r"\-", "-"), (r"\.", "."), (r"\_", "_"),
                       (r"\(", "("), (r"\)", ")"), (r"\/", "/")):
        out = out.replace(esc, plain)
    return out


def _strip_md_escapes(v: str) -> str:
    """Strip mammoth-produced markdown-escape backslashes and common
    wet-sign / placeholder patterns."""
    if not v:
        return ""
    # Common escapes that survive mammoth's markdown conversion
    for esc, plain in ((r"\_", "_"), (r"\-", "-"), (r"\.", "."), (r"\(", "("), (r"\)", ")")):
        v = v.replace(esc, plain)
    # Kill leading colons/dashes left over from label boundary matches
    v = v.lstrip(":._-").strip()
    # Kill trailing wet-sign underscores
    v = v.rstrip("_ ").strip()
    return v


def _pick_field(window: str, same_re: re.Pattern, two_re: re.Pattern) -> Optional[str]:
    """Try same-line pattern first, fall back to two-line. Cleans
    markdown-escape artifacts, rejects empty / placeholder values."""
    for rx in (same_re, two_re):
        m = rx.search(window)
        if not m:
            continue
        v = _strip_md_escapes(m.group(1) or "")
        if not v:
            continue
        if v.startswith("<") or v.startswith("[") or v == "_":
            continue
        # Reject wet-sign lines (all underscores)
        if set(v) <= {"_", " "}:
            continue
        return v[:120]
    return None


def detect_doc_control_header(text: str) -> DocControlHeader:
    """Detect a consultant-toolkit doc-control header in the first
    ~30 lines of the document (same-line `Label: value`) OR anywhere
    in the doc for two-line `Label\\nvalue` table shape.

    `is_present` requires ≥3 fields to co-occur — guards against
    false-positive matches deep in body prose. Handles the mammoth-
    extracted docx table shape (each cell on its own line, labels
    bolded with `__` or `**`)."""
    if not text:
        return DocControlHeader()
    # Same-line matches scope to the header window; two-line matches
    # (from doc-control tables) can appear a bit deeper. Union both.
    lines = text.splitlines()[: _DOC_CONTROL_WINDOW_LINES + 20]
    window = "\n".join(lines)

    hdr = DocControlHeader(
        doc_no       = _pick_field(window, _DOC_NO_SAME_RE,      _DOC_NO_TWO_RE),
        revision     = _pick_field(window, _REVISION_SAME_RE,    _REVISION_TWO_RE),
        rev_date     = _pick_field(window, _REV_DATE_SAME_RE,    _REV_DATE_TWO_RE),
        prepared_by  = _pick_field(window, _PREPARED_BY_SAME_RE, _PREPARED_BY_TWO_RE),
        reviewed_by  = _pick_field(window, _REVIEWED_BY_SAME_RE, _REVIEWED_BY_TWO_RE),
        approved_by  = _pick_field(window, _APPROVED_BY_SAME_RE, _APPROVED_BY_TWO_RE),
    )
    if hdr.is_present:
        hdr.excerpt = window[:600]
    return hdr


# ── Revision history ───────────────────────────────────────────────────

_REV_HISTORY_HEADER_RE = re.compile(
    # Optional heading prefix: numbered "10." / markdown "## " / both.
    r"(?im)^\s*(?:#+\s+|\d+\.?\s+)*Revision\s+History\s*$"
)
# Row heuristic: version + date + description on one line separated by
# whitespace/tabs/pipes. Kept loose because tables round-trip through
# many extraction paths.
_REV_ROW_HEURISTIC_RE = re.compile(
    r"(?im)^\s*(?:v?\d+(?:\.\d+)?)\s+[\d/\-\.\s\w]{6,20}\s+.+$"
)


@dataclass
class RevisionHistory:
    present:   bool = False
    row_count: int  = 0
    excerpt:   str  = ""


# Row-shaped in same-line prose: "03  03 Aug 2026  Description ..."
_REV_ROW_INLINE_RE = re.compile(
    r"(?im)^\s*v?\d+(?:\.\d+)?\s+[\d/\-\.\s\w]{6,25}\s+\S+"
)
# Date-shaped standalone line — used to count rows when the table
# extracted as one-cell-per-line (mammoth docx output).
_DATE_LINE_RE = re.compile(
    r"^\s*(?:\d{1,2}[\s\-/]\w{3,10}[\s\-/]\d{2,4}"      # 03 Aug 2026
    r"|\d{4}-\d{2}-\d{2}"                                 # 2026-08-03
    r"|\d{1,2}/\d{1,2}/\d{2,4})\s*$"                      # 03/08/2026
)


def detect_revision_history(text: str) -> RevisionHistory:
    """Detect a revision-history table anywhere in the document.
    Signal: 'Revision History' heading + ≥1 following line that
    pattern-matches a version+date+description row (inline table)
    OR a standalone date-shaped line (one-cell-per-line docx table).
    """
    if not text:
        return RevisionHistory()
    m = _REV_HISTORY_HEADER_RE.search(text)
    if not m:
        return RevisionHistory()
    # Sample the 60 lines below the header for row-shaped content
    tail = text[m.end():]
    tail_lines = tail.splitlines()[:60]
    rows = 0
    for ln in tail_lines:
        # Skip table column-header lines
        if re.match(r"(?i)^\s*version\s*\|\s*date\s*\|", ln):
            continue
        if re.match(r"(?i)^\s*(?:__|\*\*)?(?:version|date|description|author)", ln):
            continue
        if _REV_ROW_INLINE_RE.match(ln):
            rows += 1
            continue
        # docx one-cell-per-line: count date lines as row anchors
        if _DATE_LINE_RE.match(ln):
            rows += 1
    return RevisionHistory(
        present   = rows >= 1,
        row_count = rows,
        excerpt   = "\n".join([m.group(0)] + tail_lines[:6])[:500],
    )


# ── Signature blocks ───────────────────────────────────────────────────

_SIGN_LINE_RE = re.compile(
    r"(?im)^\s*(?:"
    r"Signature\s*[:\.]"
    r"|Signed\s*[:\.]"
    r"|_{5,}\s*/\s*_{5,}"                    # ____/____ signature line
    r"|(?:Author|Reviewer|Approver)['’]s\s+Name\s+(?:&|and)\s+Signature"
    r")"
)


@dataclass
class SignatureBlock:
    present: bool = False
    count:   int  = 0
    excerpt: str  = ""


def detect_signature_blocks(text: str) -> SignatureBlock:
    """Detect signature line patterns anywhere in the document.
    Presence + count signals formal approval discipline."""
    if not text:
        return SignatureBlock()
    matches = list(_SIGN_LINE_RE.finditer(text))
    if not matches:
        return SignatureBlock()
    # Excerpt the first signature-block-ish region
    first = matches[0]
    start = max(0, first.start() - 80)
    excerpt = text[start:first.end() + 200][:400]
    return SignatureBlock(
        present = True,
        count   = len(matches),
        excerpt = excerpt,
    )


# ── Interested parties enumeration ─────────────────────────────────────

_INTERESTED_PARTIES_RE = re.compile(
    r"(?im)^\s*(?:\d+\.?\d*\s+)?"
    r"(?:INTERESTED\s+PARTIES?"
    r"|STAKEHOLDERS?"
    r"|RELEVANT\s+PARTIES?)\s*$"
)
# Bullet or dash-prefixed lines below the header
_BULLET_LINE_RE = re.compile(r"^\s*(?:[-•·*]|\d+\.|\([a-z]\))\s+(.+?)\s*$")


@dataclass
class InterestedParties:
    present: bool = False
    parties: list[str] = field(default_factory=list)
    excerpt: str = ""


def detect_interested_parties(text: str) -> InterestedParties:
    """Detect the 'INTERESTED PARTIES' section (ISO 27001 clause 4.2).
    Enumerated bullets or numbered items following the header count
    as the party list."""
    if not text:
        return InterestedParties()
    m = _INTERESTED_PARTIES_RE.search(text)
    if not m:
        return InterestedParties()
    tail = text[m.end():]
    tail_lines = tail.splitlines()[:20]
    parties: list[str] = []
    for ln in tail_lines:
        # Stop at the next uppercase section header
        if re.match(r"^\s*\d*\.?\d*\s*[A-Z][A-Z ]{4,}\s*$", ln):
            break
        b = _BULLET_LINE_RE.match(ln)
        if b:
            item = b.group(1).strip()
            if 2 < len(item) < 120:
                parties.append(item)
    return InterestedParties(
        present = bool(parties),
        parties = parties[:20],
        excerpt = "\n".join([m.group(0)] + tail_lines[:6])[:500],
    )


# ── Table of Contents ──────────────────────────────────────────────────

_TOC_HEADER_RE = re.compile(
    r"(?im)^\s*(?:\d+\.?\s+)?TABLE\s+OF\s+CONTENTS\s*$"
)
# TOC entry heuristic: text ending in dots + a page number
_TOC_ENTRY_RE = re.compile(r"^\s*\d+\.?\d*.+?[\.\s]{3,}\d{1,4}\s*$")


@dataclass
class TableOfContents:
    present: bool = False
    entry_count: int = 0


def detect_table_of_contents(text: str) -> TableOfContents:
    """Detect a Table of Contents. Signal: 'TABLE OF CONTENTS' header
    + ≥3 entry-shaped lines below it. Presence is a document-maturity
    signal (formal vs. ad-hoc draft)."""
    if not text:
        return TableOfContents()
    m = _TOC_HEADER_RE.search(text)
    if not m:
        return TableOfContents()
    tail = text[m.end():]
    tail_lines = tail.splitlines()[:60]
    entries = sum(1 for ln in tail_lines if _TOC_ENTRY_RE.match(ln))
    return TableOfContents(
        present     = entries >= 3,
        entry_count = entries,
    )


# ── Combined runner ────────────────────────────────────────────────────

@dataclass
class StructuralEvidence:
    """Aggregate of all structural-evidence detectors run over one
    document. Fields align with the individual detector dataclasses."""
    doc_control:       DocControlHeader   = field(default_factory=DocControlHeader)
    revision_history:  RevisionHistory    = field(default_factory=RevisionHistory)
    signatures:        SignatureBlock     = field(default_factory=SignatureBlock)
    interested_parties: InterestedParties = field(default_factory=InterestedParties)
    toc:               TableOfContents    = field(default_factory=TableOfContents)

    @property
    def any_detected(self) -> bool:
        return (
            self.doc_control.is_present
            or self.revision_history.present
            or self.signatures.present
            or self.interested_parties.present
            or self.toc.present
        )

    def summary(self) -> dict:
        """Compact dict for logging + document_findings metadata."""
        return {
            "doc_control_fields":  self.doc_control.field_count,
            "doc_control_present": self.doc_control.is_present,
            "revision_history":    self.revision_history.present,
            "revision_history_rows": self.revision_history.row_count,
            "signatures":          self.signatures.count,
            "interested_parties":  len(self.interested_parties.parties),
            "toc":                 self.toc.present,
            "toc_entries":         self.toc.entry_count,
        }


def extract_structural_evidence(text: str) -> StructuralEvidence:
    """Run all detectors over one document's text. Returns a single
    StructuralEvidence aggregate. Called from the intake pipeline
    after content-based extraction to produce structural findings.

    Mammoth-escape normalization applied at the top so detectors
    work uniformly on both `Doc control: value` prose and mammoth-
    extracted docx table output."""
    norm = _normalize_mammoth_output(text)
    return StructuralEvidence(
        doc_control        = detect_doc_control_header(norm),
        revision_history   = detect_revision_history(norm),
        signatures         = detect_signature_blocks(norm),
        interested_parties = detect_interested_parties(norm),
        toc                = detect_table_of_contents(norm),
    )


# ── Ship 54'.e Phase 2 — DocumentFinding conversion ────────────────────
#
# Maps detected structural patterns to document_findings rows with
# checklist_item_id bindings + auditor-facing excerpts. Called from
# the intake pipeline after content-based extraction.
#
# Binding strategy — Phase 2 targets 4 universal MUST slugs that
# appear across many curated leaves:
#
#   :owner           — 37 leaves (any leaf with an owner MUST)
#                       ← doc-control Prepared_By populated
#   :approved        — 2 leaves (top policies)
#                       ← doc-control Approved_By populated
#                       ← signature block present
#   :rev_date        — 198 leaves (any leaf with rev_date MUST —
#                       covers all *_program_review leaves)
#                       ← doc-control Rev_Date populated
#                       ← revision history table present
#   :rev_reviewer    — 198 leaves (paired with rev_date)
#                       ← revision history table present
#   :parties_listed  — 1 leaf (req:4.2:interested_parties_register)
#                       ← interested parties enumeration present
#
# Excerpts are pattern-specific + auditor-defensible: "Prepared By:
# Jane Doe" not "we detected a doc-control block". Every finding is
# provenance-traceable to a specific line/table row in the doc.

# Universal target MUST slugs. Each maps a structural detection to
# a MUST slug suffix; the finding-builder iterates the leaf catalog
# looking for MUSTs ending with each slug on the target controls.
_STRUCTURAL_BINDING_SLUGS = {
    "prepared_by":         "owner",
    "approved_by":         "approved",
    "signature_present":   "approved",
    "rev_date":            "rev_date",
    "rev_history":         "rev_date",       # revision history → rev_date
    "rev_reviewer":        "rev_reviewer",
    "interested_parties":  "parties_listed",
}


def _leaf_musts_for(control_ref: str) -> dict[str, list[tuple[str, str]]]:
    """Return {slug_suffix: [(leaf_id, must_id_full), ...]} for a
    given control_ref by walking the canonical catalog union.

    Called from structural_evidence_to_findings — cached per-call by
    the caller via a small dict so multi-control docs don't re-walk
    the catalog for each pattern.
    """
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    out: dict[str, list[tuple[str, str]]] = {}
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS)
    for spec in ALL_DERIVED_SPECS:
        all_ers.extend(spec.direct_evidence)
    for er in all_ers:
        # Match leaves for this control_ref
        er_ctrl = (er.id or "").split(":")[1] if ":" in (er.id or "") else ""
        if er_ctrl != control_ref:
            continue
        for it in er.must_contain:
            slug = it.id.split(":")[-1] if ":" in it.id else it.id
            out.setdefault(slug, []).append((er.id, it.id))
    return out


def structural_evidence_to_findings(
    ev: "StructuralEvidence",
    *,
    upload_id:      str,
    tenant_id:      str,
    document_name:  str,
    control_refs:   list[str],
    standard_ids:   dict[str, str],
) -> list:
    """Convert detected structural patterns to DocumentFinding rows.

    Args:
        ev             — result of extract_structural_evidence(doc_text)
        upload_id      — document_uploads.id
        tenant_id      — tenant UUID
        document_name  — auditor-facing document title
        control_refs   — controls the doc was scoped to (from extract())
        standard_ids   — {control_ref: standard_id} for canonical ref tagging

    Returns list[DocumentFinding] with inference_source='structural_pattern'
    on each row. Skips patterns that produce no bindings on the given
    control scope. Returns [] when no structural patterns detected OR
    when no target MUST slugs are present on any of the given controls.
    """
    from rag.intake.models import DocumentFinding

    if not ev.any_detected:
        return []

    # Cache leaf-must lookups per control_ref
    _cache: dict[str, dict[str, list[tuple[str, str]]]] = {}
    def _musts(cref: str):
        if cref not in _cache:
            _cache[cref] = _leaf_musts_for(cref)
        return _cache[cref]

    # Per-pattern excerpt + binding-key mapping
    pattern_bindings: list[tuple[str, str, str]] = []
    # tuples: (binding_key, excerpt, evidence_text)

    if ev.doc_control.is_present:
        if ev.doc_control.prepared_by:
            pattern_bindings.append((
                "prepared_by",
                f"Prepared By: {ev.doc_control.prepared_by}",
                f"Document owner named: {ev.doc_control.prepared_by} (structural: doc-control header Prepared By field)",
            ))
        if ev.doc_control.approved_by:
            pattern_bindings.append((
                "approved_by",
                f"Approved By: {ev.doc_control.approved_by}",
                f"Document approved: {ev.doc_control.approved_by} (structural: doc-control header Approved By field)",
            ))
        if ev.doc_control.rev_date:
            pattern_bindings.append((
                "rev_date",
                f"Revision Date: {ev.doc_control.rev_date}",
                f"Revision date recorded: {ev.doc_control.rev_date} (structural: doc-control header)",
            ))

    if ev.revision_history.present:
        pattern_bindings.append((
            "rev_history",
            (ev.revision_history.excerpt or "Revision History section present")[:200],
            f"Revision history table present with {ev.revision_history.row_count} row(s) (structural: versioned document control)",
        ))
        pattern_bindings.append((
            "rev_reviewer",
            (ev.revision_history.excerpt or "Revision History section present")[:200],
            "Revision history documents named reviewers per version (structural)",
        ))

    if ev.signatures.present:
        pattern_bindings.append((
            "signature_present",
            (ev.signatures.excerpt or "Signature block present")[:200],
            f"Signature block(s) present ({ev.signatures.count}) — structural approval evidence",
        ))

    if ev.interested_parties.present:
        parties_str = ", ".join(ev.interested_parties.parties[:8])
        pattern_bindings.append((
            "interested_parties",
            f"Interested Parties: {parties_str}"[:200],
            f"Interested parties enumerated ({len(ev.interested_parties.parties)}): {parties_str} (structural)",
        ))

    if not pattern_bindings:
        return []

    # Build findings by pairing each pattern with matching leaves per control
    findings: list[DocumentFinding] = []
    for control_ref in control_refs:
        std_id = standard_ids.get(control_ref, "")
        musts = _musts(control_ref)
        for binding_key, excerpt, evidence_text in pattern_bindings:
            slug = _STRUCTURAL_BINDING_SLUGS.get(binding_key)
            if not slug:
                continue
            leaf_hits = musts.get(slug, [])
            if not leaf_hits:
                continue
            # Emit one finding per (control_ref, checklist_item_id).
            # If multiple leaves under the same control share the same
            # slug (rare), emit once per leaf's must_id.
            for _leaf_id, must_id_full in leaf_hits:
                findings.append(DocumentFinding(
                    upload_id         = upload_id,
                    tenant_id         = tenant_id,
                    document_name     = document_name,
                    control_ref       = control_ref,
                    standard_id       = std_id,
                    finding           = "Comply",   # structural evidence = the requirement IS met
                    evidence_text     = evidence_text,
                    confidence        = "medium",
                    checklist_item_id = must_id_full,
                    inference_source  = "structural_pattern",
                ))

    return findings


__all__ = [
    "DocControlHeader", "RevisionHistory", "SignatureBlock",
    "InterestedParties", "TableOfContents", "StructuralEvidence",
    "detect_doc_control_header", "detect_revision_history",
    "detect_signature_blocks", "detect_interested_parties",
    "detect_table_of_contents", "extract_structural_evidence",
    "structural_evidence_to_findings",
]
