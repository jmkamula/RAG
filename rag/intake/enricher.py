"""
ArionComply — Document Enricher
Stage 2: Classify the document, detect standards, scan for explicit control refs,
and decide the extraction path based on document size.

Token thresholds:
  ≤ 100,000  → FULL_DOCUMENT  (one LLM call)
  100,001 – 500,000 → SECTION_BASED (one call per section)
  > 500,000  → MANUAL_REVIEW  (flag for human)
  XLSX/CSV structured → STRUCTURED (no LLM)
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

from .models import ParsedDocument, ExtractionPath
from .ref_normalizer import extract_refs_from_text

logger = logging.getLogger(__name__)

TOKEN_FULL_LIMIT    = 100_000
TOKEN_SECTION_LIMIT = 500_000

SUPPORTED_STANDARDS = [
    "ISO27001:2022",
    "ISO27701:2019",
    "GDPR:2016/679",
    "SOC2:2017",
    "NIST:CSF2",
    "CYBER_ESSENTIALS",
]

# Keywords for standard detection without LLM
_STANDARD_KEYWORDS = {
    "ISO27001:2022":  ["iso 27001", "iso27001", "isms", "information security management", "annex a"],
    "ISO27701:2019":  ["iso 27701", "iso27701", "pims", "privacy information management"],
    "GDPR:2016/679":  ["gdpr", "general data protection", "data protection regulation", "article 32", "dpa"],
    "SOC2:2017":      ["soc 2", "soc2", "aicpa", "trust service"],
    "NIST:CSF2":      ["nist csf", "cybersecurity framework", "nist 2"],
    "CYBER_ESSENTIALS": ["cyber essentials", "cyberessentials"],
}

_DOC_TYPE_KEYWORDS = {
    "policy":          ["policy", "policies"],
    "procedure":       ["procedure", "process", "workflow", "how to"],
    "risk_register":   ["risk register", "risk assessment", "risk log", "risk matrix"],
    "audit_report":    ["audit report", "audit finding", "internal audit", "surveillance audit"],
    "evidence":        ["evidence", "proof of", "record of", "log of", "screenshot"],
    "asset_inventory": ["asset inventory", "asset register", "cmdb", "asset list"],
}


def enrich(doc: ParsedDocument, api_key: Optional[str] = None) -> ParsedDocument:
    """
    Enrich a ParsedDocument with:
    - doc_type (from filename + content keywords, confirmed by LLM if needed)
    - standard_ids (from content keyword scan)
    - explicit_refs (control refs found by regex in full text)
    - scope_statement (first sentence containing "this policy/procedure applies to")
    - extraction_path (based on token count and file type)
    """
    # Check for structured XLSX/CSV first — no LLM needed
    structured_sections = [
        s for s in doc.raw_sections
        if s.metadata.get("structured") is True
    ]
    if structured_sections and doc.file_type in ("xlsx", "csv"):
        doc.extraction_path = ExtractionPath.STRUCTURED
        doc.doc_type        = _detect_doc_type_keyword(doc)
        doc.standard_ids    = _detect_standards_keyword(doc.full_text, doc.original_name)
        if not doc.doc_type:
            doc.doc_type = "risk_register" if doc.file_type in ("xlsx", "csv") else "other"
        logger.info(f"STRUCTURED path: {doc.original_name} ({doc.doc_type})")
        return doc

    # Decide extraction path based on token count
    if doc.token_estimate > TOKEN_SECTION_LIMIT:
        doc.extraction_path = ExtractionPath.MANUAL_REVIEW
        logger.warning(
            f"Document too large ({doc.token_estimate:,} tokens): {doc.original_name} — flagged for manual review"
        )
        return doc
    elif doc.token_estimate > TOKEN_FULL_LIMIT:
        doc.extraction_path = ExtractionPath.SECTION_BASED
    else:
        doc.extraction_path = ExtractionPath.FULL_DOCUMENT

    # Keyword-based detection (fast, no LLM)
    doc.doc_type     = _detect_doc_type_keyword(doc)
    doc.standard_ids = _detect_standards_keyword(doc.full_text, doc.original_name)

    # Scope statement
    doc.scope_statement = _extract_scope_statement(doc.full_text)

    # Explicit control refs (regex scan of full text)
    for std in doc.standard_ids:
        refs = extract_refs_from_text(doc.full_text, std)
        for ref in refs:
            if ref not in doc.explicit_refs:
                doc.explicit_refs.append(ref)

    # LLM classification if keyword detection failed
    if (not doc.doc_type or not doc.standard_ids) and api_key:
        logger.info(f"Keyword detection incomplete — using LLM for {doc.original_name}")
        _llm_classify(doc, api_key)

    if not doc.doc_type:
        doc.doc_type = "other"
    if not doc.doc_type_confidence:
        doc.doc_type_confidence = 0.6 if doc.doc_type != "other" else 0.3

    logger.info(
        f"Enriched: {doc.original_name} | type={doc.doc_type} | "
        f"standards={doc.standard_ids} | path={doc.extraction_path.value} | "
        f"explicit_refs={len(doc.explicit_refs)} | ~{doc.token_estimate:,} tokens"
    )
    return doc


# =============================================================================
# KEYWORD DETECTION
# =============================================================================

def _detect_doc_type_keyword(doc: ParsedDocument) -> Optional[str]:
    """Detect doc type from filename and first 500 chars of text."""
    text  = (doc.original_name + " " + doc.full_text[:500]).lower()
    best  = None
    score = 0
    for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > score:
            score = hits
            best  = doc_type
    if best:
        doc.doc_type_confidence = min(0.5 + score * 0.15, 0.9)
    return best


def _detect_standards_keyword(text: str, filename: str) -> list[str]:
    """Detect which standards a document relates to from keywords."""
    combined = (filename + " " + text[:2000]).lower()
    found    = []
    for std, keywords in _STANDARD_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            found.append(std)
    return found or ["ISO27001:2022"]  # default assumption


def _extract_scope_statement(text: str) -> Optional[str]:
    """Extract the first sentence that describes document scope."""
    patterns = [
        r'[Tt]his\s+(?:policy|procedure|document|standard)\s+applies\s+to[^.]+\.',
        r'[Tt]his\s+(?:policy|procedure|document)\s+covers[^.]+\.',
        r'[Ss]cope[:\s]+([^.\n]+\.)',
        r'[Aa]pplicable\s+to[^.]+\.',
    ]
    for pattern in patterns:
        m = re.search(pattern, text[:3000])
        if m:
            return m.group(0).strip()
    return None


# =============================================================================
# LLM CLASSIFICATION (fallback)
# =============================================================================

def _llm_classify(doc: ParsedDocument, api_key: str) -> None:
    """
    Use LLM to classify doc_type and standard when keyword detection fails.
    Small, fast call — first 1000 chars of document + filename.
    """
    import urllib.request

    preview = doc.full_text[:1000]
    prompt  = f"""You are classifying a compliance document.

Filename: {doc.original_name}
First 1000 characters:
\"\"\"{preview}\"\"\"

Return JSON only:
{{
  "doc_type": one of ["policy","procedure","risk_register","evidence","audit_report","asset_inventory","other"],
  "standard_ids": list from ["ISO27001:2022","ISO27701:2019","GDPR:2016/679","SOC2:2017","NIST:CSF2","CYBER_ESSENTIALS"],
  "confidence": number between 0.0 and 1.0,
  "scope": "one sentence describing what this document covers, or null"
}}"""

    try:
        body = json.dumps({
            "model":      "claude-haiku-4-5-20251001",
            "max_tokens": 300,
            "messages":   [{"role": "user", "content": prompt}],
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
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())

        text = data["content"][0]["text"]
        # Strip any markdown fences
        text = re.sub(r'```json\s*|\s*```', '', text).strip()
        result = json.loads(text)

        if not doc.doc_type and result.get("doc_type"):
            doc.doc_type            = result["doc_type"]
            doc.doc_type_confidence = float(result.get("confidence", 0.7))

        if not doc.standard_ids and result.get("standard_ids"):
            doc.standard_ids = result["standard_ids"]

        if not doc.scope_statement and result.get("scope"):
            doc.scope_statement = result["scope"]

    except Exception as e:
        logger.warning(f"LLM classification failed for {doc.original_name}: {e}")
