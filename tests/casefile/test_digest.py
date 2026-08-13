"""
Tests for rag/casefile/digest.py — the compact prompt renderer.

Verifies:
  - Section structure (fixed slots, empty sections omitted)
  - Posture ranking (cited > session > NC > OFI > Comply)
  - Verdict tags with [DRAFT] where required
  - xfw bridges rendered with inherited postures
  - Deictic hint fires only when deictic + no last_entity
  - Token budgets stay under 2000 for realistic cases

Run: PYTHONPATH=/data/arioncomply python3 tests/casefile/test_digest.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from rag.casefile import CaseFile
from rag.casefile.digest import (
    approx_tokens,
    build_prompt_digest,
    build_prompt_pair,
    build_system_prompt,
    _rank_posture_refs,
    _render_posture,
    _render_query,
    _render_xfw_bridges,
    _render_obligations,
    _render_documents,
    _render_session,
    _render_scope,
    _render_deictic_hint,
    _verdict_tag,
    _posture_line,
    _plan_for,
    _sanitize_gap_text,
)


# ── Test fixtures ─────────────────────────────────────────────────────

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


@dataclass
class Sc:
    queryable_standards: list = field(default_factory=list)


@dataclass
class T:
    tenant_name: str = "Arion Networks"
    tenant_id:   str = "uuid-1"
    scope:       Any = None


@dataclass
class Sess:
    active_refs:    list = field(default_factory=list)
    active_cluster: str = ""


@dataclass
class Doc:
    control_ref:    str
    title:          str = ""
    node_id:        str = ""
    evidence_type:  str = "policy"
    trigger_type:   str = "universal"
    description:    str = ""
    must_contain:   list = field(default_factory=list)
    should_contain: list = field(default_factory=list)

    @property
    def missing_must(self):
        return [i for i in self.must_contain
                if getattr(i, "status", None) in (None, "missing")]

    @property
    def present_must(self):
        return [i for i in self.must_contain
                if getattr(i, "status", None) == "present"]

    @property
    def has_document_uploaded(self):
        return any(getattr(i, "status", None) is not None for i in self.must_contain)


@dataclass
class Item:
    text:   str
    status: Any = None


def _posture(items):
    """items = list of (ref, finding, confirmation_status)."""
    return {
        f"ISO27001:2022:{ref}": {
            "finding": f,
            "gap_description": f"gap for {ref}",
            "evidence_text":   f"evidence for {ref}",
            "control_ref":     ref,
            "confirmation_status": cs,
        }
        for ref, f, cs in items
    }


def make_cf(
    query="test",
    posture=None,
    primary=None,
    xfw=None,
    docs=None,
    tenant=None,
    session=None,
    intent=None,
    last_entity=None,
    incidents=None,
):
    gn = G(
        primary_nodes = list(primary or []),
        xfw_nodes     = list(xfw or []),
        doc_contexts  = dict(docs or {}),
    )
    return CaseFile(
        query    = query,
        intent   = intent,
        resolved = R(
            posture_nodes = dict(posture or {}),
            graph_nodes   = gn,
        ),
        tenant   = tenant or T(scope=Sc(queryable_standards=["ISO27001:2022"])),
        session  = session,
        last_entity = last_entity,
        incidents   = list(incidents or []),
    )


def _ok(cond, msg=""):
    return (bool(cond), msg or "ok")


# ── Verdict-tag primitive ─────────────────────────────────────────────

def test_verdict_tag_variants():
    return _ok(
        _verdict_tag("NC", False) == "[NC]"
        and _verdict_tag("NC", True) == "[NC-DRAFT]"
        and _verdict_tag("OFI", False) == "[OFI]"
        and _verdict_tag("Comply", True) == "[Comply-DRAFT]"
        and _verdict_tag("", False) == ""
        and _verdict_tag("", True) == ""
    )


# ── Posture line ──────────────────────────────────────────────────────

def test_posture_line_nc_uses_gap():
    rec = {"finding": "NC", "gap_description": "register incomplete"}
    line = _posture_line("A.5.18", rec, draft=True)
    return _ok(line == "- A.5.18 [NC-DRAFT] register incomplete", line)


def test_posture_line_comply_uses_evidence():
    rec = {"finding": "Comply", "evidence_text": "policy in place"}
    line = _posture_line("A.5.15", rec, draft=False)
    return _ok(line == "- A.5.15 [Comply] policy in place", line)


def test_posture_line_truncates_long_body():
    rec = {"finding": "NC", "gap_description": "x" * 300}
    line = _posture_line("A.5.18", rec, draft=False, max_body_chars=50)
    body = line.split("] ", 1)[1]
    return _ok(
        len(body) <= 50 and body.endswith("…"),
        f"body='{body}' len={len(body)}",
    )


def test_posture_line_collapses_whitespace():
    rec = {"finding": "NC", "gap_description": "line1\n\n\n  line2\t\ttab"}
    line = _posture_line("A.5.18", rec, draft=False)
    return _ok(
        "\n" not in line and "\t" not in line and "  " not in line,
        line,
    )


def test_posture_line_no_body_no_dash():
    rec = {"finding": "NC"}
    line = _posture_line("A.5.18", rec, draft=False)
    return _ok(line == "- A.5.18 [NC]", line)


# ── Ranking: cited > session > NC > OFI > Comply ──────────────────────

def test_ranking_cited_first():
    posture = _posture([
        ("A.5.18", "OFI", "unconfirmed"),
        ("A.5.15", "NC",  "unconfirmed"),
    ])
    cf = make_cf(
        posture=posture,
        intent={"intent_type": "gap_analysis", "focus_refs": ["A.5.18"]},
    )
    refs = _rank_posture_refs(cf, limit=5)
    # A.5.18 (cited OFI) must precede A.5.15 (NC not cited)
    return _ok(refs == ["A.5.18", "A.5.15"], f"got {refs}")


def test_ranking_session_before_findings():
    posture = _posture([
        ("A.5.18", "OFI", "unconfirmed"),
        ("A.5.15", "NC",  "unconfirmed"),
        ("A.5.16", "NC",  "unconfirmed"),
    ])
    cf = make_cf(
        posture=posture,
        session=Sess(active_refs=["A.5.18"]),
    )
    refs = _rank_posture_refs(cf, limit=5)
    # A.5.18 (session OFI) first, then NC, NC
    return _ok(refs[0] == "A.5.18" and set(refs[1:]) == {"A.5.15", "A.5.16"}, f"got {refs}")


def test_ranking_nc_before_ofi_before_comply():
    posture = _posture([
        ("A.5.18", "Comply", "confirmed"),
        ("A.5.15", "OFI",    "unconfirmed"),
        ("A.5.16", "NC",     "unconfirmed"),
    ])
    cf = make_cf(posture=posture)
    refs = _rank_posture_refs(cf, limit=5)
    return _ok(refs == ["A.5.16", "A.5.15", "A.5.18"], f"got {refs}")


def test_ranking_drops_na_and_unassessed():
    posture = _posture([
        ("A.5.18", "NC",  "unconfirmed"),
        ("A.5.15", "N/A", "confirmed"),
        ("A.5.16", "",    "unconfirmed"),
    ])
    cf = make_cf(posture=posture)
    refs = _rank_posture_refs(cf, limit=10)
    return _ok(refs == ["A.5.18"], f"got {refs}")


def test_ranking_respects_limit():
    posture = _posture([(f"A.5.{i}", "NC", "unconfirmed") for i in range(1, 21)])
    cf = make_cf(posture=posture)
    refs = _rank_posture_refs(cf, limit=5)
    return _ok(len(refs) == 5, f"got {len(refs)}")


# ── Section renderers ────────────────────────────────────────────────

def test_render_query():
    cf = make_cf(query="what are our NCs?")
    return _ok(_render_query(cf) == "QUERY: what are our NCs?")


def test_render_query_empty():
    cf = make_cf(query="")
    return _ok(_render_query(cf) == "QUERY: (empty)")


def test_render_posture_empty_returns_blank():
    cf = make_cf(posture={})
    return _ok(_render_posture(cf) == "")


def test_render_posture_has_draft_tag_when_unconfirmed():
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    cf = make_cf(posture=posture)
    out = _render_posture(cf)
    return _ok("[NC-DRAFT]" in out and "A.5.18" in out, out)


def test_render_posture_no_draft_when_confirmed():
    posture = _posture([("A.5.15", "Comply", "confirmed")])
    cf = make_cf(posture=posture)
    out = _render_posture(cf)
    return _ok("[Comply]" in out and "[Comply-DRAFT]" not in out, out)


def test_render_xfw_bridges_shows_primary_postures():
    posture = _posture([("A.5.15", "Comply", "confirmed"),
                        ("A.5.18", "NC",     "unconfirmed")])
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15"),
                         E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18")])
    cf = make_cf(posture=posture, xfw=[art32])
    out = _render_xfw_bridges(cf)
    return _ok(
        "Art.32 ←" in out
        and "A.5.15 [Comply]" in out
        and "A.5.18 [NC-DRAFT]" in out,
        out,
    )


def test_render_xfw_bridges_marks_unassessed():
    """When linked primaries have no substantive posture, tag it."""
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.99")])
    cf = make_cf(xfw=[art32])  # no posture for A.5.99
    out = _render_xfw_bridges(cf)
    return _ok("[not yet assessed]" in out and "Art.32" in out, out)


def test_render_xfw_bridges_empty():
    cf = make_cf(xfw=[])
    return _ok(_render_xfw_bridges(cf) == "")


def test_render_obligations_prefers_cited_refs():
    a1 = N(node_id="X:1", ref="A.5.99", metadata={"obligation_text": "unrelated"})
    a2 = N(node_id="X:2", ref="A.5.18", metadata={"obligation_text": "access rights obligation"})
    cf = make_cf(
        primary=[a1, a2],
        intent={"intent_type": "definition", "focus_refs": ["A.5.18"]},
    )
    out = _render_obligations(cf, max_items=1)
    return _ok("A.5.18" in out and "A.5.99" not in out, out)


def test_render_obligations_truncates():
    a1 = N(node_id="X:1", ref="A.5.18",
           metadata={"obligation_text": "x" * 500})
    cf = make_cf(primary=[a1])
    out = _render_obligations(cf, max_items=1, max_chars_each=100)
    return _ok(
        "…" in out and out.count("A.5.18:") == 1,
        out,
    )


def test_render_obligations_empty_when_no_text():
    a1 = N(node_id="X:1", ref="A.5.18", metadata={})
    cf = make_cf(primary=[a1])
    return _ok(_render_obligations(cf) == "")


def test_render_documents_uploaded_shows_progress():
    doc = Doc(
        control_ref="A.5.15", title="Access Control Policy",
        must_contain=[Item("scope", "present"), Item("roles", "missing"), Item("owner", "present")],
    )
    cf = make_cf(docs={"n1": doc})
    out = _render_documents(cf)
    return _ok("A.5.15" in out and "2/3" in out, out)


def test_render_documents_not_uploaded():
    doc = Doc(
        control_ref="A.5.15", title="Access Control Policy",
        must_contain=[Item("scope", None), Item("roles", None)],
    )
    cf = make_cf(docs={"n1": doc})
    out = _render_documents(cf)
    return _ok("no document uploaded" in out, out)


def test_render_documents_empty():
    cf = make_cf(docs={})
    return _ok(_render_documents(cf) == "")


def test_render_session_active_refs():
    cf = make_cf(session=Sess(active_refs=["A.5.18", "A.5.15"]))
    return _ok(_render_session(cf) == "SESSION active: A.5.18, A.5.15")


def test_render_session_empty():
    cf = make_cf(session=Sess(active_refs=[]))
    return _ok(_render_session(cf) == "")


def test_render_scope_humanizes_standards():
    cf = make_cf(tenant=T(scope=Sc(queryable_standards=[
        "ISO27001:2022", "GDPR:2016/679", "ISO27701:2019",
    ])))
    return _ok(_render_scope(cf) == "SCOPE: ISO 27001 + GDPR + ISO 27701")


def test_render_scope_empty():
    cf = make_cf(tenant=T(scope=Sc(queryable_standards=[])))
    return _ok(_render_scope(cf) == "")


# ── Deictic hint ──────────────────────────────────────────────────────

def test_deictic_hint_fires_when_deictic_no_entity():
    cf = make_cf(query="what about the policy?", last_entity=None)
    return _ok("DEICTIC" in _render_deictic_hint(cf))


def test_deictic_hint_suppressed_with_last_entity():
    cf = make_cf(query="what about the policy?", last_entity={"ref": "A.5.15"})
    return _ok(_render_deictic_hint(cf) == "")


def test_deictic_hint_suppressed_when_not_deictic():
    cf = make_cf(query="show me our NC findings", last_entity=None)
    return _ok(_render_deictic_hint(cf) == "")


# ── End-to-end shape ──────────────────────────────────────────────────

def test_build_prompt_digest_realistic_shape():
    """Realistic tenant scenario — verify all sections present."""
    posture = _posture([
        ("A.5.15", "Comply", "confirmed"),
        ("A.5.16", "OFI",    "unconfirmed"),
        ("A.5.17", "OFI",    "unconfirmed"),
        ("A.5.18", "NC",     "unconfirmed"),
        ("A.5.20", "NC",     "unconfirmed"),
    ])
    a518 = N(node_id="ISO27001:2022:A.5.18", ref="A.5.18",
             metadata={"obligation_text": "Access rights shall be provisioned reviewed modified and removed."})
    a515 = N(node_id="ISO27001:2022:A.5.15", ref="A.5.15",
             metadata={"obligation_text": "Rules to control physical and logical access shall be established."})
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15"),
                         E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18")])
    cf = make_cf(
        query="what are our access-rights gaps?",
        posture=posture,
        primary=[a518, a515],
        xfw=[art32],
        intent={"intent_type": "gap_analysis", "focus_refs": ["A.5.18"]},
        session=Sess(active_refs=["A.5.18"]),
        tenant=T(scope=Sc(queryable_standards=["ISO27001:2022", "GDPR:2016/679"])),
    )
    out = build_prompt_digest(cf)
    return _ok(
        "QUERY:" in out
        and "POSTURE" in out
        and "XFW BRIDGES:" in out
        and "OBLIGATIONS:" in out
        and "SESSION active:" in out
        and "SCOPE:" in out
        and "A.5.18 [NC-DRAFT]" in out
        and "A.5.15 [Comply]" in out
        and "Art.32 ←" in out,
        out,
    )


def test_build_prompt_digest_token_budget():
    """A realistic query must fit under 2000 tokens (system + user).
    This is the core Ship 2' promise."""
    posture = _posture([
        (f"A.5.{i}", f, cs)
        for i, f, cs in [
            (15, "Comply", "confirmed"), (16, "OFI", "unconfirmed"),
            (17, "OFI", "unconfirmed"),  (18, "NC",  "unconfirmed"),
            (20, "NC",  "unconfirmed"),  (21, "NC",  "unconfirmed"),
            (22, "NC",  "unconfirmed"),  (23, "NC",  "unconfirmed"),
            (24, "OFI", "unconfirmed"),  (25, "OFI", "unconfirmed"),
        ]
    ])
    primary = [
        N(node_id=f"ISO27001:2022:A.5.{i}", ref=f"A.5.{i}",
          metadata={"obligation_text": "x" * 300})
        for i in range(15, 26)
    ]
    art32 = N(node_id="GDPR:2016/679:Art.32", ref="Art.32",
              standard_id="GDPR:2016/679",
              xfw_edges=[E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.18"),
                         E("GDPR:2016/679:Art.32", "ISO27001:2022:A.5.15")])
    cf = make_cf(
        query="what are our access-rights gaps?" * 3,
        posture=posture, primary=primary, xfw=[art32],
        session=Sess(active_refs=["A.5.18", "A.5.15"]),
        tenant=T(scope=Sc(queryable_standards=["ISO27001:2022", "GDPR:2016/679", "ISO27701:2019"])),
    )
    sys_p, user_p = build_prompt_pair(cf)
    total = approx_tokens(sys_p) + approx_tokens(user_p)
    return _ok(
        total < 2000,
        f"tokens: system={approx_tokens(sys_p)} user={approx_tokens(user_p)} total={total}",
    )


def test_build_prompt_digest_omits_empty_sections():
    """A query with only posture (no xfw, no session, no docs) should
    show only the sections that have content."""
    posture = _posture([("A.5.18", "NC", "unconfirmed")])
    cf = make_cf(posture=posture)
    out = build_prompt_digest(cf)
    return _ok(
        "XFW BRIDGES:" not in out
        and "DOCUMENTS:" not in out
        and "SESSION active:" not in out
        and "OBLIGATIONS:" not in out,
        out,
    )


def test_build_system_prompt_uses_tenant_name():
    cf = make_cf(tenant=T(tenant_name="Acme Corp"))
    return _ok("Acme Corp" in build_system_prompt(cf))


def test_build_prompt_pair_returns_both():
    cf = make_cf()
    sys_p, user_p = build_prompt_pair(cf)
    return _ok(isinstance(sys_p, str) and isinstance(user_p, str) and sys_p and user_p)


# ── Ship 2'.i: intent-aware plan + jargon sanitizer ─────────────────

def test_plan_definition_puts_obligations_first():
    cf = make_cf(intent={"intent_type": "definition", "focus_refs": ["A.6.4"]})
    plan = _plan_for(cf)
    return _ok(
        plan.obligations_first is True
        and plan.obligation_chars >= 400
        and plan.posture_limit <= 3,
        f"plan={plan}",
    )


def test_plan_posture_check_keeps_posture_first():
    cf = make_cf(intent={"intent_type": "posture_check", "focus_refs": ["A.5.18"]})
    plan = _plan_for(cf)
    return _ok(
        plan.obligations_first is False
        and plan.posture_limit >= 10,
        f"plan={plan}",
    )


def test_plan_standard_knowledge_uses_definition_mode():
    cf = make_cf(intent={"intent_type": "standard_knowledge"})
    plan = _plan_for(cf)
    return _ok(plan.obligations_first is True, f"plan={plan}")


def test_plan_unknown_intent_falls_back_to_defaults():
    cf = make_cf(intent={"intent_type": "gap_analysis"})
    plan = _plan_for(cf)
    return _ok(plan.obligations_first is False)


def test_definition_digest_puts_obligations_above_posture():
    """The key regression fix — for a "what is A.6.4?" query, OBLIGATIONS
    must appear before POSTURE in the digest text."""
    a64 = N(
        node_id="ISO27001:2022:A.6.4", ref="A.6.4",
        metadata={"obligation_text": "Disciplinary process. Personnel disciplinary framework."},
    )
    posture = _posture([("A.5.10", "NC", "unconfirmed")])
    cf = make_cf(
        query="what is ISO 27001 control A.6.4?",
        primary=[a64], posture=posture,
        intent={"intent_type": "definition", "focus_refs": ["A.6.4"]},
    )
    out = build_prompt_digest(cf)
    obl_idx = out.find("OBLIGATIONS:")
    pos_idx = out.find("POSTURE")
    return _ok(
        obl_idx != -1 and pos_idx != -1 and obl_idx < pos_idx,
        f"OBLIGATIONS at {obl_idx}, POSTURE at {pos_idx}",
    )


def test_definition_digest_obligation_text_is_400_chars():
    """A.6.4's full obligation should reach the digest — 160-char cap
    was truncating before 'disciplinary' in the definition-query
    Ship 2'.h regression."""
    long_text = "Disciplinary process. " + ("More text here. " * 30)
    a64 = N(
        node_id="ISO27001:2022:A.6.4", ref="A.6.4",
        metadata={"obligation_text": long_text},
    )
    cf = make_cf(
        primary=[a64],
        intent={"intent_type": "definition", "focus_refs": ["A.6.4"]},
    )
    out = build_prompt_digest(cf)
    # The obligation body in the digest should be roughly 400 chars,
    # not the default 160.
    # Find the A.6.4 line and check its length.
    line = next(l for l in out.split("\n") if l.startswith("- A.6.4:"))
    return _ok(len(line) > 250, f"line len={len(line)}: {line[:80]}...")


def test_sanitize_gap_text_children_satisfied():
    # Ship 67' — engine's "children" count is the composite of leaves +
    # derived deps, so we say "fulfilment elements met" not "required
    # items present" (which the RelatedCard evidence_summary uses for
    # its leaves-only count).
    return _ok(
        _sanitize_gap_text("0/4 children satisfied") == "0 of 4 fulfilment elements met",
    )


def test_sanitize_gap_text_missing_artifacts():
    return _ok(
        _sanitize_gap_text("missing artifacts of type: policy_document")
        == "still needed: policy_document",
    )


def test_sanitize_gap_text_multi_jargon():
    raw = "0/4 children satisfied; missing artifacts of type: register"
    got = _sanitize_gap_text(raw)
    return _ok(
        "children satisfied" not in got and "missing artifacts of type" not in got,
        got,
    )


def test_sanitize_gap_text_no_change_when_clean():
    clean = "register incomplete; last review overdue"
    return _ok(_sanitize_gap_text(clean) == clean)


def test_posture_line_uses_sanitized_gap():
    rec = {"finding": "NC", "gap_description": "0/4 children satisfied"}
    line = _posture_line("A.5.18", rec, draft=True)
    # Ship 67' — the engine-jargon phrase is replaced by the composite-
    # view phrase, not the leaves-only phrase.
    return _ok(
        "children satisfied" not in line and "fulfilment elements met" in line,
        line,
    )


def test_definition_digest_end_to_end_preserves_key_terms():
    """The Ship 2'.h regression #23: 'what is A.6.4?' — the word
    'disciplinary' must appear in the digest even after truncation."""
    a64 = N(
        node_id="ISO27001:2022:A.6.4", ref="A.6.4",
        metadata={},
        document="ISO27001:2022 A.6.4: Disciplinary process\nTo ensure personnel and other relevant interested parties understand the consequences of information security policy violation, to deter and appropriately deal with personnel and other relevant interested parties who committed the violation.",
    )
    cf = make_cf(
        query="what is ISO 27001 control A.6.4?",
        primary=[a64],
        intent={"intent_type": "definition", "focus_refs": ["A.6.4"]},
    )
    out = build_prompt_digest(cf)
    return _ok(
        "disciplinary" in out.lower() and "OBLIGATIONS:" in out,
        f"digest does not contain 'disciplinary' — snippet: {out[:400]}",
    )


TESTS = [
    test_plan_definition_puts_obligations_first,
    test_plan_posture_check_keeps_posture_first,
    test_plan_standard_knowledge_uses_definition_mode,
    test_plan_unknown_intent_falls_back_to_defaults,
    test_definition_digest_puts_obligations_above_posture,
    test_definition_digest_obligation_text_is_400_chars,
    test_sanitize_gap_text_children_satisfied,
    test_sanitize_gap_text_missing_artifacts,
    test_sanitize_gap_text_multi_jargon,
    test_sanitize_gap_text_no_change_when_clean,
    test_posture_line_uses_sanitized_gap,
    test_definition_digest_end_to_end_preserves_key_terms,
    test_verdict_tag_variants,
    test_posture_line_nc_uses_gap,
    test_posture_line_comply_uses_evidence,
    test_posture_line_truncates_long_body,
    test_posture_line_collapses_whitespace,
    test_posture_line_no_body_no_dash,
    test_ranking_cited_first,
    test_ranking_session_before_findings,
    test_ranking_nc_before_ofi_before_comply,
    test_ranking_drops_na_and_unassessed,
    test_ranking_respects_limit,
    test_render_query,
    test_render_query_empty,
    test_render_posture_empty_returns_blank,
    test_render_posture_has_draft_tag_when_unconfirmed,
    test_render_posture_no_draft_when_confirmed,
    test_render_xfw_bridges_shows_primary_postures,
    test_render_xfw_bridges_marks_unassessed,
    test_render_xfw_bridges_empty,
    test_render_obligations_prefers_cited_refs,
    test_render_obligations_truncates,
    test_render_obligations_empty_when_no_text,
    test_render_documents_uploaded_shows_progress,
    test_render_documents_not_uploaded,
    test_render_documents_empty,
    test_render_session_active_refs,
    test_render_session_empty,
    test_render_scope_humanizes_standards,
    test_render_scope_empty,
    test_deictic_hint_fires_when_deictic_no_entity,
    test_deictic_hint_suppressed_with_last_entity,
    test_deictic_hint_suppressed_when_not_deictic,
    test_build_prompt_digest_realistic_shape,
    test_build_prompt_digest_token_budget,
    test_build_prompt_digest_omits_empty_sections,
    test_build_system_prompt_uses_tenant_name,
    test_build_prompt_pair_returns_both,
]


def main():
    print("─" * 70)
    print("  Prompt digest tests")
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
