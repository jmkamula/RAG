"""
Tests for rag/casefile/types.CaseFile — the ground-truth wrapper
that Ship 2' will feed into the digest + preservation flow.

Standalone script — matches the project's pytest-free test style.
Run:  PYTHONPATH=/data/arioncomply python3 tests/casefile/test_types.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from rag.casefile import CaseFile


# ── Test fixtures ─────────────────────────────────────────────────────

@dataclass
class FakeEdge:
    source_id: str
    target_id: str
    rel_type:  str = "IMPLEMENTS"


@dataclass
class FakeNode:
    node_id:      str
    ref:          str
    standard_id:  str = "ISO27001:2022"
    title:        str = ""
    xfw_edges:    list = field(default_factory=list)
    is_informational: bool = False


@dataclass
class FakeGraph:
    primary_nodes:    list = field(default_factory=list)
    secondary_nodes:  list = field(default_factory=list)
    xfw_nodes:        list = field(default_factory=list)
    doc_contexts:     dict = field(default_factory=dict)
    xfw_edges:        list = field(default_factory=list)


@dataclass
class FakeResolved:
    posture_nodes:  dict = field(default_factory=dict)
    graph_nodes:    Any = None


@dataclass
class FakeScope:
    queryable_standards: list = field(default_factory=list)


@dataclass
class FakeTenant:
    tenant_name: str = ""
    tenant_id:   str = ""
    scope:       Any = None


@dataclass
class FakeSession:
    active_refs:    list = field(default_factory=list)
    active_cluster: str = ""


def make_case(
    query="test",
    posture=None,
    primary=None,
    xfw=None,
    docs=None,
    tenant=None,
    session=None,
    intent=None,
):
    gn = FakeGraph(
        primary_nodes = list(primary or []),
        xfw_nodes     = list(xfw or []),
        doc_contexts  = dict(docs or {}),
    )
    return CaseFile(
        query    = query,
        intent   = intent,
        resolved = FakeResolved(
            posture_nodes = dict(posture or {}),
            graph_nodes   = gn,
        ),
        tenant   = tenant,
        session  = session,
    )


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Tests ─────────────────────────────────────────────────────────────

def test_empty_casefile_returns_defaults():
    cf = CaseFile(query="", intent=None, resolved=FakeResolved())
    return _ok(
        cf.tenant_name == ""
        and cf.tenant_id == ""
        and cf.scope_standards == []
        and cf.question_type == "unknown"
        and cf.cited_refs == []
        and cf.active_session_refs == []
        and cf.active_cluster is None
        and cf.primary_nodes() == []
        and cf.xfw_nodes() == []
        and cf.posture_nodes == {}
        and cf.posture_by_ref() == {}
        and cf.posture_for("A.5.18") is None
        and cf.is_assessed("A.5.18") is False
        and cf.needs_draft_tag("A.5.18") is False
        and cf.xfw_bridges() == {}
        and cf.doc_contexts == {}
        and cf.doc_refs() == []
        and cf.incidents == []
    )


def test_none_graph_nodes_does_not_crash():
    cf = CaseFile(
        query="q", intent=None,
        resolved=FakeResolved(posture_nodes={}, graph_nodes=None),
    )
    return _ok(
        cf.primary_nodes() == []
        and cf.xfw_nodes() == []
        and cf.xfw_bridges() == {}
    )


def test_posture_by_ref_reindexes_from_control_ref():
    posture = {
        "ISO27001:2022:A.5.18": {
            "finding": "NC", "gap_description": "x",
            "control_ref": "A.5.18", "confirmation_status": "unconfirmed",
        },
        "ISO27001:2022:A.5.15": {
            "finding": "Comply", "evidence_text": "y",
            "control_ref": "A.5.15", "confirmation_status": "confirmed",
        },
    }
    cf = make_case(posture=posture)
    idx = cf.posture_by_ref()
    return _ok(
        set(idx.keys()) == {"A.5.18", "A.5.15"}
        and idx["A.5.18"]["finding"] == "NC",
        f"got {list(idx.keys())}",
    )


def test_posture_by_ref_falls_back_to_node_id_suffix():
    posture = {"GDPR:2016/679:Art.32": {"finding": "OFI"}}
    cf = make_case(posture=posture)
    return _ok("Art.32" in cf.posture_by_ref())


def test_is_assessed_and_needs_draft_tag():
    posture = {
        "ISO27001:2022:A.5.18": {"finding": "NC",     "control_ref": "A.5.18", "confirmation_status": "unconfirmed"},
        "ISO27001:2022:A.5.15": {"finding": "Comply", "control_ref": "A.5.15", "confirmation_status": "confirmed"},
        "ISO27001:2022:A.5.19": {"finding": "N/A",    "control_ref": "A.5.19", "confirmation_status": "confirmed"},
    }
    cf = make_case(posture=posture)
    return _ok(
        cf.is_assessed("A.5.18") and cf.needs_draft_tag("A.5.18")
        and cf.is_assessed("A.5.15") and not cf.needs_draft_tag("A.5.15")
        and not cf.is_assessed("A.5.19") and not cf.needs_draft_tag("A.5.19")
        and not cf.is_assessed("A.999")
    )


def test_needs_draft_tag_recognises_all_confirmed_states():
    posture = {
        f"ISO27001:2022:A.5.{i}": {
            "finding": "NC",
            "control_ref": f"A.5.{i}",
            "confirmation_status": state,
        }
        for i, state in enumerate(
            ["confirmed", "overridden", "document_confirmed", "engine_confirmed"],
            start=1,
        )
    }
    cf = make_case(posture=posture)
    return _ok(all(not cf.needs_draft_tag(f"A.5.{i}") for i in range(1, 5)))


def test_xfw_bridges_derive_from_edges():
    art32 = FakeNode(
        node_id="GDPR:2016/679:Art.32", ref="Art.32",
        standard_id="GDPR:2016/679",
        xfw_edges=[
            FakeEdge("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15"),
            FakeEdge("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18"),
        ],
    )
    cf = make_case(xfw=[art32])
    bridges = cf.xfw_bridges()
    return _ok(bridges == {"Art.32": ["A.5.15", "A.5.18"]}, f"got {bridges}")


def test_xfw_bridges_handle_reverse_edge_direction():
    """Edges can point IN — bridges take the *other* end either way."""
    art32 = FakeNode(
        node_id="GDPR:2016/679:Art.32", ref="Art.32",
        standard_id="GDPR:2016/679",
        xfw_edges=[FakeEdge("ISO27001:2022:A.5.15", "GDPR:2016/679:Art.32")],
    )
    cf = make_case(xfw=[art32])
    return _ok(cf.xfw_bridges() == {"Art.32": ["A.5.15"]})


def test_xfw_bridges_skip_unlinked_nodes():
    art32 = FakeNode(
        node_id="GDPR:2016/679:Art.32", ref="Art.32",
        standard_id="GDPR:2016/679", xfw_edges=[],
    )
    cf = make_case(xfw=[art32])
    return _ok(cf.xfw_bridges() == {})


def test_informational_nodes_are_excluded():
    good = FakeNode(node_id="X:1", ref="A.5.18")
    info = FakeNode(node_id="X:2", ref="A.5.19", is_informational=True)
    cf = make_case(primary=[good, info])
    refs = [n.ref for n in cf.primary_nodes()]
    return _ok(refs == ["A.5.18"], f"got {refs}")


def test_active_session_refs_and_cluster():
    session = FakeSession(active_refs=["A.5.18", "A.5.15"], active_cluster="access")
    cf = make_case(session=session)
    return _ok(
        cf.active_session_refs == ["A.5.18", "A.5.15"]
        and cf.active_cluster == "access"
    )


def test_tenant_and_scope_read_through():
    tenant = FakeTenant(
        tenant_name="Arion Networks",
        tenant_id="uuid-1",
        scope=FakeScope(queryable_standards=["ISO27001:2022", "GDPR:2016/679"]),
    )
    cf = make_case(tenant=tenant)
    return _ok(
        cf.tenant_name == "Arion Networks"
        and cf.tenant_id == "uuid-1"
        and cf.scope_standards == ["ISO27001:2022", "GDPR:2016/679"]
    )


def test_tenant_without_scope_returns_empty_standards():
    tenant = FakeTenant(tenant_name="X", scope=None)
    cf = make_case(tenant=tenant)
    return _ok(cf.scope_standards == [])


def test_intent_dict_shape():
    cf = CaseFile(
        query="q",
        intent={"intent_type": "posture_check", "focus_refs": ["A.5.18", "A.5.15"]},
        resolved=FakeResolved(),
    )
    return _ok(
        cf.question_type == "posture_check"
        and cf.cited_refs == ["A.5.18", "A.5.15"]
    )


def test_intent_dataclass_with_enum_qt():
    class QT:
        value = "gap_analysis"

    @dataclass
    class FakeIntent:
        question_type: Any = None
        cited_refs:    list = field(default_factory=list)

    cf = CaseFile(
        query="q",
        intent=FakeIntent(question_type=QT(), cited_refs=["A.5.18"]),
        resolved=FakeResolved(),
    )
    return _ok(cf.question_type == "gap_analysis" and cf.cited_refs == ["A.5.18"])


def test_doc_refs_from_doc_contexts():
    @dataclass
    class FakeDoc:
        control_ref: str
    cf = make_case(docs={"n1": FakeDoc("A.5.15"), "n2": FakeDoc("A.5.18")})
    return _ok(set(cf.doc_refs()) == {"A.5.15", "A.5.18"})


def test_summary_shape():
    posture = {
        "ISO27001:2022:A.5.18": {"finding": "NC",     "control_ref": "A.5.18"},
        "ISO27001:2022:A.5.15": {"finding": "Comply", "control_ref": "A.5.15"},
        "ISO27001:2022:A.5.19": {"finding": "N/A",    "control_ref": "A.5.19"},
        "ISO27001:2022:A.5.20": {"finding": "",       "control_ref": "A.5.20"},
    }
    art32 = FakeNode(
        node_id="GDPR:2016/679:Art.32", ref="Art.32",
        standard_id="GDPR:2016/679",
        xfw_edges=[FakeEdge("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15")],
    )
    cf = make_case(query="q", posture=posture, xfw=[art32])
    s = cf.summary()
    return _ok(
        s["posture_counts"]["NC"] == 1
        and s["posture_counts"]["Comply"] == 1
        and s["posture_counts"]["N/A"] == 1
        and s["posture_counts"]["unassessed"] == 1
        and s["xfw_nodes"] == 1
        and s["xfw_bridges"] == 1,
        f"got {s}",
    )


TESTS = [
    test_empty_casefile_returns_defaults,
    test_none_graph_nodes_does_not_crash,
    test_posture_by_ref_reindexes_from_control_ref,
    test_posture_by_ref_falls_back_to_node_id_suffix,
    test_is_assessed_and_needs_draft_tag,
    test_needs_draft_tag_recognises_all_confirmed_states,
    test_xfw_bridges_derive_from_edges,
    test_xfw_bridges_handle_reverse_edge_direction,
    test_xfw_bridges_skip_unlinked_nodes,
    test_informational_nodes_are_excluded,
    test_active_session_refs_and_cluster,
    test_tenant_and_scope_read_through,
    test_tenant_without_scope_returns_empty_standards,
    test_intent_dict_shape,
    test_intent_dataclass_with_enum_qt,
    test_doc_refs_from_doc_contexts,
    test_summary_shape,
]


# ── Ship 2'.i: role-aware accessors (framework-role-model-arc) ───────

@dataclass
class FakeStandardInfo:
    id: str
    role: str = ""


@dataclass
class FakeRoleScope:
    programs:    list = field(default_factory=list)
    extensions:  list = field(default_factory=list)
    obligations: list = field(default_factory=list)
    queryable_standards: list = field(default_factory=list)


def _tenant_with_role_scope():
    return FakeTenant(
        tenant_name="Arion Networks",
        tenant_id="uuid-1",
        scope=FakeRoleScope(
            programs   = [FakeStandardInfo(id="ISO27001:2022")],
            extensions = [FakeStandardInfo(id="ISO27701:2019")],
            obligations= [FakeStandardInfo(id="GDPR:2016/679")],
        ),
    )


def test_role_map_reads_scope_groupings():
    cf = make_case(tenant=_tenant_with_role_scope())
    rmap = cf._role_map()
    return _ok(
        rmap.get("ISO27001:2022") == "program"
        and rmap.get("ISO27701:2019") == "extension"
        and rmap.get("GDPR:2016/679") == "obligation",
        f"got {rmap}",
    )


def test_role_of_uses_node_standard_id():
    n = FakeNode(node_id="GDPR:2016/679:Art.32", ref="Art.32",
                 standard_id="GDPR:2016/679")
    cf = make_case(primary=[n], tenant=_tenant_with_role_scope())
    return _ok(cf.role_of("Art.32") == "obligation")


def test_role_of_falls_back_to_posture_record():
    """When the ref isn't on a graph node but IS in the posture dict,
    fall back to posture record's standard_id."""
    posture = {
        "GDPR:2016/679:Art.32": {
            "finding": "NC", "control_ref": "Art.32",
            "standard_id": "GDPR:2016/679",
        }
    }
    cf = make_case(posture=posture, tenant=_tenant_with_role_scope())
    return _ok(cf.role_of("Art.32") == "obligation")


def test_role_of_none_when_off_scope():
    cf = make_case(tenant=_tenant_with_role_scope())
    return _ok(cf.role_of("NIST-CSF.PR-1") is None)


def test_demonstrated_by_reads_posture_field():
    posture = {
        "GDPR:2016/679:Art.32": {
            "finding": "NC",
            "control_ref": "Art.32",
            "demonstrated_by": [
                {"src_id": "ISO27001:2022:A.5.15",
                 "src_std": "ISO27001:2022",
                 "via_edge": "IMPLEMENTS",
                 "finding": "NC",
                 "strength": "high"},
            ],
        }
    }
    cf = make_case(posture=posture, tenant=_tenant_with_role_scope())
    sources = cf.demonstrated_by("Art.32")
    return _ok(
        len(sources) == 1
        and sources[0]["src_id"] == "ISO27001:2022:A.5.15",
    )


def test_demonstrated_by_empty_when_no_field():
    posture = {"ISO27001:2022:A.5.18": {"finding": "NC", "control_ref": "A.5.18"}}
    cf = make_case(posture=posture, tenant=_tenant_with_role_scope())
    return _ok(cf.demonstrated_by("A.5.18") == [])


def test_obligations_of_role_program():
    """Return only nodes owned by program-role standards."""
    iso = FakeNode(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
                   standard_id="ISO27001:2022")
    gdpr = FakeNode(node_id="GDPR:2016/679:Art.32", ref="Art.32",
                    standard_id="GDPR:2016/679")
    ext = FakeNode(node_id="ISO27701:2019:A.7.2.5", ref="A.7.2.5",
                   standard_id="ISO27701:2019")
    cf = make_case(primary=[iso, gdpr, ext], tenant=_tenant_with_role_scope())
    program_refs = [n.ref for n in cf.obligations_of_role("program")]
    return _ok(program_refs == ["A.5.18"], program_refs)


def test_all_nodes_pools_and_dedupes():
    """all_nodes should union primary + secondary + xfw and dedupe."""
    # duplicate on node_id: same node in two buckets
    n1 = FakeNode(node_id="ISO27001:2022:A.5.18", ref="A.5.18")
    n2 = FakeNode(node_id="ISO27001:2022:A.5.15", ref="A.5.15")
    gn = FakeGraph(
        primary_nodes=[n1, n2],
        secondary_nodes=[n1],       # dup
        xfw_nodes=[],
    )
    cf = CaseFile(
        query="q", intent=None,
        resolved=FakeResolved(posture_nodes={}, graph_nodes=gn),
    )
    refs = [n.ref for n in cf.all_nodes()]
    return _ok(refs == ["A.5.18", "A.5.15"], refs)


TESTS = TESTS + [
    test_role_map_reads_scope_groupings,
    test_role_of_uses_node_standard_id,
    test_role_of_falls_back_to_posture_record,
    test_role_of_none_when_off_scope,
    test_demonstrated_by_reads_posture_field,
    test_demonstrated_by_empty_when_no_field,
    test_obligations_of_role_program,
    test_all_nodes_pools_and_dedupes,
]


def main():
    print("─" * 70)
    print("  CaseFile dataclass tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            import traceback
            ok, msg = False, f"raised {type(e).__name__}: {e}\n{traceback.format_exc()}"
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
