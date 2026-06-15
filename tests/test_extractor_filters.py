"""
Unit tests for content-shape filters in rag/intake/extractor.py.

Each filter exists to keep the LLM extractor from binding obviously-wrong
content as evidence of compliance. The filters are precise (low false-
positive risk on real policy text) and additive — adding new ones is the
canonical response to a "doc shape X produced N spurious findings"
incident report.

Current coverage:
  - `_looks_like_questionnaire`  — added 2026-06-12 (vendor security
    assessment template flooded findings)
  - `_looks_like_toc`            — added 2026-06-15 (TOC upload of
    ISMS doc list produced 47 inert pending findings)

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_extractor_filters.py
"""
from __future__ import annotations

import sys
from types import SimpleNamespace

from rag.intake.extractor import _looks_like_questionnaire, _looks_like_toc


def _doc(name: str = "", full_text: str = "", markdown: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        original_name=name, full_text=full_text, markdown=markdown,
    )


def _check(label: str, got: bool, want: bool) -> bool:
    status = "PASS" if (bool(got) == want) else "FAIL"
    print(f"  [{status}] {label}  got={got!r} want={want}")
    return bool(got) == want


def test_questionnaire() -> int:
    print("\n_looks_like_questionnaire")
    cases = [
        ("Y/N marker",        "Does the vendor encrypt at rest? (Y/N) Proof Point: yes", True),
        ("Yes/No marker",     "Is MFA enforced (Yes/No)?", True),
        ("Proof Point token", "Proof Point: SSO is enforced via Okta", True),
        ("interrogative",     "Does the organisation maintain an asset register?", True),
        ("real statement",    "The organisation maintains an asset register reviewed annually.", False),
        ("empty",             "", False),
    ]
    fails = 0
    for label, quote, want in cases:
        if not _check(label, _looks_like_questionnaire(quote), want):
            fails += 1
    return fails


def test_toc() -> int:
    print("\n_looks_like_toc")
    fails = 0

    # Filename signals
    fails += 0 if _check(
        "filename 'TOC'",
        _looks_like_toc(_doc(name="TOC Information Security Documents.docx")),
        True,
    ) else 1
    fails += 0 if _check(
        "filename 'Table of Contents'",
        _looks_like_toc(_doc(name="Table of Contents.pdf")),
        True,
    ) else 1
    fails += 0 if _check(
        "filename 'Index of'",
        _looks_like_toc(_doc(name="Index of Policies.docx")),
        True,
    ) else 1

    # Content-density signal — synthetic TOC body, no filename hint
    toc_body = (
        "ISMS Document Register\n\n"
        "2.1 Information Security Policy — Purpose: Defines security objectives.\n"
        "2.2 Access Control Policy — Purpose: Establishes access rules.\n"
        "2.4 Incident Management Policy — Purpose: Defines IR procedures.\n"
        "3.2 Access Management Process — Purpose: Defines provisioning.\n"
        "3.3 Incident Handling Process — Purpose: Outlines escalation steps.\n"
    )
    fails += 0 if _check(
        "toc-shape density (no filename hint)",
        _looks_like_toc(_doc(name="ISMS_register.docx", full_text=toc_body)),
        True,
    ) else 1

    # Negatives — real policy text + cross-ref policy + empty
    policy_body = (
        "1. Purpose\n"
        "This Information Security Policy establishes the framework for "
        "protecting information assets across the organisation.\n\n"
        "2. Scope\n"
        "This policy applies to all employees, contractors and third parties.\n"
    )
    fails += 0 if _check(
        "real policy",
        _looks_like_toc(_doc(name="information_security_policy.docx", full_text=policy_body)),
        False,
    ) else 1

    mixed_refs = (
        "Section 4.2 Access Management requires least privilege.\n"
        "Per ISO 27001 A.5.18, access rights must be reviewed periodically.\n"
        "Authentication (A.5.17) must use MFA.\n"
    )
    fails += 0 if _check(
        "policy with control cross-refs",
        _looks_like_toc(_doc(name="security_standard.docx", full_text=mixed_refs)),
        False,
    ) else 1

    fails += 0 if _check(
        "empty doc",
        _looks_like_toc(_doc(name="anything.docx")),
        False,
    ) else 1

    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/intake/extractor — content-shape filters")
    print("─" * 70)
    fails = test_questionnaire() + test_toc()
    print()
    if fails == 0:
        print(f"  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
