"""
ArionComply external API — /api/external/v1/*.

Ship 4'.a foundation:
  * scoped API-key auth (fine-grained `external:*` scopes)
  * per-key fixed-window rate limiting (60/min default)
  * structured error contract ({"error": {"code", "message", "request_id"}})
  * first endpoint: GET /api/external/v1/status

External API surface is intentionally separate from the internal
UI-serving surface (`/api/v1/*` in `api_server.py`). External
consumers get:
  * A stable versioned namespace (`/api/external/v1`)
  * A predictable auth + error contract
  * Rate limiting they can rely on
  * OpenAPI docs at `/api/external/v1/docs` (Ship 4'.g planned)

Internal endpoints remain unversioned externally — they're an
implementation detail of the browser UI.
"""

from rag.external.router import external_router

__all__ = ["external_router"]
