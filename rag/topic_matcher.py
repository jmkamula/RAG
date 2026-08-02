"""
Topic-slug detection helper for Ship 54'.c chat topic-routing.

When the classifier tags a query as `topic_bundle`, this module
resolves the query to a specific topic slug (e.g., `dsr_management`)
using a curator-authored keyword map. Same source-of-truth pattern
as `rag/framework_refs.py` — data lives in code so it can be
reviewed + rippled in one commit.

Data flow:
    "how do I set up DSR?"       → dsr_management
    "walk me through incident"    → incident_response
    "what's involved in consent"  → consent_and_lawful_basis

The matcher returns `None` when no confident topic slug matches —
callers fall through to the normal chat pipeline.
"""

from __future__ import annotations

import re
from typing import Optional


# ── Topic keyword universe ────────────────────────────────────────────
#
# Ordered dict — longer phrases FIRST so "data subject access request"
# matches before "subject access". Slugs are the same identifiers used
# in `db/topics/*.yaml` (schema_v91 topics.slug PK).
#
# Extend when adding topics. Test: `python3 -c "from rag.topic_matcher
# import detect_topic_slug; print(detect_topic_slug('how do I set up
# DSR'))"` → "dsr_management".
_TOPIC_KEYWORDS: list[tuple[str, list[str]]] = [
    ("data_transfers_disclosures", [
        "cross-border transfer", "international transfer",
        "schrems ii", "schrems", "data transfer", "disclosure log",
        "third country transfer", "transfer impact assessment",
        "supplementary measures",
    ]),
    ("privacy_notice_transparency", [
        "privacy notice", "transparency notice", "privacy statement",
        "privacy information",
    ]),
    ("consent_and_lawful_basis", [
        "consent management", "lawful basis", "consent lifecycle",
        "consent capture", "lawfulness of processing",
        "consent withdrawal", "consent",
    ]),
    ("processor_operations", [
        "processor operations", "being a processor",
        "customer agreement", "processor mode",
        "we are a processor",
    ]),
    ("supplier_onboarding", [
        "supplier onboarding", "vendor onboarding",
        "processor onboarding", "third party assessment",
        "third-party assessment",
    ]),
    ("employee_lifecycle", [
        "employee lifecycle", "joiner mover leaver",
        "onboarding offboarding", "personnel security",
        "hr security", "starter leaver",
    ]),
    ("access_rights_lifecycle", [
        "access rights", "identity management", "identity lifecycle",
        "access provisioning", "identity + access", "iam lifecycle",
    ]),
    ("records_of_processing", [
        "ropa", "records of processing", "art 30 record",
        "art.30 record", "processing register",
    ]),
    ("business_continuity", [
        "business continuity", "bcp", "disaster recovery",
        "ict readiness", "dr plan",
    ]),
    ("continual_improvement", [
        "continual improvement", "corrective action",
        "nonconformity", "internal audit", "management review",
        "isms improvement",
    ]),
    ("change_management", [
        "change management", "change control", "isms change",
    ]),
    ("dpia_workflow", [
        "dpia", "data protection impact assessment",
        "privacy impact assessment", "pia",
    ]),
    ("breach_notification", [
        "breach notification", "data breach notification",
        "72 hour", "72-hour", "supervisory authority notification",
        "personal data breach",
    ]),
    ("incident_response", [
        "incident response", "security incident",
        "incident handling", "incident lifecycle",
        "incident management",
    ]),
    ("risk_assessment_treatment", [
        "risk assessment", "risk treatment", "risk cycle",
        "risk register", "risk methodology",
        "isms risk management",
    ]),
    ("dsr_management", [
        "data subject access request", "subject access request",
        "data subject rights", "dsar", "dsr",
        "subject rights", "rectification request",
        "erasure request", "right to be forgotten",
    ]),
    ("pii_lifecycle", [
        "pii lifecycle", "data minimization", "data minimisation",
        "retention schedule", "data disposal", "temp file",
        "privacy engineering", "pii retention",
        "personal data retention",
    ]),
]


# Trigger verbs — matched before the topic keyword to bias toward
# workflow queries vs. definition/gap queries. All optional; a bare
# topic-keyword query ("consent management") still matches.
_TRIGGER_RE = re.compile(
    r"\b("
    r"how\s+(?:do|would|should|can)\s+(?:i|we)\s+"
    r"(?:set\s+up|handle|run|implement|manage|do|approach|set-up|do)"
    r"|walk\s+me\s+through"
    r"|what(?:'|)s\s+involved\s+in"
    r"|tell\s+me\s+about"
    r"|guide\s+me\s+through"
    r"|help\s+me\s+with"
    r"|show\s+me\s+(?:the|our)\s+(?:workflow|process|bundle)\s+for"
    r")\b",
    re.IGNORECASE,
)


def detect_topic_slug(query: str) -> Optional[str]:
    """Match a natural-language query to a topic slug, or None.

    Priority ordering:
      1. Longer phrase-matches trump shorter ones (list order matters)
      2. Trigger verbs are considered but not required — a bare
         "consent management?" still resolves to consent_and_lawful_basis
      3. No confidence scoring in v1 — first-match wins after the
         phrase-length priority.
    """
    if not query:
        return None
    q = query.lower()
    for slug, keywords in _TOPIC_KEYWORDS:
        for kw in keywords:
            if kw in q:
                return slug
    return None


def has_topic_trigger(query: str) -> bool:
    """True when the query has a workflow-intent trigger verb.
    Used by the classifier to bump confidence on topic_bundle
    routing when a trigger + keyword co-occur."""
    if not query:
        return False
    return bool(_TRIGGER_RE.search(query))


__all__ = ["detect_topic_slug", "has_topic_trigger"]
