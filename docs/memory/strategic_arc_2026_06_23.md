---
name: strategic-arc-2026-06-23
description: "Arc-level summary of 2026-06-23 (15 commits since 9150a0b). Day combined planned MVP work (PDF Layer A, re-extract endpoint) with a deep architectural arc surfaced by tenant uploads (Direction C two-pass extraction + schema_v43 per-MUST overrides). Plus two data-quality cleanups (NULL node_id backfill, workbook bare-Annex-A normalization, physical-scope N/A application). Eval baseline confirmed at 198/199 twice through the day. Sibling of [[strategic-pause-2026-06-15]]."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The day at a glance

A planned-MVP-work day that turned into an architectural arc when the
tenant re-uploaded their updated Access Control Policy and ISO 27001
workbook for testing. Each upload surfaced a deeper issue than the
last:

1. **Access Control Policy** updated → why didn't posture move?
2. → Per-MUST binding worked but missed metadata MUSTs (recall ceiling)
3. → Direction C two-pass extraction designed + shipped
4. → A.5.15 flipped NC → OFI (real movement)
5. → Advisory now leaks "physical" into chat → schema_v43 tenant N/A
6. → Workbook re-uploaded → bare Annex A refs → cleanup data fix
7. → "Not per ISMS Scope" evidence → physical-N/A application
8. → NULL node_id rows surfaced → broader backfill data fix

## What shipped (15 commits)

| Commit | What | Memory entry |
|---|---|---|
| `9150a0b` | PDF reader Layer A | [[pdf-layer-a-2026-06-19]] |
| `3fde996` | Re-extract endpoint + duplicate UX | [[reextract-endpoint-2026-06-23]] |
| `ec7f2bb` | Per-MUST recall strategy doc + prompt+cap | docs/per_must_recall_strategy.md |
| `7a0f5b3` | Direction C — pass-2 targeted recall | [[per-must-recall-direction-c-2026-06-23]] |
| `f7fdfc9` | schema_v43 — tenant_must_overrides | [[tenant-must-overrides-v43-2026-06-23]] |
| `590d315` | CLAUDE.md — 198/199 baseline | n/a (config) |
| `c366c55` | Data fix: NULL node_id backfill | (this entry's sub-topic) |
| `f4677ba` | Data fix + memory: workbook bare Annex A | [[workbook-importer-bare-annex-a-2026-06-23]] |
| `08c7872` | Data fix: physical N/A + ISMS 7.x restore | (this entry's sub-topic) |
| `74790df`, `92fd92f` | Memory commits | (the entries themselves) |

## Architectural insights surfaced

### 1. Single-pass LLM extraction has a recall ceiling

Per [[per-must-recall-direction-c-2026-06-23]] — empirically validated
through 3 iterations on the same doc:

- Morning extract (cap=15): 14 findings
- Cap+prompt fix: 17 findings
- Direction C pass-2: 22 findings

The remaining gap (still missing some MUSTs) is structural. Direction
A (form-as-completion) catches what C can't.

### 2. Scope declarations are first-class, not evidence claims

Per [[tenant-must-overrides-v43-2026-06-23]] — a MUST that's N/A for
a tenant's scope (e.g. physical-scope MUSTs for cloud-only tenants)
needs its own data type. Not a `document_findings` row (those are
evidence). schema_v43 introduced `tenant_must_overrides`.

### 3. Posture data has historical drift

NULL `node_id` on 28 posture_controls rows on Arion — invisible to the
engine for who-knows-how-long. Surfaced when A.5.15 wouldn't flip during
the Direction C work. Backfilled 11 valid controls; retired 5
misclassified/obsolete (Art.28/30 with wrong standard_id; 2013-era
A.6.1.x); 9 custom X.XXXX.99 left inactive by design.

**Rule**: any tenant data created pre-2026-06-08 may have NULL node_id.
New onboarding paths always populate node_id.

### 4. Workbook intake has multiple disambiguation traps

Per [[workbook-importer-bare-annex-a-2026-06-23]]:

- **Bare numbering**: workbook uses bare 5.x/6.x/7.x/8.x for both
  ISMS clauses (Support/Planning/etc.) AND Annex A controls (controls
  5.4+ are unambiguously Annex A; 5.1-3 are ambiguous)
- **"Not per ISMS Scope" claims**: evidence text declares N/A but
  workbook intake records as `status='present'` (mis-categorization)
- **Bare 7.x mixed semantics**: same workbook uses bare 7.2 for BOTH
  ISMS clause 7.2 (Competence Records) AND A.7.2 (Physical entry
  controls) in different rows — only sheet context disambiguates

These are open architectural issues. Today's data fixes are surgical;
permanent fixes need context-aware workbook importer (sheet name →
normalization rule + "not per ISMS scope" → not_applicable status).

### 5. Headline-recompute response is misleading

The `_recompute_posture_for_control` returns "finding/prior_finding"
in the approve API response, suggesting flips. But the engine's
actual verdict (multi-leaf strict) determines whether posture
actually moves. After 262 approved findings on the workbook upload:
- API response showed 100+ flips
- Actual posture_controls changes: 0
- Engine refused flips on unbound evidence + insufficient per-MUST coverage

Operators reading the approval response are misled. Worth either
hiding the legacy headline path or labelling it as a recommendation
not an actual flip.

## Eval discipline held

| Run | Result | Notes |
|---|---|---|
| Direction C eval | 196/199 | #1+#5 "physical" leaked from new advisory |
| Schema_v43 eval | 197/199 | #1 fixed; #5+#16 LLM-stochastic |
| **Baseline-confirm (clean)** | **198/199** | only #16 |
| **Post-workbook eval (close)** | **197/199** | #5+#16 LLM-stochastic |

198/199 confirmed as the honest target — #16 in the ~85-95% pass band,
no architectural regressions.

## Net Arion posture state at end of day

```
N/A           17
NC           144
OFI            4
Not assessed 260
─────────────────
Total        425 active
```

Plus:
- A.5.15: OFI (was NC; flipped via management_approval leaf 3/3 after Direction C)
- Engine vs live: 6 disagreements (5 ISMS 7.x being newly evaluated; 1 A.5.18 demotion proposal sitting in Stage-2)
- 17 controls correctly N/A (physical-scope honesty)
- 425 controls now have proper node_id (engine-evaluable)

## Open follow-ups documented

1. **Workbook importer hardening** — sheet-context normalization + "Not per ISMS Scope" → N/A
2. **A.5.18 engine demotion proposal** — tenant decision via Stage-2
3. **93 unbound workbook findings** — extend workbook_mappings YAML coverage
4. **Curation-driven `applies_when` on MUSTs** — long-term replacement for per-tenant overrides
5. **Dashboard latest-trace fix** — show newest trace per upload_id, not worst-case
6. **Headline-recompute response confusion** — relabel as recommendation, not actual flip

## Pattern observation: investigation-driven architecture

Today's arc shows a recurring pattern: a tenant action (upload,
re-upload, approval) surfaces an architectural gap that the data
exposes. Each gap triggers a focused investigation, which yields
either a fix or a clarification of the contract:

```
upload → fails to do what tenant expects → investigation → real bug OR scope clarification
```

This is healthy when the gap is real. The risk is whack-a-mole on
imagined gaps. Today's discipline was:
- Verify the gap with data before designing a fix
- Push back when "production-grade defaults" are pretexts (per [[strategic-pause-2026-06-15]])
- Ship the architecturally-honest fix, document the deferred follow-up

## Related arcs

- [[strategic-pause-2026-06-15]] — prior arc-level capstone (5 strategy docs)
- [[per-must-recall-direction-c-2026-06-23]] — the architectural fix that anchored today
- [[curation-phase-b-retrospective]] — earlier arc-level retrospective pattern
