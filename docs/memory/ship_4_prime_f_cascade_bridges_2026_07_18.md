---
name: ship-4-prime-f-cascade-bridges-2026-07-18
description: "Ship 4'.f — /cascade family + /bridges on external API"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.f (2026-07-18) — cascade timeline + framework-graph
bridges for external consumers.

## What shipped

`rag/external/endpoints/cascade.py` + `bridges.py` — 3 endpoints:

### GET /api/external/v1/cascade/timeline
Chronological feed of `triggered_implication` + `expected_
followup_event` rows. Kept simpler than the internal
`/api/v1/tenant/cascade-timeline` (drops verifications +
suppressions — internal telemetry / edge-case).

Query params:
- `kind[]` — `implication` and/or `followup`
- `control_ref` — filter implications to one target control
- `since_days` — rolling window (default 30, max 365)
- `limit / offset` — pagination

Response `summary` reports `{implication, followup, total,
overdue}` counts across the FILTERED set. `overdue` counts
implications past `due_date` while still `status='pending'`.

Scope: `external:cascade:read`.

### GET /api/external/v1/cascade/implications/{id}
Single implication drill-in. Returns all `triggered_implication`
columns for the specified row. 404 on unknown, 400 on
malformed UUID.

Scope: `external:cascade:read`.

### GET /api/external/v1/bridges?control_ref=X&standard_id=Y
Cross-framework relationships from the Neo4j RequirementNode
graph. Returns outbound + inbound edges by type (IMPLEMENTS /
SUPPORTS / ENABLES / GOVERNANCE) with each edge carrying
`{id, ref, standard_id, title, rel}` for the linked control.

Pure framework metadata — no tenant state. Still gated behind
`external:xfw:read` scope for partner permission granularity.

## Design decisions worth remembering

- **Bridges use their own scope** (`external:xfw:read`), not
  posture:read or cascade:read. Rationale: cross-framework
  mapping is orthogonal to both — partners might want just the
  bridge metadata without the tenant-scoped cascade timeline.
- **cascade/timeline drops verifications + suppressions** — the
  internal endpoint unions 4 tables; external strips to just
  the 2 auditor-actionable kinds (implications + followups).
  Verifications are noisy telemetry, suppressions are edge-case.
- **Neo4j lazy driver init** — the driver is created per-request
  inside `_neo_driver()`. Not a connection pool. Fine at this
  scale; move to pooling if we ever hit 10+ req/s on this
  endpoint.

## Tests

**53/53 pass** (42 from Ships 4'.a-e + 11 new for /cascade
+ /bridges). New fixture `_test_state_cascade()` seeds:
- 2 api_keys (external:cascade:read, external:xfw:read)
- 1 `tenant_external_system` row (idempotent)
- 1 `external_evidence_verification_log` row (source of FK
  for the seeded cascade rows)
- 1 `triggered_implication` on A.5.18 due 30d out
- 1 `expected_followup_event` expiring 14d out

## Test-fixture teardown pattern EVOLVED

Two more tables joined the "compliance-load-bearing, no DELETE
for arioncomply_app" list surfaced by this arc:

- `external_evidence_verification_log` — audit trail of cite-mode
  verifications (INSERT/SELECT only)
- `tenant_external_system` — has DELETE but FK-referenced by
  verification_log rows that we can't delete, so tenant_external_
  system rows for the test tenant are also stuck

Applied [[feedback-test-fixture-audit-log-fks]] pattern: leave
both in place, use idempotent ON CONFLICT / SELECT-first
seeding so subsequent runs reuse the existing row. Only delete
the children with DELETE grants (triggered_implication +
expected_followup_event).

Second lesson learned: within a single test run, /documents
upload tests fire `upload_processed` notifications that pollute
subsequent /notifications tests' summary counts. Fix: the
`_test_state_notifications` fixture now DELETEs all
notifications for the test tenant at BOTH setup and teardown,
not just TEST-4d-prefixed titles.

## Baseline

Eval running. No RAG path change; cascade queries Postgres
directly, bridges queries Neo4j directly.

## Ship 4 progress

| Sub-arc | Status |
|---|---|
| 4'.a Foundation | ✓ shipped |
| 4'.b /query | ✓ shipped |
| 4'.c /posture family | ✓ shipped |
| 4'.d /notifications | ✓ shipped |
| 4'.e /documents + /evidence | ✓ shipped |
| **4'.f /cascade + /bridges** | **✓ shipped** |
| 4'.g Python SDK + docs + key UI | next / last |

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — auth
- [[feedback-test-fixture-audit-log-fks]] — audit-log FK teardown
  pattern; extended in this arc with 2 more tables
