"""
Tests for rag/casefile/preservation.py — the MUST-preserve extractor.
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
    PreservationSpec,
    extract_preservation_spec,
    _required_refs,
    _has_data_in_casefile,
    _build_bridge_footer,
    _extract_article_refs,
    _REQUIRED_TOP_N,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@dataclass
class E:
    source_id: str
    target_id: str
    rel_type:  str = "IMPLEMENTS"


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


def make_cf(
    query="q",
    posture=None,
    primary=None,
    xfw=None,
    intent=None,
    session=None,
):
    return CaseFile(
        query=query, intent=intent,
        resolved=R(
            posture_nodes=dict(posture or {}),
            graph_nodes=G(
                primary_nodes=list(primary or []),
                xfw_nodes=list(xfw or []),
            ),
        ),
        session=session,
    )


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── _has_data_in_casefile ─────────────────────────────────────────────

def test_has_data_matches_posture():
    cf = make_cf(posture=_posture([("A.5.18", "NC", "unconfirmed")]))
    return _ok(
        _has_data_in_casefile(cf, "A.5.18")
        and not _has_data_in_casefile(cf, "A.5.99")
    )


def test_has_data_matches_primary_node():
    cf = make_cf(primary=[N(node_id="X:1", ref="A.5.18")])
    return _ok(_has_data_in_casefile(cf, "A.5.18"))


def test_has_data_matches_xfw_node():
    cf = make_cf(xfw=[N(node_id="X:1", ref="Art.32", standard_id="GDPR:2016/679")])
    return _ok(_has_data_in_casefile(cf, "Art.32"))


# ── _required_refs ────────────────────────────────────────────────────

def test_required_refs_includes_cited_with_data():
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    cf = make_cf(
        posture=posture,
        intent={"intent_type": "posture_check", "focus_refs": ["A.5.18"]},
    )
    refs = _required_refs(cf)
    return _ok("A.5.18" in refs, refs)


def test_required_refs_excludes_cited_without_data():
    """A cited ref with no data should NOT be forced into the answer.
    The extractor filters cited_refs by _has_data_in_casefile."""
    cf = make_cf(
        posture={},
        primary=[],
        xfw=[],
        intent={"intent_type": "posture_check", "focus_refs": ["A.5.99"]},
    )
    refs = _required_refs(cf)
    return _ok("A.5.99" not in refs, refs)


def test_required_refs_takes_top_n_from_ranking():
    """Even without cited refs, top-3 posture entries enter required_refs."""
    posture = _posture([
        (f"A.5.{i}", "NC", "unconfirmed") for i in range(1, 6)
    ])
    cf = make_cf(posture=posture)
    refs = _required_refs(cf)
    # top 3 NCs — but at least 3 refs should be present
    return _ok(len(refs) >= 3 and len(refs) <= _REQUIRED_TOP_N + 0, refs)


def test_required_refs_union_cited_and_top_n():
    """cited_refs + top-N union. The ranker puts cited refs at
    position 1, so top-N includes them — the union size is
    max(len(cited), _REQUIRED_TOP_N) with cited guaranteed present."""
    posture = _posture([
        ("A.5.18", "OFI", "unconfirmed"),
        ("A.5.15", "NC",  "unconfirmed"),
        ("A.5.16", "NC",  "unconfirmed"),
        ("A.5.17", "NC",  "unconfirmed"),
    ])
    cf = make_cf(
        posture=posture,
        intent={"intent_type": "gap_analysis", "focus_refs": ["A.5.18"]},
    )
    refs = _required_refs(cf)
    # Cited A.5.18 present + at least 2 NCs from ranker's top-3
    return _ok(
        "A.5.18" in refs
        and len(refs & {"A.5.15", "A.5.16", "A.5.17"}) >= 2
        and len(refs) == _REQUIRED_TOP_N,
        f"got {refs}",
    )


# ── Bridge footer builder ─────────────────────────────────────────────

def test_extract_article_refs_from_cited():
    cf = make_cf(intent={"intent_type": "cross_framework", "focus_refs": ["Art.32", "A.5.18"]})
    refs = _extract_article_refs(cf)
    return _ok(refs == ["Art.32"], refs)


def test_extract_article_refs_from_query_when_no_cited():
    cf = make_cf(query="tell me about Art.5.1 and Art.32")
    refs = _extract_article_refs(cf)
    return _ok("Art.32" in refs and any("Art.5" in r for r in refs), refs)


def test_bridge_footer_fires_when_article_and_xfw():
    posture = _posture([
        ("A.5.15", "Comply", "confirmed"),
        ("A.5.18", "NC",     "unconfirmed"),
    ])
    art32 = N(
        node_id="GDPR:2016/679:Art.32", ref="Art.32",
        standard_id="GDPR:2016/679",
        xfw_edges=[
            E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15"),
            E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18"),
        ],
    )
    cf = make_cf(
        posture=posture, xfw=[art32],
        intent={"intent_type": "cross_framework", "focus_refs": ["Art.32"]},
    )
    footer, article_refs = _build_bridge_footer(cf)
    return _ok(
        footer is not None
        and "Art.32" in footer
        and "A.5.15 [Comply]" in footer
        and "A.5.18 [NC-DRAFT]" in footer
        and article_refs == ["Art.32"],
        footer,
    )


def test_bridge_footer_no_article_no_footer():
    posture = _posture([("A.5.15", "Comply", "confirmed")])
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15")])
    cf = make_cf(posture=posture, xfw=[art32])   # no Art.32 in cited or query
    footer, refs = _build_bridge_footer(cf)
    return _ok(footer is None and refs == [])


def test_bridge_footer_no_xfw_no_footer():
    cf = make_cf(intent={"intent_type": "cross_framework", "focus_refs": ["Art.32"]})
    footer, refs = _build_bridge_footer(cf)
    return _ok(footer is None)


def test_bridge_footer_uses_confirmed_state_no_draft():
    posture = _posture([("A.5.15", "Comply", "confirmed")])
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15")])
    cf = make_cf(
        posture=posture, xfw=[art32],
        intent={"intent_type": "cross_framework", "focus_refs": ["Art.32"]},
    )
    footer, _ = _build_bridge_footer(cf)
    return _ok(
        footer is not None and "[Comply]" in footer and "-DRAFT" not in footer,
        footer,
    )


# ── extract_preservation_spec end-to-end ──────────────────────────────

def test_extract_produces_all_fields():
    posture = _posture([
        ("A.5.15", "Comply", "confirmed"),
        ("A.5.16", "OFI",    "unconfirmed"),
        ("A.5.18", "NC",     "unconfirmed"),
    ])
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18")])
    cf = make_cf(
        posture=posture, xfw=[art32],
        intent={"intent_type": "posture_check", "focus_refs": ["A.5.18", "Art.32"]},
    )
    spec = extract_preservation_spec(cf)
    return _ok(
        "A.5.18" in spec.required_refs
        and "Art.32" in spec.required_refs
        and "A.5.18" in spec.draft_refs
        and "A.5.15" not in spec.draft_refs  # confirmed
        and spec.verdict_by_ref["A.5.18"] == "NC"
        and spec.verdict_by_ref["A.5.16"] == "OFI"
        and spec.bridge_footer is not None
        and spec.bridge_article_refs == ["Art.32"]
    )


def test_extract_is_empty_when_no_data():
    cf = make_cf()
    spec = extract_preservation_spec(cf)
    return _ok(spec.is_empty(), spec)


def test_extract_only_verdicts_for_posture_refs():
    """Cited Art.32 has no direct posture — should be in required_refs
    but NOT in verdict_by_ref (article inherits via bridges)."""
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679")
    cf = make_cf(
        xfw=[art32],
        intent={"intent_type": "cross_framework", "focus_refs": ["Art.32"]},
    )
    spec = extract_preservation_spec(cf)
    return _ok(
        "Art.32" in spec.required_refs
        and "Art.32" not in spec.verdict_by_ref
    )


TESTS = [
    test_has_data_matches_posture,
    test_has_data_matches_primary_node,
    test_has_data_matches_xfw_node,
    test_required_refs_includes_cited_with_data,
    test_required_refs_excludes_cited_without_data,
    test_required_refs_takes_top_n_from_ranking,
    test_required_refs_union_cited_and_top_n,
    test_extract_article_refs_from_cited,
    test_extract_article_refs_from_query_when_no_cited,
    test_bridge_footer_fires_when_article_and_xfw,
    test_bridge_footer_no_article_no_footer,
    test_bridge_footer_no_xfw_no_footer,
    test_bridge_footer_uses_confirmed_state_no_draft,
    test_extract_produces_all_fields,
    test_extract_is_empty_when_no_data,
    test_extract_only_verdicts_for_posture_refs,
]


def main():
    print("─" * 70)
    print("  Preservation extractor tests")
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
