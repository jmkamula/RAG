"""
FastAPI router for /api/external/v1/*.

All endpoints under this router MUST use `external_key_with_scope`
(rag/external/auth.py) for authentication + scope check + rate
limit. Endpoints WITHOUT scope enforcement are not allowed (docs
pages are the only exception — they're public-by-design).

Full surface (Ship 4'.a → 4'.g, all shipped 2026-07-17→18):

  Status + query
    GET  /status                             external:status
    POST /query                              external:query

  Posture family
    GET  /frameworks                         external:posture:read
    GET  /posture                            external:posture:read
    GET  /posture/{control_ref}              external:posture:read

  Notifications
    GET  /notifications                      external:notifications:read
    GET  /notifications/{id}                 external:notifications:read

  Documents + evidence
    POST /documents                          external:evidence:write
    GET  /documents/{id}                     external:evidence:read
    GET  /evidence                           external:evidence:read

  Cascade + bridges
    GET  /cascade/timeline                   external:cascade:read
    GET  /cascade/implications/{id}          external:cascade:read
    GET  /bridges                            external:xfw:read

  Docs (no scope — public)
    GET  /openapi.json
    GET  /docs                               (Swagger UI)
    GET  /redoc                              (ReDoc UI)

See [[ship-4-prime-arc-retrospective-2026-07-18]] for the full-arc
synthesis: architectural constants, test-fixture patterns,
lessons learned, and follow-up work.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from rag.external.auth import external_key_with_scope
from rag.external.endpoints.status        import router as status_router
from rag.external.endpoints.query         import router as query_router
from rag.external.endpoints.posture       import router as posture_router
from rag.external.endpoints.notifications import router as notifications_router
from rag.external.endpoints.documents     import router as documents_router
from rag.external.endpoints.cascade       import router as cascade_router
from rag.external.endpoints.bridges       import router as bridges_router
from rag.external.docs                    import router as docs_router


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
external_router.include_router(posture_router)
external_router.include_router(notifications_router)
external_router.include_router(documents_router)
external_router.include_router(cascade_router)
external_router.include_router(bridges_router)
external_router.include_router(docs_router)
