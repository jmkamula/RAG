---
name: ship-15-prime-d-demonstrates-sdk-2026-07-22
description: "Ship 15'.d — DEMONSTRATES traversal on obligation-linked risk drill-ins + Python SDK typed methods for the 3 read endpoints"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 15'.d (2026-07-22) — fourth sub-arc of Ship 15. Two
concerns bundled: (1) DEMONSTRATES traversal in the risk drill-
in for obligation-linked controls; (2) Python SDK typed methods
for the 3 external risk endpoints.

## Part 1 — DEMONSTRATES traversal in risk drill-in

Ship 14'.g flagged this: when a risk links to an obligation
(e.g. `GDPR:2016/679:Art.32`), the drill-in currently shows the
raw ref but doesn't traverse to the program/extension sources
that demonstrate it. This sub-arc fills that gap.

### Implementation

- New `<div id="risk-demonstrated-by-slot">` container appended
  after the "Linked controls" section in `_renderRiskDetail`
  (Ship 14'.d)
- New `_appendRiskDemonstratedBy(linked)` async function:
  - Iterates `linked_controls` filtering to `role === 'obligation'`
  - For each obligation, GETs
    `/api/v1/dashboard/control/{ref}/demonstrated-by?standard_id=X`
  - Renders `renderDemonstratedByPanel(dm)` (existing Ship 4a
    helper) inside a wrapping `<div>` with a header identifying
    the obligation ref + standard display name
  - Silent-fail per Phase 4a convention — endpoint / cache /
    Neo4j errors just skip the panel; drill-in still complete
  - Fire-and-forget: called at the end of `_renderRiskDetail`
    without blocking initial render

### Verification (end-to-end)

Endpoint smoke test on `Art.32` with `standard_id=GDPR:2016/679`:
- 11 demonstrated_by sources returned
- Mix of ISO27001 (`A.5.23`) + ISO27701 (`A.7.2.1`, `B.8.2.2`)
  program + extension refs
- `propagated_finding = OFI` (aggregated across the 11 sources'
  live findings)

Client wiring verified via HTML fetch — all 3 pieces landed:
- `_appendRiskDemonstratedBy` function definition
- `risk-demonstrated-by-slot` container div
- `role === 'obligation'` role filter in the JS

Framework role model discipline reinforced: when a risk links
to `Art.32` (obligation), the drill-in now surfaces the ISO
27001 + ISO 27701 controls demonstrating it — program +
extension appear together as first-class citizens, no
primary/xfw split.

## Part 2 — Python SDK typed methods

Ship 14'.g flagged this: SDK needs typed methods for the 3
external read endpoints (write endpoints stay internal-only
per Ship 15'.a).

### New models in `sdk/python/arioncomply/models.py`

- `LinkedControl` — role + subject + standard_display tagged
  control ref
- `RiskRow` — compact list-surface shape (13 core fields +
  linked_controls)
- `RiskDetail` — drill-in shape (RiskRow + treatment plan +
  audit trail; all 5 schema_v87 columns exposed)
- `RiskSummarySummary` — nested summary shape inside RisksListResponse
- `RisksListResponse` — envelope for `GET /risks`
- `RiskSummaryResponse` — full aggregate for `GET /risks/summary`
  (counts + per-option / per-status breakdowns + 5x5 heatmap +
  top-5 rows)

### New methods on `Client` in `sdk/python/arioncomply/client.py`

- `.risks(status=None, limit=200, offset=0) → RisksListResponse`
- `.risk_summary() → RiskSummaryResponse`
- `.risk(risk_id: str) → RiskDetail`

All require `external:risks:read` scope on the API key.

### Verification (end-to-end SDK smoke test)

```python
c = Client(base_url="http://localhost:8080", api_key="arion_dev_key_2026")
s = c.risk_summary()        # total=35, top_count=5, typed
rr = c.risks(limit=2)       # linked_controls[0].role='program' (typed)
d = c.risk(rr.risks[0].id)  # RiskDetail with typed treatment plan
```

All 3 methods returned typed Pydantic responses; IDE
autocomplete + type-checker coverage now on par with the other
external endpoints.

## Ship 14'.a addendum alignment

**1. Role split?**

**YES, reinforced.** The DEMONSTRATES panel is the concrete
render of the framework-role-model DEMONSTRATES cascade —
obligation-linked risks now show their program + extension
demonstrators explicitly. SDK's LinkedControl model preserves
`role` + `subject` fields per response.

**2. Parallel CaseFile view?**

Not applicable — this arc is UI + SDK-layer, no chat surfaces
touched.

**3. Deterministic routing?**

Not applicable — no LLM inference. The
`role === 'obligation'` filter is a deterministic string check;
`_appendRiskDemonstratedBy` iterates the pre-tagged
linked_controls array in-order.

**4. Guidance-normative discipline?**

Preserved — DEMONSTRATES traversal is READ over posture data
already populated by Phase 2b/2c. No engine mutations. SDK
methods are read-only.

## What did NOT ship

- **DEMONSTRATES panel on the top-5 / full-list rows** — only
  on the drill-in. The list rows show `linked_controls` inline
  without demonstration lineage. Adding lineage inline would
  clutter the compact table shape. Deferred as UI polish.
- **Async SDK client** — the SDK still ships as a sync `Client`.
  Deferred to a future arc when async partners ask.
- **SDK write methods** — POST/PATCH/DELETE are internal-only
  (Ship 15'.a). SDK stays consume-only per Ship 4' external
  discipline. Would need `external:risks:write` scope + external
  endpoints first.
- **DEMONSTRATES caching on the client** — repeat visits to
  the same risk drill-in re-fetch the demonstrated-by data for
  each obligation. Not measurably slow (2-3 obligations × 20ms
  each ~ 60ms).

## Ship 15 progress

| Sub-arc | Status |
|---|---|
| 15'.a POST + PATCH + DELETE + emit_risk_added | ✓ |
| 15'.b Workbook importer INSERT detection + producer | ✓ |
| 15'.c Notification UI drill-in for 4 risk kinds | ✓ |
| **15'.d DEMONSTRATES traversal + SDK typed methods** | **✓ (this doc)** |
| 15'.e Eval cases + arc retrospective | next |

## Related

- [[framework-role-model-arc]] Phase 4a — the demonstrated-by
  provenance surface this arc re-uses for the risk drill-in
- [[ship-14-prime-d-risk-register-dashboard-2026-07-22]] — the
  drill-in this arc extends with DEMONSTRATES panels
- [[ship-4-prime-g-docs-sdk-key-mgmt-2026-07-18]] — the SDK
  pattern this arc extends with 3 new typed methods
- Ship 15'.e: eval cases + arc retrospective
