"""
FastAPI router for /api/external/v1/*.

All endpoints under this router MUST use `external_key_with_scope`
(rag/external/auth.py) for authentication + scope check + rate
limit. Endpoints WITHOUT scope enforcement are not allowed.

Currently exposed:
  * GET /api/external/v1/status — health + tenant context (Ship 4'.a)

Planned (Ship 4'.b onward):
  * POST /query
  * GET  /posture
  * GET  /posture/{control_ref}
  * GET  /notifications
  * GET  /evidence/{leaf_id}
  * POST /documents
  * GET  /cascade/timeline
  * GET  /bridges/{control_ref}
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from rag.external.auth import external_key_with_scope
from rag.external.endpoints.status import router as status_router
from rag.external.endpoints.query  import router as query_router


external_router = APIRouter(
    prefix = "/api/external/v1",
    tags   = ["external"],
    responses = {
        401: {"description": "Missing or invalid API key"},
        403: {"description": "API key missing required scope"},
        429: {"description": "Rate limit exceeded (60 req/min per key)"},
    },
)

external_router.include_router(status_router)
external_router.include_router(query_router)
