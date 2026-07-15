"""
StandardKnowledgePayload builder — DEFINITION queries.

Handles queries like:
  "what is OFI?"          → acronym expansion
  "what does ISMS mean?"  → acronym expansion + brief definition
  "what is A.5.15?"       → business_description from Chroma enrichment
  "what is GDPR Art.32?"  → business_description from Chroma enrichment

The builder is deterministic — no LLM. Given intent + tenant_context
+ optional retriever, it fills:
  - acronym + expansion from _ACRONYM_DEFINITIONS
  - business_description from Chroma (when a ref is in scope)
  - definition (short summary line)

Ship 3 (later) will polish these payload fields into natural prose
while preserving them structurally.
"""
from __future__ import annotations

import re
import time
from typing import Optional

from rag.answer.types import StandardKnowledgePayload, RefRecord
from rag.answer.builders.freeform import _infer_framework


# ══════════════════════════════════════════════════════════════════
# Compliance-domain acronyms surfaced by definition queries. Mirror
# the acronym set in the classifier's CLEAR_INTENT_PHRASES definition
# regex. Single source of truth for acronym expansions.
# ══════════════════════════════════════════════════════════════════

_ACRONYM_DEFINITIONS: dict[str, tuple[str, str]] = {
    # short name → (expansion, one-line definition)
    "OFI":  ("Opportunity for Improvement",
             "a required control exists but has gaps to address"),
    "NC":   ("Non-Conformity",
             "a required control or obligation is absent or not effectively implemented"),
    "ISMS": ("Information Security Management System",
             "a systematic approach to managing sensitive company information"),
    "DPIA": ("Data Protection Impact Assessment",
             "a GDPR-required assessment for processing that may risk data subjects' rights"),
    "DPO":  ("Data Protection Officer",
             "an individual appointed to oversee compliance with data protection law"),
    "RoPA": ("Record of Processing Activities",
             "a documented inventory of all personal-data processing under GDPR Art.30"),
    "DSAR": ("Data Subject Access Request",
             "a request from an individual to see, correct, or delete their personal data"),
    "DSR":  ("Data Subject Request",
             "a request from an individual exercising GDPR data subject rights"),
    "DPA":  ("Data Processing Agreement",
             "a contract between controller and processor governing personal-data handling"),
    "PIMS": ("Privacy Information Management System",
             "the ISO 27701 extension of an ISMS to cover privacy-specific controls"),
    "SoA":  ("Statement of Applicability",
             "a mandatory ISO 27001 document listing which Annex A controls apply and why"),
}


# Case-insensitive word-boundary regex for acronym detection
_ACRONYM_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _ACRONYM_DEFINITIONS) + r")\b",
    re.IGNORECASE,
)


def _match_acronym(query: str) -> Optional[str]:
    """Return the canonical acronym key if the query mentions one."""
    if not query:
        return None
    m = _ACRONYM_RE.search(query)
    if not m:
        return None
    matched_text = m.group(1)
    # Return canonical case from the dict
    for k in _ACRONYM_DEFINITIONS:
        if k.lower() == matched_text.lower():
            return k
    return None


def _extract_business_description(document: str) -> str:
    """Pull the business_description-shaped preamble out of a Chroma
    vector document. Chroma docs are structured layered text — the
    business description sits after the header line and before
    'Text: ' / 'Evidence: ' / 'Gaps: ' markers.
    """
    if not document:
        return ""
    # Split on lines and find the business_description slice
    lines = [ln.strip() for ln in document.split("\n") if ln.strip()]
    if len(lines) < 2:
        return ""
    # Line 0 is the header (e.g. "ISO27001:2022 A.8.19: title"). Body starts at 1.
    body_lines = []
    for ln in lines[1:]:
        # Stop at the first layered marker
        if ln.startswith(("Text: ", "Evidence: ", "Gaps: ", "Keywords: ",
                          "Related ", "Procedures ", "The following")):
            break
        body_lines.append(ln)
    return " ".join(body_lines).strip()


def build(
    intent,
    tenant_context,
    resolver,
    neo_driver=None,
    chroma_retriever=None,
) -> StandardKnowledgePayload:
    """Assemble a StandardKnowledgePayload from the query + resolver
    context. Deterministic — no LLM.
    """
    t0 = time.time()

    query = getattr(intent, "raw_query", "") or ""

    # ── Metadata ──────────────────────────────────────────────────
    tenant_id     = ""
    tenant_name   = ""
    frameworks    = []
    if tenant_context is not None:
        tenant_id   = str(getattr(tenant_context, "tenant_id", "") or "")
        tenant_name = str(getattr(tenant_context, "tenant_name", "") or "")
        _s = getattr(tenant_context, "scope", None)
        if _s is not None:
            frameworks = list(getattr(_s, "queryable_standards", []) or [])

    # ── Subject refs from cited_refs ──────────────────────────────
    subject_refs: list[RefRecord] = []
    provenance: list[str] = []
    for r in (getattr(intent, "cited_refs", []) or []):
        if not r:
            continue
        subject_refs.append(RefRecord(
            ref       = r,
            framework = _infer_framework(r),
            title     = "",
            node_id   = "",
        ))
    if subject_refs:
        provenance.append("cited_refs")

    # ── Acronym detection ────────────────────────────────────────
    acronym: Optional[str] = _match_acronym(query)
    expansion: Optional[str] = None
    one_line_def: str = ""
    if acronym:
        exp, defn = _ACRONYM_DEFINITIONS[acronym]
        expansion    = exp
        one_line_def = defn
        provenance.append("acronym_definitions")

    # ── Chroma enrichment for cited refs ─────────────────────────
    business_description = ""
    if subject_refs and chroma_retriever is not None:
        # First ref wins for the primary business_description
        top_ref = subject_refs[0].ref
        try:
            vr = chroma_retriever.search_by_ref(top_ref)
            if vr is not None:
                # Update the ref with title from Chroma
                subject_refs[0].title = vr.title or subject_refs[0].title
                subject_refs[0].node_id = vr.node_id
                # Extract business_description
                doc = getattr(vr, "document", "") or ""
                business_description = _extract_business_description(doc)
                if business_description:
                    provenance.append("chroma_business_description")
        except Exception:
            pass  # silent-fail; still produce a payload

    # ── Framework primary — from cited-ref shape or scope ─────────
    framework_primary = ""
    if subject_refs and subject_refs[0].framework:
        framework_primary = subject_refs[0].framework
    elif frameworks:
        framework_primary = frameworks[0]

    payload = StandardKnowledgePayload(
        question_type        = "definition",
        query                = query,
        tenant_id            = tenant_id,
        tenant_name          = tenant_name,
        framework_primary    = framework_primary,
        frameworks_scope     = frameworks,
        subject_refs         = subject_refs,
        signals_provenance   = provenance,
        acronym              = acronym,
        expansion            = expansion,
        definition           = one_line_def,
        business_description = business_description,
        examples             = [],       # deferred to Ship 3 / Chroma metadata
        misconceptions       = [],
        build_latency_ms     = int((time.time() - t0) * 1000),
    )
    return payload
