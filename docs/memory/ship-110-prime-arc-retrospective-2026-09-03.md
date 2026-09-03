---
name: ship-110-prime-arc-retrospective-2026-09-03
description: Ship 110' arc retrospective — client_facts scoping SSoT + progressive discovery + fact-driven applicability derivation, one day
metadata:
  type: project
---

# Ship 110' — client_facts scoping SSoT + fact-driven applicability

**Date:** 2026-09-03 (one day)
**Commits:** `dfe4d564` (a) → `6c2bb647` (b) → `1175df9b` (c) → `a759f06f` (d) → `d70a5dee` (e) → this doc (f)
**Eval baseline:** 237/238 PASS + 1 WARN (#200) + 0 FAIL — unchanged
**Test suite:** grew from 226 → 238 cases outside this arc; Ship 110' added zero eval cases (schema + infra work, no user-facing behaviour to lock).

## Motivation

`client_facts` was defined but effectively unused — Quickstart wrote to
`tenants` and skipped `client_facts` entirely. Every scoping-driven
decision (applies_when clauses, cascade fires, engine proposals) evaluated
against a fictional tenant made of schema defaults (all booleans FALSE
except `has_physical_premises=TRUE`). The tenant's own state didn't
influence what the system did with them.

Trigger: `bootstrap_available` cutover flow shipped in Ship 104' left
Arion demo populated but with `tenants.cloud_only=TRUE` +
`client_facts.has_physical_premises=TRUE` — contradictory. `scope_filter`
was over-reporting Arion as having physical premises, and would inject
"suggest physical controls" instructions into every LLM prompt. Fresh
Quickstart tenants would be even worse: 118 stage2 proposal notifications
on framework enrolment, per Ship 107's incident.

Ship 107's answer was a lifecycle-stage gate on notification producers.
User pushed back during scoping: the stage a client is at shouldn't
change whether a control applies. Applicability is a property of what
the tenant IS, not where they are in the journey. That framing landed
this arc.

## Design principles codified

1. **`client_facts` is the SSoT for compliance-scoping attributes.**
   `tenants` stays slim — identity + RLS pivot only. The legacy
   overlapping columns on `tenants` (`sector`/`industry`/`country`/
   `cloud_only`/`employee_count`/`has_physical_premises`/
   `does_software_development`) remain in place with `COALESCE(cf.X, t.X)`
   read fallbacks; drop them in a follow-up migration once every read
   site is migrated.

2. **`fact_source` JSONB tracks per-column provenance** —
   `default`/`declared`/`derived`/`overridden` — so downstream code can
   distinguish "the tenant said this" from "we assumed this at Quickstart"
   from "the column is at schema default because nobody's answered yet".
   Absence-from-fact_source means default; presence means declared or
   derived.

3. **Fact-driven applicability, no lifecycle coupling.** A control is
   N/A because of WHAT the tenant is (cloud-only, no PII, not a
   controller), not WHERE they are in the journey. Ship 107's lifecycle
   gate stays scoped to notification-producer cadence — a different
   concern from applicability. User rule verbatim: "the stage at which
   a client is shouldn't matter".

4. **Conservative-in-doubt.** Applicability rules fire ONLY when every
   driving fact is `declared` or `derived`. Default facts do NOT fire
   N/A rules — err on showing controls the tenant might need until they
   explicitly say otherwise. The "Not answered" chip in the Profile
   questionnaire is the discovery affordance.

5. **Progressive discovery, not one big questionnaire.** Quickstart
   captures what it asks (sector / country / cloud_only). Profile has
   an "About your organisation" section for the ~10 core scoping
   questions. Future arcs can wire JIT prompts at framework enrolment
   or document upload moments. Bulk survey is bad UX; per-moment
   questions get answered.

6. **Idempotent derivation.** `derive_applicability` clears all
   previously-derived N/A markings first, then re-applies. Handles the
   "fact flipped back" case without per-rule reversal logic. Manual
   overrides deferred (would need an `applicability_source` column
   distinguishing 'derived' from 'overridden').

7. **Human-readable `applicability_reason`** on each N/A control, with
   `[rule_id]` prefix for audit trail. Tenant or auditor asking "why
   is this N/A?" reads a sentence, not a slug.

## Delivery summary

### 110'.a — Schema clarification (`dfe4d564`)

Migration `schema_v112_client_facts_scoping_consolidation.sql`:
- Added `country`, `employee_count` columns to `client_facts` (were only on `tenants`).
- Added `fact_source JSONB` per-column provenance tracking.
- Added `applicability_reason TEXT` to `posture_controls`.
- Backfilled from `tenants` for existing rows.
- Corrected `has_physical_premises` where `cloud_only=TRUE` (Arion).
- Marked all pre-existing non-default column values as `declared` (per rule 3 — don't demote existing state to tentative).
- Read path: `rag/scope_filter.py::get_tenant_scope_facts` now `COALESCE(cf.X, t.X)` for the three overlapping fields — client_facts wins, tenants is the legacy fallback.

Pre-commit hook auto-regenerated the Postgres golden (Ship 102' pattern).

### 110'.b — Quickstart fact initializer (`6c2bb647`)

`rag/onboarding/quickstart.py::_initial_client_facts()` — pure function
producing (declared_values, fact_source_markers) from Quickstart inputs.
`create_first_tenant` now INSERTs `client_facts` atomically alongside
`tenants` + `users` + `api_keys`.

Populates:
- `country` (declared, always set)
- `sector` (declared, if provided)
- `has_physical_premises` + `uses_cloud_services` (declared, from cloud_only checkbox)
- `eu_data_subjects` (derived from country in `_EU_EEA_COUNTRIES`, 30 codes)
- `uk_data_subjects` (derived from `country == "GB"`)

Everything else stays at schema default AND absent from fact_source —
signals `default` to Ship 110'.d.

### 110'.c — Profile "About your organisation" scoping questionnaire (`1175df9b`)

Backend:
- `GET /api/v1/tenant/profile` extended with `scoping_facts` block —
  14 columns × `{value, source, from, at}`.
- `PUT /api/v1/tenant/facts` — allowlisted columns, type-checked,
  UPSERTs `client_facts`, marks `fact_source[col]='declared'`.

Frontend:
- `renderScopingSection()` — 12 Yes/No questions in 4 grouped cards
  (Data operations / Role / Sensitive processing / Organisation).
- Auto-save on each answer with inline ✓ affordance.
- "Not answered" chip for `default` facts, "Assumed from your country ·
  change if wrong" chip for `derived` facts.
- JS version: `scoping-facts`.

### 110'.d — Applicability derivation module (`a759f06f`)

`rag/scoping/applicability.py`:
- 11 MVP rules covering the scope-reduction cases most tenants care about.
- `AppRule` dataclass: driving_facts + predicate + targets + reason.
- `derive_applicability(pg, tenant_id) -> DerivationResult` — reads
  facts + fact_source, clears prior derived N/A, re-applies rules that
  fire.
- Idempotent + reverses correctly on fact flip.

Triggers wired:
- `PUT /api/v1/tenant/facts` (auto-derive on fact change)
- `POST /api/v1/tenant/standards` (auto-derive after framework enrolment)
- `POST /api/v1/admin/derive-applicability` (manual sweep)

Rules (11):

| Rule | Driving facts | Targets | 
|---|---|---|
| cloud_only_no_physical | `has_physical_premises` | ISO27001 A.7.% |
| no_software_development | `develops_software` | ISO27001 A.8.25/26/27/28/29/30/31/33 |
| no_pii_gdpr | `processes_personal_data` | GDPR Art.% |
| no_pii_iso27701 | `processes_personal_data` | ISO27701 % |
| no_eu_uk_subjects | `eu_data_subjects` + `uk_data_subjects` | GDPR Art.% |
| not_controller | `role_controller` + `role_joint_controller` | GDPR Art.24-27 + ISO27701 A.7.% |
| not_processor | `role_processor` | GDPR Art.28 + ISO27701 B.8.% |
| no_special_category | `special_category_data` | GDPR Art.9 |
| no_automated_decisions | `automated_decision_making` | GDPR Art.22 |
| no_cross_border_transfers | `transfers_data_outside_eu` | GDPR Art.44-49 |
| no_children_data | `childrens_data` | GDPR Art.8 (dormant — not surfaced in questionnaire yet) |

### 110'.e — Cascade engine gate + orphan cleanup (`d70a5dee`)

`rag/cascade/engine.py::fire_cascade` — SELECT `applicability_status`
before `triggered_implication` INSERT; skip + info-log if `na`. Silent-
skip rather than `cascade_suppression_log` entry (would need
`schema_v113` CHECK-constraint extension; deferred until audit asks
for persistent trace).

**Discovered pre-existing gates during scope reduction:**
- `posture_loader._persist_engine_proposals` already had the
  `applicability_status='na'` short-circuit from Ship 98'.c.
- `scope_filter.get_tenant_na_scope` already reads
  `applicability_status='na'` for the chat prompt from Ship 66'.a.

**Three-layer applicability discipline now complete:**
1. Chat prompt (Ship 66'.a)
2. Engine proposals (Ship 98'.c)
3. Cascade fires (Ship 110'.e)

Orphan cleanup: dry-run on both active tenants reported 0 orphans —
Ship 107' + Ship 98'.c already covered the mess.

## Verified state on Arion demo (final)

- **`client_facts`**: 8 columns marked `declared` (sector, country,
  role_controller/processor, eu/uk_data_subjects, has_physical_premises,
  processes_personal_data, uses_cloud_services, uses_processors,
  has_remote_workers, develops_software); 6 columns remain at `default`
  (automated_decision_making, employee_count_250_plus, public_authority,
  special_category_data, transfers_data_outside_eu, criminal_conviction_data
  etc.) so the user can answer them via the Profile UI while testing.
- **Applicability derivation**: 11 rules evaluated / 6 skipped for
  default facts / 1 fires (`cloud_only_no_physical`) / 14 A.7.% controls
  marked N/A with reason `"[cloud_only_no_physical] Cloud-only tenant —
  physical premises controls do not apply."`
- **Eval**: 237/238 PASS + 1 known WARN + 0 FAIL — unchanged from
  pre-arc baseline.

## Lessons codified

### Lesson 181 — SSoT drift accumulates when multiple tables answer the same question

`tenants.sector` vs `client_facts.sector` vs `tenants.cloud_only` vs
`client_facts.has_physical_premises` — same semantics, three tables,
none authoritative. Each table was correct when added (identity vs
compliance-scoping vs template placeholders — distinct concerns) but
overlap grew without pruning. Fix: nominate one table as SSoT + migrate
read paths + deprecate duplicated columns for later drop. Follow the
COALESCE fallback pattern so migration is non-breaking.

### Lesson 182 — "The stage at which a client is shouldn't matter"

User's verbatim framing. Applicability is a function of the tenant's
state (facts), not their journey position (lifecycle). Ship 107's
lifecycle gate remains valid for notification cadence — different
concern. Coupling applicability to lifecycle would mean the same
control could flip between applicable/N/A based on whether the tenant
completed onboarding steps — nonsense.

### Lesson 183 — Provenance tracking distinguishes default from declared-false

Before `fact_source`: a boolean column at FALSE could mean either
"tenant explicitly said No" or "nobody's answered yet, using the
schema default". Downstream code can't tell the difference. After
`fact_source`: absence-from-jsonb means default; presence with
`source='declared'` means explicitly answered. This unlocked
conservative-in-doubt derivation — rules only fire when facts are
declared/derived, never for default-shaped data.

### Lesson 184 — Reduced scope is win, not loss

Ship 110'.e was scoped as "cascade engine gate + posture_loader gate +
orphan cleanup". Investigation showed both posture_loader and
scope_filter already had the applicability gate (Ship 98'.c and Ship
66'.a respectively). Ship 110'.e's real delivery was the cascade
engine gate alone (23 LOC + info log). Total arc scope was correct at
plan time — the gates just landed piecewise across three earlier arcs
without a unifying design doc. Ship 110' is that unifying arc.

### Lesson 185 — Progressive discovery over bulk questionnaire

Original scoping considered a 20-question "About your organisation"
form. Cut to 12 questions in 4 cards. Rationale: bulk-survey UX gets
abandoned; per-moment discovery gets answered. Future arcs can wire
JIT prompts (at framework enrolment: "this framework applies specifically
to controllers — are you one?"; at document upload: "this document
mentions personal data — do you process it?"). Progressive discovery
is a pattern; Profile "About your organisation" is the primary manual
entry point.

### Lesson 186 — Deferred: applicability_source column for tenant overrides

Current derivation clears + re-applies. If a tenant explicitly overrides
a derived N/A back to applicable ("no, we DO need to worry about A.7.5
because our cloud provider hosts our physical badge system"), the
override would get clobbered on next re-derive. Ship 110' MVP doesn't
support overrides. Follow-up arc: add
`posture_controls.applicability_source` column with values
`derived`/`overridden` — `_clear_derived_na` filters on `derived` only.

## Related arcs

- [[ship-66-prime-a-applicability-status-column]] — introduced
  `applicability_status` column + chat scope filter read
- [[ship-98-prime-c-engine-proposal-na-gate]] — posture_loader gate
- [[ship-107-prime-tenant-lifecycle-gate]] — notification producer
  lifecycle gate (distinct concern from applicability)
- [[ship-104-prime-arc-retrospective-2026-09-02]] — Quickstart
  bootstrap flow this arc extends
- [[dejargonize-ux-pass-2026-07-01]] — humanization patterns applied
  to Profile section (grouped cards, natural-language question text,
  chips for "Not answered" / "Assumed from your country")

## Deferred

1. `applicability_source` column + override path (see Lesson 186).
2. Drop deprecated overlapping columns from `tenants` after full read-site migration.
3. `cascade_suppression_log` extension for `not_applicable` kind (persistent audit trace).
4. JIT scoping-question prompts at framework enrolment + document upload.
5. Additional derivation rules — the current 11 cover MVP; SOC 2, NIS 2, DORA scoping will land here as those frameworks arrive.
