---
name: ship-15-prime-b-importer-insert-wiring-2026-07-22
description: "Ship 15'.b — workbook importer INSERT detection via Postgres xmax trick; new bulk-uploaded risks fire risk_added notification; UPSERT updates don't re-fire"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 15'.b (2026-07-22) — second sub-arc of Ship 15. Closes the
`emit_risk_added` wire-up loop that Ship 14'.f left open. The
POST endpoint from Ship 15'.a already fires notifications on
create; this sub-arc extends the same behaviour to the
canonical-template bulk-upload path.

## What ships

### `_upsert_risk()` helper in `db/workbook_importer.py`

New method that mirrors the generic `_upsert()` but returns
whether the row was newly INSERTed vs UPDATEd. Uses the
Postgres `RETURNING (xmax = 0) AS was_inserted` trick — on
INSERT `xmax = 0`, on UPDATE `xmax` is the transaction id of
the updater. Deterministic; no separate SELECT needed.

### `_write_rows()` branches on `risks` table

- Non-`risks` tables → unchanged path (`_upsert()` / `_upsert_audit()`
  / `_upsert_incident()`)
- `risks` table → uses `_upsert_risk()` and collects
  `(external_ref, threat)` tuples for genuinely-new rows
- Post-commit — iterate the collected new-row list + call
  `emit_risk_added()` (Ship 14'.f producer) once per new row

Notification insert happens AFTER the risks-table commit so a
failed notification write can never roll back the risk import.
Silent-fail per the `emit_risk_added` contract; failures never
affect the workbook import status.

## Verification (end-to-end round-trip)

Synthetic 2-row workbook: `R-15B-NEW` (never seen) +
`R001` (already exists on the demo tenant).

Importer processed both:
- 2 rows mapped for insert
- Only 1 `risk_added` notification fired — for `R-15B-NEW`
- `R001` UPSERT touched the existing row but did NOT re-fire
  the notification (xmax != 0 on the update path)

Verifies the exact contract:
- new rows → notification
- existing rows → silent update
- workbook re-uploads don't spam the inbox

State cleanup performed after test.

## Ship 14'.a addendum alignment

**1. Role split?**

N/A — bulk-import path; no chat surface. `control_refs` in the
inserted rows are already merged into a single array by
`RowMappers.risk_treatment` (Ship 14'.b) without primary/xfw
split. Notification body doesn't reference specific controls.

**2. Parallel CaseFile view?**

N/A — write-layer path only.

**3. Deterministic routing?**

Yes — `xmax = 0` is a deterministic SQL-level check. No LLM
inference of "is this new?".

**4. Guidance-normative discipline?**

Preserved — importer operates on schema columns. No engine
mutations. Notification bodies cite 27005 §8.6.1 as authority
(via `emit_risk_added` prose) but don't add MUSTs.

## What did NOT ship

- **Threshold-based sweep trigger** — the periodic
  `sweep_risk_register_notify` handles ongoing state changes
  (residual crossing 15, review dates approaching); this
  sub-arc adds ONLY the `risk_added` write-path producer to
  the bulk-import path. State transitions in the bulk-import
  path (e.g. residual bumped from 10 → 20 via workbook
  re-upload) are picked up by the periodic sweep, not fired
  immediately by the importer.
- **POST-endpoint side of `risk_added`** — already shipped
  in Ship 15'.a; not touched here.

## Ship 15 progress

| Sub-arc | Status |
|---|---|
| 15'.a POST + PATCH + DELETE + emit_risk_added | ✓ |
| **15'.b Workbook importer INSERT detection + producer** | **✓ (this doc)** |
| 15'.c Notification UI drill-in for 4 risk kinds | next |
| 15'.d DEMONSTRATES traversal + SDK typed methods | pending |
| 15'.e Eval cases + arc retrospective | pending |

## Related

- [[ship-14-prime-f-risk-notifications-2026-07-22]] —
  `emit_risk_added` producer this sub-arc wires
- [[ship-14-prime-b-risk-register-schema-template-2026-07-22]]
  — the canonical xlsx template + `RowMappers.risks` this
  sub-arc extends
- [[ship-15-prime-a-risk-write-endpoints-2026-07-22]] —
  POST-endpoint side of `risk_added` (already wired)
- Ship 15'.c: notification UI drill-in for the 4 risk kinds
