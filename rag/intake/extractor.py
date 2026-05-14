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
        return _extract_structured(doc)

    # Scope controls to those relevant for this document type + standard
    scoped = _scope_controls(controls, doc)
    if not scoped:
        logger.warning(f"No controls scoped for {doc.original_name} — using all controls")
        scoped = controls[:MAX_CONTROLS_PER_CALL]

    if doc.extraction_path == ExtractionPath.FULL_DOCUMENT:
        return _extract_full(doc, scoped, api_key)
    else:  # SECTION_BASED
        return _extract_sections(doc, scoped, api_key)


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
    doc:      ParsedDocument,
    controls: list[dict],
    api_key:  str,
) -> list[DocumentFinding]:
    """Single LLM call for the entire document."""

    chunks = _chunk_controls(controls, MAX_CONTROLS_PER_CALL)
    all_findings = []

    for chunk_controls in chunks:
        text = _build_doc_context(doc) + "\n\n" + doc.full_text

        raw = _llm_extract(
            text       = text,
            controls   = chunk_controls,
            doc_name   = doc.original_name,
            api_key    = api_key,
            chunk_hint = "full document",
        )
        findings = _parse_llm_response(raw, doc, chunk_controls, section=None, chunk_id="full")
        all_findings.extend(findings)

    logger.info(f"Full extraction: {len(all_findings)} findings from {doc.original_name}")
    return all_findings


# =============================================================================
# SECTION-BASED PATH
# =============================================================================

def _extract_sections(
    doc:      ParsedDocument,
    controls: list[dict],
    api_key:  str,
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

        # Scope controls to this section using heading keywords + explicit refs
        section_controls = _scope_controls_to_section(controls, section, doc)
        if not section_controls:
            continue

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
            )
            findings = _parse_llm_response(
                raw, doc, control_chunk,
                section  = section.heading,
                chunk_id = chunk_id,
                page     = section.page_start,
            )

            # Merge: Comply > OFI > NC > not_addressed
            # If same control found in multiple sections, keep the strongest
            _PRIORITY = {"Comply": 3, "OFI": 2, "NC": 1, "not_addressed": 0}
            for f in findings:
                existing = all_findings.get(f.control_ref)
                if existing is None:
                    all_findings[f.control_ref] = f
                elif _PRIORITY.get(f.finding, 0) > _PRIORITY.get(existing.finding, 0):
                    all_findings[f.control_ref] = f

    result = list(all_findings.values())
    logger.info(f"Section extraction: {len(result)} findings from {doc.original_name}")
    return result


# =============================================================================
# LLM CALL
# =============================================================================

_SYSTEM_PROMPT = """You are a compliance analyst reviewing a document to assess ISO 27001 / GDPR compliance.

Your task: for each control provided, determine whether this document provides evidence of compliance.

Rules:
- Only assess controls that are clearly addressed in the document text
- Use "not_addressed" when the document simply doesn't cover that control
- Do NOT infer or assume — only extract explicit evidence
- "Comply" = document demonstrates the control is implemented
- "OFI" = document shows partial or planned implementation
- "NC" = document explicitly states the control is not implemented or missing
- "not_addressed" = the document does not address this control

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
    "finding": "Comply",
    "evidence": "one sentence from the document that supports this finding",
    "confidence": "high"
  }},
  ...
]

Only include controls that are addressed in this document.
For controls not addressed, omit them from the response entirely."""


def _llm_extract(
    text:       str,
    controls:   list[dict],
    doc_name:   str,
    api_key:    str,
    chunk_hint: str = "",
) -> str:
    """Make one LLM extraction call. Returns raw JSON string."""

    control_list = "\n".join(
        f"- {c['ref']}: {c.get('title', c['ref'])}"
        for c in controls
    )

    user_prompt = _USER_TEMPLATE.format(
        doc_context  = f"Document: {doc_name}" + (f" | Section: {chunk_hint}" if chunk_hint else ""),
        text         = text[:80000],   # safety cap — should be within context window
        control_list = control_list,
    )

    body = json.dumps({
        "model":      EXTRACT_MODEL,
        "max_tokens": 2000,
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
    except Exception as e:
        logger.error(f"LLM extraction failed for {doc_name} [{chunk_hint}]: {e}")
        return "[]"


# =============================================================================
# RESPONSE PARSER
# =============================================================================

def _parse_llm_response(
    raw:        str,
    doc:        ParsedDocument,
    controls:   list[dict],
    section:    Optional[str],
    chunk_id:   str,
    page:       Optional[int] = None,
) -> list[DocumentFinding]:
    """Parse the LLM JSON response into DocumentFinding objects."""

    # Strip markdown fences
    raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
    if not raw or raw == "[]":
        return []

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in LLM response: {e}\nRaw: {raw[:200]}")
        return []

    # Build control lookup for validation
    valid_refs = {c["ref"] for c in controls}

    findings = []
    for item in items:
        ref     = item.get("control_ref", "").strip()
        finding = item.get("finding", "not_addressed").strip()

        if not ref or finding == "not_addressed":
            continue

        # Normalize ref
        for std in (doc.standard_ids or ["ISO27001:2022"]):
            normalized = normalize_ref(ref, std)
            if normalized:
                ref = normalized
                standard_id = std
                break
        else:
            standard_id = doc.standard_ids[0] if doc.standard_ids else "ISO27001:2022"

        if finding not in ("Comply", "OFI", "NC"):
            continue

        confidence = item.get("confidence", "medium")
        if confidence not in ("high", "medium", "low"):
            confidence = "medium"

        findings.append(DocumentFinding(
            upload_id       = doc.upload_id or "",
            tenant_id       = "",   # set by writer
            document_name   = doc.original_name,
            control_ref     = ref,
            standard_id     = standard_id,
            finding         = finding,
            evidence_text   = item.get("evidence", "")[:500],
            confidence      = confidence,
            section         = section,
            page_number     = page,
            extraction_path = doc.extraction_path.value,
            chunk_id        = chunk_id,
        ))

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


def _scope_controls_to_section(
    controls: list[dict],
    section:  RawSection,
    doc:      ParsedDocument,
) -> list[dict]:
    """
    Further scope controls to a specific section using heading keywords
    and explicit refs found in the section text.
    """
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
    from intake.readers import CHARS_PER_TOKEN
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
