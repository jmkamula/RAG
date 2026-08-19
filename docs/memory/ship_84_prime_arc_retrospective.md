# Ship 84' arc retrospective (2026-08-19)

## Arc summary

User direction: **"what is pending for MVP? I would do Measurement /
GT quality, include excel and pdf."** Follow-up: **"I don't have PDF
at hand, let's start with xls."**

Ship 84' extends Ship 82'.a's LLM-authored GT to XLSX format so we can
measure the workbook_persistence extraction pipeline (which sits
outside the extractor.py consensus/critic/per_must path).

**Partial delivery** — 2 of 4 planned XLSX docs authored before
Anthropic API credit exhausted mid-run.

## Sub-arcs

### Ship 84'.a — LLM GT authoring on XLSX docs

`scripts/ship84a_gt_xlsx.py` — thin wrapper over Ship 82'.a's
`author_gt_for_doc` with an XLSX-specific `DOCS` map. `read_document`
dispatches xlsx/xlsm files through `_read_xlsx` which produces
pipe-delimited markdown tables per sheet — usable Claude Opus context.

Selected 4 XLSX candidates on demo tenant:
- `iso_workbook` — 300KB ISO 27001 workbook, 93 findings from
  workbook_persistence (**largest / most valuable**)
- `raci` — 7KB templated RACI (~4 findings pre-cleanup)
- `a51_review` — 10KB templated single-control (~3 findings)
- `a51_comm` — 10KB templated single-control (~3 findings)

**Outcome — credit exhaustion mid-run:**
- ✓ `raci_expected.yaml` — 34 verdicts (from smoke test)
- ✓ `iso_workbook_expected.yaml` — 370 verdicts (completed just before
  credit ran out)
- ✗ `a51_review_expected.yaml` — not authored
- ✗ `a51_comm_expected.yaml` — not authored

The ISO workbook's 370-verdict GT is by far the highest-value asset
here (most MUSTs measured on any single doc across all Ship 77+ work).

### Ship 84'.b — scoring XLSX findings against LLM GT

`scripts/ship84b_score_xlsx.py` — reuses `ship77e_compare._score` +
`ship82b_score_llm_gt._load_llm_gt`. Exports current active
`document_findings` for the 2 scored docs.

**Results**:

| Doc | Findings | Strict F1 | Lenient F1 | Strict TP | Lenient TP |
|---|---|---|---|---|---|
| iso_workbook (300KB) | 220 | 4.63% | **21.70%** | 5 | 37 |
| raci (7KB) | 0 (soft-deleted) | 0.00% | 0.00% | 0 | 0 |
| **Aggregate** | 220 | 4.50% | 20.61% | 5 | 37 |

**Key observation — strict vs lenient gap on ISO workbook is 5×:**
- Strict precision: 2.75% (only 5 of 220 findings had `status='present'`
  matching a `satisfies`-GT MUST)
- Lenient precision: 20.33% (37 findings had `status='partial'` or
  `present` matching a `satisfies|partial`-GT MUST)

**Root cause**: workbook_persistence pipeline marks most findings
`status='partial'` even when the underlying evidence would be
`satisfies` under GT. This looks like an over-conservative
`present` vs `partial` threshold in workbook_mappings YAML defs.

**Lenient F1 21.7% is comparable to DOCX Union+vocab (F: 28.90%
lenient)** — the XLSX pipeline is producing meaningful signal despite
the strict-status gap.

**RACI's 0 findings**: findings existed (extraction_status='completed'
with 4 findings historically) but were soft-deleted at some point —
likely during Ship 82 residue cleanup that swept pending findings.
Would need re-extraction to score.

## Codified lessons

**Lesson 74: Measurement can be format-blind by accident.**

Ships 77-83 measured extraction quality on 5 DOCX docs but never
tested XLSX or PDF. Real production tenants upload all three formats;
each goes through a different pipeline (extractor.py for DOCX/PDF vs
workbook_persistence for XLSX). MVP-level confidence requires
measurement on every supported format.

**Lesson 75: Cross-model GT authoring exposes format-specific bugs
that same-model extraction masks.**

The ISO workbook produces 220 findings with 5 marked `present` and
215 marked `partial`. Same-tool self-scoring would say "everything
was extracted." Claude Opus GT says 34 MUSTs are `satisfies` — of
those 34, workbook_persistence extracted 5 as `present` (14% hit
rate on strict). The `present` vs `partial` threshold in
workbook_persistence needs empirical calibration against auditor-
grade GT.

**Lesson 76: External API credit is a real production dependency.**

Anthropic credit exhaustion mid-Ship-84'.a killed 2 of 4 planned
GT docs. Every LLM-driven arc should budget cost + verify balance
before batch runs. Retrospective cost tracking (post-hoc: ~$5-6 for
the completed 404 verdicts + ~$4-5 wasted on the failed batches
= ~$10 spent, 60% wasted on failures).

## Files changed

- `scripts/ship84a_gt_xlsx.py` (new)
- `scripts/ship84b_score_xlsx.py` (new)
- `docs/ground_truth/llm_authored/iso_workbook_expected.yaml` (new, 370 verdicts)
- `docs/ground_truth/llm_authored/raci_expected.yaml` (new, 34 verdicts)
- `docs/ground_truth/ship77d_measurement/run_xlsx_current.csv` (new, 220 rows)
- `docs/memory/ship_84_prime_arc_retrospective.md` (this)

## Deferred to Ship 85' + future

- **Ship 85' opened**: investigate workbook_persistence strict/lenient
  F1 gap. Determine whether `status='present'` threshold is calibrated
  too conservatively; compare to workbook_mappings YAML defs.
- Complete a51_review + a51_comm GT authoring (~$1 each) after credit
  top-up
- Re-extract RACI to score against its 34-verdict GT
- PDF format measurement — user has no PDF at hand; deferred until
  real tenant PDFs are available or public-source seed is agreed

## Baseline

Ship 84' close: no code changes in this arc (measurement + GT authoring
only). Chat pipeline unchanged. Eval baseline holds at 232 PASS + 1
WARN + 0 FAIL / 233 from Ship 83' close (earlier same day).
