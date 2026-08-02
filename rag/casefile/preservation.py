"""
Preservation spec — the MUST-preserve facts extracted from a CaseFile
that the LLM's answer is checked against.

The LLM sees the compact digest (rag/casefile/digest.py) and never sees
this spec. The spec is what the repair pass consults to detect + fix
drop-outs in the LLM's answer.

Four kinds of preservation, per user policy (Ship 2' design choice):

  1. required_refs  — refs the LLM must cite. Union of:
                        * cf.cited_refs that have data in the CaseFile
                        * top 3 refs from the digest's posture ranking
                      Rationale: the classifier locked cited_refs in via
                      Signal B / C; digest surfaces top-3 to the LLM
                      already. Dropping either is a stochastic loss the
                      LLM shouldn't be trusted with.

  2. draft_refs     — refs whose mention must carry the [DRAFT] tag
                      (unconfirmed posture). Repair inserts if missing.

  3. verdict_by_ref — {ref: NC|OFI|Comply} mapping for every required_ref
                      with a substantive finding. Repair adds the tag
                      near the ref if absent.

  4. bridge_footer  — the deterministic "↳ Bridges to ISO 27001 for
                      Art.X: A.5.15 [Comply], A.5.18 [NC-DRAFT]" line
                      that Ship 1.14 already established for xfw
                      queries. Repair appends if missing.

The extractor does NOT run the digest — it reads the CaseFile directly.
The two share `_rank_posture_refs` from digest.py to guarantee the
top-N is identical.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from rag.casefile.types import CaseFile
from rag.casefile.digest import _rank_posture_refs, _rank_obligation_refs, _verdict_tag


# Top-N of ranked posture that go into required_refs (in addition
# to cited_refs). Kept small — over-preservation just clutters
# answers when the LLM did nothing wrong.
_REQUIRED_TOP_N = 3


@dataclass
class PreservationSpec:
    """Ground-truth requirements the LLM answer must satisfy.

    Fields are read-only — the extractor builds one; the repair
    pass reads it. No mutation.
    """
    required_refs:   set[str]              = field(default_factory=set)
    draft_refs:      set[str]              = field(default_factory=set)
    verdict_by_ref:  dict[str, str]        = field(default_factory=dict)
    bridge_footer:   Optional[str]         = None
    # Article refs from the query that anchor the bridge_footer's
    # "for Art.X:" label — kept for the repair pass to build the
    # correct label text.
    bridge_article_refs: list[str]         = field(default_factory=list)
    # Ship 14'.e — risk external_refs (e.g. "R-042") that the RISKS
    # digest section surfaced. Repair pass appends any dropped refs
    # via the existing `↳ Compliance facts: …` footer pattern.
    required_risk_refs:  list[str]         = field(default_factory=list)

    def is_empty(self) -> bool:
        return (
            not self.required_refs
            and not self.draft_refs
            and not self.verdict_by_ref
            and not self.bridge_footer
            and not self.required_risk_refs
        )


# ── Bridge footer — mirrors llm_answer.py's Ship 1.14 rule ────────────

import re as _re

_ARTICLE_RE = _re.compile(r"\bArt\.\d+(?:\.\d+)?\b")


def _extract_article_refs(cf: CaseFile) -> list[str]:
    """Article refs to anchor the bridge_footer label on.
    Cited refs first; fall back to regex-extract from the query.
    Matches llm_answer.py's existing rule (Ship 1.7c)."""
    cited = [r for r in cf.cited_refs if r and r.startswith("Art.")]
    if cited:
        return cited
    return _ARTICLE_RE.findall(cf.query or "")


def _build_bridge_footer(cf: CaseFile) -> tuple[Optional[str], list[str]]:
    """Return (footer_text, article_refs) for the CaseFile, or (None, []).

    Fires when:
      1. xfw_bridges is non-empty AND
      2. the query has an article ref (cited or in query text) AND
      3. some xfw node links to that article (or an article-family).

    Footer format matches llm_answer.py:
      ↳ Bridges to ISO 27001 for Art.X: A.5.15 [Comply], A.5.18 [NC-DRAFT]
    """
    bridges = cf.xfw_bridges()
    if not bridges:
        return None, []

    article_refs = _extract_article_refs(cf)
    if not article_refs:
        return None, []

    # Only include xfw nodes whose linked primaries relate to the
    # cited articles (same family match as llm_answer.py).
    posture = cf.posture_by_ref()
    relevant: list[tuple[str, str, bool]] = []  # (xfw_ref, verdict|placeholder, draft)
    for xfw_ref, primary_refs in bridges.items():
        # xfw_ref itself is the linked article's "other end" here — the
        # bridge dict is keyed by the xfw node's ref (e.g. Art.32)
        # and lists primary refs (e.g. A.5.15). But the article we're
        # anchoring is what the query cited.
        # An xfw entry is "relevant" if EITHER:
        #   (a) the xfw_ref matches an article in article_refs (or family), OR
        #   (b) one of its primary_refs matches an article in article_refs
        matched = False
        for art in article_refs:
            if xfw_ref == art or xfw_ref.startswith(art + "."):
                matched = True
                break
            for pref in primary_refs:
                if pref == art or pref.startswith(art + "."):
                    matched = True
                    break
            if matched:
                break
        if not matched:
            continue

        # Take the xfw_ref's own posture if present (rare — xfw refs
        # usually don't have direct posture; they inherit). Otherwise
        # take the "worst" of the linked primary refs — matches
        # llm_answer.py's behaviour of showing each linked primary's
        # finding rather than a single roll-up.
        # For the footer we mirror llm_answer.py which lists each
        # linked primary. To keep the footer readable and close to
        # existing shape, we emit primary-ref entries.
        for pref in sorted(primary_refs):
            rec = posture.get(pref) or {}
            finding = rec.get("finding")
            if finding in ("NC", "OFI", "Comply"):
                draft = cf.needs_draft_tag(pref)
                relevant.append((pref, finding, draft))

    if not relevant:
        return None, []

    # Dedupe by ref, preserve sort.
    seen: set[str] = set()
    unique: list[tuple[str, str, bool]] = []
    for ref, verdict, draft in relevant:
        if ref in seen:
            continue
        seen.add(ref)
        unique.append((ref, verdict, draft))

    if not unique:
        return None, []

    parts = [f"{ref} {_verdict_tag(v, d)}" for ref, v, d in unique]
    label = ", ".join(article_refs)
    footer = f"↳ Bridges to ISO 27001 for {label}: " + ", ".join(parts)
    return footer, article_refs


# ── Required refs — union of cited (with data) + top ranked posture ─

def _has_data_in_casefile(cf: CaseFile, ref: str) -> bool:
    """True when the CaseFile carries something to say about this ref:
    posture OR a node in graph_nodes."""
    if ref in cf.posture_by_ref():
        return True
    for n in cf.all_nodes():
        if n.ref == ref:
            return True
    return False


def _required_refs(cf: CaseFile) -> set[str]:
    """Refs the answer must mention.

    Three feeders:
      1. cf.cited_refs — refs the query or classifier locked in.
         Filter to those we actually have data for (avoid demanding
         mention of an off-scope ref the resolver couldn't surface).
      2. Top-N of _rank_posture_refs — the highest-priority POSTURE
         entries in the digest. If the LLM was shown these, they
         should appear in the answer.
      3. Ship 53'.j — top-N of _rank_obligation_refs — refs surfaced
         in the OBLIGATIONS section. Especially load-bearing on
         definition queries with `→ guidance: ISO 27005` markers
         where the underlying clause (e.g. 6.1.2) may not appear in
         cited_refs or top-3 posture but IS in the OBLIGATIONS text
         the LLM was shown. Case #222 exposed this drop mode.
    """
    out: set[str] = set()
    for r in cf.cited_refs:
        if r and _has_data_in_casefile(cf, r):
            out.add(r)
    for r in _rank_posture_refs(cf, limit=_REQUIRED_TOP_N):
        out.add(r)
    for r in _rank_obligation_refs(cf, limit=_REQUIRED_TOP_N + 2):
        out.add(r)
    return out


# ── Main extractor ────────────────────────────────────────────────────

def extract_preservation_spec(cf: CaseFile) -> PreservationSpec:
    """Build the preservation spec for one CaseFile.

    Reads:
      cf.cited_refs                    → required_refs (data-filtered)
      _rank_posture_refs top-N         → required_refs
      posture_by_ref[ref].finding      → verdict_by_ref
      posture_by_ref[ref] confirmation → draft_refs
      xfw_bridges + article refs       → bridge_footer

    Never writes; the CaseFile is treated as immutable.
    """
    # Ship 44'.d — span for preservation-spec extraction. Cheap
    # function but useful signal for how many refs the preservation
    # check will police on a per-turn basis.
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    _span_cm = _tracer.start_as_current_span("arion.casefile.extract_preservation_spec")
    _span = _span_cm.__enter__()

    refs = _required_refs(cf)
    posture = cf.posture_by_ref()

    verdict_by_ref: dict[str, str] = {}
    draft_refs: set[str] = set()
    for r in refs:
        rec = posture.get(r)
        if not rec:
            continue
        f = rec.get("finding")
        if f in ("NC", "OFI", "Comply"):
            verdict_by_ref[r] = f
            if cf.needs_draft_tag(r):
                draft_refs.add(r)

    bridge_footer, article_refs = _build_bridge_footer(cf)

    # Ship 14'.e — extract risk external_refs from the RISKS digest
    # section. Repair pass appends any dropped refs to the standard
    # `↳ Compliance facts:` footer. Only fires when cf.risks is
    # non-empty (i.e. classifier routed to POSTURE_RISK).
    required_risk_refs: list[str] = [
        r.get("external_ref") for r in (getattr(cf, "risks", None) or [])
        if r.get("external_ref")
    ]

    spec = PreservationSpec(
        required_refs       = refs,
        draft_refs          = draft_refs,
        verdict_by_ref      = verdict_by_ref,
        bridge_footer       = bridge_footer,
        bridge_article_refs = article_refs,
        required_risk_refs  = required_risk_refs,
    )

    try:
        _span.set_attribute("arion.casefile.spec.n_required_refs", len(refs))
        _span.set_attribute("arion.casefile.spec.n_draft_refs", len(draft_refs))
        _span.set_attribute("arion.casefile.spec.n_verdicts", len(verdict_by_ref))
        _span.set_attribute("arion.casefile.spec.n_bridge_articles", len(article_refs))
        _span.set_attribute("arion.casefile.spec.n_required_risk_refs",
                            len(required_risk_refs))
        _span.set_attribute("arion.casefile.spec.has_bridge_footer",
                            bool(bridge_footer))
    except Exception:
        pass
    try: _span_cm.__exit__(None, None, None)
    except Exception: pass

    return spec
