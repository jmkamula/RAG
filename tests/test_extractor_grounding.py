"""
Unit tests for the verbatim-quote grounding check in
rag/intake/extractor.py::_evidence_grounded.

This is the load-bearing anti-hallucination safeguard for the
Determinative LLM path — it drops any extractor-produced finding
whose quote can't be substring-matched (after punctuation
normalisation) back to the source document. See
[[ship-6-prime-a-llm-role-audit-2026-07-18]] +
[[ship-6-prime-b-grounding-provenance-2026-07-18]].

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_extractor_grounding.py
"""
from __future__ import annotations

import sys

from rag.intake.extractor import _evidence_grounded, _MIN_EVIDENCE_LEN
from rag.intake.models import ExtractionPath, ParsedDocument


def _doc(full_text: str = "", markdown: str = "") -> ParsedDocument:
    return ParsedDocument(
        source_file="/tmp/x.docx",
        file_type="docx",
        original_name="test.docx",
        full_text=full_text,
        markdown=markdown or None,
        extraction_path=ExtractionPath.FULL_DOCUMENT,
    )


def _check(label: str, got: bool, want: bool) -> bool:
    status = "PASS" if (bool(got) == want) else "FAIL"
    print(f"  [{status}] {label}  got={got!r} want={want}")
    return bool(got) == want


def test_grounded_verbatim() -> int:
    print("\n_evidence_grounded — real quote is grounded")
    body = (
        "Section 4. Access rights shall be reviewed quarterly and "
        "revoked on termination. Additional content here."
    )
    quote = "Access rights shall be reviewed quarterly and revoked on termination."
    return 0 if _check("verbatim quote grounded", _evidence_grounded(quote, _doc(full_text=body)), True) else 1


def test_fabricated_dropped() -> int:
    print("\n_evidence_grounded — fabricated quote dropped")
    body = (
        "Section 4. Access rights shall be reviewed quarterly and "
        "revoked on termination. Additional content here."
    )
    # Plausible-sounding compliance phrasing that does NOT appear in body
    quote = "The organisation encrypts all data at rest using AES-256 with quarterly key rotation."
    return 0 if _check("fabricated quote dropped", _evidence_grounded(quote, _doc(full_text=body)), False) else 1


def test_punctuation_drift_lenient() -> int:
    print("\n_evidence_grounded — punctuation drift is tolerated")
    # Source renders bullets with dashes + newlines
    body = (
        "Access controls include:\n"
        "- Role-based access control\n"
        "- Multi-factor authentication\n"
        "- Quarterly access reviews\n"
    )
    # LLM cites with semicolons between bullets — a common paraphrase
    quote = "Access controls include: Role-based access control; Multi-factor authentication; Quarterly access reviews"
    return 0 if _check("dash→semicolon bullets grounded", _evidence_grounded(quote, _doc(full_text=body)), True) else 1


def test_short_quote_dropped() -> int:
    print(f"\n_evidence_grounded — quotes below {_MIN_EVIDENCE_LEN} chars dropped")
    body = "MFA is required for all administrative accounts across the organisation."
    quote = "MFA is required."  # < 40 chars, even if present
    fails = 0
    fails += 0 if _check("short quote dropped even if present", _evidence_grounded(quote, _doc(full_text=body)), False) else 1
    fails += 0 if _check("empty quote dropped", _evidence_grounded("", _doc(full_text=body)), False) else 1
    return fails


def test_markdown_source_grounded() -> int:
    print("\n_evidence_grounded — markdown source is checked when full_text empty")
    md = (
        "## Access Control\n\n"
        "| Role | Access | Review |\n"
        "|------|--------|--------|\n"
        "| Admin | Full | Quarterly access reviews are performed each quarter |\n"
    )
    quote = "Quarterly access reviews are performed each quarter by the IT security team"
    # quote isn't verbatim (extra clause) but first 50 chars normalized ARE in md
    return 0 if _check(
        "grounded via markdown when full_text empty",
        _evidence_grounded(quote, _doc(full_text="", markdown=md)),
        True,
    ) else 1


def test_no_text_lenient() -> int:
    print("\n_evidence_grounded — no text at all → lenient (Stage-1 catches it)")
    quote = "This policy establishes the framework for information security across the organisation."
    # Both full_text + markdown empty (unusual — happens on unsupported formats)
    fails = 0
    fails += 0 if _check(
        "both sources empty → grounded (deferred to HITL)",
        _evidence_grounded(quote, _doc(full_text="", markdown="")),
        True,
    ) else 1
    # But if EITHER source has content, missing quote is still a hallucination
    fails += 0 if _check(
        "one source populated, quote absent → dropped",
        _evidence_grounded(quote, _doc(full_text="Unrelated content that does not contain the quote at all.", markdown="")),
        False,
    ) else 1
    return fails


def main() -> int:
    print("─" * 70)
    print("  rag/intake/extractor — _evidence_grounded (Ship 6'.b)")
    print("─" * 70)
    fails = (
        test_grounded_verbatim()
        + test_fabricated_dropped()
        + test_punctuation_drift_lenient()
        + test_short_quote_dropped()
        + test_markdown_source_grounded()
        + test_no_text_lenient()
    )
    print()
    if fails == 0:
        print("  All tests PASS")
        return 0
    print(f"  {fails} test(s) FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
