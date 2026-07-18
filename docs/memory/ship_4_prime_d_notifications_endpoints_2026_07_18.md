---
name: ship-4-prime-d-notifications-endpoints-2026-07-18
description: "Ship 4'.d — notification feed on external API for SIEM/SOAR polling"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.d (2026-07-18) — read-side notification feed. SIEM,
SOAR, monitoring dashboards, and compliance-platform integrations
can now poll the tenant's inbox as a JSON feed. Read-only in
this arc; marking read/dismissed is a future write-scope arc.

## What shipped

`rag/external/endpoints/notifications.py` — 2 endpoints, scope
`external:notifications:read`:

### GET /api/external/v1/notifications

Query params:
- `since` — ISO8601, only rows with `fired_at >= since`. Primary
  incremental-polling contract — clients remember the highest
  `fired_at` they saw and pass it back next time.
- `kind[]` — repeatable filter (13 valid kinds — Ship 3' inventory)
- `severity[]` — repeatable filter (critical/high/medium/low/info)
- `unread_only` — bool, filter to unread+not-dismissed
- `include_dismissed` — bool, default false
- `limit` (default 200, max 1000), `offset` for pagination

Response includes `summary` counts (total / unread / urgent)
across the FILTERED set — pagination-aware clients get whole-set
aggregates for free. Same pattern as Ship 4'.c's /posture.

`urgent` matches the internal `/api/v1/tenant/notifications`
definition: severity in (critical, high) AND unread AND
not-dismissed.

### GET /api/external/v1/notifications/{id}

Fetch a single notification by UUID. 404 if unknown for this
tenant. Malformed UUID → 400 (invalid_input) rather than 500.

## Filter validation

Kind + severity filters are checked against explicit allow-lists
at the endpoint boundary. Unknown values → 400 with the message
listing valid options. This prevents SQL-shape leaks and gives
external client authors a clear error message when they typo
a filter value.

## Tests

`tests/test_external_api.py` — **33/33 pass** (22 from
Ships 4'.a-c + 11 new for /notifications). New fixture
`_test_state_notifications()` seeds 4 notifications with
distinct kinds/severities/states:
- 2 unread + high (nc_surfaced on A.5.18, A.6.4)
- 1 read + medium (freshness_expiry on A.5.15)
- 1 dismissed + low (auto_resolved)

Test coverage:
1. Default list excludes dismissed (3 rows, 2 unread, 2 urgent)
2. `include_dismissed=true` returns all 4
3. `unread_only=true` returns 2
4. `kind=nc_surfaced` filter returns 2
5. `severity=medium` filter returns 1
6. Bad kind → 400 invalid_input
7. Bad since → 400 invalid_input
8. Scope check (key without external:notifications:read → 403)
9. Single fetch by id → 200
10. Unknown id → 404 not_found
11. Malformed id → 400 invalid_input

## Baseline

Eval running (PID 104584). No RAG path change — new endpoints
query tenant_notification directly.

## Ship 4 progress

| Sub-arc | Status |
|---|---|
| 4'.a Foundation | ✓ shipped |
| 4'.b /query | ✓ shipped |
| 4'.c /posture family | ✓ shipped |
| **4'.d /notifications** | **✓ shipped** |
| 4'.e /evidence + POST /documents | next |
| 4'.f /cascade + /bridges | future |
| 4'.g Python SDK + docs + key UI | future |

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — auth
  + rate limit + error contract
- [[ship-4-prime-c-posture-endpoints-2026-07-17]] — the
  summary-across-filtered-set pattern this arc reuses
- [[ship-3-prime-arc-retrospective-2026-07-17]] — the 13
  notification kinds this feed surfaces
