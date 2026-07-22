---
name: ship-14-prime-arc-retrospective-2026-07-22
description: "Ship 14' arc retrospective — Risk Register product feature; 6 delivery sub-arcs + closer; from schema_v2 legacy to first-class product surface"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14' arc — Risk Register product feature. From the user's
opening question ("can we surface a risk register on the
dashboard now that ISO 27005 is in?") to a first-class product
surface with dashboard + chat + notifications + API — all in
one day.

**Arc window:** 2026-07-22. 6 delivery sub-arcs + this closer,
single session.

## Sub-arc inventory

| Sub-arc | Delivery | Commit |
|---|---|---|
| 14'.a | Design memo — discovery-driven; `risks` table already existed (schema_v2 legacy); role-model + case-file addendum | `36d5eb8` + `529665a` |
| 14'.b | schema_v87 (5 columns per 27005 §8.6.1) + canonical xlsx template + workbook-importer extension | `3df2bb0` |
| 14'.c | 7 endpoints (4 internal + 3 external) + `rag/risk/` module + `external:risks:read` scope | `bad95d5` |
| 14'.d | Dashboard: 4 tiles + 5×5 heatmap + top-5 + full list + drill-in detail panel | `546520b` |
| 14'.e | Chat surfaces: `POSTURE_RISK` question_type + Signal C at 1.00 + short-circuit + CaseFile.risks + digest slot + preservation + nav badge | `a273a67` |
| 14'.f | schema_v88 (4 notification kinds + sweep work_type + `app_risk_all` policy) + `rag/risk/notify.py` (sweep + write-path producers) | `e80b1e5` |
| **14'.g Arc retrospective** | **This doc + 3 eval cases** | (next commit) |

## What ships from Ship 14'

**Schema (2 migrations):**
- `schema_v87` — 5 new columns on `risks` per 27005 §8.6.1
  (treatment_rationale, resources_required, performance_indicators,
  constraints, reporting_cadence)
- `schema_v88` — 4 new notification kinds + 1 sweep work_type +
  `app_risk_all` RLS policy

**Data:**
- Canonical xlsx template at `db/templates/risk_register_canonical.xlsx`
  — 4 sheets (Register + Treatment Plan + Guidance + hidden
  `_arion_meta` with auto_approve marker)

**Modules:**
- `rag/risk/__init__.py` + `rag/risk/queries.py` — shared query +
  display module; `RiskRow`, `RiskDetail`, `RiskSummary`,
  `LinkedControl` Pydantic models; `linked_controls_view()`
  explodes control_refs into role-tagged entries
- `rag/risk/notify.py` — `emit_risk_added()` write-path +
  `sweep_risk_register_notify()` scheduler sweep

**API surface (7 endpoints):**
- Internal: `GET /api/v1/tenant/risks` (list + filter + paginate),
  `/risks/summary` (dashboard aggregate), `/risks/template`
  (canonical xlsx download), `/risks/{risk_id}` (drill-in)
- External (under `external:risks:read` scope):
  `GET /api/external/v1/risks`, `/risks/summary`,
  `/risks/{risk_id}`

**Chat pipeline extensions:**
- New `QuestionType.POSTURE_RISK` enum value
- 10 Signal C `CLEAR_INTENT_PHRASES` at weight 1.00
- `_is_risk_query()` + `_answer_risk_query()` deterministic
  short-circuit in `rag/arion_graph.py`
- `CaseFile.risks` ground-truth field on the dataclass
- `_render_risks()` fixed-slot digest section
  (≤300-token budget)
- `required_risk_refs` on PreservationSpec
- `missing_risk_ref` RepairEvent kind + `↳ Risk register:`
  APPEND-ONLY footer

**Dashboard (`static/arioncomply.html`):**
- "Risk register" sidebar entry with nav badge
- 4-tile summary row + 5×5 heatmap + top-5 list + full table
- Drill-in detail panel with all treatment-plan fields
- `refreshRiskBadge()` on connect() with red/orange severity
  coloring

**Workbook importer extension:**
- `RowMappers.risk_treatment` now parses 5 new columns
  additively (nullable-safe)

**Eval + tests:**
- 3 new eval cases (#225-227) locking `posture_risk` routing +
  short-circuit + query-mode inference
- (Existing round-trip unit test on the mapper stays passing)

Baseline: **228/229 → 231/232 PASS + 1 WARN + 0 FAIL** across
the arc (with 3 new cases added by 14'.g). Only WARN throughout
was the pre-existing #200.

## Codified lessons

### 1. Discovery-driven design catches wiring-up disguised as greenfield

14'.a's design memo started as a scoping exercise ("what does a
Risk Register product feature need?"). Discovery revealed:

- `risks` table already exists (schema_v2, pre-arc-labeling)
- 35 populated rows on Arion demo tenant
- `remediation_plans` FK already in place
- `DocType.RISK_REGISTER` in intake pipeline
- Curated leaves (6.1.2, 6.1.3) already carry Ship 13'.b 27005
  authority paragraphs

The arc pivoted from **greenfield build** to **wiring-up**.
That reshape saved probably 2-3 sub-arcs of duplicated schema
+ intake work.

**Generalisation**: before proposing a new feature, grep for
its data-model shadow. Old tables from earlier arcs often exist
as scaffolding waiting to be surfaced.

### 2. Architecture-constraint addendum is worth writing

Mid-14'.a the user asked to codify two constraints:
- Framework role model (program/extension/obligation as
  first-class, no primary/xfw split)
- Case-file architecture pattern (compact digest + fixed slots
  + preservation + APPEND-ONLY repair + Signal C at weight 1.00)

Wrote them into the memo as an addendum with 4 alignment
questions PR memos must answer:
1. Does it split by role, or treat all roles first-class?
2. Does it add a new digest slot, or parallel the CaseFile?
3. Does it deterministically route, or rely on LLM inference?
4. Does it add MUSTs, or maintain guidance-not-normative?

Every subsequent sub-arc memo answered these. That kept 14'.d's
dashboard chips role-first-class, 14'.e's chat surface honouring
case-file discipline, 14'.f's notifications avoiding cascade
overreach.

**Generalisation**: for multi-sub-arc arcs, codify architectural
constraints AS-YOU-GO in the design memo. The 4-question
alignment check per sub-arc is cheap discipline that catches
drift.

### 3. Cascade events vs. terminal notifications — pick the right
frame

Original 14'.a plan had "cascade events" as 14'.e scope.
Discovery in 14'.f: risks are TERMINAL nodes — they get treated,
reviewed, closed. They don't propagate to other controls the
way `incident_declared` does (which triggers evidence
obligations across the framework).

Reframe: 4 new NOTIFICATION KINDS, not 4 new cascade taxonomy
edges. No Neo4j relationship types added. No implication rows
generated. Just three sweep-triggered kinds + one write-path
kind, each with severity ladders + dedup.

**Generalisation**: not every state-change event needs to
enter the cascade meditation. Terminal events (risks closing,
policies retiring, users offboarding) can be pure notifications
without triggering cross-control implications.

### 4. Legacy scaffolding needs RLS policy audits

`risks` had `tenant_isolation` policy only — required
`app.tenant_id` on every SELECT. The sweep pattern needs
cross-tenant scan capability for the `arioncomply_app` role.
The `posture_controls` table had `app_posture_all` policy for
exactly this; `risks` didn't.

Fixed in `schema_v88`: added `app_risk_all` policy. Discovered
via the sweep returning 0 scanned when the demo tenant clearly
had matching rows.

**Generalisation**: any table added before Ship 3'.a scheduler
existed probably needs an RLS audit. If you plan to sweep it
across tenants, verify the `arioncomply_app` role has permissive
access via a maintenance policy.

### 5. Additive-only migrations preserve the baseline

Every 14' schema change was NULL-permissive-additive:
- schema_v87 added 5 nullable columns (no backfill needed)
- schema_v88 extended CHECK constraint allowlists (no data
  breakage)

No sub-arc broke existing rows on the 35-row demo dataset.
Eval baseline never dipped below 228/229 across all 6 sub-arcs.
The Ship 12'.b enrollment-stub pattern generalises: schema
changes should be additive-only where possible; when they must
be mutating, land a scrub script alongside so the mutation is
reversible.

## What did NOT ship

**Deferred to follow-up arcs:**

- **`emit_risk_added` write-path wire-up in workbook importer** —
  `_write_rows` in `db/workbook_importer.py` needs to detect new
  INSERTs (vs UPSERT updates) and call the helper. INSERT
  detection is invasive; deferred until a natural POST /risks
  endpoint arrives (which has clean INSERT-only semantics).
- **UI drill-in enhancements for the 4 new notification kinds** —
  existing inbox renders arbitrary kinds already; "Open R-042"
  deep-link buttons follow the Ship 3'.h/'i pattern but aren't
  built for the risk kinds.
- **Client-side filters / sort / bulk actions** on the full list
  table.
- **DEMONSTRATES lineage on obligation-linked drill-in** — when
  a risk links to `GDPR:2016/679:Art.32`, the drill-in shows
  the ref but doesn't traverse to the demonstrating program/
  extension sources. Full role-model Phase 4a integration
  deferred.
- **Cross-collection Chroma retrieval on risk text** — risks are
  structured; semantic search on threat/vulnerability descriptions
  ("supply chain risks", "cryptography risks") is a Ship 15+
  candidate.
- **SDK typed methods** for the new endpoints (Python SDK in
  `sdk/python/arioncomply/`).
- **Risk automation** — no auto-classification of threats,
  auto-scoring, or NIST NVD / MITRE integration. Human judgment
  stays central per the human-in-the-loop positioning memo.

## Baseline throughout

| Sub-arc | PASS | WARN | FAIL |
|---|---|---|---|
| Start (Ship 13'.f close) | 228/229 | 1 | 0 |
| After 14'.b (schema + template) | not run (data-layer only) | — | — |
| After 14'.c (API surface) | 228/229 | 1 | 0 |
| After 14'.d (dashboard) | not run (UI-only) | — | — |
| After 14'.e (chat + case-file) | 228/229 | 1 | 0 |
| After 14'.f (notifications) | 228/229 | 1 | 0 |
| **After 14'.g (+3 cases)** | **231/232** | **1** | **0** |

## Ship 14' close

| Sub-arc | Status |
|---|---|
| 14'.a Design + role-model + case-file addendum | ✓ |
| 14'.b schema_v87 + xlsx template + upload path | ✓ |
| 14'.c API surface (internal + external) | ✓ |
| 14'.d Dashboard cards + heatmap + drill-in | ✓ |
| 14'.e Chat surfaces + case-file discipline + nav badge | ✓ |
| 14'.f Notification producers (sweep + write-path) | ✓ |
| **14'.g Eval cases + arc retrospective** | **✓ (this doc)** |

Total: 6 delivery sub-arcs + closer. Second-largest arc in
project count after Ship 4' (7+closer) and Ship 13' (5+closer).
Single-day arc.

## Related

- [[ship-13-prime-arc-retrospective-2026-07-22]] — the ISO
  27005 grounding arc that motivated 14' (user's question
  post-13'.f close)
- [[framework-role-model-arc]] — the role model 14'.a
  addendum codified alignment questions around
- [[ship-2-prime-casefile-arc-2026-07-15]] — the case-file
  architecture 14'.e extended with the RISKS digest section
  + preservation for risk refs
- [[ship-1-consensus-arc-2026-07-15]] — Signal C at weight
  1.00 discipline the 14'.e CLEAR_INTENT_PHRASES follow
- [[ship-3-prime-a-sweep-scheduler]] (implicit via CLAUDE.md
  build sequence) — the scheduler productionization Ship
  14'.f's sweep runs under
- Ship 15+ candidates: `emit_risk_added` wire-up; UI drill-in
  for risk notification kinds; DEMONSTRATES traversal in the
  drill-in; Chroma retrieval of risk text; SDK typed methods
