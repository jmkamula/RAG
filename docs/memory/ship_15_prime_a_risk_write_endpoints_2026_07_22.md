---
name: ship-15-prime-a-risk-write-endpoints-2026-07-22
description: "Ship 15'.a — POST / PATCH / DELETE endpoints for the risks table + emit_risk_added wire-up"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 15'.a (2026-07-22) — opens Ship 15 arc (risk register
polish + close-out). Delivers the write-side API for the risks
table, closing the loop between the workbook-driven bulk path
(Ship 14'.b) and interactive tenant edits.

## What ships

### 3 new endpoints on `/api/v1/tenant/risks`

All internal-only (require_api_key). External writes deferred
to a future arc if a partner asks.

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/tenant/risks` | Create a new row. Body = `RiskCreate` (external_ref required, everything else optional). 201 → returns full RiskDetail. 409 on duplicate external_ref. |
| `PATCH /api/v1/tenant/risks/{risk_id}` | Partial update. Body = `RiskPatch` (every field optional). external_ref is IMMUTABLE — 400 if included. Returns updated RiskDetail. 404 if not found. |
| `DELETE /api/v1/tenant/risks/{risk_id}` | Soft-delete (`is_active = FALSE`). Row preserved for auditor provenance. Optional `?reason=` persisted to `deletion_reason`. 204 on delete; 404 if not found. |

### New Pydantic request models + helpers in `rag/risk/queries.py`

- `RiskCreate` — POST body schema. All 21 columns exposed;
  external_ref required; likelihood/impact CHECK 1-5;
  residual_risk_level CHECK 1-25; validation via Pydantic
  ge/le constraints.
- `RiskPatch` — PATCH body schema. Same fields as RiskCreate
  but every one optional (via Optional[...]). `model_dump(
  exclude_unset=True)` isolates the fields the caller actually
  named — unset fields keep DB values.
- `DuplicateRiskError` — raised by `create_risk()` when the
  UNIQUE(tenant_id, external_ref) constraint fires. Endpoint
  handler catches it and returns 409 with structured detail.

### Query helpers

- `create_risk(conn, tenant_id, payload)` — INSERT with
  only-non-None-values. Returns `(risk_id, external_ref)`.
- `update_risk(conn, tenant_id, risk_id, payload)` — dynamic
  UPDATE built from `exclude_unset=True` fields; bumps
  `updated_at = NOW()`; returns risk_id or None on miss.
- `soft_delete_risk(conn, tenant_id, risk_id, reason)` —
  is_active flip + deletion_reason + deleted_at. Returns
  True/False.

### Notification wire-up

`create_tenant_risk` calls `emit_risk_added()` from Ship
14'.f AFTER commit of the INSERT. Silent-fail — the API
response commits to the row insert regardless of whether
the notification write succeeds. Existing 7-day dedup handles
double-POSTs.

## Verification (end-to-end smoke tests)

**POST create:**
```
POST /api/v1/tenant/risks
  {"external_ref":"R-TEST-15A","threat":"Test risk...",
   "likelihood":3,"impact":4,"risk_score":12,
   "treatment_option":"Mitigate","treatment_status":"open",
   "control_refs":["ISO27001:2022:A.5.15","ISO27701:2019:A.7.2.8"]}
→ 201 {"id":"48c894f7-...","external_ref":"R-TEST-15A",...}
```
- Framework-role-model discipline: `linked_controls` returned
  `roles=['extension', 'program']` side-by-side (ISO 27001 +
  ISO 27701)
- `risk_added` notification verified in `tenant_notification`
  table with severity `low`, title "New risk R-TEST-15A added
  to the register"

**POST duplicate:**
```
POST same external_ref → 409 {"detail":"A risk with external_ref='R-TEST-15A' already exists..."}
```

**PATCH update:**
```
PATCH /api/v1/tenant/risks/{id}
  {"treatment_status":"in_progress","residual_risk_level":8,
   "treatment_rationale":"Mitigation via A.5.15..."}
→ 200 {"treatment_status":"in_progress","residual_risk_level":8,...}
```
- Only sent fields updated; other row values unchanged

**DELETE soft-delete:**
```
DELETE /api/v1/tenant/risks/{id}?reason=smoke_test_cleanup → 204
GET /api/v1/tenant/risks/{id} → 404 (RLS filters is_active=FALSE)
```

## Ship 14'.a addendum alignment

**1. Role split?**

Yes — `RiskCreate.control_refs` accepts any
`STANDARD:VERSION:REF` string across ALL roles. The
`fetch_risk_detail` in the POST response uses
`linked_controls_view()` from Ship 14'.c to expand refs into
role-tagged entries. Live smoke test verified program +
extension refs render side-by-side.

**2. Parallel CaseFile view?**

Not applicable — write-layer only. No chat surfaces touched.

**3. Deterministic routing?**

Not applicable — no LLM calls, no classifier changes.

**4. Guidance-normative discipline?**

Preserved — endpoints operate on schema_v2 + schema_v87
columns. No engine mutations. Payloads validated against the
schema's own CHECK constraints (treatment_option enum,
likelihood/impact integer ranges).

## What did NOT ship

- **External write endpoints** — `POST /api/external/v1/risks`
  under a new `external:risks:write` scope. Deferred until
  a real partner (SIEM / GRC platform) asks. Adding partner
  write surface expands the attack blast radius; conservative
  default is read-only externally.
- **Bulk create endpoint** (`POST /api/v1/tenant/risks:batch`)
  — deferred. The canonical xlsx template + workbook importer
  handle bulk today; a JSON batch endpoint would duplicate
  that pathway.
- **State-transition validation** — currently PATCH accepts
  any legal `treatment_status`. A stricter transition model
  (e.g. `open → in_progress → implemented` one-way) could
  land in a future arc if compliance auditors flag it.
- **Restore endpoint** for soft-deleted rows — deferred;
  restore is a superuser DB operation for now.

## Ship 15 progress

| Sub-arc | Status |
|---|---|
| **15'.a POST + PATCH + DELETE + emit_risk_added** | **✓ (this doc)** |
| 15'.b Workbook importer INSERT detection + producer | next |
| 15'.c Notification UI drill-in for 4 risk kinds | pending |
| 15'.d DEMONSTRATES traversal + SDK typed methods | pending |
| 15'.e Eval cases + arc retrospective | pending |

## Related

- [[ship-14-prime-c-risk-register-api-2026-07-22]] — the 7
  read endpoints this arc extends with 3 write endpoints
- [[ship-14-prime-f-risk-notifications-2026-07-22]] —
  `emit_risk_added` producer this arc wires
- [[ship-4-prime-arc-retrospective-2026-07-18]] — external
  API discipline (external write scopes require conservative
  motivation)
- Ship 15'.b: workbook importer INSERT-detection for bulk-
  uploaded risks
