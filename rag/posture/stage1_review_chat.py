"""ArionComply — chat surface for Stage-1 batch approval of extraction findings.

Recognises queries like:
  "approve findings for A.5.1"
  "approve A.5.1 extractions"
  "reject findings for A.5.18 because the extractor misread Section 4"
  "show pending findings for A.5.1"
  "what findings need review?"

Implements the first HITL gate from [[hitl-two-stage-approval-design]]:
extraction writes stage proposals into posture_controls.system_finding;
the live posture_controls.finding only changes once the user approves the
extraction's per-finding bundle. Per-control batch approval — no
per-finding auto-promotion of the parent posture row.

Per [[human_in_the_loop_positioning]]: the platform proposes, the client
decides. Approve promotes the proposal to live; reject preserves the
finding (is_active=false + rejection_reason) so the auditor can see the
extraction that was overridden.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ── Slot grammar ──────────────────────────────────────────────────────────────

# Approve verbs — limited to extraction-approval vocabulary so we don't
# collide with [[acknowledge-gap]]'s "dismiss" verb (which requires a role
# slot to fire). "approve" / "accept" / "confirm" are the natural Stage-1
# verbs and have no overlap with the acknowledge surface.
_APPROVE_RE = re.compile(
    r"\b(?:approve|accept|confirm)\b",
    re.IGNORECASE,
)
_REJECT_RE = re.compile(
    r"\b(?:reject|deny)\b",
    re.IGNORECASE,
)
# List/queue verbs — three sub-shapes:
#   "show|list pending findings [for X]"
#   "what findings need review|approval?"
#   "review queue" / "review findings for X"
_LIST_RE = re.compile(
    r"\b(?:"
    r"pending\s+findings|"
    r"findings?\s+(?:need|needing|awaiting)\s+(?:review|approval)|"
    r"review\s+(?:queue|findings)|"
    r"what\s+findings?\s+(?:need|needs|require)"
    r")\b",
    re.IGNORECASE,
)
# "findings" / "extraction(s)" / "extracted findings" — the object being
# approved. Required for approve/reject verbs so we don't fire on "approve
# A.5.1 as Comply" or "approve the policy".
_OBJECT_RE = re.compile(
    r"\b(?:findings?|extractions?|extracted|proposals?|pending)\b",
    re.IGNORECASE,
)
# Control reference — same shape as [[acknowledge-chat]].
_CONTROL_RE = re.compile(
    r"\b("
    r"A\.\d+(?:\.\d+)*"
    r"|Art\.\d+(?:\.\d+[a-z]?)*"
    r"|\d+\.\d+(?:\.\d+)?"   # ISMS clauses 4.1 … 10.2 — \d+ so '10.x' matches
    r")\b",
)
# Optional rationale on rejection.
_RATIONALE_RE = re.compile(
    r"(?:\bbecause\b|\bsince\b|\breason:?\b|—|-)\s*(?P<reason>.+?)\s*\.?\s*$",
    re.IGNORECASE,
)
# Disqualifier — the xfw proposer owns "cross-framework findings need review"
# queries via [[rag/resolver.py:_build_xfw_proposals_answer]]. Stage-1 is for
# primary-standard extraction findings only, so we yield to xfw on any query
# that names the cross-framework / xfw surface explicitly.
_XFW_DISQUALIFIER_RE = re.compile(
    r"\b(?:cross[\s-]?framework|xfw|x[\s-]?framework)\b",
    re.IGNORECASE,
)


@dataclass
class Stage1Intent:
    action:      str                # 'approve' | 'reject' | 'list_one' | 'list_queue'
    control_ref: Optional[str]      # required for approve/reject/list_one
    rationale:   str                # rejection reason; "" for approve/list
    raw_query:   str


def parse_stage1_intent(query: str) -> Optional[Stage1Intent]:
    """Returns a Stage1Intent if the query is recognisably a Stage-1
    approval / rejection / review request, else None. Conservative grammar:
    approve/reject require both a verb AND an object word ("findings" /
    "extractions") AND a control ref — anything weaker would fire on
    unrelated approve-the-policy prose."""
    if not query:
        return None

    # Yield to the xfw proposer surface for cross-framework queue queries —
    # they share the "findings need review" suffix but belong to a different
    # write surface ([[rag/resolver.py:_build_xfw_proposals_answer]]).
    if _XFW_DISQUALIFIER_RE.search(query):
        return None

    is_approve = bool(_APPROVE_RE.search(query))
    is_reject  = bool(_REJECT_RE.search(query))
    is_list    = bool(_LIST_RE.search(query))

    if not (is_approve or is_reject or is_list):
        return None

    ctrl_m = _CONTROL_RE.search(query)
    ctrl   = ctrl_m.group(1) if ctrl_m else None

    if is_approve or is_reject:
        # Require the object word so "approve A.5.1 as Comply" / "approve
        # the policy" don't accidentally fire as Stage-1 batch approval.
        if not _OBJECT_RE.search(query):
            return None
        if not ctrl:
            return None
        rationale = ""
        if is_reject:
            r_m = _RATIONALE_RE.search(query)
            if r_m:
                rationale = (r_m.group("reason") or "").strip().rstrip(".")
        return Stage1Intent(
            action      = "approve" if is_approve else "reject",
            control_ref = ctrl,
            rationale   = rationale,
            raw_query   = query,
        )

    # List flow — control_ref optional. Without a control_ref we surface
    # the multi-control queue; with one we list that control's pending
    # findings only.
    return Stage1Intent(
        action      = "list_one" if ctrl else "list_queue",
        control_ref = ctrl,
        rationale   = "",
        raw_query   = query,
    )


# ── Read paths ────────────────────────────────────────────────────────────────

# Module-level cache: checklist_item_id → (must_text, leaf_id, leaf_title,
# category). Built lazily on first call so import is cheap. The curation
# set is static for the process lifetime; rebuild only on engine restart.
_ITEM_LOOKUP: Optional[dict[str, tuple[str, str, str, str]]] = None

def _build_item_lookup() -> dict[str, tuple[str, str, str, str]]:
    """Index every ChecklistItem (MUST + SHOULD) across the curation set.
    Returns {item_id: (text, leaf_id, leaf_title, category)}."""
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    out: dict[str, tuple[str, str, str, str]] = {}
    def add(er):
        for it in list(er.must_contain) + list(er.should_contain):
            out[it.id] = (it.text, er.id, er.title, it.category)
    for er in ALL_EVIDENCE_REQUIREMENTS:
        add(er)
    for spec in ALL_DERIVED_SPECS:
        for er in spec.direct_evidence:
            add(er)
    return out

# Excerpt-parse regex: extracts sheet_name + column_name from the
# "sheet 'X' col 'Y'" excerpt format the workbook persistence layer emits.
# Falls back gracefully when the excerpt has another shape (LLM doc
# extraction, xfw inference, etc.) — the parser returns (None, None).
import re as _re
_EXCERPT_RE = _re.compile(r"sheet '([^']+)' col '([^']+)'")


def list_pending_for_control(pg_conn, tenant_id: str, control_ref: str) -> list[dict]:
    """Return the pending findings for one control. Each row carries enough
    context for the Stage-1 detail view to group by sheet + leaf and show
    the MUST text the binding satisfies:

    Keys:
      finding_id, status, confidence, excerpt, extracted_at,
      inferred_from_control_ref, inferred_from_standard_id, inference_source,
      checklist_item_id, must_text, must_category (must|should),
      leaf_id, leaf_title,
      sheet_name, column_name (parsed from excerpt; None when not workbook-shaped)

    The MUST + leaf fields come from the curation lookup; the sheet/column
    fields come from parsing the excerpt. None values are returned when a
    field can't be resolved (older findings without checklist_item_id,
    LLM-doc-extraction excerpts in another shape, etc.) — the UI handles
    those gracefully.

    Inference fields let the UI show the source control when a finding
    was derived (GDPR Art via xfw) rather than directly extracted — see
    [[stage1-detail-show-inference-chain-idea]]."""
    global _ITEM_LOOKUP
    if _ITEM_LOOKUP is None:
        _ITEM_LOOKUP = _build_item_lookup()

    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            """
            SELECT id::text, status, confidence, excerpt, extracted_at::text,
                   inferred_from_control_ref, inferred_from_standard_id,
                   inference_source,
                   checklist_item_id
              FROM document_findings
             WHERE tenant_id     = %s
               AND control_ref   = %s
               AND review_status = 'pending'
               AND is_active     = TRUE
             ORDER BY extracted_at
            """,
            (tenant_id, control_ref),
        )
        rows = cur.fetchall()

    out: list[dict] = []
    for r in rows:
        excerpt = r[3] or ""
        item_id = r[8]
        # Curation lookup
        if item_id and item_id in _ITEM_LOOKUP:
            must_text, leaf_id, leaf_title, category = _ITEM_LOOKUP[item_id]
        else:
            must_text, leaf_id, leaf_title, category = None, None, None, None
        # Parse sheet + column from excerpt when in workbook shape
        m = _EXCERPT_RE.match(excerpt)
        sheet_name = m.group(1) if m else None
        column_name = m.group(2) if m else None
        out.append({
            "finding_id":                r[0],
            "status":                    r[1],
            "confidence":                r[2],
            "excerpt":                   excerpt,
            "extracted_at":              r[4],
            "inferred_from_control_ref": r[5],
            "inferred_from_standard_id": r[6],
            "inference_source":          r[7],
            "checklist_item_id":         item_id,
            "must_text":                 must_text,
            "must_category":             category,
            "leaf_id":                   leaf_id,
            "leaf_title":                leaf_title,
            "sheet_name":                sheet_name,
            "column_name":               column_name,
        })
    return out


def list_queue(pg_conn, tenant_id: str) -> list[dict]:
    """Return per-control pending counts so the user can pick which queue
    to drain first. Sorted by count desc — controls with the most pending
    findings first."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            """
            SELECT control_ref, standard_id, count(*) AS n
              FROM document_findings
             WHERE tenant_id     = %s
               AND review_status = 'pending'
               AND is_active     = TRUE
             GROUP BY control_ref, standard_id
             ORDER BY n DESC, control_ref
            """,
            (tenant_id,),
        )
        return [
            {"control_ref": r[0], "standard_id": r[1], "pending_count": r[2]}
            for r in cur.fetchall()
        ]


# ── Write paths ───────────────────────────────────────────────────────────────

# Finding priority for aggregation. Mirrors posture_writer._FINDING_PRIORITY
# so the Stage-1 promotion picks the same headline finding the writer
# proposed in system_finding.
_FINDING_PRIORITY: dict[str, int] = {
    "NC": 3, "OFI": 2, "Comply": 1, "N/A": 0, "Not assessed": -1,
}

# df.status → posture finding vocabulary. Mirrors posture_writer's
# _FINDING_TO_DF_STATUS in reverse, then promoted to posture vocab.
_DF_STATUS_TO_FINDING: dict[str, str] = {
    "missing": "NC",
    "partial": "OFI",
    "present": "Comply",
}


def approve_findings_for_control(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    reviewed_by:  str = "chat_user",
) -> dict:
    """Promote pending findings for one control to approved and flip the
    parent posture_controls row to confirmation_status='document_confirmed'.

    The live posture_controls.finding adopts the aggregate of the just-
    approved findings (NC > OFI > Comply > N/A) — same priority the
    writer used when populating system_finding. Falls back to system_finding
    if all approved rows share that aggregate (the typical case).

    Returns:
      {'ok': True,  'control_ref': X, 'approved': N, 'finding': F, 'standard_id': S}
      {'ok': False, 'reason': 'no_pending' | 'db_error'}
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

            cur.execute(
                """
                SELECT id, status, standard_id
                  FROM document_findings
                 WHERE tenant_id     = %s
                   AND control_ref   = %s
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                """,
                (tenant_id, control_ref),
            )
            rows = cur.fetchall()
            if not rows:
                return {"ok": False, "reason": "no_pending"}

            standard_id = rows[0][2]
            finding_ids = [r[0] for r in rows]
            statuses    = [r[1] for r in rows]
            promoted_findings = [
                _DF_STATUS_TO_FINDING.get(s, "Not assessed") for s in statuses
            ]
            headline = max(
                promoted_findings,
                key=lambda f: _FINDING_PRIORITY.get(f, -1),
            )

            cur.execute(
                """
                UPDATE document_findings
                   SET review_status = 'approved',
                       reviewed_by   = %s::uuid,
                       reviewed_at   = NOW()
                 WHERE id = ANY(%s::uuid[])
                """,
                (_uuid_or_null(reviewed_by), finding_ids),
            )

            cur.execute(
                """
                SELECT id, finding, confirmation_status, source
                  FROM posture_controls
                 WHERE tenant_id   = %s
                   AND control_ref = %s
                   AND standard_id = %s
                   AND is_active   = TRUE
                 LIMIT 1
                """,
                (tenant_id, control_ref, standard_id),
            )
            pc = cur.fetchone()
            if not pc:
                # The writer's INSERT path should have created the row in
                # 'draft' / 'Not assessed' state, but defend against drift.
                pg_conn.commit()
                return {
                    "ok": True,
                    "control_ref":  control_ref,
                    "standard_id":  standard_id,
                    "approved":     len(finding_ids),
                    "finding":      headline,
                    "prior_finding": None,
                    "no_posture_row": True,
                }
            posture_id, prior_finding, prior_status, prior_source = pc

            # Stage-1 contract per [[posture-engine-alignment-plan-2026-05-22]]
            # Phase D: confirm the *evidence*, not the posture. We mark the
            # control as document_confirmed (the human accepted the extracted
            # findings) but leave posture_controls.finding untouched — the
            # fulfilment engine + Stage-2 are the only path that mutates it.
            # No posture_status_log row either; this isn't a finding change.
            cur.execute(
                """
                UPDATE posture_controls
                   SET confirmation_status = 'document_confirmed',
                       confirmed_by        = %s::uuid,
                       confirmed_at        = NOW(),
                       source              = 'document'
                 WHERE id = %s
                """,
                (_uuid_or_null(reviewed_by), posture_id),
            )

        pg_conn.commit()
        return {
            "ok":            True,
            "control_ref":   control_ref,
            "standard_id":   standard_id,
            "approved":      len(finding_ids),
            "finding":       headline,
            "prior_finding": prior_finding,
        }

    except Exception as e:
        logger.warning("stage1_review_chat.approve: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def reject_findings_for_control(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    rationale:    str,
    reviewed_by:  str = "chat_user",
) -> dict:
    """Reject all pending findings for one control. Rows go is_active=false
    + rejection_reason + reviewed_by/at. The live posture_controls.finding
    is NOT touched — rejection is the auditor-preserving alternative to
    silent deletion, not an override of posture.

    Returns:
      {'ok': True,  'control_ref': X, 'rejected': N}
      {'ok': False, 'reason': 'no_pending' | 'no_rationale' | 'db_error'}
    """
    if not rationale or not rationale.strip():
        return {"ok": False, "reason": "no_rationale"}

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                UPDATE document_findings
                   SET review_status    = 'rejected',
                       rejection_reason = %s,
                       reviewed_by      = %s::uuid,
                       reviewed_at      = NOW(),
                       is_active        = FALSE
                 WHERE tenant_id     = %s
                   AND control_ref   = %s
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                """,
                (rationale[:500], _uuid_or_null(reviewed_by),
                 tenant_id, control_ref),
            )
            n = cur.rowcount
            if n == 0:
                return {"ok": False, "reason": "no_pending"}
        pg_conn.commit()
        return {"ok": True, "control_ref": control_ref, "rejected": n}

    except Exception as e:
        logger.warning("stage1_review_chat.reject: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def approve_findings_by_ids(
    pg_conn,
    tenant_id:    str,
    finding_ids:  list[str],
    reviewed_by:  str = "chat_user",
) -> dict:
    """Per-finding-id variant of [[approve_findings_for_control]]. Promotes
    only the named findings and recomputes each touched control's headline
    from ALL currently-approved+active findings (not just this batch) so
    partial approval doesn't overwrite a prior high-priority promotion.

    Returns:
      {'ok': True, 'approved': N, 'controls': [{control_ref, standard_id,
       finding, prior_finding}, ...]}
      {'ok': False, 'reason': 'no_pending' | 'db_error'}
    """
    if not finding_ids:
        return {"ok": False, "reason": "no_pending"}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

            cur.execute(
                """
                UPDATE document_findings
                   SET review_status = 'approved',
                       reviewed_by   = %s::uuid,
                       reviewed_at   = NOW()
                 WHERE tenant_id     = %s::uuid
                   AND id            = ANY(%s::uuid[])
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                RETURNING control_ref, standard_id
                """,
                (_uuid_or_null(reviewed_by), tenant_id, finding_ids),
            )
            touched_rows = cur.fetchall()
            if not touched_rows:
                return {"ok": False, "reason": "no_pending"}

            seen: set[tuple[str, str]] = set()
            control_results: list[dict] = []
            for control_ref, standard_id in touched_rows:
                key = (control_ref, standard_id)
                if key in seen:
                    continue
                seen.add(key)
                control_results.append(_recompute_posture_for_control(
                    cur, tenant_id, control_ref, standard_id, reviewed_by,
                ))

        pg_conn.commit()
        return {
            "ok":       True,
            "approved": len(touched_rows),
            "controls": control_results,
        }
    except Exception as e:
        logger.warning("stage1_review_chat.approve_by_ids: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def _recompute_posture_for_control(
    cur, tenant_id: str, control_ref: str, standard_id: str, reviewed_by: str,
) -> dict:
    """Recompute the posture_controls.finding headline from ALL active+
    approved document_findings for (control_ref, standard_id). Logs the
    transition iff the headline actually changes."""
    cur.execute(
        """
        SELECT status
          FROM document_findings
         WHERE tenant_id     = %s::uuid
           AND control_ref   = %s
           AND standard_id   = %s
           AND review_status = 'approved'
           AND is_active     = TRUE
        """,
        (tenant_id, control_ref, standard_id),
    )
    statuses = [r[0] for r in cur.fetchall()]
    if not statuses:
        return {"control_ref": control_ref, "standard_id": standard_id,
                "finding": None, "prior_finding": None,
                "no_approved_remaining": True}

    promoted = [_DF_STATUS_TO_FINDING.get(s, "Not assessed") for s in statuses]
    headline = max(promoted, key=lambda f: _FINDING_PRIORITY.get(f, -1))

    cur.execute(
        """
        SELECT id, finding
          FROM posture_controls
         WHERE tenant_id   = %s::uuid
           AND control_ref = %s
           AND standard_id = %s
           AND is_active   = TRUE
         LIMIT 1
        """,
        (tenant_id, control_ref, standard_id),
    )
    pc = cur.fetchone()
    if not pc:
        return {"control_ref": control_ref, "standard_id": standard_id,
                "finding": headline, "prior_finding": None,
                "no_posture_row": True}
    posture_id, prior_finding = pc

    # Stage-1 contract per [[posture-engine-alignment-plan-2026-05-22]]
    # Phase D: confirm the *evidence*, not the posture. See sibling site in
    # approve_findings_for_control above. headline + prior_finding are still
    # returned to the caller so the chat surface can describe what was
    # approved without claiming a posture change.
    cur.execute(
        """
        UPDATE posture_controls
           SET confirmation_status = 'document_confirmed',
               confirmed_by        = %s::uuid,
               confirmed_at        = NOW(),
               source              = 'document'
         WHERE id = %s
        """,
        (_uuid_or_null(reviewed_by), posture_id),
    )

    return {"control_ref": control_ref, "standard_id": standard_id,
            "finding": headline, "prior_finding": prior_finding}


def reject_findings_by_ids(
    pg_conn,
    tenant_id:    str,
    finding_ids:  list[str],
    rationale:    str,
    reviewed_by:  str = "chat_user",
) -> dict:
    """Per-finding-id variant of [[reject_findings_for_control]]. Marks the
    named findings rejected + is_active=false. Posture is not touched —
    rejection is an audit-preserving alternative to silent deletion."""
    if not rationale or not rationale.strip():
        return {"ok": False, "reason": "no_rationale"}
    if not finding_ids:
        return {"ok": False, "reason": "no_pending"}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                UPDATE document_findings
                   SET review_status    = 'rejected',
                       rejection_reason = %s,
                       reviewed_by      = %s::uuid,
                       reviewed_at      = NOW(),
                       is_active        = FALSE
                 WHERE tenant_id     = %s::uuid
                   AND id            = ANY(%s::uuid[])
                   AND review_status = 'pending'
                   AND is_active     = TRUE
                """,
                (rationale[:500], _uuid_or_null(reviewed_by),
                 tenant_id, finding_ids),
            )
            n = cur.rowcount
            if n == 0:
                return {"ok": False, "reason": "no_pending"}
        pg_conn.commit()
        return {"ok": True, "rejected": n}
    except Exception as e:
        logger.warning("stage1_review_chat.reject_by_ids: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def _uuid_or_null(s: str) -> Optional[str]:
    """Convert a free-text reviewer string to a UUID where possible. The
    chat surface uses 'chat_user' as a placeholder until session-bound user
    IDs are wired through. Returning None lets the column stay NULL rather
    than poisoning the row with an invalid uuid."""
    if not s:
        return None
    try:
        return str(uuid.UUID(s))
    except (ValueError, AttributeError):
        return None


# ── Answer formatting ─────────────────────────────────────────────────────────

def render_stage1_answer(
    result: dict,
    intent: Stage1Intent,
    listing: Optional[list[dict]] = None,
) -> str:
    """Deterministic answer for the Stage-1 surface. The acknowledge
    pattern: no LLM polish — the user's review decision needs to be
    unambiguously confirmed."""
    if intent.action == "list_queue":
        if not listing:
            return (
                "No pending findings to review. New uploads land in the "
                "review queue automatically; this list is empty either "
                "because nothing has been extracted yet or everything has "
                "already been approved or rejected."
            )
        lines = [f"Pending review ({len(listing)} control(s)):"]
        for r in listing:
            lines.append(
                f"  • {r['control_ref']} ({r['standard_id']}): "
                f"{r['pending_count']} finding(s) — approve with "
                f"\"approve findings for {r['control_ref']}\""
            )
        return "\n".join(lines)

    if intent.action == "list_one":
        ctrl = intent.control_ref
        if not listing:
            return (
                f"No pending findings for {ctrl}. They've either been "
                f"approved, rejected, or no extraction has run yet."
            )
        lines = [f"Pending findings for {ctrl} ({len(listing)}):"]
        for r in listing:
            excerpt = (r["excerpt"] or "")[:140].strip()
            tail = "…" if r["excerpt"] and len(r["excerpt"]) > 140 else ""
            lines.append(
                f"  • [{r['status']}/{r['confidence']}] {excerpt}{tail}"
            )
        lines.append(
            f"\nApprove all with \"approve findings for {ctrl}\" or "
            f"\"reject findings for {ctrl} because <reason>\"."
        )
        return "\n".join(lines)

    # approve / reject — single-control writes
    ctrl = intent.control_ref
    if intent.action == "approve":
        if result.get("ok"):
            n = result["approved"]
            f = result.get("finding")
            # Stage-1 no longer mutates posture_controls.finding — it only
            # confirms the evidence. The headline below describes what the
            # *evidence* suggests; the engine + Stage-2 are responsible for
            # any posture change.
            if f:
                tail = (
                    f' The extracted evidence indicates "{f}" — the engine '
                    f'will propose a posture update for your Stage-2 review.'
                )
            else:
                tail = (
                    " The engine will propose a posture update for your "
                    "Stage-2 review."
                )
            return (
                f"Approved {n} extracted finding(s) for {ctrl}. "
                f"{ctrl} is now document_confirmed.{tail}"
            )
        reason = result.get("reason", "unknown")
        if reason == "no_pending":
            return (
                f"No pending findings for {ctrl}. Either the extraction "
                f"hasn't run yet, or these findings have already been "
                f"approved or rejected."
            )
        if reason == "db_error":
            return (
                f"Couldn't approve findings for {ctrl} due to a database "
                f"error. Please try again."
            )
        return f"Couldn't approve findings for {ctrl} (reason: {reason})."

    if intent.action == "reject":
        if result.get("ok"):
            n = result["rejected"]
            return (
                f"Rejected {n} extracted finding(s) for {ctrl}. The "
                f"rejection reason is recorded against each finding. "
                f"{ctrl} posture is unchanged — rejection preserves audit "
                f"trail but does not retract any prior approved finding."
            )
        reason = result.get("reason", "unknown")
        if reason == "no_rationale":
            return (
                f"To reject findings for {ctrl}, please include a reason: "
                f"\"reject findings for {ctrl} because <reason>\". "
                f"Rejections without a reason aren't auditable."
            )
        if reason == "no_pending":
            return (
                f"No pending findings to reject for {ctrl}."
            )
        if reason == "db_error":
            return (
                f"Couldn't reject findings for {ctrl} due to a database "
                f"error. Please try again."
            )
        return f"Couldn't reject findings for {ctrl} (reason: {reason})."

    return f"Stage-1 review surface — unrecognised action: {intent.action}"
