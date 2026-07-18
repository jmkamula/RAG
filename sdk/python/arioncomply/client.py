"""
`Client` — httpx-based synchronous client for the ArionComply
external API.

Every method:
  * Handles auth via the `X-API-Key` header
  * Parses the response into a Pydantic model from `.models`
  * Raises typed exceptions from `.errors` on 4xx/5xx

The client keeps a persistent `httpx.Client` for connection
reuse. Use as a context manager to close cleanly:

    with Client(base_url=..., api_key=...) as c:
        status = c.status()
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Iterable

import httpx

from arioncomply.errors import (
    ArionAuthError, ArionScopeError, ArionRateLimitError,
    ArionNotFoundError, ArionValidationError, ArionServerError,
    ArionResponseError,
)
from arioncomply.models import (
    StatusResponse, QueryResponse,
    FrameworksResponse, PostureSnapshotResponse, PostureControlDetail,
    NotificationsResponse, Notification,
    UploadResponse, DocumentStatus, EvidenceResponse,
    CascadeTimelineResponse, ImplicationDetail, BridgesResponse,
)


DEFAULT_TIMEOUT = 30.0
UPLOAD_TIMEOUT  = 120.0


class Client:
    """Sync client for /api/external/v1/*.

    Parameters
    ----------
    base_url : str
        Root URL of the ArionComply deployment
        (e.g. `https://example.arioncomply.com`).
    api_key  : str
        External API key with the appropriate `external:*` scopes.
    timeout  : float
        Default request timeout in seconds. Uploads use a separate
        `UPLOAD_TIMEOUT` because pipeline runs can be slow.
    """
    def __init__(
        self,
        base_url: str,
        api_key:  str,
        *,
        timeout:  float = DEFAULT_TIMEOUT,
    ):
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self._client  = httpx.Client(
            base_url = self.base_url,
            headers  = {"X-API-Key": api_key, "Accept": "application/json"},
            timeout  = timeout,
        )

    # ── Context manager plumbing ──────────────────────────────────────

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ── Internal request helpers ──────────────────────────────────────

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"/api/external/v1{path}"

    def _raise_for_error(self, r: httpx.Response) -> None:
        """Translate an error response into a typed exception."""
        if 200 <= r.status_code < 300:
            return
        try:
            body = r.json()
        except Exception:
            body = {}
        err  = body.get("error") or {}
        code = err.get("code")
        msg  = err.get("message") or r.text or f"HTTP {r.status_code}"
        rid  = err.get("request_id")
        status = r.status_code
        kw = dict(code=code, status=status, request_id=rid, response=body)
        if status == 401:
            raise ArionAuthError(msg, **kw)
        if status == 403:
            raise ArionScopeError(msg, **kw)
        if status == 404:
            raise ArionNotFoundError(msg, **kw)
        if status == 429:
            retry_after = r.headers.get("Retry-After")
            raise ArionRateLimitError(
                msg,
                retry_after=int(retry_after) if retry_after else None,
                **kw,
            )
        if status in (400, 422):
            raise ArionValidationError(msg, **kw)
        if status in (500, 503):
            raise ArionServerError(msg, **kw)
        raise ArionResponseError(msg, **kw)

    def _get(self, path: str, *, params: Optional[dict] = None) -> dict:
        r = self._client.get(self._url(path), params=params)
        self._raise_for_error(r)
        return r.json()

    def _post_json(self, path: str, *, json: dict) -> dict:
        r = self._client.post(self._url(path), json=json)
        self._raise_for_error(r)
        return r.json()

    def _post_multipart(
        self,
        path:    str,
        *,
        files:   dict,
        data:    Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> dict:
        r = self._client.post(
            self._url(path),
            files   = files,
            data    = data,
            timeout = timeout,
        )
        self._raise_for_error(r)
        return r.json()

    # ── Public methods — one per endpoint ─────────────────────────────

    # Status
    def status(self) -> StatusResponse:
        """GET /status — health + tenant context."""
        return StatusResponse.model_validate(self._get("/status"))

    # Query
    def query(
        self,
        question:   str,
        *,
        session_id: Optional[str] = None,
    ) -> QueryResponse:
        """POST /query — submit a compliance question to the RAG."""
        body = {"question": question}
        if session_id: body["session_id"] = session_id
        return QueryResponse.model_validate(self._post_json("/query", json=body))

    # Frameworks + posture
    def frameworks(self) -> FrameworksResponse:
        """GET /frameworks — enrolled standards + control counts."""
        return FrameworksResponse.model_validate(self._get("/frameworks"))

    def posture(
        self,
        *,
        standard_id:   Optional[str] = None,
        finding:       Optional[Iterable[str]] = None,
        changed_since: Optional[str] = None,
        limit:         int = 500,
        offset:        int = 0,
    ) -> PostureSnapshotResponse:
        """GET /posture — bulk posture snapshot."""
        params: dict = {"limit": limit, "offset": offset}
        if standard_id:                params["standard_id"]   = standard_id
        if finding:                    params["finding"]       = list(finding)
        if changed_since:              params["changed_since"] = changed_since
        return PostureSnapshotResponse.model_validate(self._get("/posture", params=params))

    def posture_control(
        self,
        control_ref: str,
        *,
        standard_id: str,
    ) -> PostureControlDetail:
        """GET /posture/{ref} — drill-in on one control."""
        return PostureControlDetail.model_validate(
            self._get(f"/posture/{control_ref}", params={"standard_id": standard_id}),
        )

    # Notifications
    def notifications(
        self,
        *,
        since:             Optional[str]           = None,
        kind:              Optional[Iterable[str]] = None,
        severity:          Optional[Iterable[str]] = None,
        unread_only:       bool                    = False,
        include_dismissed: bool                    = False,
        limit:             int                     = 200,
        offset:            int                     = 0,
    ) -> NotificationsResponse:
        """GET /notifications — inbox feed."""
        params: dict = {
            "unread_only":       str(unread_only).lower(),
            "include_dismissed": str(include_dismissed).lower(),
            "limit":             limit,
            "offset":            offset,
        }
        if since:    params["since"]    = since
        if kind:     params["kind"]     = list(kind)
        if severity: params["severity"] = list(severity)
        return NotificationsResponse.model_validate(self._get("/notifications", params=params))

    def notification(self, notification_id: str) -> Notification:
        """GET /notifications/{id} — single by UUID."""
        return Notification.model_validate(self._get(f"/notifications/{notification_id}"))

    # Documents + evidence
    def upload_document(
        self,
        file_path:              str,
        *,
        filename:               Optional[str] = None,
        declared_standard_id:   Optional[str] = None,
        declared_evidence_type: Optional[str] = None,
    ) -> UploadResponse:
        """POST /documents — multipart upload; runs async on server."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(file_path)
        name = filename or p.name
        with p.open("rb") as fh:
            files = {"file": (name, fh, "application/octet-stream")}
            data:  dict = {}
            if declared_standard_id:   data["declared_standard_id"]   = declared_standard_id
            if declared_evidence_type: data["declared_evidence_type"] = declared_evidence_type
            return UploadResponse.model_validate(self._post_multipart(
                "/documents",
                files   = files,
                data    = data,
                timeout = UPLOAD_TIMEOUT,
            ))

    def document(self, upload_id: str) -> DocumentStatus:
        """GET /documents/{id} — poll extraction status."""
        return DocumentStatus.model_validate(self._get(f"/documents/{upload_id}"))

    def evidence(
        self,
        *,
        control_ref: str,
        standard_id: str,
    ) -> EvidenceResponse:
        """GET /evidence — all findings for a (control, standard)."""
        return EvidenceResponse.model_validate(self._get(
            "/evidence",
            params={"control_ref": control_ref, "standard_id": standard_id},
        ))

    # Cascade
    def cascade_timeline(
        self,
        *,
        kind:        Optional[Iterable[str]] = None,
        control_ref: Optional[str] = None,
        since_days:  int = 30,
        limit:       int = 200,
        offset:      int = 0,
    ) -> CascadeTimelineResponse:
        """GET /cascade/timeline — implications + followups feed."""
        params: dict = {"since_days": since_days, "limit": limit, "offset": offset}
        if kind:        params["kind"]        = list(kind)
        if control_ref: params["control_ref"] = control_ref
        return CascadeTimelineResponse.model_validate(self._get("/cascade/timeline", params=params))

    def implication(self, implication_id: str) -> ImplicationDetail:
        """GET /cascade/implications/{id} — single drill-in."""
        return ImplicationDetail.model_validate(
            self._get(f"/cascade/implications/{implication_id}"),
        )

    # Bridges
    def bridges(
        self,
        *,
        control_ref: str,
        standard_id: str,
    ) -> BridgesResponse:
        """GET /bridges — cross-framework relationships."""
        return BridgesResponse.model_validate(self._get(
            "/bridges",
            params={"control_ref": control_ref, "standard_id": standard_id},
        ))
