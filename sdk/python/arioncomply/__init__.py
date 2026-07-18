"""
ArionComply Python SDK for the external API (`/api/external/v1/*`).

Quickstart:

    from arioncomply import Client

    c = Client(base_url="https://example.arioncomply.com",
               api_key="arion_ext_...")
    print(c.status())
    print(c.query("what are our access rights gaps?").answer)
    for row in c.posture(standard_id="ISO27001:2022").controls:
        print(row.ref, row.finding)

The SDK is a thin, typed layer over httpx. Each response is a
Pydantic model — so IDEs autocomplete field names and type
checkers catch errors.

Error handling raises exceptions from `arioncomply.errors`:
- ArionAuthError            (401)
- ArionScopeError           (403)
- ArionRateLimitError       (429, carries retry_after)
- ArionNotFoundError        (404)
- ArionValidationError      (400 / 422)
- ArionServerError          (500 / 503)
- ArionResponseError        (other)
"""
from arioncomply.client import Client
from arioncomply.errors import (
    ArionError,
    ArionAuthError,
    ArionScopeError,
    ArionRateLimitError,
    ArionNotFoundError,
    ArionValidationError,
    ArionServerError,
    ArionResponseError,
)

__all__ = [
    "Client",
    "ArionError",
    "ArionAuthError",
    "ArionScopeError",
    "ArionRateLimitError",
    "ArionNotFoundError",
    "ArionValidationError",
    "ArionServerError",
    "ArionResponseError",
]

__version__ = "0.1.0"
