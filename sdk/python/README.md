# arioncomply — Python SDK for the ArionComply external API

A thin, typed client over the `/api/external/v1/*` surface. Use it
to poll posture, feed notifications into your SIEM, upload documents,
or query the RAG programmatically.

## Install

```bash
pip install arioncomply
```

## Quickstart

```python
from arioncomply import Client

with Client(base_url="https://example.arioncomply.com",
            api_key="arion_ext_...") as c:

    # Verify auth + see enrolled frameworks
    s = c.status()
    print("Tenant:", s.tenant_display_name, "— scopes:", s.scopes)

    # Ask a question
    q = c.query("what are our access rights gaps?")
    print(q.answer)
    for citation in q.citations:
        print("  ", citation.ref, "posture:", citation.posture)

    # Bulk posture snapshot filtered to non-compliant controls
    snap = c.posture(standard_id="ISO27001:2022", finding=["NC", "OFI"])
    print(f"{snap.summary['total']} controls to review")

    # Notification feed for the last 24h
    inbox = c.notifications(unread_only=True)
    for n in inbox.notifications:
        print(n.severity.upper(), n.kind, n.title)

    # Upload a policy document
    up = c.upload_document(
        "policies/access_control.docx",
        declared_standard_id="ISO27001:2022",
    )
    print("Upload started:", up.upload_id, up.extraction_status)
```

## Scopes

Each endpoint requires a scope on the API key:

| Endpoint                                        | Required scope                 |
|---|---|
| `status()`                                      | `external:status`              |
| `query()`                                       | `external:query`               |
| `frameworks()`, `posture()`, `posture_control()` | `external:posture:read`        |
| `notifications()`, `notification()`             | `external:notifications:read`  |
| `evidence()`, `document()`                      | `external:evidence:read`       |
| `upload_document()`                             | `external:evidence:write`      |
| `cascade_timeline()`, `implication()`           | `external:cascade:read`        |
| `bridges()`                                     | `external:xfw:read`            |

Missing scope → `ArionScopeError` (HTTP 403).

## Rate limits

Default is 60 requests/minute per key. Exceeded → `ArionRateLimitError`
(HTTP 429) — the exception carries `retry_after` (seconds).

Every response also carries `X-RateLimit-Limit / Remaining / Reset`
headers so you can pace yourself proactively.

## Error handling

```python
from arioncomply import Client, ArionScopeError, ArionRateLimitError

try:
    c.bridges(control_ref="A.5.18", standard_id="ISO27001:2022")
except ArionScopeError as e:
    print(f"Missing scope: {e.message} (request_id={e.request_id})")
except ArionRateLimitError as e:
    print(f"Slow down; retry in {e.retry_after}s")
```

All exceptions subclass `ArionError` and carry:
- `.status`     — HTTP status code
- `.code`       — server-side error code (`invalid_scope` / `rate_limited` / ...)
- `.request_id` — correlate with server logs
- `.response`   — full parsed body

## OpenAPI

The server publishes a filtered OpenAPI at
`/api/external/v1/openapi.json`, with human-readable Swagger UI at
`/docs` and ReDoc at `/redoc` (both under the `/api/external/v1/`
prefix). Point your code generator at the JSON if you'd rather
generate a client than use this one.

## Versioning

Uses semver on `arioncomply.__version__`. Breaking changes bump
the major.
