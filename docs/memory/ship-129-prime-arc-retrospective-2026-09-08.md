---
name: ship-129-prime-arc-retrospective-2026-09-08
description: Ship 129' arc — discovery vs surfacing separation (Stage-1/Stage-2 subscription filter + xfw enrolment gate + jurisdiction-driven enrolment nudge)
metadata:
  type: project
---

# Ship 129' — discovery vs evidence-surface separation

**Date:** 2026-09-08
**Sub-arcs:** 129'.a Stage-1 → 129'.b Stage-2 → 129'.c chat xfw
            → 129'.d enrolment nudge → 129'.e retro + PoC deploy
**Trigger:** Ship 128' surfaced 2 Art.30 GDPR findings in an
             ISO-only tenant's Stage-1 queue. Operator asked how
             to present out-of-scope results + whether GDPR was
             hard-coded across modules.

## Discussion → design

Codified separation rule (see `[[feedback-discovery-vs-surfacing-separation]]`):

- **Discovery layer** (workbook_discovery / doc_discovery /
  persistence writers): framework-agnostic. Every mapping YAML fires.
  Every finding lands in `document_findings`. Zero change from today.
  Two motivations: (1) instant compliance flip when a tenant enrols a
  new framework — data is already there; (2) foundation for future
  cite-mode automated evidence gathering.
- **Evidence surface** (Stage-1 queue / Stage-2 queue / chat xfw
  citations / notifications): strictly filtered to enrolled
  frameworks. Non-enrolled findings persist but never surface.
- **Enrolment nudge**: driven by JURISDICTION facts
  (`client_facts.eu_data_subjects` etc.), NOT by discovery counts.
  Counts enrich the nudge body as supporting evidence but never
  drive the trigger.

The framing "GDPR is hardcoded in many modules" was empirically
inaccurate — audit confirmed the CATALOG (mapping YAMLs, Neo4j
xfw edges, fingerprints) has GDPR content but the RUNTIME (engines,
queries) is framework-agnostic. The gap was that HITL surfaces
didn't filter by tenant_standards.

## Delivery summary

### 129'.a — Stage-1 queue subscription filter

`rag/posture/stage1_review_chat.py` — both `list_queue()` +
`list_pending_for_control()` INNER JOIN `tenant_evaluation_scope`
(NOT `tenant_standards` directly). The view returns direct
enrolments PLUS inferred ones (e.g. GDPR reachable via ISO 27701
`maps_to`) and is the same predicate the runtime uses for scope
resolution.

**First-attempt mistake — captured for future reference**: initial
implementation used `tenant_standards ts WHERE ts.status <>
'lapsed'`. That's stricter than the runtime `scope_loader` (which
reads `tenant_evaluation_scope`). Filtering on the stricter predicate
hid 43 GDPR eval cases that were legitimately in-scope via inference.
Rule of thumb: any DB-level subscription filter must use the SAME
predicate the runtime uses for scope resolution — otherwise the
filter is silently inconsistent with what the tenant sees elsewhere.

`tests/test_stage_queue_subscription_filter.py` — 4 tests locking
the invariants: out-of-scope hidden, per-control view hides too,
instant-flip on enrolment, lapsed re-hides. Tests remain valid
because they seed direct `tenant_standards` rows (which drive the
view).

### 129'.b — Stage-2 queue subscription filter

`rag/posture/stage2_approval_chat.py` — same shape on
`list_pending_proposals()` + `get_proposal_for_control()`, INNER JOIN
on `tenant_evaluation_scope` for the same runtime-consistency reason
as 129'.a. Deep-link to an out-of-scope control returns None → API
surfaces the same 404 as "no posture entry for this control"
(symmetric with list).

Fallback text at line 608 updated to explicitly mention the enrolment
possibility as one of three reasons a proposal isn't on file, since
the Ship 129'.b filter added that as a third cause.

Test file extended: 3 more tests (list filter, single-control 404,
instant-flip). Cleanup fixture extended to include posture_assertions
+ posture_controls. **7/7 PASS**.

### 129'.c — Chat xfw bridge footer respects subscription

Added `CaseFile.is_ref_enrolled(ref)` predicate to `rag/casefile/
types.py`. Uses tenant's `scope_standards` (populated from
tenant_standards via scope_loader upstream). Ref → standard lookup
via posture record first, graph_nodes fallback.

**Fail-open contract**: returns True when either the ref's standard
can't be resolved, or `scope_standards` is empty. Matches Ship 66'.a
"widen rather than assume ISO" convention — never silently censors
content whose provenance we can't verify.

Applied at two rendering sites (`rag/casefile/digest.py::
_render_xfw_bridges` + `rag/casefile/preservation.py::
_build_bridge_footer`). The filter runs on BOTH sides of each bridge
line (node ref + linked refs) — a bridge line must not contain any
non-enrolled ref, even if the "primary" side is enrolled. Prevents
the preservation footer from reintroducing a ref that
`framework_scope_guard` (Ship 3'.l) just stripped from LLM prose.

`tests/test_casefile_enrolment_filter.py` — 8 hand-built CaseFile
unit tests: predicate cases (True/False/fail-open ×2) +
`_render_xfw_bridges` (drop/keep) + `_build_bridge_footer` (None/
fire). No DB needed.

### 129'.d — Enrolment nudge notification

Schema `db/schema_v119_unenrolled_framework_notification.sql`:
- New notification kind `unenrolled_framework_applicable` (18 total in
  allowlist).
- New sweep work_type `enrolment_nudge`.
- **Fixed pre-existing CHECK drift** on `sweep_log.work_type` — added
  `posture_refresh` (Ship 58'.u) + `cite_attestation_retention` (Ship
  93'.z.i). Both were in `_WORK_TYPES` registry but never added to the
  constraint; they'd have blocked the CHECK re-creation otherwise.

Module `rag/notifications/enrolment_nudge.py`:
- Nudge rules as data (`FrameworkNudge` dataclass — standard_id,
  display_name, driving_facts, predicate, why_message). Same shape as
  `AppRule` in the applicability engine.
- 2 rules today: GDPR (eu_data_subjects OR uk_data_subjects) + ISO
  27701 (processes_personal_data). Extends to LGPD/CCPA/etc when
  regional frameworks land per Ship 115+ deferred backlog.
- Facts must be `declared` or `derived` in `fact_source` — `default`
  facts don't fire (Ship 110'.d conservative-in-doubt convention).
- Dedup per (tenant, framework) within 30 days.
- Sweep iterates tenants via `posture_controls` (has `app_posture_all`
  permissive policy) rather than `tenants` (strict RLS) — avoided
  broadening tenant-table RLS to `arioncomply_app`.
- Inner reads (`client_facts`, `tenant_standards`) set app.tenant_id
  before SELECT — those tables have strict RLS.

Discovery-count enrichment via `_discovery_count()` — added to the
notification body when > 0 ("we've already scanned your evidence and
found N findings ready to activate on enrolment"). When N=0 the
sentence is omitted; the trigger is still jurisdiction, not count.

Wired into `rag/scheduler/tick.py::_WORK_TYPES`.

`tests/test_enrolment_nudge.py` — 7 tests covering fires/skips (facts
not declared / already enrolled / dedup / discovery count enrichment
present + absent / PIMS variant). **7/7 PASS**.

### 129'.e — Retro + PoC deploy

`scripts/ops/ship-129-poc-update.sh` — install.sh (applies v119) →
API restart → probe → CHECK-constraint verification → dry-run sweep →
regression tests → live queue counts (post-filter) → nudge
candidates → deployment log tail.

## Lessons codified

### Lesson 261 — Vocabulary matters: enrolment vs applicability vs in-scope

Three overlapping-but-distinct predicates:
- **Enrolled** — row exists in `tenant_standards` with `status <>
  'lapsed'`. Tenant subscription decision.
- **Applicable** — `client_facts` predicates return True (per Ship
  110'.d `AppRule`). Jurisdiction + role-driven.
- **In-scope** — `posture_controls.applicability_status <> 'na'` at
  the individual control level. Per-control N/A from applicability
  rules OR tenant override.

Ship 129 needed a NEW predicate (`is_ref_enrolled`) because none of
the three matched. `in_scope` was the closest but semantically
different — a control could be in-scope AND applicable but not
enrolled. Adding new predicates is preferable to overloading
existing ones (`in_scope` has ~15 call sites; extending its
semantics would have unpredictable ripple).

### Lesson 262 — Bridge lines need bilateral filtering

When a rendering surface displays a RELATIONSHIP (like the xfw bridge
`A.5.15 ← Art.32`), enrolment filtering on ONE side isn't enough. If
the tenant has ISO enrolled but not GDPR, filtering only on the
node's own ref (`Art.32`) misses the mirror direction (`A.5.15's`
bridge dict entry lists `Art.32` as a linked ref). Rule of thumb:
every ref that appears in the output line must satisfy the filter.

Test-driven caught this in Ship 129'.c — first pass hid one direction
but not the mirror; regression test showed `A.5.15 ← Art.32` still
rendering. Fix: filter linked refs too, and drop the whole line if
any ref fails.

### Lesson 263 — Fail-open filter contracts prevent silent censorship

`CaseFile.is_ref_enrolled()` returns True when either the scope is
unknown OR the ref's standard can't be resolved. This is deliberate:
a missing tenant profile shouldn't silently drop legitimate content.
Same pattern as Ship 66'.a "widen rather than assume ISO." Any new
filter that could hide content should have an explicit fail-open
clause — otherwise operational glitches (missing scope, unknown
standard) silently degrade the tenant experience.

### Lesson 265 — DB filters must match runtime scope predicates

Ship 129'.a/b initially filtered on `tenant_standards.status <>
'lapsed'` — direct-enrolment only. The runtime `scope_loader` reads
`tenant_evaluation_scope` which INCLUDES inferred standards (GDPR
via ISO 27701 `maps_to`, for example). The mismatch hid 43 GDPR
eval cases that were legitimately in-scope from the runtime's
perspective.

Rule: any new filter that gates surfaced content must join against
the SAME view/table the runtime uses for scope resolution — never a
stricter proxy. Runtime scope is the source of truth; DB filters are
enforcement layers, not policy layers. Caught only when 43 unrelated
eval cases regressed on a single flag.

If two scope predicates exist (direct vs. direct-plus-inferred),
have a design conversation about which one applies BEFORE writing
the filter, and document the choice inline. Both are legitimate for
different use cases (nudge trigger uses direct, worklist filter uses
direct-plus-inferred).

### Lesson 264 — CHECK-constraint drift accumulates silently

Adding a new value to `sweep_log.work_type` CHECK constraint failed
because `posture_refresh` + `cite_attestation_retention` — added to
`_WORK_TYPES` registry in prior arcs — had never been added to the
CHECK. They ran fine (INSERT worked because CHECK wasn't re-created)
until my ADD CONSTRAINT tried to validate existing data.

Same class as Ship 121 audit-table grant drift + Ship 120 baseline-
grants drift: a policy value defined in one place (code) that must
also be reflected in a constraint (SQL). Fix: whenever a new value
lands in `_WORK_TYPES` or `tenant_notification_kind`, the same PR
must extend the CHECK. A regression test could enforce this
(assert every `_WORK_TYPES` key appears in the CHECK). Deferred.

## Related arcs

- [[ship-128-prime-arc-retrospective-2026-09-08]] — the workbook fix
  that surfaced this design gap (Art.30 in ISO-only queue)
- [[ship-110-prime-arc-retrospective-2026-09-03]] — client_facts SSoT
  + `AppRule` shape that FrameworkNudge mirrors
- [[ship-104-prime-arc-retrospective-2026-09-02]] — grey-out vs filter
  pattern (worklists filter, discovery surfaces grey-out)
- [[ship-66-prime-a-scope-column-fix]] — `applicability_status` split
  from `finding`; `in_scope` predicate origin
- [[ship-76-prime-b-in-scope-ssot]] — `CaseFile.in_scope()` predicate
  consolidation; new `is_ref_enrolled` is the sibling for enrolment
- [[feedback-discovery-vs-surfacing-separation]] — the codified rule

## Deferred to Ship 130'+

- **Regional-framework nudges** (LGPD/CCPA/APPI/PIPEDA/PDPA) — waits
  on the regional-framework curation arc. `FrameworkNudge` shape is
  ready — each new framework adds one entry to `_NUDGES`.
- **Enrolment banner on Get Started** — the sidebar's Get Started
  mode could show unenrolled-applicable frameworks inline, not just
  in the notification inbox. Same data source as the nudge (dry-run
  of the sweep exposes candidates); rendering is UX-side.
- **Regression test for CHECK-constraint drift** — assert every
  `_WORK_TYPES` key appears in `sweep_log_work_type_check` +
  every kind emitted by producers appears in
  `tenant_notification_kind_check`. Would have caught the drift
  before it blocked schema_v119.
- **External API filter for cross-framework results** — the external
  `/posture` + `/notifications` endpoints (Ship 4') already filter
  by enrolment. The `/documents` + `/evidence` endpoints should be
  audited to confirm they don't leak out-of-scope findings to
  external callers. Small arc.
- **Chat "would you enrol" call-to-action** — when a user queries
  about a non-enrolled ref (Art.32 example), the chat could inline
  a "This is a GDPR question. Enrol GDPR to see how your existing
  controls map to it" prompt. Behavioral, not just filtering.

## PoC state after Ship 129'

- Not yet deployed (dev-side ship complete; operator to run
  `scripts/ops/ship-129-poc-update.sh` when ready).
- Regression suites all green:
  - `tests/test_stage_queue_subscription_filter.py` — 7/7 PASS
  - `tests/test_casefile_enrolment_filter.py` — 8/8 PASS
  - `tests/test_enrolment_nudge.py` — 7/7 PASS
- Schema v119 applied on dev VM; sweep wiring verified via dry-run
  scanning 2 tenants correctly (both skipped as facts_not_ready —
  demo tenants haven't declared jurisdiction facts).
