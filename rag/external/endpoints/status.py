"""
GET /api/external/v1/status — proves the plumbing works.

Returns:
  * tenant_id (UUID)
  * tenant_display_name
  * queryable_standards (list) — the frameworks this tenant is enrolled in
  * scopes granted to the key (subset of external:*)
  * rate_limit: limit, remaining, reset_epoch — pulled from response headers
  * server_time (ISO-8601 UTC)

Auth: any external:* scope. Convention — a key with ANY external
scope should be able to read /status. Enforced with the `external:status`
scope; keys minted for external use should always include this one.
"""
from __future__ import annotations

import datetime as _dt

from fastapi import APIRouter, Depends, Request, Response

from rag.external.auth import external_key_with_scope


router = APIRouter()


@router.get("/status", summary="Health + tenant context")
async def get_status(
    request:  Request,
    response: Response,
    key       = Depends(external_key_with_scope("external:status")),
):
    """Returns the caller's tenant context + a health OK. Useful for
    smoke-testing an API key or building a client-side connectivity
    check. Also mirrors the rate-limit state via X-RateLimit-*
    headers on the response."""
    # Load the tenant's queryable standards (enrolled frameworks)
    # via the canonical scope loader — same source of truth as the
    # internal /api/v1/tenant/scope endpoint.
    from rag.scope_loader import load_tenant_scope
    pool = request.app.state.pg_pool
    conn = pool.getconn()
    tenant_name = None
    standards   = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (key.tenant_id,),
            )
            cur.execute(
                "SELECT name FROM tenants WHERE id = %s::uuid",
                (key.tenant_id,),
            )
            row = cur.fetchone()
            if row:
                tenant_name = row[0]
        scope = load_tenant_scope(conn, key.tenant_id)
        standards = list(scope.queryable_standards)
    finally:
        pool.putconn(conn)

    return {
        "ok":                   True,
        "tenant_id":            key.tenant_id,
        "tenant_display_name":  tenant_name,
        "queryable_standards":  standards,
        "scopes":               key.scopes,
        "rate_limit": {
            "limit":       int(response.headers.get("X-RateLimit-Limit",     "0")),
            "remaining":   int(response.headers.get("X-RateLimit-Remaining", "0")),
            "reset_epoch": int(response.headers.get("X-RateLimit-Reset",     "0")),
        },
        "server_time": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
