"""
Exception hierarchy for the ArionComply SDK.

Each exception subclasses `ArionError` and carries the structured
error body from the server:

    {"error": {"code": "...", "message": "...", "request_id": "..."}}

The `request_id` is the correlation id for support requests — it
matches the server-side log entry for the failed request.
"""
from __future__ import annotations

from typing import Optional


class ArionError(Exception):
    """Base for all SDK-raised errors."""
    def __init__(
        self,
        message:    str,
        *,
        code:       Optional[str] = None,
        status:     Optional[int] = None,
        request_id: Optional[str] = None,
        response:   Optional[object] = None,
    ):
        super().__init__(message)
        self.code       = code
        self.status     = status
        self.request_id = request_id
        self.response   = response

    def __repr__(self) -> str:
        parts = [self.__class__.__name__ + "("]
        if self.status is not None: parts.append(f"status={self.status}, ")
        if self.code:               parts.append(f"code={self.code!r}, ")
        if self.request_id:         parts.append(f"request_id={self.request_id!r}, ")
        parts.append(f"message={str(self)!r})")
        return "".join(parts)


class ArionAuthError(ArionError):
    """401 Unauthorized — missing/invalid/inactive API key."""


class ArionScopeError(ArionError):
    """403 Forbidden — API key lacks the required `external:*` scope."""


class ArionRateLimitError(ArionError):
    """429 Too Many Requests — rate-limit exceeded.

    `retry_after` is seconds until the window resets."""
    def __init__(self, message: str, *, retry_after: Optional[int] = None, **kw):
        super().__init__(message, **kw)
        self.retry_after = retry_after


class ArionNotFoundError(ArionError):
    """404 Not Found — resource not visible to this tenant."""


class ArionValidationError(ArionError):
    """400 or 422 — invalid request shape."""


class ArionServerError(ArionError):
    """500 / 503 — something went wrong upstream."""


class ArionResponseError(ArionError):
    """Any other unexpected status."""
