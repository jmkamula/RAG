"""
Ship 75'.d — critic-verifier path FindingContract migration test.

Locks the wire-up: `_run_critic_verifier_pass` builds an
`ExtractedCandidate` per surviving critic entry and calls
`FINDING_CONTRACT.bind()`. The contract's skip-reason gates
(EMPTY_TEXT / PURE_SCAFFOLDING / MANGLED_ITEM_ID / UNRESOLVABLE_REF)
now protect the critic path in addition to the LLM + fingerprint +
consensus paths.

The critic-verifier function has more scaffolding upstream than
the other paths (Neo4j meta lookup, priming/extend pool build,
embedding cosine gate). We monkeypatch enough to let the migrated
bind() loop run with crafted entries.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.intake import extractor


class _FakeParsedDoc:
    def __init__(self, name: str = "fake.md", body: str = ""):
        self.upload_id      = ""
        self.original_name  = name
        self.markdown       = body
        self.full_text      = body
        self.standard_ids   = ["ISO27001:2022"]
        self.explicit_refs  = []
        self.extraction_metrics: dict = {}
        self.paragraphs = [body] if body else []
        self.raw_sections = []


@dataclass
class _FakePrimingItem:
    control_ref: str = "A.5.18"
    business_description: str = "Access rights review anchor description."
    candidate_musts: list = field(default_factory=list)


def _run(entries: list[dict], body: str) -> tuple[list, dict]:
    """Invoke `_run_critic_verifier_pass` with crafted entries.

    Monkeypatches every upstream stage that would otherwise need Neo4j /
    LLM / embedding infrastructure. The bind() loop is what we're
    testing — everything else is scaffolding.
    """
    doc = _FakeParsedDoc(body=body)
    priming = [_FakePrimingItem(
        candidate_musts=[{"must_id": "item:A.5.18:rev_sla_met",
                          "standard_id": "ISO27001:2022"}]
    )]

    with patch("rag.intake.critic_verifier._extract_critic_verifier",
                      return_value=({"confirmed": entries, "extended": []}, None)), \
         patch("rag.intake.critic_verifier._build_priming_set",
               return_value=priming), \
         patch("rag.intake.critic_verifier._build_extend_pool",
               return_value=[]), \
         patch("rag.intake.critic_verifier.build_control_meta_from_neo4j",
               return_value={}), \
         patch("rag.intake.must_embedding_lookup.semantic_controls_in_scope",
               return_value=set()), \
         patch("rag.posture_loader._build_engine_neo4j_driver",
               return_value=None), \
         patch("rag.intake.critic_verifier._get_embed_fn",
               return_value=None), \
         patch("rag.intake.critic_verifier._semantic_fit_ok",
               return_value=(True, "ok", 1.0)), \
         patch.object(extractor, "_looks_like_field_or_header",
                      return_value=(False, "")), \
         patch.object(extractor, "_evidence_grounded",
                      return_value=True):
        findings = extractor._run_critic_verifier_pass(
            doc, scoped=[], fp_findings=[], fp_covered=set(),
        )
    return findings, doc.extraction_metrics


# ── Test cases ──────────────────────────────────────────────────────

def test_substantive_entry_binds_and_emits_finding():
    substantive = (
        "Access rights for departing employees shall be revoked within "
        "24 hours of the last day of employment."
    )
    entries = [{
        "control_ref":       "A.5.18",
        "checklist_item_id": "item:A.5.18:rev_sla_met",
        "quote":             substantive,
        "confidence":        "high",
    }]
    findings, metrics = _run(entries, body=substantive)

    assert len(findings) == 1, f"expected 1 finding, got {len(findings)}"
    assert findings[0].control_ref == "A.5.18"
    assert findings[0].checklist_item_id == "item:A.5.18:rev_sla_met"
    assert findings[0].extraction_path == "critic_verifier"
    for k in ("contract_skip_empty_text", "contract_skip_pure_scaffolding",
              "contract_skip_mangled_item_id",
              "contract_skip_unresolvable_control_ref"):
        assert metrics.get(k, 0) == 0, f"{k} should be zero, got {metrics.get(k)}"


def test_mangled_id_drops_and_increments_counter():
    substantive = "Access revocation completed within 24 hours."
    entries = [{
        "control_ref":       "A.5.18",
        "checklist_item_id": "item:A.5.18:not_a_real_must_id_xyz",
        "quote":             substantive,
        "confidence":        "medium",
    }]
    findings, metrics = _run(entries, body=substantive)

    assert findings == [], "mangled item_id must not bind"
    assert metrics.get("contract_skip_mangled_item_id", 0) == 1


def test_null_checklist_item_id_passes_through_by_design():
    """Bind's line-321 rule: `if candidate.item_id and not catalog_recognises(...)`
    — empty item_id (from `entry.get('checklist_item_id') or ""`) SKIPS
    the catalog check. Findings without a per-MUST binding pass through
    with checklist_item_id=None. This preserves the pre-migration critic
    behavior. If we later want to tighten null-item_id acceptance, that's
    a bind() change (affects LLM + critic + future paths uniformly)."""
    substantive = "Access revocation completed within 24 hours."
    entries = [{
        "control_ref":       "A.5.18",
        "checklist_item_id": None,
        "quote":             substantive,
        "confidence":        "medium",
    }]
    findings, metrics = _run(entries, body=substantive)

    assert len(findings) == 1, "null item_id should emit (design)"
    assert findings[0].checklist_item_id is None
    # No skip counter should fire — this candidate is bind-accepted.
    assert metrics.get("contract_skip_mangled_item_id", 0) == 0


if __name__ == "__main__":
    test_substantive_entry_binds_and_emits_finding()
    test_mangled_id_drops_and_increments_counter()
    test_null_checklist_item_id_passes_through_by_design()
    print("OK — critic-verifier path routes through FindingContract")
