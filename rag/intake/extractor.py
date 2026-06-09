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
        return _extract_structured(doc)

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
- Cap your output at the 15 most-relevant controls. If more apply,
  rank by directness of coverage and return only the top 15.

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


def _evidence_grounded(evidence: str, doc: ParsedDocument) -> bool:
    """Verbatim-quote check. The LLM is instructed to provide a quote that
    actually appears in the document. Substring match (case-insensitive,
    normalised whitespace) catches hallucinated quotes — a common failure
    mode where the LLM paraphrases the doc but claims it's verbatim. We
    use only the first 50 chars of the evidence to be lenient on minor
    drift (the LLM sometimes elides trailing punctuation or articles)."""
    if not evidence or len(evidence) < _MIN_EVIDENCE_LEN:
        return False
    body = (doc.full_text or "").lower()
    if not body:
        # Some extraction paths don't keep the full text — skip the check
        # rather than wrongly drop. Tenant can still reject via Stage-1.
        return True
    needle = re.sub(r"\s+", " ", evidence[:50].lower()).strip()
    haystack = re.sub(r"\s+", " ", body)
    return needle in haystack


def _parse_llm_response(
    raw:        str,
    doc:        ParsedDocument,
    controls:   list[dict],
    section:    Optional[str],
    chunk_id:   str,
    page:       Optional[int] = None,
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
        logger.warning(f"JSON parse error in LLM response: {e}\nRaw: {raw[:200]}")
        return []

    # Build control lookup for validation
    valid_refs = {c["ref"] for c in controls}

    dropped_low_conf = 0
    dropped_short_quote = 0
    dropped_hallucinated = 0
    dropped_unknown_ref = 0
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

        findings.append(DocumentFinding(
            upload_id       = doc.upload_id or "",
            tenant_id       = "",   # set by writer
            document_name   = doc.original_name,
            control_ref     = ref,
            standard_id     = standard_id,
            finding         = finding,
            evidence_text   = evidence,
            confidence      = confidence,
            section         = section,
            page_number     = page,
            extraction_path = doc.extraction_path.value,
            chunk_id        = chunk_id,
        ))

    if dropped_low_conf or dropped_short_quote or dropped_hallucinated or dropped_unknown_ref:
        logger.info(
            "extractor filters dropped %d findings on chunk %s (doc=%s): "
            "low_conf=%d short_quote=%d hallucinated_quote=%d unknown_ref=%d",
            dropped_low_conf + dropped_short_quote + dropped_hallucinated + dropped_unknown_ref,
            chunk_id, doc.original_name,
            dropped_low_conf, dropped_short_quote, dropped_hallucinated, dropped_unknown_ref,
        )

    # Enforce 15-finding cap per chunk (the LLM is also prompted to cap;
    # this is the parse-side enforcement). Retains highest-confidence
    # findings first — Comply+high > OFI+high > NC+high > Comply+medium etc.
    if len(findings) > 15:
        conf_rank = {"high": 0, "medium": 1, "low": 2}
        find_rank = {"Comply": 0, "OFI": 1, "NC": 2}
        findings.sort(key=lambda f: (conf_rank.get(f.confidence, 3), find_rank.get(f.finding, 3)))
        findings = findings[:15]

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

    Logs the chosen mapping(s) at INFO so the next upload's scoping is
    visible in /tmp/api.log.
    """
    from .doc_discovery import discover_doc, union_target_controls

    proposals = discover_doc(
        filename     = doc.original_name or "",
        body_text    = doc.full_text or "",
        topic_tokens = doc.topic_tokens or None,
    )
    if not proposals:
        return []

    target_ctrls = set(union_target_controls(proposals))
    if not target_ctrls:
        return []

    # Intersect with the caller-provided control list — the caller already
    # filtered to controls that exist in the curated set; we just narrow.
    scoped = [c for c in controls if c.get("ref") in target_ctrls]

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
