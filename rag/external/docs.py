"""
Publish an EXTERNAL-ONLY OpenAPI spec at /api/external/v1/docs.

FastAPI's built-in `/docs` and `/redoc` expose the FULL app —
including internal UI-serving endpoints that partners have no
business seeing. This module:

  * Generates a filtered OpenAPI schema containing ONLY endpoints
    under the `external` tag.
  * Serves a Swagger UI page at /api/external/v1/docs.
  * Serves a ReDoc page at /api/external/v1/redoc.
  * Publishes the raw filtered JSON at /api/external/v1/openapi.json.

External clients can point their code generators at
`.../openapi.json` and build against a stable contract without
seeing the internal 60+ endpoint surface.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()


_EXTERNAL_TITLE       = "ArionComply External API"
_EXTERNAL_DESCRIPTION = (
    "External-facing API for programmatic access to the ArionComply "
    "compliance RAG platform. Intended for compliance-platform "
    "integrations, tenant automation / SIEM feeds, and partner-embedded "
    "surfaces. Authenticate with an `X-API-Key` header (see "
    "GET `/api/external/v1/status` to verify a key). All endpoints use a "
    "structured error contract: `{error: {code, message, request_id}}`."
)
_EXTERNAL_VERSION     = "1.0.0"


def _filter_openapi(full_schema: dict) -> dict:
    """Take FastAPI's full OpenAPI schema and return a version that
    only exposes /api/external/v1/* paths."""
    paths = full_schema.get("paths", {}) or {}
    filtered_paths = {
        p: ops for p, ops in paths.items()
        if p.startswith("/api/external/v1/")
    }
    return {
        "openapi": full_schema.get("openapi", "3.0.0"),
        "info": {
            "title":       _EXTERNAL_TITLE,
            "description": _EXTERNAL_DESCRIPTION,
            "version":     _EXTERNAL_VERSION,
        },
        "paths":      filtered_paths,
        "components": full_schema.get("components", {}),
        "tags":       [{
            "name":        "external",
            "description": "External API endpoints — see individual "
                           "operation for required scope.",
        }],
    }


@router.get("/openapi.json", include_in_schema=False)
async def external_openapi(request: Request):
    """Filtered OpenAPI JSON — external endpoints only."""
    app = request.app
    if not getattr(app.state, "_external_openapi_cache", None):
        # Generate the full schema once, filter, cache. Regenerate on
        # every request if the cache is missing so a code change
        # picks up without a restart during development.
        full = get_openapi(
            title       = app.title,
            version     = app.version,
            openapi_version = app.openapi_version,
            summary     = getattr(app, "summary", None),
            description = app.description,
            routes      = app.routes,
        )
        filtered = _filter_openapi(full)
        app.state._external_openapi_cache = filtered
    return JSONResponse(app.state._external_openapi_cache)


_SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ArionComply External API — Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url:  '/api/external/v1/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        docExpansion: 'list',
        defaultModelsExpandDepth: 1,
        tryItOutEnabled: true,
      });
    };
  </script>
</body>
</html>"""


_REDOC_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ArionComply External API — ReDoc</title>
  <style>body { margin: 0; padding: 0; }</style>
</head>
<body>
  <redoc spec-url="/api/external/v1/openapi.json"></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
</body>
</html>"""


@router.get("/docs", include_in_schema=False)
async def external_docs():
    """Swagger UI over the filtered OpenAPI."""
    return HTMLResponse(_SWAGGER_HTML)


@router.get("/redoc", include_in_schema=False)
async def external_redoc():
    """ReDoc over the filtered OpenAPI."""
    return HTMLResponse(_REDOC_HTML)
