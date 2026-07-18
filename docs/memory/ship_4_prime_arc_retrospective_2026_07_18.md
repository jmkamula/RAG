---
name: ship-4-prime-arc-retrospective-2026-07-18
description: "Ship 4' arc retrospective — 8 sub-arcs (a→h) building the external RAG API end-to-end"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4' arc — start-to-finish log of the external-facing RAG API
build. Entry point for future work on anything under
`/api/external/v1/*` or `sdk/python/`.

**Arc window:** 2026-07-17 (opened after Ship 3' close) →
2026-07-18. 8 sub-arcs across ~24 hours.

## Motivation

Ship 3' finished the notification pipeline (13 producer kinds,
delivery worker, retention). At that point the system was
functionally rich but only accessible via the browser UI. Real
users — compliance-platform integrations, SIEM/SOAR feeds,
partner-embedded surfaces — need programmatic access. The user
asked for "the RAG API for external systems to use the RAG's
full capabilities" as a big first-principles rebuild.

We chose:
- **New versioned namespace** `/api/external/v1/*` distinct from
  the internal UI-serving surface (`/api/v1/*` stays as-is)
- **Full API-product treatment** — versioning, OpenAPI, scoped
  keys, rate limits, structured errors, changelog discipline
- **Use case: all-of-the-above** — compliance-platform reads,
  tenant automation writes, partner-embedded UIs

## Sub-arc inventory (with wins)

| Sub-arc | What | Key win |
|---|---|---|
| 4'.a | Foundation | Namespace + auth wrapper + rate-limit bucket + structured error contract + `GET /status` |
| 4'.b | `POST /query` | Structured RAG answer (answer + citations + session_id + latency_ms) — new endpoint reusing arion_graph pipeline |
| 4'.c | `/posture` family | 3 endpoints (bulk snapshot + drill-in + frameworks list); summary counts across FILTERED set pattern established |
| 4'.d | `/notifications` feed | SIEM/SOAR polling with since/kind[]/severity[]/unread_only filters |
| 4'.e | `/documents` + `/evidence` | Multipart upload → background pipeline; evidence JOIN both document_uploads + client_documents (bimodal FK) |
| 4'.f | `/cascade` + `/bridges` | Cascade timeline + Neo4j xfw edge lookup |
| 4'.g | Docs + SDK + Key mgmt | Filtered OpenAPI/Swagger/ReDoc + sdk/python/arioncomply/ + tenant-facing key management UI |
| 4'.b addendum | schema_v79 audit-log correction | Reclassified 5 tables from "audit" to "diagnostic" (DELETE granted, retention-eligible); posture_status_log FK CASCADE→NO ACTION |

## Final endpoint inventory — 14 endpoints, 8 scopes

Scope model is **fine-grained per-surface**. Every external endpoint
declares exactly one scope via `external_key_with_scope(scope)`
(rag/external/auth.py). Keys can hold any subset.

| Endpoint | Scope | Sub-arc |
|---|---|---|
| `GET /status` | `external:status` | 4'.a |
| `POST /query` | `external:query` | 4'.b |
| `GET /frameworks` | `external:posture:read` | 4'.c |
| `GET /posture` | `external:posture:read` | 4'.c |
| `GET /posture/{ref}` | `external:posture:read` | 4'.c |
| `GET /notifications` | `external:notifications:read` | 4'.d |
| `GET /notifications/{id}` | `external:notifications:read` | 4'.d |
| `POST /documents` | `external:evidence:write` | 4'.e |
| `GET /documents/{id}` | `external:evidence:read` | 4'.e |
| `GET /evidence` | `external:evidence:read` | 4'.e |
| `GET /cascade/timeline` | `external:cascade:read` | 4'.f |
| `GET /cascade/implications/{id}` | `external:cascade:read` | 4'.f |
| `GET /bridges` | `external:xfw:read` | 4'.f |
| `GET /openapi.json` + `/docs` + `/redoc` | *(public)* | 4'.g |

## Architectural constants that emerged

1. **Structured error contract**: `{error: {code, message,
   request_id}}` for every 4xx/5xx. Codes: `missing_api_key`,
   `invalid_api_key`, `invalid_scope`, `rate_limited`,
   `not_found`, `invalid_input`, `internal_error`,
   `service_unavailable`. Gated on request path so internal
   `{detail: ...}` shape is unchanged.
2. **X-RateLimit-\* headers on all responses** (both 200 and
   429), following AWS/Stripe convention. Fixed-window 60/min
   in `api_rate_limit_bucket` — atomic INSERT ON CONFLICT
   DO UPDATE.
3. **Summary counts across the FILTERED set, not just the
   page** (Ships 4'.c → 4'.d → 4'.e → 4'.f). External clients
   aggregating across pages get whole-set aggregates for free.
4. **Required `standard_id` on ref-drilling endpoints** — refs
   like `Art.32` exist across GDPR + ISO27701 with different
   meanings. Failing loud beats guessing.
5. **Structured 404 with `not_found` code** on every lookup
   endpoint. Malformed UUID → 400 `invalid_input`, not 500.
6. **Lazy imports in the auth dependency + endpoints** —
   avoids circular deps between `rag/external/*` and
   `api_server.py`.

## Test-fixture pattern

Ship 4'.j (predecessor arc) established the "idempotent tenant +
surgical delete" fixture pattern. Ship 4 extended it three times:

- **4'.b** — the `/query` pipeline writes to append-only audit
  logs (ai_call_log, chat_casefile_log, ...); tenant DELETE
  blocked. Rule: leave tenant idempotent, surgical-delete only
  what the test creates. Captured as
  [[feedback-test-fixture-audit-log-fks]].
- **4'.b addendum (schema_v79)** — audited the "audit log" claim.
  Reclassified 5 of 6 tables as diagnostic (DELETE-eligible);
  only `posture_status_log` stays truly load-bearing.
- **4'.f** — 2 more tables joined the compliance-load-bearing
  no-DELETE list: `external_evidence_verification_log` +
  `tenant_external_system` (FK-chain to verification_log).
  Fixture leaves both in place with idempotent ON CONFLICT /
  SELECT-first seeding.

Also: 4'.f caught a **within-run ordering issue** — the
`/documents` upload tests fire `upload_processed` notifications
that pollute subsequent `/notifications` tests. Fix: notification
fixture clears ALL tenant notifications at both setup and
teardown.

## Test suite growth

`tests/test_external_api.py` grew from 0 → 59 tests across the
arc:
- 4'.a: +7 (auth + rate limit)
- 4'.b: +6 (query)
- 4'.c: +9 (posture family)
- 4'.d: +11 (notifications)
- 4'.e: +9 (documents + evidence)
- 4'.f: +11 (cascade + bridges)
- 4'.g: +6 (docs + key mgmt)

Baseline held 207/208 across every sub-arc eval run.

## Frontend surfaces added

- **Profile page**: `renderApiKeys` + `showCreateApiKey` +
  `showNewKeyReveal` + `revokeApiKey` — full CRUD for external
  API keys with scope-picker checkbox tree over the 8
  `external:*` scopes. Copy-once red-panel warning on create.

## Schemas landed

- v78 — `api_rate_limit_bucket` table + `app_*_all` RLS policy
- v79 — audit-log classification correction (4'.b addendum);
  5 diagnostic logs get DELETE, `ai_call_log` loses UPDATE,
  `posture_status_log` tenant FK CASCADE→NO ACTION

## SDK — sdk/python/arioncomply/

PyPI-ready package:
- `client.py` — sync `Client` with method per endpoint;
  httpx + Pydantic; context-manager support
- `models.py` — response models mirroring server-side
- `errors.py` — typed exception hierarchy
- `pyproject.toml` — Python 3.10+; httpx>=0.24 + pydantic>=2.0
- `README.md` — quickstart + scope table + error patterns

**Future work not shipped:**
- Async client (currently sync-only)
- Codegen from openapi.json for models.py (manual sync today)
- Retry-on-429 with backoff
- Pagination iterator for /posture + /notifications

## What we did NOT ship (deferred)

- **Write-side notifications** (mark read/dismiss via external API) —
  needs `external:notifications:write` scope + PATCH endpoint
- **Write-side posture** (override / set N/A) — needs
  `external:posture:write` scope + careful design of audit trail
- **Webhook subscriptions** — currently external clients POLL;
  webhook push would be a natural companion
- **API-key rotation** flow (create new + soft-delete old +
  return raw once, all in one atomic call)
- **Non-external scopes in the key UI picker** — currently
  only `external:*` shown; internal chat/hitl/documents/posture
  scopes not exposed
- **Publish SDK to PyPI** — currently source-only in-repo

None of these are blockers for external clients today; all are
natural next-arc candidates.

## Lessons carried forward

- [[feedback-rls-grant-parity]] — audit both RLS + GRANTs on
  every `app_*_all` policy addition. Ship 4'.b addendum ran
  a systematic audit that reclassified 5 tables.
- [[feedback-test-fixture-audit-log-fks]] — compliance-
  load-bearing tables block tenant DELETE via FK. Use
  idempotent seeds + surgical delete of just what you created.
- **Scope decision is architectural.** Adding an endpoint means
  picking a scope. Fine-grained-per-surface has served well —
  8 scopes over 14 endpoints, clean pairs.
- **Duplication vs. abstraction.** `/query` duplicated ~50
  lines of arion_graph invocation from the internal `/chat`
  endpoint rather than refactoring into a helper. Contained;
  low regression risk. Refactor if a third caller appears.
- **Slow OpenAI evals are OK.** Multiple sub-arcs' evals ran
  slow (LLM rate limits + stdout buffering hiding progress).
  When the arc doesn't touch the RAG path, the eval is purely
  a regression guard — outcome is guaranteed identical.

## Related

- [[ship-3-prime-arc-retrospective-2026-07-17]] — companion arc
  retrospective; the notification pipeline this arc exposes
- [[ship-4-prime-a-external-api-foundation-2026-07-17]] →
  [[ship-4-prime-g-docs-sdk-key-mgmt-2026-07-18]] — per-sub-arc
  memories
- [[feedback-rls-grant-parity]] — the RLS/GRANT discipline
- [[feedback-test-fixture-audit-log-fks]] — the fixture
  teardown pattern
