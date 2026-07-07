"""
ArionComply — LangGraph Pipeline

Replaces orchestrator.py (~791 lines) with a typed state graph.
The existing QueryClassifier, GraphExpander, ContextAssembler, and
LLMAnswer classes are unchanged — they become graph nodes.

Graph structure:
                    ┌─────────┐
    query ──────────│ CLASSIFY │
                    └────┬────┘
              ┌──────────┤
              │          │
           CLEAR      AMBIGUOUS
              │          │
              ▼          ▼
          ┌───────┐  ┌─────────┐
          │RETRIEVE│  │ CLARIFY │──── END (return question)
          └───┬───┘  └─────────┘
              │
              ▼
          ┌────────┐
          │ ANSWER │
          └───┬────┘
              │
              ▼
          ┌──────────────┐
          │ UPDATE_SESSION│
          └──────┬────────┘
                 │
                END

Checkpointing:
  Dev:  SqliteSaver("~/.arioncomply/sessions.db")
  Prod: PostgresSaver(DATABASE_URL)
"""
from __future__ import annotations

import os
import time
from typing import Literal, Optional

from langgraph.graph import StateGraph, END

from rag.arion_state    import ArionState, make_initial_state
from rag.classifier     import (
    QueryClassifier, TenantProfile, IntakeState,
)
from rag.orchestrator   import OVERRIDE_PHRASES
from rag.context_assembler import ContextAssembler
from rag.graph_expander    import GraphExpander
from rag.llm_answer        import LLMAnswer
from rag.chain_logger      import get_logger


class _NullLogger:
    """Fallback when chain logging isn't enabled — get_logger() returns
    None in that case. Avoids 'NoneType has no attribute warning'."""
    def warning(self, *args, **kwargs): pass
    def info(self,    *args, **kwargs): pass
    def error(self,   *args, **kwargs): pass
    def debug(self,   *args, **kwargs): pass
import re as _re_graph
import re

# ── Upload status query helpers ───────────────────────────────────────────────

# "uploaded" is the canonical verb, but users naturally say submitted /
# delivered / provided / shared / sent in. Treat them as synonyms.
_UPLOAD_VERB = r'(?:uploaded|submitted|delivered|provided|shared|sent\s+in)'

_UPLOAD_STATUS_PATTERNS = [
    re.compile(rf'\bhave\s+we\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(rf'\bdid\s+we\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(rf'\b(?:is|are)\s+(?:our|the)\s+[\w\s]{{2,40}}(?:policy|procedure|plan|playbook|document)s?\s+(?:{_UPLOAD_VERB}|in\s+the\s+system|on\s+the\s+platform)\b', re.IGNORECASE),
    re.compile(rf'\bwhich\s+documents?\s+(?:have\s+(?:not|yet)\s+been|are\s+(?:not|still)?)\s+{_UPLOAD_VERB}\b', re.IGNORECASE),
    re.compile(r'\bshow\s+(?:me\s+)?(?:missing|unuploaded)\s+documents?\b', re.IGNORECASE),
    # "what/which documents are missing?", "are any documents missing?"
    re.compile(r'\b(?:what|which|any)\s+documents?\s+(?:are\s+)?(?:missing|unuploaded)\b', re.IGNORECASE),
    re.compile(r'\bdocuments?\s+(?:are\s+)?(?:missing|unuploaded|not\s+(?:yet\s+)?(?:uploaded|submitted))\b', re.IGNORECASE),
]


def _is_upload_status_query(query: str) -> bool:
    return any(p.search(query) for p in _UPLOAD_STATUS_PATTERNS)


# ── Deictic-only query detection ───────────────────────────────────────────
# Short follow-up queries that lean on prior-turn context: "this", "that",
# "it", "what about X?", "tell me more", "is it ...?". When the prior turn
# was an inventory list (no single entity), these queries have no referent
# to resolve. Without short-circuiting, the retriever pulls whatever
# default nodes match the topic word ("policy"), the LLM uses them, and
# the user gets a NC dump that's unrelated to anything they meant.
# See [[conversational-context-routing-followup]].

_DEICTIC_PHRASES_RE = re.compile(
    r"\b(this|that|it|those|these|what\s+about|how\s+about|"
    r"tell\s+me\s+more|is\s+it|are\s+they|"
    r"the\s+(policy|plan|procedure|register|document|doc)s?)\b",
    re.IGNORECASE,
)

# Explicit refs that disqualify a query from "deictic-only". If the user
# names A.5.18 / Art.32 / DOC006 / a control title, the retriever has a
# real referent and we should not short-circuit.
_EXPLICIT_REF_RE = re.compile(
    r"\b(?:[Aa]\.\d+(?:\.\d+)*"
    r"|Art(?:icle)?\.?\s?\d+(?:\(\d+\))?"
    r"|\d+\.\d+(?:\.\d+)?"
    r"|DOC\d{3,4}"
    r"|CD-[A-Z]{2,4}-\d{3,4})\b",
    re.IGNORECASE,
)


def _is_deictic_only_query(query: str) -> bool:
    """True when the query relies on prior-turn context (deictic words /
    "the X" / "tell me more") AND names no explicit control / doc ref of
    its own. Used to short-circuit retrieval when no last_entity exists
    to anchor the deictic referent."""
    if not query or len(query.split()) > 10:
        # Long queries usually carry their own context. Threshold tuned to
        # catch "what about the policy" (5 words), "tell me more about it"
        # (5 words), "is the access control policy compliant?" (7 words)
        # would NOT match because it names a doc.
        return False
    if _EXPLICIT_REF_RE.search(query):
        return False
    return bool(_DEICTIC_PHRASES_RE.search(query))


_DEICTIC_CLARIFY_RESPONSE = (
    "I'm not sure which document or control you're asking about. Could "
    "you name it specifically? For example:\n"
    "  • \"Is the access control policy compliant?\"\n"
    "  • \"What's the status of A.5.18?\"\n"
    "  • \"Have we uploaded our business continuity policy?\"\n"
    "If you meant to follow up on something from earlier, the prior "
    "turn may have been a list rather than a single doc — happy to "
    "drill into any item by name."
)


# ── Deterministic posture-enumeration compose (L3 hallucination guard) ─────
#
# For POSTURE_CHECK queries that ask to ENUMERATE findings ("what is our X
# compliance status", "what are our NCs", "where do we stand"), the truth
# IS the posture data. The LLM rank step adds no signal, only risk: same
# query → different controls selected run-to-run, missing titles, broken
# markdown when the LLM picks an unusual list shape.
#
# This compose path bypasses rank_and_answer for matching queries and
# formats posture deterministically. Free-form posture questions
# ("explain how A.5.18 affects us") still route through the LLM.
# See [[posture-claim-hallucination-guard]] L3.

_POSTURE_ENUMERATION_RE = re.compile(
    r"""
    \b(?:
       # "what is/are our [topic] compliance/posture status"
       what(?:\'s|\s+is|\s+are)\s+our\s+[\w\s\-]{0,80}\s+(?:compliance|posture)\s+(?:status|finding|posture)\b
       # "what is/are our compliance/posture status"
     | what(?:\'s|\s+is|\s+are)\s+our\s+(?:compliance|posture)\s+(?:status|finding|posture)\b
       # "what are our (main/compliance) NCs / OFIs / gaps / findings"
     | what(?:\'s|\s+is|\s+are)\s+our\s+
         (?:main\s+|top\s+|biggest\s+|compliance\s+|posture\s+|open\s+|outstanding\s+)*
         (?:NCs?|non[- ]?conform\w*|OFIs?|opportunit\w+\s+for\s+improvement|gaps?|findings?|non[- ]?compliance(?:s)?)\b
       # "where do/are we stand[ing]" / "where are we (on X)"
     | where\s+(?:do|are)\s+we\s+(?:stand|standing|at)\b
     | where\s+are\s+we\s+(?:on|with|for)\s+
       # "list / show our NCs / gaps / findings / posture"
     | (?:list|show)\s+(?:me\s+)?(?:our\s+|the\s+|all\s+)?
         (?:NCs?|non[- ]?conform\w*|OFIs?|opportunit\w+\s+for\s+improvement|
            gaps?|findings?|posture|status|compliance\s+status)\b
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _is_posture_enumeration_query(query: str) -> bool:
    return bool(query) and bool(_POSTURE_ENUMERATION_RE.search(query.strip()))


_STANDARD_LABEL_MAP = {
    "ISO27001:2022":  "ISO 27001",
    "ISO27001:2013":  "ISO 27001",
    "GDPR:2016/679":  "GDPR",
    "GDPR":           "GDPR",
    "ISO27002:2022":  "ISO 27002",
    "ISO27701:2019":  "ISO 27701",
    "ISO27701:2022":  "ISO 27701",
}


def _label_for_standard(standard_id: str) -> str:
    return _STANDARD_LABEL_MAP.get(standard_id, standard_id.split(":")[0])


# Engine-reason artifact "role" names → human-readable form. Roles come
# from posture_loader's missing-artifacts list and use snake_case from
# the curated EvidenceRequirement spec. Render them in natural language
# so the row reads as instructions, not as field identifiers.
_ROLE_LABELS = {
    "procedure":                     "operating procedure",
    "register":                      "register",
    "review_record":                 "review record",
    "scope_note":                    "scope note",
    "revocation_record":             "revocation records",
    "configuration_baseline":        "configuration baseline",
    "monitoring_record":             "monitoring records",
    "communication_record":          "communication records",
    "approval":                      "approval records",
    "discovery_record":              "discovery records",
    "policy":                        "policy document",
    "matrix":                        "controls matrix",
    "directive":                     "directive",
    "asset_register":                "asset register",
    "contact_register":              "contact register",
    "non_return_record":             "non-return records",
    "return_record":                 "return records",
    "disposal_record":               "disposal records",
    "application_record":            "application records",
    "closure_record":                "closure records",
    "exercise_record":               "exercise / drill records",
    "activation_record":             "activation records",
    "operating_procedures_register": "operating procedures register",
    "schedule_register":             "schedule register",
    "nonconformity_register":        "nonconformity register",
    "isms_scope":                    "ISMS scope statement",
    "manual":                        "manual",
    "statement_of_applicability":    "statement of applicability",
    # Second-batch additions — evidence_types curated but not previously
    # labelled. Keep lowercase for mid-sentence prose fit.
    "agreement_template":            "agreement template",
    "approval_record":               "approval record",
    "arrangement":                   "arrangement",
    "audit_programme":               "audit programme",
    "audit_record":                  "audit record",
    "audit_report":                  "audit report",
    "breach_notification":           "breach notification",
    "change_record":                 "change record",
    "charter":                       "charter",
    "classification_scheme":         "classification scheme",
    "communication_evidence":        "communication evidence",
    "configuration_record":          "configuration record",
    "data_flow_inventory":           "data flow inventory",
    "data_processing_agreement":     "data processing agreement",
    "decision_record":               "decision record",
    "designation_document":          "designation document",
    "dsar_response":                 "data subject request response",
    "erasure_procedure":             "erasure procedure",
    "intake_process":                "intake process",
    "lawful_basis_register":         "lawful basis register",
    "management_directive":          "management directive",
    "management_review_minutes":     "management review minutes",
    "plan":                          "plan",
    "privacy_notice":                "privacy notice",
    "process_map":                   "process map",
    "publication_record":            "publication record",
    "records_of_processing":         "records of processing",
    "rectification_procedure":       "rectification procedure",
    "responsibility_matrix":         "responsibility matrix",
    "risk_assessment":               "risk assessment",
    "risk_assessment_record":        "risk assessment record",
    "risk_treatment_plan":           "risk treatment plan",
    "risk_treatment_record":         "risk treatment record",
    "risk_register":                 "risk register",
    "scope_statement":               "scope statement",
    "segregation_matrix":            "segregation of duties matrix",
    "test_log":                      "test log",
    "training_programme":            "training programme",
    "asset_inventory":               "asset inventory",
    "evidence":                      "evidence artifact",
    "other":                         "supporting document",
}


def _pretty_role(role: str) -> str:
    return _ROLE_LABELS.get(role, role.replace("_", " "))


def _prettify_reason(reason: str) -> str:
    """
    Convert an engine reason string to readable form.

    Input shape (from posture_loader._compose):
      "ALL: 0/4 children satisfied; missing artifacts of type: a, b;
       partial: leaf_role (X/Y — missing: ...)"

    Conservative rewrites: counts to "X of Y requirements met",
    "missing artifacts of type" to "still needed", snake_case roles
    to natural words. Partial-leaf text is light-touch since the
    inner detail is unpredictable.
    """
    if not reason:
        return ""

    segments = [s.strip() for s in reason.split(";")]
    out: list[str] = []

    for seg in segments:
        if not seg:
            continue
        # "ALL: X/Y children satisfied" or "X/Y children satisfied"
        m = re.match(
            r"^(?:ALL:\s*)?(\d+)\s*/\s*(\d+)\s+children\s+satisfied\s*(.*)$",
            seg, re.IGNORECASE,
        )
        if m:
            sat, total, tail = m.group(1), m.group(2), m.group(3).strip()
            text = f"{sat} of {total} requirements met"
            if tail:
                text += f" {tail}"
            out.append(text)
            continue
        # "missing artifacts of type: a, b, c"
        m = re.match(r"^missing\s+artifacts\s+of\s+type:\s*(.+)$", seg, re.IGNORECASE)
        if m:
            roles = [r.strip() for r in m.group(1).split(",") if r.strip()]
            pretty = [_pretty_role(r) for r in roles]
            out.append("still needed: " + ", ".join(pretty))
            continue
        # "partial: leaf_role (X/Y — missing: ...), ..."
        m = re.match(r"^partial:\s*(.+)$", seg, re.IGNORECASE | re.DOTALL)
        if m:
            partial_text = m.group(1)
            # Replace snake_case role tokens with pretty form. Only
            # rewrites tokens we recognise; unknown words pass through.
            partial_text = re.sub(
                r"\b([a-z][a-z0-9_]+_[a-z0-9_]+)\b",
                lambda mm: _pretty_role(mm.group(1)),
                partial_text,
            )
            out.append("partial: " + partial_text)
            continue
        out.append(seg)

    return "; ".join(out)


def _fetch_auditor_attestations(tenant_id: str) -> dict[str, dict]:
    """Return {control_ref → {report, attested_at, excerpt}} for the most
    recent approved finding from a doc with evidence_type='audit_report'
    on each control. Used to surface auditor context alongside engine
    verdicts without overriding them. See [[feedback-intake-label-
    unreliability]] and the end-of-day liability discussion 2026-06-12.

    Best-effort: on DB error returns empty dict so posture compose
    still runs without auditor context.
    """
    try:
        import psycopg2, os
        from dotenv import load_dotenv
        load_dotenv(".env")
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)",
                    (tenant_id,),
                )
                cur.execute(
                    """
                    SELECT DISTINCT ON (df.control_ref)
                           df.control_ref,
                           cd.filename,
                           df.extracted_at,
                           df.excerpt
                      FROM document_findings df
                      JOIN client_documents cd ON cd.id = df.document_id
                     WHERE df.tenant_id      = %s::uuid
                       AND cd.evidence_type  = 'audit_report'
                       AND df.is_active      = TRUE
                       AND df.review_status  = 'approved'
                       AND cd.is_active      = TRUE
                     ORDER BY df.control_ref, df.extracted_at DESC
                    """,
                    (tenant_id,),
                )
                out: dict[str, dict] = {}
                for ref, filename, at, excerpt in cur.fetchall():
                    out[ref] = {
                        "report":   filename,
                        "at":       at,
                        "excerpt":  (excerpt or "")[:160],  # short snippet
                    }
                return out
        finally:
            conn.close()
    except Exception:
        return {}


def _compose_posture_enumeration_answer(
    expanded_nodes: list,
    posture:        dict,
    scope_standards: list[str],
    tenant_name:    str = "",
    auditor_attestations: dict[str, dict] | None = None,
) -> str | None:
    """
    Deterministic markdown for POSTURE_CHECK enumeration queries.

    Returns None if no postured nodes are in the retrieved set (caller
    falls back to rank_and_answer for empty-retrieval handling).

    Format: flat bullet list per status bucket. Each row carries
    "**STD REF — Title**: reason" so the control name is always
    surfaced and bold renders cleanly.
    """
    if not expanded_nodes or not posture:
        return None

    posture_by_ref: dict[str, dict] = {}
    for nid, rec in (posture or {}).items():
        ref = rec.get("control_ref") or nid.split(":")[-1]
        if ref:
            posture_by_ref[ref] = rec

    postured_stds: set[str] = set()
    for nid in (posture or {}):
        parts = nid.split(":")
        if len(parts) >= 2:
            postured_stds.add(":".join(parts[:2]))
    if "ISO27001:2022" in postured_stds:
        primary_std = "ISO27001:2022"
    elif postured_stds:
        primary_std = sorted(postured_stds)[0]
    else:
        primary_std = "ISO27001:2022"

    scope_set = set(scope_standards or []) | {primary_std}

    nc_bucket:     list = []
    ofi_bucket:    list = []
    comply_bucket: list = []
    xfw_bucket:    list = []

    for n in expanded_nodes:
        if getattr(n, "is_informational", False):
            continue
        if n.standard_id not in scope_set:
            continue
        rec     = (posture or {}).get(n.node_id, {})
        finding = (rec.get("finding") or "").upper()

        if n.standard_id == primary_std:
            if finding == "NC":
                nc_bucket.append((n, rec))
            elif finding == "OFI":
                ofi_bucket.append((n, rec))
            elif finding == "COMPLY":
                comply_bucket.append((n, rec))
            # Skip N/A (out of scope) and unassessed
        else:
            # Cross-framework: inherit finding from linked primary controls
            linked: list[tuple[str, str]] = []
            for edge in (getattr(n, "xfw_edges", []) or []):
                lref = (edge.source_id.split(":")[-1]
                        if n.node_id == edge.target_id
                        else edge.target_id.split(":")[-1])
                if not lref:
                    continue
                lrec  = posture_by_ref.get(lref, {})
                lfind = (lrec.get("finding") or "").upper()
                if lfind in ("NC", "OFI", "COMPLY"):
                    linked.append((lref, lfind))
            # Dedupe linked refs — Neo4j can return multiple edges of
            # different rel_type to the same target.
            seen_refs: set[str] = set()
            uniq_linked: list[tuple[str, str]] = []
            for lr, lf in linked:
                if lr not in seen_refs:
                    seen_refs.add(lr)
                    uniq_linked.append((lr, lf))
            if uniq_linked:
                xfw_bucket.append((n, uniq_linked))

    if not (nc_bucket or ofi_bucket or comply_bucket or xfw_bucket):
        return None

    aud = auditor_attestations or {}

    def _row(n, rec) -> str:
        title   = (getattr(n, "title", "") or "").strip()
        ref_str = f"{_label_for_standard(n.standard_id)} {n.ref}"
        head    = f"**{ref_str} — {title}**" if title else f"**{ref_str}**"
        reason  = (rec.get("gap_description") or rec.get("evidence_text") or "").strip()
        # posture_loader emits engine reasons as multi-line strings —
        # summary on the first line, then indented bullet lines for
        # each partial leaf (`  - operating procedure: 6/8 — needs …`).
        # Preserve that structure so the LLM's final synthesis renders
        # the bullets rather than collapsing them into one wall of
        # text. Legacy narrative rows (single-line prose in
        # posture_controls.gap_description) still work because
        # `.strip()` above already cleared surrounding whitespace and
        # single-line inputs pass through unchanged.
        if "\n" in reason:
            first, rest = reason.split("\n", 1)
            reason = _prettify_reason(first.strip()) + "\n" + rest
        else:
            reason = _prettify_reason(reason)
        main_line = f"- {head}: {reason}" if reason else f"- {head}"

        # Auditor context — when an external audit report has an
        # approved finding on this control, surface the attestation
        # under the main row. Doesn't change the engine verdict;
        # purely operator-visible context so the gap between
        # auditor-blessed-clauses and engine-bound-MUSTs is clear
        # rather than hidden.
        att = aud.get(n.ref)
        if att:
            try:
                date_str = att["at"].strftime("%Y-%m-%d")
            except Exception:
                date_str = str(att.get("at") or "")
            snippet = (att.get("excerpt") or "").strip()
            if snippet:
                # Trim to one sentence-ish for readability.
                if len(snippet) > 140:
                    snippet = snippet[:137] + "…"
                main_line += (
                    f"\n  ↳ *External auditor ({att['report']}, {date_str}): "
                    f"\"{snippet}\"*"
                )
            else:
                main_line += (
                    f"\n  ↳ *External auditor confirmed "
                    f"({att['report']}, {date_str})*"
                )
        return main_line

    nc_bucket.sort(key=lambda x: x[0].ref)
    ofi_bucket.sort(key=lambda x: x[0].ref)
    comply_bucket.sort(key=lambda x: x[0].ref)
    xfw_bucket.sort(key=lambda x: x[0].ref)

    parts: list[str] = []
    name_for_lead = (tenant_name or "").strip() or "your organisation"
    parts.append(
        f"Please find our findings below, based on the information we "
        f"have on file for {name_for_lead}."
    )
    parts.append("")
    if nc_bucket:
        parts.append(f"**Non-Conformities (NC) — {len(nc_bucket)}:**")
        parts.extend(_row(n, rec) for n, rec in nc_bucket)
        parts.append("")
    if ofi_bucket:
        parts.append(f"**Opportunities for Improvement (OFI) — {len(ofi_bucket)}:**")
        parts.extend(_row(n, rec) for n, rec in ofi_bucket)
        parts.append("")
    if comply_bucket:
        parts.append(f"**Compliant — {len(comply_bucket)}:**")
        parts.extend(_row(n, rec) for n, rec in comply_bucket)
        parts.append("")
    if xfw_bucket:
        parts.append("**Cross-Framework:**")
        for n, linked in xfw_bucket:
            title   = (getattr(n, "title", "") or "").strip()
            ref_str = f"{_label_for_standard(n.standard_id)} {n.ref}"
            head    = f"**{ref_str} — {title}**" if title else f"**{ref_str}**"
            tag_list = ", ".join(f"{lr} [{lf}]" for lr, lf in linked)
            parts.append(f"- {head} — addressed via {tag_list}")
        parts.append("")

    return "\n".join(parts).rstrip()


# ── Posture timeline query helpers (schema_v21 / posture_status_log) ────────
#
# "How did A.5.18 evolve?", "timeline for Art.32", "show me the history of
# the access control posture". The handler reads posture_status_log directly
# and short-circuits before the resolver — no LLM dependency on a control
# the LLM may not remember.

_TIMELINE_PATTERNS = [
    re.compile(r'\b(?:timeline|history|evolution)\s+(?:for|of)\b',                       re.IGNORECASE),
    re.compile(r'\bhow\s+(?:did|has)\s+.+\s+(?:evolve|change|progress)\b',                re.IGNORECASE),
    re.compile(r'\bshow\s+(?:me\s+)?(?:the\s+)?(?:posture\s+)?(?:timeline|history)\b',    re.IGNORECASE),
    re.compile(r'\bwhen\s+did\s+.+\s+(?:change|become|move|transition)\b',                re.IGNORECASE),
    re.compile(r'\b(?:posture|status)\s+(?:changes?|transitions?)\s+(?:for|over\s+time)\b', re.IGNORECASE),
]

# Control-ref shapes the timeline can talk about: ISO Annex A clauses
# (A.5.18, A.6.4), GDPR articles (Art.32, Article 5), and plain dotted
# numeric refs (5.18, 8.16) — same set the classifier already recognises.
_TIMELINE_REF_PATTERN = re.compile(
    r'\b(A\.\d+(?:\.\d+)*)\b'
    r'|\b(Art(?:icle)?\.?\s?\d+(?:\(\d+\))?)\b'
    r'|\b(\d+\.\d+(?:\.\d+)?)\b',
    re.IGNORECASE,
)


def _is_timeline_query(query: str) -> bool:
    return any(p.search(query) for p in _TIMELINE_PATTERNS)


def _extract_timeline_ref(query: str, focus_refs: list[str]) -> Optional[str]:
    """Prefer the classifier's focus_refs (canonicalised upstream). Fall
    back to in-query regex extraction when the classifier didn't surface
    anything."""
    for r in focus_refs or []:
        if r:
            return r
    m = _TIMELINE_REF_PATTERN.search(query or "")
    if not m:
        return None
    return next((g for g in m.groups() if g), None)


_POSITIVE_UPLOAD_MARKERS = (
    # canonical verb variants
    "have we uploaded", "we have uploaded", "we uploaded",
    "documents uploaded", "uploaded documents",
    "what is uploaded", "what's uploaded", "what are uploaded",
    "show uploaded", "list uploaded", "list of uploaded",
    "which documents have we uploaded",
    # natural synonyms users actually use
    "have we submitted", "we submitted", "did we submit",
    "have we delivered", "we delivered",
    "have we provided", "we provided",
    "have we shared", "we shared",
    "have we sent", "we sent",
)

_NEGATIVE_UPLOAD_MARKERS = (
    "not uploaded", "haven't been uploaded", "have not been uploaded",
    "not yet uploaded", "yet to be uploaded", "still need to upload",
    "do we need to upload",
    "not submitted", "not yet submitted",
    "missing", "unuploaded",
)


def _detect_upload_polarity(query: str) -> str:
    """
    Classify an upload-status query as 'positive' (user wants list of
    uploaded docs), 'negative' (wants missing list), or 'ambiguous'
    (likely a specific-doc lookup — try title match against both lists).
    Negative markers win when both are present ("have we uploaded the
    things that aren't uploaded" → negative).
    """
    q = query.lower()
    if any(m in q for m in _NEGATIVE_UPLOAD_MARKERS):
        return "negative"
    if any(m in q for m in _POSITIVE_UPLOAD_MARKERS):
        return "positive"
    return "ambiguous"


_STOP_WORDS = {
    "have", "has", "our", "the", "any", "and", "what", "which", "are",
    "been", "yet", "have", "ours", "do", "did", "we", "we've", "your",
    "for", "with", "from", "this", "that", "these", "those",
    "document", "documents", "policy", "policies", "procedure",
    "procedures", "plan", "plans",
}


# Framework-aware ref helpers live in rag/framework_refs.py so they can be
# shared between arion_graph and context_assembler without circular import.
from rag.framework_refs import (
    group_refs_by_framework  as _group_refs_by_framework,
    render_framework_refs    as _render_framework_refs,
)


# Shape words distinguish related-but-different doc types. A "Business
# Continuity Policy" and "Business Continuity Plan" share the topic
# (business + continuity) but are different artifacts. The title matcher
# below requires shape words on both sides to canonicalise to the same
# shape — otherwise "have we uploaded the policy?" wrongly hits a plan
# titled "Business Continuity Plan".
_SHAPE_CANONICAL = {
    # canonical form          synonyms
    "policy":     {"policy", "standard", "directive", "rule"},
    "procedure":  {"procedure", "process", "workflow", "sop"},
    "plan":       {"plan", "programme", "program", "roadmap"},
    "register":   {"register", "log", "list", "inventory", "tracker", "record"},
    "assessment": {"assessment", "report", "evaluation"},
    "template":   {"template"},
    "scope":      {"scope"},
    "manual":     {"manual", "handbook", "guide", "guideline"},
}
_SHAPE_TOKEN_TO_CANONICAL = {
    syn: canonical
    for canonical, syns in _SHAPE_CANONICAL.items()
    for syn in syns
}


def _detect_shape(words: set) -> str | None:
    """Return the canonical shape word present in a set, or None."""
    for w in words:
        if w in _SHAPE_TOKEN_TO_CANONICAL:
            return _SHAPE_TOKEN_TO_CANONICAL[w]
    return None


def _title_match_against(query: str, items: list, title_key: str) -> list:
    """
    Find items whose title overlaps the query by ≥2 significant words.
    Returns matching items ranked by overlap (best first). Significant =
    >3 chars and not in _STOP_WORDS.

    Shape-word disambiguation: if both query and title contain a shape
    word (policy/plan/procedure/register/etc), they must canonicalise
    to the same shape. Stops "business continuity policy" from matching
    a doc titled "Business Continuity Plan".
    """
    # Shape detection runs on the FULL tokenization (pre-stopwords) because
    # _STOP_WORDS strips shape words like "policy" / "plan" / "procedure".
    # Those are needed to disambiguate doc types ("BC Policy" vs "BC Plan").
    q_all = set(re.split(r"[\W_]+", query.lower()))
    q_shape = _detect_shape(q_all)
    q_words = {w for w in q_all if len(w) > 3 and w not in _STOP_WORDS}
    if not q_words:
        return []
    ranked = []
    for it in items:
        title = (it.get(title_key) or "").lower()
        t_all = set(re.split(r"[\W_]+", title))
        t_shape = _detect_shape(t_all)
        # If both sides name a shape, they must agree.
        if q_shape and t_shape and q_shape != t_shape:
            continue
        t_words = {w for w in t_all if len(w) > 3 and w not in _STOP_WORDS}
        overlap = len(q_words & t_words)
        if overlap >= 2:
            ranked.append((overlap, it))
    ranked.sort(key=lambda r: r[0], reverse=True)
    return [it for _, it in ranked]


def _control_entity(control_ref: str, title: str = "") -> dict:
    """Build a `last_entity` dict for short-circuits that resolved a
    specific control (acknowledge, Stage-1/2, timeline, scope_na).
    Standard_id is inferred from the ref shape: Art.* → GDPR, else
    ISO27001:2022. Title is optional metadata for the LLM prompt.

    Used to carry the matched control across turns so deictic
    follow-ups ("is it approved?", "tell me more about it") have a
    referent. See [[conversational-context-routing-followup]]."""
    if not control_ref:
        return {}
    standard_id = "GDPR:2016/679" if control_ref.startswith("Art.") else "ISO27001:2022"
    return {
        "type":        "control",
        "ref":         control_ref,
        "standard_id": standard_id,
        "title":       title or control_ref,
    }


def _resolve_upload_entity(
    query: str,
    uploaded: list,
    alerts: list,
) -> dict:
    """Return a small summary of the doc that an upload-status query
    matched against, for next-turn conversational context. Returns
    `{}` when no specific doc was named or no match was found —
    inventory-style queries ("what docs have we uploaded?") don't
    produce a single-entity context.

    Used to populate `state["last_entity"]` so the LLM can reference
    the prior turn on deictic follow-ups. See [[conversational-
    context-routing-followup]]."""
    polarity = _detect_upload_polarity(query)
    if polarity != "positive":
        return {}
    # Title-match against uploaded first, then alerts. We only return
    # an entity when the query named a SPECIFIC doc by title — generic
    # inventory queries have no single subject to carry forward.
    hits = _title_match_against(query, uploaded or [], "document_title")
    if hits:
        d = hits[0]
        return {
            "type":        "document",
            "title":       d.get("document_title") or d.get("filename") or "",
            "ref":         d.get("external_ref") or d.get("platform_ref") or "",
            "doc_type":    d.get("doc_type") or "",
            "status":      d.get("document_status") or "uploaded",
            "uploaded_at": (d.get("uploaded_at") or "")[:10] if d.get("uploaded_at") else "",
        }
    hits = _title_match_against(query, alerts or [], "document_title")
    if hits:
        a = hits[0]
        return {
            "type":     "document",
            "title":    a.get("document_title") or "",
            "ref":      a.get("external_ref") or "",
            "status":   "registered_not_uploaded",
        }
    return {}


def _answer_upload_status(
    query:    str,
    alerts:   list,
    uploaded: list | None = None,
) -> str | None:
    """
    Answer an upload status question directly from the right data source:
      - positive polarity → answer from client_documents (status='uploaded')
      - negative polarity → list from document_alerts (registered, missing)
      - ambiguous (specific doc by name) → match titles against both lists
    Deterministic — no LLM involved. Returns None to fall through to LLM.
    """
    uploaded = uploaded or []
    polarity = _detect_upload_polarity(query)

    # ── Positive: which documents have we uploaded / submitted / etc ───
    if polarity == "positive":
        # If the query names a specific document, answer about THAT one,
        # not the full inventory. Look in uploaded first (yes-answer wins),
        # then in alerts (no-answer for a known-but-missing doc).
        up_hits = _title_match_against(query, uploaded, "document_title")
        if up_hits:
            d = up_hits[0]
            title    = d.get("document_title") or d.get("filename") or "the requested document"
            ref      = d.get("external_ref") or d.get("platform_ref") or ""
            ref_s    = f" ({ref})" if ref else ""
            when     = d.get("uploaded_at")
            when_s   = f" on {when[:10]}" if when else ""
            doc_type = d.get("doc_type") or ""
            type_s   = f" ({doc_type})" if doc_type else ""
            extras = []
            if d.get("page_count"):
                extras.append(f"{d['page_count']} pages")
            framework_clause = _render_framework_refs(d.get("framework_refs"))
            if framework_clause:
                extras.append(f"assessed against {framework_clause}")
            extra_s = f" — {'; '.join(extras)}" if extras else ""
            return (
                f"Yes — {title}{ref_s}{type_s} has been uploaded{when_s}{extra_s}. "
                f"Document status: {d.get('document_status', 'uploaded')}."
            )

        alert_hits = _title_match_against(query, alerts, "document_title")
        if alert_hits:
            a = alert_hits[0]
            title = a.get("document_title") or "the requested document"
            ref   = a.get("external_ref") or ""
            ref_s = f" ({ref})" if ref else ""
            # Prefer the structured array from the view; fall back to the
            # flat string for older snapshots.
            framework_clause = _render_framework_refs(a.get("linked_control_refs"))
            if not framework_clause and a.get("linked_controls"):
                framework_clause = a["linked_controls"]
            ctl_s = f" It is linked to {framework_clause}." if framework_clause else ""
            return (
                f"No — {title}{ref_s} is registered but has not yet been "
                f"uploaded to the platform.{ctl_s}"
            )

        # No specific doc named — answer about the whole inventory
        if not uploaded:
            return (
                "No documents have been uploaded to the platform yet. "
                "Registered documents are tracked in our checklist but their "
                "files haven't been delivered — use the upload endpoint or "
                "tools/doc_uploader.py to upload them."
            )
        lines = [f"Uploaded documents ({len(uploaded)} total):"]
        for d in uploaded[:20]:
            title    = d.get("document_title") or d.get("filename") or "?"
            ref      = d.get("external_ref") or d.get("platform_ref") or ""
            ref_s    = f" ({ref})" if ref else ""
            doc_type = d.get("doc_type") or ""
            type_s   = f" — {doc_type}" if doc_type else ""
            when     = d.get("uploaded_at")
            when_s   = f", uploaded {when[:10]}" if when else ""
            framework_clause = _render_framework_refs(d.get("framework_refs"))
            asses_s  = f"; assessed against {framework_clause}" if framework_clause else ""
            lines.append(f"  • {title}{ref_s}{type_s}{when_s}{asses_s}")
        if len(uploaded) > 20:
            lines.append(f"  … and {len(uploaded) - 20} more")
        return "\n".join(lines)

    # ── Negative or ambiguous: report missing/registered from alerts ───
    if not alerts and polarity == "negative":
        return "No registered documents are currently flagged as missing."
    if not alerts:
        return None  # Nothing to say; let the LLM try

    query_lower = query.lower()

    # Title-match for ambiguous specific-doc queries
    relevant = []
    if polarity == "ambiguous":
        for alert in alerts:
            title = (alert.get("document_title") or "").lower()
            title_words = [w for w in title.split() if len(w) > 3]
            if any(w in query_lower for w in title_words):
                relevant.append(alert)

    # Negative polarity (or ambiguous with no title hit): list everything missing
    if not relevant:
        if polarity == "negative":
            relevant = [a for a in alerts
                       if a.get("alert_type") in ("CRITICAL", "WARNING", "INFO")]
        else:
            return None  # Ambiguous and no title match — let LLM handle

    lines = []
    critical = [a for a in relevant if a.get("alert_type") == "CRITICAL"]
    warning  = [a for a in relevant if a.get("alert_type") == "WARNING"]
    info     = [a for a in relevant if a.get("alert_type") == "INFO"]

    def _link_clause(a: dict) -> str:
        """Framework-aware 'linked to …' clause for one alert."""
        rendered = _render_framework_refs(a.get("linked_control_refs"))
        if rendered:
            return rendered
        # Legacy fallback when the structured array is unavailable
        flat = a.get("linked_controls")
        return flat if flat else "unknown"

    if critical:
        lines.append("The following documents are registered but NOT yet uploaded "
                     "and are linked to open NC findings:")
        for a in critical:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to {_link_clause(a)}"
            )
    if warning:
        if lines:
            lines.append("")
        lines.append("Also registered but not uploaded — linked to OFI findings:")
        for a in warning:
            lines.append(
                f"  • {a['document_title']} ({a['external_ref']}) "
                f"— linked to {_link_clause(a)}"
            )
    if info:
        if not critical and not warning:
            lines.append("Registered but not yet uploaded:")
            for a in info[:5]:
                lines.append(f"  • {a['document_title']} ({a['external_ref']})")
            if len(info) > 5:
                lines.append(
                    f"  … and {len(info) - 5} more registered but not yet "
                    f"linked to findings."
                )
        else:
            # Critical/warning already listed individually; summarise the
            # rest so the LLM composer (and the user) know they exist.
            lines.append("")
            lines.append(
                f"There are also {len(info)} additional documents registered "
                f"but not yet uploaded (not currently linked to any open "
                f"NC or OFI findings)."
            )

    if lines:
        lines.append("")
        lines.append(
            "Upload these files to the platform so the system can verify "
            "their content against control checklists automatically."
        )

    return "\n".join(lines) if lines else None


# ── Posture timeline answerer (schema_v21) ───────────────────────────────────

# ── S3l: cascade chat short-circuits ─────────────────────────────────
_CASCADE_IMPL_PATTERNS = [
    # Catch any of: "<verb-bit>* implications <preposition>"
    # The space between "implications" and "for/on" can carry helper
    # words ("do I have", "are there", "exist", etc.). Use a generic
    # lookahead instead of explicit phrase enumeration.
    re.compile(r'\b(?:cascade\s+)?implications?\s+(?:\w+\s+){0,5}?(?:on|for)\s+', re.IGNORECASE),
    re.compile(r'\b(?:show|list)\s+(?:me\s+)?(?:the\s+)?(?:cascade\s+)?implications?\b', re.IGNORECASE),
    re.compile(r'\bpending\s+implications?\b', re.IGNORECASE),
    re.compile(r'\boverdue\s+implications?\b', re.IGNORECASE),
]

_CASCADE_FOLLOWUP_PATTERNS = [
    re.compile(r'\boverdue\s+followups?\b', re.IGNORECASE),
    re.compile(r'\bwhich\s+followups?\s+are\s+overdue\b', re.IGNORECASE),
    re.compile(r'\b(?:show|list)\s+(?:me\s+)?(?:the\s+)?(?:overdue\s+|pending\s+)?expected\s+followups?\b', re.IGNORECASE),
    re.compile(r'\b(?:overdue|pending|expected)\s+(?:event\s+)?followups?\b', re.IGNORECASE),
]

_CASCADE_SUPPRESSION_PATTERNS = [
    re.compile(r'\bsuppressed\s+cascades?\b', re.IGNORECASE),
    re.compile(r'\bblocked\s+(?:cascades?|implications?)\b', re.IGNORECASE),
    re.compile(r'\bwhat\s+cascades?\s+(?:were|got|have\s+been)\s+(?:blocked|suppressed)\b', re.IGNORECASE),
]


def _is_cascade_impl_query(query: str) -> bool:
    return any(p.search(query) for p in _CASCADE_IMPL_PATTERNS)


def _is_cascade_followups_query(query: str) -> bool:
    return any(p.search(query) for p in _CASCADE_FOLLOWUP_PATTERNS)


def _is_cascade_suppressions_query(query: str) -> bool:
    return any(p.search(query) for p in _CASCADE_SUPPRESSION_PATTERNS)


def _answer_cascade_implications(
    query:       str,
    tenant_id:   str,
    control_ref: Optional[str],
) -> Optional[str]:
    """Deterministic answer for 'what implications do I have for X?'.

    When control_ref is supplied, scopes to that one control. When
    None (no ref in query), returns a top-summary across all controls.
    """
    if not tenant_id:
        return None
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return None
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
    except Exception:
        return None

    try:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL app.tenant_id = %s", (tenant_id,))
            if control_ref:
                cur.execute(
                    """
                    SELECT target_control_ref, source_event_type,
                           cascade_path, cascade_depth, expected_action,
                           due_date, status, rationale, scope_kind,
                           clock_anchor
                      FROM triggered_implication
                     WHERE tenant_id = %s::uuid
                       AND target_control_ref = %s
                       AND status = 'pending'
                     ORDER BY due_date NULLS LAST, fired_at DESC
                     LIMIT 20
                    """,
                    (tenant_id, control_ref),
                )
            else:
                cur.execute(
                    """
                    SELECT target_control_ref, source_event_type,
                           cascade_path, cascade_depth, expected_action,
                           due_date, status, rationale, scope_kind,
                           clock_anchor
                      FROM triggered_implication
                     WHERE tenant_id = %s::uuid
                       AND status = 'pending'
                     ORDER BY due_date NULLS LAST, fired_at DESC
                     LIMIT 30
                    """,
                    (tenant_id,),
                )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        if control_ref:
            return (f"No pending cascade implications on {control_ref}. "
                    f"Either no event has triggered obligations on this "
                    f"control, or all triggered implications have been "
                    f"satisfied or dismissed.")
        return ("No pending cascade implications across any control. "
                "Either no structured events have been emitted from cite "
                "verifications, or all triggered implications have been "
                "resolved.")

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    overdue = sum(1 for r in rows if r[5] and r[5] < now)
    head = (f"Cascade implications on {control_ref}" if control_ref
            else "Cascade implications (pending)")
    lines = [f"{head} — {overdue} overdue, {len(rows)-overdue} pending:", ""]
    for r in rows:
        ref, src_evt, path, depth, action, due, _status, rationale, scope_kind, anchor = r
        path = path if isinstance(path, list) else []
        is_overdue = bool(due and due < now)
        tag = "OVERDUE" if is_overdue else "pending"
        due_s = due.date().isoformat() if due else "open-ended"
        path_s = " → ".join(path) if path else src_evt
        suffix = f" (scope={scope_kind})" if scope_kind else ""
        suffix += f" [clock={anchor}]" if anchor and anchor != "verified_at" else ""
        lines.append(f"  - [{tag}] {ref}: {action} (due {due_s}){suffix}")
        lines.append(f"    via {path_s}")
        if rationale:
            lines.append(f"    {rationale[:140]}")
    return "\n".join(lines)


def _answer_cascade_followups(query: str, tenant_id: str) -> Optional[str]:
    """Deterministic answer for 'overdue followups' / 'which followups are overdue'."""
    if not tenant_id:
        return None
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return None
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
    except Exception:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL app.tenant_id = %s", (tenant_id,))
            cur.execute(
                """
                SELECT source_event_type, expected_event_type, window_days,
                       expires_at, status, rationale
                  FROM expected_followup_event
                 WHERE tenant_id = %s::uuid
                   AND status IN ('pending', 'overdue')
                 ORDER BY status, expires_at
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    if not rows:
        return ("No pending or overdue expected followups. The cascade "
                "engine isn't currently tracking any missing downstream "
                "events.")
    overdue = [r for r in rows if r[4] == 'overdue']
    pending = [r for r in rows if r[4] == 'pending']
    lines = [
        f"Expected followups — {len(overdue)} overdue, {len(pending)} pending:",
        "",
    ]
    if overdue:
        lines.append("OVERDUE (expected window already elapsed):")
        for src, exp, win, expires, _status, rat in overdue:
            lines.append(f"  - {src} expected {exp} within {win}d; "
                         f"expired {expires.date().isoformat()}")
            if rat:
                lines.append(f"    {rat[:140]}")
    if pending:
        if overdue:
            lines.append("")
        lines.append("PENDING (within window):")
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        for src, exp, win, expires, _status, rat in pending:
            days_left = int((expires - now).total_seconds() / 86400)
            lines.append(f"  - {src} expects {exp} within {win}d; "
                         f"{days_left}d remaining")
    return "\n".join(lines)


def _answer_cascade_suppressions(query: str, tenant_id: str) -> Optional[str]:
    """Deterministic answer for 'show suppressed cascades' / 'what was blocked'."""
    if not tenant_id:
        return None
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return None
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
    except Exception:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL app.tenant_id = %s", (tenant_id,))
            cur.execute(
                """
                SELECT suppression_kind, source_event_type,
                       target_event_type, target_requirement_id,
                       applies_when, fired_at
                  FROM cascade_suppression_log
                 WHERE tenant_id = %s::uuid
                 ORDER BY fired_at DESC
                 LIMIT 20
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    if not rows:
        return ("No cascade suppressions recorded. Every fired cascade "
                "has run without applies_when / BLOCKS_WHEN intercepts.")
    lines = [f"Cascade suppressions (most recent {len(rows)}):", ""]
    for kind, src, tgt_evt, tgt_req, applies, fired_at in rows:
        when = fired_at.date().isoformat() if fired_at else "?"
        if kind == "blocks_when":
            lines.append(f"  - {when}  {kind:12s}  {src} -X-> {tgt_req}   "
                         f"applies_when: {applies}")
        else:
            lines.append(f"  - {when}  {kind:12s}  {src} -X-> {tgt_evt}   "
                         f"applies_when: {applies}")
    return "\n".join(lines)


_CASCADE_REF_PATTERN = re.compile(
    r"\b(A\.\d+\.\d+|Art\.\d+(?:\.\d+)*(?:\.[a-z])?|\d+\.\d+(?:\.\d+)?)\b",
    re.IGNORECASE,
)


def _extract_cascade_ref(query: str, focus_refs: list[str]) -> Optional[str]:
    for r in focus_refs or []:
        if r:
            return r
    m = _CASCADE_REF_PATTERN.search(query or "")
    if not m:
        return None
    return m.group(1)


def _answer_control_timeline(
    query:       str,
    tenant_id:   str,
    control_ref: str,
) -> Optional[str]:
    """
    Return a deterministic answer for a "timeline of <control>" query by
    reading posture_status_log. Returns None when the control has no
    history rows for the tenant — that falls through to the resolver,
    which can answer about current posture even when history is empty.
    """
    if not tenant_id or not control_ref:
        return None

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return None

    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
    except Exception:
        return None

    try:
        with conn.cursor() as cur:
            # RLS uses app.tenant_id — set before reading.
            cur.execute("SET LOCAL app.tenant_id = %s", (tenant_id,))
            cur.execute(
                """
                SELECT h.changed_at::date::text,
                       h.status_before, h.status_after,
                       h.source,
                       u.filename, u.version_no,
                       h.evidence_citation,
                       h.standard_id
                  FROM posture_status_log h
             LEFT JOIN document_uploads   u ON u.id = h.source_upload_id
                 WHERE h.tenant_id   = %s::uuid
                   AND h.control_ref = %s
                 ORDER BY h.changed_at
                """,
                (tenant_id, control_ref),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    standards = sorted({r[7] for r in rows if r[7]})
    std_hint  = f" ({', '.join(standards)})" if standards else ""

    lines = [f"Timeline for {control_ref}{std_hint}:", ""]
    for r in rows:
        changed_at, before, after, source, fname, ver_no, evidence, _ = r
        if before is None:
            transition = f"first recorded as {after}"
        else:
            transition = f"{before} → {after}"
        src = f"from {fname}" if fname else f"via {source}"
        if ver_no is not None:
            src += f" (v{ver_no})"
        line = f"- {changed_at}: {transition} {src}."
        if evidence:
            line += f' Evidence: "{evidence[:200]}".'
        lines.append(line)

    return "\n".join(lines)


# ── Generic short-circuit → LLM polish helper ────────────────────────────────

# Every ref shape that MUST survive any rewrite verbatim:
#   - DOC###, CD-XXX-### : entity identifiers (which document/control)
#   - A.x.y              : ISO 27001/27701 clause numbers (which control the
#                          finding/document maps to — auditors need these)
#   - Art.X              : GDPR / NIS2 articles (cross-framework attribution)
# Dropping any of these silently changes the answer's compliance content.
# The LLM should rephrase prose, never drop refs.
_SHORT_CIRCUIT_REQUIRED_REF_PATTERN = re.compile(
    r'\bDOC\d{3}\b'
    r'|\bCD-[A-Z]{2,4}-\d{3,4}\b'
    r'|\bA\.\d+(?:\.\d+)*\b'
    r'|\bArt\.\s?\d+(?:\(\d+\))?\b'
)

# Lines that look like a CLI action the user is expected to run.
_ACTION_HINT_MARKERS = ("upload:", "run:", "tools/")


_BULLET_PREFIXES = ("•", "* ", "- ")


def _count_bullets(text: str) -> int:
    if not text:
        return 0
    return sum(
        1 for line in text.splitlines()
        if line.lstrip().startswith(_BULLET_PREFIXES)
    )


# Post-polish jargon scrub. The LLM sometimes reintroduces the raw
# evidence_type / role slug form ('review_record', 'revocation_record')
# — or the raw engine-reason phrasing ('N/M children satisfied',
# 'missing artifacts of type: X') — in prose even when the
# deterministic input already used the humanized form. The model
# pattern-matches on the training-corpus form. Substitute back to
# natural language after compose so the tenant never sees the debug
# form. Skips URL contexts by requiring word boundaries with no
# adjacent `/` or `:`.
def _scrub_jargon_slugs(text: str) -> str:
    if not text:
        return text
    out = text
    # 1. Role slug substitutions (only worth running if `_` is present)
    if "_" in out:
        for slug, label in _ROLE_LABELS.items():
            if "_" not in slug or slug not in out:
                continue
            # Word-boundary substitution guarded against URL / id contexts
            # (skips '/req:A.5.16:review_record/', 'item:X:review_record').
            out = re.sub(
                rf"(?<![A-Za-z0-9_/:]){re.escape(slug)}(?![A-Za-z0-9_/:])",
                label,
                out,
            )
    # 2. Engine-reason phrasing the LLM reconstructs from context.
    #    "N out of M children satisfied" / "N/M children satisfied" →
    #    "N of M requirements met". Handles the "children" leak that
    #    surfaces in POSTURE_CHECK enumerations even after prettify
    #    ran on the deterministic input.
    out = re.sub(
        r"\b(\d+)\s+(?:out\s+of|of|/)\s+(\d+)\s+children\s+satisfied\b",
        r"\1 of \2 requirements met",
        out,
        flags=re.IGNORECASE,
    )
    #    Same shape without the count phrasing: "M children satisfied" or
    #    "children are unsatisfied".
    out = re.sub(r"\bchildren\s+satisfied\b", "requirements met", out, flags=re.IGNORECASE)
    out = re.sub(r"\bchildren\s+are\s+unsatisfied\b", "requirements are not yet met", out, flags=re.IGNORECASE)
    out = re.sub(r"\bare\s+unsatisfied\b", "are not yet met", out, flags=re.IGNORECASE)
    # 'N child(ren)' → 'N requirement(s)' for the count-singular case.
    out = re.sub(r"\b(\d+)\s+child(?:ren)?\b", r"\1 requirement", out, flags=re.IGNORECASE)
    out = re.sub(r"\bchildren\b", "requirements", out, flags=re.IGNORECASE)
    #    "missing artifacts of type: a, b" → "still needed: a, b"
    out = re.sub(
        r"\bmissing\s+artifacts\s+of\s+type:",
        "still needed:",
        out,
        flags=re.IGNORECASE,
    )
    return out


def polish_short_circuit_answer(
    query:                str,
    deterministic_answer: str,
    llm,
) -> str:
    """
    Polish any deterministic short-circuit answer into conversational prose
    via LLMAnswer.compose(). Extracts every ref shape and action-hint line
    from the deterministic text so the composer can preserve them verbatim.

    Data-loss guard: after the polish, verify every distinctive ref and
    bullet from the deterministic answer survives in the composed output.
    If the LLM silently dropped a bullet or ref (e.g. rewriting "6 total"
    as "5 total" and omitting one document row), fall back to the
    deterministic text. The short-circuit invariant — no data loss — is
    enforced, not just hoped for.
    """
    if not deterministic_answer:
        return deterministic_answer

    required_refs = list(set(_SHORT_CIRCUIT_REQUIRED_REF_PATTERN.findall(deterministic_answer)))

    action_hint = None
    for line in deterministic_answer.splitlines():
        s = line.strip()
        if any(m in s.lower() for m in _ACTION_HINT_MARKERS):
            action_hint = s
            break

    composed = llm.compose(
        query              = query,
        deterministic_text = deterministic_answer,
        required_refs      = required_refs,
        action_hint        = action_hint,
    )

    # Ref-drop guard: every distinctive ref in the input must survive.
    if required_refs and composed:
        composed_refs = set(_SHORT_CIRCUIT_REQUIRED_REF_PATTERN.findall(composed))
        missing = sorted(set(required_refs) - composed_refs)
        if missing:
            (get_logger() or _NullLogger()).warning(
                "polish_short_circuit_answer: LLM dropped refs %s — "
                "falling back to deterministic text",
                missing,
            )
            return deterministic_answer

    # Bullet-drop guard: list-shaped answers (e.g. "Uploaded documents (N total)")
    # lose data even when refs are sparse. If the composed has fewer bullets
    # than the input, fall back.
    det_bullets = _count_bullets(deterministic_answer)
    if det_bullets and _count_bullets(composed or "") < det_bullets:
        (get_logger() or _NullLogger()).warning(
            "polish_short_circuit_answer: LLM dropped bullets "
            "(deterministic=%d, composed=%d) — falling back",
            det_bullets, _count_bullets(composed or ""),
        )
        return deterministic_answer

    # Jargon scrub: substitute raw `_role` slugs the LLM sometimes echoes
    # ('review_record', 'revocation_record') back to natural language.
    # Locked in by eval case #200.
    return _scrub_jargon_slugs(composed)


from vector.retriever      import VectorRetriever


# ── Node implementations ────────────────────────────────────────────────────

def make_classify_node(
    classifier: QueryClassifier,
):
    """
    Node: classify intent.
    Replaces: _handle_intake + _handle_query + classify_query routing.
    """
    def classify(state: ArionState) -> dict:
        query  = state["query"]
        logger = get_logger()

        # Override: "just answer" / "skip" → force best-effort
        if query.lower().strip() in OVERRIDE_PHRASES:
            return {
                "intent_type":   "gap_analysis",   # best-effort default
                "focus_refs":    state.get("focus_refs", []),
                "needs_posture": True,
                "confidence":    0.5,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

        # Clarification response: user replied to a taxonomy question (a/b/c).
        # Accept bare letters ("a", "b)", "c."), bracketed forms ("(a)", "[c]"),
        # AND the rendered button text the UI sends back ("(c) Do you need ...").
        # The letter must be followed by ).].:.,/whitespace/end to avoid false
        # matches on real words that start with a-c (e.g. "are we GDPR …").
        import re as _re
        _letter_re = _re.compile(r"^[\(\[]?\s*([a-c])(?=\s*[\)\].\:,]|\s*$)")
        _letter_match = _letter_re.match(query.strip().lower()) if query else None
        _is_clarif_response = bool(
            state.get("turn_count", 0) > 0            # not first turn
            and state.get("needs_clarif") is True     # clarif question was shown
            and state.get("clarif_count", 0) > 0      # we did ask a clarif question
            and bool(state.get("clarif_question"))    # there is a pending question
            and _letter_match
        )
        if _is_clarif_response:
            # Map letter directly to intent type from taxonomy_options_map
            # stored in state (set when we returned the clarif question)
            tmap = state.get("taxonomy_options_map") or {}
            letter = _letter_match.group(1)
            taxonomy_id = tmap.get(letter)
            from rag.taxonomy import CLASSIFIER_TO_TAXONOMY
            TAXONOMY_TO_CLASSIFIER = {v: k for k, v in CLASSIFIER_TO_TAXONOMY.items()}
            if taxonomy_id:
                intent_type = TAXONOMY_TO_CLASSIFIER.get(taxonomy_id, "gap_analysis")
                return {
                    "intent_type":    intent_type,
                    "focus_refs":     state.get("focus_refs", []),
                    "needs_posture":  intent_type in ("gap_analysis", "posture_check"),
                    "confidence":     0.95,
                    "needs_clarif":   False,
                    "clarif_question": "",
                    "clarif_count":   0,
                    # Keep original query for retrieval
                    "query":          state.get("original_query", state["query"]),
                }

        # Build a minimal SessionContext from graph state
        from rag.classifier import SessionContext, QuestionType
        session = SessionContext(
            tenant_profile = classifier.tenant,
            standards      = state["standards"],
            role           = state.get("role"),
            intent_type    = None,
            active_refs    = state.get("focus_refs", []),
            active_cluster = None,
        )

        # First turn: use process_intake (handles ambiguous clusters)
        # Follow-up turns: use classify_query (faster, session-aware)
        if state["turn_count"] == 0:
            intake = classifier.process_intake(query)
            if intake.state == IntakeState.AMBIGUOUS:
                count = state["clarif_count"] + 1
                if count >= 2:
                    # Exhausted — fall through to best-effort
                    return {
                        "intent_type":    "unknown",
                        "focus_refs":     [],
                        "needs_posture":  True,
                        "confidence":     0.5,
                        "needs_clarif":   False,
                        "clarif_question": "",
                        "clarif_count":   count,
                    }
                return {
                    "intent_type":       "ambiguous",
                    "focus_refs":        [],
                    "needs_posture":     False,
                    "confidence":        0.0,
                    "needs_clarif":      True,
                    "clarif_question":   intake.clarification or "",
                    "clarif_count":      count,
                    "turn_count":        state["turn_count"] + 1,  # advance so next turn is follow-up
                    "taxonomy_options_map": getattr(intake, "taxonomy_options_map", {}) or {},
                    "original_query":    query,
                }
            if intake.state == IntakeState.NO_MATCH:
                count = state["clarif_count"] + 1
                if count >= 2:
                    # Already asked once — fall through to best-effort
                    return {
                        "intent_type":    "unknown",
                        "focus_refs":     [],
                        "needs_posture":  True,
                        "confidence":     0.5,
                        "needs_clarif":   False,
                        "clarif_question": "",
                        "clarif_count":   count,
                    }
                return {
                    "intent_type":    "unknown",
                    "focus_refs":     [],
                    "needs_posture":  False,
                    "confidence":     0.0,
                    "needs_clarif":   True,
                    "clarif_question": intake.clarification or "",
                    "clarif_count":   count,
                    "turn_count":     state["turn_count"] + 1,
                    "original_query": query,
                }
            # CLEAR or EXPLICIT
            sess = intake.session
            return {
                "intent_type":   sess.intent_type.value if sess.intent_type else "unknown",
                "focus_refs":    sess.active_refs[:3],
                "needs_posture": sess.intent_type.value in ("gap_analysis", "posture_check")
                                 if sess.intent_type else False,
                "confidence":    0.88,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

        else:
            # Follow-up turn — build history from graph state for context
            _history = []
            if state.get("original_query"):
                _history.append({"role": "user", "content": state["original_query"]})
            if state.get("answer_text"):
                _history.append({"role": "assistant", "content": state["answer_text"][:400]})
            _history.append({"role": "user", "content": query})
            intent = classifier.classify_query(query, session, _history)
            if intent.clarification_question:
                count = state["clarif_count"] + 1
                if count >= 2:
                    return {
                        "intent_type":    "unknown",
                        "focus_refs":     intent.cited_refs[:3],
                        "needs_posture":  True,
                        "confidence":     0.5,
                        "needs_clarif":   False,
                        "clarif_question": "",
                        "clarif_count":   count,
                    }
                return {
                    "intent_type":    intent.question_type.value,
                    "focus_refs":     intent.cited_refs[:3],
                    "needs_posture":  intent.needs_posture,
                    "confidence":     intent.confidence,
                    "needs_clarif":   True,
                    "clarif_question": intent.clarification_question,
                    "clarif_count":   count,
                }

            return {
                "intent_type":   intent.question_type.value,
                "focus_refs":    intent.cited_refs[:3],  # ONLY cited refs — no stale session
                "needs_posture": intent.needs_posture,
                "confidence":    intent.confidence,
                "needs_clarif":  False,
                "clarif_question": "",
                "clarif_count":  0,
            }

    return classify


from rag.scope_na import is_scope_na_query as _is_scope_na_query

def _answer_scope_na(query: str, posture: dict) -> str:
    """
    Answer scope N/A queries directly — no LLM, no graph traversal.
    Returns a direct statement that these controls are out of scope.
    """
    query_lower = query.lower()

    is_physical = re.search(
        r'physical\s+security|physical\s+access|perimeter|premises', query_lower)
    is_dev = re.search(
        r'software\s+dev|secure\s+cod|development\s+security', query_lower)

    if is_physical:
        # Confirm from posture that A.7.x are all N/A
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("7.","A.7."))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else ""
        )
        return (
            f"Physical security controls (A.7.x) are marked not applicable "
            f"for Arion Networks{controls_note}. "
            f"Your ISMS scope excludes physical premises controls — "
            f"Arion operates as a cloud-based organisation without dedicated physical facilities "
            f"requiring ISO 27001 physical security controls. "
            f"No physical security gaps apply to your organisation."
        )
    elif is_dev:
        na_controls = [
            v.get("control_ref", k.split(":")[-1])
            for k, v in posture.items()
            if (v.get("control_ref","") or k.split(":")[-1]).startswith(("A.8.2","8.2"))
            and v.get("finding") == "N/A"
        ]
        controls_note = (
            f" ({', '.join(sorted(na_controls)[:5])}{'...' if len(na_controls) > 5 else ''})"
            if na_controls else " (A.8.25–A.8.31)"
        )
        return (
            f"Software development security controls{controls_note} are marked "
            f"not applicable for Arion Networks. "
            f"Your ISMS scope excludes software development — "
            f"Arion Networks does not develop software products, so secure development "
            f"lifecycle controls do not apply to your organisation. "
            f"No software development security gaps exist in your scope."
        )

    return (
        "The controls related to this area are marked not applicable "
        "for Arion Networks and are excluded from your ISMS scope."
    )


def build_answer_envelope(
    *,
    answer_text:      str,
    cited_refs:       list,
    answer_source:    str,
    question_type:    str,
    state:            dict = None,
    tenant           = None,
    intent           = None,
    # LLM-path metadata (optional; omitted from result when None)
    verified:         bool = None,
    was_corrected:    bool = None,
    posture_findings: dict = None,
    node_count:       int  = None,
    neo4j_ms:         int  = None,
    resolver_trace         = None,
    last_entity:      dict = None,
    # UX enrichment toggles
    attach_templates: bool = True,
    attach_advisory:  bool = True,
    confidence:       float = 1.0,
) -> dict:
    """Standard retrieve() return dict shape + auto-attached UX
    enrichments (templates_block, per-MUST advisory) based on
    (question_type, cited_refs) — factoring out the boilerplate that
    used to live open-coded at each of retrieve()'s ~13 return sites.

    See task #203 for the migration arc. Wave 1: migrate the two
    fresh-dict paths (deterministic enumeration + LLM fallback).
    Wave 2: migrate the 11 `{**state, ...}` chat short-circuits.

    Rules:
      - `answer_text` also set as `answer` (alias — some consumers
        read either).
      - `question_type` also written to `intent_type` (both fields
        are read downstream; the timeline short-circuit comment at
        line ~2055 explains why they must be kept in sync).
      - When `state` is supplied, spread it into the result first
        (chat short-circuit shape). Explicit fields override state.
      - `templates_block` attached automatically when:
          * `attach_templates=True`
          * cited_refs non-empty
          * tenant + tenant_id resolvable
          * question_type is action-oriented (implementation /
            gap_analysis / posture_check / document_inventory /
            document_content — matches
            rag.templates.answer_footer._RELEVANT_QUESTION_TYPES).
      - Per-MUST advisory appendix appended to answer_text when:
          * `attach_advisory=True`
          * exactly ONE cited_ref (single-control query)
          * question_type in {posture_check, cross_framework}
          * tenant + tenant_id resolvable
        Uses intent.cited_refs preferentially when intent is passed
        (matches the pre-envelope behaviour that prefers the
        classifier's original cited refs over the LLM's expanded
        set, so xfw expansion doesn't suppress the advisory).
      - LLM-path metadata (`verified`, `posture_findings`,
        `node_count`, `neo4j_ms`, `resolver_trace`, `last_entity`)
        included only when the caller supplies them (chat short-
        circuits typically pass None → keys omitted).
    """
    import os as _os
    import logging as _logging
    _elog = _logging.getLogger(__name__)

    result: dict = {}
    if state:
        result.update(state)

    # Task #204: Per-MUST advisory appendix RETIRED as prose. The
    # advisory data now flows through templates_block.leaves[].items_missing
    # + upload_hint (see rag/templates/answer_footer.py enrichment loop).
    # `attach_advisory` kept as a parameter for backward compat + so the
    # SPA can suppress the enrichment if needed — but doesn't append text
    # to answer_text any more. The chat prose stays about the finding;
    # actionable "what next" lives entirely on the structured cards.
    _ = attach_advisory   # noqa: F841 — signature preserved

    # Freeze core fields.
    result["answer_text"]   = answer_text or ""
    result["answer"]        = answer_text or ""   # alias
    result["cited_refs"]    = list(cited_refs or [])
    result["answer_source"] = answer_source
    result["confidence"]    = confidence
    if question_type:
        result["question_type"] = question_type
        result["intent_type"]   = question_type

    # LLM-path metadata — include only when caller provided.
    if verified is not None:
        result["verified"] = verified
    if was_corrected is not None:
        result["was_corrected"] = was_corrected
    if posture_findings is not None:
        result["posture_findings"] = posture_findings
    if node_count is not None:
        result["node_count"] = node_count
    if neo4j_ms is not None:
        result["neo4j_ms"] = neo4j_ms
    if resolver_trace is not None:
        result["resolver_trace"] = resolver_trace
    if last_entity is not None:
        result["last_entity"] = last_entity

    # UX enrichment: templates_block.
    if attach_templates and cited_refs and tenant is not None:
        _tid = str(getattr(tenant, "tenant_id", "") or "")
        if _tid:
            try:
                from rag.templates.answer_footer import build_templates_block
                result["templates_block"] = build_templates_block(
                    cited_refs    = list(cited_refs),
                    question_type = question_type,
                    tenant_id     = _tid,
                    db_url        = _os.getenv("DATABASE_URL"),
                )
            except Exception as _e:
                _elog.warning("envelope: templates_block skipped: %s", _e)

    return result


def make_retrieve_node(
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,   # kept for API compat, used by fallback
    llm:       LLMAnswer,
    tenant:    TenantProfile,
    posture:   dict,
):
    """
    Node: vector retrieval + graph expansion + rank_and_answer (combined).
    Replaces: Steps 3-6 of _run_pipeline in one node.
    Uses rank_and_answer for zero-position-bias answering.
    """
    def retrieve(state: ArionState) -> dict:
        import re as _re
        from rag.classifier import QueryIntent, QuestionType

        # ── Deictic-only short-circuit (no last_entity to anchor) ─────────
        # Pattern 5 in [[conversational-context-routing-followup]]: when
        # the user asks "what about the policy?" / "tell me more" / "is
        # it ...?" with no entity carried from the prior turn (typically
        # because the prior turn was an inventory list, not a single-doc
        # match), neither the retriever nor the LLM has a real referent.
        # Without this short-circuit the retriever pulls default nodes
        # matching the topic word ("policy"), the LLM uses them, and
        # the user gets an NC dump for unrelated controls. Asking which
        # specific doc/control is the honest response.
        if (_is_deictic_only_query(state["query"])
                and not state.get("last_entity")):
            # Wave 2 migration (task #203). No cited_refs so templates/
            # advisory auto-attach skips anyway; being explicit here for
            # clarity — a clarification response shouldn't try to sell
            # template downloads.
            return build_answer_envelope(
                state            = state,
                answer_text      = _DEICTIC_CLARIFY_RESPONSE,
                cited_refs       = [],
                answer_source    = "deictic_clarify",
                question_type    = "unknown",
                attach_templates = False,
                attach_advisory  = False,
            )

        qtype_map = {
            "gap_analysis":       QuestionType.GAP_ANALYSIS,
            "implementation":     QuestionType.IMPLEMENTATION,
            "definition":         QuestionType.DEFINITION,
            "posture_check":      QuestionType.POSTURE_CHECK,
            "cross_framework":    QuestionType.CROSS_FRAMEWORK,
            "free_assessment":    QuestionType.FREE_ASSESSMENT,
            "document_inventory": QuestionType.DOCUMENT_INVENTORY,
            "document_content":   QuestionType.DOCUMENT_CONTENT,
            "unknown":            QuestionType.UNKNOWN,
        }
        qtype = qtype_map.get(state["intent_type"], QuestionType.UNKNOWN)

        from rag.classifier import QueryDimensions
        from enrichment.events.event_nodes import detect_events

        # Reconstruct dimensions from state
        # needs_documentation detected from query phrases
        from rag.classifier import _detect_document_dimensions, _detect_document_question_type
        needs_doc, doc_topic = _detect_document_dimensions(state["query"])
        doc_qtype = _detect_document_question_type(state["query"])
        if doc_qtype:
            qtype = doc_qtype

        dimensions = QueryDimensions(
            needs_obligation    = True,
            needs_posture       = state["needs_posture"],
            needs_documentation = needs_doc,
        )

        # Detect events from query
        try:
            detected_events = detect_events(state["query"])
        except Exception:
            detected_events = []

        intent = QueryIntent(
            question_type      = qtype,
            standards_scope    = state["standards"],
            role_filter        = state.get("role"),
            needs_posture      = state["needs_posture"],
            cited_refs         = state["focus_refs"],
            resolved_refs      = state["focus_refs"],
            confidence         = state["confidence"],
            raw_query          = state["query"],
            dimensions         = dimensions,
            detected_events    = detected_events,
            document_topic_ref = doc_topic,
        )

        # ── Acknowledge-gap short-circuit ─────────────────────────────────
        # Recognises "acknowledge the A.5.1 review record gap because X" and
        # writes status='acknowledged' on the matching tenant_evidence_gaps
        # row. Deterministic confirmation answer — no LLM, no resolver.
        # Per [[human_in_the_loop_positioning]]: acknowledging suppresses the
        # gap from the headline but does NOT flip the verdict to Comply.
        try:
            from rag.posture.acknowledge_chat import (
                parse_acknowledge_intent,
                acknowledge_gap,
                render_acknowledge_answer,
            )
            _ack_intent = parse_acknowledge_intent(state["query"])
            if _ack_intent is not None:
                import psycopg2
                _pg_conn = psycopg2.connect(
                    host     = os.getenv("POSTGRES_HOST", "127.0.0.1"),
                    dbname   = "arioncomply_compliance",
                    user     = "arioncomply_app",
                    password = os.getenv("POSTGRES_PASSWORD"),
                )
                try:
                    _ack_result = acknowledge_gap(
                        _pg_conn,
                        tenant_id = str(getattr(tenant, "tenant_id", "") or ""),
                        intent    = _ack_intent,
                    )
                finally:
                    _pg_conn.close()
                _ack_answer = render_acknowledge_answer(_ack_result, _ack_intent)
                # Wave 2 migration. Acknowledge-gap is a conversational
                # confirmation ("noted; the A.5.15 review-record gap is
                # acknowledged"). Skip templates_block + advisory
                # appendix — the tenant just told us the gap is OK; no
                # need to immediately push them a template.
                return build_answer_envelope(
                    state            = state,
                    answer_text      = _ack_answer,
                    cited_refs       = [_ack_intent.control_ref],
                    answer_source    = "postgres",
                    question_type    = "posture_check",
                    last_entity      = _control_entity(_ack_intent.control_ref),
                    attach_templates = False,
                    attach_advisory  = False,
                )
        except Exception as _ack_exc:
            (get_logger() or _NullLogger()).warning("acknowledge short-circuit failed: %s", _ack_exc)
            # Fall through to normal pipeline.

        # ── Stage-1 batch-approval short-circuit ──────────────────────────
        # Recognises "approve findings for A.5.1" / "reject findings for
        # A.5.18 because X" / "show pending findings [for A.5.1]" / "what
        # findings need review?". Implements the first HITL gate from
        # [[hitl-two-stage-approval-design]]: extraction proposes into
        # system_finding, this surface promotes the bundle to live finding
        # once the user approves.
        try:
            from rag.posture.stage1_review_chat import (
                parse_stage1_intent,
                list_pending_for_control,
                list_queue,
                approve_findings_for_control,
                reject_findings_for_control,
                render_stage1_answer,
            )
            _s1_intent = parse_stage1_intent(state["query"])
            if _s1_intent is not None:
                import psycopg2
                _pg_conn = psycopg2.connect(
                    host     = os.getenv("POSTGRES_HOST", "127.0.0.1"),
                    dbname   = "arioncomply_compliance",
                    user     = "arioncomply_app",
                    password = os.getenv("POSTGRES_PASSWORD"),
                )
                try:
                    _tenant_id = str(getattr(tenant, "tenant_id", "") or "")
                    _s1_listing = None
                    _s1_result  = {}
                    if _s1_intent.action == "list_queue":
                        _s1_listing = list_queue(_pg_conn, _tenant_id)
                    elif _s1_intent.action == "list_one":
                        _s1_listing = list_pending_for_control(
                            _pg_conn, _tenant_id, _s1_intent.control_ref,
                        )
                    elif _s1_intent.action == "approve":
                        _s1_result = approve_findings_for_control(
                            _pg_conn, _tenant_id, _s1_intent.control_ref,
                        )
                    elif _s1_intent.action == "reject":
                        _s1_result = reject_findings_for_control(
                            _pg_conn, _tenant_id, _s1_intent.control_ref,
                            _s1_intent.rationale,
                        )
                finally:
                    _pg_conn.close()
                _s1_answer = render_stage1_answer(
                    _s1_result, _s1_intent, listing=_s1_listing,
                )
                _refs = [_s1_intent.control_ref] if _s1_intent.control_ref else []
                # Wave 2 migration. Stage-1 approval is a HITL flow, not
                # a "what next" surface — skip templates/advisory.
                return build_answer_envelope(
                    state            = state,
                    answer_text      = _s1_answer,
                    cited_refs       = _refs,
                    answer_source    = "postgres",
                    question_type    = "posture_check",
                    last_entity      = _control_entity(_s1_intent.control_ref) if _s1_intent.control_ref else {},
                    attach_templates = False,
                    attach_advisory  = False,
                )
        except Exception as _s1_exc:
            (get_logger() or _NullLogger()).warning("stage1 review short-circuit failed: %s", _s1_exc)
            # Fall through to normal pipeline.

        # ── Stage-2 engine-verdict approval short-circuit ─────────────────
        # Recognises "approve engine verdict for A.5.1" / "reject engine
        # verdict for A.5.1 because X" / "show pending engine proposals" /
        # "what engine verdicts need review?". Promotes the persisted engine
        # proposal (commit 4) to live finding once approved.
        # The "engine verdict|proposal" object word keeps this surface
        # disjoint from [[stage1_review_chat]]'s "findings|extractions".
        try:
            from rag.posture.stage2_approval_chat import (
                parse_stage2_intent,
                list_pending_proposals,
                get_proposal_for_control,
                approve_engine_proposal,
                reject_engine_proposal,
                render_stage2_answer,
            )
            _s2_intent = parse_stage2_intent(state["query"])
            if _s2_intent is not None:
                import psycopg2
                _pg_conn = psycopg2.connect(
                    host     = os.getenv("POSTGRES_HOST", "127.0.0.1"),
                    dbname   = "arioncomply_compliance",
                    user     = "arioncomply_app",
                    password = os.getenv("POSTGRES_PASSWORD"),
                )
                try:
                    _tenant_id = str(getattr(tenant, "tenant_id", "") or "")
                    _s2_listing  = None
                    _s2_proposal = None
                    _s2_result   = {}
                    if _s2_intent.action == "list_queue":
                        _s2_listing = list_pending_proposals(_pg_conn, _tenant_id)
                    elif _s2_intent.action == "list_one":
                        _s2_proposal = get_proposal_for_control(
                            _pg_conn, _tenant_id, _s2_intent.control_ref,
                        )
                    elif _s2_intent.action == "approve":
                        _s2_result = approve_engine_proposal(
                            _pg_conn, _tenant_id, _s2_intent.control_ref,
                        )
                    elif _s2_intent.action == "reject":
                        _s2_result = reject_engine_proposal(
                            _pg_conn, _tenant_id, _s2_intent.control_ref,
                            _s2_intent.rationale,
                        )
                finally:
                    _pg_conn.close()
                _s2_answer = render_stage2_answer(
                    _s2_result, _s2_intent,
                    listing=_s2_listing, proposal=_s2_proposal,
                )
                _refs = [_s2_intent.control_ref] if _s2_intent.control_ref else []
                # Wave 2 migration. Stage-2 engine approval flow — same
                # rationale as Stage-1: HITL surface, skip templates/advisory.
                return build_answer_envelope(
                    state            = state,
                    answer_text      = _s2_answer,
                    cited_refs       = _refs,
                    answer_source    = "postgres",
                    question_type    = "posture_check",
                    last_entity      = _control_entity(_s2_intent.control_ref) if _s2_intent.control_ref else {},
                    attach_templates = False,
                    attach_advisory  = False,
                )
        except Exception as _s2_exc:
            (get_logger() or _NullLogger()).warning("stage2 approval short-circuit failed: %s", _s2_exc)
            # Fall through to normal pipeline.

        # ── Scope N/A short-circuit ───────────────────────────────────────
        # Physical security (A.7.x) and dev controls (A.8.25-31) are N/A.
        # Don't surface unrelated findings for these scope-excluded queries.
        if _is_scope_na_query(state["query"]):
            na_answer = _answer_scope_na(state["query"], posture)
            composed = polish_short_circuit_answer(
                query                = state["query"],
                deterministic_answer = na_answer,
                llm                  = llm,
            )
            # Wave 2 migration. Scope N/A response ("this doesn't apply
            # to us") — no cited_refs, no templates surface makes sense.
            return build_answer_envelope(
                state            = state,
                answer_text      = composed,
                cited_refs       = [],
                answer_source    = "postgres+llm",
                question_type    = "gap_analysis",
                attach_templates = False,
                attach_advisory  = False,
            )

        # ── Postgres short-circuit for posture timeline queries ────────────
        # "How did A.5.18 evolve?" / "show me the timeline for Art.32".
        # Reads posture_status_log directly — no LLM dependency on a
        # control's history the LLM doesn't have. Returns None when the
        # control has no history rows; falls through to the resolver in
        # that case so the user gets the current posture instead of a
        # "no data" dead-end.
        # ── S3l: cascade chat short-circuits ──────────────────────────────
        _tid = str(getattr(tenant, "tenant_id", "") or "")
        # Wave 2 migration. Cascade + timeline short-circuits report on
        # in-progress workflows (follow-ups, suppressions, implications,
        # posture history) — templates_block would misfire here as a
        # push-a-download surface where the tenant is asking about
        # process state. Skip templates/advisory on all three.
        if _is_cascade_followups_query(state["query"]):
            _fu_ans = _answer_cascade_followups(state["query"], _tid)
            if _fu_ans:
                composed = polish_short_circuit_answer(
                    query=state["query"], deterministic_answer=_fu_ans, llm=llm,
                )
                return build_answer_envelope(
                    state            = state,
                    answer_text      = composed,
                    cited_refs       = [],
                    answer_source    = "postgres+llm",
                    question_type    = "posture_check",
                    attach_templates = False,
                    attach_advisory  = False,
                )

        if _is_cascade_suppressions_query(state["query"]):
            _sp_ans = _answer_cascade_suppressions(state["query"], _tid)
            if _sp_ans:
                composed = polish_short_circuit_answer(
                    query=state["query"], deterministic_answer=_sp_ans, llm=llm,
                )
                return build_answer_envelope(
                    state            = state,
                    answer_text      = composed,
                    cited_refs       = [],
                    answer_source    = "postgres+llm",
                    question_type    = "posture_check",
                    attach_templates = False,
                    attach_advisory  = False,
                )

        if _is_cascade_impl_query(state["query"]):
            _ci_ref = _extract_cascade_ref(state["query"], state.get("focus_refs", []))
            _ci_ans = _answer_cascade_implications(state["query"], _tid, _ci_ref)
            if _ci_ans:
                composed = polish_short_circuit_answer(
                    query=state["query"], deterministic_answer=_ci_ans, llm=llm,
                )
                return build_answer_envelope(
                    state            = state,
                    answer_text      = composed,
                    cited_refs       = [_ci_ref] if _ci_ref else [],
                    answer_source    = "postgres+llm",
                    question_type    = "posture_check",
                    last_entity      = _control_entity(_ci_ref) if _ci_ref else None,
                    attach_templates = False,
                    attach_advisory  = False,
                )

        if _is_timeline_query(state["query"]):
            _ref = _extract_timeline_ref(state["query"], state.get("focus_refs", []))
            if _ref:
                _tl_answer = _answer_control_timeline(
                    query       = state["query"],
                    tenant_id   = str(getattr(tenant, "tenant_id", "") or ""),
                    control_ref = _ref,
                )
                if _tl_answer:
                    composed = polish_short_circuit_answer(
                        query                = state["query"],
                        deterministic_answer = _tl_answer,
                        llm                  = llm,
                    )
                    # Timeline query is a history report ("show me how
                    # A.5.18 evolved"). Skip templates/advisory.
                    return build_answer_envelope(
                        state            = state,
                        answer_text      = composed,
                        cited_refs       = [_ref],
                        answer_source    = "postgres+llm",
                        question_type    = "posture_check",
                        last_entity      = _control_entity(_ref),
                        attach_templates = False,
                        attach_advisory  = False,
                    )

        # ── Postgres short-circuit for upload status questions ─────────────
        # Runs BEFORE the resolver: the resolver's DOCUMENT_STATUS handler
        # only knows the "missing" side and mis-answers positive-polarity
        # queries via title-word heuristics. We have a polarity-aware
        # answerer + both data sides on the tenant profile, so use them.
        if (intent.question_type.value == "document_inventory"
                and _is_upload_status_query(state["query"])):
            _alerts   = getattr(tenant, "document_alerts", []) or []
            _uploaded = getattr(tenant, "uploaded_documents", []) or []
            pg_answer = _answer_upload_status(
                query    = state["query"],
                alerts   = _alerts,
                uploaded = _uploaded,
            )
            if pg_answer:
                # Fact-preserving prose polish over the deterministic answer.
                # Falls back to pg_answer on any failure — never regresses.
                composed = polish_short_circuit_answer(
                    query                = state["query"],
                    deterministic_answer = pg_answer,
                    llm                  = llm,
                )
                # Carry the matched entity (if any) into next-turn state
                # so deictic follow-ups ("this", "what about the policy?")
                # have the LLM access to prior-turn context.
                # See [[conversational-context-routing-followup]].
                last_entity = _resolve_upload_entity(state["query"], _uploaded, _alerts)
                # Wave 2 migration. Upload inventory question — answers
                # "do we have doc X?"; no cited_refs so templates auto-
                # skip anyway. Being explicit for clarity.
                return build_answer_envelope(
                    state            = state,
                    answer_text      = composed,
                    cited_refs       = [],
                    answer_source    = "postgres+llm",
                    question_type    = "document_inventory",
                    last_entity      = last_entity,
                    attach_templates = False,
                    attach_advisory  = False,
                )

        # ── Resolver: dispatch to per-taxonomy data sources ──────────────
        # Replaces ~190 lines of inline retrieval assembly.
        # Each taxonomy type gets the right sources (DB / graph / vector / both).
        from rag.resolver import Resolver, ResolveRequest
        from rag.taxonomy  import get_taxonomy_type

        _resolver = Resolver(
            retriever = retriever,
            expander  = expander,
            posture   = posture,
        )
        _req = ResolveRequest(
            query            = state["query"],
            classifier_type  = state["intent_type"],
            tenant_context   = tenant,
            topic_ref        = intent.document_topic_ref,
            standards        = intent.standards_scope,
            history          = [],
            # Explicit refs from the query — used by handlers to seed graph
            # expansion when the user names a specific control by ref
            cited_refs       = list(getattr(intent, "cited_refs", []) or []),
            # Observability: thread_id from LangGraph state = conversation request_id
            # tenant_id denormalised for fast trace access without hitting tenant_context
            request_id       = state.get("thread_id") or state.get("session_id") or "",
            tenant_id        = str(getattr(tenant, "tenant_id", "") or ""),
        )
        _resolved = _resolver.resolve(_req)

        # Short-circuit: Resolver found a direct Postgres answer
        if _resolved.has_short_circuit:
            composed = polish_short_circuit_answer(
                query                = state["query"],
                deterministic_answer = _resolved.short_circuit_answer,
                llm                  = llm,
            )
            # Wave 2 migration. Resolver short-circuit — sets cited_refs=[]
            # by convention (the SC has already composed its own citations
            # into the answer text). No templates surface makes sense
            # without cited_refs to route.
            return build_answer_envelope(
                state            = state,
                answer_text      = composed,
                cited_refs       = [],
                answer_source    = "postgres+llm",
                question_type    = state["intent_type"],
                attach_templates = False,
                attach_advisory  = False,
            )

        # Store resolver trace in state for ANALYTICS display
        # (before we check for short-circuit so it's always available)
        _trace = getattr(_resolved, "trace", None)

        # Build expanded from resolved context
        # graph_nodes is always GraphResult after Phase 1 rewrite
        _gr              = _resolved.graph_nodes
        expanded_nodes   = _gr.all_nodes if hasattr(_gr, "all_nodes") else list(_gr)
        doc_contexts     = _resolved.doc_contexts   # property on ResolvedContext
        # Read active incidents + their materialized obligations from Postgres
        # (enriched by Neo4j for required-document IDs). Returns [] if either
        # store unavailable — chat still works without incident context.
        incident_contexts = expander.get_incident_obligations(
            tenant_id = state["tenant_id"],
            standards = state["standards"],
        )
        neo4j_ms         = _resolved.neo4j_ms

        # ── Rank + Answer in one Mistral call ──────────────────────────────
        # Pass all non-informational nodes as a numbered list.
        # Mistral selects the most relevant nodes and answers from them.
        # No position bias — every node gets equal attention.
        all_nodes = [
            n for n in expanded_nodes
            if not getattr(n, 'is_informational', False)
        ]

        standards_str = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in state["standards"]
        )

        # Deterministic compose for POSTURE_CHECK enumeration queries.
        # Truth IS the posture data; LLM ranking adds stochasticity, drops
        # control titles, and breaks markdown. See L3 in
        # [[posture-claim-hallucination-guard]].
        if (intent.question_type == QuestionType.POSTURE_CHECK
                and _is_posture_enumeration_query(state["query"])):
            _det_text = _compose_posture_enumeration_answer(
                expanded_nodes  = all_nodes,
                posture         = posture,
                scope_standards = list(getattr(tenant, "applicable_standards", []) or []),
                tenant_name     = getattr(tenant, "name", "") or "",
                auditor_attestations = _fetch_auditor_attestations(
                    str(getattr(tenant, "tenant_id", "") or "")
                ),
            )
            if _det_text:
                _det_refs = [
                    n.ref for n in all_nodes
                    if (posture or {}).get(n.node_id, {}).get("finding")
                       in ("NC", "OFI", "Comply")
                ]
                _det_findings = {
                    n.ref: (posture or {}).get(n.node_id, {}).get("finding")
                    for n in all_nodes
                    if (posture or {}).get(n.node_id, {}).get("finding")
                }
                # Wave 1 migration to build_answer_envelope (task #203):
                # replaces the open-coded templates_block + return dict
                # with the shared envelope. Same behavior (templates_block
                # auto-attaches for action-oriented questions when
                # cited_refs are present) — no expected change.
                return build_answer_envelope(
                    answer_text      = _det_text,
                    cited_refs       = _det_refs,
                    answer_source    = "posture_enumeration_deterministic",
                    question_type    = intent.question_type.value,
                    tenant           = tenant,
                    intent           = intent,
                    verified         = True,
                    was_corrected    = False,
                    posture_findings = _det_findings,
                    node_count       = len(all_nodes),
                    neo4j_ms         = neo4j_ms,
                    resolver_trace   = _trace,
                )

        result = llm.rank_and_answer(
            query            = state["query"],
            nodes            = all_nodes,
            posture          = posture,
            intent           = intent,
            tenant_name      = state["tenant_id"],
            standards        = standards_str,
            doc_contexts     = doc_contexts     if doc_contexts     else None,
            incident_contexts= incident_contexts if incident_contexts else None,
            # Scope guard: only standards the tenant has enrolled in
            # (direct + bridged) are citable. xfw expansion is filtered
            # to this set so we never reference a framework the client
            # hasn't actually rolled out.
            scope_standards  = list(getattr(tenant, "applicable_standards", []) or []),
            # Prior-turn entity (populated by upload-status short-circuit
            # on the previous turn) — lets the LLM ground deictic
            # follow-ups instead of returning a generic empty-retrieval
            # template. See [[conversational-context-routing-followup]].
            last_entity      = state.get("last_entity") or None,
        )

        # ── Write structured trace to DB (best-effort, never blocks answer) ─
        # Note: previously the templates_block attachment + per-MUST
        # advisory appendix lived open-coded here. Wave 1 migration
        # (task #203) moved that logic into build_answer_envelope so
        # every retrieve() return site gets consistent UX enrichment.
        if _trace:
            try:
                _write_request_trace(
                    posture_db = posture_db if "posture_db" in dir() else None,
                    trace      = _trace,
                    tenant     = tenant,
                    topic_ref  = getattr(intent, "document_topic_ref", None),
                )
            except Exception as _te:
                logger.debug(f"[trace] write skipped: {_te}")

        _qt_value = (
            intent.question_type.value
            if intent and getattr(intent, "question_type", None)
            else None
        )
        return build_answer_envelope(
            answer_text      = result.answer_text,
            cited_refs       = result.cited_refs or [],
            answer_source    = "llm",
            question_type    = _qt_value,
            tenant           = tenant,
            intent           = intent,
            verified         = result.verified,
            was_corrected    = result.was_corrected,
            posture_findings = result.posture_findings,
            node_count       = len(all_nodes),
            neo4j_ms         = neo4j_ms,
            resolver_trace   = _trace,
        )

    return retrieve


def _write_request_trace(posture_db, trace, tenant, topic_ref) -> None:
    """
    Write one row to request_trace_log.
    Best-effort — called in a try/except so failures never block answers.
    posture_db: the Postgres connection/engine used for posture queries.
    """
    if not posture_db or not trace:
        return

    tenant_id = str(getattr(tenant, "tenant_id", "") or "")
    if not tenant_id:
        return

    sql = """
        INSERT INTO request_trace_log (
            request_id, tenant_id,
            query_text, classifier_type, taxonomy_type, handler_name,
            strategy, topic_ref,
            policy_posture, policy_vector, policy_graph,
            policy_doc_inv, policy_short_circuit,
            node_ids_built, nodes_primary, nodes_secondary,
            vector_hits, doc_contexts,
            posture_ids_used, vector_top_scores,
            posture_total, posture_nc, posture_ofi,
            posture_confirmed, posture_draft,
            short_circuit, answer_source,
            neo4j_ms, vector_ms, postgres_ms, total_ms,
            error_type, error_hint,
            traced_at
        ) VALUES (
            %(request_id)s, %(tenant_id)s::UUID,
            %(query_text)s, %(classifier_type)s, %(taxonomy_type)s, %(handler_name)s,
            %(strategy)s, %(topic_ref)s,
            %(policy_posture)s, %(policy_vector)s, %(policy_graph)s,
            %(policy_doc_inv)s, %(policy_short_circuit)s,
            %(node_ids_built)s, %(nodes_primary)s, %(nodes_secondary)s,
            %(vector_hits)s, %(doc_contexts)s,
            %(posture_ids_used)s, %(vector_top_scores)s::JSONB,
            %(posture_total)s, %(posture_nc)s, %(posture_ofi)s,
            %(posture_confirmed)s, %(posture_draft)s,
            %(short_circuit)s, %(answer_source)s,
            %(neo4j_ms)s, %(vector_ms)s, %(postgres_ms)s, %(total_ms)s,
            %(error_type)s, %(error_hint)s,
            NOW()
        )
        ON CONFLICT DO NOTHING
    """
    import json
    params = {
        "request_id":         trace.request_id or "",
        "tenant_id":          tenant_id,
        "query_text":         trace.query[:500],
        "classifier_type":    trace.classifier_type,
        "taxonomy_type":      trace.taxonomy_type,
        "handler_name":       trace.handler_name,
        "strategy":           trace.strategy,
        "topic_ref":          topic_ref,
        "policy_posture":     trace.policy_posture,
        "policy_vector":      trace.policy_vector,
        "policy_graph":       trace.policy_graph,
        "policy_doc_inv":     trace.policy_doc_inv,
        "policy_short_circuit": trace.policy_short_circuit,
        "node_ids_built":     trace.node_ids_built,
        "nodes_primary":      trace.nodes_primary,
        "nodes_secondary":    trace.nodes_secondary,
        "vector_hits":        trace.vector_results,
        "doc_contexts":       trace.doc_contexts,
        "posture_ids_used":   trace.posture_ids_used or [],
        "vector_top_scores":  json.dumps(trace.vector_top_scores or []),
        "posture_total":      trace.posture_total,
        "posture_nc":         trace.posture_nc,
        "posture_ofi":        trace.posture_ofi,
        "posture_confirmed":  trace.posture_confirmed,
        "posture_draft":      trace.posture_draft,
        "short_circuit":      trace.short_circuit,
        "answer_source":      trace.answer_source,
        "neo4j_ms":           trace.neo4j_ms,
        "vector_ms":          trace.vector_ms,
        "postgres_ms":        trace.postgres_ms,
        "total_ms":           trace.total_ms,
        "error_type":         type(trace.error).__name__ if trace.error else None,
        "error_hint":         trace.error_hint,
    }

    # Support psycopg2 connection, SQLAlchemy engine, or connection pool
    if hasattr(posture_db, "execute"):
        posture_db.execute(sql, params)
    elif hasattr(posture_db, "connect"):
        with posture_db.connect() as conn:
            conn.execute(sql, params)
            if hasattr(conn, "commit"):
                conn.commit()


def _node_exists_check(node_id: str, retriever) -> bool:
    """Check if a node_id exists in ChromaDB."""
    try:
        parts = node_id.split(":")
        ref = parts[-1]
        result = retriever.search_by_ref(ref)
        return result is not None
    except Exception:
        return False


# make_answer_node removed — rank_and_answer is now in make_retrieve_node

def make_clarify_node():
    """
    Node: return clarification question to user.
    Replaces: _clarification_response.
    """
    def clarify(state: ArionState) -> dict:
        # Nothing to compute — clarif_question already set by classify node
        return {}

    return clarify


def make_update_session_node():
    """
    Node: update session state after successful answer.
    Replaces: scattered session.update_refs() calls.
    This is the ONLY place focus_refs can be updated — no more stale ref bugs.
    """
    def update_session(state: ArionState) -> dict:
        return {
            "turn_count":    state["turn_count"] + 1,
            "clarif_count":  0,
            "needs_clarif":  False,
            "clarif_question": "",
        }

    return update_session


# ── Routing ─────────────────────────────────────────────────────────────────

def route_after_classify(
    state: ArionState,
) -> Literal["retrieve", "clarify"]:
    """
    Replaces: if/else routing in _handle_intake and _handle_query.
    Single explicit decision point — no more hidden routing logic.
    """
    if state["needs_clarif"]:
        return "clarify"
    return "retrieve"


# ── Graph builder ────────────────────────────────────────────────────────────

def build_arion_graph(
    tenant:    TenantProfile,
    retriever: VectorRetriever,
    expander:  GraphExpander,
    assembler: ContextAssembler,
    llm:       LLMAnswer,
    classifier: QueryClassifier,
    posture:   dict,
    checkpointer = None,
):
    """
    Build and compile the ArionComply LangGraph pipeline.
    
    Args:
        checkpointer: SqliteSaver, PostgresSaver, or MemorySaver instance
                      If None, uses in-memory (no persistence)
    
    Returns:
        Compiled graph ready for invoke()
    """
    builder = StateGraph(ArionState)

    # Add nodes
    builder.add_node("classify",       make_classify_node(classifier))
    builder.add_node("retrieve",       make_retrieve_node(retriever, expander, assembler, llm, tenant, posture))
    builder.add_node("clarify",        make_clarify_node())
    builder.add_node("update_session", make_update_session_node())

    # Entry point
    builder.set_entry_point("classify")

    # Edges — retrieve now includes rank_and_answer (no separate answer node)
    builder.add_conditional_edges("classify", route_after_classify)
    builder.add_edge("retrieve",       "update_session")
    builder.add_edge("update_session", END)
    builder.add_edge("clarify",        END)

    compiled = builder.compile(checkpointer=checkpointer)

    # Force Neo4j connection warmup — explicitly cache _online=True
    # so the retrieve node doesn't hit a timeout on first graph.invoke()
    if hasattr(expander, '_is_online'):
        online = expander._is_online()
        if online:
            # Explicitly confirm so _online stays True across invocations
            expander._online = True
        else:
            import warnings
            warnings.warn(
                "Neo4j is offline at graph build time — "
                "expansion will use vector-only mode until Neo4j is reachable.",
                RuntimeWarning,
            )

    return compiled


# ── Convenience: get default checkpointer ───────────────────────────────────

def get_checkpointer(db_path: str = None):
    """
    Sync checkpointer for graph.invoke() — uses PostgresSaver (psycopg v3).
    For async streaming use get_async_checkpointer().
    """
    import logging
    _log = logging.getLogger(__name__)

    sessions_url = (
        os.getenv("SESSIONS_DATABASE_URL") or
        os.getenv("DATABASE_URL", "").replace(
            "arioncomply_compliance", "arioncomply_sessions"
        )
    )

    if sessions_url and "arioncomply" in sessions_url:
        try:
            import psycopg
            from langgraph.checkpoint.postgres import PostgresSaver
            # autocommit=True is REQUIRED by langgraph's PostgresSaver:
            # without it, checkpoint writes never commit and follow-up
            # turns can't see prior state across requests.
            conn = psycopg.connect(sessions_url, autocommit=True)
            saver = PostgresSaver(conn)
            saver.setup()
            _log.info(f"Checkpointer: PostgresSaver ({sessions_url.split('@')[-1]})")
            return saver
        except Exception as _e:
            _log.warning(f"PostgresSaver failed ({_e}) — falling back to InMemorySaver")

    from langgraph.checkpoint.memory import InMemorySaver
    _log.info("Checkpointer: InMemorySaver")
    return InMemorySaver()


async def get_async_checkpointer():
    """
    Async checkpointer for graph.astream_events() — uses AsyncPostgresSaver (psycopg v3 async).
    Falls back to InMemorySaver if Postgres unavailable.
    """
    import logging
    _log = logging.getLogger(__name__)

    sessions_url = (
        os.getenv("SESSIONS_DATABASE_URL") or
        os.getenv("DATABASE_URL", "").replace(
            "arioncomply_compliance", "arioncomply_sessions"
        )
    )

    if sessions_url and "arioncomply" in sessions_url:
        try:
            import psycopg
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            # autocommit=True required: otherwise writes never commit and
            # cross-request state (turn_count, taxonomy_options_map, ...)
            # is lost between calls — causing infinite clarification loops.
            conn = await psycopg.AsyncConnection.connect(
                sessions_url, autocommit=True
            )
            saver = AsyncPostgresSaver(conn)
            await saver.setup()
            _log.info(f"AsyncCheckpointer: AsyncPostgresSaver ({sessions_url.split('@')[-1]})")
            return saver
        except Exception as _e:
            _log.warning(f"AsyncPostgresSaver failed ({_e}) — falling back to InMemorySaver")

    from langgraph.checkpoint.memory import InMemorySaver
    _log.info("AsyncCheckpointer: InMemorySaver")
    return InMemorySaver()

