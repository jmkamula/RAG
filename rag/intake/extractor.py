"""
ArionComply — Compliance Evidence Extractor
Stage 3: Extract compliance findings from document text.

Three paths:
  STRUCTURED    → parse rows directly (no LLM) from XLSX/CSV workbook
  FULL_DOCUMENT → one LLM call for the entire document
  SECTION_BASED → one LLM call per section, findings aggregated

Approach B throughout: LLM confirms coverage of a pre-scoped control list.
It never discovers controls — only confirms whether the text addresses known controls.
"""
from __future__ import annotations

import json
import logging
import re
import time
import urllib.request
import urllib.error
from typing import Optional

from .models import (
    DocumentChunk, DocumentFinding, ExtractionPath,
    ParsedDocument, RawSection,
)
from .ref_normalizer import (
    DOC_TYPE_CLAUSE_MAP, extract_refs_from_text,
    get_clause_scope, normalize_ref,
)

logger = logging.getLogger(__name__)

# Extraction LLM — use Sonnet for quality, Haiku for speed/cost
EXTRACT_MODEL = "claude-sonnet-4-6"

# Max controls per LLM call — avoid overwhelming the model
MAX_CONTROLS_PER_CALL = 25

# Section size limit for SECTION_BASED path
MAX_SECTION_TOKENS = 80_000   # ~320k chars per section call


def extract(
    doc:       ParsedDocument,
    controls:  list[dict],    # [{ref, title, standard_id}] from Neo4j
    api_key:   str,
) -> list[DocumentFinding]:
    """
    Main extraction entry point.
    Returns list of DocumentFinding — one per control assessed.
    """
    if doc.extraction_path == ExtractionPath.MANUAL_REVIEW:
        logger.warning(f"Skipping extraction — document flagged for manual review: {doc.original_name}")
        return []

    if doc.extraction_path == ExtractionPath.STRUCTURED:
        # Workbook intake architecture (Part A, 2026-06-23): for xlsx/xlsm/xls
        # files the workbook_persistence path (Stage 4.6) is the canonical
        # finding writer — it uses db/workbook_mappings/*.yaml for
        # deterministic per-MUST binding (the 92%-bind-rate path). Running
        # _extract_structured in parallel produced duplicate, unbound
        # findings that cluttered Stage-1 (the 93-unbound problem on the
        # 2026-06-23 Arion re-upload). Sheets with no YAML mapping now
        # produce 0 findings here + an unmapped-sheet telemetry signal;
        # operators see "needs new YAML" instead of "noisy approximation".
        # CSV files still go through _extract_structured (no
        # multi-sheet structure for workbook_persistence to use).
        if (doc.file_type or "").lower() in ("xlsx", "xlsm"):
            n_mapped, n_unmapped, unmapped_names = _classify_workbook_sheets(doc)
            doc.extraction_metrics["workbook_sheets_total"]    = n_mapped + n_unmapped
            doc.extraction_metrics["workbook_sheets_mapped"]   = n_mapped
            doc.extraction_metrics["workbook_sheets_unmapped"] = n_unmapped
            if unmapped_names:
                doc.extraction_metrics["workbook_unmapped_sheets"] = ", ".join(unmapped_names[:10])
                logger.info(
                    "workbook %s: %d unmapped sheets (need YAMLs): %s",
                    doc.original_name, n_unmapped, ", ".join(unmapped_names),
                )
            logger.info(
                "workbook %s: structured extraction retired; "
                "workbook_persistence (Stage 4.6) is the canonical path",
                doc.original_name,
            )
            return []
        return _extract_structured(doc)

    # TOC / document-index filter — same shape as the questionnaire filter
    # but at the doc level. TOC docs describe what policies exist; their
    # body is "X.Y Title — Purpose: Defines …" blurbs that read like real
    # statements of compliance but are just descriptions OF other docs.
    # Without this gate every uploaded TOC produces dozens of inert
    # findings (no checklist_item_id, can't feed engine post Phase-1
    # retirement) that clutter the Stage-1 queue. Surfaced 2026-06-15 by
    # a "TOC Information Security Documents.docx" upload producing 47
    # spurious pending findings.
    toc_reason = _looks_like_toc(doc)
    if toc_reason:
        logger.info(
            "Skipping extraction — document looks like a TOC/index: %s (%s)",
            doc.original_name, toc_reason,
        )
        doc.extraction_metrics["skipped_as_toc"] = toc_reason
        return []

    # Templated-upload fast-path: when the doc text contains
    # <<MUST item:X>> markers (because the tenant downloaded one of our
    # template scaffolds, edited it, and uploaded back), bind per-MUST
    # deterministically without any LLM call. Per-MUST evidence is the
    # tenant's text between the marker and the next marker / section /
    # rule. See _extract_templated() in this module.
    templated_findings = _extract_templated(doc)
    if templated_findings is not None:
        doc.extraction_metrics["templated_findings"] = len(templated_findings)
        logger.info(
            "Templated fast-path: %s → %d findings (no LLM call)",
            doc.original_name, len(templated_findings),
        )
        return templated_findings

    # Doc-mapping pre-filter (db/doc_mappings/*.yaml) — analog of the
    # workbook intake YAML matcher, applied to docs. When a canonical
    # doc-shape mapping matches the upload (e.g. "Supplier Vendor
    # Security Policy.docx" → supplier_security_policy.yaml), we scope
    # the LLM candidate set to ONLY that mapping's target_leaves' parent
    # controls. Replaces the broad DOC_TYPE_CLAUSE_MAP path (which let
    # one "policy" doc be evaluated against all of A.5-A.8) with a
    # tight per-shape scope. Soft fallback to _scope_controls when no
    # mapping matches — older / mapping-less docs continue to work.
    scoped = _scope_controls_via_doc_mappings(controls, doc)
    if not scoped:
        scoped = _scope_controls(controls, doc)
    if not scoped:
        logger.warning(f"No controls scoped for {doc.original_name} — using all controls")
        scoped = controls[:MAX_CONTROLS_PER_CALL]

    # Telemetry: how many candidates did we scope to? Combined with
    # findings_kept downstream, gives the per-doc yield ratio.
    doc.extraction_metrics["candidate_controls"] = len(scoped)
    doc.extraction_metrics["paragraph_chars"]    = len(doc.full_text or "")
    doc.extraction_metrics["markdown_chars"]     = len(doc.markdown or "")
    # Fallback: when doc_mappings didn't match (legacy _scope_controls
    # path took over), primary == union. The legacy path doesn't have a
    # "primary" notion — every control in the clause-scope is equally
    # weighted. Set primary = len(scoped) so the yield ratio computes
    # the same as the old behaviour; the schema_v36 distinction kicks
    # in only when doc_mappings narrows below the union.
    doc.extraction_metrics.setdefault("primary_candidate_controls", len(scoped))

    # Per-MUST binding: when doc_mappings narrowed to specific leaves, fetch
    # those leaves' checklist items from Neo4j and pass them to the LLM as
    # candidate ids. Findings come back tagged with checklist_item_id; the
    # writer persists the binding. Without this, findings stay at Phase-1
    # coarse coverage and can't feed the engine (post 2026-06-13 retirement).
    target_leaves = doc.extraction_metrics.get("target_leaves") or []
    leaf_musts = None
    if target_leaves:
        leaf_ids = [t.get("leaf_id") for t in target_leaves if t.get("leaf_id")]
        leaf_musts = _fetch_leaf_musts(leaf_ids)
        doc.extraction_metrics["leaf_musts_count"] = sum(
            len(items) for items in leaf_musts.values()
        )

    if doc.extraction_path == ExtractionPath.FULL_DOCUMENT:
        return _extract_full(doc, scoped, api_key, leaf_musts=leaf_musts)
    else:  # SECTION_BASED
        return _extract_sections(doc, scoped, api_key, leaf_musts=leaf_musts)


# =============================================================================
# WORKBOOK SHEET CLASSIFIER (Part A, 2026-06-23)
# =============================================================================

# Threshold for "sheet name probably matches a YAML". 0.5 jaccard requires
# at least half the sheet-name tokens to be in the YAML's fingerprints.
# Lower = more permissive (fewer flagged unmapped); higher = stricter.
_WORKBOOK_SHEET_MATCH_THRESHOLD = 0.5


def _classify_workbook_sheets(doc: ParsedDocument) -> tuple[int, int, list[str]]:
    """Return (n_mapped, n_unmapped, unmapped_sheet_names) for the
    workbook's content sheets (meta sheets already filtered by reader).

    A sheet is 'mapped' when at least one db/workbook_mappings/*.yaml
    has sheet_name_fingerprints scoring above the threshold. This is
    a telemetry-grade signal — workbook_persistence does its own full
    discovery at Stage 4.6 with column/row scoring on top.

    Silent on import errors / missing mappings — degrades gracefully.
    """
    try:
        from rag.intake.workbook_discovery import load_mappings, _best_sheet_name_score
        mappings = load_mappings()
    except Exception as e:
        logger.warning(f"_classify_workbook_sheets: load failed: {e}")
        return 0, 0, []

    n_mapped = 0
    n_unmapped = 0
    unmapped_names: list[str] = []
    for section in doc.raw_sections:
        sheet_name = (section.metadata or {}).get("sheet_name") or section.heading or ""
        if not sheet_name:
            continue
        try:
            best = max(
                (_best_sheet_name_score(sheet_name, m) for m in mappings),
                default=0.0,
            )
        except Exception:
            best = 0.0
        if best >= _WORKBOOK_SHEET_MATCH_THRESHOLD:
            n_mapped += 1
        else:
            n_unmapped += 1
            unmapped_names.append(sheet_name)
    return n_mapped, n_unmapped, unmapped_names


# =============================================================================
# TEMPLATED PATH — uploads derived from db/templates/*.md scaffolds
# =============================================================================

# Marker shape mirrors enrichment/templates/load_to_postgres.py — tight to
# real item-ID structure (avoids false positives on example placeholders).
_TEMPLATED_MUST_RE   = re.compile(
    r"<<MUST\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>", re.IGNORECASE,
)
_TEMPLATED_SHOULD_RE = re.compile(
    r"<<SHOULD\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>", re.IGNORECASE,
)
_TEMPLATED_TEXT_PLACEHOLDER = re.compile(r"<<\s*TEXT\s*>>", re.IGNORECASE)
_TEMPLATED_NAME_PLACEHOLDER = re.compile(r"<<\s*NAME\s*>>", re.IGNORECASE)
_TEMPLATED_WHY_LINE         = re.compile(r"^\s*_Why:\s.*?_\s*$", re.MULTILINE)
_TEMPLATED_EDIT_ZONE_RE     = re.compile(
    r"<!--\s*EDIT-ZONE-START\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->"
    r"(.*?)"
    r"<!--\s*EDIT-ZONE-END\s+\1\s*-->",
    re.DOTALL | re.IGNORECASE,
)
# Tabular variant — single edit zone per LEAF (not per-MUST), wrapping
# a markdown table. The column→MUST mapping lives in a sibling
# TABLE-COLUMNS metadata block.
_TEMPLATED_TABLE_ZONE_RE    = re.compile(
    r"<!--\s*EDIT-ZONE-START\s+leaf:(req:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->"
    r"(.*?)"
    r"<!--\s*EDIT-ZONE-END\s+leaf:\1\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_TEMPLATED_TABLE_COLUMNS_RE = re.compile(
    r"<!--\s*TABLE-COLUMNS\s+leaf:(req:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->"
    r"(.*?)"
    r"<!--\s*/TABLE-COLUMNS\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_TEMPLATED_TABLE_COLUMN_RE  = re.compile(
    r"<!--\s*column:\s*(item:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->",
)
_TEMPLATED_PREFILL_COMMENT  = re.compile(
    r"<!--\s*prefilled\s+from\s+[^>]*-->",
    re.IGNORECASE,
)


def _control_ref_to_standard(control_ref: str) -> str:
    """Map a control_ref prefix to its standard_id. Aligns with the rest
    of the intake pipeline's normalisation (rag/intake/ref_normalizer.py)."""
    if control_ref.startswith("Art."):
        return "GDPR:2016/679"
    # ISO 27001 covers both Annex A (A.5.x, A.7.x...) and ISMS clauses (4.x..10.x)
    return "ISO27001:2022"


def _is_pure_scaffolding(zone_text: str) -> bool:
    """Return True when the edit-zone content is purely template
    scaffolding — placeholder still intact, or only prefilled prior
    evidence with no tenant authorship added.

    Triggers:
      - empty/whitespace only
      - just the <<TEXT>>/<<NAME>> placeholder
      - prefill block (zero or more **From <doc>:** segments followed by
        a <!-- prefilled from N -->/<!-- prefilled from <doc> via ... -->
        comment) with NOTHING substantive after the closing comment
    """
    text = zone_text.strip()
    if not text:
        return True
    # Strip the placeholders → if nothing remains, no tenant content
    no_text = _TEMPLATED_TEXT_PLACEHOLDER.sub("", text)
    no_name = _TEMPLATED_NAME_PLACEHOLDER.sub("", no_text).strip()
    if not no_name:
        return True
    # Pure prefill detection: zone ends with prefill comment + nothing
    # substantive after. We don't try to verify the body matches the
    # exact render — the comment + closing position is the signal.
    m = _TEMPLATED_PREFILL_COMMENT.search(text)
    if m:
        trailing = text[m.end():].strip()
        # Allow trailing horizontal rules / heading transitions
        trailing = re.sub(r"^[-=]{3,}\s*$|^#{1,}\s.*$", "", trailing, flags=re.MULTILINE).strip()
        if not trailing:
            return True
    return False


def _extract_templated(doc: ParsedDocument) -> Optional[list[DocumentFinding]]:
    """Templated-upload fast path.

    Two extraction modes:

    A. **Edit-zone mode (preferred)** — when the upload contains
       `<!-- EDIT-ZONE-START item:X -->...<!-- EDIT-ZONE-END item:X -->`
       markers (added by the render endpoint), parse zones directly.
       This isolates tenant authorship from template scaffolding
       (guidance prose + prefilled prior evidence) — no circular
       counting. Sections where the zone holds only scaffolding are
       skipped.

    B. **Legacy mode** — when no edit zones are found (older renders or
       direct uploads not via the render endpoint), fall back to the
       full-section scan that strips `_Why:` lines + placeholders. This
       can produce false positives on v2 hand-refined templates that
       carry guidance text + prefill in the section body.

    Returns None when no `<<MUST item:X>>` / `<<SHOULD item:X>>` markers
    are present so the caller falls through to the LLM extraction path.
    """
    body = (doc.markdown or "") or (doc.full_text or "")
    if not body:
        return None

    # Cheap detection — bail out early if no markers anywhere
    must_markers   = _TEMPLATED_MUST_RE.findall(body)
    should_markers = _TEMPLATED_SHOULD_RE.findall(body)
    if not must_markers and not should_markers:
        return None

    # Mode A: hybrid edit-zone extraction. Templates can carry BOTH:
    #   - Table zones (`<!-- EDIT-ZONE-START leaf:req:X -->`) wrapping a
    #     markdown table — per-row MUSTs become columns; column→MUST
    #     mapping in a sibling TABLE-COLUMNS metadata block. Used for
    #     register/record/matrix/log/inventory shapes.
    #   - Per-MUST zones (`<!-- EDIT-ZONE-START item:X -->`) wrapping
    #     narrative content. Used for policy/procedure/scope_note
    #     shapes, AND for doc-level MUSTs in hybrid templates (e.g.
    #     SoA owner+version are narrative, the 93-row body is tabular).
    # Both processed in one pass so hybrid v2 anchors work.
    table_zones = list(_TEMPLATED_TABLE_ZONE_RE.finditer(body))
    edit_zones  = list(_TEMPLATED_EDIT_ZONE_RE.finditer(body))

    if table_zones or edit_zones:
        findings: list[DocumentFinding] = []
        if table_zones:
            findings.extend(_extract_templated_via_table(doc, body, table_zones))
        if edit_zones:
            findings.extend(_extract_templated_via_edit_zones(doc, edit_zones))
        return findings

    # Mode B: legacy full-section scan
    return _extract_templated_via_full_section(doc, body)


def _extract_templated_via_table(
    doc: ParsedDocument,
    body: str,
    table_zones: list,
) -> list[DocumentFinding]:
    """Tabular extraction. For each table zone, parse the markdown
    table inside and bind per-column MUST satisfaction.

    Mapping: a sibling `<!-- TABLE-COLUMNS leaf:<leaf_id> -->...<!-- /TABLE-COLUMNS -->`
    block carries an ordered list of `<!-- column: <item_id> -->`
    entries. Column index in the table aligns 1:1 with the metadata
    order — first column → first metadata entry, etc.

    For each column with at least one non-empty data cell (after the
    header + separator rows), bind the corresponding MUST as
    status='present'. Columns with all-empty cells stay unbound — the
    MUST surfaces as "missing" via the engine's leaf evaluator.
    """
    # Build leaf_id → column item_ids map from all metadata blocks
    leaf_columns: dict[str, list[str]] = {}
    for tc in _TEMPLATED_TABLE_COLUMNS_RE.finditer(body):
        leaf_id = tc.group(1)
        cols    = _TEMPLATED_TABLE_COLUMN_RE.findall(tc.group(2))
        if cols:
            leaf_columns[leaf_id] = cols

    findings: list[DocumentFinding] = []
    n_zones_bound = 0
    n_zones_empty = 0

    n_rows_captured = 0
    for m in table_zones:
        leaf_id   = m.group(1)
        zone_text = m.group(2)
        columns   = leaf_columns.get(leaf_id)
        if not columns:
            # No metadata for this leaf zone — skip rather than misbind
            continue

        # Parse rows. Two outputs:
        #   - col_has_data + sample_cell: per-column satisfaction +
        #     first-non-empty sample (legacy engine semantics).
        #   - tabular_rows: per-row capture into doc.tabular_rows (the
        #     full register content, persisted to
        #     tabular_evidence_rows so the renderer can replay all
        #     rows on round-trip and future advisory can surface
        #     per-row completeness).
        col_has_data = [False] * len(columns)
        sample_cell  = [""] * len(columns)
        rows_seen    = 0
        data_row_ix  = 0
        for raw_line in zone_text.splitlines():
            line = raw_line.strip()
            if not line.startswith("|"):
                continue
            # Skip separator row (---|---|...)
            if re.fullmatch(r"\|[\s\-:|]+\|", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if rows_seen == 0:
                # First non-separator row = header. Don't count as data.
                rows_seen = 1
                continue
            rows_seen += 1

            # Per-row capture — sparse JSONB map {item_id: cell_text}.
            # Skip the row entirely if every cell is empty (filler row).
            row_payload: dict[str, str] = {}
            for i in range(min(len(cells), len(columns))):
                if cells[i]:
                    row_payload[columns[i]] = cells[i][:1000]
            if row_payload:
                doc.tabular_rows.append({
                    "leaf_id":       leaf_id,
                    "row_index":     data_row_ix,
                    "column_values": row_payload,
                })
                data_row_ix    += 1
                n_rows_captured += 1

            # Legacy per-column satisfaction
            for i in range(min(len(cells), len(columns))):
                if cells[i] and not col_has_data[i]:
                    col_has_data[i] = True
                    sample_cell[i]  = cells[i]

        bound_in_zone = 0
        for i, item_id in enumerate(columns):
            if not col_has_data[i]:
                continue
            parts = item_id.split(":")
            if len(parts) < 3:
                continue
            control_ref = parts[1]
            standard_id = _control_ref_to_standard(control_ref)
            findings.append(DocumentFinding(
                upload_id         = doc.upload_id or "",
                tenant_id         = "",
                document_name     = doc.original_name,
                control_ref       = control_ref,
                standard_id       = standard_id,
                finding           = "Comply",
                evidence_text     = sample_cell[i][:500],
                confidence        = "high",
                checklist_item_id = item_id,
                extraction_path   = "templated",
                inference_source  = "templated",
            ))
            bound_in_zone += 1

        if bound_in_zone:
            n_zones_bound += 1
        else:
            n_zones_empty += 1

    doc.extraction_metrics["templated_table_zones_total"] = len(table_zones)
    doc.extraction_metrics["templated_table_zones_bound"] = n_zones_bound
    doc.extraction_metrics["templated_table_zones_empty"] = n_zones_empty
    doc.extraction_metrics["templated_tabular_rows_captured"] = n_rows_captured
    return findings


def _extract_templated_via_edit_zones(
    doc: ParsedDocument,
    edit_zones: list,
) -> list[DocumentFinding]:
    """Edit-zone-driven extraction. One finding per zone that contains
    tenant authorship. Zones with only scaffolding (placeholder, pure
    prefill) are skipped — those contribute no new evidence."""
    findings: list[DocumentFinding] = []
    n_skipped_scaffolding = 0
    for m in edit_zones:
        item_id    = m.group(1)
        zone_text  = m.group(2)

        if _is_pure_scaffolding(zone_text):
            n_skipped_scaffolding += 1
            continue

        # item:A.5.15:physical_rules → control_ref='A.5.15'
        parts = item_id.split(":")
        if len(parts) < 3:
            continue
        control_ref = parts[1]
        standard_id = _control_ref_to_standard(control_ref)

        evidence = zone_text.strip()[:500]
        findings.append(DocumentFinding(
            upload_id         = doc.upload_id or "",
            tenant_id         = "",
            document_name     = doc.original_name,
            control_ref       = control_ref,
            standard_id       = standard_id,
            finding           = "Comply",
            evidence_text     = evidence,
            confidence        = "high",
            checklist_item_id = item_id,
            extraction_path   = "templated",
            inference_source  = "templated",
        ))

    doc.extraction_metrics["templated_edit_zones_total"]  = len(edit_zones)
    doc.extraction_metrics["templated_edit_zones_bound"]  = len(findings)
    doc.extraction_metrics["templated_zones_scaffolding"] = n_skipped_scaffolding
    return findings


def _extract_templated_via_full_section(
    doc: ParsedDocument,
    body: str,
) -> list[DocumentFinding]:
    """Legacy mode — full-section scan. Used when no edit-zone markers
    are found (older renders or direct uploads). Less precise: treats
    any substantive section content as tenant evidence, including v2
    guidance prose. Kept for backward compatibility.
    """
    anchors: list[tuple[int, str, str, int]] = []  # (start, kind, item_id, end)
    for m in _TEMPLATED_MUST_RE.finditer(body):
        anchors.append((m.start(), "MUST", m.group(1), m.end()))
    for m in _TEMPLATED_SHOULD_RE.finditer(body):
        anchors.append((m.start(), "SHOULD", m.group(1), m.end()))
    anchors.sort(key=lambda a: a[0])

    findings: list[DocumentFinding] = []
    for i, (start, kind, item_id, mark_end) in enumerate(anchors):
        slice_end = anchors[i + 1][0] if i + 1 < len(anchors) else len(body)
        section_body = body[mark_end:slice_end]
        boundary = re.search(r"^(?:#{2,}\s|---\s*$)", section_body, re.MULTILINE)
        if boundary:
            section_body = section_body[:boundary.start()]
        cleaned = _TEMPLATED_WHY_LINE.sub("", section_body)
        had_placeholder = bool(_TEMPLATED_TEXT_PLACEHOLDER.search(cleaned))
        cleaned_no_ph   = _TEMPLATED_TEXT_PLACEHOLDER.sub("", cleaned).strip()
        cleaned_no_ph   = re.sub(r"^[-=]{3,}\s*$", "", cleaned_no_ph,
                                  flags=re.MULTILINE).strip()
        if not cleaned_no_ph:
            finding  = "NC"
            evidence = "(template section left blank by tenant)" if had_placeholder \
                       else "(template section empty)"
        else:
            finding  = "Comply"
            evidence = cleaned_no_ph[:500]

        parts = item_id.split(":")
        if len(parts) < 3:
            continue
        control_ref = parts[1]
        standard_id = _control_ref_to_standard(control_ref)

        findings.append(DocumentFinding(
            upload_id         = doc.upload_id or "",
            tenant_id         = "",
            document_name     = doc.original_name,
            control_ref       = control_ref,
            standard_id       = standard_id,
            finding           = finding,
            evidence_text     = evidence,
            confidence        = "high",
            checklist_item_id = item_id,
            extraction_path   = "templated",
            inference_source  = "templated",
        ))

    return findings


# =============================================================================
# STRUCTURED PATH — XLSX/CSV workbooks
# =============================================================================

def _extract_structured(doc: ParsedDocument) -> list[DocumentFinding]:
    """
    Parse structured rows directly from XLSX/CSV — no LLM needed.
    Each row already has control_ref + finding + gap_description.
    """
    findings = []
    for section in doc.raw_sections:
        rows = section.metadata.get("rows", [])
        for row in rows:
            raw_ref = row.get("control_ref", "").strip()
            finding = row.get("finding", "not_addressed")

            if not raw_ref or finding == "not_addressed":
                continue

            # Normalize ref for each known standard
            # Try each standard until one normalizes successfully
            normalized = None
            standard   = None
            for std in (doc.standard_ids or ["ISO27001:2022"]):
                n = normalize_ref(raw_ref, std)
                if n:
                    normalized = n
                    standard   = std
                    break

            if not normalized:
                logger.debug(f"Could not normalize ref: {raw_ref}")
                continue

            findings.append(DocumentFinding(
                upload_id      = doc.upload_id or "",
                tenant_id      = "",   # set by writer
                document_name  = doc.original_name,
                control_ref    = normalized,
                standard_id    = standard or "ISO27001:2022",
                finding        = finding,
                evidence_text  = row.get("gap_description") or row.get("evidence_text", ""),
                confidence     = "high",   # structured data = high confidence
                section        = section.heading,
                extraction_path = "structured",
            ))

    logger.info(f"Structured extraction: {len(findings)} findings from {doc.original_name}")
    return findings


# =============================================================================
# FULL DOCUMENT PATH
# =============================================================================

def _extract_full(
    doc:        ParsedDocument,
    controls:   list[dict],
    api_key:    str,
    leaf_musts: Optional[dict] = None,
) -> list[DocumentFinding]:
    """Single LLM call for the entire document."""

    chunks = _chunk_controls(controls, MAX_CONTROLS_PER_CALL)
    all_findings = []

    # Prefer structured markdown when the reader produced it (currently docx
    # via mammoth). It preserves tables/headings/lists that doc.full_text —
    # built from a paragraph join — silently drops.
    doc_text = doc.markdown if doc.markdown else doc.full_text

    for chunk_controls in chunks:
        text = _build_doc_context(doc) + "\n\n" + doc_text

        raw = _llm_extract(
            text       = text,
            controls   = chunk_controls,
            doc_name   = doc.original_name,
            api_key    = api_key,
            chunk_hint = "full document",
            leaf_musts = leaf_musts,
        )
        doc.extraction_metrics["llm_calls"] = doc.extraction_metrics.get("llm_calls", 0) + 1
        findings = _parse_llm_response(
            raw, doc, chunk_controls,
            section=None, chunk_id="full",
            leaf_musts=leaf_musts,
        )
        all_findings.extend(findings)

    # Pass-2: targeted recall on partial leaves. See
    # [[per-must-recall-strategy]] — single-pass LLM extraction has a
    # structural ceiling on metadata + cross-section MUSTs (dates,
    # version refs, reviewer rows, revision-history bullets). When a
    # leaf has 1+ but <N MUSTs bound, the doc clearly evidences the
    # control area and likely contains the missed metadata too. A
    # focused pass-2 call with unfilled MUSTs as the candidate list
    # surfaces these.
    all_findings = _run_pass2(doc, leaf_musts, all_findings, api_key, controls)

    logger.info(f"Full extraction: {len(all_findings)} findings from {doc.original_name}")
    return all_findings


# =============================================================================
# SECTION-BASED PATH
# =============================================================================

def _extract_sections(
    doc:        ParsedDocument,
    controls:   list[dict],
    api_key:    str,
    leaf_musts: Optional[dict] = None,
) -> list[DocumentFinding]:
    """
    One LLM call per section.
    Sections are merged if too small (< 200 tokens).
    """
    doc_context = _build_doc_context(doc)
    all_findings: dict[str, DocumentFinding] = {}  # control_ref → best finding

    # Merge small sections
    sections = _merge_small_sections(doc.raw_sections, min_tokens=200)

    for section in sections:
        if not section.text.strip():
            continue

        # Scope controls to this section using heading keywords + explicit
        # refs. When the section gives no signal, fall back to the doc-level
        # scope — `controls` here is already pre-filtered by doc_mappings,
        # so it's the tight target set, not the universe. Skipping the
        # section entirely (the prior behaviour) discards real evidence in
        # meta-policy docs where most section headings don't match the
        # small keyword list (e.g. "Purpose", "Scope", "Roles", "Review").
        section_controls = _scope_controls_to_section(controls, section, doc)
        if not section_controls:
            section_controls = controls

        chunk_id = section.section_id
        text     = doc_context + f"\n\nSection: {section.heading or 'Untitled'}\n\n" + section.text

        chunks = _chunk_controls(section_controls, MAX_CONTROLS_PER_CALL)
        for control_chunk in chunks:
            raw = _llm_extract(
                text       = text,
                controls   = control_chunk,
                doc_name   = doc.original_name,
                api_key    = api_key,
                chunk_hint = section.heading or chunk_id,
                leaf_musts = leaf_musts,
            )
            doc.extraction_metrics["llm_calls"] = doc.extraction_metrics.get("llm_calls", 0) + 1
            findings = _parse_llm_response(
                raw, doc, control_chunk,
                section    = section.heading,
                chunk_id   = chunk_id,
                page       = section.page_start,
                leaf_musts = leaf_musts,
            )

            # Merge: Comply > OFI > NC > not_addressed
            # Dedup key is (control_ref, checklist_item_id) — distinct MUST
            # bindings on the same control are SEPARATE findings (the engine
            # needs each to mark its respective MUST satisfied). When the
            # binding is None, we fall back to control_ref dedup as before
            # so unbound findings still collapse to one row per control.
            _PRIORITY = {"Comply": 3, "OFI": 2, "NC": 1, "not_addressed": 0}
            for f in findings:
                key = (f.control_ref, f.checklist_item_id) if f.checklist_item_id \
                      else (f.control_ref, None)
                existing = all_findings.get(key)
                if existing is None:
                    all_findings[key] = f
                elif _PRIORITY.get(f.finding, 0) > _PRIORITY.get(existing.finding, 0):
                    all_findings[key] = f

    result = list(all_findings.values())
    # Pass-2: targeted recall on partial leaves. Runs doc-scoped (not
    # section-scoped) because cross-section linking is the whole point.
    result = _run_pass2(doc, leaf_musts, result, api_key, controls)
    logger.info(f"Section extraction: {len(result)} findings from {doc.original_name}")
    return result


# =============================================================================
# LLM CALL
# =============================================================================

_SYSTEM_PROMPT = """You are a compliance analyst reviewing a document to assess ISO 27001 / GDPR compliance.

Your task: for each control provided, determine whether this document provides DIRECT, SUBSTANTIVE evidence of compliance.

The bar is HIGH. Bind a control ONLY when:
  (a) the document has substantive content about THIS CONTROL'S SPECIFIC SUBJECT
      (e.g. bind A.5.23 cloud-services ONLY if the doc actually defines
      cloud-service security obligations — NOT if it merely mentions
      cloud as one of several deployment options), AND
  (b) you can quote ≥40 characters of verbatim text from the document that
      directly supports the binding (no paraphrase, no summary).

When in doubt — OMIT. False-positive bindings (binding a control the doc
doesn't really cover) are worse than missing bindings. The tenant can
always re-extract; they cannot easily unrecognise spurious evidence.

Rules:
- Only assess controls clearly and substantively addressed in the text
- Do NOT bind on incidental mentions, topic adjacency, or assumed coverage
- Do NOT bind because the doc's TITLE looks adjacent ("Supplier Policy"
  alone does not bind cloud-services A.5.23 — the body must discuss
  cloud-service security specifically)
- Use "not_addressed" (omit from response) when the document doesn't
  substantively cover the control
- "Comply" = document demonstrates the control is implemented
- "OFI" = document shows partial or planned implementation
- "NC" = document explicitly states the control is not implemented or missing
- Quote must be a real, verbatim substring of the document. Hallucinated
  quotes are auto-rejected.
- When a per-MUST checklist is provided, emit ONE finding PER MUST item
  that the document evidences — do not collapse multiple distinct MUST
  items into a single finding. Sign-off blocks, revision history rows,
  and dated artefacts contain multiple separate MUSTs in close
  proximity; bind each independently:
    * "Approved | Joseph Kamula | ISMS Owner | 11 Apr 2025"
      → bind signatory → approval_signatory  (quote includes name + role)
      → bind date      → approval_date       (quote includes the date)
      → bind version   → approval_target     (quote includes "v1.1" or similar)
    * Revision-history bullets like "added SLA-met flag" each map to
      their respective MUSTs (sla_targets / completeness / orphan-access etc.)
    * Reviewer-row entries map to review_reviewer + review_date + review_outcome
  Dates and version references that look like metadata ARE first-class
  evidence when a MUST asks for them.
- Do not cap your output. Emit every applicable MUST binding the
  document evidences — recall over precision when the per-MUST list
  is provided and the evidence quote is verbatim.

Respond with JSON only — no markdown, no explanation."""

_USER_TEMPLATE = """{doc_context}

Document text:
\"\"\"
{text}
\"\"\"

Assess the following controls:
{control_list}

Respond with a JSON array:
[
  {{
    "control_ref": "A.5.18",
    "checklist_item_id": "item:A.5.18:review_record",
    "finding": "Comply",
    "evidence": "one sentence from the document that supports this finding",
    "confidence": "high"
  }},
  ...
]

The "checklist_item_id" field is optional — include it ONLY when the
"Available checklist items per control" block was provided in this prompt
AND the evidence quote clearly matches one specific MUST item. Use the
id verbatim. Omit the field entirely otherwise.

Only include controls that are addressed in this document.
For controls not addressed, omit them from the response entirely."""


# Catalog crosscheck — lazy-loaded per-process. Maps must_id → list of
# keyword_sets pulled from db/must_fingerprints/*.yaml. Reuses the same
# fingerprints leaf-scan uses; this turns the catalog set into a
# dual-purpose asset (back-bind regex matcher + extractor 2nd opinion).
# When the LLM emits a checklist_item_id, we run the evidence quote
# against the catalog's fingerprints for that MUST. Three outcomes:
#   - catalog absent → no crosscheck (counted)
#   - catalog present + match → confirmed (counted)
#   - catalog present + no match → disagreement (counted, binding kept)
# Disagreement is a SOFT signal: autogen catalogs are noisy enough that
# silent drops would lose real bindings. Surface in trace_log + dashboard.
_MUST_FINGERPRINTS_CACHE: Optional[dict] = None


def _load_must_fingerprints() -> dict:
    global _MUST_FINGERPRINTS_CACHE
    if _MUST_FINGERPRINTS_CACHE is not None:
        return _MUST_FINGERPRINTS_CACHE
    try:
        from .leaf_driven_scan import load_catalogs
        cats = load_catalogs()
        out: dict[str, list[list[str]]] = {}
        for cat in cats:
            for fp in cat.fingerprints:
                # Multiple catalogs could declare the same must_id — merge
                # keyword sets defensively.
                out.setdefault(fp.must_id, []).extend(fp.excerpt_keywords)
        _MUST_FINGERPRINTS_CACHE = out
        return out
    except Exception as e:
        logger.warning(f"crosscheck: failed to load catalogs: {e}")
        _MUST_FINGERPRINTS_CACHE = {}
        return {}


def _crosscheck_must_binding(must_id: str, evidence: str) -> str:
    """Return one of: 'unavailable' (no catalog), 'confirmed' (excerpt
    matches catalog fingerprints), 'disagreement' (catalog has
    fingerprints but excerpt matches none).
    """
    cats = _load_must_fingerprints()
    keyword_sets = cats.get(must_id)
    if not keyword_sets:
        return "unavailable"
    try:
        from .leaf_driven_scan import _excerpt_matches
        return "confirmed" if _excerpt_matches(evidence, keyword_sets) else "disagreement"
    except Exception:
        return "unavailable"


# Neo4j MUST-fetcher — env-driven; cached per-process so repeated calls
# inside one extract() invocation share a driver. Returns
#   {leaf_id: [(item_id, item_text), ...], ...}
# When Neo4j is unavailable or any leaf has zero MUSTs in the graph, the
# caller treats that leaf as having no per-MUST binding hints — LLM still
# runs but findings stay unbound (graceful degradation, no exception).
_NEO_DRIVER_CACHE = {}


def _fetch_leaf_musts(leaf_ids: list[str]) -> dict[str, list[tuple[str, str]]]:
    if not leaf_ids:
        return {}
    try:
        from neo4j import GraphDatabase
        import os
        uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER",     "neo4j")
        pw   = os.getenv("NEO4J_PASSWORD", "")
        key  = (uri, user)
        drv  = _NEO_DRIVER_CACHE.get(key)
        if drv is None:
            drv = GraphDatabase.driver(uri, auth=(user, pw))
            _NEO_DRIVER_CACHE[key] = drv
        with drv.session() as s:
            res = s.run(
                """
                MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(item:ChecklistItem)
                WHERE er.id IN $leaf_ids
                RETURN er.id AS leaf_id, item.id AS item_id, item.text AS item_text
                ORDER BY er.id, item.id
                """,
                leaf_ids=leaf_ids,
            )
            out: dict[str, list[tuple[str, str]]] = {}
            for row in res:
                out.setdefault(row["leaf_id"], []).append(
                    (row["item_id"], row["item_text"] or row["item_id"])
                )
            return out
    except Exception as e:
        logger.warning(f"Neo4j unavailable for MUST fetch: {e}")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# PASS 2 — targeted recall on partial leaves
# Per [[per-must-recall-strategy]] (2026-06-23 strategy doc): single-pass
# LLM extraction has a structural ceiling on metadata + cross-section
# MUSTs. Pass 2 runs after pass-1 collects findings; for any leaf with
# 1+ but <N MUSTs bound, it issues a focused LLM call listing only the
# unfilled MUSTs and asking the LLM to ground each in verbatim text.
#
# Cost: ~one LLM call per partial leaf. Bounded by doc_mappings scope
# (typically ≤5 controls × ≤4 leaves = ≤20 partial leaves worst case).
# Typical: 1-3 partial leaves per doc → +1-3 LLM calls, ~$0.05-0.10.
# ─────────────────────────────────────────────────────────────────────────────

def _find_partial_leaves(
    leaf_musts:     Optional[dict],
    pass1_findings: list,
) -> list[tuple[str, list[tuple[str, str]]]]:
    """Return [(leaf_id, unfilled_musts), ...] for leaves where pass-1
    bound some MUSTs but not all. Leaves with zero pass-1 bindings are
    NOT included — they're either truly empty in the doc or fully outside
    its scope; pass-2 has no signal that the doc covers them.
    """
    if not leaf_musts:
        return []
    covered: set[str] = set()
    for f in pass1_findings or []:
        cid = getattr(f, "checklist_item_id", None)
        if cid:
            covered.add(cid)
    out = []
    for leaf_id, items in (leaf_musts or {}).items():
        if not items:
            continue
        n_total = len(items)
        unfilled = [(iid, itext) for (iid, itext) in items if iid not in covered]
        n_filled = n_total - len(unfilled)
        if 0 < n_filled < n_total:
            out.append((leaf_id, unfilled))
    return out


_PASS2_SYSTEM_PROMPT = """You are a compliance analyst doing a SECOND PASS on a document.
The first pass extracted some MUST bindings but may have missed
metadata-shaped items (dates, version numbers, signatory rows,
revision-history bullets, cross-section references).

Re-read the document with fresh attention to ONLY the specific MUSTs
listed in the user message. For each MUST you can ground in verbatim
text from the document, emit one finding. Omit any MUST you cannot
ground — do not guess, do not infer.

Rules:
- "evidence" MUST be a verbatim substring of the document (≥40 chars)
- "checklist_item_id" MUST be one of the IDs from the listed MUSTs
- Treat the same evidence quote as bindable to multiple MUSTs ONLY when
  the quote literally contains content satisfying each
- A sign-off row like "Approved | Joseph Kamula | ISMS Owner | 22 June 2026"
  contains THREE MUSTs (signatory + role + date) — emit each separately
- A revision-history entry like "v1.1, 15 Jun 2026, Zorko Petrusa: added X"
  contains the version (approval_target), date (review_date or approval_date),
  reviewer (review_reviewer), and outcome (review_outcome) — emit each

Respond with JSON only — no markdown, no commentary."""


def _llm_extract_pass2(
    text:           str,
    leaf_id:        str,
    evidence_type:  str,
    unfilled_musts: list[tuple[str, str]],
    doc_name:       str,
    api_key:        str,
) -> str:
    """Pass-2 focused LLM call. Returns raw JSON string."""
    must_list = "\n".join(
        f'  - "{iid}": {itext}' for iid, itext in unfilled_musts
    )

    # Parse control_ref out of leaf_id: "req:A.5.15:management_approval" → "A.5.15"
    parts = leaf_id.split(":")
    ctrl_ref = parts[1] if len(parts) >= 2 else ""

    user_prompt = f"""Document: {doc_name}

Pass-2 target: leaf "{leaf_id}" (evidence type: {evidence_type}, control {ctrl_ref})

The first pass bound some MUSTs on this leaf. These specific MUSTs are
still UNFILLED — examine the document carefully for content that
evidences each:

{must_list}

Document text:
\"\"\"
{text[:80000]}
\"\"\"

Respond with a JSON array. For each MUST above that you can ground in
verbatim text, emit one finding:

[
  {{
    "control_ref": "{ctrl_ref}",
    "checklist_item_id": "<one id from the list above, verbatim>",
    "finding": "Comply",
    "evidence": "verbatim quote of >=40 characters",
    "confidence": "high"
  }},
  ...
]

Omit any MUST you cannot ground. Do not invent quotes. Do not guess."""

    body = json.dumps({
        "model":      EXTRACT_MODEL,
        "max_tokens": 4000,
        "system":     _PASS2_SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": user_prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data    = body,
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()[:500]
        except Exception:
            err_body = "<no body>"
        logger.error(
            f"Pass-2 LLM call failed for {doc_name} [{leaf_id}]: "
            f"HTTP {e.code}: {err_body}"
        )
        return "[]"
    except Exception as e:
        logger.error(f"Pass-2 LLM call failed for {doc_name} [{leaf_id}]: {e}")
        return "[]"


def _run_pass2(
    doc,
    leaf_musts:     Optional[dict],
    pass1_findings: list,
    api_key:        str,
    controls:       list[dict],
) -> list:
    """Run pass-2 targeted extraction. Returns the merged finding list
    (pass-1 + pass-2 with parse-time dedup by (control_ref, checklist_item_id)).
    """
    if not leaf_musts:
        return pass1_findings
    partial = _find_partial_leaves(leaf_musts, pass1_findings)
    if not partial:
        doc.extraction_metrics["pass2_leaves_targeted"] = 0
        doc.extraction_metrics["pass2_findings"] = 0
        return pass1_findings

    logger.info(
        f"Pass-2: {len(partial)} partial leaves to re-examine "
        f"({sum(len(unf) for _, unf in partial)} unfilled MUSTs total)"
    )

    # Build the doc text once (markdown if available, else full_text)
    doc_text = doc.markdown if doc.markdown else (doc.full_text or "")
    text_with_ctx = _build_doc_context(doc) + "\n\n" + doc_text

    # leaf_id → evidence_type lookup. Pass-2 prompts include the evidence
    # type so the LLM knows whether to look for a register-row vs a
    # policy statement vs a review record etc.
    leaf_evidence_type: dict[str, str] = {}
    try:
        for cat_id, items in (doc.extraction_metrics.get("target_leaves") or []):
            pass  # not iterable in this shape; leave empty
    except Exception:
        pass
    # Read evidence_type from target_leaves metric set by
    # _scope_controls_via_doc_mappings (list of dicts).
    for tl in (doc.extraction_metrics.get("target_leaves") or []):
        if isinstance(tl, dict) and tl.get("leaf_id"):
            leaf_evidence_type[tl["leaf_id"]] = tl.get("role") or tl.get("evidence_type") or "evidence"

    pass2_findings: list = []
    pass2_llm_calls = 0
    for leaf_id, unfilled in partial:
        evidence_type = leaf_evidence_type.get(leaf_id, "evidence")
        raw = _llm_extract_pass2(
            text           = text_with_ctx,
            leaf_id        = leaf_id,
            evidence_type  = evidence_type,
            unfilled_musts = unfilled,
            doc_name       = doc.original_name,
            api_key        = api_key,
        )
        pass2_llm_calls += 1
        # Reuse the standard parse pipeline so filters (grounding, crosscheck,
        # questionnaire, referential demotion, validation) apply uniformly.
        parsed = _parse_llm_response(
            raw, doc, controls,
            section=None,
            chunk_id=f"pass2:{leaf_id}",
            leaf_musts=leaf_musts,
        )
        pass2_findings.extend(parsed)

    # Dedup by (control_ref, checklist_item_id): pass-2 may re-emit a MUST
    # pass-1 also caught (LLM stochasticity). Keep the higher-confidence one.
    merged: dict[tuple, "DocumentFinding"] = {}
    for f in pass1_findings + pass2_findings:
        key = (f.control_ref, f.checklist_item_id or f"_unbound_{id(f)}")
        existing = merged.get(key)
        if existing is None:
            merged[key] = f
        else:
            # Higher confidence wins; tie-break on chunk_id (pass-1 first)
            conf_rank = {"high": 0, "medium": 1, "low": 2}
            if conf_rank.get(f.confidence, 3) < conf_rank.get(existing.confidence, 3):
                merged[key] = f

    final = list(merged.values())

    doc.extraction_metrics["pass2_leaves_targeted"] = len(partial)
    doc.extraction_metrics["pass2_findings"] = len(pass2_findings)
    doc.extraction_metrics["llm_calls"] = doc.extraction_metrics.get("llm_calls", 0) + pass2_llm_calls
    logger.info(
        f"Pass-2: +{len(pass2_findings)} findings across {len(partial)} "
        f"leaves ({pass2_llm_calls} LLM calls); final dedup retained {len(final)} "
        f"(pass-1 was {len(pass1_findings)})"
    )
    return final


def _llm_extract(
    text:       str,
    controls:   list[dict],
    doc_name:   str,
    api_key:    str,
    chunk_hint: str = "",
    leaf_musts: Optional[dict] = None,
) -> str:
    """Make one LLM extraction call. Returns raw JSON string."""

    control_list = "\n".join(
        f"- {c['ref']}: {c.get('title', c['ref'])}"
        for c in controls
    )

    # When leaf_musts is supplied (doc_mappings narrowed to specific leaves),
    # render a per-control MUST-items section. The LLM is asked to tag each
    # finding with the checklist_item_id that best matches the evidence
    # quote — enabling per-MUST binding without the leaf-scan back-step.
    must_section = ""
    if leaf_musts:
        # Group by control_ref (the LLM doesn't need leaf_id context — every
        # checklist_item_id is unique and resolves to its leaf downstream).
        ctrl_to_items: dict[str, list[tuple[str, str]]] = {}
        for leaf_id, items in leaf_musts.items():
            # leaf_id format: "req:A.5.18:access_rights_procedure" → control "A.5.18"
            parts = leaf_id.split(":")
            if len(parts) >= 2:
                ctrl = parts[1]
                ctrl_to_items.setdefault(ctrl, []).extend(items)
        if ctrl_to_items:
            blocks = []
            for ctrl in sorted(ctrl_to_items.keys()):
                items = ctrl_to_items[ctrl]
                if not items:
                    continue
                lines = "\n".join(f"  * {iid} — {itext}" for iid, itext in items)
                blocks.append(f"{ctrl}:\n{lines}")
            must_section = (
                "\n\nFor each finding, also tag the single checklist_item_id "
                "whose text best matches your evidence quote. Use the id "
                "EXACTLY as listed; omit the field if none clearly applies.\n\n"
                "Available checklist items per control:\n"
                + "\n\n".join(blocks)
            )

    user_prompt = _USER_TEMPLATE.format(
        doc_context  = f"Document: {doc_name}" + (f" | Section: {chunk_hint}" if chunk_hint else ""),
        text         = text[:80000],   # safety cap — should be within context window
        control_list = control_list,
    ) + must_section

    body = json.dumps({
        "model":      EXTRACT_MODEL,
        "max_tokens": 4000,
        "system":     _SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": user_prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data    = body,
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        return data["content"][0]["text"]
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode()[:500]
        except Exception:
            err_body = "<no body>"
        logger.error(
            f"LLM extraction failed for {doc_name} [{chunk_hint}]: "
            f"HTTP {e.code}: {err_body}"
        )
        return "[]"
    except Exception as e:
        logger.error(f"LLM extraction failed for {doc_name} [{chunk_hint}]: {e}")
        return "[]"


# =============================================================================
# RESPONSE PARSER
# =============================================================================

# Minimum evidence-quote length. Anything shorter (e.g. "the policy",
# "as defined", "controls in place") is too generic to ground a binding
# and is almost certainly the LLM grabbing whatever passing reference it
# could find. Calibrated against the v1 over-attribution incident on
# Arion's Supplier Vendor Security Policy / Access Control Policy /
# Business Continuity Policy (~30-42 controls each, most coarse-matches).
_MIN_EVIDENCE_LEN = 40

# Drop low-confidence findings at parse time. The LLM uses "low" when
# its own gut says the binding might not hold; we shouldn't write those
# to the engine where they count toward leaf satisfaction.
_DROP_CONFIDENCES = {"low"}


_GROUNDING_PUNCT_RE = re.compile(r"[^\w\s]")

# Detects ISO 27001 / GDPR control refs in evidence quotes — `5.31`,
# `A.5.31`, `Art.32`, etc. Used by the referential-mention demotion rule.
# No capture groups so findall returns full matches as strings.
_REFERENTIAL_REF_RE = re.compile(
    r"\b[Aa]\.\d+\.\d+(?:\.\d+)?\b|\b\d+\.\d+(?:\.\d+)?\b|\bArt\.\s*\d+(?:\.\d+)?\b"
)


# Questionnaire / checklist markers — when the LLM's "evidence" quote
# contains one of these, the document is a questionnaire/template (a
# list of questions to ASK), not a statement of compliance. The LLM is
# fooled because questions about a control textually match the control
# itself; without this filter every vendor assessment template
# generates dozens of false-positive Comply findings.
#
# Surfaced 2026-06-12 by a Vendor Security Assessment Report.docx
# upload that produced 22 ISO + 25 GDPR findings, almost all of them
# `"Does the vendor X? (Y/N) - Proof Point: ..."` style questions.
# Same shape as the [[extractor-referential-mention-demotion]] rule —
# a content-level filter for a specific failure mode.
_QUESTIONNAIRE_PATTERNS = [
    re.compile(r"\(\s*Y\s*/\s*N\s*\)",                          re.IGNORECASE),  # "(Y/N)"
    re.compile(r"\(\s*Yes\s*/\s*No\s*\)",                       re.IGNORECASE),  # "(Yes/No)"
    re.compile(r"\b(?:Proof|Evidence)\s+Point\s*:",             re.IGNORECASE),  # "Proof Point:"
    re.compile(                                                                  # interrogative + ? close
        r"\b(?:Does|Has|Have|Is|Are|Will|Would|Can|Should)\s+(?:the|your|a|an|you)\b[^?]{0,200}\?",
        re.IGNORECASE,
    ),
]


def _looks_like_questionnaire(quote: str) -> bool:
    """True when the evidence quote looks like a question/checklist
    item, not a statement of compliance. One marker hit is enough —
    the patterns are precise (no false-positive risk on statements).
    """
    if not quote:
        return False
    return any(p.search(quote) for p in _QUESTIONNAIRE_PATTERNS)


# TOC detection — doc-level analog of the questionnaire filter.
# A Table-of-Contents document lists what policies an org HAS; its body
# is dominated by lines like "2.1 Information Security Policy — Purpose:
# Defines the overarching security objectives…" These read like real
# compliance statements to the LLM but are descriptions OF other docs.
_TOC_FILENAME_TOKENS = ("toc", "table of contents", "index of")
_TOC_LINE_RE = re.compile(
    r"\b\d+\.\d+\s+[A-Z][\w &/-]{2,80}\s+[—\-–]\s+"
    r"(?:Purpose|Defines|Establishes|Provides|Describes|Outlines)\b",
)


def _looks_like_toc(doc: "ParsedDocument") -> str:
    """Detect a TOC / document-index upload. Returns a non-empty reason
    string when detected, else "".

    Two signals — either is sufficient:
      (1) Filename token: "TOC", "Table of Contents", "Index of"
      (2) Content density: ≥3 TOC-shape lines AND ≥30% of body lines
          match. The filename signal alone is enough for the common case;
          density catches TOCs that don't self-label.
    """
    name = (getattr(doc, "original_name", "") or "").lower()
    for tok in _TOC_FILENAME_TOKENS:
        if tok in name:
            return f"filename token '{tok}'"

    text = (getattr(doc, "full_text", "") or
            getattr(doc, "markdown", "") or "")
    text = text[:20_000]  # cap scan for cost
    if not text:
        return ""

    toc_hits = _TOC_LINE_RE.findall(text)
    if len(toc_hits) < 3:
        return ""
    nonblank = sum(1 for ln in text.splitlines() if ln.strip()) or 1
    density = len(toc_hits) / nonblank
    if density >= 0.30:
        return f"toc-shape density {len(toc_hits)}/{nonblank} ({density:.0%})"
    return ""


def _ground_normalize(s: str) -> str:
    """Normalise for grounding match: lowercase, strip punctuation,
    collapse whitespace. Punctuation handling is critical — the LLM
    routinely cites bullet lists with semicolons inserted between items,
    but the source text (paragraph walk OR mammoth markdown) renders
    those bullets with dashes / hyphens / commas / no separator at all.
    Word content + order is what makes a citation grounded; punctuation
    is noise that varies across renderings."""
    s = s.lower()
    s = _GROUNDING_PUNCT_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _evidence_grounded(evidence: str, doc: ParsedDocument) -> bool:
    """Verbatim-quote check. The LLM is instructed to provide a quote that
    actually appears in the document. Punctuation-stripped substring
    match catches hallucinated quotes (LLM paraphrases the doc but
    claims it's verbatim) while tolerating bullet-separator drift (LLM
    inserts ';' between bullets that source renders with '-' or
    newlines), markdown escapes (`\\(`, `\\-`), and case differences.

    We use only the first 50 chars of the evidence (post-normalisation)
    to be lenient on trailing punctuation/articles. Check against BOTH
    `doc.full_text` AND `doc.markdown` because the LLM is fed one or
    the other depending on extraction path, and they diverge for docs
    where mammoth captures list/table content the paragraph walker
    drops."""
    if not evidence or len(evidence) < _MIN_EVIDENCE_LEN:
        return False
    needle = _ground_normalize(evidence)[:50]
    if not needle:
        return False
    for source in (doc.full_text, doc.markdown):
        if not source:
            continue
        if needle in _ground_normalize(source):
            return True
    # Neither source has the quote. If both are missing entirely, the
    # extraction path isn't keeping text — be lenient (tenant can still
    # reject via Stage-1).
    if not doc.full_text and not doc.markdown:
        return True
    return False


def _parse_llm_response(
    raw:        str,
    doc:        ParsedDocument,
    controls:   list[dict],
    section:    Optional[str],
    chunk_id:   str,
    page:       Optional[int] = None,
    leaf_musts: Optional[dict] = None,
) -> list[DocumentFinding]:
    """Parse the LLM JSON response into DocumentFinding objects.

    Post-process tightenings (2026-06-07, fix for over-attribution
    incident — Supplier Vendor policy bound to 42 controls, Access
    Control policy to 29, etc.):
      - drop confidence='low'
      - require evidence quote ≥ _MIN_EVIDENCE_LEN chars
      - require quote to appear verbatim in the document text (catches
        hallucinated quotes)
    Cap at 15 retained findings per chunk (the LLM is also asked to
    self-cap in the prompt; this enforces it on the parse side)."""

    # Strip markdown fences
    raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
    if not raw or raw == "[]":
        return []

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        # Salvage: max_tokens truncation cuts the JSON mid-object. Trim
        # back to the last complete `}` followed by `,` (or none), close
        # the array, retry. Recovers the N-1 valid findings instead of
        # silently dropping the entire response.
        items = None
        try:
            last_complete = raw.rfind("},")
            if last_complete < 0:
                last_complete = raw.rfind("}")
            if last_complete > 0:
                salvaged = raw[: last_complete + 1].rstrip().rstrip(",") + "]"
                # Ensure leading [
                if not salvaged.lstrip().startswith("["):
                    salvaged = "[" + salvaged.lstrip()
                items = json.loads(salvaged)
                logger.warning(
                    f"JSON parse error recovered via salvage: {e} — "
                    f"kept {len(items) if isinstance(items, list) else 0} "
                    f"complete findings from truncated response"
                )
        except Exception:
            items = None
        if items is None:
            logger.warning(f"JSON parse error in LLM response: {e}\nRaw: {raw[:200]}")
            return []

    # Build control lookup for validation
    valid_refs = {c["ref"] for c in controls}

    # Build the per-control valid checklist_item_id set. When leaf_musts is
    # supplied (doc_mappings narrowed to specific leaves), we accept the
    # LLM's checklist_item_id ONLY when it appears in this control's MUSTs.
    # Otherwise the field is dropped (silently — the finding stays unbound
    # rather than carrying a hallucinated id).
    valid_items_by_ctrl: dict[str, set[str]] = {}
    if leaf_musts:
        for leaf_id, items_list in leaf_musts.items():
            parts = leaf_id.split(":")
            if len(parts) >= 2:
                ctrl = parts[1]
                bucket = valid_items_by_ctrl.setdefault(ctrl, set())
                for iid, _itext in items_list:
                    bucket.add(iid)

    dropped_low_conf      = 0
    dropped_short_quote   = 0
    dropped_hallucinated  = 0
    dropped_unknown_ref   = 0
    dropped_questionnaire = 0
    dropped_unbound       = 0
    # Catalog crosscheck (schema_v42) — counts only, no rejections. Surfaces
    # cases where the LLM picked a valid MUST id but the evidence quote
    # doesn't match the catalog's keyword fingerprints for that MUST.
    crosscheck_confirmed     = 0
    crosscheck_disagreements = 0
    crosscheck_unavailable   = 0
    findings = []
    for item in items:
        ref     = item.get("control_ref", "").strip()
        finding = item.get("finding", "not_addressed").strip()

        if not ref or finding == "not_addressed":
            continue

        # Direct match against the candidate list first. If the LLM echoed
        # back a ref from our input list, accept it as-is — that's the
        # canonical form. This avoids the normalize_iso27001 ambiguity
        # for 2-dot refs (ISMS clause 8.2 vs Annex A.8.2).
        standard_id = None
        if ref in valid_refs:
            standard_id = doc.standard_ids[0] if doc.standard_ids else "ISO27001:2022"
        else:
            # Try normalize as fallback (handles LLM rephrasing of A5.18 → A.5.18
            # or ISMS-clause-A. corruption that earlier outputs produced).
            for std in (doc.standard_ids or ["ISO27001:2022"]):
                normalized = normalize_ref(ref, std)
                if normalized and normalized in valid_refs:
                    ref = normalized
                    standard_id = std
                    break

        if standard_id is None:
            # LLM returned a ref that isn't in our candidate list. Drop — we
            # didn't ask about this control, so the binding is unverified.
            dropped_unknown_ref += 1
            continue

        if finding not in ("Comply", "OFI", "NC"):
            continue

        confidence = item.get("confidence", "medium")
        if confidence not in ("high", "medium", "low"):
            confidence = "medium"
        if confidence in _DROP_CONFIDENCES:
            dropped_low_conf += 1
            continue

        evidence = (item.get("evidence", "") or "").strip()[:500]
        if len(evidence) < _MIN_EVIDENCE_LEN:
            dropped_short_quote += 1
            continue
        if not _evidence_grounded(evidence, doc):
            dropped_hallucinated += 1
            continue
        # Questionnaire / checklist filter: when the LLM's quoted
        # evidence is a question or checklist item (Y/N, Proof Point,
        # interrogative + "?"), the document is a questionnaire/
        # template not a compliance statement. Drop — approving these
        # would falsely advance posture based on questions ABOUT
        # controls being mistaken for statements OF compliance.
        if _looks_like_questionnaire(evidence):
            dropped_questionnaire += 1
            logger.info(
                "questionnaire drop: %s — evidence quote is a "
                "question/checklist item, not a statement of "
                "compliance (chunk %s)",
                ref, chunk_id,
            )
            continue

        # Referential-mention demotion: if the evidence quote cites OTHER
        # control refs but NOT the bound one, the LLM is reading a register-
        # shape doc (compliance requirements list, control matrix, gap
        # analysis) and treating "doc mentions control X" as implementation
        # of X. That's not real evidence. Demote Comply → OFI so the finding
        # still surfaces for HITL review but doesn't claim "implemented".
        # Doesn't drop — registers ARE partial evidence of awareness.
        if finding == "Comply":
            other_refs_in_quote = _REFERENTIAL_REF_RE.findall(evidence)
            if other_refs_in_quote:
                bound_short = ref[2:] if ref.startswith("A.") else ref
                if (ref not in evidence) and (bound_short not in other_refs_in_quote):
                    finding = "OFI"
                    logger.info(
                        "referential-mention demotion: %s → OFI (quote cites %s, "
                        "not the bound ref) on chunk %s",
                        ref, sorted(set(other_refs_in_quote))[:3], chunk_id,
                    )

        # Per-MUST binding: accept the LLM's checklist_item_id only when
        # it's in the valid set for this control. Hallucinated ids are
        # silently dropped (finding stays unbound rather than carrying a
        # bad binding through to the engine).
        bound_item_id = None
        raw_item_id = (item.get("checklist_item_id") or "").strip()
        if raw_item_id and valid_items_by_ctrl:
            allowed = valid_items_by_ctrl.get(ref, set())
            if raw_item_id in allowed:
                bound_item_id = raw_item_id
                # Catalog crosscheck — soft signal. Tally without dropping.
                outcome = _crosscheck_must_binding(bound_item_id, evidence)
                if outcome == "confirmed":
                    crosscheck_confirmed += 1
                elif outcome == "disagreement":
                    crosscheck_disagreements += 1
                    logger.info(
                        "crosscheck disagreement: %s — catalog fingerprints "
                        "do not match evidence excerpt (chunk %s)",
                        bound_item_id, chunk_id,
                    )
                else:
                    crosscheck_unavailable += 1

        # Unbound-finding drop: post Phase-1 retirement (2026-06-13) the
        # engine ignores unbound rows (no checklist_item_id). They only
        # clutter Stage-1. Direction-C (per-MUST binding via doc_mappings)
        # is the canonical path; if it didn't bind, the right answer is
        # to add the missing doc_mapping, not to emit inert control-level
        # matches. Drop unconditionally — un-mapped docs that previously
        # produced "evidence of awareness" control-level findings will
        # now produce 0 findings, surfacing the doc_mapping gap clearly.
        if bound_item_id is None:
            dropped_unbound += 1
            continue

        findings.append(DocumentFinding(
            upload_id         = doc.upload_id or "",
            tenant_id         = "",   # set by writer
            document_name     = doc.original_name,
            control_ref       = ref,
            standard_id       = standard_id,
            finding           = finding,
            evidence_text     = evidence,
            confidence        = confidence,
            checklist_item_id = bound_item_id,
            section           = section,
            page_number       = page,
            extraction_path   = doc.extraction_path.value,
            chunk_id          = chunk_id,
        ))

    total_dropped = (dropped_low_conf + dropped_short_quote + dropped_hallucinated
                     + dropped_unknown_ref + dropped_questionnaire + dropped_unbound)
    if total_dropped:
        logger.info(
            "extractor filters dropped %d findings on chunk %s (doc=%s): "
            "low_conf=%d short_quote=%d hallucinated_quote=%d unknown_ref=%d "
            "questionnaire=%d unbound=%d",
            total_dropped, chunk_id, doc.original_name,
            dropped_low_conf, dropped_short_quote, dropped_hallucinated,
            dropped_unknown_ref, dropped_questionnaire, dropped_unbound,
        )

    # Accumulate drop counts onto the doc for pipeline-side persistence
    # (schema_v35 quality telemetry — see [[intake-quality-telemetry]]).
    m = doc.extraction_metrics
    m["dropped_low_conf"]      = m.get("dropped_low_conf", 0)      + dropped_low_conf
    m["dropped_short_quote"]   = m.get("dropped_short_quote", 0)   + dropped_short_quote
    m["dropped_hallucinated"]  = m.get("dropped_hallucinated", 0)  + dropped_hallucinated
    m["dropped_unknown_ref"]   = m.get("dropped_unknown_ref", 0)   + dropped_unknown_ref
    m["dropped_questionnaire"] = m.get("dropped_questionnaire", 0) + dropped_questionnaire
    m["dropped_unbound"]       = m.get("dropped_unbound", 0)       + dropped_unbound
    # schema_v42 — crosscheck telemetry
    m["crosscheck_confirmed"]     = m.get("crosscheck_confirmed", 0)     + crosscheck_confirmed
    m["crosscheck_disagreements"] = m.get("crosscheck_disagreements", 0) + crosscheck_disagreements
    m["crosscheck_unavailable"]   = m.get("crosscheck_unavailable", 0)   + crosscheck_unavailable

    # Per-chunk finding cap. Pre-2026-06-23 this was hard 15 — fine when
    # findings were 1-per-control. With per-MUST binding active (post B,
    # 2026-06-15) a single control can carry 5-15 MUSTs; 4 well-scoped
    # controls × ~7 MUSTs = ~28 candidates per chunk. Capping at 15
    # silently dropped legitimate MUST bindings (esp. metadata-shaped
    # ones like approval_date, approval_target, review_date — surfaced
    # 2026-06-23 when a re-uploaded policy still showed 0 leaves
    # satisfied despite the text containing the evidence).
    #
    # New cap: 60. Generous headroom for doc_mappings-scoped extractions
    # (typically ≤5 controls × ≤15 MUSTs each); still gated by
    # validation (grounded quote, valid ref, valid item_id) so noise
    # doesn't grow proportionally. Confidence-ordered retention kept.
    if len(findings) > 60:
        conf_rank = {"high": 0, "medium": 1, "low": 2}
        find_rank = {"Comply": 0, "OFI": 1, "NC": 2}
        findings.sort(key=lambda f: (conf_rank.get(f.confidence, 3), find_rank.get(f.finding, 3)))
        findings = findings[:60]

    return findings


# =============================================================================
# HELPERS
# =============================================================================

def _build_doc_context(doc: ParsedDocument) -> str:
    """Build the document-level context injected into every LLM call."""
    parts = [f"Document: {doc.original_name}"]
    if doc.doc_type:
        parts.append(f"Type: {doc.doc_type}")
    if doc.standard_ids:
        parts.append(f"Standards: {', '.join(doc.standard_ids)}")
    if doc.scope_statement:
        parts.append(f"Scope: {doc.scope_statement}")
    if doc.explicit_refs:
        parts.append(f"Controls explicitly cited: {', '.join(doc.explicit_refs[:10])}")
    return " | ".join(parts)


def _scope_controls_via_doc_mappings(
    controls: list[dict], doc: ParsedDocument,
) -> list[dict]:
    """Scope the control list via db/doc_mappings/*.yaml when one matches.

    Returns the matched mapping(s)' target_controls (deduped) intersected
    with the supplied `controls` list. Returns [] when no mapping matches
    above the discovery confidence_floor — caller falls back to the
    legacy DOC_TYPE_CLAUSE_MAP path.

    Side effect: stores the matched proposals' `target_leaves` on
    `doc.extraction_metrics["target_leaves"]` (deduped by leaf_id) so the
    extractor can fetch per-MUST checklist items and pass them to the LLM
    for per-MUST binding. Without this, findings land unbound and can't
    feed the engine post 2026-06-13 Phase-1 retirement.

    Logs the chosen mapping(s) at INFO so the next upload's scoping is
    visible in /tmp/api.log.
    """
    from .doc_discovery import discover_doc, union_target_controls

    proposals = discover_doc(
        filename     = doc.original_name or "",
        body_text    = doc.full_text or "",
        topic_tokens = doc.topic_tokens or None,
    )
    # Telemetry: how many doc_mappings YAMLs fingerprinted this upload?
    # 0 means we fell through to legacy _scope_controls. Tracked so the
    # admin endpoint can group unmatched filenames and surface missing
    # umbrellas (schema_v37 + /admin/intake/unmatched-patterns).
    doc.extraction_metrics["doc_mappings_match_count"] = len(proposals)
    if not proposals:
        return []

    target_ctrls = set(union_target_controls(proposals))
    if not target_ctrls:
        return []

    # Collect target_leaves across all matched proposals, deduped by leaf_id.
    leaves_by_id: dict[str, dict] = {}
    for p in proposals:
        for leaf in (p.target_leaves or []):
            lid = leaf.get("leaf_id")
            if lid and lid not in leaves_by_id:
                leaves_by_id[lid] = leaf
    doc.extraction_metrics["target_leaves"] = list(leaves_by_id.values())

    # Intersect with the caller-provided control list — the caller already
    # filtered to controls that exist in the curated set; we just narrow.
    scoped = [c for c in controls if c.get("ref") in target_ctrls]

    # Only claim a "primary candidate count" when doc_mappings actually
    # contributed scoped controls. If proposals exist but the intersection
    # with `controls` is empty (e.g. GDPR-only proposals against an ISO-
    # only curated list), the caller falls back to `_scope_controls` —
    # leave primary unset so the fallback's setdefault picks up.
    if scoped:
        top = max(proposals, key=lambda p: p.confidence)
        primary_ctrls = set(top.target_controls or [])
        primary_scoped = [c for c in controls if c.get("ref") in primary_ctrls]
        doc.extraction_metrics["primary_candidate_controls"] = len(primary_scoped)

    if proposals:
        mapping_summary = ", ".join(
            f"{p.mapping_id}({p.confidence})" for p in proposals
        )
        logger.info(
            "doc_mappings matched %s → %d controls (%s): %s",
            doc.original_name, len(scoped),
            ", ".join(sorted(target_ctrls))[:120],
            mapping_summary,
        )
    return scoped


def _scope_controls(controls: list[dict], doc: ParsedDocument) -> list[dict]:
    """
    Scope the control list to those relevant for this doc_type + standard.
    If explicit refs were found, prioritize those controls.
    """
    if not controls:
        return []

    # Get clause groups relevant for this doc type
    clause_groups = []
    for std in (doc.standard_ids or []):
        clause_groups.extend(get_clause_scope(doc.doc_type or "policy", std))

    # If explicit refs found, add those controls to the priority list
    priority_refs = set(doc.explicit_refs)

    scoped = []
    for ctrl in controls:
        ref = ctrl.get("ref", "")
        if ref in priority_refs:
            scoped.insert(0, ctrl)   # priority refs first
        elif any(ref.startswith(grp) for grp in clause_groups):
            scoped.append(ctrl)

    # If nothing matched, return first 25 controls
    if not scoped:
        return controls[:MAX_CONTROLS_PER_CALL]

    return scoped[:MAX_CONTROLS_PER_CALL * 2]   # allow up to 2 batches


_SECTION_NARROW_THRESHOLD = 25   # only narrow if doc-level scope > 25


def _scope_controls_to_section(
    controls: list[dict],
    section:  RawSection,
    doc:      ParsedDocument,
) -> list[dict]:
    """
    Further scope controls to a specific section. Narrowing is
    SUBTRACTIVE — pick a subset of `controls` to send to the LLM —
    so it's only safe when the doc-level scope is wide enough that
    each section won't need the whole list anyway.

    When the caller has already narrowed via doc_mappings (~6-15
    controls), per-section narrowing only discards legitimate
    candidates the LLM could find evidence for. The
    _SECTION_NARROW_THRESHOLD gate skips narrowing in that case;
    the caller's doc-level scope is used per section. The LLM's
    40-char verbatim-quote bar + post-process filters handle false
    positives.

    For pre-doc_mappings flows (large `controls` lists from
    `_scope_controls`), the original narrowing logic still applies.
    """
    if len(controls) <= _SECTION_NARROW_THRESHOLD:
        return controls

    # Extract refs explicitly mentioned in this section
    section_refs = set()
    for std in (doc.standard_ids or ["ISO27001:2022"]):
        section_refs.update(extract_refs_from_text(section.text, std))

    if section_refs:
        # This section mentions specific controls — only assess those
        return [c for c in controls if c["ref"] in section_refs]

    # Fall back to heading keyword matching
    heading = (section.heading or "").lower()
    keyword_map = {
        "access": ["A.5.15", "A.5.16", "A.5.17", "A.5.18"],
        "incident": ["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28"],
        "supplier": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
        "cryptograph": ["A.8.24"],
        "backup": ["A.8.13"],
        "logging": ["A.8.15", "A.8.16", "A.8.17"],
        "vulnerability": ["A.8.8"],
        "physical": ["A.7.1", "A.7.2", "A.7.3", "A.7.4"],
        "personnel": ["A.6.1", "A.6.2", "A.6.3", "A.6.4", "A.6.5"],
        "asset": ["A.5.9", "A.5.10", "A.5.11"],
        "risk": ["6.1", "8.2", "8.3"],
        "privacy": ["Art.5", "Art.6", "Art.7", "Art.32"],
        "data subject": ["Art.13", "Art.14", "Art.15", "Art.17"],
    }

    matched_refs = set()
    for keyword, refs in keyword_map.items():
        if keyword in heading:
            matched_refs.update(refs)

    if matched_refs:
        return [c for c in controls if c["ref"] in matched_refs]

    return []   # no match — skip this section


def _chunk_controls(controls: list[dict], size: int) -> list[list[dict]]:
    """Split control list into batches for LLM calls."""
    return [controls[i:i + size] for i in range(0, len(controls), size)]


def _merge_small_sections(sections: list[RawSection], min_tokens: int = 200) -> list[RawSection]:
    """
    Merge sections that are too small to assess independently.
    Small sections are appended to the next section.
    """
    from rag.intake.readers import CHARS_PER_TOKEN
    merged = []
    buffer = []

    for section in sections:
        token_est = len(section.text) // CHARS_PER_TOKEN
        buffer.append(section)

        if token_est >= min_tokens:
            if len(buffer) == 1:
                merged.append(buffer[0])
            else:
                combined_text    = "\n\n".join(s.text for s in buffer)
                combined_heading = buffer[0].heading or buffer[-1].heading
                merged.append(RawSection(
                    section_id = buffer[0].section_id,
                    heading    = combined_heading,
                    text       = combined_text,
                    page_start = buffer[0].page_start,
                    page_end   = buffer[-1].page_end,
                    level      = buffer[0].level,
                ))
            buffer = []

    # Flush remaining buffer
    if buffer:
        if merged:
            last = merged[-1]
            merged[-1] = RawSection(
                section_id = last.section_id,
                heading    = last.heading,
                text       = last.text + "\n\n" + "\n\n".join(s.text for s in buffer),
                page_start = last.page_start,
                page_end   = buffer[-1].page_end,
                level      = last.level,
            )
        else:
            for s in buffer:
                merged.append(s)

    return merged
