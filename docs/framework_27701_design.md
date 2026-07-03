# ISO 27701 Framework Extension — Design Doc

**Status:** design (2026-07-03). Companion to
[framework_readiness_27701.md](framework_readiness_27701.md), which
scoped the strategic case for 27701 as first multi-framework
expansion. This doc turns that brief into an executable design with
the open decisions locked and the phased plan aligned to the current
codebase (post-templating arc, post-cascade arc, post-dejargonize
pass, post-Tier-4 starter kit).

Related retrospectives that shaped the current baseline:

- [cascade arc retrospective](cascade_arc_retrospective_2026_06_30.md) — the relationship_catalog + 11 edge types + 505 typed edges we'll extend
- [curation Phase B retrospective](curation_phase_b_retrospective.md) — the multi-leaf curation playbook for 27001 + GDPR
- Memory: [[dejargonize-ux-pass-2026-07-01]], [[tier4-starter-kit-arc-2026-07-02]] — the tenant-facing conventions any new 27701 surface must respect

## Motivation

ISO 27701 is the strongest test case for a truly multi-framework
architecture:

- **Parent-extending** — 27701 extends 27001. Every 27701 control
  cites a 27001 parent that it privacy-augments.
- **Peer-mapping** — 27701 Annex C explicitly maps to GDPR
  Articles. Certifiable operationalization of GDPR.
- **Role-gated** — Annex A applies to controllers, Annex B to
  processors. The `applies_when` DSL we already use for
  profile-fact gating is the exact right hammer.

Adding 27701 exercises every cross-framework path the product
wants to support. If the schema absorbs 27701 cleanly, the same
shape works for TISAX/VDA (extends 27001), 27017/27018 (extend
27001), SOC 2 (peer-maps to 27001 via TSC), NIS2 / DORA / AI Act
(peer-map to GDPR).

## Architectural decisions locked

The readiness brief left five open decisions. Locking them here as
the design-doc-of-record. Change with an ADR block, not by edit.

### D1 — Extension model: standalone with SUPPORTS edges

27701 controls are curated as **first-class standalone requirements**
with their own MUSTs, evidence types, and posture verdicts. They
carry outbound `SUPPORTS` edges to the 27001 parent they augment,
and outbound `IMPLEMENTS` edges to the GDPR articles they
operationalize.

**Not doing:** an implicit "27701 = 27001 + patch" derivation
model. Tempting because it compresses the catalog, but the auditor
trail suffers — a 27701 finding needs to stand alone in a
posture_controls row, with its own gap_description and its own
approval history. Same treatment as GDPR articles today.

**Consequence:** duplicated MUST authoring where 27701 restates a
27001 MUST verbatim. Acceptable — this is what the compliance
industry treats as normal.

### D2 — Edge type: use existing SUPPORTS + IMPLEMENTS, not a new EXTENDS

The relationship_catalog has 11 edge types today. The two we need
for 27701 already exist:

- `SUPPORTS` — "control A helps satisfy control B without being
  identical". Perfect for 27701 → 27001 (27701 §7.2 supports 27001
  A.5.34 by adding privacy-specific requirements on the same
  processing).
- `IMPLEMENTS` — "control A is a certifiable operationalization
  of law/obligation B". Perfect for 27701 → GDPR (27701 Annex A.7.4
  implements GDPR Art.6 lawfulness by requiring documented
  legal-basis assessment).

**Not adding EXTENDS.** The readiness brief argued for it on
semantic-distinctness grounds; on reflection the product doesn't
consume the distinction anywhere the existing two edges wouldn't
serve. If we later find a query that needs the tighter semantic
("parent standard extension" vs "supporting relationship"), we
add it then.

### D3 — Anchor cut: 20 v2 anchors, Annex A only (controllers), v1

For the v1 curation batch, ship:
- **20 hand-refined v2 anchor templates** for the highest-value
  27701 Annex A controls. Mirror the 27001 v2 anchor treatment —
  full MUST detail, tenant-authored guidance prose,
  business_description, cross-framework citations, evidence_type
  chosen per shape.
- **Auto-scaffold** the remaining ~10 Annex A controls as v1
  templates (like scripts/generate_template_scaffolds.py did for
  27001). Coverage without depth.
- **Skip Annex B (processors)** — deferred to a v2 batch. Annex B
  is smaller (~20 controls) and can follow once Annex A patterns
  are proven.

The 20-anchor list (proposed — refine with 27701 in hand):

```
27701 §5.x — PIMS management-system extensions (7 anchors):
  5.2  PIMS Context Extension
  5.3  PIMS Leadership Extension
  5.4  PIMS Planning Extension          (parents 27001 §6.1.2/3)
  5.5  PIMS Support Extension
  5.6  PIMS Operation Extension
  5.7  PIMS Performance Evaluation Extension
  5.8  PIMS Improvement Extension

Annex A — controller-specific controls (13 anchors):
  A.7.2   Conditions for collection and processing
  A.7.2.2 Identify lawful basis
  A.7.2.3 Determine when consent required
  A.7.2.4 Obtain and record consent
  A.7.2.5 Privacy impact assessment (DPIA)
  A.7.2.6 Contracts with PII processors
  A.7.2.7 Joint PII controllers
  A.7.3.2 Determining PII subject rights
  A.7.3.3 Determining fulfilment of PII subject rights
  A.7.4   Privacy by design + by default
  A.7.5.2 Countries + international organisations to which PII may be transferred
  A.7.5.3 Records of transfers
  A.7.5.4 Records of PII disclosure to third parties
```

Rationale: the 20 anchors span (a) the whole PIMS management-system
extension and (b) the controller obligations with tightest GDPR
mapping (Chap II/III/V Articles). A tenant working through these
20 covers 80% of the "PIMS certified" story.

### D4 — Arion opts in; keep GDPR as separate primary; Annex B later

- **Arion is a controller** (per tenant profile). We backfill 27701
  Annex A posture for Arion during Phase 4 seeding.
- **GDPR stays as its own primary framework**, not subsumed. Rationale:
  GDPR is law (not certifiable), and Arion cites GDPR articles
  independently of whether they hold a 27701 certification. Two
  primaries can coexist.
- **Annex B (processors) deferred to a v2 batch.** Not because it's
  unimportant — because sequencing it after Annex A lets us reuse
  patterns without rebuilding them.

### D5 — Scope opt-in, not inferred

`scope_loader` today infers GDPR scope from data-processing signals.
27701 should require **explicit subscribe** — it's a deliberate
certification choice, not a derivable consequence of "you process
PII". Add a `tenant_framework_subscription` table (or reuse
`tenants.applicable_standards`) with explicit `ISO27701:2019`
membership.

## Data model

### standard_id convention

`ISO27701:2019` — matches `ISO27001:2022` + `GDPR:2016/679` pattern.
Already handled by `humanizeStandardId()` (frontend) +
`_STANDARD_LABEL` (backend) — no code change needed for the label.

### RequirementNode + EvidenceRequirement shape

Same as 27001/GDPR. Naming conventions:

- Control nodes: `ISO27701:2019:5.2`, `ISO27701:2019:A.7.2.6` etc.
- Leaf ids: `req:5.2:pims_scope_statement`, `req:A.7.2.6:controller_processor_contracts`, …
- MUST item ids: `item:A.7.2.6:contract_scope`, …

27701's nested numbering (§7.2.6.x) works with the existing regex — no
changes needed. Verify with a smoke test on the sub-sub-sub case.

### Role-gate via `applies_when`

Every Annex A leaf gets `applies_when = {"role": "controller"}`.
Future Annex B leaves would get `applies_when = {"role": "processor"}`.
Tenants with `role = ["controller", "processor"]` see both.

The `applies_when` DSL is already Phase-1 hardened
([[applies-when-phase1-regression-tests]]) and supported by the
loader + engine. No new code.

### Cross-framework edges

Two edge sets, both in `enrichment/relationships/relationship_catalog.py`:

**27701 → 27001** (SUPPORTS): every 27701 control that augments an
existing 27001 control gets a SUPPORTS edge to its 27001 parent.
Example: `27701:A.7.2.6 SUPPORTS 27001:A.5.19` (both are about
supplier / processor contracts).

**27701 → GDPR** (IMPLEMENTS): 27701 controls with a GDPR mapping in
Annex C get IMPLEMENTS edges. Example: `27701:A.7.2.2 IMPLEMENTS
GDPR:Art.6` (lawful basis identification).

Both edge types already loaded by `load_to_neo4j.py` — no new loader
work.

Annex C transcription: **manual, not LLM-assisted**. Precedent
matters for the next framework onboarding, and the mapping is only
~50 pairs.

## Product surfaces — what breaks, what needs work

### Dashboard heatmap

The heatmap renders columns per framework. Currently: 2 columns
(ISO 27001 + GDPR) plus a "Cross-Framework" section for the xfw
bridges. Adding 27701 as a third primary column requires:

- Verify the column layout works with 3 primaries. Should be a
  no-code change — `renderDashboard` iterates `d.frameworks`.
- Confirm the framework ordering: 27001 first (primary), 27701
  second (privacy extension), GDPR third (legal citation layer).
  Backend `_STANDARD_DISPLAY` + posture_loader ordering may need
  a hint.

### Chat cross-framework answers

`rank_and_answer` + the LLM system prompt already handle Layer 2
(cross-framework) nodes with `[XFW→ ref]` tagging. Adding 27701 as
a third framework should Just Work if:

- 27701 gets added to `RANK_AND_ANSWER_SYSTEM.scope_block` when in
  scope.
- The classifier recognises "27701" / "PIMS" / "privacy management
  system" as scope keywords.
- The xfw_proposer walks IMPLEMENTS edges from 27701 same as it
  does from 27001 today.

### Tier-4 templates_block

Any cited 27701 NC/OFI ref should produce a starter-kit card
alongside 27001/GDPR cards. `build_templates_block()` already
filters by cited_refs — no change needed, just verify with a
smoke test after curation.

### Get Started page

`_ANCHOR_LEAVES` in `rag/journey/state.py` is currently 20 ISO 27001
anchors. Options for 27701:

- **(a) Extend the same 20 anchors list to include 27701 anchors** —
  becomes ~40 anchors. Foundation gets bigger.
- **(b) Split by framework** — foundation lists per-framework, tenant
  picks which framework's foundation to focus on first.
- **(c) Merge sensibly** — 27001 + 27701 anchors interleaved in
  recommended order (do 27001 A.5.15 access policy, then 27701
  A.7.2.4 consent recording, etc.).

Recommend **(c)** — the anchors ARE the recommended sequence, and
27001/27701 anchors have natural dependencies (do the 27001 ISMS
scope before the 27701 PIMS scope extension).

### Chat streaming + LLM prompt

`RANK_AND_ANSWER_SYSTEM` has a `STANDARDS SCOPE` block enumerating
citable frameworks. Add `ISO27701:2019` when in scope. The rest of
the prompt (glossary, xfw tagging, etc.) is framework-agnostic —
27701 gets Layer 2 treatment when queried indirectly, Layer 1
treatment when queried directly.

## Phased build sequence

Six phases, eval-gated per phase. Total estimate: **5-7 days**.

### Phase 0 — Baseline snapshot (½ day)

- Snapshot eval baseline: `results/eval_pre_27701_baseline.csv`
- Confirm current state (197-198/200 known-stochastic)
- Read the ISO/IEC 27701:2019 standard PDF (prerequisite — see below)
- Verify Arion's role profile (`controller` confirmed)
- Update `docs/framework_readiness_27701.md` header to point at this
  design doc as the current-authoritative plan

### Phase 1 — Data foundations (1 day)

- Add `ISO27701:2019` to `applicable_standards` for Arion tenant
- Extend `_STANDARD_LABEL_MAP` in `rag/arion_graph.py` (verify —
  probably already there)
- Confirm `humanizeStandardId('ISO27701:2019')` returns
  `ISO 27701:2019`
- Add 27701 detection keywords to classifier (`pims`, `privacy
  information management`, `iso 27701`) — verify already present
- Add `tenant.applicable_standards` mechanism to opt in to 27701
- Post-conditions: `is 27701 compliant?` classifier routes correctly,
  even before any curation

### Phase 2 — Anchor curation (2-3 days)

- Author the 20 v2 anchor `EvidenceRequirement` entries in
  `enrichment/documents/document_requirements.py` following the
  27001 v2 anchor pattern:
  - `standard_id="ISO27701:2019"`
  - Full MUST detail with `text` + `id`
  - `should_contain` items where applicable
  - `evidence_type` chosen per shape (procedure / register /
    review_record / scope_note / policy)
  - `applies_when={"role": "controller"}`
  - `business_description` + `title` for the tenant-facing display
- Auto-scaffold the remaining ~10 Annex A controls as v1 via
  `scripts/generate_template_scaffolds.py` (extend to accept
  `--standard=ISO27701:2019`)
- Run `enrichment/documents/load_to_neo4j.py` — verify node counts
  (should add 30ish RequirementNodes + 100-150 ChecklistItems)
- Generate template scaffolds (v2 hand-refined for the 20 anchors,
  v1 for the ~10 rest) into `db/templates/req__*.md`
- Eval: existing 199 must stay at floor

### Phase 3 — Cross-framework wiring (½ day)

- Author 27701 → 27001 SUPPORTS edges in `relationship_catalog.py`
  (~30 edges, one per Annex A control that extends a 27001 parent)
- Author 27701 → GDPR IMPLEMENTS edges from Annex C mapping
  (~40-50 edges)
- Run relationship_catalog loader
- Verify xfw_proposer walks the new edges by running a test extraction
- Eval: existing 199 must stay at floor

### Phase 4 — Arion posture seed (½ day)

- Insert `posture_controls` rows for Arion × 27701 Annex A
- Assign initial findings matching Arion's actual state (OFI for
  partially-implemented, NC for missing, N/A for non-applicable —
  role-gated so processor-only controls are auto-N/A)
- Confirm engine sweep populates + Stage-2 proposals surface
- Confirm 27701 shows on the dashboard as a third framework column

### Phase 5 — Get Started + templates integration (½ day)

- Extend `_ANCHOR_LEAVES` in `rag/journey/state.py` — interleave
  27701 anchors into the 27001 sequence per the strategy in
  "Product surfaces" above
- Verify `JourneyState.foundation_anchors` includes 27701 entries
- Verify Get Started page renders the mixed sequence correctly
- Verify Tier-4 chat templates_block includes 27701 cited refs
- Add 27701 to `RANK_AND_ANSWER_SYSTEM` scope block

### Phase 6 — Eval + documentation (½ day)

New eval cases (5-8):

1. `is our ISO 27701 §7.2.4 (consent recording) compliant?` —
   direct posture on a 27701 leaf
2. `how does ISO 27701 map to GDPR?` — xfw shape validator
3. `what documents do we need for PIMS?` — document_inventory
4. `are we PIMS ready?` — posture_check with must_contain shape
   validator
5. `is ISO 27701 §7.2.6 compliant?` (a control that BOTH extends
   27001 A.5.19 AND implements GDPR Art.28) — three-way bridge
6. Optional: Stage-1 HITL path with 27701 finding
7. Optional: Get Started page shows 27701 anchors interleaved

Docs:

- Memory: new memo `iso_27701_v1_arc_2026_07_XX.md`
- MEMORY.md index entry
- CLAUDE.md build sequence: "ISO 27701 v1 — 20 v2 anchors + Annex A
  auto-scaffold + xfw wiring" as SHIPPED
- Update `framework_readiness_27701.md` header: "SUPERSEDED — see
  the v1 arc memo"

## Prerequisites (do before Phase 0)

1. **ISO/IEC 27701:2019 standard PDF** on hand. Not free; likely
   already acquired for Arion's 27701 certification path.
2. **Annex C GDPR mapping** extracted from the standard as a
   spreadsheet or YAML (~50 rows).
3. **Confirmation Arion is controller-only** (already known — profile
   says `controller`).
4. **4-day uninterrupted block** for continuous curation context.

## Stress-test signals to watch during the build

Per the readiness brief's architectural question list:

1. **Nested numbering (§7.2.6.x)** — verify RequirementNode.ref regex
   handles deeper nesting. Smoke test on the deepest sub-control.
2. **Three-way bridges** — a 27701 control mapping to BOTH 27001 (parent)
   AND GDPR (article). Test with §7.2.6 → A.5.19 + Art.28.
3. **Role-gating** — a controller-only tenant shouldn't see §8/Annex B
   controls (once those are curated). Verify with a synthetic
   processor-only tenant fixture.
4. **Multi-standard candidate lists** — a privacy policy uploaded by
   Arion might match doc_mappings for BOTH `27001:A.5.34`
   AND `27701:A.7.2.4`. Verify the extractor prompt + parse handle
   multi-standard candidates.
5. **xfw_proposer three-framework walk** — an A.5.19 finding should
   propose BOTH GDPR Art.28 AND 27701 A.7.2.6 findings simultaneously.
6. **Tier-4 templates_block with 27701 leaves** — verify the block
   correctly shows the right primary_download (docx for narrative
   27701 leaves, xlsx for register-shaped Annex A controls like
   A.7.5.3 records of transfers).
7. **Get Started page ordering** — 27001 ISMS scope must come before
   27701 PIMS scope in the sequence (the PIMS extends the ISMS).

## What "done" looks like

Acceptance criteria for the v1 27701 arc:

1. **Data**: ~30 27701 Annex A control nodes in Neo4j + ~100-150
   ChecklistItems + no schema regressions.
2. **Bridges**: SUPPORTS edges from every Annex A control to its
   27001 parent (where applicable) + IMPLEMENTS edges from every
   Annex A control to its GDPR Article per Annex C.
3. **Templates**: 20 hand-refined v2 anchor templates for 27701
   Annex A + ~10 auto-scaffold v1 templates + xlsx/docx renderers
   work.
4. **Posture**: Arion's 27701 Annex A posture visible on the
   dashboard as a third framework column, with role-gated N/A on
   any leaf `applies_when` excludes.
5. **Chat**: `is our ISO 27701 posture ok?` returns a Layer-1 answer
   citing 27701 leaves; `how does 27701 §7.2.6 relate to GDPR Art.28?`
   returns a cross-framework answer using the IMPLEMENTS edge.
6. **Get Started**: mixed 27001+27701 anchors in recommended order.
7. **Templates block in chat**: cited 27701 NC/OFI leaves produce
   starter-kit cards with the right format download.
8. **Eval**: 5-8 new 27701-specific cases PASS + existing 200 stay
   at floor.

## Open items for the tenant to resolve

Answer these before Phase 2 starts (curation is expensive to rework):

1. **Anchor list refinement** — the 20 anchors above are a proposal.
   Prefer we swap any out for higher-value picks based on Arion's
   actual audit priorities?
2. **Annex C source** — do you have the ISO 27701 → GDPR mapping
   extracted as a spreadsheet, or do we transcribe from PDF?
3. **Auto-scaffold vs skip for the remaining 10 Annex A controls** —
   coverage-without-depth (auto-scaffold) or ship 20 and revisit
   later (skip)?
4. **Annex B timing** — targeted for a v2 batch date, or open-ended?

Answer those, and Phase 0 can start.
