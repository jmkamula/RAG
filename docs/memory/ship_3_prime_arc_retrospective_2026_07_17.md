---
name: ship-3-prime-arc-retrospective-2026-07-17
description: "Ship 3' arc retrospective — 13 sub-arcs (a→m) building the notification pipeline end-to-end + closing legacy data quality"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 3' arc — start-to-finish log of what got built, why, and
what future work should know before touching this area.

**Arc window:** 2026-07-17 (single day, 13 sub-arcs).

**Entry point for future work:** read this first if you're
touching anything notification-shaped.

## Motivation

Coming out of Ship 2' (2026-07-15/16), the case-file digest arc
was closed, ID discipline was in, and the LLM prompt-token
average was down 17×. Ship 3' pivoted from chat-pipeline
plumbing to operational infrastructure — the sweep scheduler,
notification pipeline, and delivery workers that let the app
actually TELL tenants when something needed their attention.

## Sub-arc inventory (with wins)

| Sub-arc | What | Key win |
|---|---|---|
| 3'.a | Productionize sweep scheduler | systemd timer installer, `rag/scheduler/tick.py` alive on 30-min cadence |
| 3'.b | Real `freshness_expiry` producer | Comply postures past leaf freshness_days notify tenants |
| 3'.c | `nc_surfaced` + `upload_processed` | Write-path notifications from `_log_status_change` + `write_findings` |
| 3'.d | Channel-config UI | Tenant-facing surface to add/edit/delete email/slack channels + RLS `app_*_all` policies |
| 3'.e | `stage2_proposal_ready` + `upload_failed` | Two silent-failure gaps closed |
| 3'.f | `overdue_followups` real backstop | Replaced counting stub with real per-tenant sweep over expected_followup_event + triggered_implication |
| 3'.g | `cite_verification_overdue` | Cite-mode auditor-critical backstop |
| 3'.h | Inbox per-kind rendering | Humanized labels + Tabler icons + one-click "Open X" deep-links (mode-level) |
| 3'.i | `posture_flip_to_comply` + `api_key_expiring` | Producer inventory COMPLETE at 13 kinds |
| 3'.j | Delivery worker integration tests | First integration test suite in repo; SMTP + Slack monkey-patched, end-to-end verified |
| schema_v76 | RLS + GRANT parity fix | Post-Ship 3'.j audit; aligned 6 tables where `USING (true)` didn't match GRANTs |
| 3'.k | `notification_retention` sweep | Age-out rules close unbounded-inbox gap |
| 3'.l | ISO 27001:2013→2022 renumber | Data-quality pivot; 16 misprefixed refs fixed in gdpr_nodes_phase2.json + 1 in doc_mapping YAML |
| 3'.m | Cleanup close-out | Inbox per-row focus (Ship 3'.h deferred UX) + docstring cleanup + this retrospective |

## Producer inventory FINAL — 13 kinds

Cross-write-path (5 kinds — fire from cascade engine + posture writer):
- `implication_overdue` (cascade engine, write-path)
- `followup_overdue` (cascade engine, write-path)
- `threshold_crossed` (cascade engine, write-path)
- `cascade_blocked` (cascade engine, write-path)
- `auto_resolved` (cascade engine, write-path)

Write-path producers (5 kinds):
- `nc_surfaced` (`posture_writer._log_status_change` — Ship 3'.c)
- `upload_processed` (`posture_writer.write_findings` — Ship 3'.c)
- `stage2_proposal_ready` (`posture_loader._persist_engine_proposals` — Ship 3'.e)
- `upload_failed` (`doc_pipeline` exception handler — Ship 3'.e)
- `posture_flip_to_comply` (`posture_writer._log_status_change` — Ship 3'.i)

Sweep producers (3 kinds):
- `freshness_expiry` (Ship 3'.b)
- `cite_verification_overdue` (Ship 3'.g)
- `api_key_expiring` (Ship 3'.i)

Sweep backstops for write-path (1 kind — same kind as write-path):
- `overdue_followups` sweep for expected_followup_event + triggered_implication (Ship 3'.f)

## Test suite growth

Ship 3' contributed **42 tests across 3 files** to the notification
arc alone:
- `tests/test_notification_producers.py` — 28 producer tests (source-read + monkey-patched)
- `tests/test_notification_delivery.py` — 7 integration tests (throwaway tenant + SMTP/Slack patches)
- `tests/test_notification_retention.py` — 7 integration tests (age-out rules + attempt cleanup)

Plus baseline eval 207/208 PASS + 1 WARN + 0 FAIL held through every sub-arc.

## Sweep tick — 7 work_types

Runs every 30 min via `arioncomply-sweep.timer`:
- `fact_recompute`
- `overdue_followups` (backstop for cascade write-path)
- `freshness_expiry`
- `cite_verification_overdue`
- `api_key_expiring`
- `notification_delivery` (SMTP + Slack via `rag/notifications/deliver.py`)
- `notification_retention` (age-out)

Every tick writes a `sweep_log` row per work_type. Cross-tenant
maintenance sweeps use permissive `app_*_all ... USING (true)`
RLS policies alongside their per-tenant `tenant_isolation`
policies — arioncomply_app sees all rows for maintenance, tenant
callers still get scoped.

## Retrospectively-valuable lessons (feedback memories)

- [[feedback-rls-grant-parity]] — RLS `USING (true)` doesn't
  imply GRANT parity. Audit both when giving arioncomply_app
  cross-tenant access. schema_v76 aligned 6 tables surfaced by
  audit after Ship 3'.j fixture cleanup silently failed.

- [[feedback-posture-test-state-cleanup]] — Manual UPDATEs on
  posture_controls for smoke tests must restore BOTH `finding`
  AND `confirmation_status`. Guard trigger blocks some
  transitions; use trigger-bypass pattern. Discovered during
  A.5.9 restore after Ship 3'.b smoke test.

## Frontend surfaces

- Inbox mode: renders 13 kinds with humanized labels + Tabler
  icons + per-kind deep-link to target mode
  (`_NOTIF_KIND_LABEL` + `_NOTIF_KIND_META` in
  `static/arioncomply.html`)
- Per-row focus: click "Open X" → target mode's loader
  scroll+flash the matching row via
  `window._notifTarget` + `_applyNotifFocus()` (dashboard heatmap,
  queue Stage-1 + Stage-2 cards, cascade timeline rows)
- Profile mode: channel-config UI (Ship 3'.d) for adding/editing
  /deleting email + slack destinations

## Schemas landed in this arc

- v65 — `sweep_log` table + registered work_types (Wave 3b, pre-3')
- v66 — `tenant_notification_channel` + `notification_delivery_attempt` (pre-3')
- v67 — cascade producers pre-3'
- v68 — chat_casefile_log (Ship 2')
- v69 — `freshness_expiry` in tenant_notification_kind_check (Ship 3'.b)
- v70 — `nc_surfaced`, `upload_processed` kinds + `app_*_all` RLS policies (Ship 3'.c)
- v71 — `stage2_proposal_ready` + `upload_failed` kinds (Ship 3'.e)
- v72 — RLS grants for `expected_followup_event` + `triggered_implication` (Ship 3'.f)
- v73 — `cite_verification_overdue` kind + sweep + RLS (Ship 3'.g)
- v74 — `posture_flip_to_comply` + `api_key_expiring` kinds (Ship 3'.i)
- v75 — DELETE grants on tenant_notification + notification_delivery_attempt (Ship 3'.j)
- v76 — RLS + GRANT parity across 6 legitimate DELETE candidates (post-3'.j audit)
- v77 — `notification_retention` work_type (Ship 3'.k)

## What's next (not in scope)

Real remaining candidates for a follow-up arc:
- Notification preferences UI (per-kind mute, severity threshold customization)
- Notification metrics / observability dashboard
- Docs mode focus (Ship 3'.m stopped short of teaching this loader — upload rows would need data-focus-entity)
- Fresh Ship 4 arc — pivot to something else entirely

Two long-standing eval-case TODOs remain (CLAUDE.md lines
1009-1011): incident obligations chat surface eval + GDPR Art.25
DPbD DerivedSpec eval. Neither is Ship 3' scope.

## Related — sub-arc memories

- [[ship-3-prime-a-sweep-scheduler-2026-07-17]] — details on the tick + timer
- [[ship-3-prime-e-notification-producers-2026-07-17]] — Ship 3'.e implementation notes
- [[ship-3-prime-i-final-producers-2026-07-17]] — producer inventory close-out
- [[ship-3-prime-j-delivery-integration-tests-2026-07-17]] — first integration test suite
- [[ship-3-prime-l-iso27001-2013-renumber-2026-07-17]] — data-quality pivot

## Also read

- [[ship-2-prime-retrospective-2026-07-17]] — arc that precedes this one
