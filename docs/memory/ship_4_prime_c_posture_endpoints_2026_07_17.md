---
name: ship-4-prime-c-posture-endpoints-2026-07-17
description: "Ship 4'.c — 3 posture-read endpoints on the external API (/posture, /posture/{ref}, /frameworks)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.c (2026-07-17) — read-side surface for the external
RAG API. Compliance-platform integrations, SIEM feeds, and
partner UIs can now poll or bulk-snapshot the tenant's posture.

## What shipped

`rag/external/endpoints/posture.py` — 3 endpoints, all under
scope `external:posture:read`:

### GET /api/external/v1/frameworks
Enrolled standards + control counts. Small response — useful
for partners to know what to expect before iterating /posture.

Response:
```
{
  "tenant_id": "...",
  "frameworks": [
    {"standard_id":"ISO27001:2022","display_name":"ISO 27001:2022","control_count":118},
    ...
  ]
}
```

### GET /api/external/v1/posture
Bulk snapshot as a flat list — external clients iterate
directly rather than walking a nested {standard: {theme:
[controls]}} tree like the internal dashboard endpoint.

Query params:
- `standard_id` — filter to one framework
- `finding` — repeatable (`?finding=NC&finding=OFI`)
- `changed_since` — ISO8601 for incremental polling
- `limit` (default 500, max 2000), `offset` for pagination

Response includes:
- `controls[]` — the current page
- `summary` — counts by finding across the FILTERED set
  (not just the page), so pagination doesn't lose the whole-set
  aggregate
- `total_before_pagination`

### GET /api/external/v1/posture/{control_ref}
Drill-in on one (standard, ref) tuple. Returns finding +
confirmation_status + confidence + gap_description +
action_required + engine's pending proposal (if any).

**`standard_id` is REQUIRED as a query param.** Refs like
`Art.32` exist across GDPR + ISO27701 with different meanings.
Failing loud on ambiguity is better than guessing.

Returns 404 with structured error when no matching row exists
for this tenant.

## Design decisions worth remembering

- **Summary counts ignore pagination** — the summary block
  reflects the full filtered set. External clients aggregating
  across pages shouldn't have to re-run counts themselves.
- **`changed_since` uses `last_updated` field** — enables
  cheap incremental polling for SIEM/SOAR consumers that only
  need diffs since their last pull.
- **Engine proposal humanized via lazy import** —
  `_humanize_reason` from api_server keeps external prose
  auditor-readable rather than exposing raw engine slugs.

## Tests

`tests/test_external_api.py` — **22/22 pass** (13 from
Ships 4'.a-b + 9 new for /posture):

1. `test_frameworks_happy_path` — 200 with frameworks list
2. `test_frameworks_scope_check` — 403 without external:posture:read
3. `test_posture_snapshot_happy_path` — 200 with seeded rows visible
4. `test_posture_finding_filter` — `?finding=NC` returns only NC rows
5. `test_posture_bad_finding_returns_400` — unknown finding rejected
6. `test_posture_bad_changed_since_returns_400` — bad ISO8601 rejected
7. `test_posture_drill_in_happy_path` — 200 with full detail
8. `test_posture_drill_in_unknown_ref_returns_404` — structured 404
9. `test_posture_drill_in_missing_standard_id_returns_422` — required param

Fixture extends the standard `_test_state()` with an idempotent
posture-rows seed (2 controls, distinct findings) so the summary
math has data to work with. Teardown removes the seeded rows.

## Baseline

Eval running. Ship 4'.c doesn't touch the RAG pipeline — only
adds 3 read endpoints querying `posture_controls` directly.
Expected 207/208.

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — auth
  + rate limit + error contract
- [[ship-4-prime-b-query-endpoint-2026-07-17]] — POST /query
  (the write-side companion)

## Ship 4 progress

| Sub-arc | Status |
|---|---|
| 4'.a Foundation | ✓ shipped |
| 4'.b /query | ✓ shipped |
| **4'.c /posture family** | **✓ shipped** |
| 4'.d /notifications feed | next |
| 4'.e /evidence + POST /documents | future |
| 4'.f /cascade + /bridges | future |
| 4'.g Python SDK + docs + key UI | future |
