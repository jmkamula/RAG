"""
Ship 78'.b — regression test for the union extractor helper.

Locks the dedup behavior per Ship 78'.a D2/D6:
  - Dedup key is (control_ref, checklist_item_id)
  - Winner selection: higher confidence wins
  - Tie-break: prefer critic (LLM refinement)
  - Uniques from each path pass through
  - Empty-input paths handled cleanly (one path fails → other path's
    findings still emit)
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.intake.extractor import _union_findings
from rag.intake.models import DocumentFinding


def _mk(ref: str, must: str, conf: str, evidence: str = "") -> DocumentFinding:
    return DocumentFinding(
        upload_id="", tenant_id="", document_name="test.docx",
        control_ref=ref, standard_id="ISO27001:2022",
        finding="Comply", evidence_text=evidence or f"{ref}/{must}/{conf}",
        confidence=conf,
        checklist_item_id=must,
    )


def test_higher_confidence_wins():
    """Critic's high beats consensus's medium on the same (ref, must)."""
    c = [_mk("A.5.1", "item:A.5.1:x", "medium", "consensus_evidence")]
    k = [_mk("A.5.1", "item:A.5.1:x", "high", "critic_evidence")]
    u = _union_findings(c, k)
    assert len(u) == 1
    assert u[0].confidence == "high"
    assert u[0].evidence_text == "critic_evidence"


def test_lower_confidence_loses():
    """Consensus's medium keeps if critic offers low."""
    c = [_mk("A.5.1", "item:A.5.1:x", "medium", "consensus_evidence")]
    k = [_mk("A.5.1", "item:A.5.1:x", "low", "critic_evidence")]
    u = _union_findings(c, k)
    assert len(u) == 1
    assert u[0].confidence == "medium"
    assert u[0].evidence_text == "consensus_evidence"


def test_tie_breaks_to_critic():
    """Same confidence: critic wins per D6."""
    c = [_mk("A.5.1", "item:A.5.1:x", "medium", "consensus_evidence")]
    k = [_mk("A.5.1", "item:A.5.1:x", "medium", "critic_evidence")]
    u = _union_findings(c, k)
    assert len(u) == 1
    assert u[0].evidence_text == "critic_evidence"


def test_uniques_pass_through():
    """Findings unique to one path pass through unchanged."""
    c = [
        _mk("A.5.1", "item:A.5.1:x", "medium"),
        _mk("A.5.2", "item:A.5.2:y", "high"),
    ]
    k = [
        _mk("A.5.3", "item:A.5.3:z", "high"),
    ]
    u = _union_findings(c, k)
    refs = {f.control_ref for f in u}
    assert refs == {"A.5.1", "A.5.2", "A.5.3"}
    assert len(u) == 3


def test_empty_consensus():
    """Consensus failure / empty output — critic findings still emit."""
    u = _union_findings([], [
        _mk("A.5.1", "item:A.5.1:x", "high"),
    ])
    assert len(u) == 1


def test_empty_critic():
    """Critic failure / empty output — consensus findings still emit."""
    u = _union_findings([_mk("A.5.1", "item:A.5.1:x", "high")], [])
    assert len(u) == 1


def test_both_empty():
    """Both empty → empty result."""
    u = _union_findings([], [])
    assert u == []


def test_dedup_key_includes_checklist_item_id():
    """Same control_ref but different checklist_item_id → 2 separate findings."""
    c = [
        _mk("A.5.1", "item:A.5.1:x", "medium"),
        _mk("A.5.1", "item:A.5.1:y", "medium"),
    ]
    u = _union_findings(c, [])
    assert len(u) == 2


def test_dedup_handles_null_checklist_item_id():
    """Findings without checklist_item_id keyed on (control_ref, '')."""
    # Both findings would have "" as the empty key
    c = [
        DocumentFinding(
            upload_id="", tenant_id="", document_name="t.docx",
            control_ref="A.5.1", standard_id="ISO27001:2022",
            finding="Comply", evidence_text="c", confidence="medium",
            checklist_item_id=None,
        ),
    ]
    k = [
        DocumentFinding(
            upload_id="", tenant_id="", document_name="t.docx",
            control_ref="A.5.1", standard_id="ISO27001:2022",
            finding="Comply", evidence_text="k", confidence="high",
            checklist_item_id=None,
        ),
    ]
    u = _union_findings(c, k)
    # Same (A.5.1, None) key → dedup, critic wins on confidence
    assert len(u) == 1
    assert u[0].confidence == "high"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
    print("OK — Ship 78'.b union extractor invariants hold")
