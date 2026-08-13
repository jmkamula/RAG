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
import re
from dataclasses import dataclass
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


# Ship 2'.i: engine-jargon phrases that leak through gap_description
# straight into the LLM's prose. These are internal fulfilment-engine
# strings that should never surface to the tenant — dejargonize them
# at the digest boundary, same policy as [[dejargonize-ux-pass-2026-07-01]].
_JARGON_SUBS = [
    # Ship 67' (2026-08-13) — engine's "children" count is the composite
    # of direct leaves + derived-dependency verdicts (e.g. GDPR Art.32's
    # 9 children = 4 direct-evidence leaves + 5 ISO 27001 controls it
    # derives from). This was rendering as "required items present" —
    # colliding semantically with the RelatedCard evidence_summary
    # (leaves-only count) and confusing the LLM. Use a distinct phrase
    # for the composite view so the two surfaces speak different
    # languages the LLM can quote without contradiction.
    # "0/9 children satisfied" → "0 of 9 fulfilment elements met"
    (re.compile(r"\b(\d+)/(\d+)\s+children\s+satisfied\b", re.IGNORECASE),
     r"\1 of \2 fulfilment elements met"),
    # "partial evidence" (harmless but re-word for clarity)
    (re.compile(r"\bwith partial evidence\b", re.IGNORECASE),
     "with partial evidence"),
    # "missing artifacts of type: X" (engine legacy)
    (re.compile(r"\bmissing artifacts of type:\s*", re.IGNORECASE),
     "still needed: "),
]


def _sanitize_gap_text(text: str) -> str:
    """Strip engine-internal jargon out of gap_description before it
    reaches the LLM digest. Same principles as the dejargonize UX pass."""
    if not text:
        return text
    out = text
    for pat, replacement in _JARGON_SUBS:
        out = pat.sub(replacement, out)
    return out


# One-line posture entry: "- A.5.18 [NC-DRAFT] register incomplete"
def _posture_line(ref: str, rec: dict, draft: bool, max_body_chars: int = 120) -> str:
    finding = rec.get("finding", "") or ""
    tag = _verdict_tag(finding, draft)
    body = ""
    if finding == "NC" or finding == "OFI":
        body = _sanitize_gap_text((rec.get("gap_description", "") or "").strip())
    elif finding == "Comply":
        body = _sanitize_gap_text((rec.get("evidence_text", "") or "").strip())
    if body:
        # Collapse whitespace + newlines, cap length.
        body = " ".join(body.split())
        if len(body) > max_body_chars:
            body = body[: max_body_chars - 1] + "…"
        return f"- {ref} {tag} {body}".rstrip()
    return f"- {ref} {tag}".rstrip()


# Rank posture refs by relevance to this query:
#   1. Cited refs from intent (including N/A — Ship 66'.c)
#   2. Session active refs (including N/A)
#   3. NC findings (any not-yet-listed)
#   4. OFI findings
#   5. Comply findings
# Unassessed dropped. N/A included only when the ref is explicitly
# cited or in the active session — so the LLM has grounding to say
# "A.7.7 is Not Applicable per your scope" instead of hallucinating
# "no assessment shown" (Ship 66' dogfood finding, 2026-08-12).
def _rank_posture_refs(cf: CaseFile, limit: int) -> list[str]:
    posture = cf.posture_by_ref()
    if not posture:
        return []
    ranked: list[str] = []
    seen: set[str] = set()

    def _add(ref: str, allow_na: bool = False):
        if ref in seen or ref not in posture:
            return
        f = posture[ref].get("finding")
        eligible = ("NC", "OFI", "Comply") + (("N/A",) if allow_na else ())
        if f not in eligible:
            return
        ranked.append(ref)
        seen.add(ref)

    for r in cf.cited_refs:
        _add(r, allow_na=True)
    for r in cf.active_session_refs:
        _add(r, allow_na=True)
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


def _render_posture(cf: CaseFile, limit: int = 10, body_chars: int = 120) -> str:
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
        _posture_line(r, posture[r], draft=cf.needs_draft_tag(r),
                       max_body_chars=body_chars)
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
    # Ship 60'.j — bridge-coverage counts precomputed in llm_answer.py.
    # Empty dict when unavailable → suffix simply omitted per line.
    counts = getattr(cf, "bridge_counts", None) or {}
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
        # Compact bridge-count suffix — only rendered when SSoT has
        # rows for this ref. Reads "(N/M MUSTs bridge-covered)" —
        # tells the LLM how much of the obligation's required-element
        # set is addressed via cross-framework evidence without
        # inflating the section beyond one short parenthetical.
        _ct = counts.get(xfw_ref)
        if _ct is not None:
            n_bridged, n_total = _ct
            if n_total:
                bridge_suffix = f"  ({n_bridged}/{n_total} MUSTs bridge-covered)"
            else:
                bridge_suffix = ""
        else:
            bridge_suffix = ""
        if any_assessed:
            lines.append(f"- {xfw_ref} ← {joined}{bridge_suffix}")
        else:
            lines.append(f"- {xfw_ref} ← {joined} [not yet assessed]{bridge_suffix}")
    return "XFW BRIDGES:\n" + "\n".join(lines)


def _rank_obligation_refs(cf: CaseFile, limit: int = 5) -> list[str]:
    """Return the top-N refs that _render_obligations would surface.

    Ship 53'.j — kept in lockstep with _render_obligations' iteration
    (cited refs first, then remaining nodes by insertion order). Used
    by preservation.py::_required_refs so any ref the LLM sees in the
    OBLIGATIONS section is a preservation target — dropping any of
    them is exactly the class of stochastic loss the repair pass
    exists to catch.

    Case #222 in the Ship 53'.i eval surfaced this: definition query
    "what does ISO 27005 recommend for risk assessment methodology?"
    had cited_refs=[] and the top-3 posture (10.1 / 10.2 / 4.1 all NC
    0/4) didn't include 6.1.2 (OFI 2/4), but 6.1.2 was in OBLIGATIONS
    with the `→ guidance: ISO 27005` marker. LLM cited it correctly
    ~99% of the time; the 1% miss was invisible to preservation.
    """
    primary = cf.all_nodes()
    if not primary:
        return []
    cited = set(cf.cited_refs)
    ordered: list[str] = []
    seen: set[str] = set()
    for n in primary:
        if n.ref in cited and n.ref not in seen:
            ordered.append(n.ref)
            seen.add(n.ref)
    for n in primary:
        if n.ref not in seen:
            ordered.append(n.ref)
            seen.add(n.ref)
        if len(ordered) >= limit:
            break
    return ordered[:limit]


def _render_obligations(
    cf: CaseFile,
    max_items: int = 5,
    max_chars_each: int = 160,
) -> str:
    """Short obligation excerpts for the top-N relevant nodes.

    Ship 2'.i: iterates all_nodes() (no primary/xfw split — see
    framework-role-model-arc). Priority: cited refs first, then
    remaining nodes by insertion order.

    Uses node.metadata.obligation_text / business_description /
    node.document — same fallback chain as rank_and_answer's node
    template.
    """
    primary = cf.all_nodes()
    if not primary:
        return ""

    # Ship 66'.c — N/A dominance in downstream reader. Skip nodes
    # whose posture is scoped out: the tenant declared them N/A, so
    # the "here's what the standard requires" text is misleading
    # (Ship 66' dogfood finding — LLM was hallucinating "no assessment
    # shown" when it saw the obligation text without scope tag). The
    # POSTURE section still surfaces cited N/A refs with a [N/A] tag
    # so the LLM has grounding to acknowledge them.
    #
    # Ship 66'.d — check applicability_status (source of truth per
    # Ship 66'.a schema split) instead of the legacy finding value.
    # Both are equivalent today (data migrated 1:1), but new checks
    # should prefer applicability_status.
    posture = cf.posture_by_ref()
    def _in_scope(ref: str) -> bool:
        rec = posture.get(ref)
        if not rec:
            return True
        return rec.get("applicability_status") != "na"

    cited = set(cf.cited_refs)
    ordered: list = []
    seen_refs: set[str] = set()
    # cited-refs first
    for n in primary:
        if n.ref in cited and n.ref not in seen_refs and _in_scope(n.ref):
            ordered.append(n)
            seen_refs.add(n.ref)
    # then any remaining
    for n in primary:
        if n.ref not in seen_refs and _in_scope(n.ref):
            ordered.append(n)
            seen_refs.add(n.ref)
        if len(ordered) >= max_items:
            break
    ordered = ordered[:max_items]

    lines: list[str] = []
    for n in ordered:
        meta = getattr(n, "metadata", {}) or {}
        obligation = meta.get("obligation_text") or ""
        bd = meta.get("business_description") or ""
        doc_fallback = (getattr(n, "document", "") or "")
        text_src = "obligation" if obligation else (
            "bd" if bd else ("document" if doc_fallback else "title")
        )
        text = (
            obligation
            or bd
            or doc_fallback
            or getattr(n, "title", "")
        )
        text = " ".join((text or "").split())
        if not text:
            continue
        if len(text) > max_chars_each:
            text = text[: max_chars_each - 1] + "…"
        lines.append(f"- {n.ref}: {text}")

        # Ship 13'.d/e + Ship 53 addendum — surface guidance authority
        # as an attribution the LLM can cite when grounding remediation
        # actions.
        #
        # Two cases:
        #  (a) `obligation` was present AND bd distinct → emit the ISO
        #      27002/3/4/5 paraphrase as a `→ guidance (ISO ...):`
        #      continuation line.
        #  (b) `obligation` was empty (text came from bd or document) →
        #      the paraphrase IS the main text; append a `← source:`
        #      tag inferred from the ref pattern so the LLM knows
        #      which standard to cite. Applies whether the paraphrase
        #      came from bd (context_assembler parsed it) or from
        #      n.document (Chroma raw text passthrough — the common
        #      runtime path since context_assembler's parser doesn't
        #      always fire on graph-expander nodes).
        _std_id = getattr(n, "standard_id", "") or ""
        if obligation and bd:
            _hint, _source = _extract_guidance_hint(bd, ref=n.ref, standard_id=_std_id)
            if _hint:
                if _source:
                    lines.append(f"  → guidance ({_source}): {_hint}")
                else:
                    lines.append(f"  → guidance: {_hint}")
        elif text_src in ("bd", "document"):
            # Infer source from ref+standard even without bd on metadata.
            _inferred_source = _infer_guidance_standard(n.ref, _std_id)
            if _inferred_source:
                lines.append(f"  ← source: {_inferred_source} implementation guidance")

    if not lines:
        return ""
    return "OBLIGATIONS:\n" + "\n".join(lines)


def _infer_guidance_standard(ref: str, standard_id: str) -> str:
    """Ship 53' — return the authoritative implementation-guidance
    standard for a given ref+standard.

    Mapping:
      ISO 27001 Annex A (A.5.x-A.8.x)  → ISO 27002:2022
      ISO 27001 ISMS body (4.x-10.x)    → ISO 27003:2017
      ISO 27701 A.7.x / B.8.x           → ISO 27701:2019 itself

    ISO 27701 is self-contained: unlike 27001→27002, the 27701 standard
    includes its own implementation guidance inline under each control
    clause (that's where the BD text comes from). Citing ISO 27002 for
    a PIMS control is factually wrong — auditors would flag it —
    because 27002 does not cover PIMS controllers or processors.
    Ship 53'.d fix. Supplementary standards (27018 for cloud
    processors, 29134 for DPIA methodology) are candidates for a
    post-MVP grounding-corpus expansion; not needed for the honest
    baseline.

    Returns "" when no mapping applies (e.g., GDPR articles, ISO
    body clauses whose guidance is fine-tuned elsewhere)."""
    if not ref:
        return ""
    if standard_id == "ISO27001:2022":
        if ref.startswith("A."):
            return "ISO 27002:2022"
        if re.match(r"^\d+\.", ref):
            return "ISO 27003:2017"
    elif standard_id == "ISO27701:2019":
        return "ISO 27701:2019"
    return ""


def _extract_guidance_hint(
    business_description: str,
    max_chars:            int = 220,
    ref:                  str = "",
    standard_id:          str = "",
) -> tuple[str, str]:
    """Extract a compact one-sentence guidance hint from `business_description`
    + return the source-standard attribution the digest should surface.

    Returns `(hint, source)` where `source` is one of:
      - "ISO 27002:2022" — Annex A implementation guidance
      - "ISO 27003:2017" — ISMS implementation guidance (clauses 4-10)
      - "ISO 27004:2016" — measurement / monitoring guidance
      - "ISO 27005:2022" — risk-management guidance
      - "" — no substantive guidance to surface

    Attribution logic (Ship 53 addendum):
      1. If a curated `Per ISO 2700x:YYYY` marker exists, use it as
         authoritative — that beats any ref-based inference.
      2. Otherwise, if the business_description is substantive (>150
         chars distinct from any curated marker paragraphs), fall
         back to inferring the guidance standard from the ref pattern:
           A.5.x-A.8.x on ISO27001  →  ISO 27002:2022 (Annex A)
           4.x-10.x on ISO27001     →  ISO 27003:2017 (ISMS body)
           A.7.x.x / B.8.x.x on ISO27701 → ISO 27002:2022 shape (PIMS)
      3. Trim to `max_chars` on a word boundary.

    Before this change, only 12/93 Annex A controls surfaced a
    guidance hint (those with curated markers). The other 81 had
    27002 paraphrases in business_description that never reached
    the LLM. This function now emits for all of them."""
    if not business_description:
        return ("", "")

    # 1. Curated marker — highest authority.
    markers = {
        "Per ISO 27002:2022": "ISO 27002:2022",
        "Per ISO 27003:2017": "ISO 27003:2017",
        "Per ISO 27004:2016": "ISO 27004:2016",
        "Per ISO 27005:2022": "ISO 27005:2022",
    }
    best_idx: int | None = None
    best_marker_source: str = ""
    for marker, source in markers.items():
        idx = business_description.find(marker)
        if idx >= 0 and (best_idx is None or idx < best_idx):
            best_idx = idx
            best_marker_source = source

    if best_idx is not None:
        tail = business_description[best_idx:]
        m = re.search(r"\.\s", tail)
        sentence = tail if m is None else tail[: m.start() + 1]
        sentence = " ".join(sentence.split())
        if len(sentence) > max_chars:
            sentence = sentence[: max_chars - 1].rsplit(" ", 1)[0] + "…"
        return (sentence, best_marker_source)

    # 2. Unmarked — infer from ref pattern.
    if len(business_description.strip()) < 150:
        return ("", "")   # too thin to bother

    source = ""
    if standard_id == "ISO27001:2022":
        if ref.startswith("A."):
            source = "ISO 27002:2022"        # Annex A implementation guidance
        elif re.match(r"^\d+\.", ref):
            source = "ISO 27003:2017"        # ISMS body implementation guidance
    elif standard_id == "ISO27701:2019":
        # PIMS shares 27002 shape for its implementation guidance.
        source = "ISO 27002:2022"

    if not source:
        return ("", "")

    # Unmarked content is a multi-sentence paraphrase; the useful
    # "how to remediate" material is often in the 2nd-3rd sentences
    # (e.g. "A topic-specific policy on access control should be
    # defined and communicated to all interested parties" comes
    # AFTER the intro "To ensure authorized access..."). Take up to
    # max_chars of the full paraphrase — trim on a word boundary.
    text = " ".join(business_description.split())
    if len(text) > max_chars:
        text = text[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return (text, source)


def _render_demonstrated_by(cf: CaseFile, max_items: int = 8) -> str:
    """When a cited ref is an OBLIGATION (e.g. GDPR Art.32), render its
    DEMONSTRATED BY list — the PROGRAM/EXTENSION obligations that
    contribute to its posture via IMPLEMENTS/SUPPORTS edges.

    Ship 2'.i: this section replaces the "Posture from linked
    primaries" block that used to hang off Layer 2 nodes. The
    demonstrated_by data comes from posture_loader's Phase 2b overlay
    (2026-07-05); see framework-role-model-arc.

    Only fires when at least one cited ref has role='obligation'.
    """
    obligation_refs = [
        r for r in cf.cited_refs if cf.role_of(r) == "obligation"
    ]
    if not obligation_refs:
        return ""

    lines: list[str] = []
    for ref in obligation_refs:
        sources = cf.demonstrated_by(ref)
        if not sources:
            continue
        entries: list[str] = []
        from rag.id_types import ref_of
        for src in sources[:max_items]:
            src_id  = src.get("src_id", "")
            src_ref = ref_of(src_id) if src_id else ""
            src_std = src.get("src_std", "")
            std_lbl = ""
            if src_std == "ISO27001:2022":
                std_lbl = "ISO 27001 "
            elif src_std == "ISO27701:2019":
                std_lbl = "ISO 27701 "
            finding = src.get("finding") or ""
            edge    = (src.get("via_edge") or "").lower()
            entry   = f"{std_lbl}{src_ref}"
            if finding in ("NC", "OFI", "Comply"):
                entry += f" [{finding}]"
            if edge:
                entry += f" via {edge}"
            entries.append(entry)
        if entries:
            lines.append(f"For {ref}:")
            for e in entries:
                lines.append(f"  - {e}")
    if not lines:
        return ""
    return "DEMONSTRATED BY:\n" + "\n".join(lines)


def _render_programs(cf: CaseFile) -> str:
    """List the tenant's enrolled standards grouped by role.

    Ship 2'.i: makes the framework universe explicit at digest time.
    Programs (ISMS spine), extensions (overlays), obligations
    (regulatory demonstrated by programs+extensions).
    """
    scope = getattr(cf.tenant, "scope", None) if cf.tenant else None
    if scope is None:
        return ""

    def _short_labels(standards):
        # Dedup — TenantScope combines direct + inferred, so the same
        # standard can appear multiple times (e.g. GDPR inferred via
        # multiple ISO relationships).
        seen: set[str] = set()
        out: list[str] = []
        for s in (standards or []):
            sid = getattr(s, "id", "")
            if not sid or sid in seen:
                continue
            seen.add(sid)
            if sid == "ISO27001:2022":
                out.append("ISO 27001")
            elif sid == "ISO27701:2019":
                out.append("ISO 27701 (extends ISO 27001)")
            elif sid == "ISO27018:2019":
                out.append("ISO 27018")
            elif sid.startswith("GDPR"):
                out.append("GDPR")
            elif sid.startswith("NIS2"):
                out.append("NIS2")
            else:
                out.append(sid)
        return out

    programs   = _short_labels(getattr(scope, "programs", []) or [])
    extensions = _short_labels(getattr(scope, "extensions", []) or [])
    obligations= _short_labels(getattr(scope, "obligations", []) or [])

    parts: list[str] = []
    if programs:
        parts.append(f"programs: {', '.join(programs)}")
    if extensions:
        parts.append(f"extensions: {', '.join(extensions)}")
    if obligations:
        parts.append(f"obligations: {', '.join(obligations)}")
    if not parts:
        return ""
    return "FRAMEWORKS ENROLLED — " + "; ".join(parts)


# Query types where the LLM needs to ENUMERATE required document items.
# For these, the DOCUMENTS section renders each MUST item as its own
# line (not just a count) so the LLM has the actual text to cite.
# Ship 2'.j: closes eval #31 (ISMS scope statement — needed ≥5 items
# but digest only showed the count).
_ENUMERATE_MUSTS_INTENTS = {
    "document_content",
    "document_inventory",
}


def _render_documents(cf: CaseFile, max_items: int = 5,
                     max_musts_per_doc: int = 20) -> str:
    """Document-context lines when the resolver surfaced doc contexts.

    For document_content / document_inventory queries, ENUMERATE each
    MUST item with its status. For other queries, show just the
    summary count (LLM doesn't need the detail).

    Empty doc_contexts → returns ''.
    """
    ctxs = cf.doc_contexts
    if not ctxs:
        return ""
    enumerate_musts = cf.question_type in _ENUMERATE_MUSTS_INTENTS
    lines: list[str] = []
    for _nid, ctx in list(ctxs.items())[:max_items]:
        ref = getattr(ctx, "control_ref", "") or ""
        title = getattr(ctx, "title", "") or ""
        try:
            present    = ctx.present_must
            total_must = len(getattr(ctx, "must_contain", []) or [])
            uploaded   = getattr(ctx, "has_document_uploaded", False)
            if uploaded:
                header = f"- {ref}: {title} — {len(present)}/{total_must} required items present"
            else:
                header = f"- {ref}: {title} — no document uploaded ({total_must} required items)"
            lines.append(header)
            if enumerate_musts:
                for item in list(getattr(ctx, "must_contain", []) or [])[:max_musts_per_doc]:
                    text = (getattr(item, "text", "") or "").strip()
                    if not text:
                        continue
                    status = getattr(item, "status", None)
                    if status == "present":
                        mark = "✓"
                    elif status in ("missing", None):
                        mark = "•"
                    else:
                        mark = "?"
                    # Truncate very long items to keep the digest lean.
                    if len(text) > 140:
                        text = text[:139] + "…"
                    lines.append(f"    {mark} {text}")
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


def _render_risks(cf: CaseFile, max_items: int = 8, max_chars_each: int = 180) -> str:
    """Ship 14'.e — RISKS section for POSTURE_RISK queries.

    Fixed-slot digest section per case-file discipline (Ship 2'):
    - empty when cf.risks is empty; no per-taxonomy branching
    - top-N by risk_score DESC (already sorted by fetch helper)
    - each row: external_ref + treatment_status + threat + score/residual
    - linked controls rendered inline WITHOUT role split
      (program/extension/obligation refs side-by-side per Ship
      14'.a addendum framework-role-model discipline)
    - budget target: ≤300 tokens for 8 rows

    Format per line (single line each — no wrapping):
      - R-042 [Mitigate, in_progress]  Ransomware in SaaS backups
          score 15/25  residual 8/25  linked: A.5.15, A.8.13
    """
    risks = getattr(cf, "risks", None) or []
    if not risks:
        return ""

    lines: list[str] = []
    shown = risks[:max_items]
    total = len(risks)
    header = (
        f"RISKS (showing {len(shown)} of {total} open):"
        if total > len(shown) else "RISKS:"
    )
    lines.append(header)

    for r in shown:
        ext_ref  = r.get("external_ref") or "(no-ref)"
        threat   = (r.get("threat") or r.get("vulnerability") or "").strip()
        opt      = r.get("treatment_option") or "?"
        status   = r.get("treatment_status") or "?"
        score    = r.get("risk_score")
        residual = r.get("residual_risk_level")
        review   = r.get("review_date")

        # Line 1: ref + tags + threat
        threat_short = threat[:max_chars_each] + ("…" if len(threat) > max_chars_each else "")
        lines.append(f"- {ext_ref} [{opt}, {status}]  {threat_short}")

        # Line 2: scores + linked controls (compact)
        parts = []
        if score is not None:
            parts.append(f"score {score}/25")
        if residual is not None:
            parts.append(f"residual {residual}/25")
        if review:
            parts.append(f"review {review}")

        # Framework role model discipline: render linked controls
        # side-by-side. Sort by role rank so reading order is
        # program → extension → obligation → guidance.
        linked = r.get("linked_controls") or []
        if linked:
            rank = {"program": 1, "extension": 2, "obligation": 3, "guidance": 4}
            linked_sorted = sorted(linked, key=lambda c: rank.get(c.get("role"), 9))
            refs = [c.get("ref", "?") for c in linked_sorted[:6]]
            if len(linked_sorted) > 6:
                refs.append(f"+{len(linked_sorted) - 6} more")
            parts.append("linked: " + ", ".join(refs))

        if parts:
            lines.append("    " + "  ".join(parts))

    return "\n".join(lines)


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


# ── EDPB / WP29 guidance grounding (Ship 53'.f) ────────────────────────
#
# For any cited GDPR ref, fetch 2-3 EDPB / WP29 guidance chunks from
# the edpb_guidelines Chroma collection. Attributes each chunk to the
# specific EDPB doc (e.g., "EDPB 07/2020") so the LLM can cite the
# authoritative source in remediation cards — same auditor-defensible
# grounding pattern as ISO 27002 for A.5.x-A.8.x, but for GDPR.
#
# Fires only when at least one cited ref is a GDPR article. Total
# added text is capped to keep the digest token-budget-friendly.

_EDPB_COLLECTION_NAME = "edpb_guidelines"
_EDPB_MAX_CHUNKS_PER_REF = 2
_EDPB_MAX_CHARS_PER_CHUNK = 500
_EDPB_TOTAL_CHAR_CAP = 2500

# Module-level Chroma client cache. Lazily initialised on first use.
_edpb_collection = None


def _get_edpb_collection():
    """Lazy-init handle to the edpb_guidelines Chroma collection.

    Uses VectorIndexer.get_collection so the returned handle carries
    the correct 3072-dim OpenAI embedding function (matching how
    the collection was indexed). A bare
    `chromadb.HttpClient().get_collection()` would default to the
    onnx 384-dim embedder and every query would raise a dimension-
    mismatch error.

    Cached at module scope so repeated digest builds within one
    process share the client. Returns None if the collection is not
    available (fresh install, indexing not yet run) — the digest
    falls through gracefully with no EDPB section.
    """
    global _edpb_collection
    if _edpb_collection is not None:
        return _edpb_collection
    try:
        from vector.indexer import VectorIndexer
        from rag.embedding_config import EMBED_MODEL_STANDARD
        indexer = VectorIndexer(
            provider="openai",
            embedding_model=EMBED_MODEL_STANDARD,
        )
        _edpb_collection = indexer.get_collection(_EDPB_COLLECTION_NAME)
        return _edpb_collection
    except Exception as e:
        logger.debug("EDPB collection unavailable: %s", e)
        _edpb_collection = None
        return None


def _fetch_edpb_chunks_for_ref(ref: str, query_hint: str = "") -> list[dict]:
    """Return up to _EDPB_MAX_CHUNKS_PER_REF guidance chunks whose
    metadata `interprets_articles` includes the given GDPR ref.

    Strategy: semantic search on `edpb_guidelines` with the ref plus
    a topic hint (the article's own title / obligation text), then
    post-filter results by metadata to keep only chunks that actually
    interpret this article.

    Ship 53'.f note: EDPB docs rarely mention the article number
    verbatim in prose ("Art.35" appears in a wp248 chunk maybe once
    per page vs. "DPIA" every paragraph), so the ref alone is a
    weak semantic signal. We overfetch (n_results large enough to
    survive post-filter) and rely on the caller enriching
    `query_hint` with the article title.

    Returns empty list if the collection isn't available or no
    matching chunks exist.
    """
    coll = _get_edpb_collection()
    if coll is None:
        return []

    query_text = f"{ref} {query_hint}".strip() if query_hint else ref
    try:
        # Overfetch so post-filter has enough population — EDPB semantic
        # relevance and metadata-filter relevance are often disjoint.
        results = coll.query(
            query_texts=[query_text],
            n_results=30,
            include=["documents", "metadatas"],
        )
    except Exception as e:
        logger.debug("EDPB query failed for %s: %s", ref, e)
        return []

    matches: list[dict] = []
    docs_row = (results.get("documents") or [[]])[0]
    metas_row = (results.get("metadatas") or [[]])[0]
    for doc, meta in zip(docs_row, metas_row):
        if not meta:
            continue
        # `interprets_articles` is stored as comma-joined string.
        interprets = (meta.get("interprets_articles") or "").split(",")
        interprets = [x.strip() for x in interprets if x.strip()]
        if ref not in interprets:
            continue
        matches.append({
            "source_doc":    meta.get("source_doc", "EDPB"),
            "section_title": (meta.get("section_title") or "")[:80],
            "text":          doc or "",
        })
        if len(matches) >= _EDPB_MAX_CHUNKS_PER_REF:
            break
    return matches


def _render_edpb_guidance(cf: CaseFile) -> str:
    """Render the EDPB GUIDANCE: section for any cited GDPR refs.

    Ship 53'.f — closes the "GDPR shallowness" gap. Previously the
    LLM cited only the article verbatim + training-data-drafted
    remediation. Now it sees 2-3 EDPB guidance snippets attributed
    to specific documents (EDPB 07/2020, WP29 wp248 rev.01, etc.)
    so the remediation cards can name the authoritative source the
    same way ISO 27001 answers cite ISO 27002.

    Only fires when at least one cited ref is a GDPR article. Total
    output capped at _EDPB_TOTAL_CHAR_CAP to keep the digest token-
    friendly.
    """
    cited_refs = cf.cited_refs or []
    gdpr_refs = [r for r in cited_refs if r.startswith("Art.")]
    if not gdpr_refs:
        return ""

    # Build a per-ref topic hint from the CaseFile's own nodes.
    # EDPB docs use topical language ("DPIA", "controller-processor",
    # "supplementary measures") rather than article numbers verbatim,
    # so the semantic query needs the article's *subject matter* to
    # rank correctly. Fall back to cf.query if no node title is found.
    ref_to_title: dict[str, str] = {}
    for n in cf.all_nodes():
        if n.ref in gdpr_refs and n.ref not in ref_to_title:
            title = (getattr(n, "title", "") or "").strip()
            if title:
                ref_to_title[n.ref] = title

    tenant_query_hint = (cf.query or "")[:150]

    lines: list[str] = []
    total_chars = 0
    for ref in gdpr_refs:
        title = ref_to_title.get(ref, "")
        query_hint = f"{title} {tenant_query_hint}".strip() if title else tenant_query_hint
        chunks = _fetch_edpb_chunks_for_ref(ref, query_hint=query_hint)
        for ch in chunks:
            text = ch["text"].strip()
            if len(text) > _EDPB_MAX_CHARS_PER_CHUNK:
                text = text[: _EDPB_MAX_CHARS_PER_CHUNK - 1] + "…"
            # Attribution: [EDPB 07/2020] Art.28 — section title
            #   text
            heading = f"[{ch['source_doc']}] {ref}"
            if ch["section_title"]:
                heading += f" — {ch['section_title']}"
            line = f"{heading}\n  {text}"
            if total_chars + len(line) > _EDPB_TOTAL_CHAR_CAP:
                break
            lines.append(line)
            total_chars += len(line)
        if total_chars >= _EDPB_TOTAL_CHAR_CAP:
            break

    if not lines:
        return ""
    return "EDPB GUIDANCE (authoritative implementation guidance — cite the source doc verbatim in remediation actions):\n" + "\n\n".join(lines)


# ── Deictic hint (from rank_and_answer's prior_turn_block logic) ─────

_DEICTIC_RE = re.compile(
    r"\b(this|that|it|those|these|what about|how about|tell me more|"
    r"is it|are they|the (policy|plan|procedure|register|document|doc))\b",
    re.IGNORECASE,
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


# ── Intent-aware section budgets ─────────────────────────────────────
#
# Ship 2'.i: The digest keeps its fixed-slots layout, but the section
# budgets and ORDER shift based on question_type. Rationale:
#
#   For POSTURE_CHECK / GAP_ANALYSIS the LLM needs findings first —
#   POSTURE section is prominent, obligation text is context.
#
#   For DEFINITION / STANDARD_KNOWLEDGE the LLM needs the control's
#   obligation text prominently. Posture is background — otherwise
#   the LLM biases toward enumerating tenant findings when asked
#   "what is A.6.4?" (Ship 2'.h eval regression #22, #23, #213, #214).
#
# This is soft branching — same slot structure, different weights.
# NOT a per-taxonomy dispatch table (which would re-introduce the
# Ship 2 duplication problem).

# Intent groups. Anything not listed uses posture-first defaults.
_DEFINITION_INTENTS = {
    "definition",
    "standard_knowledge",
    "definition_query",
}


@dataclass
class _DigestPlan:
    """Section ordering + budgets for one digest render."""
    posture_limit:       int
    posture_body_chars:  int
    obligation_limit:    int
    obligation_chars:    int
    obligations_first:   bool     # if True, put OBLIGATIONS above POSTURE


def _plan_for(cf: CaseFile) -> _DigestPlan:
    """Choose section budgets/ordering based on question_type."""
    if cf.question_type in _DEFINITION_INTENTS:
        # DEFINITION mode: obligations lead, posture is secondary.
        return _DigestPlan(
            posture_limit       = 3,
            posture_body_chars  = 80,     # tighter — posture is context
            obligation_limit    = 5,
            obligation_chars    = 400,    # was 160; large enough for
                                          # "Disciplinary process" +
                                          # opening sentence
            obligations_first   = True,
        )
    # Default: posture-focused (matches Ship 2'.a-h behaviour).
    return _DigestPlan(
        posture_limit       = 10,
        posture_body_chars  = 120,
        obligation_limit    = 5,
        obligation_chars    = 160,
        obligations_first   = False,
    )


# ── Main digest builder ──────────────────────────────────────────────

def build_prompt_digest(
    cf: CaseFile,
    posture_limit:    int | None = None,
    obligation_limit: int | None = None,
    document_limit:   int = 5,
) -> str:
    """Compact render of the CaseFile for the LLM user-prompt slot.

    Section budgets and ORDER are chosen from `_plan_for(cf)` — a
    soft-branching helper that shifts weights based on question_type.
    Explicit `posture_limit` / `obligation_limit` kwargs override the
    plan (used by tests + tuning).

    Returns a plain string. Sections that would be empty are omitted
    entirely — the LLM sees a lean prompt.
    """
    plan = _plan_for(cf)
    if posture_limit is None:
        posture_limit = plan.posture_limit
    if obligation_limit is None:
        obligation_limit = plan.obligation_limit

    sections: list[str] = []

    def _add(section: str):
        if section:
            sections.append(section)

    _add(_render_query(cf))
    _add(_render_deictic_hint(cf))
    _add(_render_incidents(cf))

    # Ship 2'.i: role-aware section ordering.
    # If any cited ref is an OBLIGATION (regulatory — GDPR Art., NIS2,
    # DORA, HIPAA, PCI DSS), the DEMONSTRATED BY section is the primary
    # answer surface. Follow with OBLIGATIONS text (of ALL cited refs)
    # then POSTURE.
    # If no cited ref is an obligation OR the query is definition-style,
    # fall through to the layout in _plan_for (obligations-first for
    # definition / posture-first otherwise).
    has_cited_obligation = any(
        cf.role_of(r) == "obligation" for r in (cf.cited_refs or [])
    )

    if has_cited_obligation:
        # OBLIGATION-cited: lead with the DEMONSTRATED BY surface,
        # then OBLIGATIONS text so the LLM has the obligation context,
        # then POSTURE ranked.
        _add(_render_demonstrated_by(cf))
        _add(_render_obligations(
            cf, max_items=obligation_limit,
            max_chars_each=plan.obligation_chars,
        ))
        _add(_render_posture(
            cf, limit=posture_limit,
            body_chars=plan.posture_body_chars,
        ))
    elif plan.obligations_first:
        # DEFINITION mode: OBLIGATIONS lead, then XFW bridges,
        # then POSTURE as background.
        _add(_render_obligations(
            cf, max_items=obligation_limit,
            max_chars_each=plan.obligation_chars,
        ))
        _add(_render_xfw_bridges(cf))
        _add(_render_posture(
            cf, limit=posture_limit,
            body_chars=plan.posture_body_chars,
        ))
    else:
        # Default: POSTURE leads (gap_analysis / posture_check).
        _add(_render_posture(
            cf, limit=posture_limit,
            body_chars=plan.posture_body_chars,
        ))
        _add(_render_xfw_bridges(cf))
        _add(_render_obligations(
            cf, max_items=obligation_limit,
            max_chars_each=plan.obligation_chars,
        ))

    _add(_render_edpb_guidance(cf))  # Ship 53'.f — GDPR consulting grounding
    _add(_render_documents(cf, max_items=document_limit))
    _add(_render_risks(cf))        # Ship 14'.e — POSTURE_RISK section
    _add(_render_session(cf))
    _add(_render_programs(cf))     # framework-role-model context
    _add(_render_scope(cf))        # standards list (kept for continuity)

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
2. Report posture only from the tags in the POSTURE / DEMONSTRATED
   BY sections:
     NC (Non-Conformity) — required control absent or ineffective;
     OFI (Opportunity for Improvement) — control exists with gaps;
     Comply — control in place with evidence.
   The -DRAFT suffix means posture is not yet auditor-confirmed —
   keep the [DRAFT] tag when it's on the source.
3. FRAMEWORK ROLES — every enrolled standard has one role:
     PROGRAM (ISMS spine): ISO 27001 — carries direct posture on
       every control.
     EXTENSION (overlay on a program): ISO 27701 extends ISO 27001
       with PIMS — carries direct posture on its extension controls.
     OBLIGATION (legal/regulatory mandate): GDPR, NIS2, DORA — its
       articles carry posture partly from tenant-asserted findings
       AND partly from DEMONSTRATED-BY propagation (ISO 27001 /
       ISO 27701 controls that implement the article contribute).
   When answering about an OBLIGATION ref: describe the article's
   requirement + cite the DEMONSTRATED BY sources that implement
   it. When answering about a PROGRAM or EXTENSION ref: describe
   its own control text + posture directly.
   For a broad "are we [OBLIGATION-framework] compliant?" question
   (e.g. "are we GDPR compliant?", "are we NIS2 compliant?"):
   NEVER answer with a flat "you are / are not compliant" verdict.
   Instead explain the compliance MODEL: this obligation framework
   is demonstrated by the tenant's programs + extensions, and
   summarise where the programs stand on the article-level
   controls. Use the DEMONSTRATED BY data to name the specific
   program/extension that carries the obligation
   (e.g. "GDPR is demonstrated via ISO 27701 (PIMS extension of
   ISO 27001)"). Then summarise the current posture across the
   articles the programs implement.
4. Lead with NC findings, then OFI, then Comply. Never list
   "not yet assessed" or omitted controls as gaps. When the query
   asks about "gaps" — use the word "gap(s)" naturally in the
   answer. NC findings ARE the tenant's compliance gaps; mirror
   the query's vocabulary rather than switching to
   "non-conformities" exclusively.
5. Cite frameworks only from the FRAMEWORKS ENROLLED line.
   Frameworks outside scope are not implemented by the tenant and
   must never appear in your answer.
6. Cite controls with the readable framework prefix:
   "ISO 27001 A.5.18", "GDPR Art. 32", "ISO 27001 clause 9.2",
   "ISO 27701 A.7.2.4".
   ISO body clauses (5.x/6.x/7.x/8.x/9.x/10.x) are NOT Annex A —
   never write "A.9.2" or "A.10.1".
7. If the DEICTIC WITHOUT CONTEXT hint is present, follow it —
   ask which entity the user meant rather than inventing one.
8. For "what is X" / "what does X mean" / "what is control X"
   questions: LEAD with the control's official name from the
   OBLIGATIONS section, quoted verbatim. Do not paraphrase the
   title. Then briefly explain what the control requires from
   the obligation text. Only mention posture AFTER defining.
   Example: "A.6.4 (Disciplinary process) requires..." NOT
   "A.6.4 is related to information security management".
9. When defining a compliance acronym (NC, OFI, ISMS, DPIA, DPO,
   RoPA, DSAR, DSR, DPA, PIMS, SoA), spell out the full phrase:
   "OFI (Opportunity for Improvement)" — the acronym alone is
   insufficient for a definition answer.
10. REMEDIATION queries ("how do I remediate X", "how do we
    improve X", "what to do about X"): ground each recommendation
    in the guidance authority attached to the cited control. Two
    markers in the digest carry that authority:
      - `→ guidance (ISO ...):` continuation line (curated
        paraphrase, present when obligation text and BD are both
        available)
      - `← source: ISO ...:YYYY implementation guidance` tag line
        (present when the main obligation text IS the ISO 27002
        paraphrase itself — the tag names which standard it comes
        from)
    Either marker means: cite the ISO standard explicitly in your
    answer. Example: "ISO 27002:2022 §5.15 recommends defining a
    topic-specific access control policy communicated to all
    relevant teams — start with the periodic review, which is your
    biggest gap...". Prioritise by BIGGEST GAP first: leaves with
    fewer of their required items present come before near-complete
    leaves. Name the specific missing MUSTs from the POSTURE
    section rather than saying "the documentation" or "the policy"
    generically. Use plain business language over ISO phrasing
    where possible ("relevant teams" over "interested parties",
    "policy for this topic" over "topic-specific policy").

Be direct and actionable. State what's missing and what to do.
End when the actionable content ends — do not append closing
paragraphs summarising what the user should do (the UI renders
next-actions separately)."""


def build_system_prompt(cf: CaseFile) -> str:
    """Render the slim system prompt with tenant_name filled in."""
    return _SLIM_SYSTEM.format(tenant_name=cf.tenant_name or "the tenant")


def build_structured_system_prompt(cf: CaseFile) -> str:
    """Ship 18'.b — slim system prompt PLUS the JSON output-format
    rules. Used when calling the LLM with response_format=json_object.

    Same content rules as the prose prompt; the OUTPUT FORMAT section
    reshapes the response into intro + actions[] JSON. `related[]` is
    NOT emitted — the backend builds it deterministically."""
    from rag.casefile.answer_schema import LLM_OUTPUT_RULES
    base = _SLIM_SYSTEM.format(tenant_name=cf.tenant_name or "the tenant")
    return base + "\n\n" + LLM_OUTPUT_RULES


# ── Combined helper for downstream wiring ────────────────────────────

def build_prompt_pair(cf: CaseFile) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) as a pair — this is what
    rank_and_answer's _call_llm expects."""
    # Ship 44'.d — span for case-file digest build. Tracks token
    # estimates so we can see when digests grow unexpectedly (case-file
    # discipline's whole point is compact digests).
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    with _tracer.start_as_current_span("arion.casefile.build_prompt_pair") as span:
        system_prompt = build_system_prompt(cf)
        user_prompt = build_prompt_digest(cf)
        try:
            span.set_attribute("arion.casefile.system_chars", len(system_prompt))
            span.set_attribute("arion.casefile.user_chars", len(user_prompt))
            # ~4 chars per token rough estimate
            span.set_attribute("arion.casefile.system_tokens_est",
                                len(system_prompt) // 4)
            span.set_attribute("arion.casefile.user_tokens_est",
                                len(user_prompt) // 4)
            span.set_attribute("arion.casefile.n_posture_lines",
                                len(getattr(cf, 'posture_lines', []) or []))
            span.set_attribute("arion.casefile.n_bridges",
                                len(getattr(cf, 'bridges', []) or []))
        except Exception:
            pass
        return system_prompt, user_prompt


def build_structured_prompt_pair(cf: CaseFile) -> tuple[str, str]:
    """Ship 18'.b — (structured_system_prompt, user_digest) pair for
    the JSON-mode LLM call. The digest itself is identical to the
    prose path; only the system prompt gains the OUTPUT FORMAT rules."""
    # Ship 44'.d — span mirrors build_prompt_pair so both call sites
    # produce the same telemetry shape.
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    with _tracer.start_as_current_span(
        "arion.casefile.build_structured_prompt_pair"
    ) as span:
        system_prompt = build_structured_system_prompt(cf)
        user_prompt = build_prompt_digest(cf)
        try:
            span.set_attribute("arion.casefile.system_chars", len(system_prompt))
            span.set_attribute("arion.casefile.user_chars", len(user_prompt))
            span.set_attribute("arion.casefile.system_tokens_est",
                                len(system_prompt) // 4)
            span.set_attribute("arion.casefile.user_tokens_est",
                                len(user_prompt) // 4)
            span.set_attribute("arion.casefile.n_posture_lines",
                                len(getattr(cf, 'posture_lines', []) or []))
            span.set_attribute("arion.casefile.n_bridges",
                                len(getattr(cf, 'bridges', []) or []))
        except Exception:
            pass
        return system_prompt, user_prompt
