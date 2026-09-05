---
name: ship-118-prime-arc-retrospective-2026-09-05
description: Ship 118' arc — point-in-time posture reconstruction with breach-narrative artifact
metadata:
  type: project
---

# Ship 118' — point-in-time posture reconstruction

**Date:** 2026-09-05
**Commits:** `778d7dcc` (a) → `2c8d9dfb` (b) → this doc (c)
**Trigger:** operator question during architecture-doc review — "are we able to reconstruct posture as of a date? we should have it as a first-class query/export ('show me our posture on 14 March'). It's the single most compelling artifact for the breach narrative."

## Motivation

An audit or regulatory investigation triggered by an incident asks a specific question: **what did you know about your compliance posture on the day the incident occurred?** A repository that only shows current state cannot answer this — the answer becomes a forensic project of git-blaming through the codebase, cross-referencing commit dates with change logs, and hoping nothing important got mutated in place.

ArionComply's storage already had the raw material (posture_assertions supersession trail from Ship 59'.b, document_findings lifecycle timestamps, cascade_triggered_implication append-only log) but no first-class query layer to compose them into a point-in-time snapshot. Ship 118' delivers that layer, closes the two audit-gap tables that were missing, and adds a print-optimised HTML output the auditor can save-as-PDF from any browser.

## Delivery summary

### 118'.a — snapshot function + admin endpoint (`778d7dcc`)

`rag/posture/snapshot.py`:
- `snapshot_posture(pg_conn, tenant_id, as_of=None)` → `PostureSnapshot`
- Reconstructs per-control state from three already-tracked sources:
  - Finding + reason + source + set_at ← `posture_assertions` supersession trail
  - Evidence linked ← `document_findings` lifecycle timestamps (Ship 118'.a decision A2 includes `expires_at` guard so stale evidence doesn't appear on historical snapshots)
  - Cascade follow-ups open on date ← `triggered_implication` (fired_at + resolved_at)
- `coverage_notes` field per axis: `full` when reconstructible from log, `current-only` with tracking-start date explanation when not
- `snapshot_to_dict` (JSON), `snapshot_to_csv` (auditor spreadsheet) serialisers

New endpoint: `GET /api/v1/admin/posture-snapshot?as_of=YYYY-MM-DD&fmt=json|csv`. Requires api key; RLS-scoped via `set_session`.

Verified on Arion demo across five dates: the curation ramp (May→August) is clearly visible in the finding counts (Jan: all Not-assessed → May: 62 NC → Aug: 162 NC). Full snapshot with 3055 evidence rows returns in ~200 ms.

### 118'.b — audit tables for applicability + scoping (`2c8d9dfb`)

`schema_v115` — two new append-only tables:

**applicability_status_log**: one row per `(tenant, standard, control)` status/reason change. Fields: `status_before`, `status_after`, `reason_before`, `reason_after`, `rule_id` (from `RULES` registry), `change_source`, `changed_at`, `changed_by`. Matches `posture_status_log`'s compliance-load-bearing shape from Ship 4'.b addendum: FK `ON DELETE NO ACTION`, SELECT+INSERT to app role only, UPDATE+DELETE revoked.

**client_facts_log**: one row per `(tenant, column)` fact change. Fields: `column_name`, `value_before`, `value_after` (text-rendered), `source_before`, `source_after`, `change_source` enum (`user_put` / `quickstart_init` / `backfill_script` / `admin` / `derivation`), `changed_at`, `changed_by`. Same RLS + grants shape.

Writers wired in three places:
- `rag/scoping/applicability.py::_clear_derived_na` + `_apply_rule`: two-step SELECT-then-UPDATE captures prior state, logs one row per changed control with `rule_id` extracted from the `[rule_id] ...` reason prefix convention.
- `rag/onboarding/quickstart.py::create_first_tenant`: logs each initial fact with `change_source='quickstart_init'`.
- `api_server.py` PUT `/api/v1/tenant/facts`: logs one row per changed column with delta detection (idempotent PUTs produce no log).

Snapshot updated to read `applicability_status_log` when `as_of >= APPLICABILITY_TRACKING_BEGAN` (2026-09-05). For older dates: gracefully falls back to `posture_controls` current-state and reports `coverage: current-only` with tracking-start explanation.

Verified end-to-end on Arion: sweep wrote 28 log rows (14 clears + 14 sets, all with correct rule_id). Test PUT round-trip on `automated_decision_making` logged both directions correctly. Snapshot now reports `applicability: full` with "Full reconstruction from log."

### 118'.c — print-optimised HTML export (this)

`rag/posture/snapshot.py::snapshot_to_html(snap, snapshot_id)` — self-contained HTML with:

- **Cover header** — tenant name, as-of date, generation timestamp, snapshot UUID
- **Date picker** — `<input type=date>` that reloads the page with new `?as_of=` (hidden in print via `@media print { .picker-bar { display: none } }`)
- **8-card summary grid** — total / NC / OFI / Comply / N/A-scope / Not-assessed / evidence rows / open follow-ups. Each card colour-coded.
- **Coverage notes panel** — per-axis coverage report (green "full" vs amber "current-only") from `snapshot.coverage_notes`
- **Per-framework tables** — one `<section>` per standard with control ref + verdict pill + reason. Sorted by control_ref.
- **Data-protection footer** — retention statement, "not a certification", audit-context note (matches the auditor-ledger design principles established in the design conversation)
- **Watermark** — tenant name + snapshot UUID on every page (`position: fixed`, includes `@media print` rule)

Print CSS uses `@media print` for page breaks between framework sections, hides the interactive picker bar, and repositions the watermark for A4/US-Letter pages.

New endpoint variant: `GET /api/v1/admin/posture-snapshot?fmt=html` — text/html response, no attachment header (auditor opens in browser, uses Save-as-PDF from browser menu).

Design decision: **HTML + browser Save-as-PDF rather than server-side PDF**. Zero new server dependencies (no weasyprint, no reportlab, no pandoc). More accessible (screen readers, resize, copy-paste). URL-shareable. Every modern browser supports high-fidelity print-to-PDF. When we eventually need a server-side PDF option (e.g. for API-driven auditor delivery without human-in-the-loop), we can add it as a new `fmt=pdf` without changing the HTML endpoint.

Verified end-to-end on Arion: HTML output is 133 KB, all 3 frameworks rendered as separate sections, 16 summary cards, 8 coverage-notes rows, 159 NC pills + 21 na-scope pills, 3 watermark instances. Past-date query renders `cov-partial` styling on the applicability coverage row + correct current-only note.

`scripts/ops/ship-118-poc-update.sh` follows Ship 113'.d convention. install.sh → API restart → optional derive-applicability sweep to populate the log → verification of both audit tables + snapshot health.

## Lessons codified

### Lesson 211 — Point-in-time is a property of the storage layer, not a feature

We didn't have to add new stores to answer "what was our posture on 14 March?" — the raw data was already time-tracked in `posture_assertions` (supersession-tracked since Ship 59'.b), `document_findings` (lifecycle timestamps since intake landed), and `triggered_implication` (append-only since Ship 40). The gap was the *query layer* that composed them, not the storage. When storage decisions are made with time-fidelity in mind up front, the reporting layer can be added later without data migrations. Two axes we hadn't tracked (applicability + scoping) needed new tables; the rest was pure query composition.

### Lesson 212 — Honest coverage_notes beat inflated capabilities

The snapshot response has a `coverage_notes` block that explicitly says which axes are fully-reconstructible-from-log and which are current-only fallbacks. When a customer or auditor loads a pre-Ship-118'.b snapshot, they see "applicability: current-only — historical tracking begins 2026-09-05" rather than a silent misrepresentation. This is the auditor-defensibility discipline: a document that overstates what it can prove is worse than one that clearly bounds its claims.

### Lesson 213 — Two-step SELECT-then-UPDATE beats RETURNING for audit trails

PostgreSQL `RETURNING` returns NEW values after an UPDATE — useful for chaining, useless for logging OLD values. The two-step SELECT-then-UPDATE pattern in `_clear_derived_na` and `_apply_rule` gives us the prior state we need to log. Slightly more verbose SQL, dramatically more useful audit trail.

### Lesson 214 — Print-optimised HTML replaces a server-side PDF dependency

For MVP scale (single-tenant PoCs, single-auditor workflows), a print-optimised HTML endpoint that leverages the browser's native PDF export is functionally equivalent to a server-side PDF renderer, with zero new dependencies + better accessibility + URL-shareability. Save server-side PDF for when the delivery model demands automated PDF generation (e.g. scheduled reports, no-human-in-the-loop delivery to auditor).

### Lesson 215 — Idempotent writes with delta detection keep the log honest

Every log writer in Ship 118'.b checks whether the change is actually a change before writing a log row. Re-firing an applicability rule that produces the same status + same reason writes nothing to `applicability_status_log`. PUT-ing the same fact value with the same declared source writes nothing to `client_facts_log`. The log records semantic changes, not writes. This keeps the log small + the audit trail readable — no forensic archaeology needed to distinguish "the state actually changed" from "someone re-clicked the button."

## Related arcs

- [[ship-59-prime-arc-2026-08-11]] — `posture_assertions` supersession trail; the load-bearing prerequisite for Ship 118'.a's finding reconstruction
- [[ship-4-prime-b-addendum-audit-log-correction-2026-07-17]] — `posture_status_log` classification pattern this arc's `applicability_status_log` matches
- [[ship-110-prime-arc-retrospective-2026-09-03]] — applicability engine + rule_id convention this arc leans on for log entries
- [[ship-117-prime-arc]] — architecture doc; the trigger for the point-in-time question

## Deferred to Ship 119'+

1. **Auditor's ledger (aggregate compilation)** — Ship 119' as previously scoped. Now unblocked by Ship 118'. The revised 4-arc plan with PII redaction module + scope-acknowledgement flow + PDF renderer.
2. **Server-side PDF option** — if a customer requests programmatic PDF delivery. Would use weasyprint or wkhtmltopdf.
3. **UI date-picker on the main dashboard** — currently only the standalone HTML view has one. Adding to the tenant-facing dashboard means a substantial React-like state refactor; deferred until proven demand.
4. **Automated snapshot at incident close** — when a tenant marks an incident closed, auto-generate + store the point-in-time snapshot as-of the incident date for future reference.
5. **Cascade follow-up detail in snapshot** — currently the snapshot shows a count of open follow-ups per control; a future revision could inline the follow-up specifics for controls where it matters.

## PoC deployment plan

`scripts/ops/ship-118-poc-update.sh` follows Ship 113'.d convention. From operator's Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-118-poc-update.sh
'
```

Expected result: schema_v115 applied idempotently; API restarted; sweep triggers first log rows; verification confirms both audit tables + snapshot health.

To try the HTML view from the operator's Mac after deploy:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 -L 8080:127.0.0.1:8080 arionops@10.0.1.85
# then in browser:
# http://localhost:8080/api/v1/admin/posture-snapshot?fmt=html
# (needs the admin api key)
```
