---
name: ship-15-prime-arc-retrospective-2026-07-22
description: "Ship 15' arc retrospective — Risk Register polish + close-out; 4 delivery sub-arcs + closer; closed all Ship 14'.g deferred items"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 15' arc — Risk Register polish + close-out. Closed every
deferred item from Ship 14'.g in a focused polish arc: write
endpoints + importer INSERT wiring + notification UI drill-in +
DEMONSTRATES traversal + SDK typed methods.

**Arc window:** 2026-07-22. 4 delivery sub-arcs + this closer,
single-session.

## Sub-arc inventory

| Sub-arc | Delivery | Commit |
|---|---|---|
| 15'.a | POST + PATCH + DELETE endpoints + emit_risk_added wire-up | `785d413` |
| 15'.b | Workbook importer INSERT detection (xmax trick) + producer wire-up | `9ec026e` |
| 15'.c | Notification inbox UI drill-in for 4 risk kinds (label + icon + deep-link) | `7cd5c76` |
| 15'.d | DEMONSTRATES traversal on obligation-linked drill-in + Python SDK typed methods | `8548eb7` |
| **15'.e Arc retrospective** | **This doc** | (next commit) |

## What ships from Ship 15'

**API (3 new internal endpoints):**
- `POST /api/v1/tenant/risks` — create; 409 on duplicate
- `PATCH /api/v1/tenant/risks/{id}` — partial update; external_ref
  immutable
- `DELETE /api/v1/tenant/risks/{id}` — soft-delete via
  is_active=FALSE + deletion_reason

**Modules extended:**
- `rag/risk/queries.py` — `RiskCreate` + `RiskPatch` + 3 helpers +
  `DuplicateRiskError`
- `db/workbook_importer.py` — `_upsert_risk()` with xmax trick +
  post-commit notification pass
- `static/arioncomply.html` — 4 notification kinds humanized +
  data-focus-entity + auto-open drill-in + DEMONSTRATES panel per
  obligation
- `sdk/python/arioncomply/` — 6 new models + 3 new Client methods

**Producers wired:**
- POST endpoint fires `emit_risk_added` on create (silent-fail)
- Workbook importer fires `emit_risk_added` for genuinely-new
  rows only (xmax = 0)

**UI capabilities added:**
- Notification click → risks mode → scroll+flash matching row →
  drill-in panel auto-opens with full treatment plan
- Drill-in surfaces DEMONSTRATES lineage per obligation-linked
  control (program + extension demonstrators together)

**Eval baseline:** stayed at **231/232 PASS + 1 WARN + 0 FAIL**.
Ship 15 didn't touch the chat pipeline — no new cases added
(see lesson 5 below).

## Codified lessons

### 1. Focused polish arcs preserve primary-arc landings

Ship 14' closed with 6+ deferred items (Ship 14'.g). Rather
than jamming them back into a hypothetical Ship 14''.a
follow-up, Ship 15 took each explicit deferral and delivered
it. Result: Ship 14's retrospective claims stayed accurate
(6 sub-arcs shipped, 6 items deferred), and Ship 15's memo
inventories exactly what got closed.

**Generalisation:** when a large arc closes with a substantial
deferral list, a focused close-out arc is cleaner than
re-opening the primary. The primary retro stays truthful; the
close-out gets its own memo.

### 2. `xmax = 0` is the right INSERT-vs-UPDATE detection for UPSERT flows

Ship 14'.g deferred `emit_risk_added` in the workbook importer
citing "invasive INSERT-detection" — the concern was that
distinguishing new rows from UPDATED rows during an UPSERT
required either a separate SELECT (race-prone) or restructuring
the UPSERT path entirely.

Ship 15'.b closed it in ~40 LOC using
`RETURNING (xmax = 0) AS was_inserted`. Postgres populates
`xmax` on the UPDATE side of ON CONFLICT DO UPDATE with the
transaction id; on the pure-INSERT path it stays 0. Deterministic,
race-free, no schema addition.

**Generalisation:** for UPSERT patterns that need
side-effects only on the INSERT path, use `RETURNING (xmax = 0)`
before falling back to more invasive restructuring.

### 3. Framework-role-model endpoints get re-used across surfaces

Ship 4a's `/api/v1/dashboard/control/{ref}/demonstrated-by`
was originally built for the posture drill-in. Ship 15'.d
re-uses it verbatim for the risk drill-in — same endpoint,
same helper function (`renderDemonstratedByPanel`), same
silent-fail convention. Zero new backend code needed for
Part 1 of 15'.d.

**Generalisation:** when adding a new drill-in that overlaps
with an existing one's controls surface, look for existing
framework-role-model endpoints before writing new ones.
`demonstrated-by` scales linearly across product surfaces.

### 4. Conservative external-write default has been the right call

Ship 15'.a punted external write endpoints
(`POST /api/external/v1/risks` under `external:risks:write`)
citing partner-attack-surface concerns. Ship 15'.d re-affirmed
this by keeping the SDK read-only. The Ship 4' external
discipline stays intact: partners consume, tenants write.

If/when a real partner (SIEM / GRC platform) requests write
capability, opening that surface will be a well-motivated
follow-up arc — not a speculative expansion.

**Generalisation:** deferring write-side external endpoints
by policy (not oversight) means each future addition needs
a real caller. Prevents scope creep at the perimeter.

### 5. Eval-suite additions belong on chat-pipeline changes, not HTTP/UI/SDK layers

Ship 15'.e deliberately did NOT add new eval cases. Rationale:
none of the Ship 15 sub-arcs modified the chat pipeline. The
existing #225-227 cases (Ship 14'.g) still lock the chat
posture_risk routing; adding cases that hit
`POST /api/v1/tenant/risks` from the eval suite would exercise
the write endpoint but not verify anything about answer
quality.

**Generalisation:** eval-suite ratchet fires on pipelines that
produce LLM answers. HTTP endpoints, UI surfaces, importer
paths, SDK methods — these are unit-testable but not eval-
testable. Don't inflate the case count for coverage
appearance; inflate it when a chat contract needs locking.

## Ship 15' close

| Sub-arc | Status |
|---|---|
| 15'.a POST + PATCH + DELETE + emit_risk_added | ✓ |
| 15'.b Workbook importer INSERT detection + producer | ✓ |
| 15'.c Notification UI drill-in for 4 risk kinds | ✓ |
| 15'.d DEMONSTRATES traversal + SDK typed methods | ✓ |
| **15'.e Arc retrospective** | **✓ (this doc)** |

Total: 4 delivery sub-arcs + closer. Smallest arc since Ship
8' (2 sub-arcs + 1 dropped) — reflects the focused-close-out
scope; every sub-arc closed a specific Ship 14'.g deferral.

## Ship 14 + Ship 15 combined — Risk Register is done

The full Risk Register product feature is now complete:

- Data model + template + workbook importer + 5 27005 §8.6.1
  columns (Ship 14'.b)
- 7 read endpoints (Ship 14'.c)
- 3 write endpoints (Ship 15'.a)
- Dashboard: 4 tiles + heatmap + drill-in + notification badge
  (Ship 14'.d + Ship 14'.e nav badge)
- Chat: POSTURE_RISK question_type + case-file discipline +
  preservation-check + short-circuit (Ship 14'.e)
- Notifications: 4 kinds + sweep + write-path + inbox UI +
  deep-link + auto-open drill-in (Ship 14'.f + Ship 15'.c)
- DEMONSTRATES traversal on obligation-linked drill-ins
  (Ship 15'.d)
- Python SDK typed methods for the 3 read endpoints (Ship 15'.d)
- 3 eval cases locking posture_risk routing (Ship 14'.g)

**Baseline: 231/232 PASS + 1 WARN + 0 FAIL** (highest in
project history, unchanged from Ship 14'.g close).

## Deferred to future arcs (both from 14'.g + new)

- **External write endpoints** (`external:risks:write` scope +
  `POST /api/external/v1/risks`) — waits for a real partner ask
- **Async SDK client** — sync-only for now
- **Chroma retrieval of risk text** — semantic search on
  threat/vulnerability descriptions ("supply chain risks", etc.)
- **State-transition validation** on PATCH (e.g. `open →
  in_progress → implemented` one-way)
- **Restore endpoint for soft-deleted rows** — superuser-only
  for now
- **Bulk-create endpoint** (JSON batch POST) — workbook path
  covers this today
- **Risk automation** — auto-classification of threats,
  auto-scoring, NIST NVD / MITRE integration. Explicit product
  policy per human-in-the-loop-positioning memo: humans decide.
- **DEMONSTRATES panel on top-5 / full-list rows** (currently
  only on drill-in)
- **Client-side filters / sort / bulk actions** on the full
  list table
- **Live toast on new-risk-added event** — no websocket/SSE
  channel exists in the app
- **Filter-by-kind UI** in the notification inbox — API
  supports it; inbox doesn't wire it yet

## Related

- [[ship-14-prime-arc-retrospective-2026-07-22]] — the parent
  arc whose deferral list this arc closes
- [[framework-role-model-arc]] Phase 4a — the demonstrated-by
  pattern Ship 15'.d re-uses
- [[ship-4-prime-g-docs-sdk-key-mgmt-2026-07-18]] — the SDK
  pattern Ship 15'.d extends
- Ship 16+ candidates: new-framework enrollment (SOC 2 / NIS2
  / DORA / HIPAA); fingerprint token discipline (Ship 11
  follow-up); SHOULD-promotion review batch (Ship 13 follow-up);
  Chroma retrieval integration
