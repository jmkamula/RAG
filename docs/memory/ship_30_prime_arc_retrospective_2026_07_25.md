---
name: ship-30-prime-arc-retrospective-2026-07-25
description: "Ship 30' arc closer — demo tenant queue hygiene. Swept 102 measurement-run findings, archived 394 dormant rows, confirmed 2 DRAFT postures, and uncovered + fixed a cross-tenant bug in posture_loader that was making every assessed posture emit [NC-DRAFT] in chat regardless of actual confirmation state. Also codified a measurement-script cleanup contract via scripts/dev/demo_tenant_cleanup.py."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 30' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Started as a user-reported operational issue ("42
items in the intake queue and I uploaded no documents; chat says
DRAFT"), grew into (a) queue sweep + (b) confirmation-status
loader bug that had been silently affecting every tenant.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 30'.a | Design memo + investigation write-up | 70772b7 |
| 30'.b | Sweep + confirm + hygiene helper + posture_loader bug fix | 1ea16de |
| **30'.c** | **Eval + retrospective (this doc)** | pending |

## The user report → root cause chain

**User report** (verbatim): "there 42 items in the stage 1 intake
and yet i uploaded no documents. some chat queries return DRAFT
not sure what this means - can we go through and clear that queue?"

Investigation ladder:
1. **42 items in queue** → 42 distinct (control_ref, standard_id)
   groups; 102 total pending findings underneath.
2. **"I uploaded no documents"** → 5 orphan document_ids on the
   findings; NOT in `document_uploads` BUT present in
   `client_documents` (the newer canonical documents table).
   Filenames DO resolve — they're the 5 Ship-10-baseline docs
   (Data Quality Accuracy Procedure, DPIA, RoPA, Consent
   Management, Processor Operations).
3. **Where the findings came from** → `extracted_at` all fell
   within a 30-second window on 2026-07-21 07:46-47, three
   minutes after commit `ca0f9bb` (Ship 11'.e measurement
   checkpoint). `scripts/critic_verifier_ab.py` or
   `measure_ship11_reextraction.py` (docstring lies about being
   dry-run) ran the real extraction pipeline against the demo
   tenant during the Ship 11 measurement checkpoint.
4. **"DRAFT" in chat** → user's intuition surfaced a bigger bug.
   I initially said "only 2 postures trigger DRAFT" (correct
   as DB truth) but chat verification revealed EVERY assessed
   posture was emitting `[NC-DRAFT]` in chat regardless.
5. **Loader bug** →
   `rag/posture_loader.py::load_posture` SELECT never fetched
   `confirmation_status`. Every rec had it as None. Downstream
   `CaseFile.needs_draft_tag(ref)` returned True universally.

Root causes surfaced by the user's single sentence:
- **Operational** — Ship 11 measurement leaked 102 orphan
  findings; no cleanup contract for dev/measurement scripts
- **Cross-tenant** — every assessed posture on every tenant was
  labeled `[NC-DRAFT]` in chat since `posture_loader` shipped

## What Ship 30 delivered

### Data mutations (Arion demo)
- 102 measurement-run findings soft-deleted (Ship 11'.e residue)
- 394 dormant `is_active=FALSE + review_status='pending'` rows
  archived to `review_status='rejected'` (housekeeping)
- 2 draft postures (A.7.4.6 + B.8.4.1 ISO 27701 temp-file sweep)
  flipped to `confirmation_status='document_confirmed'`
- 2 `posture_status_log` acknowledgement rows for audit trail

### Code fixes
- `rag/posture_loader.py` — added `confirmation_status` to the
  SELECT. **Fixes the [NC-DRAFT] chat label surfacing bug on
  every tenant.**
- `rag/casefile/answer_schema.py::LLM_OUTPUT_RULES` — added
  explicit "use digest verdict tag verbatim" rule + a non-DRAFT
  example (B.8.4.1 as `[NC]`) so the LLM stops echoing `-DRAFT`
  from example memory when the digest tag doesn't include it.

### Measurement-script hygiene contract
- `scripts/dev/demo_tenant_cleanup.py` — new shared helper with
  `cleanup_measurement_residue(tenant_id, since, dry_run,
  reason)`. Bounded time-window sweep of pending findings a
  measurement script produced. Idempotent. Also runnable as CLI
  for ad-hoc cleanup.
- `scripts/measure_ship11_reextraction.py` — docstring corrected
  (was "Does NOT touch the DB — pure measurement", which was
  false); wrapped `main()` in `try/finally` calling the helper
- `scripts/critic_verifier_ab.py` — `try/finally` cleanup wired
  in `main()` alongside the existing `pg.close()`

## Codified 4 lessons

### 1. Data-model puzzles surface bigger bugs than the puzzle

The user's report was "42 items I didn't upload." The obvious fix
was to sweep the 102 findings. But investigating the "why does
chat say DRAFT" question surfaced that `posture_loader` had never
been fetching `confirmation_status` — the label was firing chat-
wide on every tenant since load_posture was written. If the user
had accepted "just sweep the queue" as an answer, this bug would
have kept shipping.

**Rule**: when a user reports something confusing, the loudest
answer is usually not the whole answer. Follow the "why does this
feel wrong to them" thread even after you've solved the surface
issue.

### 2. Docstrings that lie corrupt future arcs

`scripts/measure_ship11_reextraction.py` opened with "Does NOT
touch the DB — pure measurement." That was false. Three days
later ("today" for us) I trusted the docstring and had to trace
via git log + timestamp forensics to find the actual write path.
If the docstring had accurately said "writes findings via the
real pipeline; run demo_tenant_cleanup after," this investigation
would have been 5 minutes not 40.

**Rule**: when a script's docstring makes a claim about
side-effects, that claim is load-bearing for future debugging.
An inaccurate docstring is worse than no docstring — it actively
misdirects. Ship 30'.b corrected this docstring.

### 3. Confirmation state is a load-bearing tenant signal

The `confirmation_status` field on `posture_controls` distinguishes
"tenant has accepted this posture" from "engine derived this
verdict, awaiting review." The `[NC-DRAFT]` label surfaces this
distinction to the tenant — auditor-critical for showing which
findings the tenant has vs hasn't reviewed. Loader-blindness
meant EVERY posture read as DRAFT, quietly eroding the meaning
of the label.

**Rule**: when a database field carries a semantic signal that
downstream code checks (Python code doing `.get("field") not in
_ALLOWED`), the loader SELECT must fetch it. A missing field
silently becomes `None` and defaults to the "wrong" branch.
Consider a smoke test: query the loader, assert every expected
field is populated in a sample row.

### 4. Measurement-script residue is drift-by-construction (parallels Ship 29)

Ship 29 codified "multi-path-to-same-destination is drift-by-
construction" for generators. Ship 30 shows the same pattern for
measurement scripts writing to the production demo tenant: 8
scripts hardcode the Arion UUID, they run the real write path,
they leave residue because there's no cleanup contract.
Consolidation isn't the fix here (each script has a legitimate
distinct purpose); the fix is a **shared exit contract** — the
`demo_tenant_cleanup.py` helper called in `try/finally`.

**Rule**: when N scripts share a write surface and each is
individually justified, the fix is not consolidation but a shared
lifecycle contract. Give them a common `cleanup()` to call in
`finally`.

## Diagnosis note — pool-poisoning masked the arc

First eval run showed 230/1 FAIL/1 WARN (regression of 1 from Ship
29'.c baseline). The failing case (#5, "access rights NC") is
documented in CLAUDE.md as historically stochastic. Investigation
of a 3× repro showed all attempts producing EMPTY answers, not
noisy prose. API logs revealed
`psycopg.errors.AdminShutdown: terminating connection due to
administrator command` — the Postgres pool got poisoned mid-eval
by an external command (likely my sweep transaction earlier
holding a session unexpectedly). After API restart, case #5 ran
3/3 clean.

**Rule**: an eval failure with empty answers is not an LLM
regression — it's an infrastructure fault. Grep the API log for
DB errors before considering it a code issue.

## What Ship 30 did NOT do

- **Introduce a sandbox tenant** — bigger arc (tenant
  provisioning + fixture cloning + write-path migration for
  every dev script). Deferred to a future arc. The
  `demo_tenant_cleanup.py` helper is a lighter interim solution.
- **Retire `document_uploads` or `client_documents`** —
  investigation confirmed they serve different purposes (raw
  ingress vs logical registry). Both stay.
- **Change `[DRAFT]` label semantics** — the label is
  semantically correct. The bug was in the loader; the label
  now works as designed.
- **Audit other loader SELECTs** for missing semantic fields —
  worth considering but scope-creep for this arc. Follow-on
  candidate.
- **Backfill `posture_status_log` for prior draft→confirm
  flips** — no prior flips of the exact "curator-seeded NC
  accepted by tenant" shape; only the 2 A.7.4.6/B.8.4.1 got
  logged this arc.

## Deferred / follow-on candidates from Ship 30

- **Sandbox tenant** (`00000000-...-99` or similar) so dev
  scripts stop touching demo tenant production data
- **Audit other loader SELECTs** — `posture_loader`,
  `graph_expander`, `resolver`'s posture query, etc. — for
  semantic fields missed the same way `confirmation_status` was
- **Retire `document_uploads` vs `client_documents` naming
  confusion** — user found the distinction confusing; a rename
  or comment header could reduce future surprise
- **Sweep-log surface** — `intake_trace_log` records extractions
  but there's no obvious surface for "here's what dev scripts
  wrote in the last 24h" that a tenant admin could inspect

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 30'.a | Investigation + plan | 102 findings traced to Ship 11'.e; 2 DRAFT postures identified; hygiene helper designed |
| 30'.b | Execute sweep + fix bug + wire helper | Queue clean; DRAFT chat-wide bug fixed; measurement scripts retrofitted |
| **30'.c** | **Eval + retro (this)** | **Baseline holds 231/232 PASS + 1 WARN (#200) + 0 FAIL; arc codifies 4 lessons** |

## Related

- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc whose
  measurement runs left the residue
- [[ship-29-prime-arc-retrospective-2026-07-24]] — the immediately
  prior arc; shares the "shared write surface without a contract
  is drift-by-construction" pattern
- [[stage1-queue-sweep-2026-06-27]] — the earlier queue sweep
  (different scenario: catalog-refactor cleanup, not measurement
  residue)
- [[feedback-validate-set-membership]] — conservative sweep
  discipline established after a 2026-06-27 incident
