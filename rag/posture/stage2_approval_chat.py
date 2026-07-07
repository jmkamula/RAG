"""ArionComply — chat surface for Stage-2 approval of engine verdicts.

Recognises queries like:
  "approve engine verdict for A.5.1"
  "approve engine proposal for A.5.1"
  "reject engine verdict for A.5.1 because we accept the policy-only signal"
  "show pending engine proposals"
  "what engine verdicts need review?"

Implements the second HITL gate from [[hitl-two-stage-approval-design]]:
the fulfilment engine writes verdicts as pending posture_assertions
(source='engine', status='pending'); this surface promotes a proposed
verdict to live finding once the user approves. Approval flips
posture_controls.finding to the proposed value, sets confirmation_status
='engine_confirmed', supersedes the pending engine PA row, and logs the
transition with change_kind='engine'.

Per [[human_in_the_loop_positioning]]: the platform proposes, the client
decides. Rejection preserves the audit trail (status='rejected'); the live
finding is not touched.

Distinct from [[stage1_review_chat]]: Stage-1 batch-approves extraction
findings (document_findings.review_status); Stage-2 approves engine
verdicts (posture_controls.engine_proposal_status). They operate on
different rows and different vocabularies — the object words
("engine verdict|proposal" vs "findings|extractions") disambiguate.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ── Slot grammar ──────────────────────────────────────────────────────────────

_APPROVE_RE = re.compile(
    r"\b(?:approve|accept|confirm)\b",
    re.IGNORECASE,
)
_REJECT_RE = re.compile(
    r"\b(?:reject|deny)\b",
    re.IGNORECASE,
)
# List/queue verbs. The Stage-2 object words ("engine verdict|proposal")
# must appear in the list query as well so we don't collide with Stage-1's
# "what findings need review?" surface.
_LIST_RE = re.compile(
    r"\b(?:"
    r"pending\s+engine\s+(?:verdicts?|proposals?)|"
    r"engine\s+(?:verdicts?|proposals?)\s+(?:need|needing|awaiting)\s+(?:review|approval)|"
    r"engine\s+review\s+(?:queue|verdicts?|proposals?)|"
    r"what\s+engine\s+(?:verdicts?|proposals?)\s+(?:need|needs|require)"
    r")\b",
    re.IGNORECASE,
)
# Object word: "engine verdict" / "engine proposal" — required for
# approve/reject so we don't collide with Stage-1's "findings" / "extractions"
# vocabulary, and so we don't fire on "approve the policy" / "accept A.5.1
# as Comply".
_OBJECT_RE = re.compile(
    r"\bengine\s+(?:verdicts?|proposals?)\b",
    re.IGNORECASE,
)
# Control reference — same shape as [[stage1_review_chat]] and
# [[acknowledge_chat]].
_CONTROL_RE = re.compile(
    r"\b("
    r"A\.\d+(?:\.\d+)*"
    r"|Art\.\d+(?:\.\d+[a-z]?)*"
    r"|\d+\.\d+(?:\.\d+)?"   # ISMS clauses 4.1 … 10.2 — \d+ so '10.x' matches
    r")\b",
)
_RATIONALE_RE = re.compile(
    r"(?:\bbecause\b|\bsince\b|\breason:?\b|—|-)\s*(?P<reason>.+?)\s*\.?\s*$",
    re.IGNORECASE,
)


@dataclass
class Stage2Intent:
    action:      str                # 'approve' | 'reject' | 'list_one' | 'list_queue'
    control_ref: Optional[str]
    rationale:   str
    raw_query:   str


def parse_stage2_intent(query: str) -> Optional[Stage2Intent]:
    """Returns a Stage2Intent if the query is recognisably a Stage-2 engine
    verdict approval / rejection / review request, else None. Conservative
    grammar: approve/reject require both a verb AND the 'engine verdict' /
    'engine proposal' object words AND a control ref."""
    if not query:
        return None

    is_approve = bool(_APPROVE_RE.search(query))
    is_reject  = bool(_REJECT_RE.search(query))
    is_list    = bool(_LIST_RE.search(query))

    if not (is_approve or is_reject or is_list):
        return None

    ctrl_m = _CONTROL_RE.search(query)
    ctrl   = ctrl_m.group(1) if ctrl_m else None

    if is_approve or is_reject:
        if not _OBJECT_RE.search(query):
            return None
        if not ctrl:
            return None
        rationale = ""
        if is_reject:
            r_m = _RATIONALE_RE.search(query)
            if r_m:
                rationale = (r_m.group("reason") or "").strip().rstrip(".")
        return Stage2Intent(
            action      = "approve" if is_approve else "reject",
            control_ref = ctrl,
            rationale   = rationale,
            raw_query   = query,
        )

    return Stage2Intent(
        action      = "list_one" if ctrl else "list_queue",
        control_ref = ctrl,
        rationale   = "",
        raw_query   = query,
    )


# ── Read paths ────────────────────────────────────────────────────────────────

def list_pending_proposals(pg_conn, tenant_id: str) -> list[dict]:
    """Return all controls with a pending engine assertion + lifecycle still
    'proposed', sorted by standard_id, control_ref. Each row carries the
    proposed finding, the live finding it would overwrite, and the snapshotted
    reason.

    Phase 1b: verdict (finding + reason + proposed_at) sourced from
    posture_assertions; lifecycle filter (engine_proposal_status='proposed')
    still on posture_controls. Phase 1c made approve/reject explicitly
    supersede the pending PA row, so the JOIN no longer relies on lifecycle
    drift to filter out completed proposals — but the pc.engine_proposal_
    status check stays as a belt-and-suspenders guard."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            """
            SELECT pc.standard_id, pc.control_ref, pc.finding,
                   pa.finding, pa.set_at::text,
                   pa.gap_description
              FROM posture_assertions pa
              JOIN posture_controls pc
                ON pa.tenant_id   = pc.tenant_id
               AND pa.control_ref = pc.control_ref
               AND pa.standard_id = pc.standard_id
             WHERE pa.tenant_id              = %s
               AND pa.source                 = 'engine'
               AND pa.status                 = 'pending'
               AND pc.is_active              = TRUE
               AND pc.engine_proposal_status = 'proposed'
             ORDER BY pc.standard_id, pc.control_ref
            """,
            (tenant_id,),
        )
        return [
            {
                "standard_id":      r[0],
                "control_ref":      r[1],
                "live_finding":     r[2],
                "proposed_finding": r[3],
                "proposed_at":      r[4],
                "reason":           r[5] or "",
            }
            for r in cur.fetchall()
        ]


def get_proposal_for_control(
    pg_conn, tenant_id: str, control_ref: str,
) -> Optional[dict]:
    """Read the engine proposal state for one control. Returns None if no
    posture_controls row exists for the (tenant, control_ref).

    Phase 1c: posture_assertions is now the sole source of truth for the
    engine verdict. A correlated subquery picks the latest engine PA row
    regardless of status — pending wins over active wins over superseded —
    so the function works for 'proposed' (pending row), 'approved' (active
    row created by the reverse-sync trigger on the approve UPDATE), and
    'rejected' (superseded row whose metadata holds the rationale).
    """
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            """
            SELECT pc.id::text, pc.standard_id, pc.finding,
                   pc.engine_proposal_status,
                   pa.finding,
                   pa.set_at::text,
                   pa.gap_description,
                   pa.metadata
              FROM posture_controls pc
              LEFT JOIN LATERAL (
                  SELECT finding, set_at, gap_description, metadata
                    FROM posture_assertions
                   WHERE tenant_id   = pc.tenant_id
                     AND control_ref = pc.control_ref
                     AND standard_id = pc.standard_id
                     AND source      = 'engine'
                   ORDER BY (status = 'pending')  DESC,
                            (status = 'active')   DESC,
                            set_at                DESC
                   LIMIT 1
              ) pa ON TRUE
             WHERE pc.tenant_id   = %s
               AND pc.control_ref = %s
               AND pc.is_active   = TRUE
             LIMIT 1
            """,
            (tenant_id, control_ref),
        )
        row = cur.fetchone()
        if row is None:
            return None
        (posture_id, standard_id, live_finding,
         status,
         proposed_finding, proposed_at, reason, metadata) = row
        # On rejected lifecycle the historical pending row carries the
        # rationale in metadata; surface it inline for display continuity
        # with the pre-1c behaviour where it was appended to the reason text.
        if status == "rejected" and metadata:
            rationale = (metadata or {}).get("rejection_rationale")
            if rationale:
                reason = (
                    f"{reason} | rejected: {rationale[:300]}"
                    if reason else f"rejected: {rationale[:300]}"
                )
        return {
            "posture_id":       posture_id,
            "standard_id":      standard_id,
            "live_finding":     live_finding,
            "proposed_finding": proposed_finding,
            "status":           status,
            "proposed_at":      proposed_at,
            "reason":           reason or "",
        }


# ── Write paths ───────────────────────────────────────────────────────────────

def approve_engine_proposal(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    reviewed_by:  str = "chat_user",
    standard_id:  Optional[str] = None,
) -> dict:
    """Promote the engine proposal to live finding for one control.

    Effects (single transaction):
      - posture_controls.finding              ← pending PA finding
      - posture_controls.engine_proposal_status='approved'
      - posture_controls.engine_approved_by / engine_approved_at
      - posture_controls.confirmation_status  ='engine_confirmed'
      - pending engine PA row → status='superseded' with decision metadata
      - posture_status_log row with change_kind='engine'

    Returns:
      {'ok': True,  'control_ref': X, 'standard_id': S,
       'prior_finding': F0, 'new_finding': F1, 'reason': R}
      {'ok': False, 'reason': 'no_proposal' | 'already_approved' |
                             'no_posture_row' | 'db_error', ...}

    Idempotency: re-running on a row whose status is already 'approved'
    returns reason='already_approved' rather than re-writing. A subsequent
    engine sweep that produces an UNCHANGED verdict is also a no-op (see
    posture_loader._persist_engine_proposals). A CHANGED verdict resets the
    proposal back to 'proposed', and this function must be called again to
    re-approve.
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

            # Defence in depth: prefer the PC row that actually has a
            # pending engine proposal when the caller didn't supply
            # standard_id explicitly. Prior to this ordering the query
            # would arbitrarily LIMIT 1 across duplicate (control_ref,
            # standard_id) rows — an issue when the pre-d60734a bug
            # left orphan 27001-tagged copies of 27701 refs. See the
            # commit for the upstream fix; this is the read-side guard.
            std_filter = "AND pc.standard_id = %s" if standard_id else ""
            params: list = [tenant_id, control_ref]
            if standard_id:
                params.append(standard_id)
            cur.execute(
                f"""
                SELECT pc.id, pc.standard_id, pc.finding,
                       pa.finding, pc.engine_proposal_status,
                       pa.gap_description
                  FROM posture_controls pc
                  LEFT JOIN posture_assertions pa
                    ON pa.tenant_id   = pc.tenant_id
                   AND pa.control_ref = pc.control_ref
                   AND pa.standard_id = pc.standard_id
                   AND pa.source      = 'engine'
                   AND pa.status      = 'pending'
                 WHERE pc.tenant_id   = %s
                   AND pc.control_ref = %s
                   {std_filter}
                   AND pc.is_active   = TRUE
                 ORDER BY (pa.finding IS NOT NULL
                          AND pc.engine_proposal_status = 'proposed') DESC,
                          pc.last_updated DESC
                 LIMIT 1
                """,
                params,
            )
            row = cur.fetchone()
            if row is None:
                return {"ok": False, "reason": "no_posture_row"}
            (posture_id, standard_id, live_finding,
             proposed_finding, status, reason_snap) = row

            if status == "approved":
                return {
                    "ok": False, "reason": "already_approved",
                    "control_ref": control_ref,
                    "standard_id": standard_id,
                    "live_finding": live_finding,
                }
            if not proposed_finding or status != "proposed":
                return {
                    "ok": False, "reason": "no_proposal",
                    "control_ref": control_ref,
                    "standard_id": standard_id,
                }

            cur.execute(
                """
                UPDATE posture_controls
                   SET finding                = %s,
                       engine_proposal_status = 'approved',
                       engine_approved_by     = %s::uuid,
                       engine_approved_at     = NOW(),
                       confirmation_status    = 'engine_confirmed',
                       source                 = 'engine'
                 WHERE id = %s
                """,
                (proposed_finding, _uuid_or_null(reviewed_by), posture_id),
            )

            # Phase 1c: explicitly supersede the pending engine PA row. The
            # PC.finding UPDATE above fires the reverse-sync trigger which
            # supersedes the prior ACTIVE engine PA row (if any) and inserts
            # a new active row with the approved verdict — but the trigger
            # never touches pending rows. Leaving the pending row dangling
            # would cause the next engine sweep to see "no diff" (its skip-
            # no-op check compares against the pending row) and silently no-
            # op, hiding any later engine re-evaluation.
            from rag.posture.assertions import supersede_pending_proposal
            supersede_pending_proposal(
                cur,
                tenant_id   = tenant_id,
                control_ref = control_ref,
                standard_id = standard_id,
                source      = "engine",
                decided_by  = reviewed_by or "chat_user",
                decision    = "approved",
            )

            cur.execute(
                """
                INSERT INTO posture_status_log (
                    tenant_id, posture_id, control_ref, standard_id,
                    status_before, status_after,
                    source, evidence_citation,
                    change_kind
                ) VALUES (
                    %s::uuid, %s::uuid, %s, %s,
                    %s, %s,
                    'engine', %s,
                    'engine'
                )
                """,
                (
                    tenant_id, posture_id, control_ref, standard_id,
                    live_finding, proposed_finding,
                    f"Stage-2 approval: {reason_snap or 'engine verdict'}",
                ),
            )

        pg_conn.commit()
        return {
            "ok":            True,
            "control_ref":   control_ref,
            "standard_id":   standard_id,
            "prior_finding": live_finding,
            "new_finding":   proposed_finding,
            "reason":        reason_snap or "",
        }
    except Exception as e:
        logger.warning("stage2_approval_chat.approve: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def reject_engine_proposal(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    rationale:    str,
    reviewed_by:  str = "chat_user",
    standard_id:  Optional[str] = None,
) -> dict:
    """Reject the engine proposal. Sets engine_proposal_status='rejected'
    and stamps engine_approved_by / engine_approved_at (the field doubles as
    "decided by / at" — fkey + index already exist). The live finding is
    NOT touched: rejection preserves the audit trail without applying the
    engine verdict.

    Phase 1c: the rationale is stamped on the pending PA row's metadata
    (decision='rejected', rejection_rationale=...) as it transitions to
    'superseded'. PC.engine_proposal_reason was dropped in schema_v30.

    Returns:
      {'ok': True,  'control_ref': X, 'proposed_finding': F}
      {'ok': False, 'reason': 'no_proposal' | 'no_rationale' | 'db_error'}
    """
    if not rationale or not rationale.strip():
        return {"ok": False, "reason": "no_rationale"}

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))

            # Defence-in-depth ordering — see approve_engine_proposal.
            std_filter = "AND pc.standard_id = %s" if standard_id else ""
            params: list = [tenant_id, control_ref]
            if standard_id:
                params.append(standard_id)
            cur.execute(
                f"""
                SELECT pc.id, pc.standard_id,
                       pa.finding, pc.engine_proposal_status
                  FROM posture_controls pc
                  LEFT JOIN posture_assertions pa
                    ON pa.tenant_id   = pc.tenant_id
                   AND pa.control_ref = pc.control_ref
                   AND pa.standard_id = pc.standard_id
                   AND pa.source      = 'engine'
                   AND pa.status      = 'pending'
                 WHERE pc.tenant_id   = %s
                   AND pc.control_ref = %s
                   {std_filter}
                   AND pc.is_active   = TRUE
                 ORDER BY (pa.finding IS NOT NULL
                          AND pc.engine_proposal_status = 'proposed') DESC,
                          pc.last_updated DESC
                 LIMIT 1
                """,
                params,
            )
            row = cur.fetchone()
            if row is None:
                return {"ok": False, "reason": "no_proposal"}
            posture_id, standard_id, proposed_finding, status = row
            if not proposed_finding or status != "proposed":
                return {
                    "ok": False, "reason": "no_proposal",
                    "control_ref": control_ref,
                    "standard_id": standard_id,
                }

            cur.execute(
                """
                UPDATE posture_controls
                   SET engine_proposal_status = 'rejected',
                       engine_approved_by     = %s::uuid,
                       engine_approved_at     = NOW()
                 WHERE id = %s
                """,
                (_uuid_or_null(reviewed_by), posture_id),
            )

            from rag.posture.assertions import supersede_pending_proposal
            supersede_pending_proposal(
                cur,
                tenant_id   = tenant_id,
                control_ref = control_ref,
                standard_id = standard_id,
                source      = "engine",
                decided_by  = reviewed_by or "chat_user",
                decision    = "rejected",
                rationale   = rationale[:300],
            )

        pg_conn.commit()
        return {
            "ok":               True,
            "control_ref":      control_ref,
            "standard_id":      standard_id,
            "proposed_finding": proposed_finding,
        }
    except Exception as e:
        logger.warning("stage2_approval_chat.reject: db error: %s", e)
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return {"ok": False, "reason": "db_error", "error": str(e)}


def _uuid_or_null(s: str) -> Optional[str]:
    """Same chat_user placeholder helper as [[stage1_review_chat]]."""
    if not s:
        return None
    try:
        return str(uuid.UUID(s))
    except (ValueError, AttributeError):
        return None


# ── Answer formatting ─────────────────────────────────────────────────────────

def render_stage2_answer(
    result: dict,
    intent: Stage2Intent,
    listing: Optional[list[dict]] = None,
    proposal: Optional[dict] = None,
) -> str:
    """Deterministic Stage-2 answer. Mirrors the [[stage1_review_chat]]
    pattern: no LLM polish."""
    if intent.action == "list_queue":
        if not listing:
            return (
                "No engine verdicts are pending review. The engine writes a "
                "proposal whenever the multi-leaf fulfilment evaluation "
                "differs from the live posture finding; this list is empty "
                "either because every proposal has been approved/rejected "
                "or because no curated multi-leaf spec disagrees with the "
                "current finding."
            )
        lines = [f"Engine verdicts pending review ({len(listing)}):"]
        for r in listing:
            lines.append(
                f"  • {r['control_ref']} ({r['standard_id']}): "
                f"engine proposes {r['proposed_finding']!r}, "
                f"live is {r['live_finding']!r} — "
                f"approve with \"approve engine verdict for {r['control_ref']}\""
            )
        if listing:
            sample = listing[0]
            reason = sample.get("reason") or ""
            if reason:
                lines.append("")
                lines.append(
                    f"Reason for {sample['control_ref']}: {reason[:160]}"
                )
        return "\n".join(lines)

    if intent.action == "list_one":
        ctrl = intent.control_ref
        if not proposal:
            return (
                f"No engine proposal on file for {ctrl}. Either the control "
                f"has no curated multi-leaf FulfilmentSpec, or the engine "
                f"hasn't run yet for this tenant."
            )
        status = proposal["status"]
        if status == "none":
            # Engine concurs with live (no Stage-2 decision pending). When an
            # 'active' engine PA exists (NC/OFI concurrence), surface its
            # structured reason so partial-evidence progress is still visible
            # to the reviewer. See [[engine_agreement_suppression]].
            if proposal.get("proposed_finding") and proposal.get("reason"):
                return (
                    f"{ctrl}: engine concurs with live at "
                    f"{proposal['live_finding']!r}.\n"
                    f"Reason: {proposal['reason']}"
                )
            return (
                f"{ctrl}: engine has no current proposal (status: "
                f"{status!r}). Posture stays at "
                f"{proposal['live_finding']!r}."
            )
        if not proposal.get("proposed_finding"):
            return (
                f"{ctrl}: engine has no current proposal (status: "
                f"{status!r}). Posture stays at "
                f"{proposal['live_finding']!r}."
            )
        if status == "approved":
            return (
                f"{ctrl}: engine verdict {proposal['proposed_finding']!r} "
                f"already approved. Live finding: "
                f"{proposal['live_finding']!r}."
            )
        if status == "rejected":
            return (
                f"{ctrl}: engine verdict {proposal['proposed_finding']!r} "
                f"was rejected. Live finding stays "
                f"{proposal['live_finding']!r}.\n"
                f"Reason: {proposal['reason']}"
            )
        return (
            f"{ctrl}: engine proposes {proposal['proposed_finding']!r}, "
            f"live finding is {proposal['live_finding']!r}.\n"
            f"Reason: {proposal['reason']}\n"
            f"Approve with \"approve engine verdict for {ctrl}\" or "
            f"\"reject engine verdict for {ctrl} because <reason>\"."
        )

    ctrl = intent.control_ref
    if intent.action == "approve":
        if result.get("ok"):
            return (
                f"Approved engine verdict for {ctrl}: "
                f"{result['prior_finding']!r} → {result['new_finding']!r}. "
                f"{ctrl} is now engine_confirmed."
            )
        reason = result.get("reason", "unknown")
        if reason == "already_approved":
            return (
                f"Engine verdict for {ctrl} is already approved. Live "
                f"finding stays {result.get('live_finding', '?')!r}."
            )
        if reason == "no_proposal":
            return (
                f"No engine proposal pending for {ctrl}. Either the engine "
                f"hasn't produced a verdict yet, or the proposal was "
                f"already approved or rejected."
            )
        if reason == "no_posture_row":
            return (
                f"No posture row for {ctrl}. Approve the extraction findings "
                f"first to create one."
            )
        if reason == "db_error":
            return (
                f"Couldn't approve engine verdict for {ctrl} due to a "
                f"database error. Please try again."
            )
        return f"Couldn't approve engine verdict for {ctrl} (reason: {reason})."

    if intent.action == "reject":
        if result.get("ok"):
            return (
                f"Rejected engine verdict for {ctrl} (proposed "
                f"{result['proposed_finding']!r}). The live finding is "
                f"unchanged; the rejection reason is recorded."
            )
        reason = result.get("reason", "unknown")
        if reason == "no_rationale":
            return (
                f"To reject the engine verdict for {ctrl}, please include "
                f"a reason: \"reject engine verdict for {ctrl} because "
                f"<reason>\"."
            )
        if reason == "no_proposal":
            return f"No engine proposal pending for {ctrl}."
        if reason == "db_error":
            return (
                f"Couldn't reject engine verdict for {ctrl} due to a "
                f"database error. Please try again."
            )
        return f"Couldn't reject engine verdict for {ctrl} (reason: {reason})."

    return f"Stage-2 approval surface — unrecognised action: {intent.action}"
