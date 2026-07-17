"""
Auth dependency factory for /api/external/v1/*.

Wraps the existing `require_api_key` (in api_server.py) with:
  * fine-grained scope check
  * per-key rate-limit check + response headers

Usage on an endpoint:

    from rag.external.auth import external_key_with_scope

    @external_router.get("/query")
    async def query(
        key = Depends(external_key_with_scope("external:query")),
        ...
    ):
        ...

The `key` object is the `APIKeyInfo` dataclass from api_server.py —
callers use `key.tenant_id` for tenant scoping.

Rate-limit headers are attached to EVERY response (both allowed and
429-blocked), following AWS/Stripe conventions:
  * X-RateLimit-Limit      — the applicable ceiling
  * X-RateLimit-Remaining  — requests left in the current window
  * X-RateLimit-Reset      — unix ts when the window resets

On 429, add `Retry-After` header (seconds).
"""
from __future__ import annotations

import logging
from typing import Callable

from fastapi import Depends, HTTPException, Request, Response, status

from rag.external.rate_limit import (
    DEFAULT_RATE_LIMIT_PER_MIN,
    check_and_bump,
)

logger = logging.getLogger(__name__)


def external_key_with_scope(scope: str) -> Callable:
    """Factory: returns a dependency that (1) validates the API key,
    (2) requires `scope` to be present, (3) applies the fixed-window
    rate limit, (4) attaches X-RateLimit-* headers to the response.

    The dependency imports `require_api_key` LAZILY from api_server so
    the module load order stays clean (api_server can import this
    module without a circular dep).
    """
    async def _dep(
        request:  Request,
        response: Response,
    ):
        # Lazy imports to avoid a circular dependency with api_server.
        from api_server import require_api_key, APIKeyInfo  # noqa: WPS433

        # Step 1: validate the key (reuses existing dep — will raise
        # 401 on missing/invalid/expired).
        key_info: APIKeyInfo = await require_api_key(
            request,
            x_api_key=request.headers.get("x-api-key"),
        )

        # Step 2: scope check.
        if scope not in (key_info.scopes or []):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail      = f"API key missing scope: {scope}",
            )

        # Step 3: rate limit.
        pool = request.app.state.pg_pool
        conn = pool.getconn()
        try:
            with conn.cursor() as cur:
                # Set tenant scope so RLS-guarded reads elsewhere in
                # the same request work. arioncomply_app's permissive
                # policy on api_rate_limit_bucket doesn't need it, but
                # downstream reads on tenant-scoped tables will.
                cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                            (key_info.tenant_id,))
                state = check_and_bump(cur, key_info.key_id,
                                       limit=DEFAULT_RATE_LIMIT_PER_MIN)
                conn.commit()
        finally:
            pool.putconn(conn)

        # Step 4: attach headers to whatever response the endpoint
        # returns. Both allowed and 429-blocked paths carry these.
        response.headers["X-RateLimit-Limit"]     = str(state.limit)
        response.headers["X-RateLimit-Remaining"] = str(state.remaining)
        response.headers["X-RateLimit-Reset"]     = str(state.reset_epoch)

        if not state.allowed:
            raise HTTPException(
                status_code = status.HTTP_429_TOO_MANY_REQUESTS,
                detail      = (
                    f"Rate limit exceeded: {state.limit} req/min "
                    f"(retry in {state.retry_after}s)"
                ),
                headers     = {
                    "Retry-After":          str(state.retry_after),
                    "X-RateLimit-Limit":    str(state.limit),
                    "X-RateLimit-Remaining":"0",
                    "X-RateLimit-Reset":    str(state.reset_epoch),
                },
            )

        return key_info

    return _dep
