# ISO 27701 Onboarding Readiness Brief

> **STATUS 2026-07-03 — SUPERSEDED by
> [framework_27701_design.md](framework_27701_design.md).** This brief
> remains as the strategic-context document (why 27701 first, current
> readiness of code paths, work-breakdown estimates). The current-
> authoritative plan for execution lives in the design doc, which
> locks the five architectural decisions the brief had left open,
> aligns phase estimates with the current codebase (post-templating,
> post-cascade, post-dejargonize, post-Tier-4), and enumerates
> stress-test signals + acceptance criteria.
>
> **Phase 0 amendment (2026-07-03):** Arion Networks tenant profile
> shows `role_controller=true` AND `role_processor=true` per
> client_facts. Both Annex A (controller) and Annex B (processor)
> apply to the demo tenant, which affects design decision D4
> (originally "Annex B deferred to v2 batch"). Open item for the
> tenant to resolve before Phase 2.

## Original brief (retained as strategic context)

Strategic placeholder for the first multi-framework expansion. Drafted
end-of-day after today's intake-pipeline + LLM-provider strategy work;
not yet a plan to execute. When the framework #3 onboarding turn comes,
convert to a real plan + ADR.

## Why 27701 first

Three reasons, in priority order:

1. **Stress-tests the extension model** — 27701 is structurally an
   overlay on ISO 27001 (PIMS extending ISMS). If our schema can absorb
   27701 cleanly, the same shape works for any standard that extends
   an existing standard (TISAX/VDA extends 27001, ISO 27017/27018
   extend 27001, etc.).
2. **Highest readiness** — most pre-staged framework in the codebase
   (see § Readiness today). Smallest investment per learning extracted.
3. **Real tenant value today** — Arion already self-identifies as
   "ISO 27001 + ISO 27701" in `chat.py:198`. Closing the data gap
   matches existing positioning rather than requires new positioning.

If a different framework drove a contractual deadline (SOC 2 audit,
HIPAA requirement, AI Act enforcement), priority shifts. Absent that
forcing function, 27701 is the right first pick.

## Readiness today

### Code path (READY)

| Module | What's wired | Status |
|---|---|---|
| `rag/framework_refs.py:24` | `"ISO27701": ("ISO 27701", "controls")` display | ✓ |
| `rag/framework_refs.py:32` | Priority slot between 27001 + GDPR | ✓ |
| `rag/intake/enricher.py:30` | `ISO27701:2019` in known standards | ✓ |
| `rag/intake/enricher.py:40` | Detection keywords (`iso 27701`, `pims`, `privacy information management`) | ✓ |
| `db/workbook_importer.py:502` | PIMS workbook column parsing (`ISO27701:2019:<ref>`) | ✓ |
| `chat.py:198` | Tenant header advertises "ISO 27001 + ISO 27701" | ✓ |
| Storage convention | `ISO27701:2019:<ref>` validated across schema | ✓ |

The code paths assume multi-framework from the start. No new code is
needed for 27701 specifically — only data.

### Data (MISSING)

| Asset | Today | Needed |
|---|---|---|
| Neo4j `RequirementNode` | 0 nodes with `standard_id='ISO27701:2019'` | ~50-60 control nodes + per-leaf EvidenceRequirement structure |
| `db/doc_mappings/*.yaml` | 0 target 27701 leaves | ~10-15 YAMLs for PIMS-specific shapes (privacy policy, DPIA template, transfer impact assessment) |
| `db/must_fingerprints/*.yaml` | 0 catalogs for 27701 MUSTs | ~100-150 catalogs (4-5 MUSTs per leaf × 30-40 multi-leaf controls) |
| `db/workbook_mappings/*.yaml` | PIMS workbook column parsing exists but no leaf mappings | ~10-15 YAMLs if a PIMS workbook shape exists |
| Cross-framework bridges | 0 edges from 27701 → 27001 or 27701 → GDPR | ~30-50 `IMPLEMENTS`/`SUPPORTS` edges |
| Eval cases | 1 mention ("Should explain ISO 27701 bridge" in case #11 notes) | ~5-8 framework-specific posture queries |
| `posture_controls` seeds | 0 rows | ~50 rows per tenant subscribing to 27701 |

## What 27701 actually requires

Structure overview (read this before authoring Neo4j data):

**§5 PIMS-specific requirements** — extends ISO 27001 Clauses 4-10:
- §5.2 Context (extends 27001 §4)
- §5.3 Leadership (extends §5)
- §5.4 Planning (extends §6)
- §5.5 Support (extends §7)
- §5.6 Operation (extends §8)
- §5.7 Performance evaluation (extends §9)
- §5.8 Improvement (extends §10)

**§6 PIMS-specific guidance for ISO 27002 controls** — adds privacy
guidance to existing A.5-A.8 Annex A controls. Examples:
- §6.2.1.1 — PIMS-specific application of A.5.x

**§7 Additional guidance for PII controllers** — controller-specific
obligations. ~31 sub-controls.

**§8 Additional guidance for PII processors** — processor-specific
obligations. ~18 sub-controls.

**Annex A (normative)** — PIMS-specific objectives + controls (not the
same as ISO 27001 Annex A).

**Annex B (normative)** — PIMS-specific objectives + controls for
processors.

**Annex C (informative)** — GDPR mapping. The single biggest leverage
point — most §7 and §8 controls map 1:1 or 1:N to GDPR articles.

### Profile fact: controller vs processor

A tenant is one of:
- Controller-only — §7 applies, §8 doesn't
- Processor-only — §8 applies, §7 doesn't
- Both — §7 + §8 both apply (common for SaaS platforms)

This is a new `profile_fact` dimension following the GDPR pattern
already in use (e.g. Art.7 children — `applicable=false` when tenant
profile excludes it). Per-tenant scope filters §7 vs §8 applicability.

## Curation work breakdown

Five sequential phases, each gated on eval coverage. Total estimate:
**5-7 working days**.

### Phase A — Neo4j data load (~1.5 days)

- Author a one-shot Cypher script: 27701 controls (PIMS-specific §5-6
  + Annex A + Annex B + §7 + §8) as `RequirementNode` rows
- Multi-leaf `EvidenceRequirement` structure following ISO 27001 pattern
  (procedure / register / review / scope leaves where applicable)
- `ChecklistItem` MUST + SHOULD per leaf

Reuse the curation playbook from
`[[curation-phase-b-retrospective]]`. Most leaves should mirror their
ISO 27001 parent's shape (procedure/register/review structure).

### Phase B — Cross-framework bridges (~1 day)

Two bridge sets:

1. **27701 → 27001**: most 27701 controls extend an existing 27001
   control. The extension relationship: `(27701_node)-[:EXTENDS]->(27001_node)`.
   (May need a new edge type or reuse `IMPLEMENTS` — see § Open
   decisions.)
2. **27701 → GDPR**: §7 and §8 controls map cleanly to GDPR articles
   via Annex C. Use existing `IMPLEMENTS` / `SUPPORTS` edges following
   the GDPR ↔ 27001 pattern.

Annex C is the single biggest accelerator — the mapping is already
done in the standard, just needs transcription to Cypher.

### Phase C — doc_mappings (~1 day)

PIMS-specific document shapes (those that don't already exist in the
298 ISO+GDPR YAMLs):

| Doc shape | Filename fingerprints |
|---|---|
| Privacy policy / PIMS policy | `[privacy, policy]`, `[pims, policy]` |
| Privacy notice (controller artefact) | `[privacy, notice]` |
| Data processing impact assessment (DPIA) | `[dpia]`, `[data, protection, impact]` |
| Records of processing activities (RoPA) | `[ropa]`, `[records, processing]` |
| Sub-processor list | `[subprocessor]`, `[sub, processor]` |
| Transfer impact assessment (TIA) | `[tia]`, `[transfer, impact, assessment]` |
| Data sharing agreement (DSA) | `[data, sharing, agreement]` |
| DPA template (controller) | `[dpa]`, `[data, processing, agreement]` |
| Cookie/consent notice | `[cookie, notice]`, `[consent, banner]` |
| Privacy training materials | `[privacy, training]`, `[awareness, privacy]` |

Many overlap with existing GDPR mappings (Art.30 ↔ RoPA already
mapped). The work is largely about extending existing YAMLs' target
leaves to include 27701 equivalents.

### Phase D — must_fingerprints (~1.5 days)

Use `scripts/gen_leaf_scan_catalog.py` to autogenerate skeletons, then
refine. Per the [[leaf-scan-catalog-campaign-2026-06-14]] playbook,
3-7 min per leaf with v3 generator → ~30-50 catalogs × 5 min = 2.5-4
hours of focused work.

Apply the lessons from the autogen-catalog noise issue surfaced today:
- Avoid generic anchor tokens (`[register]` alone, `[activity]` alone)
- Require multi-token trigrams for binding-relevant MUSTs
- Use `[[extractor-catalog-crosscheck-2026-06-15]]` as the validation
  surface — after seeding catalogs, run an extraction on a known doc
  and check crosscheck disagreement rate per MUST

### Phase E — Eval coverage (~0.5 day)

Add 5-8 eval cases following existing patterns:
- "What is our ISO 27701 posture?" (gap_analysis shape)
- "What's our DPIA status?" (document_inventory)
- "Are we PIMS compliant?" (posture_check, structural assertion)
- "How does ISO 27701 §7.2 map to GDPR?" (cross_framework, shape validator)
- One per-leaf NC verification (engine path)
- One Stage-1 HITL path verification
- One workbook → posture flow if PIMS workbook shape exists on Arion

Per the [[feedback-eval-state-drift]] rule, prefer structural
assertions over data-specific locks where possible.

### Phase F — Per-tenant seeding (~0.5 day)

For Arion (the first tenant):
- Tenant profile updates: `profile_fact.pims_role = ['controller', 'processor']`
- Posture seed: 27701 controls with initial finding state matching
  Arion's actual self-assessment (`OFI` for partially-implemented,
  `NC` for missing, `N/A` for non-applicable per profile)
- Run engine sweep, confirm posture_controls populates correctly

## Architectural stress-test questions

This onboarding is the test of "is the architecture really
framework-agnostic". Watch for these signals during the work:

1. **Does the schema accommodate 27701 numbering quirks?** 27701
   uses sub-sub-section numbering (§7.2.6.x) that's deeper than
   ISO 27001's flat A.5.18 style. Verify `RequirementNode.ref` and
   downstream code handle this.

2. **Does the bridge model handle three-way mappings?** A single
   27701 control may map to 27001 (parent) + GDPR (article). Today's
   `IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE` edges are pairwise. Test
   with a real example: 27701 §6.10 → 27001 A.5.34 + GDPR Art.5.

3. **Does profile_fact gating work as expected?** A controller-only
   tenant shouldn't see §8 controls in their queue. Verify with a
   synthetic processor-only tenant fixture.

4. **Does the LLM extractor handle 27701 candidate lists?**
   Post-B path expects per-MUST candidates from Neo4j. With 27701
   added, a privacy policy doc might match doc_mappings for BOTH
   ISO 27001 A.5.34 AND ISO 27701 §6.10.x. The candidate list could
   span two standards in one extraction call. Verify the prompt + parse
   handle multi-standard candidates.

5. **Does `xfw_proposer` propose 27701 from existing ISO 27001
   findings?** Today's flow proposes GDPR from 27001. With 27701
   bridges in place, an A.5.34 finding should also propose a 27701
   §6.10 finding. Same code path, more candidates.

## Open decisions

1. **`EXTENDS` edge type vs reuse `IMPLEMENTS`.** 27701's overlay
   relationship to 27001 is semantically distinct from GDPR's
   bridge relationship. Adding `EXTENDS` is cleaner; reusing
   `IMPLEMENTS` is faster. **Lean toward adding `EXTENDS`** — clarity
   compounds at SOC 2 / AI Act onboarding.

2. **Annex C mapping import: manual or LLM-assisted?** Annex C lists
   ~50 ISO 27701 → GDPR mappings. Manual transcription is ~2 hours;
   LLM-assisted (Claude reads the standard, outputs Cypher) is faster
   but introduces transcription errors. **Recommend manual** —
   precedent matters for next framework's bridge mappings.

3. **Workbook shape: does Arion have a PIMS workbook?** If yes,
   workbook_mappings YAMLs are highest-leverage per-leaf binding.
   If no, skip Phase F workbook variant. **Check Arion uploads** before
   Phase A starts.

4. **Tenant scope auto-inference vs explicit subscribe.** Today's
   `scope_loader` infers GDPR from data processing. Should it infer
   27701 from "tenant has GDPR scope + processes structured PII"? Or
   should 27701 require explicit subscribe? **Lean explicit** — 27701
   is a deliberate certification choice, not a derivable consequence.

5. **Annex A vs Annex B priority.** 27701 has TWO normative annexes
   (A for controllers, B for processors). For a both-role tenant,
   both apply. Authoring order: A first (controllers more common),
   B second.

## Eval baseline before starting

Per the discipline established today, snapshot eval state before
Phase A:
- 199/199 baseline (or current state)
- Existing case #11 mentions "ISO 27701 bridge" — confirm it still
  passes
- Document Arion's pre-27701 posture state for comparison after seeding

## Test plan: what "27701 done" looks like

Acceptance criteria for the onboarding:

1. **Schema**: 50-60 27701 nodes in Neo4j, no schema regressions
2. **Bridges**: every 27701 control with a clear ISO/GDPR analog has
   a bridge edge
3. **Eval**: 5-8 new 27701-specific cases all PASS; existing 199
   stay green
4. **Arion posture**: 27701 control list visible in dashboard,
   per-control NC/OFI/Comply/N/A as expected per profile_fact
5. **Doc upload smoke test**: upload Arion's privacy policy, verify
   it binds to both 27001 A.5.34 AND 27701 §6.10 leaves (per-MUST
   binding from B + multi-standard candidate list)
6. **Stage-1 HITL**: 27701 proposals surface alongside 27001 in the
   queue; tenant approves/rejects same flow
7. **Cross-framework query**: "How does our 27701 §7.4 status map to
   GDPR Art.6?" returns a coherent bridge answer

## Prerequisites for executing

1. **Standard text on hand** — ISO/IEC 27701:2019 PDF (paid standard,
   not free). Without the actual normative text, curation is
   guesswork. Likely already acquired during Arion's certification.
2. **Annex C extracted** — the GDPR mapping table, in machine-readable
   form. Spreadsheet or YAML is fine.
3. **Arion's PIMS scope statement** — controller-only? processor-only?
   both? Drives §7 vs §8 applicability per-tenant.
4. **Decision on EXTENDS edge type** (open decision #1) — affects
   data load shape.
5. **A 4-day uninterrupted block** — the curation arc benefits from
   continuous context; spreading across weeks loses momentum.

## What this brief isn't

- Not a project plan. Phase estimates are rough; firm numbers belong
  in a real plan when execution begins.
- Not a curation guide. Detailed curation patterns live in
  `[[curation-phase-b-retrospective]]` and the per-batch memory entries.
- Not vendor-/tooling-specific. Same Cypher + YAML toolchain that
  curated ISO 27001 + GDPR.

## Related

- `[[curation-phase-b-retrospective]]` — the curation arc that proved
  the multi-leaf model on ISO 27001 + GDPR
- `[[intake-pipeline-architecture]]` — the intake side that this
  framework's data will flow through
- `[[per-must-binding-in-extractor-2026-06-15]]` — the extractor work
  that this framework's leaves will benefit from natively
- `[[extractor-catalog-crosscheck-2026-06-15]]` — the validation
  signal for catalog quality on new MUSTs
- `[[leaf-scan-catalog-campaign-2026-06-14]]` — the catalog authoring
  playbook
- `[[llm-provider-strategy]]` — orthogonal but related; 27701's curation
  doesn't depend on LLM provider, but post-onboarding extraction does

## Next-thread starter

When this work begins, the first commits should be:

1. Snapshot eval baseline (`results/eval_pre_27701_baseline.csv`)
2. Author the 27701 Neo4j loader (one-shot Cypher script in `db/`)
3. Run loader, verify node counts + edge counts
4. Add open-decision answers as ADR comment block at top of loader
5. Phase B onward in batches, eval-gated per batch

Same shape as the 2026-05-26 → 06-02 Phase B arc but tighter — one
framework, not two, with the playbook already proven.
