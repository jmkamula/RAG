"""
Tests for rag/casefile/repair.py — the check-and-repair pass.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from rag.casefile import CaseFile
from rag.casefile.preservation import (
    extract_preservation_spec,
    PreservationSpec,
)
from rag.casefile.repair import (
    check_and_repair,
    _refs_in_text,
    _verdict_appears_near,
    _draft_appears_near,
    _compliance_facts_footer,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@dataclass
class E:
    source_id: str; target_id: str; rel_type: str = "IMPLEMENTS"

@dataclass
class N:
    node_id:      str
    ref:          str
    standard_id:  str = "ISO27001:2022"
    title:        str = ""
    xfw_edges:    list = field(default_factory=list)
    is_informational: bool = False
    metadata:     dict = field(default_factory=dict)
    document:     str = ""

@dataclass
class G:
    primary_nodes:    list = field(default_factory=list)
    secondary_nodes:  list = field(default_factory=list)
    xfw_nodes:        list = field(default_factory=list)
    doc_contexts:     dict = field(default_factory=dict)
    xfw_edges:        list = field(default_factory=list)

@dataclass
class R:
    posture_nodes:  dict = field(default_factory=dict)
    graph_nodes:    Any = None


def _posture(items):
    return {
        f"ISO27001:2022:{ref}": {
            "finding": f,
            "gap_description": f"gap-{ref}",
            "evidence_text":   f"evid-{ref}",
            "control_ref":     ref,
            "confirmation_status": cs,
        }
        for ref, f, cs in items
    }


def make_cf(query="q", posture=None, primary=None, xfw=None, intent=None):
    return CaseFile(
        query=query, intent=intent,
        resolved=R(
            posture_nodes=dict(posture or {}),
            graph_nodes=G(
                primary_nodes=list(primary or []),
                xfw_nodes=list(xfw or []),
            ),
        ),
    )


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Detection primitives ──────────────────────────────────────────────

def test_refs_in_text_finds_annex_a():
    return _ok(_refs_in_text("A.5.18 is missing") == {"A.5.18"})


def test_refs_in_text_finds_gdpr_article():
    return _ok(_refs_in_text("Art.32 covers security") == {"Art.32"})


def test_refs_in_text_finds_iso_body_clause():
    return _ok("9.2" in _refs_in_text("clause 9.2 requires internal audit"))


def test_refs_in_text_multiple():
    got = _refs_in_text("A.5.18 [NC-DRAFT] and A.5.20 [NC] with Art.32 xfw")
    return _ok({"A.5.18", "A.5.20", "Art.32"}.issubset(got), got)


def test_verdict_appears_near_matches():
    return _ok(_verdict_appears_near("A.5.18 [NC-DRAFT] register", "A.5.18", "NC"))


def test_verdict_appears_near_case_insensitive():
    return _ok(_verdict_appears_near("A.5.18 nc register", "A.5.18", "NC"))


def test_verdict_appears_near_fails_when_far():
    text = "A.5.18 is a control." + " x " * 50 + "NC is a term."
    return _ok(not _verdict_appears_near(text, "A.5.18", "NC", window=20))


def test_draft_appears_near_matches():
    return _ok(_draft_appears_near("A.5.18 [NC-DRAFT] register", "A.5.18"))


def test_draft_appears_near_case_insensitive():
    return _ok(_draft_appears_near("A.5.18 (draft) register", "A.5.18"))


def test_draft_appears_near_fails_when_far():
    text = "A.5.18 is present." + " x " * 60 + "DRAFT unrelated"
    return _ok(not _draft_appears_near(text, "A.5.18", window=20))


# ── compliance_facts_footer ───────────────────────────────────────────

def test_compliance_facts_footer_includes_body_and_tag():
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    cf = make_cf(posture=posture, intent={"focus_refs": ["A.5.18"]})
    spec = extract_preservation_spec(cf)
    line = _compliance_facts_footer(["A.5.18"], spec, cf)
    return _ok(
        "A.5.18 [NC-DRAFT]" in line and "gap-A.5.18" in line,
        line,
    )


def test_compliance_facts_footer_emits_only_ref_when_no_verdict():
    """Refs without substantive posture (e.g. Art.32 that inherits)
    should still appear as bare refs — otherwise they'd silently drop."""
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32", standard_id="GDPR:2016/679")
    cf = make_cf(xfw=[art32], intent={"focus_refs": ["Art.32"]})
    spec = extract_preservation_spec(cf)
    line = _compliance_facts_footer(["Art.32"], spec, cf)
    return _ok(line.strip().endswith("Art.32"), line)


def test_compliance_facts_footer_empty_when_no_refs():
    cf = make_cf()
    spec = extract_preservation_spec(cf)
    line = _compliance_facts_footer([], spec, cf)
    return _ok(line == "")


# ── check_and_repair scenarios ────────────────────────────────────────

def _build_scenario():
    """Standard fixture: 3 primary NC/OFI, 1 xfw article. Cited: A.5.18 + Art.32."""
    posture = _posture([
        ("A.5.15", "Comply", "confirmed"),
        ("A.5.16", "OFI",    "unconfirmed"),
        ("A.5.18", "NC",     "unconfirmed"),
        ("A.5.20", "NC",     "unconfirmed"),
    ])
    art32 = N(
        node_id="GDPR:2016/679:Art.32", ref="Art.32", standard_id="GDPR:2016/679",
        xfw_edges=[
            E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15"),
            E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18"),
        ],
    )
    cf = make_cf(
        query="what is our A.5.18 status? bridges to Art.32?",
        posture=posture, xfw=[art32],
        intent={"intent_type": "posture_check", "focus_refs": ["A.5.18", "Art.32"]},
    )
    spec = extract_preservation_spec(cf)
    return cf, spec


def test_perfect_answer_no_repair():
    cf, spec = _build_scenario()
    good = (
        "A.5.18 [NC-DRAFT] register incomplete. A.5.20 [NC-DRAFT] gap. "
        "A.5.16 [OFI-DRAFT] identified. Art.32 addressed via bridges.\n\n"
        "↳ Bridges to ISO 27001 for Art.32: A.5.15 [Comply], A.5.18 [NC-DRAFT]"
    )
    r = check_and_repair(good, spec, cf)
    return _ok(not r.repaired and len(r.events) == 0, r.events)


def test_dropped_ref_produces_missing_ref_event():
    cf, spec = _build_scenario()
    r = check_and_repair("Some findings.", spec, cf)
    kinds = [e.kind for e in r.events]
    return _ok("missing_ref" in kinds and len(r.footers_added) > 0, r.events)


def test_missing_ref_appears_in_footer():
    cf, spec = _build_scenario()
    r = check_and_repair("Nothing here.", spec, cf)
    return _ok(
        "A.5.18 [NC-DRAFT]" in r.text
        and "A.5.20 [NC-DRAFT]" in r.text
        and "A.5.16 [OFI-DRAFT]" in r.text
        and "Art.32" in r.text,
        r.text,
    )


def test_missing_bridge_footer_gets_appended():
    cf, spec = _build_scenario()
    r = check_and_repair(
        "A.5.18 [NC-DRAFT] register. A.5.20 [NC-DRAFT] gap. A.5.16 [OFI-DRAFT]. Art.32 handled.",
        spec, cf,
    )
    return _ok(
        "↳ Bridges to ISO 27001 for Art.32" in r.text
        and "A.5.15 [Comply]" in r.text,
        r.text,
    )


def test_missing_draft_tag_flagged_and_repaired():
    cf, spec = _build_scenario()
    # LLM mentioned A.5.18 with NC but no DRAFT
    r = check_and_repair(
        "A.5.18 NC register incomplete. A.5.20 NC has gap. A.5.16 OFI identified. Art.32 handled.\n"
        "↳ Bridges to ISO 27001 for Art.32: A.5.15 [Comply], A.5.18 [NC-DRAFT]",
        spec, cf,
    )
    kinds = [e.kind for e in r.events]
    return _ok(
        "missing_draft_near_ref" in kinds
        and "↳ Compliance facts" in r.text
        and "A.5.18 [NC-DRAFT]" in r.text,
        r,
    )


def test_missing_verdict_flagged():
    cf, spec = _build_scenario()
    # LLM mentioned A.5.18 but no NC anywhere near it
    r = check_and_repair(
        "A.5.18 register is incomplete. A.5.20 has issues. A.5.16 too. Art.32 involved.\n"
        "↳ Bridges to ISO 27001 for Art.32: A.5.15 [Comply], A.5.18 [NC-DRAFT]",
        spec, cf,
    )
    kinds = [e.kind for e in r.events]
    return _ok("missing_verdict_near_ref" in kinds, r.events)


def test_confirmed_ref_no_draft_event():
    """A confirmed posture (Comply) shouldn't be flagged for missing DRAFT."""
    posture = _posture([("A.5.15", "Comply", "confirmed")])
    cf = make_cf(posture=posture, intent={"focus_refs": ["A.5.15"]})
    spec = extract_preservation_spec(cf)
    r = check_and_repair("A.5.15 Comply is in place.", spec, cf)
    kinds = [e.kind for e in r.events]
    return _ok(
        "missing_draft_near_ref" not in kinds
        and "missing_verdict_near_ref" not in kinds,
        r.events,
    )


def test_empty_spec_no_repair():
    cf = make_cf()
    spec = extract_preservation_spec(cf)  # empty
    r = check_and_repair("Answer with no requirements.", spec, cf)
    return _ok(r.text == "Answer with no requirements." and not r.repaired)


def test_repair_appends_no_duplicate_footer():
    """When the LLM already included the bridge footer, don't add a
    second one."""
    cf, spec = _build_scenario()
    answer_with_footer = (
        "A.5.18 [NC-DRAFT] register incomplete. A.5.20 [NC-DRAFT] gap. "
        "A.5.16 [OFI-DRAFT] identified. Art.32 addressed via bridges.\n\n"
        "↳ Bridges to ISO 27001 for Art.32: A.5.15 [Comply], A.5.18 [NC-DRAFT]"
    )
    r = check_and_repair(answer_with_footer, spec, cf)
    # Should not add another bridge footer
    return _ok(r.text.count("↳ Bridges to ISO 27001 for Art.32") == 1, r.text)


def test_repair_preserves_original_prose():
    cf, spec = _build_scenario()
    prose = "The tenant's access-rights posture has open items."
    r = check_and_repair(prose, spec, cf)
    return _ok(r.text.startswith(prose), r.text)


TESTS = [
    test_refs_in_text_finds_annex_a,
    test_refs_in_text_finds_gdpr_article,
    test_refs_in_text_finds_iso_body_clause,
    test_refs_in_text_multiple,
    test_verdict_appears_near_matches,
    test_verdict_appears_near_case_insensitive,
    test_verdict_appears_near_fails_when_far,
    test_draft_appears_near_matches,
    test_draft_appears_near_case_insensitive,
    test_draft_appears_near_fails_when_far,
    test_compliance_facts_footer_includes_body_and_tag,
    test_compliance_facts_footer_emits_only_ref_when_no_verdict,
    test_compliance_facts_footer_empty_when_no_refs,
    test_perfect_answer_no_repair,
    test_dropped_ref_produces_missing_ref_event,
    test_missing_ref_appears_in_footer,
    test_missing_bridge_footer_gets_appended,
    test_missing_draft_tag_flagged_and_repaired,
    test_missing_verdict_flagged,
    test_confirmed_ref_no_draft_event,
    test_empty_spec_no_repair,
    test_repair_appends_no_duplicate_footer,
    test_repair_preserves_original_prose,
]


def main():
    print("─" * 70)
    print("  check_and_repair tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok = False
            msg = f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
