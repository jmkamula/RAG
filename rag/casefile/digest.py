"""
Prompt digest builder — compact ~1-2k token render of a CaseFile
for the LLM's rank-and-answer call.

Design: fixed-slots layered. Every digest has the same top-level
structure regardless of question_type — no per-taxonomy branching.
Empty sections are omitted entirely (a 'POSTURE' block with zero
findings prints nothing rather than an empty header).

Section budgets (soft — sections truncate items but don't hard-clip
mid-line):
  QUERY          ~50 tok
  POSTURE       ~600 tok  (~10 lines × 60 tok)
  XFW BRIDGES   ~200 tok  (~5 lines × 40 tok)
  OBLIGATIONS   ~200 tok  (~5 lines × 40 tok)
  DOCUMENTS     ~100 tok  (only when relevant)
  SESSION       ~50 tok
  SCOPE         ~30 tok
  ----
  Total user    ~1230 tok

The slim system prompt (build_system_prompt) targets ~1000 tokens,
so the grand total lands near ~2.2k. See tests/casefile for the
token-budget assertions.
"""
from __future__ import annotations

import logging
from typing import Optional

from rag.casefile.types import CaseFile


logger = logging.getLogger(__name__)


# ── Token math ────────────────────────────────────────────────────────

# Rough estimator — good enough for section budgeting. Real tokens
# are measured post-render via tiktoken when logging.
def approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)


# ── Formatting primitives ─────────────────────────────────────────────

# Verdict tag renderer — [NC-DRAFT] / [OFI] / [Comply-DRAFT] etc.
def _verdict_tag(finding: str, draft: bool) -> str:
    if not finding:
        return ""
    suffix = "-DRAFT" if draft else ""
    return f"[{finding}{suffix}]"


# One-line posture entry: "- A.5.18 [NC-DRAFT] register incomplete"
def _posture_line(ref: str, rec: dict, draft: bool, max_body_chars: int = 120) -> str:
    finding = rec.get("finding", "") or ""
    tag = _verdict_tag(finding, draft)
    body = ""
    if finding == "NC" or finding == "OFI":
        body = (rec.get("gap_description", "") or "").strip()
    elif finding == "Comply":
        body = (rec.get("evidence_text", "") or "").strip()
    if body:
        # Collapse whitespace + newlines, cap length.
        body = " ".join(body.split())
        if len(body) > max_body_chars:
            body = body[: max_body_chars - 1] + "…"
        return f"- {ref} {tag} {body}".rstrip()
    return f"- {ref} {tag}".rstrip()


# Rank posture refs by relevance to this query:
#   1. Cited refs from intent
#   2. Session active refs
#   3. NC findings (any not-yet-listed)
#   4. OFI findings
#   5. Comply findings
# N/A + unassessed are dropped.
def _rank_posture_refs(cf: CaseFile, limit: int) -> list[str]:
    posture = cf.posture_by_ref()
    if not posture:
        return []
    ranked: list[str] = []
    seen: set[str] = set()

    def _add(ref: str):
        if ref in seen or ref not in posture:
            return
        f = posture[ref].get("finding")
        if f not in ("NC", "OFI", "Comply"):
            return
        ranked.append(ref)
        seen.add(ref)

    for r in cf.cited_refs:
        _add(r)
    for r in cf.active_session_refs:
        _add(r)
    for target in ("NC", "OFI", "Comply"):
        for ref, rec in posture.items():
            if len(ranked) >= limit:
                break
            if rec.get("finding") == target:
                _add(ref)
        if len(ranked) >= limit:
            break

    return ranked[:limit]


# ── Section renderers ────────────────────────────────────────────────

def _render_query(cf: CaseFile) -> str:
    q = (cf.query or "").strip()
    return f"QUERY: {q}" if q else "QUERY: (empty)"


def _render_posture(cf: CaseFile, limit: int = 10) -> str:
    """Top-N ranked posture lines. Returns '' when nothing to show."""
    refs = _rank_posture_refs(cf, limit)
    if not refs:
        return ""
    posture = cf.posture_by_ref()
    total_assessed = sum(
        1 for rec in posture.values()
        if rec.get("finding") in ("NC", "OFI", "Comply")
    )
    header = f"POSTURE (showing {len(refs)} of {total_assessed} assessed):"
    lines = [
        _posture_line(r, posture[r], draft=cf.needs_draft_tag(r))
        for r in refs
    ]
    return header + "\n" + "\n".join(lines)


def _render_xfw_bridges(cf: CaseFile) -> str:
    """One line per xfw node: 'Art.32 ← A.5.15 [Comply], A.5.18 [NC]'
    Postures come from posture_by_ref — same source the LLM would
    otherwise re-derive from the per-node Layer 2 block.

    Nodes without any assessed linked primary are still listed, but
    with a '[not yet assessed]' hint — they're not anti-hallucinated
    away here (CaseFile leaves that decision to the caller).
    """
    bridges = cf.xfw_bridges()
    if not bridges:
        return ""
    posture = cf.posture_by_ref()
    lines: list[str] = []
    for xfw_ref, primary_refs in sorted(bridges.items()):
        parts: list[str] = []
        any_assessed = False
        for pref in primary_refs:
            rec = posture.get(pref)
            if rec and rec.get("finding") in ("NC", "OFI", "Comply"):
                any_assessed = True
                draft = cf.needs_draft_tag(pref)
                parts.append(f"{pref} {_verdict_tag(rec['finding'], draft)}")
            else:
                parts.append(pref)
        joined = ", ".join(parts)
        if any_assessed:
            lines.append(f"- {xfw_ref} ← {joined}")
        else:
            lines.append(f"- {xfw_ref} ← {joined} [not yet assessed]")
    return "XFW BRIDGES:\n" + "\n".join(lines)


def _render_obligations(
    cf: CaseFile,
    max_items: int = 5,
    max_chars_each: int = 160,
) -> str:
    """Short obligation excerpts for the top primary nodes.

    Uses node.metadata.obligation_text / business_description /
    node.document — same fallback chain as rank_and_answer's node
    template. Prioritise Layer 1 nodes matching cited_refs first,
    then any remaining Layer 1 nodes by insertion order.
    """
    primary = cf.primary_nodes()
    if not primary:
        return ""

    cited = set(cf.cited_refs)
    ordered: list = []
    seen_refs: set[str] = set()
    # cited-refs first
    for n in primary:
        if n.ref in cited and n.ref not in seen_refs:
            ordered.append(n)
            seen_refs.add(n.ref)
    # then any remaining
    for n in primary:
        if n.ref not in seen_refs:
            ordered.append(n)
            seen_refs.add(n.ref)
        if len(ordered) >= max_items:
            break
    ordered = ordered[:max_items]

    lines: list[str] = []
    for n in ordered:
        meta = getattr(n, "metadata", {}) or {}
        text = (
            meta.get("obligation_text")
            or meta.get("business_description")
            or (getattr(n, "document", "") or "")
            or getattr(n, "title", "")
        )
        text = " ".join((text or "").split())
        if not text:
            continue
        if len(text) > max_chars_each:
            text = text[: max_chars_each - 1] + "…"
        lines.append(f"- {n.ref}: {text}")
    if not lines:
        return ""
    return "OBLIGATIONS:\n" + "\n".join(lines)


def _render_documents(cf: CaseFile, max_items: int = 5) -> str:
    """Document-context lines when the resolver surfaced doc contexts.
    Only fires for questions where documents actually matter — an
    empty doc_contexts dict yields ''.
    """
    ctxs = cf.doc_contexts
    if not ctxs:
        return ""
    lines: list[str] = []
    for _nid, ctx in list(ctxs.items())[:max_items]:
        ref = getattr(ctx, "control_ref", "") or ""
        title = getattr(ctx, "title", "") or ""
        # Show missing-must count when uploaded, "no upload" when not.
        try:
            missing = ctx.missing_must
            present = ctx.present_must
            total_must = len(getattr(ctx, "must_contain", []) or [])
            if getattr(ctx, "has_document_uploaded", False):
                lines.append(
                    f"- {ref}: {title} — {len(present)}/{total_must} required items present"
                )
            else:
                lines.append(f"- {ref}: {title} — no document uploaded")
        except AttributeError:
            lines.append(f"- {ref}: {title}")
    if not lines:
        return ""
    return "DOCUMENTS:\n" + "\n".join(lines)


def _render_incidents(cf: CaseFile) -> str:
    """One-line per open incident, when the resolver surfaced any.
    Rare surface — most queries have zero incidents."""
    if not cf.incidents:
        return ""
    lines = []
    for inc in cf.incidents[:5]:
        title = getattr(inc, "title", "")
        urgency = getattr(inc, "urgency", "")
        deadline = getattr(inc, "deadline_at", "") or ""
        deadline_hint = f" (due {deadline})" if deadline else ""
        lines.append(f"- {title} [{urgency}]{deadline_hint}")
    return "OPEN INCIDENTS:\n" + "\n".join(lines)


def _render_session(cf: CaseFile) -> str:
    refs = cf.active_session_refs
    if not refs:
        return ""
    return f"SESSION active: {', '.join(refs)}"


def _render_scope(cf: CaseFile) -> str:
    stds = cf.scope_standards
    if not stds:
        return ""
    labels = []
    for s in stds:
        if s == "ISO27001:2022":
            labels.append("ISO 27001")
        elif s.startswith("GDPR"):
            labels.append("GDPR")
        elif s.startswith("ISO27701"):
            labels.append("ISO 27701")
        else:
            labels.append(s)
    return f"SCOPE: {' + '.join(labels)}"


# ── Deictic hint (from rank_and_answer's prior_turn_block logic) ─────

import re as _re
_DEICTIC_RE = _re.compile(
    r"\b(this|that|it|those|these|what about|how about|tell me more|"
    r"is it|are they|the (policy|plan|procedure|register|document|doc))\b",
    _re.IGNORECASE,
)


def _render_deictic_hint(cf: CaseFile) -> str:
    """When the query is deictic and no last-turn entity is carried,
    tell the LLM to ask rather than invent a referent."""
    if cf.last_entity:
        return ""
    if not _DEICTIC_RE.search(cf.query or ""):
        return ""
    return (
        "DEICTIC WITHOUT CONTEXT: The query uses referential words "
        "('this', 'the policy', 'what about X') but no prior-turn "
        "entity is carried. If the POSTURE below doesn't clearly "
        "answer the question, ask which document or control the "
        "user means rather than inventing a referent."
    )


# ── Main digest builder ──────────────────────────────────────────────

def build_prompt_digest(
    cf: CaseFile,
    posture_limit:    int = 10,
    obligation_limit: int = 5,
    document_limit:   int = 5,
) -> str:
    """Compact render of the CaseFile for the LLM user-prompt slot.

    Returns a plain string. Sections that would be empty are omitted
    entirely — the LLM sees a lean prompt.
    """
    sections: list[str] = []

    def _add(section: str):
        if section:
            sections.append(section)

    _add(_render_query(cf))
    _add(_render_deictic_hint(cf))
    _add(_render_incidents(cf))
    _add(_render_posture(cf, limit=posture_limit))
    _add(_render_xfw_bridges(cf))
    _add(_render_obligations(cf, max_items=obligation_limit))
    _add(_render_documents(cf, max_items=document_limit))
    _add(_render_session(cf))
    _add(_render_scope(cf))

    return "\n\n".join(sections)


# ── Slim system prompt (~1000 tokens) ────────────────────────────────

# Kept as a template so tenant_name + scope_standards render in.
# Compared to RANK_AND_ANSWER_SYSTEM (~3100 tokens), this drops:
#   - the two-layer LAYER 1 / LAYER 2 explainer (info is in the
#     BRIDGES section of the digest)
#   - the SELECTED_PRIMARY / SELECTED_XFW output rubric (removed —
#     the digest gives the LLM only what it should mention)
#   - the multi-paragraph glossary + controls-vs-clauses-vs-articles
#     reference (compressed to a single line each)
#   - the standards-scope + N/A control lists (moved into the SCOPE
#     section of the digest per turn)
#   - the document guidance blocks (documents come pre-scored in the
#     DOCUMENTS section)
# What we keep:
#   - persona
#   - core output rules (preserve refs, only cite CaseFile-sourced
#     data, NC → OFI → Comply ordering)
#   - one-line glossary of NC/OFI/Comply
#   - anti-invention guard for controls / dates / severities
#   - N/A behaviour (short — full list is in SCOPE)
_SLIM_SYSTEM = """You are a compliance advisor for {tenant_name}.
Answer from the CASE FILE below — nothing else. Never invent
control refs, article numbers, document IDs, or evidence you
don't see in the CASE FILE.

Output rules (absolute):
1. Preserve every ref exactly as it appears (A.5.18, Art.32, 9.2).
   Refs are the answer's audit trail — dropping any is a
   compliance failure.
2. Report posture only from the tags in the POSTURE section:
   NC (Non-Conformity) — required control absent or ineffective;
   OFI (Opportunity for Improvement) — control exists with gaps;
   Comply — control in place with evidence.
   The -DRAFT suffix means posture is not yet auditor-confirmed —
   keep the [DRAFT] tag in your answer when it's on the source.
3. Cross-framework refs (Art.X, ISO 27701 A.7.x, etc.) carry no
   posture of their own. Their status is inherited from the
   controls in the XFW BRIDGES section — cite the primary refs
   when reporting their posture.
4. Lead with NC findings, then OFI, then Comply. Never list
   "not yet assessed" or omitted controls as gaps.
5. Cite frameworks only from the SCOPE line. Frameworks outside
   scope are not implemented by the tenant and must never appear
   in your answer.
6. Cite controls with the readable framework prefix:
   "ISO 27001 A.5.18", "GDPR Art. 32", "ISO 27001 clause 9.2".
   ISO body clauses (5.x/6.x/7.x/8.x/9.x/10.x) are NOT Annex A —
   never write "A.9.2" or "A.10.1".
7. If the DEICTIC WITHOUT CONTEXT hint is present, follow it —
   ask which entity the user meant rather than inventing one.

Be direct and actionable. State what's missing and what to do.
End when the actionable content ends — do not append closing
paragraphs summarising what the user should do (the UI renders
next-actions separately)."""


def build_system_prompt(cf: CaseFile) -> str:
    """Render the slim system prompt with tenant_name filled in."""
    return _SLIM_SYSTEM.format(tenant_name=cf.tenant_name or "the tenant")


# ── Combined helper for downstream wiring ────────────────────────────

def build_prompt_pair(cf: CaseFile) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) as a pair — this is what
    rank_and_answer's _call_llm expects."""
    return build_system_prompt(cf), build_prompt_digest(cf)
