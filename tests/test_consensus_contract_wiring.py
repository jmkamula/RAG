"""
Ship 75'.c — consensus path FindingContract migration test.

Locks the wire-up: `_extract_via_consensus` builds an
`ExtractedCandidate` per accepted verdict and calls
`FINDING_CONTRACT.bind()`, so the contract's skip-reason gates
(EMPTY_TEXT / PURE_SCAFFOLDING / MANGLED_ITEM_ID / UNRESOLVABLE_REF)
now protect the consensus path in addition to the LLM +
fingerprint paths.

Monkeypatches `run_extraction_consensus` to return a crafted
`ExtractionConsensusResult` with three verdicts — substantive,
scaffolding, mangled-id — and asserts the migrated loop routes
them through bind() with the correct outcomes.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.intake import extractor
from rag.intake.consensus_extraction.types import (
    CandidateVerdict, ExtractionConsensusResult,
)


class _FakeParsedDoc:
    def __init__(self, name: str = "fake.md"):
        self.upload_id = ""
        self.original_name = name
        self.markdown = ""
        self.full_text = ""
        self.extraction_metrics: dict = {}
        self.paragraphs = []
        self.raw_sections = []


def _build_result(verdicts: list[CandidateVerdict]) -> ExtractionConsensusResult:
    """Build a minimal result where every verdict is 'accept'
    (matches the `result.accepted()` filter inside _extract_via_consensus)."""
    for v in verdicts:
        v.verdict = "accept"
    return ExtractionConsensusResult(
        verdicts=verdicts,
        total_candidates=len(verdicts),
        n_accept=len(verdicts),
        n_arbiter=0,
        n_drop=0,
    )


def _run(verdicts: list[CandidateVerdict]) -> tuple[list, dict]:
    doc = _FakeParsedDoc()
    fake_result = _build_result(verdicts)
    with patch("rag.intake.extractor.run_extraction_consensus",
               return_value=fake_result, create=True):
        # `run_extraction_consensus` is imported inside the function so
        # patch it on the module path used at import-time.
        with patch("rag.intake.consensus_extraction.orchestrator.run_extraction_consensus",
                   return_value=fake_result):
            findings = extractor._extract_via_consensus(doc, ["fake:leaf"])
    return findings, doc.extraction_metrics


# ── Test cases ──────────────────────────────────────────────────────

def test_substantive_verdict_binds_and_emits_finding():
    substantive = (
        "Access rights for departing employees shall be revoked within "
        "24 hours of the last day of employment."
    )
    verdicts = [CandidateVerdict(
        candidate=("req:A.5.18:access_rights_review", "item:A.5.18:rev_sla_met"),
        score=2.5, corroborators=3, signals=["fingerprint_keyword"],
        verdict="accept",
        fingerprint_excerpt=substantive,
        fingerprint_position=0,
        control_ref="A.5.18",
        standard_id="ISO27001:2022",
    )]
    findings, metrics = _run(verdicts)

    assert len(findings) == 1, f"expected 1 finding, got {len(findings)}"
    assert findings[0].control_ref == "A.5.18"
    assert findings[0].checklist_item_id == "item:A.5.18:rev_sla_met"
    assert findings[0].extraction_path == "consensus"
    assert findings[0].inference_source == "fingerprint_match"
    for k in ("contract_skip_empty_text", "contract_skip_pure_scaffolding",
              "contract_skip_mangled_item_id",
              "contract_skip_unresolvable_control_ref"):
        assert metrics.get(k, 0) == 0, f"{k} should be zero, got {metrics.get(k)}"


def test_scaffolding_verdict_drops_and_increments_counter():
    verdicts = [CandidateVerdict(
        candidate=("req:A.5.18:access_rights_review", "item:A.5.18:rev_sla_met"),
        score=2.5, corroborators=3, signals=["fingerprint_keyword"],
        verdict="accept",
        fingerprint_excerpt="▽ Standard text ▽",
        fingerprint_position=0,
        control_ref="A.5.18",
        standard_id="ISO27001:2022",
    )]
    findings, metrics = _run(verdicts)

    assert findings == [], "scaffolding excerpt must not bind"
    assert metrics.get("contract_skip_pure_scaffolding", 0) == 1


def test_mangled_must_id_drops_and_increments_counter():
    verdicts = [CandidateVerdict(
        candidate=("req:A.5.18:access_rights_review",
                   "item:A.5.18:not_a_real_must_id_xyz"),
        score=2.5, corroborators=3, signals=["fingerprint_keyword"],
        verdict="accept",
        fingerprint_excerpt="Access revocation completed within 24 hours.",
        fingerprint_position=0,
        control_ref="A.5.18",
        standard_id="ISO27001:2022",
    )]
    findings, metrics = _run(verdicts)

    assert findings == [], "mangled item_id must not bind"
    assert metrics.get("contract_skip_mangled_item_id", 0) == 1


if __name__ == "__main__":
    test_substantive_verdict_binds_and_emits_finding()
    test_scaffolding_verdict_drops_and_increments_counter()
    test_mangled_must_id_drops_and_increments_counter()
    print("OK — consensus path routes through FindingContract")
