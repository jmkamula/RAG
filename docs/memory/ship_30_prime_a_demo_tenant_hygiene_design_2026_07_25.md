---
name: ship-30-prime-a-demo-tenant-hygiene-design-2026-07-25
description: "Ship 30'.a — design memo for demo-tenant queue hygiene. Sweep 102 measurement-run residue + confirm 2 DRAFT postures + add a shared hygiene helper so future Ship arcs' measurement scripts don't leave orphan queue debris on the production demo tenant"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 30'.a — opens Ship 30 arc (demo tenant queue hygiene). Direct
follow-on to a live user report: "42 items in the stage 1 intake
and yet I uploaded no documents. Some chat queries return DRAFT
not sure what this means." The investigation surfaced a recurring
structural loose end.

## What the investigation found

**42 controls / 102 pending findings in Stage-1 queue** on the demo
tenant `00000000-0000-0000-0000-000000000001` (Arion Networks),
all sharing `extracted_at=2026-07-21 07:46:44` — Ship 11'.e
measurement window.

Trace:
- 5 orphan `document_id`s in the findings — NOT in
  `document_uploads` but ARE in `client_documents` (the newer
  logical-document table).
- Filenames resolve to the 5 Ship-10-baseline docs (Data Quality
  Accuracy Procedure, DPIA, RoPA, Consent Management, Processor
  Operations).
- Inference source distribution: 45 `fingerprint_match` + 35
  `extracted` + 22 `xfw_bridge`. Went through the real
  `write_findings` path — not synthetic.
- Committed 2026-07-21 07:43:16 was Ship 11'.e's measurement
  checkpoint (`ca0f9bb`). Something in that window kicked full
  extractions on the demo tenant.

Candidates for the write:
- `scripts/critic_verifier_ab.py` — explicitly "runs on Arion by
  default" + "DOES clear existing findings on each sampled doc and
  re-extract them twice"
- `scripts/measure_ship11_reextraction.py` — docstring claims
  "Does NOT touch the DB — pure measurement", but the pipeline
  paths it invokes (fingerprint + xfw_proposer) DO write.

Either or both. Doesn't matter which — the loose end is
structural, not per-script.

**Also found**: 394 findings with `review_status='pending'` +
`is_active=FALSE` from prior sweeps. Soft-deletion by `is_active`
was correct (queue hides them) but `review_status` never flipped
to `'archived'`, so they show up in diagnostics + broader queries.
Cosmetic cleanup opportunity.

## The DRAFT question

User also asked why some chat queries return `[DRAFT]`. Ship 2'.j
attaches `[DRAFT]` to any assessed posture (NC/OFI/Comply) whose
`confirmation_status` is not in `{confirmed, overridden,
document_confirmed, engine_confirmed}`.

On Arion today: **only 2 postures** would trigger `[DRAFT]`:

| Control | Standard | Verdict | Status | Note |
|---|---|---|---|---|
| A.7.4.6 | ISO27701:2019 | NC | draft | Curator-seeded during 27701 enrollment |
| B.8.4.1 | ISO27701:2019 | NC | draft | Same finding (processor mirror) |

Both are "no systematic periodic sweep of temp files in
production infra". `posture_status_log` is empty for both — never
extraction-derived, never confirmed. Curator seeded them as NC
during 27701 Phase 2 (Ship 8'.b memo — "B.8 NC postures are
correct — no seed fix needed").

The 42 pending-queue controls are NOT the ones causing DRAFT — 39
of them are already `document_confirmed`; 3 are `engine_confirmed`.

## Root cause of the loose end (structural)

**8 dev scripts hardcode the Arion demo tenant UUID.** Every Ship
arc measurement / A/B / audit runs against the production demo,
leaving residue that no cleanup step ever removes:

```
scripts/test_intake_quality_endpoint.py
scripts/audit_finding_quality.py
scripts/stage1_queue_sweep.py           # write path — pre-existing sweep
scripts/run_leaf_scan.py                # write path
scripts/discover_workbook.py            # write path
scripts/measure_ship11_reextraction.py  # write path (contra docstring)
scripts/backfill_markdown_escapes.py    # update path
scripts/critic_verifier_ab.py           # write path (explicit)
```

There is no sandbox tenant. No cleanup contract. No convention
that says "measurement scripts must clean up their own residue."

## Ship 30 plan

### 30'.b — sweep + confirm + hygiene helper

**Sweep 102 measurement-run artifacts:**
- Soft-delete: `UPDATE document_findings SET is_active=FALSE,
  rejection_reason='orphan measurement-run artifact (Ship 11'.e
  residue) — cleared in Ship 30' WHERE ...`
- All 102 rows where tenant=demo AND extracted_at =
  '2026-07-21 07:46:44' AND review_status='pending' AND
  is_active=TRUE.

**Archive 394 dormant rows:**
- `UPDATE document_findings SET review_status='archived' WHERE
  tenant=demo AND review_status='pending' AND is_active=FALSE`
- Cosmetic — these were already soft-deleted, but the status
  never flipped. Cleans up diagnostic queries.
- Note: check `document_findings.review_status` CHECK constraint
  first — must include `'archived'` OR use existing terminal
  value.

**Confirm 2 DRAFT postures:**
- A.7.4.6 + B.8.4.1 on ISO 27701:2019 both flip from
  `confirmation_status='draft'` to `'document_confirmed'`.
- Rationale: they're curator-seeded NC verdicts the tenant
  accepts; no evidence to attach. Write `posture_status_log` row
  with `change_kind='confirmation'`, `source='ship_30_sweep'`.
- After the flip, chat `[DRAFT]` labels disappear on those refs.

**Hygiene helper for future Ship arcs:**
- New file: `scripts/dev/demo_tenant_cleanup.py`
- Exposes: `sweep_measurement_residue(since: datetime, dry_run:
  bool = True)` — walks pending findings written since `since`
  matching the "measurement run" pattern (all sharing an
  `extracted_at` timestamp within 1-hour window; no
  corresponding recent `document_uploads` entry).
- Retrofit: `critic_verifier_ab.py` + `measure_ship11_reextraction.py`
  call this in a `try/finally` at exit.
- Fix `measure_ship11_reextraction.py` docstring — either make it
  actually not write OR update the docstring to match reality.

### 30'.c — eval + retrospective

Eval regression check (should be no-op — Ship 30 is a data
sweep + operational hygiene, no runtime code paths touched).
Retro codifies the "measurement scripts must clean up after
themselves" convention.

## What Ship 30 does NOT do

- **Introduce a sandbox tenant** — bigger arc (tenant
  provisioning + fixture cloning + write-path migration). Deferred.
- **Retire either document table** — `document_uploads` +
  `client_documents` serve different purposes (raw ingress vs
  logical registry). Not a wart. Investigation confirmed.
- **Change `[DRAFT]` semantics** — the label is semantically
  correct for A.7.4.6/B.8.4.1 (unconfirmed NC seeds). The fix
  is to confirm them, not to change the label logic.
- **Auto-approve future measurement runs** — measurement scripts
  should CLEAN UP their residue on exit, not skip writing to the
  DB (writing is intentional for post-run diagnostics on
  intake_trace_log / ai_call_log).

## Design decisions locked in 30'.a

1. **Soft-delete over hard-delete** — preserves audit trail;
   `is_active=FALSE + rejection_reason` is the canonical Stage-1
   reject semantics (matches existing `stage1_queue_sweep.py`
   pattern for stale rows).

2. **`document_confirmed`, not `engine_confirmed`** for A.7.4.6 +
   B.8.4.1 — the confirmation source is a human sweep decision,
   not the engine. `engine_confirmed` implies engine derived the
   verdict from evidence, which isn't what happened here.

3. **Time-window match, not extracted_at exact match** — the
   hygiene helper detects "measurement run" by 1-hour cluster of
   findings sharing timestamps. Robust to minor jitter.

4. **Retrofit vs new fixtures** — retrofit existing scripts to
   call cleanup helper. Introducing a sandbox tenant is bigger
   than this arc justifies.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **30'.a** (this) | Investigation write-up + plan | Design locked |
| 30'.b | Sweep + confirm + hygiene helper | Queue clean; DRAFT gone; measurement scripts cleanup-aware |
| 30'.c | Eval + retrospective | Baseline holds; loose-end pattern codified |

## Related

- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc whose
  measurement runs left the 102-finding residue
- [[stage1-queue-sweep-2026-06-27]] — the earlier queue sweep
  (different scenario: catalog-refactor cleanup, not measurement-
  run cleanup)
- [[feedback-validate-set-membership]] — the 2026-06-27 sweep
  that soft-deleted 96 valid findings via a wrong catalog
  predicate; motivates conservative sweep semantics
