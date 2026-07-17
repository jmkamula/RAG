---
name: ship-4-prime-a-external-api-foundation-2026-07-17
description: "Ship 4'.a — external API foundation (/api/external/v1/*) with scoped keys + rate limit + structured errors"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.a (2026-07-17) — opens Ship 4 arc. Foundation for the
external RAG API surface (compliance-platform integrations,
tenant automation / SIEM feeds, partner-embedded UIs).

## Product decision

External API is a NEW namespace (`/api/external/v1/*`) distinct
from the internal UI-serving surface (`/api/v1/*`). External
consumers get:

- Stable versioned prefix
- Fine-grained scoped API keys (per-surface `external:*` scopes)
- Rate limits (60/min per key, fail-closed with 429 + Retry-After)
- Structured error contract (`{error: {code, message, request_id}}`)
- OpenAPI-first design (docs endpoint arrives with Ship 4'.g)

Internal endpoints stay as they are — implementation detail of
the browser UI.

## What shipped

### `db/schema_v78_ship4a_rate_limit_bucket.sql`

New table `api_rate_limit_bucket`. Fixed-window (1-minute)
counter, one row per api_key:

    (key_id UUID PK, window_start TIMESTAMPTZ, count INT, updated_at)

Atomic UPSERT semantics via `INSERT ... ON CONFLICT (key_id)
DO UPDATE`. Postgres serializes the ON CONFLICT branch —
safe under concurrent hits on the same key without extra locking.

Follows the [[feedback-rls-grant-parity]] discipline —
`app_api_rate_limit_bucket_all` policy + full CRUD grants
(including DELETE for a future retention sweep).

### `rag/external/` module

Layer separation kept clean:

- `errors.py` — structured `{error: {...}}` JSON body + code map
  (missing_api_key / invalid_api_key / invalid_scope /
  rate_limited / invalid_input / not_found / internal_error /
  service_unavailable). Handlers gate on
  `request.url.path.startswith("/api/external/")` so internal
  UI routes keep their existing `{detail: ...}` shape.
- `rate_limit.py` — `check_and_bump(cur, key_id, limit)` returns
  `RateLimitState(allowed, remaining, reset_epoch, limit,
  retry_after)`. Atomic UPSERT, O(1) per call.
- `auth.py` — `external_key_with_scope(scope)` factory: (1)
  reuses existing `require_api_key` from api_server (2) checks
  scope presence (3) applies rate limit (4) attaches
  `X-RateLimit-*` headers to the response. On 429 also attaches
  `Retry-After`.
- `router.py` — `APIRouter(prefix="/api/external/v1", tags=["external"])`
  with 401/403/429 responses declared for OpenAPI.
- `endpoints/status.py` — first endpoint. Returns tenant_id +
  display_name + queryable_standards (via `load_tenant_scope`) +
  active scopes + rate-limit state + server_time.

### Wiring in api_server.py

Registered LATE (after all internal routes) so the module load
order stays clean. Exception handlers registered for
`HTTPException` and `RequestValidationError` — both gated to
external requests only via the handler's path check.

## Scopes granted for the dev key

Existing `arion_dev_key_2026` had `[chat, hitl, documents, posture]`
scopes. Added `external:status` + `external:query` so smoke tests
and the future query endpoint work. Real tenant keys will need
per-scope opt-in when we ship the key-management UI (Ship 4'.g).

## Fine-grained scope inventory (planned)

Only `external:status` is enforced today; the rest land with their
respective endpoints:

- `external:status`               — Ship 4'.a (this arc)
- `external:query`                — Ship 4'.b
- `external:posture:read`         — Ship 4'.c
- `external:posture:write`        — future
- `external:notifications:read`   — Ship 4'.d
- `external:evidence:read`        — Ship 4'.e
- `external:evidence:write`       — Ship 4'.e (uploads)
- `external:cascade:read`         — Ship 4'.f
- `external:xfw:read`             — Ship 4'.f

## Rate-limit design notes

Fixed-window at 60/min per key. `X-RateLimit-*` headers on all
responses (both allowed + 429). Standard AWS/Stripe convention.

Not yet:
- Per-key override (e.g. some partners get 300/min) — needs a
  `rate_limit_per_min` column on `api_keys`
- Distinct burst counter — 20-burst is subsumed by fixed-window
  (all 60 requests could hit in the first second under this
  design; burst enforcement means little at this scale)
- Retention sweep for stale bucket rows — table stays tiny (one
  row per active key)

## Tests

`tests/test_external_api.py` — 7 integration tests exercising
the running API server (not mocked). Fixture seeds throwaway
tenant + 3 api_keys (good/no-scope/inactive). All 4xx paths
verified with structured error body + correct code field.

**7/7 pass.** Zero test residue.

## Baseline

Full eval running against the reloaded API. Expected 207/208.
Ship 4'.a doesn't touch the RAG path — only adds a parallel
namespace + exception handlers gated on path prefix.

## Related

- [[feedback-rls-grant-parity]] — the discipline this arc followed
  from the start (schema_v78 grants DELETE alongside the
  permissive policy)
- [[ship-3-prime-j-delivery-integration-tests-2026-07-17]] —
  established the "integration test with throwaway tenant" pattern
  extended here

## Ship 4 roadmap ahead

| Sub-arc | Scope |
|---|---|
| 4'.b | POST /query — structured RAG answer JSON |
| 4'.c | GET /posture[/{ref}] — bulk + drill-in |
| 4'.d | GET /notifications — inbox feed |
| 4'.e | GET /evidence + POST /documents — evidence + upload |
| 4'.f | GET /cascade/* + /bridges/* — timeline + xfw |
| 4'.g | Python SDK skeleton + /docs page + key-management UI |
