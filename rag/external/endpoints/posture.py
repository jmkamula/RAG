"""
Posture read endpoints — /api/external/v1/posture[/{ref}] and /frameworks.

Ship 4'.c — external consumers can pull the tenant's current
compliance posture across all enrolled frameworks in one call,
or drill in on a single control for evidence + engine proposals.

Design notes:

  * Bulk snapshot flat list — external clients (SIEM feeds,
    compliance-platform integrations) want to iterate a single
    array, not walk a nested {standard: {theme: [controls]}}
    tree like the internal dashboard endpoint returns.

  * `?standard_id=` filter for scoping to one framework.
  * `?finding=` repeatable filter (e.g. only pull NC/OFI).
  * `?changed_since=` ISO8601 for incremental polling.
  * `?limit=` + `?offset=` for pagination — even at ~200 controls
    per tenant, external clients might want smaller pages.

  * Drill-in requires `standard_id` query param — refs like
    `Art.32` exist across GDPR + ISO27701, so ambiguity is a
    real risk. Fail loud rather than guess.

  * /frameworks lists enrolled standards with their role
    (controller / processor) + control counts. Useful for
    partners to know what to expect before hitting /posture.

Auth scope: `external:posture:read`.
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


_ALLOWED_FINDINGS = ("NC", "OFI", "Comply", "N/A", "Not assessed")


# ── Response models ───────────────────────────────────────────────────

class PostureControl(BaseModel):
    ref:                 str            = Field(..., description="Control ref, e.g. `A.5.18` or `Art.32`.")
    standard_id:         str            = Field(..., description="Canonical standard id (DB slug), e.g. `ISO27001:2022`. Preserved verbatim so machine consumers can key on a stable string.")
    standard_display:    Optional[str]  = Field(None, description="Human display name for `standard_id`, e.g. `ISO 27001:2022`. Ship 7'.b — non-breaking addition; use this for tenant-facing UI, keep `standard_id` for keying.")
    finding:             Optional[str]  = Field(None, description="Live finding: NC / OFI / Comply / N/A / Not assessed.")
    confirmation_status: Optional[str]  = Field(None, description="`unconfirmed` / `document_confirmed` / `engine_confirmed` / etc.")
    last_updated:        Optional[str]  = Field(None, description="ISO8601 timestamp of the last change to this row.")
    gap_summary:         Optional[str]  = Field(None, description="Short excerpt of `gap_description` (up to 200 chars).")


class PostureSnapshotResponse(BaseModel):
    tenant_id:    str
    generated_at: str
    controls:     list[PostureControl]
    summary:      dict = Field(..., description="Counts by finding: `{NC, OFI, Comply, 'N/A', 'Not assessed', total}`.")
    total_before_pagination: int = Field(..., description="Total matching rows before limit/offset applied.")


class EngineProposal(BaseModel):
    status:  Optional[str] = Field(None, description="`proposed` / `none` / etc.")
    finding: Optional[str] = Field(None, description="Engine-derived finding.")
    reason:  Optional[str] = Field(None, description="Human-readable reason (`_humanize_reason` applied).")


class PostureControlDetail(BaseModel):
    tenant_id:           str
    ref:                 str
    standard_id:         str
    standard_display:    Optional[str] = None      # Ship 7'.b — see PostureControl above
    title:               Optional[str] = None
    finding:             Optional[str] = None
    confirmation_status: Optional[str] = None
    confidence:          Optional[str] = None
    last_updated:        Optional[str] = None
    gap_description:     Optional[str] = None
    action_required:     Optional[str] = None
    engine_proposal:     Optional[EngineProposal] = None


class FrameworkInfo(BaseModel):
    standard_id:   str  = Field(..., description="Canonical id, e.g. `ISO27001:2022`.")
    display_name:  str  = Field(..., description="Human label, e.g. `ISO 27001:2022`.")
    control_count: int  = Field(..., description="Distinct controls this framework has posture rows for.")


class FrameworksResponse(BaseModel):
    tenant_id:  str
    frameworks: list[FrameworkInfo]


# ── Endpoint helpers ──────────────────────────────────────────────────

def _iso_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _standard_display(std: str) -> str:
    # Ship 7'.b: single source of truth now lives in rag/output/vocab/.
    # This wrapper stays for callsite stability; adding new frameworks
    # is a one-file edit under rag/output/vocab/*.json.
    from rag.output import format_standard_id_exact
    return format_standard_id_exact(std)


# ── GET /posture ──────────────────────────────────────────────────────

@router.get("/posture",
            response_model = PostureSnapshotResponse,
            summary        = "Bulk posture snapshot")
async def get_posture(
    request:       Request,
    key            = Depends(external_key_with_scope("external:posture:read")),
    standard_id:   Optional[str] = Query(None, description="Filter to a single framework."),
    finding:       Optional[list[str]] = Query(None, description="Filter to one or more findings (repeatable)."),
    changed_since: Optional[str] = Query(None, description="ISO8601 timestamp — return only rows updated at or after this."),
    limit:         int = Query(500, ge=1, le=2000, description="Max rows to return."),
    offset:        int = Query(0,   ge=0,          description="Rows to skip (pagination)."),
):
    """Bulk posture snapshot across all enrolled frameworks (or a
    single one via `?standard_id=`). Returns a flat list — external
    clients iterate directly without walking a nested tree."""
    # Validate finding filter values
    if finding:
        bad = [f for f in finding if f not in _ALLOWED_FINDINGS]
        if bad:
            raise HTTPException(
                status_code = 400,
                detail      = f"Unknown finding filter value(s): {bad}. Allowed: {list(_ALLOWED_FINDINGS)}",
            )

    # Parse changed_since
    changed_since_dt = None
    if changed_since:
        try:
            changed_since_dt = _dt.datetime.fromisoformat(changed_since.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code = 400,
                detail      = f"`changed_since` must be ISO8601 (e.g. `2026-07-18T12:00:00Z`); got: {changed_since!r}",
            )

    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))

            # Build WHERE clause
            where_parts = ["pc.tenant_id = %s::uuid", "pc.is_active = TRUE"]
            params: list = [key.tenant_id]
            if standard_id:
                where_parts.append("pc.standard_id = %s")
                params.append(standard_id)
            if finding:
                placeholders = ",".join(["%s"] * len(finding))
                where_parts.append(f"pc.finding IN ({placeholders})")
                params.extend(finding)
            if changed_since_dt is not None:
                where_parts.append("pc.last_updated >= %s")
                params.append(changed_since_dt)

            where_sql = " AND ".join(where_parts)

            # Count before pagination — auditors want to know how many
            # rows they're paging through.
            cur.execute(
                f"SELECT COUNT(*) FROM posture_controls pc WHERE {where_sql}",
                params,
            )
            total = cur.fetchone()[0]

            # Fetch the page
            cur.execute(
                f"""
                SELECT pc.standard_id, pc.control_ref, pc.finding,
                       pc.confirmation_status, pc.last_updated,
                       LEFT(COALESCE(pc.gap_description,''), 200) AS gap_excerpt
                  FROM posture_controls pc
                 WHERE {where_sql}
                 ORDER BY pc.standard_id, pc.control_ref
                 LIMIT %s OFFSET %s
                """,
                params + [limit, offset],
            )
            rows = cur.fetchall()

            # Summary counts across the FILTERED result set (all matching
            # rows, not just this page) — clients aggregating across
            # pages don't want to re-run the counting themselves.
            cur.execute(
                f"""
                SELECT pc.finding, COUNT(*)
                  FROM posture_controls pc
                 WHERE {where_sql}
                 GROUP BY pc.finding
                """,
                params,
            )
            summary_rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    # Ship 7'.c — scrub gap_summary through the gateway so legacy
    # slug leakage from pre-dejargonize extraction doesn't reach
    # external consumers. Non-breaking: gap_summary keeps its shape,
    # just cleaner content.
    from rag.output import humanize as _humanize
    controls = [
        PostureControl(
            ref                 = ref,
            standard_id         = std,
            standard_display    = _standard_display(std),
            finding             = fnd,
            confirmation_status = cnf,
            last_updated        = lu.isoformat() if lu else None,
            gap_summary         = _humanize(gap, surface="stage2_reason") if gap else None,
        )
        for (std, ref, fnd, cnf, lu, gap) in rows
    ]
    summary = {f: 0 for f in _ALLOWED_FINDINGS}
    for fnd, ct in summary_rows:
        if fnd:
            summary[fnd] = ct
    summary["total"] = total

    return PostureSnapshotResponse(
        tenant_id               = key.tenant_id,
        generated_at            = _iso_now(),
        controls                = controls,
        summary                 = summary,
        total_before_pagination = total,
    )


# ── GET /posture/{ref} ────────────────────────────────────────────────

@router.get("/posture/{control_ref}",
            response_model = PostureControlDetail,
            summary        = "Single control drill-in")
async def get_posture_control(
    control_ref: str,
    request:     Request,
    key          = Depends(external_key_with_scope("external:posture:read")),
    standard_id: str = Query(..., description="Required. Refs like `Art.32` exist across GDPR + ISO27701, so ambiguity would break auditor-critical output."),
):
    """Drill-in on one (standard, ref) tuple. Returns the full posture
    row plus the engine's latest pending proposal (if any).

    `standard_id` is REQUIRED because the same ref can exist in
    multiple frameworks (e.g. `Art.32` under both GDPR:2016/679 and
    ISO27701:2019 with different meanings)."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            cur.execute(
                """
                SELECT pc.finding, pc.confirmation_status, pc.confidence,
                       pc.last_updated, pc.gap_description, pc.action_required,
                       pa.status, pa.finding, pa.gap_description
                  FROM posture_controls pc
                  LEFT JOIN posture_assertions pa
                    ON pa.tenant_id   = pc.tenant_id
                   AND pa.control_ref = pc.control_ref
                   AND pa.standard_id = pc.standard_id
                   AND pa.source      = 'engine'
                   AND pa.status      = 'pending'
                 WHERE pc.tenant_id   = %s::uuid
                   AND pc.control_ref = %s
                   AND pc.standard_id = %s
                   AND pc.is_active   = TRUE
                 LIMIT 1
                """,
                (key.tenant_id, control_ref, standard_id),
            )
            row = cur.fetchone()

            # Also fetch the control's title from RequirementNode
            # (Neo4j)? Skip — that's an out-of-band lookup that adds
            # latency. Title can be looked up separately if the
            # caller cares (e.g. via /docs endpoint in Ship 4'.g).
            title = None
    finally:
        pool.putconn(conn)

    if row is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No posture row for ({standard_id}, {control_ref}) under this tenant.",
        )

    (finding, cnf, conf, lu, gap, action,
     eng_status, eng_finding, eng_reason) = row

    # Ship 7'.c — engine reason composes _humanize_reason (semantic:
    # "0/4 children" → "0 of 4 evidence sources satisfied") with the
    # gateway (jargon scrub). Semantic pass first so the gateway sees
    # human-readable text.
    from rag.output import humanize as _gateway_humanize
    engine = None
    if eng_status is not None:
        try:
            from api_server import _humanize_reason  # noqa: WPS433
            humanized = _humanize_reason(eng_reason or "")
        except Exception:
            humanized = eng_reason
        # Ship 7'.c — gateway scrub for slug residue.
        humanized = _gateway_humanize(humanized or "", surface="stage2_reason") or humanized
        engine = EngineProposal(
            status  = eng_status,
            finding = eng_finding,
            reason  = humanized,
        )

    return PostureControlDetail(
        tenant_id           = key.tenant_id,
        ref                 = control_ref,
        standard_id         = standard_id,
        standard_display    = _standard_display(standard_id),
        title               = title,
        finding             = finding,
        confirmation_status = cnf,
        confidence          = conf,
        last_updated        = lu.isoformat() if lu else None,
        gap_description     = _gateway_humanize(gap, surface="stage2_reason") if gap else None,
        action_required     = _gateway_humanize(action, surface="stage2_reason") if action else None,
        engine_proposal     = engine,
    )


# ── GET /frameworks ───────────────────────────────────────────────────

@router.get("/frameworks",
            response_model = FrameworksResponse,
            summary        = "List enrolled frameworks + control counts")
async def get_frameworks(
    request: Request,
    key      = Depends(external_key_with_scope("external:posture:read")),
):
    """Return the tenant's enrolled standards with per-framework
    control counts. Useful before iterating /posture so external
    clients know how much data to expect + which frameworks are
    even in scope for this tenant."""
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (key.tenant_id,))
            cur.execute(
                """
                SELECT standard_id, COUNT(DISTINCT control_ref)
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid AND is_active = TRUE
                 GROUP BY standard_id
                 ORDER BY standard_id
                """,
                (key.tenant_id,),
            )
            rows = cur.fetchall()
    finally:
        pool.putconn(conn)

    frameworks = [
        FrameworkInfo(
            standard_id   = std,
            display_name  = _standard_display(std),
            control_count = int(ct),
        )
        for (std, ct) in rows
    ]
    return FrameworksResponse(tenant_id=key.tenant_id, frameworks=frameworks)
