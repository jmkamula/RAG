"""
ArionComply external API — structured error contract.

External clients get JSON errors of the shape:

    {
      "error": {
        "code":       "invalid_scope",
        "message":    "API key missing scope: external:query",
        "request_id": "5f3e1c2a-..."
      }
    }

Codes:

  * `missing_api_key`      — no X-API-Key header
  * `invalid_api_key`      — key not found / expired / inactive
  * `invalid_scope`        — key valid but lacks the required scope
  * `rate_limited`         — 60/min window exceeded
  * `not_found`            — resource lookup missed
  * `invalid_input`        — request body / query param validation failed
  * `internal_error`       — anything else that reached the handler

The trace_id middleware (api_server.py) puts a `request_id` on
`request.state.trace_id`; we surface it in the response so support
requests can be correlated with server logs.

The handler is registered ONLY for the external router — internal
UI-facing endpoints keep their existing HTMLish detail contract.
"""
from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError

logger = logging.getLogger(__name__)


# Map HTTP status codes → error codes we surface externally
_STATUS_CODE_TO_ERROR_CODE = {
    400: "invalid_input",
    401: "invalid_api_key",
    403: "invalid_scope",
    404: "not_found",
    422: "invalid_input",
    429: "rate_limited",
    500: "internal_error",
    503: "service_unavailable",
}


def _external_request(request: Request) -> bool:
    """Is this request handled by the external namespace?"""
    return request.url.path.startswith("/api/external/")


async def external_http_exception_handler(request: Request, exc: HTTPException):
    """Wrap HTTPException in the structured contract for external
    endpoints. Passes through unchanged for non-external requests so
    the existing internal handlers stay unaffected."""
    if not _external_request(request):
        # Fall back to FastAPI's default handler behavior
        return JSONResponse(
            status_code = exc.status_code,
            content     = {"detail": exc.detail},
            headers     = getattr(exc, "headers", None) or {},
        )

    code = _STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, "http_error")
    # For 401 there are two sub-codes worth distinguishing
    if exc.status_code == 401 and exc.detail:
        detail_l = str(exc.detail).lower()
        if "header required" in detail_l or "missing" in detail_l:
            code = "missing_api_key"
    # Ship 76'.d — 404 sub-code for scope decisions. When a control
    # is out of scope for the tenant (applicability_status='na'), the
    # detail message contains "out of scope" and we emit the more
    # specific `control_out_of_scope` code so partners can distinguish
    # "no such control" from "control exists but you scoped it out".
    if exc.status_code == 404 and exc.detail:
        if "out of scope" in str(exc.detail).lower():
            code = "control_out_of_scope"

    request_id = getattr(request.state, "trace_id", None)
    body = {
        "error": {
            "code":       code,
            "message":    str(exc.detail),
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code = exc.status_code,
        content     = body,
        headers     = getattr(exc, "headers", None) or {},
    )


async def external_validation_exception_handler(
    request: Request, exc: RequestValidationError,
):
    """Wrap Pydantic validation errors in the structured contract."""
    if not _external_request(request):
        return JSONResponse(
            status_code = 422,
            content     = {"detail": exc.errors()},
        )
    request_id = getattr(request.state, "trace_id", None)
    # Compress the errors list to a single readable message + expose
    # the full structured errors under `details` for programmatic
    # consumers.
    first_error = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(p) for p in (first_error.get("loc") or []))
    body = {
        "error": {
            "code":       "invalid_input",
            "message":    f"Validation failed: {loc}: {first_error.get('msg') or 'invalid'}",
            "request_id": request_id,
            "details":    exc.errors(),
        }
    }
    return JSONResponse(status_code=422, content=body)


async def external_unhandled_exception_handler(request: Request, exc: Exception):
    """Last-resort handler for anything else that reaches the top.
    Logs the traceback + returns a 500 in structured form. Never
    leaks the exception details to external callers."""
    if not _external_request(request):
        # Don't intercept internal paths — let FastAPI's default handle
        raise exc
    logger.exception("Unhandled exception in external API: %s", exc)
    request_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code = 500,
        content     = {"error": {
            "code":       "internal_error",
            "message":    "Something went wrong on our side. Please retry.",
            "request_id": request_id,
        }},
    )
