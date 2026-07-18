---
name: ship-4-prime-g-docs-sdk-key-mgmt-2026-07-18
description: "Ship 4'.g — OpenAPI docs + Python SDK + tenant-facing API-key management (the arc's biggest sub-arc)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.g (2026-07-18) — three concerns bundled into one arc.
Makes the external API discoverable, consumable, and manageable.

## 1. OpenAPI docs

`rag/external/docs.py` — publishes an EXTERNAL-ONLY OpenAPI spec.
Three endpoints under `/api/external/v1`:

- `GET /openapi.json` — filtered spec (13 external endpoints only,
  not the ~80 internal routes)
- `GET /docs`  — Swagger UI (CDN-hosted, points at `openapi.json`)
- `GET /redoc` — ReDoc UI (same source)

Filter logic: `_filter_openapi()` walks FastAPI's full schema and
keeps only paths starting with `/api/external/v1/`. Title +
description overridden to reflect the external product surface.
Cached on `app.state._external_openapi_cache` so subsequent
requests skip regeneration.

## 2. Python SDK

`sdk/python/arioncomply/` — a proper PyPI-ready package.

Structure:
- `__init__.py` — public exports (Client + error classes)
- `client.py` — httpx-based sync `Client` with one method per
  endpoint. Context-manager support. Persistent httpx session
  for connection reuse.
- `models.py` — Pydantic response models mirroring the
  server-side ones. Manually kept in sync (future work:
  generator from openapi.json).
- `errors.py` — typed exception hierarchy:
  * `ArionAuthError`       (401)
  * `ArionScopeError`      (403)
  * `ArionRateLimitError`  (429 — carries `retry_after`)
  * `ArionNotFoundError`   (404)
  * `ArionValidationError` (400 / 422)
  * `ArionServerError`     (500 / 503)
  * `ArionResponseError`   (other)
- `pyproject.toml` — httpx + pydantic deps, PyPI metadata
- `README.md` — quickstart + scope table + error-handling

All 14 endpoints wrapped:
- `status()`, `query()`, `frameworks()`, `posture()`,
  `posture_control()`, `notifications()`, `notification()`,
  `upload_document()`, `document()`, `evidence()`,
  `cascade_timeline()`, `implication()`, `bridges()`

Smoke-tested against localhost: `status()` + `frameworks()` +
`posture(finding=['NC'])` + `bridges()` all work; typed
`ArionNotFoundError` raised on 404.

## 3. Tenant-facing API-key management

Three endpoints on the INTERNAL surface (not external):
- `POST /api/v1/tenant/api-keys` — create key, returns raw ONCE
- `GET  /api/v1/tenant/api-keys` — list (prefix + metadata only)
- `DELETE /api/v1/tenant/api-keys/{id}` — soft-delete
  (`is_active = FALSE`)

Design:
- Raw key format: `arion_ext_` + `secrets.token_urlsafe(32)`
- Server stores only `sha256(raw)` — no key recovery
- Scopes validated against `_EXTERNAL_SCOPES_ALLOWED` list
  (only the 8 external:* scopes)
- `expires_in_days` optional (`None` = never)
- Refuse to revoke the key you're currently authenticated with
  (would 401 the next request — tenant must use a different
  key to revoke this one)

Frontend addition in `static/arioncomply.html`:
- `renderApiKeys()` — lists active + revoked with scopes,
  last-used date, expiry, and Revoke button
- `showCreateApiKey()` — form with name field + checkbox tree
  for the 8 scopes + expires_in_days
- `submitCreateApiKey()` — POSTs, then shows the raw key ONCE
  with a Copy button + red-panel warning
- `revokeApiKey()` — confirm dialog + DELETE

Also added "Open API docs →" link in the section header pointing
at `/api/external/v1/docs`.

## Tests

**59/59 pass** (53 from Ships 4'.a-f + 6 new):
1. `test_openapi_docs_served` — openapi.json filtered to external
2. `test_api_keys_list_endpoint` — list works with any valid key
3. `test_api_keys_create_returns_raw_once` — raw key + expiry
4. `test_api_keys_create_bad_scope_returns_400` — allow-list
5. `test_api_keys_revoke_flow` — create → works → revoke → 401
6. `test_api_keys_revoke_self_returns_400` — can't revoke
   current auth key

## Baseline

Eval running (PID 127667). Ship 4'.g adds routes but doesn't
touch the RAG pipeline — regression guard only.

## Ship 4 progress

| Sub-arc | Status |
|---|---|
| 4'.a Foundation | ✓ shipped |
| 4'.b /query | ✓ shipped |
| 4'.c /posture family | ✓ shipped |
| 4'.d /notifications | ✓ shipped |
| 4'.e /documents + /evidence | ✓ shipped |
| 4'.f /cascade + /bridges | ✓ shipped |
| **4'.g Docs + SDK + Key UI** | **✓ shipped** |
| 4'.h Ship 4 arc retrospective | next / arc close |

## SDK future work (not shipped in 4'.g)

- Async client (currently sync-only)
- OpenAPI codegen for models.py — eliminates manual sync
- Retry-on-429 with backoff (currently raises immediately)
- Pagination iterator for /posture + /notifications
  (currently manual limit/offset)
- Publish to PyPI (currently just source in-repo)

## Key-management future work

- Rotate a key (create new + soft-delete old + return raw once)
- Non-external scopes in the picker (chat, hitl, documents,
  posture) — currently only external:* exposed in the UI

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — the
  scope model this arc's UI + SDK reflect
- [[ship-4-prime-f-cascade-bridges-2026-07-18]] — previous
  sub-arc
