"""
Unit tests for Ship 129'.c — chat xfw bridge footer + digest respect
tenant framework enrolment.

Locks:
  - CaseFile.is_ref_enrolled() true/false via posture standard_id lookup
  - Fail-open when scope_standards is empty (unknown scope → widen)
  - _render_xfw_bridges drops entries whose xfw_ref is non-enrolled
  - _build_bridge_footer returns None when all bridges are non-enrolled

No DB needed — CaseFile is constructed with hand-built posture + tenant
scope. See [[feedback-discovery-vs-surfacing-separation]].

Run:
    PYTHONPATH=/data/arioncomply python3 tests/test_casefile_enrolment_filter.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.casefile.types import CaseFile  # noqa: E402
from rag.casefile.digest import _render_xfw_bridges  # noqa: E402
from rag.casefile.preservation import _build_bridge_footer  # noqa: E402


def _make_edge(source_id: str, target_id: str, rel_type: str = "IMPLEMENTS"):
    return SimpleNamespace(
        source_id = source_id,
        target_id = target_id,
        rel_type  = rel_type,
    )


def _make_node(ref: str, standard_id: str, xfw_edges: list = None):
    """Minimal graph-node stub with real xfw_edges dataclass shape."""
    return SimpleNamespace(
        node_id            = f"{standard_id}:{ref}",
        ref                = ref,
        standard_id        = standard_id,
        title              = f"Test {ref}",
        description        = "",
        is_informational   = False,
        xfw_edges          = xfw_edges or [],
    )


def _make_casefile(enrolled: list[str], primary_ref: str, primary_std: str,
                   primary_finding: str, xfw_ref: str, xfw_std: str,
                   query: str = "what about our controls",
                   cited_refs: list[str] = None) -> CaseFile:
    """Build a CaseFile with one primary node (posture=finding) that
    bridges to one xfw_ref in xfw_std."""
    tenant = SimpleNamespace(
        tenant_name = "Test Tenant",
        tenant_id   = "00000000-0000-0000-0000-000000000042",
        scope       = SimpleNamespace(queryable_standards=list(enrolled)),
    )
    primary_nid = f"{primary_std}:{primary_ref}"
    xfw_nid     = f"{xfw_std}:{xfw_ref}"
    edge = _make_edge(source_id=primary_nid, target_id=xfw_nid)
    primary_node = _make_node(primary_ref, primary_std, xfw_edges=[edge])
    xfw_node     = _make_node(xfw_ref, xfw_std, xfw_edges=[edge])
    resolved = SimpleNamespace(
        graph_nodes = SimpleNamespace(
            primary_nodes   = [primary_node],
            secondary_nodes = [],
            xfw_nodes       = [xfw_node],
        ),
        posture_nodes = {
            primary_nid: {
                "control_ref":          primary_ref,
                "standard_id":          primary_std,
                "finding":              primary_finding,
                "gap_description":      "",
                "confirmation_status":  "confirmed",
                "applicability_status": "in_scope",
            },
        },
        cited_refs = cited_refs or [primary_ref],
        query      = query,
    )
    intent = SimpleNamespace(
        question_type   = SimpleNamespace(value="posture_check"),
        intent_type     = "posture_check",
        cited_refs      = cited_refs or [primary_ref],
        clarify_pending = False,
    )
    return CaseFile(
        query    = query,
        intent   = intent,
        resolved = resolved,
        tenant   = tenant,
    )


# ── is_ref_enrolled predicate ────────────────────────────────────────────

def test_is_ref_enrolled_true_when_standard_enrolled():
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    assert cf.is_ref_enrolled("A.5.15") is True


def test_is_ref_enrolled_false_when_standard_not_enrolled():
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    assert cf.is_ref_enrolled("Art.32") is False


def test_is_ref_enrolled_fail_open_when_scope_empty():
    """When queryable_standards is empty (scope unknown), predicate
    returns True — matches Ship 66'.a widening fallback."""
    cf = _make_casefile(
        enrolled       = [],   # unknown scope
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    assert cf.is_ref_enrolled("Art.32") is True
    assert cf.is_ref_enrolled("Art.99") is True


def test_is_ref_enrolled_fail_open_when_ref_standard_unknown():
    """When the ref can't be resolved to any standard, predicate returns
    True — never silently censor content whose provenance we can't check."""
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    assert cf.is_ref_enrolled("NoSuchRef.42") is True


# ── digest _render_xfw_bridges ───────────────────────────────────────────

def test_render_xfw_bridges_drops_non_enrolled_target():
    """Bridge target in a non-enrolled standard → line omitted from the
    LLM digest."""
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    out = _render_xfw_bridges(cf)
    assert "Art.32" not in out, \
        f"non-enrolled Art.32 leaked into digest bridges section:\n{out}"


def test_render_xfw_bridges_keeps_enrolled_target():
    """Sanity check: if the target IS enrolled, the line renders."""
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022", "GDPR:2016/679"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
    )
    out = _render_xfw_bridges(cf)
    assert "Art.32" in out, \
        f"enrolled Art.32 was filtered out even though enrolled:\n{out!r}"


# ── preservation _build_bridge_footer ────────────────────────────────────

def test_build_bridge_footer_returns_none_when_all_bridges_non_enrolled():
    """User queries Art.32 (non-enrolled). Preservation footer should
    NOT reintroduce the ref that framework_scope_guard would have
    stripped."""
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
        cited_refs     = ["Art.32"],
        query          = "how do we cover Art.32?",
    )
    footer, refs = _build_bridge_footer(cf)
    assert footer is None, \
        f"footer emitted despite non-enrolled xfw target: {footer!r}"


def test_build_bridge_footer_fires_when_enrolled():
    """Sanity: when GDPR IS enrolled, the footer bridges as normal."""
    cf = _make_casefile(
        enrolled       = ["ISO27001:2022", "GDPR:2016/679"],
        primary_ref    = "A.5.15", primary_std = "ISO27001:2022",
        primary_finding= "Comply",
        xfw_ref        = "Art.32", xfw_std     = "GDPR:2016/679",
        cited_refs     = ["Art.32"],
        query          = "how do we cover Art.32?",
    )
    footer, refs = _build_bridge_footer(cf)
    assert footer is not None
    assert "Art.32" in footer
    assert "A.5.15" in footer


# ── Runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("is_ref_enrolled True when standard enrolled",
         test_is_ref_enrolled_true_when_standard_enrolled),
        ("is_ref_enrolled False when standard not enrolled",
         test_is_ref_enrolled_false_when_standard_not_enrolled),
        ("is_ref_enrolled fail-open when scope empty",
         test_is_ref_enrolled_fail_open_when_scope_empty),
        ("is_ref_enrolled fail-open when ref standard unknown",
         test_is_ref_enrolled_fail_open_when_ref_standard_unknown),
        ("_render_xfw_bridges drops non-enrolled target",
         test_render_xfw_bridges_drops_non_enrolled_target),
        ("_render_xfw_bridges keeps enrolled target",
         test_render_xfw_bridges_keeps_enrolled_target),
        ("_build_bridge_footer None when all bridges non-enrolled",
         test_build_bridge_footer_returns_none_when_all_bridges_non_enrolled),
        ("_build_bridge_footer fires when enrolled",
         test_build_bridge_footer_fires_when_enrolled),
    ]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}\n      {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"ERROR {name}\n      {type(e).__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{passed + failed} PASS")
    sys.exit(0 if failed == 0 else 1)
