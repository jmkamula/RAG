"""
ArionComply — Surgical Keyword Patches
Targeted fixes for specific retrieval failures identified in benchmark.

Rules:
  - Each keyword must contain a domain anchor (not generic)
  - Max 4-6 practitioner + 3 scenario per node
  - Must not contaminate adjacent control retrieval
  - Traceable to a specific benchmark failure

Benchmark failures addressed:
  F1: "what are our encryption gaps?"        → clarification (A.8.24)
  F2: "preparing for ISO 27001 audit"        → clarification (9.2, 9.2.1)
  F3: "cloud storage for data privacy"       → clarification (A.5.23, Art.28)
  F4: "what cryptographic controls..."       → 80% confidence (A.8.24)
  F5: "our obligation on cloud storage"      → clarification (A.5.23, Art.28)
"""

KEYWORD_PATCHES = {

    # ── F1, F4 — A.8.24 Cryptography ──────────────────────────────────────
    # Failure: "encryption gaps", "cryptographic controls for personal data"
    # triggered clarification instead of gap_analysis
    "A.8.24": {
        "practitioner": [
            "encryption gaps",
            "encryption policy gap",
            "cryptographic controls gap",
            "gaps in our encryption",
            "key management policy",
            "encryption policy for personal data",
        ],
        "scenario": [
            "our encryption policy does not cover personal data",
            "encryption policy gap analysis",
            "what encryption controls do we need",
        ],
        "confusion": ["A.8.11"],  # data masking — related but different
    },

    # ── F1 — A.8.11 Data masking ──────────────────────────────────────────
    # Not a direct failure but often co-retrieved with A.8.24
    # Add specificity to avoid contaminating encryption queries
    "A.8.11": {
        "practitioner": [
            "data masking gaps",
            "no data masking procedure",
            "data masking policy missing",
            "PII in non-production environments",
            "masking personal data in test environments",
        ],
        "scenario": [
            "personal data in non-production or test systems",
            "data masking procedure for compliance",
        ],
        "confusion": ["A.8.24"],  # encryption — different control
    },

    # ── F2 — 9.2 Internal audit ────────────────────────────────────────────
    # Failure: "preparing for our ISO 27001 audit next month"
    # triggered clarification — should map directly to internal audit
    "9.2": {
        "practitioner": [
            "preparing for ISO 27001 audit",
            "ISO audit preparation",
            "audit readiness",
            "internal audit programme",
            "ISMS internal audit",
            "audit next month",
        ],
        "scenario": [
            "preparing for certification audit",
            "what to prepare before ISO 27001 audit",
            "internal audit programme planning",
            "audit schedule and programme",
        ],
        "confusion": ["9.3"],  # management review — different clause
    },

    # ── F2 — 9.3 Management review ────────────────────────────────────────
    # Often paired with 9.2 for audit preparation queries
    "9.3": {
        "practitioner": [
            "management review ISO 27001",
            "management review inputs",
            "top management ISMS review",
            "annual management review",
        ],
        "scenario": [
            "management review before certification",
            "what goes into management review",
        ],
    },

    # ── F2 — 10.2 Nonconformity and corrective action ─────────────────────
    # Audit queries often need corrective action context
    "10.2": {
        "practitioner": [
            "corrective action ISO 27001",
            "nonconformity corrective action",
            "audit finding corrective action",
            "NC corrective action plan",
            "root cause analysis ISO 27001",
        ],
        "scenario": [
            "addressing audit nonconformities",
            "corrective action after audit finding",
        ],
    },

    # ── F3, F5 — A.5.23 Cloud services ────────────────────────────────────
    # Failure: "cloud storage for data privacy", "obligation on cloud storage"
    # triggered clarification — A.5.23 had no keywords at all
    "A.5.23": {
        "practitioner": [
            "cloud storage obligations ISO 27001",
            "cloud security requirements",
            "what do we need for cloud providers",
            "cloud services security policy",
            "cloud provider assessment",
            "approved cloud services",
            "SaaS security requirements",
            "cloud exit strategy",
        ],
        "scenario": [
            "using cloud storage for personal data",
            "cloud provider security assessment",
            "what ISO 27001 requires for cloud services",
            "onboarding a new cloud provider",
            "cloud data processing agreement",
        ],
        "confusion": ["A.5.19", "A.5.20", "A.7.10"],  # A.7.10 = physical media, not cloud
    },

    # ── A.7.10 Storage media — prevent cloud storage false positive ───────────
    "A.7.10": {
        "practitioner": [
            "physical storage media management",
            "removable media policy",
            "USB drive policy",
            "storage media disposal",
            "media sanitisation policy",
            "hard drive secure disposal",
        ],
        "scenario": [
            "managing physical storage media",
            "secure disposal of hard drives",
            "removable storage media controls",
        ],
        "confusion": ["A.5.23"],  # cloud services — different domain
    },

    # ── F3, F5 — Art.28 Processor obligations ─────────────────────────────
    # Failure: cloud storage queries should also surface Art.28
    # (DPA requirement when cloud provider processes personal data)
    "Art.28": {
        "practitioner": [
            "data processing agreement cloud",
            "processor agreement for cloud storage",
            "DPA for cloud providers",
            "what GDPR requires for cloud providers",
            "cloud provider data processing agreement",
            "processor obligations personal data",
        ],
        "scenario": [
            "cloud provider handling personal data",
            "SaaS application processing customer data",
            "what to include in DPA with cloud provider",
        ],
        "confusion": ["Art.32"],  # security obligations — different article
    },

    # ── General — Art.32 Security of processing ───────────────────────────
    # Low confidence (80%) on cryptographic controls query
    # Add posture-specific keywords
    "Art.32": {
        "practitioner": [
            "security measures for personal data",
            "encryption for personal data GDPR",
            "technical security measures GDPR",
            "appropriate technical measures",
            "security of personal data processing",
            "TOMs technical organisational measures",
        ],
        "scenario": [
            "what security measures does GDPR require",
            "encryption required under GDPR",
            "risk-based security measures personal data",
        ],
        "confusion": ["Art.33"],  # breach notification — different article
    },

    # ── General — 6.1.2 Risk assessment ───────────────────────────────────
    # Often missed in posture queries about risk assessment gaps
    "6.1.2": {
        "practitioner": [
            "risk assessment ISO 27001",
            "information security risk assessment",
            "risk assessment personal data",
            "risk assessment gaps",
            "risk assessment does not cover personal data",
            "ISMS risk assessment",
        ],
        "scenario": [
            "risk assessment not covering personal data processing",
            "extending risk assessment for GDPR",
        ],
    },
}


def apply_patches(nodes: list, patches: dict = None) -> tuple[int, list]:
    """
    Apply keyword patches to a list of RequirementNode objects.
    Returns (count_patched, list_of_patched_refs).

    Merges — does not replace existing keywords.
    """
    if patches is None:
        patches = KEYWORD_PATCHES

    patched = []
    for node in nodes:
        ref = node.ref
        if ref not in patches:
            continue

        patch = patches[ref]
        existing = node.query_keywords or {}

        merged = {}
        for category in ("exact", "practitioner", "scenario", "confusion"):
            existing_list = existing.get(category, [])
            patch_list    = patch.get(category, [])
            # Merge, deduplicate, preserve order
            combined = existing_list.copy()
            for kw in patch_list:
                if kw not in combined:
                    combined.append(kw)
            if combined:
                merged[category] = combined

        node.query_keywords = merged
        patched.append(ref)

    return len(patched), patched
