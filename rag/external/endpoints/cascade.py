"""
Cascade endpoints — /api/external/v1/cascade/timeline + /cascade/implications/{id}.

Ship 4'.f — external systems can poll the tenant's cascade
timeline (implications fired + expected follow-ups) as a JSON
feed. Useful for SOAR playbooks, audit dashboards, and any
external system that needs to react to compliance events.

Design decisions:

  * The internal `/api/v1/tenant/cascade-timeline` unions 4
    tables (verifications, implications, followups,
    suppressions). This external endpoint returns only the 2
    load-bearing kinds: implications + followups. Verifications
    (with their structured_events blob) are internal telemetry;
    suppressions are edge-case.
  * `?kind[]=implication&kind=followup` filter for future
    extension when we add more kinds.
  * `?control_ref=` filter for scoping to one control.
  * `?since_days=` rolling window (default 30, max 365).
  * `?limit / ?offset` for pagination.

Auth scope: `external:cascade:read`.
"""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope

logger = logging.getLogger(__name__)

router = APIRouter()


_ALLOWED_KINDS = ("implication", "followup")


# ── Response models ───────────────────────────────────────────────────

class CascadeEvent(BaseModel):
    kind:               str            = Field(..., description="`implication` or `followup`.")
    id:                 str
    ts:                 str            = Field(..., description="Event timestamp (fired_at) — ISO8601.")
    event_type:         str            = Field(..., description="Source event that triggered this (e.g. `policy_revised`, `nc_finding`) — keyable slug.")
    event_type_display: Optional[str]  = Field(None, description="Ship 7'.c — human display of `event_type` (e.g. `policy revised`).")

    # Implication-specific
    expected_action:    Optional[str]  = None
    expected_action_display: Optional[str] = Field(None, description="Ship 7'.c — human display of `expected_action`.")
    control_ref:        Optional[str]  = None
    standard_id:        Optional[str]  = None
    standard_display:   Optional[str]  = Field(None, description="Ship 7'.c — human display of `standard_id` (e.g. `ISO 27001:2022`).")
    cascade_path:       Optional[list] = None
    cascade_depth:      Optional[int]  = None
    status:             Optional[str]  = None
    resolved_at:        Optional[str]  = None
    resolved_evidence_kind: Optional[str] = None
    dismissed_reason:   Optional[str]  = None
    rationale:          Optional[str]  = None
    due_date:           Optional[str]  = None
    clock_anchor:       Optional[str]  = None
    scope_kind:         Optional[str]  = None

    # Followup-specific
    expected_event_type: Optional[str] = None
    expected_event_type_display: Optional[str] = Field(None, description="Ship 7'.c — human display of `expected_event_type`.")
    window_days:         Optional[int] = None
    expires_at:          Optional[str] = None


class CascadeTimelineResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    since_days:              int
    events:                  list[CascadeEvent]
    summary:                 dict = Field(..., description="Counts: `{implication, followup, total, overdue}`.")
    total_before_pagination: int


class ImplicationDetail(BaseModel):
    id:                     str
    tenant_id:              str
    fired_at:               str
    source_event_type:      str
    source_event_type_display:      Optional[str] = None    # Ship 7'.c
    source_verification_id: Optional[str] = None
    expected_action:        str
    expected_action_display:        Optional[str] = None    # Ship 7'.c
    target_control_ref:     str
    target_standard_id:     str
    target_standard_display:        Optional[str] = None    # Ship 7'.c
    target_requirement_id:  str
    cascade_path:           list
    cascade_depth:          int
    status:                 str
    resolved_at:            Optional[str] = None
    resolved_by:            Optional[str] = None
    resolved_evidence_kind: Optional[str] = None
    resolved_evidence_id:   Optional[str] = None
    dismissed_reason:       Optional[str] = None
    rationale:              Optional[str] = None
    deadline_string:        Optional[str] = None
    due_date:               Optional[str] = None
    scope_kind:             Optional[str] = None
    clock_anchor:           str


def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


# ── GET /cascade/timeline ─────────────────────────────────────────────

@router.get("/cascade/timeline",
            response_model = CascadeTimelineResponse,
            summary        = "Cascade timeline (implications + followups)")
async def cascade_timeline(
    request:       Request,
    key            = Depends(external_key_with_scope("external:cascade:read")),
    kind:          Optional[list[str]] = Query(None, description="Repeatable — filter to one or more kinds. Allowed: `implication`, `followup`."),
    control_ref:   Optional[str]       = Query(None, description="Filter implications to a single target control."),
    since_days:    int                 = Query(30, ge=1, le=365, description="Rolling window in days."),
    limit:         int                 = Query(200, ge=1, le=1000),
    offset:        int                 = Query(0,   ge=0),
):
    """Chronological feed of cascade events: implications fired and
    expected follow-ups. Use `?kind=implication` for just the
    implication stream, or `?kind=followup` for just the followup
    stream. Default is both, oldest first."""
    if kind:
        bad = [k for k in kind if k not in _ALLOWED_KINDS]
        if bad:
            raise HTTPException(
                status_code = 400,
                detail      = f"Unknown cascade kind(s): {bad}. Allowed: {list(_ALLOWED_KINDS)}",
            )
    include_implications = (not kind) or ("implication" in kind)
    include_followups    = (not kind) or ("followup"    in kind)

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    events: list[CascadeEvent] = []
    imp_count = fu_count = overdue_count = 0
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))

            if include_implications:
                impl_params: list = [key.tenant_id, since_days]
                impl_where_extra = ""
                if control_ref:
                    impl_where_extra = " AND target_control_ref = %s"
                    impl_params.append(control_ref)
                cur.execute(
                    f"""
                    SELECT id::text, fired_at, source_event_type, expected_action,
                           target_control_ref, target_standard_id, cascade_path,
                           cascade_depth, status, resolved_at,
                           resolved_evidence_kind, dismissed_reason,
                           rationale, due_date, clock_anchor, scope_kind
                      FROM triggered_implication
                     WHERE tenant_id = %s::uuid
                       AND fired_at >= now() - make_interval(days => %s)
                       {impl_where_extra}
                     ORDER BY fired_at DESC
                    """,
                    tuple(impl_params),
                )
                impls = cur.fetchall()
                imp_count = len(impls)
                # Ship 7'.c — humanise slugs + scrub rationale through
                # the output gateway. Non-breaking: raw slug fields
                # (event_type, expected_action, standard_id) stay
                # verbatim; *_display companions carry human forms.
                from rag.output import (
                    format_standard_id_exact as _fmt_std,
                    humanize as _humanize,
                )
                for r in impls:
                    is_overdue = (r[13] is not None
                                  and r[13] < _dt.datetime.now(_dt.timezone.utc)
                                  and r[8] == "pending")
                    if is_overdue:
                        overdue_count += 1
                    _event_type      = r[2] or ""
                    _expected_action = r[3] or ""
                    _rationale       = (r[12] or "")[:400]
                    events.append(CascadeEvent(
                        kind                    = "implication",
                        id                      = r[0],
                        ts                      = r[1].isoformat() if r[1] else "",
                        event_type              = _event_type,
                        event_type_display      = _humanize(_event_type, surface="cascade_rationale") if _event_type else None,
                        expected_action         = r[3],
                        expected_action_display = _humanize(_expected_action, surface="cascade_rationale") if _expected_action else None,
                        control_ref             = r[4],
                        standard_id             = r[5],
                        standard_display        = _fmt_std(r[5]) if r[5] else None,
                        cascade_path            = list(r[6]) if r[6] else [],
                        cascade_depth           = r[7],
                        status                  = r[8],
                        resolved_at             = r[9].isoformat() if r[9] else None,
                        resolved_evidence_kind  = r[10],
                        dismissed_reason        = r[11],
                        rationale               = _humanize(_rationale, surface="cascade_rationale") if _rationale else None,
                        due_date                = r[13].isoformat() if r[13] else None,
                        clock_anchor            = r[14],
                        scope_kind              = r[15],
                    ))

            if include_followups:
                cur.execute(
                    """
                    SELECT id::text, fired_at, source_event_type, expected_event_type,
                           window_days, expires_at, status, rationale
                      FROM expected_followup_event
                     WHERE tenant_id = %s::uuid
                       AND fired_at >= now() - make_interval(days => %s)
                     ORDER BY fired_at DESC
                    """,
                    (key.tenant_id, since_days),
                )
                fups = cur.fetchall()
                fu_count = len(fups)
                # Ship 7'.c — same gateway pass for follow-ups.
                from rag.output import humanize as _humanize
                for r in fups:
                    _event_type   = r[2] or ""
                    _expected_evt = r[3] or ""
                    _rationale    = (r[7] or "")[:400]
                    events.append(CascadeEvent(
                        kind                = "followup",
                        id                  = r[0],
                        ts                  = r[1].isoformat() if r[1] else "",
                        event_type          = _event_type,
                        event_type_display  = _humanize(_event_type, surface="cascade_rationale") if _event_type else None,
                        expected_event_type = r[3],
                        expected_event_type_display = _humanize(_expected_evt, surface="cascade_rationale") if _expected_evt else None,
                        window_days         = r[4],
                        expires_at          = r[5].isoformat() if r[5] else None,
                        status              = r[6],
                        rationale           = _humanize(_rationale, surface="cascade_rationale") if _rationale else None,
                    ))
    finally:
        pool.putconn(conn)

    # Sort DESC by ts, then paginate
    events.sort(key=lambda e: e.ts, reverse=True)
    total = len(events)
    page  = events[offset:offset + limit]

    return CascadeTimelineResponse(
        tenant_id               = key.tenant_id,
        generated_at            = _iso_now(),
        since_days              = since_days,
        events                  = page,
        summary                 = {
            "implication": imp_count,
            "followup":    fu_count,
            "total":       total,
            "overdue":     overdue_count,
        },
        total_before_pagination = total,
    )


# ── GET /cascade/implications/{id} ────────────────────────────────────

@router.get("/cascade/implications/{implication_id}",
            response_model = ImplicationDetail,
            summary        = "Single implication drill-in")
async def get_implication(
    implication_id: str,
    request:        Request,
    key             = Depends(external_key_with_scope("external:cascade:read")),
):
    """Fetch full detail on one triggered_implication row by id.
    Returns 404 if unknown for this tenant, 400 on malformed UUID.
    """
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            try:
                cur.execute(
                    """
                    SELECT id::text, tenant_id::text, fired_at,
                           source_event_type, source_verification_id::text,
                           expected_action,
                           target_control_ref, target_standard_id,
                           target_requirement_id,
                           cascade_path, cascade_depth,
                           status, resolved_at, resolved_by::text,
                           resolved_evidence_kind, resolved_evidence_id::text,
                           dismissed_reason, rationale, deadline_string,
                           due_date, scope_kind, clock_anchor
                      FROM triggered_implication
                     WHERE tenant_id = %s::uuid AND id = %s::uuid
                     LIMIT 1
                    """,
                    (key.tenant_id, implication_id),
                )
                row = cur.fetchone()
            except Exception as e:
                logger.info("get_implication bad id %r: %s", implication_id, e)
                raise HTTPException(
                    status_code = 400,
                    detail      = f"implication_id must be a UUID; got: {implication_id!r}",
                )
    finally:
        pool.putconn(conn)

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No implication {implication_id!r} for this tenant.",
        )

    (nid, tid, fired_at, src_evt, src_vid, expected_action,
     ctrl_ref, std_id, req_id, cascade_path, depth,
     status_, resolved_at, resolved_by,
     resolved_evidence_kind, resolved_evidence_id,
     dismissed_reason, rationale, deadline_string,
     due_date, scope_kind, clock_anchor) = row

    # Ship 7'.c — display companions + rationale scrub via gateway.
    from rag.output import (
        format_standard_id_exact as _fmt_std,
        humanize as _humanize,
    )
    return ImplicationDetail(
        id                        = nid,
        tenant_id                 = tid,
        fired_at                  = fired_at.isoformat() if fired_at else "",
        source_event_type         = src_evt or "",
        source_event_type_display = _humanize(src_evt or "", surface="cascade_rationale") or None,
        source_verification_id    = src_vid,
        expected_action           = expected_action or "",
        expected_action_display   = _humanize(expected_action or "", surface="cascade_rationale") or None,
        target_control_ref        = ctrl_ref or "",
        target_standard_id        = std_id or "",
        target_standard_display   = _fmt_std(std_id) if std_id else None,
        target_requirement_id     = req_id or "",
        cascade_path              = list(cascade_path) if cascade_path else [],
        cascade_depth             = int(depth) if depth is not None else 0,
        status                    = status_ or "",
        resolved_at               = resolved_at.isoformat() if resolved_at else None,
        resolved_by               = resolved_by,
        resolved_evidence_kind    = resolved_evidence_kind,
        resolved_evidence_id      = resolved_evidence_id,
        dismissed_reason          = dismissed_reason,
        rationale                 = _humanize(rationale, surface="cascade_rationale") if rationale else None,
        deadline_string           = deadline_string,
        due_date                  = due_date.isoformat() if due_date else None,
        scope_kind                = scope_kind,
        clock_anchor              = clock_anchor or "verified_at",
    )
