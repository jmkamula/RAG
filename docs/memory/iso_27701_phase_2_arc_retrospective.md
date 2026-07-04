---
name: iso-27701-phase-2-arc-retrospective
description: "SHIPPED 2026-07-03 → 2026-07-04 in three batches (Batch 1 §A.7.2 + §B.8.2 conditions / Batch 2 §A.7.3 rights + §A.7.4 PbD + §B.8.3-4 mirrors / Batch 3 §A.7.5 + §B.8.5 transfers). Full ISO 27701 Annex A (controller) + Annex B (processor) as a first-class standalone framework in the platform. 49 controls · 196 EvidenceRequirements · 1,158 ChecklistItems · 112 typed bridge edges (26 SUPPORTS 27701→27001 + 86 IMPLEMENTS 27701→GDPR per Annex D) · 49 posture rows on Arion (dual controller+processor) · 49 documents in the new iso27701_2019 Chroma collection. Two new curation-workflow scripts established the pattern for onboarding any copyrighted standard without a source JSON. Baseline eval (197/200) preserved across every batch — no regressions. Phase 2 curation is DONE. Post-Phase-2 integration work (LLM prompt scope + classifier short-circuits + Get Started interleave + eval cases) is separate and deferred to a Phase 3 batch."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

Full ISO 27701:2019 Annex A + Annex B curated to the platform's
Style-v2 4-leaf-per-control depth. Bridges the framework to both
ISO 27001 (its parent) and GDPR (via Annex D), so that a query
about a 27701 control can cite the 27001 information-security
control it augments AND the GDPR Article it operationalises.

**By the numbers:**

| | Batch 1 | Batch 2 | Batch 3 | Total |
|---|---|---|---|---|
| Controls | 14 | 23 | 12 | **49** |
| Leaves | 56 | 92 | 48 | **196** |
| ChecklistItems | ~330 | ~500 | ~330 | **~1,158** |
| SUPPORTS edges | 6 | 11 | 9 | **26** |
| IMPLEMENTS edges | 28 | 37 | 21 | **86** |
| Arion posture rows | 14 | 23 | 12 | **49** |
| Chroma documents | 14 | 23 | 12 | **49** |
| Lines added | ~2,180 | ~2,750 | ~1,400 | **~6,300** |
| Commits | f817ece | f5cdbb1 | (batch 3) | 3 |

**All 49 controls are curated to the same shape as ISO 27001 Phase B
2026-05-31 → 2026-06-02:** procedure + register + scope + review
per op_process 4-leaf spine.

## The pattern that made this work

The Batch 1 establishment cost of two new workflow scripts paid
back immediately in Batches 2 + 3:

- `scripts/seed_27701_requirement_nodes.py` — hand-authored Seed
  list of RequirementNode shells (title + obligation text from the
  standard). This replaces the source JSON that ISO 27001 + GDPR
  have but we can't check in for 27701 (copyright).
- `scripts/index_27701_to_chroma.py` — reads 27701 nodes from Neo4j
  post-loader and upserts into COL_27701 + COL_ALL without touching
  ISO/GDPR collections.

Batch 2 + Batch 3 both required only:
1. Extend the seed list
2. Author specs + register in `ALL_EVIDENCE_REQUIREMENTS`
3. Author bridges (extend an `ISO27701_BATCH{N}_EDGES` block)
4. Run seed + loader + bridge-loader + chroma indexer
5. Write posture SQL for Arion
6. Restart API + eval baseline

**Pattern for onboarding any next copyrighted standard** (TISAX,
SOC 2, ISO 27017, 27018, 29151, NIST 800-53, PCI, HIPAA):

1. `KNOWN_STANDARD_IDS` in `relationship_catalog.py`
2. `_STANDARD_LABEL_MAP` / `_STANDARD_DISPLAY` / `humanizeStandardId`
   (mostly wired already for future frameworks —
   [[iso-27701-phase01-2026-07-03]])
3. `scripts/seed_{std}_requirement_nodes.py` per batch
4. `COL_{STD}` in `vector/indexer.py` + `search_{std}` helper in
   `vector/retriever.py`
5. `scripts/index_{std}_to_chroma.py` for partial refresh
6. Author EvidenceRequirements in `document_requirements.py`
7. Author bridges in `relationship_catalog.py`
8. Seed posture for reference tenant

## Critical bridges the arc established

The point of bringing 27701 in wasn't just to add another framework
— it was to prove that the platform can express the natural
compliance-industry mapping between (privacy-augmented ISO
27701) → (ISO 27001 security foundation) → (GDPR legal
requirements). The 26 SUPPORTS + 86 IMPLEMENTS edges make this
mapping structurally readable to the RAG + posture engine.

Notable bridges (illustrative):

- **A.7.4.9 → A.5.14 + A.8.24** — PII transmission controls bridge
  privacy transmission expectations to 27001 info-transfer policy
  and cryptography. Any A.5.14 chat query now surfaces its 27701
  privacy overlay.
- **A.7.3.6 → A.8.10** — erasure right rides on top of
  information-deletion capability. Both a philosophy statement and
  a routing hint for the engine.
- **A.7.5.1 → Art.44/45/46/47/48/49** — the entire GDPR Chapter V
  transfer regime hangs off a single 27701 control. Any 27701
  transfer-basis chat surfaces the full Chap V hierarchy.
- **A.7.2.5 → Art.35 + Art.36** — PIA control operationalises the
  GDPR DPIA + prior-consultation regime. Certification pathway
  to demonstrating Art.35 compliance.
- **B.8.2.1 + B.8.2.2 + B.8.5.4-8 → Art.28** — every processor
  contract clause maps to Art.28 subclauses. This is the
  auditor's mental model made structurally computable.

## Arion posture snapshot

Arion (dual controller + processor tenant) end state:

- **1 Comply**: 0 — no 27701 control fully satisfied on Day 1 of
  PIMS work
- **36 OFI**: mature GDPR programme provides substance for most
  27701 controls but not privacy-specific formalisation
- **11 NC**: A.7.2.5 (no PIA program), A.7.3.5 (formal objection
  mechanism), A.7.3.7 (third-party notification), A.7.4.4-6
  (minimisation, end-of-processing, temp files), A.7.5.3 + A.7.5.4
  (transfer + disclosure records), B.8.2.3 (marketing exclusion),
  B.8.2.4 (infringing instruction), B.8.4.1 (processor temp files)
- **1 N/A**: A.7.2.7 (no joint controllers)
- **1 N/A**: A.7.3.10 (no solely-automated decisions with legal
  effects)

**Distribution reflects a real pre-PIMS-certified tenant:** GDPR
carry-over + SOC 2 controls give partial coverage everywhere
(OFI), specific privacy-native artefacts (PIA program, specific
registers) are missing entirely (NC), and one control is
non-applicable in principle (N/A joint controller).

## Baseline eval preservation

All three batches ran the 199-case eval + kept the baseline at
**197/200 · 1 WARN · 2 FAIL** (same known-stochastic set: #16 A.5.18
LLM jitter, #27 state-drift, #200 dejargonize edge).

No batch introduced a regression. **The single-lookup-per-case
posture_check path was fast enough that adding 49 new controls +
196 new leaves + 112 new bridges did not slow the eval measurably.**

## What's NOT done (deferred integration)

Phase 2 is curation. **Integration work is deferred:**

- **LLM system prompt** — `RANK_AND_ANSWER_SYSTEM.scope_block` in
  `rag/llm_answer.py` still enumerates only ISO 27001 + GDPR.
  The LLM knows 27701 exists via the "Arion implements ISO 27701:2019"
  context line but no scope enumeration. Result: chat may cite 27701
  controls Layer-1 for direct queries, but the model's own
  disambiguation heuristics don't treat 27701 as a first-class
  citable standard.
- **Classifier short-circuits** — no `CLEAR_INTENT_PHRASES` patterns
  for 27701-specific queries. "our PIMS posture?" hits the LLM
  classifier route.
- **Get Started page** — `_ANCHOR_LEAVES` in `rag/journey/state.py`
  remains 20 ISO 27001 anchors. Design doc option (c) was to
  interleave 27001 + 27701 in recommended order (do 27001 ISMS
  scope before 27701 PIMS scope extension). Not implemented.
- **Templates block** — `build_templates_block()` filters cited
  refs; 27701 refs will produce cards but the primary_download URL
  path needs a 27701 template scaffold (`db/templates/req__27701*.md`)
  which doesn't exist yet.
- **Eval cases** — no 27701-specific EvalCase in `tests/eval_suite.py`.
  Original design doc target was 5-8 new cases per §7.3 + §7.5 +
  cross-framework smoke tests.
- **`scope_loader.queryable_standards`** — 27701 still gated behind
  `standards.loaded_in_graph = false`. This gate needs to flip now
  that curation is done + Neo4j nodes exist.

## Recommended next step (Phase 3?)

**Flip the queryable-standards gate + add scope_block enumeration**
as a small "27701 goes live for queries" batch. That's the minimum
needed to close the curation-to-chat gap. Everything else
(templates, Get Started, eval cases) can follow as smaller batches.

## Related

- [[iso-27701-phase01-2026-07-03]] — pre-curation setup + Arion
  dual-role amendment
- [[iso-27701-batch1-2026-07-03]] + [[iso-27701-batch2-2026-07-04]] +
  [[iso-27701-batch3-2026-07-04]] — per-batch memos
- [[curation-phase-b-retrospective]] — the ISO 27001 + GDPR
  playbook this arc reused verbatim
- `docs/framework_27701_design.md` — original design doc; some
  decisions revised in-flight (D3 20 anchors → full 49; D4 Annex A
  only → both A + B)
- [[dejargonize-ux-pass-2026-07-01]] — vocabulary any 27701
  tenant-facing surface must respect
