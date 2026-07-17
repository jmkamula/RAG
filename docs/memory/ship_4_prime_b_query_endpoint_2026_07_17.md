---
name: ship-4-prime-b-query-endpoint-2026-07-17
description: "Ship 4'.b — POST /api/external/v1/query. Structured RAG answer for external consumers."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.b (2026-07-17) — first content endpoint on the external
API. External consumers can now ask the RAG a compliance
question and get a structured JSON answer + typed citations
+ session id + trace id.

## What shipped

### `rag/external/endpoints/query.py`

- Pydantic `QueryRequest` — `question` (required, 1-4000 chars) +
  optional `session_id` (letters/digits/hyphens/underscores, ≤64).
- Pydantic `Citation` — `ref` + optional `standard` + `posture`.
- Pydantic `QueryResponse` — `answer` + `question_type` +
  `citations[]` + `session_id` + `request_id` + `latency_ms` +
  `needs_clarification` + optional `clarification_question`.
- Handler `POST /query` guarded by `external:query` scope; runs
  the same LangGraph pipeline (`arion_graph.invoke`) as internal
  `/api/v1/chat` but shapes the output structurally.

### Pipeline reuse

The invocation logic (state seed, thread-id build, tenant
context refresh, checkpointer state check, executor invoke)
is duplicated from `/api/v1/chat`. Kept short + intentional
(~50 lines) to avoid coupling internal + external endpoints.
If a future refactor lifts the common bits into a helper,
this file should adopt it — but for now the duplication is
contained and the two response shapes stay independent.

### Citation posture — best-effort in Ship 4'.b

`Citation.posture` is populated ONLY when
`result["posture_findings"]` carries the ref. For a `gap_analysis`
query the posture data flows through `context_text` and the LLM
composes it into `answer`, so `posture_findings` is empty and the
citations get `posture: null`. Not a bug — just an
enrichment gap. A follow-up sub-arc can query `posture_controls`
directly for cited refs to fill this reliably.

### Router wiring

`rag/external/router.py::external_router.include_router(query_router)`.
The scope `external:query` was already granted to `arion_dev_key_2026`
in Ship 4'.a.

## Tests

`tests/test_external_api.py` — 6 new tests (13/13 total across
the file):

1. `test_query_missing_body_returns_422` — empty POST body → 422
2. `test_query_empty_question_returns_422` — Pydantic min_length=1
3. `test_query_wrong_scope_returns_403` — key with only
   `external:status` gets 403 with `external:query` in message
4. `test_query_happy_path_returns_structured_response` — 200 with
   the full QueryResponse shape + X-RateLimit-* headers
5. `test_query_session_id_echo_and_multi_turn` — session_id echoed
   on turn 1 + accepted on turn 2
6. `test_query_bad_session_id_returns_400` — SQL-injection-shaped
   session_id rejected at boundary

## Test fixture teardown lesson

The `/query` tests invoke the RAG pipeline which writes to
`ai_call_log` + `chat_casefile_log` + `chat_consensus_log` +
`intake_trace_log` + `fact_recompute_log`. All of these are
append-only audit logs — no DELETE grant for arioncomply_app by
[[feedback-rls-grant-parity]] design. So the fixture teardown
CAN'T delete the tenant (FK blocks it).

**Resolution**: `_purge_test_api_keys()` does surgical cleanup —
deletes only api_rate_limit_bucket + api_keys for the test
tenant. Tenant + user seeded idempotently (ON CONFLICT DO
NOTHING) so subsequent runs reuse them. Audit-log rows
accumulate for the test tenant but that's fine — it's a
test tenant, not a real one.

Captured this pattern in [[feedback-test-fixture-audit-log-fks]]
for the next integration-test author to hit the same wall.

## Baseline

Full eval running. Ship 4'.b doesn't touch the RAG-pipeline code
itself (only adds a wrapper endpoint), so 207/208 expected.

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — auth/rate
  limit/error contract this arc builds on
- [[feedback-rls-grant-parity]] — the audit-log DELETE decision
  that surfaced as a test-fixture puzzle
