"""
Risk register read endpoints — /api/external/v1/risks[/{id}] +
/risks/summary.

Ship 14'.c (2026-07-22) — external SDK + partner integrations
pull the tenant's current risk state (assessment + treatment
plan) in one call, or drill in on a single risk.

Design notes:

  * Reuses `rag.risk.queries` — internal /api/v1/tenant/risks
    and external /api/external/v1/risks share the exact same
    query logic + response shapes, differing only in auth +
    rate-limit + scope check.

  * `?status=` repeatable filter (treatment_status in list).
  * `?limit=` + `?offset=` pagination — even 500-risk tenants
    are conceivable at mid-market scale.

  * Drill-in requires a UUID; 404 covers both non-existent +
    RLS-scoped-out (never leak cross-tenant existence).

  * `/summary` mirrors the dashboard tile — cheaper for partners
    than pulling the full list to compute counts client-side.

  * Framework role model discipline (Ship 14'.a addendum):
    every returned risk carries a `linked_controls` array where
    each control ref is expanded with `role` + `subject` +
    `standard_display`. Program / extension / obligation refs
    render first-class. Partners can filter client-side by role
    without needing separate endpoints per role.

Auth scope: `external:risks:read`.
"""
from __future__ import annotations

import datetime as _dt
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope
from rag.risk.queries import (
    RiskDetail,
    RiskRow,
    RiskSummary,
    fetch_risk_detail,
    fetch_risk_summary,
    fetch_risks,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Response models ───────────────────────────────────────────────────


class RisksListResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    risks:                   list[RiskRow]
    total_before_pagination: int
    limit:                   int
    offset:                  int
    summary:                 dict = Field(..., description="Counts across the filtered set: {open, overdue, above_threshold, unassigned, total}.")


class RiskSummaryResponse(RiskSummary):
    tenant_id:    str
    generated_at: str


# ── Endpoint helpers ──────────────────────────────────────────────────


def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


_ALLOWED_STATUS = ("open", "in_progress", "implemented", "accepted")


# ── GET /risks ────────────────────────────────────────────────────────


@router.get("/risks",
            response_model = RisksListResponse,
            summary        = "Bulk risk-register snapshot")
async def get_risks(
    request:       Request,
    key            = Depends(external_key_with_scope("external:risks:read")),
    status:        Optional[list[str]] = Query(None, description="Filter by treatment_status (repeatable). Values: open / in_progress / implemented / accepted."),
    limit:         int = Query(200, ge=1, le=1000, description="Max rows to return."),
    offset:        int = Query(0,   ge=0,          description="Rows to skip (pagination)."),
):
    """Bulk risk-register snapshot for the current tenant. Returns
    a flat list — external clients iterate directly without
    walking a nested tree.

    Each risk's `linked_controls` array carries the framework-
    role-model metadata (`role`, `subject`, `standard_display`)
    for every referenced control. Program / extension / obligation
    controls render first-class."""
    if status:
        bad = [s for s in status if s not in _ALLOWED_STATUS]
        if bad:
            raise HTTPException(
                status_code = 400,
                detail      = f"Unknown status filter value(s): {bad}. Allowed: {list(_ALLOWED_STATUS)}",
            )

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        from api_server import set_session
        set_session(conn, key.tenant_id)
        rows, total = fetch_risks(conn, limit=limit, offset=offset, status=status)
        summary = fetch_risk_summary(conn)
    finally:
        pool.putconn(conn)

    return RisksListResponse(
        tenant_id               = str(key.tenant_id),
        generated_at            = _iso_now(),
        risks                   = rows,
        total_before_pagination = total,
        limit                   = limit,
        offset                  = offset,
        summary                 = {
            "total":           summary.total,
            "open":            summary.open,
            "overdue":         summary.overdue,
            "above_threshold": summary.above_threshold,
            "unassigned":      summary.unassigned,
        },
    )


# ── GET /risks/summary ────────────────────────────────────────────────


@router.get("/risks/summary",
            response_model = RiskSummaryResponse,
            summary        = "Risk-register dashboard aggregate")
async def get_risks_summary(
    request: Request,
    key     = Depends(external_key_with_scope("external:risks:read")),
):
    """Dashboard-friendly aggregate — counts, per-option and
    per-status breakdowns, 5x5 heatmap, top-5 rows. Cheaper for
    partners than pulling the full list."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        from api_server import set_session
        set_session(conn, key.tenant_id)
        summary = fetch_risk_summary(conn)
    finally:
        pool.putconn(conn)

    body = summary.model_dump()
    body["tenant_id"]    = str(key.tenant_id)
    body["generated_at"] = _iso_now()
    return body


# ── GET /risks/{risk_id} ──────────────────────────────────────────────


@router.get("/risks/{risk_id}",
            response_model = RiskDetail,
            summary        = "Drill-in on a single risk")
async def get_risk_detail(
    risk_id: str,
    request: Request,
    key     = Depends(external_key_with_scope("external:risks:read")),
):
    """Drill-in view. 404 covers both non-existent and
    RLS-scoped-out — cross-tenant existence never leaks."""
    # Explicit UUID validation — 400 on malformed rather than 404
    # (matches the /notifications/{id} pattern).
    import re
    if not re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", risk_id):
        raise HTTPException(status_code=400, detail="Malformed UUID")

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        from api_server import set_session
        set_session(conn, key.tenant_id)
        detail = fetch_risk_detail(conn, risk_id)
    finally:
        pool.putconn(conn)

    if detail is None:
        raise HTTPException(status_code=404, detail=f"Risk not found: {risk_id}")
    return detail
