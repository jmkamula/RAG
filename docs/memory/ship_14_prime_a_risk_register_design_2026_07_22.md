---
name: ship-14-prime-a-risk-register-design-2026-07-22
description: "Ship 14'.a — Risk Register product arc design memo; discovery reveals the risks table already exists (schema_v2) but is unwired; arc becomes about connecting dots"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.a (2026-07-22) — opens Ship 14 arc. Motivating question
from the user: "with ISO 27005 in, shouldn't we be able to
extend our offering with a Risk Register that surfaces on the
dashboard?"

Answer: yes, and more of the plumbing exists than expected.
Ship 14 is a **wiring-up arc**, not a greenfield build.

## Discovery — what already exists

Survey during 14'.a scoping surfaced substantial infrastructure
laid down in earlier arcs but never wired to any user surface:

### Data model — mostly complete

`risks` table (from `schema_v2` — pre-arc-labeling era):

- 27 columns covering identity + asset link + threat/vuln + CIA
  scoring (likelihood 1-5, impact 1-5, risk_score) + owner (both
  text and FK to users) + treatment (option / action / status /
  implementation_date / residual_risk_level / review_date /
  effectiveness_review) + audit metadata (created / updated /
  deleted / retention_class / purge_after)
- CHECK constraints: `treatment_option ∈ {Mitigate, Accept,
  Transfer, Avoid}`; `treatment_status ∈ {open, in_progress,
  implemented, accepted}`
- FKs: `asset_id → assets`, `risk_owner → users`, `tenant_id →
  tenants`
- RLS policy: `tenant_isolation` — tenant-scoped
- `remediation_plans` table already FKs into `risks`
- Data present: 35 rows on 1 tenant

### Intake pipeline — first-class

- `DocType.RISK_REGISTER` in `rag/intake/models.py`
- Doc classifier patterns in `rag/intake/enricher.py` (matches
  "risk register", "risk assessment", "risk log", "risk matrix"
  + defaults xlsx/csv to `risk_register`)
- Workbook importer parses `residual_risk_level` from the sheet
- Ref normalizer entry for `risk_register`

### Curation — Ship 13'.b already enriched

- `req:6.1.2:risk_assessment` primary leaf + `req:6.1.2:risk_register`
  sibling leaf + `req:6.1.3:risk_treatment_plan` all curated
- Ship 13'.b added the 27005:2022 §7 authority paragraph to 6.1.2
- Ship 13'.c added the 27003:2017 §6.1.2 guidance paragraph to
  the same leaf

### Chat vocabulary — humanised

- `rag/arion_graph.py::_ROLE_LABELS` maps `risk_register` →
  "risk register" and `risk_treatment_plan` → "risk treatment
  plan"
- `rag/posture/acknowledge_chat.py` has regex for risk-treatment
  mentions

## Gaps — where Ship 14 delivers

### 1. Zero API surface

`grep -c "risks" api_server.py` returns 0. Neither
`/api/v1/risks/*` (internal) nor `/api/external/v1/risks/*`
(SDK-exposed) exist. The `risks` table is completely orphaned
from the request layer.

### 2. Zero dashboard surface

`grep -i risk static/arioncomply.html` returns matches only for
document-type filters + form field labels. No risk-register
summary card, no heatmap, no drill-in view.

### 3. Chat routing incomplete

No `DOCUMENT_TOPIC_MAP` entries for "top risks", "residual
risks", "overdue risks", "risk register" as a chat query. The
existing `risk_register` doc-type is for INGESTED files, not
for tenant queries about risk state.

### 4. Canonical template missing

No xlsx template with `_arion_meta` binding for risks. Tenants
would upload arbitrary spreadsheets — the workbook importer
tries to interpret, but there's no starter template we ship.

### 5. Schema column gaps vs 27005 §8.6.1

27005 §8.6.1 lists required treatment-plan elements:
- ✅ owner (schema has `risk_owner`)
- ✅ actions (schema has `treatment_action`)
- ✅ status (schema has `treatment_status`)
- ✅ implementation date (schema has `implementation_date`)
- ✅ residual level (schema has `residual_risk_level`)
- ❌ **rationale** (missing — why this treatment option was chosen)
- ❌ **resources_required** (missing)
- ❌ **performance_indicators** (missing — KPIs per §8.6.1)
- ❌ **constraints** (missing)
- ❌ **reporting_cadence** (missing)
- ❌ **timeline** (partially covered by implementation_date)

### 6. No cascade integration

No cascade events for `risk_added`, `risk_treatment_overdue`,
`residual_above_threshold`, `risk_review_due`. Existing
cascade taxonomy (53 events per Ship 6 arc) doesn't cover the
risk domain.

### 7. Chroma indexing of tenant risks

Not scoped for Ship 14 initially — the risks table is
structured data, not free text. But tenant-authored risk
descriptions could be semantically retrievable if we index
them ("show me all risks about supply chain compromise" →
retrieve by threat/vuln text). Deferred.

## Revised sub-arc plan (per gap inventory)

| Sub-arc | Delivery |
|---|---|
| 14'.a | This memo — discovery + design |
| 14'.b | schema_v87 adds missing 27005 §8.6.1 columns to `risks` + canonical xlsx template with `_arion_meta` binding + upload → risks row insertion path in workbook importer |
| 14'.c | API surface — `/api/v1/risks/*` (internal admin/tenant CRUD + summary) + `/api/external/v1/risks/*` (SDK read endpoints under scope `external:risks:read`) |
| 14'.d | Dashboard cards + risk heatmap (likelihood × consequence 5×5 grid) + drill-in view (per-risk detail page) — Static HTML updates to `arioncomply.html` |
| 14'.e | Chat surfaces — new `posture_risk` question_type + DOCUMENT_TOPIC_MAP entries + risk-specific case-file digest section — plus cascade events + notification producers |
| 14'.f | Eval cases (3-4 covering top-risks / residual / overdue queries) + arc retrospective |

Original sub-arc plan had 6 sub-arcs (a-f) with 14'.b as
template-only and 14'.c as YAML-curation. Discovery shifts:

- **Curation YAML was already done** (Ship 13'.b + 13'.c covered
  6.1.2 + 6.1.3). Not needed here.
- **Template + upload merges with schema-completion** into 14'.b
- **New sub-arc for API** — 14'.c — needed because zero
  endpoints exist today

The 6-sub-arc count stays the same, but scopes shift.

## Design decisions to lock in 14'.a

### Schema addition — additive only

Add 5 columns to `risks`:
- `treatment_rationale TEXT` — why this option
- `resources_required TEXT` — budget / people / infrastructure
- `performance_indicators TEXT[]` — KPIs per §8.6.1
- `constraints TEXT` — dependencies, timing gates
- `reporting_cadence TEXT` — how often status is reported

All `NULL`-permissive so existing 35 rows on demo tenant don't
need backfill. Ship 14'.b lands the migration.

### Template — xlsx with `_arion_meta`

Follow the pattern from Ship 12's templates_v2 arc:
- Register sheet (visible) with 15+ columns matching schema
- Guidance sheet (visible) with 27005 §8.6.1 authoritative
  language
- `_arion_meta` hidden sheet with per-column binding to schema
  fields
- Round-trip: tenant fills → upload → risks table populated
- Auto-approve via marker match (per Ship 12's discipline)

### Question type — new `posture_risk`

Risk queries are neither `posture_check` (which asks about a
specific compliance leaf) nor `document_inventory` (which asks
about uploads). A new question_type is cleaner than overloading
existing ones.

Router logic:
- "top risks" / "highest risks" → `posture_risk` short-circuit
  → returns top-N by `risk_score DESC`
- "overdue risks" / "risks needing review" → `posture_risk`
  short-circuit → returns rows past `review_date`
- "residual risks" → `posture_risk` → rows with
  `residual_risk_level >= 15` (top quintile of 1-25 scale)
- "what does 27005 say about risk assessment" → stays
  `definition` (Ship 13'.d locked this)

### Dashboard shape — 3 tiles + heatmap + drill-in

Landing page:
1. **Summary tile**: total risks / open / overdue / above-threshold
2. **Treatment status tile**: donut chart Mitigate/Accept/Transfer/Avoid
3. **Top-5 risks list**: highest risk_score, click-through
4. **Heatmap**: 5×5 likelihood × impact grid with counts, click
   to filter list

Drill-in per risk:
- Header: external_ref + title + risk_score + treatment_option
- Description: threat + vulnerability + asset context
- Treatment plan: all §8.6.1 fields
- Linked findings: which posture leaves reference this risk
- Review history: audit trail

### Cascade events — 4 new event types

- `risk_added` — new row inserted
- `risk_treatment_overdue` — implementation_date past, status
  != implemented
- `residual_above_threshold` — residual_risk_level >= 15
- `risk_review_due` — review_date within 30 days OR past

All feed the existing cascade timeline + notification producers.

## What Ship 14 does NOT ship

- **Risk automation** — no auto-classification of threats,
  auto-assignment of risk_owner, or auto-scoring. Human
  judgment stays central.
- **Risk aggregation** — no roll-ups by asset, department, or
  program. Deferred to a later arc.
- **External risk-feed integration** — no NIST NVD, MITRE,
  supplier-risk databases wired in. Manual entry only.
- **Chroma retrieval of risk text** — the risks table is
  structured; if tenants want semantic search on risk
  descriptions ("supply chain risks", "cryptography risks"),
  that's a future arc.
- **Cross-framework risk mapping** — NIST CSF risk-management
  functions could map here, but the framework-role-model
  applies. Deferred.

## Success criteria

1. `POST /api/v1/tenant/risks/upload` accepts the canonical
   xlsx template and creates risks rows
2. Dashboard shows 3 tiles + heatmap on Arion demo tenant with
   35 existing risks
3. Chat query "what are our top risks?" returns a top-5 list
   with treatment status
4. New question_type `posture_risk` locked by 2+ eval cases
5. `residual_above_threshold` cascade event fires on any risks
   row insert with residual_risk_level >= 15
6. Eval baseline holds at 228/229 PASS + 1 WARN + 0 FAIL or
   better (with 3-4 new cases, likely 231/232 or 232/233)

## Architecture constraints (2026-07-22 addendum)

Two arc-level architectural constraints codified by the user
after the memo landed. Every sub-arc from 14'.b onward MUST
respect these.

### 1. Framework role model — program / extension / obligation

Per [[framework-role-model-arc]], the standards taxonomy is
hierarchical, not peer:

- **program** (ISO 27001, SOC 2, NIST CSF) — the ISMS spine
- **extension** (ISO 27701, 27018, 27017) — overlays on a program
- **obligation** (GDPR, NIS2, DORA) — legal mandates,
  demonstrated by programs + extensions
- **guidance** (ISO 27002/27003/27004/27005) — code-of-practice
  companions

The layer split by "primary/xfw" is DEPRECATED (Ship 2'.n
retired the legacy `rank_and_answer` body that used it). All new
surfaces must render program + extension + obligation as
first-class citizens.

**Application to Risk Register:**

- `risks.control_refs TEXT[]` (already exists) can hold refs
  across ALL four roles. A single risk row can reference
  `A.5.15` (27001 program), `A.7.5.1` (27701 extension), and
  `Art.32` (GDPR obligation) in one array. No role filtering.
- **Dashboard drill-in** must render linked controls WITHOUT
  splitting by role. Show all linked controls together, with
  role-band chips (from Ship's framework-role-model Phase 4b
  dashboard headers) rather than tab-separated sections.
- **Chat responses** on risk queries surface controls without
  qualifying "primary standard" vs "cross-framework". The
  role-model retired that hierarchy.
- **API responses** carry `role` + `subject` on each linked
  control (per Phase 4b's `/dashboard/posture` pattern), plus
  `*_display` companions per Ship 7'.b output-gateway
  discipline. External SDK consumers filter by role client-side.
- **DEMONSTRATES cascade honoured.** If a risk links to Art.32
  (obligation) and Art.32 has DEMONSTRATES sources from ISO
  27001 A.5.15/A.8.24, the drill-in surface must show the
  demonstrated-by lineage (per Ship's framework-role-model
  Phase 4a). This is critical: an obligation-referenced risk
  gets its posture from the program's demonstration, not from
  the obligation clause itself.
- **Cascade events (14'.e)** must NOT be role-gated. A
  `residual_above_threshold` event fires regardless of which
  standard's controls the risk references.
- **`xfw_proposer` skip rule** applies: no bridge proposals in
  the `program → obligation` direction — that's DEMONSTRATES,
  handled deterministically. If a risk-related surface ever
  emits proposals (e.g. "link this risk to Art.32"), respect
  the same skip.

### 2. Case-file architecture pattern

Per [[ship-2-prime-casefile-arc-2026-07-15]] + Ship 2'.n
retirement of the legacy `rank_and_answer` body, the chat
pipeline is ONLY the case-file flow. Ship 14'.e's chat
surfaces must integrate with this pattern, not around it.

**Application to Risk Register:**

**a. New CaseFile field, not a parallel view.**

Per Ship 2' arc: "The CaseFile is the ground truth. Any new
signal (session, incidents, doc contexts) enters the CaseFile
once; digest + preservation both read from it. Never build a
parallel view."

`rag/casefile/types.py::CaseFile` gets a new optional field:
```
risks: list[RiskSummary] | None
```
Populated by the resolver when the classifier routes to
`posture_risk`. `RiskSummary` is a compact dataclass —
external_ref + threat + treatment_status + risk_score +
residual_level + review_date + linked control_refs.

**b. New digest slot — fixed budget.**

Add a `RISKS:` section renderer to `rag/casefile/digest.py`,
following the fixed-slots-empty-omitting discipline. Budget:
target ≤300 tokens for top-N risks (typically 5-8 rows).
Empty when `cf.risks is None`. No per-taxonomy branching.

Format (draft):
```
RISKS (N of M total):
- R-042 [high, open]  Ransomware in SaaS backups
    treat: mitigate  owner: CTO  residual: 12/25
    linked: A.5.15, A.8.13, Art.32
- R-017 [medium, in_progress]  Third-party data-processor breach
    treat: transfer  owner: DPO  residual: 8/25
    linked: A.5.19, Art.28
...
```

Token-budget test explicitly (< 300 tokens for 5 risks) —
follows Ship 2'.c pattern.

**c. Preservation-check on risk refs.**

Extend `extract_preservation_spec()` in
`rag/casefile/preservation.py` to include `required_risk_refs`
— the external_refs of risks the digest surfaced. If the LLM
drops a risk ref (e.g. mentions "our top ransomware risk" but
drops "R-042"), the repair pass appends via the existing
`↳ Compliance facts:` footer pattern (Ship 1.14 discipline).
APPEND-ONLY — never rewrite LLM prose.

**d. Classifier lock — deterministic routing, no LLM inference.**

Add `posture_risk` question_type behind Signal C at weight 1.00
(the top-tier per Ship 1). DOCUMENT_TOPIC_MAP entries route
risk queries deterministically — never rely on the LLM
classifier or gatekeeper to invent `posture_risk` intent.
Curator-authored mappings dominate.

Candidate entries:
- "top risks" / "highest risks" → `posture_risk`
- "overdue risks" / "risk review" → `posture_risk`
- "residual risk" / "residual risks" → `posture_risk`
- "risk register" → `posture_risk` (query-side; distinct from
  the intake DocType which routes uploads)

Per Ship 1 discipline: "prefer adding CLEAR_INTENT_PHRASES /
DOCUMENT_TOPIC_MAP entries over prompt-tuning the LLM
classifier or gatekeeper. Curator additions are top-tier
signal weight."

**e. Fail-loud, no silent fallback.**

Per Ship 2'.n retirement of `CASEFILE_ENABLED` + the legacy
fallback path: if the risk resolver errors, the error surfaces.
No hidden re-routes to legacy paths.

**f. Log to `chat_casefile_log` — observability.**

Existing schema_v68 columns already cover the new slot without
migration. `case_file_summary` gets a `risks_count` field;
`repair_events[]` includes any risk-related repair actions.
No new schema change needed for chat observability.

**g. Digest-hint pattern from Ship 13'.d.**

Continuous — the `→ guidance:` hint mechanism from
[[ship-13-prime-d-chroma-digest-eval-2026-07-22]] carries over.
A risk drill-in question hitting 6.1.2 still gets the 27005
guidance hint on the OBLIGATIONS line for 6.1.2. No new
mechanism needed.

### Reviewer discipline

Any sub-arc PR must include an explicit line in the memo
answering:
1. Does it split by role, or treat all roles first-class?
2. Does it add a new digest slot, or parallel to the CaseFile?
3. Does it deterministically route, or rely on LLM inference?
4. Does it add MUSTs, or maintain guidance-not-normative?

Where the answer is any of the wrong direction, cite the arc
memo that forbids it and revise.

## Related

- [[framework-role-model-arc]] — the role model this arc must respect
- [[ship-2-prime-casefile-arc-2026-07-15]] — the case-file pattern
- [[ship-13-prime-arc-retrospective-2026-07-22]] — the arc that
  motivated this one; 27005 grounding + digest promotion make
  risk-register a viable product surface
- [[ship-13-prime-b-iso27005-enrichment-2026-07-21]] — 6.1.2 and
  6.1.3 leaves already carry the 27005 authority paragraphs
- [[templates-v2-anchors-complete-2026-06-25]] — the xlsx
  template pattern Ship 14'.b will reuse
- [[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] — the
  `*_display` companion pattern all Ship 14 API responses use
- Ship 12'.a evidence-cascade concept — risk-register events
  fit naturally into the cascade taxonomy that Ship 6 built
