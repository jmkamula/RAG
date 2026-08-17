"""
Ship 75'.b — fingerprint path FindingContract migration test.

Locks the wire-up: `_extract_via_fingerprints` builds an
`ExtractedCandidate` and calls `FINDING_CONTRACT.bind()`, so the
contract's skip-reason gates (EMPTY_TEXT / PURE_SCAFFOLDING /
MANGLED_ITEM_ID / UNRESOLVABLE_REF) now protect the fingerprint
path in addition to the LLM path.

Monkeypatches `_fingerprint_extract_matches` to return crafted
matches — three shapes: substantive quote, scaffolding quote,
unrecognised item_id. Asserts:
  - Substantive → finding emits, contract_skip stays zero.
  - Scaffolding → drop, `contract_skip_pure_scaffolding` increments.
  - Mangled id  → drop, `contract_skip_mangled_item_id` increments.

Bypasses `_extract_quote_around_match` by injecting the quote via
a fake reader — see `_FakeParsedDoc` below.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.intake import extractor


class _FakeParsedDoc:
    """Minimal ParsedDocument stand-in for the fingerprint path."""
    def __init__(self, name: str = "fake.md", body: str = ""):
        self.upload_id = ""
        self.original_name = name
        self.markdown = body
        self.full_text = body
        self.extraction_metrics: dict = {}
        # Fields extractor may touch downstream but that don't
        # affect the fingerprint path directly:
        self.paragraphs = [body] if body else []
        self.raw_sections = []


def _run(matches: list[dict], body: str) -> tuple[list, set, dict]:
    """Invoke `_extract_via_fingerprints` with injected matches; return
    (findings, covered, metrics)."""
    doc = _FakeParsedDoc(body=body)

    # Bypass the real fingerprint match producer and the quote extractor.
    # We're not testing them here — the test targets the bind() wire-up.
    def _fake_quote(m: dict, _doc) -> str:
        return m.get("_quote", "")

    with patch.object(extractor, "_fingerprint_extract_matches",
                      return_value=matches), \
         patch.object(extractor, "_extract_quote_around_match",
                      side_effect=_fake_quote):
        findings, covered = extractor._extract_via_fingerprints(doc, [])
    return findings, covered, doc.extraction_metrics


# ── Test cases ──────────────────────────────────────────────────────

def test_substantive_quote_binds_and_emits_finding():
    """Contract accepts → finding lands, no skip counters increment."""
    substantive = (
        "Access rights for departing employees shall be revoked within "
        "24 hours of the last day of employment. The revocation is "
        "logged in the identity register."
    )
    matches = [{
        "leaf_id":     "req:A.5.18:access_rights_review",
        "must_id":     "item:A.5.18:rev_sla_met",
        "control_ref": "A.5.18",
        "standard_id": "ISO27001:2022",
        "matched_kw":  ["revocation"],
        "_quote":      substantive,
    }]
    findings, covered, metrics = _run(matches, body=substantive)

    assert len(findings) == 1, f"expected 1 finding, got {len(findings)}"
    assert covered == {"req:A.5.18:access_rights_review"}
    assert findings[0].control_ref == "A.5.18"
    assert findings[0].checklist_item_id == "item:A.5.18:rev_sla_met"
    assert findings[0].inference_source == "fingerprint_match"
    assert findings[0].extraction_path == "fingerprint"
    # No skip counters should fire.
    for k in ("contract_skip_empty_text", "contract_skip_pure_scaffolding",
              "contract_skip_mangled_item_id",
              "contract_skip_unresolvable_control_ref"):
        assert metrics.get(k, 0) == 0, f"{k} should be zero, got {metrics.get(k)}"


def test_scaffolding_quote_drops_and_increments_counter():
    """Contract rejects scaffolding → no finding, skip counter fires."""
    # Well-known scaffolding shape from the docx round-trip work.
    scaffolding = "▽ Standard text ▽"
    matches = [{
        "leaf_id":     "req:A.5.18:access_rights_review",
        "must_id":     "item:A.5.18:rev_sla_met",
        "control_ref": "A.5.18",
        "standard_id": "ISO27001:2022",
        "matched_kw":  ["revocation"],
        "_quote":      scaffolding,
    }]
    findings, covered, metrics = _run(matches, body=scaffolding)

    assert findings == [], "scaffolding must not bind"
    assert covered == set(), "no coverage on rejected fingerprint match"
    assert metrics.get("contract_skip_pure_scaffolding", 0) == 1, (
        f"expected contract_skip_pure_scaffolding=1, "
        f"got {metrics.get('contract_skip_pure_scaffolding')}"
    )


def test_mangled_must_id_drops_and_increments_counter():
    """Contract rejects unrecognised catalog id → skip counter fires."""
    substantive = "Access revocation completed within 24 hours."
    matches = [{
        "leaf_id":     "req:A.5.18:access_rights_review",
        # Deliberately malformed — not in catalog.
        "must_id":     "item:A.5.18:not_a_real_must_id_xyz",
        "control_ref": "A.5.18",
        "standard_id": "ISO27001:2022",
        "matched_kw":  ["revocation"],
        "_quote":      substantive,
    }]
    findings, covered, metrics = _run(matches, body=substantive)

    assert findings == [], "mangled item_id must not bind"
    assert covered == set(), "no coverage on rejected item_id"
    assert metrics.get("contract_skip_mangled_item_id", 0) == 1, (
        f"expected contract_skip_mangled_item_id=1, "
        f"got {metrics.get('contract_skip_mangled_item_id')}"
    )


if __name__ == "__main__":
    test_substantive_quote_binds_and_emits_finding()
    test_scaffolding_quote_drops_and_increments_counter()
    test_mangled_must_id_drops_and_increments_counter()
    print("OK — fingerprint path routes through FindingContract")
