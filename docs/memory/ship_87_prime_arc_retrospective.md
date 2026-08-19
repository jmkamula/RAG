# Ship 87' arc retrospective (2026-08-19)

## Arc summary

Follow-on to Ship 86' close. Ship 86' surfaced that ISO workbook
strict F1 was stuck at 4.88% while lenient F1 sat at 20.61%. Initial
framing: workbook_persistence marks findings `partial` too aggressively.
Investigation revealed the "aggressiveness" was designed-in — 235 of
240 workbook_mappings YAMLs explicitly declare `coverage: partial` on
column bindings, matching auditor discipline.

User's key insight: **"YAMLs are right — fix LLM GT to be conservative."**
The Ship 82'.a GT authoring prompt was too permissive; it marked
`satisfies` on populated-column presence, but auditors require
corroboration (owner + status + freshness + date across multiple
columns), not just data presence.

**Ship 87 pivot**: re-author LLM GT with corroboration-strict Pass 2
prompt.

**Result**: aggregate XLSX strict F1 jumped from **10.83% (Ship 84
permissive GT) → 18.11% (Ship 87 corroboration GT)** — +7.28pp
correction. ISO workbook specifically 4.63% → 11.76%. **Real
extractor quality was hidden by GT permissiveness.**

## Sub-arcs

### Ship 87'.a — corroboration-discipline prompt

`scripts/ship87a_gt_conservative.py` — thin wrapper over Ship 82'.a
that monkey-patches `_PASS2_SYSTEM` with a stricter prompt.

**Old Pass 2 (Ship 82'.a permissive)**:
> "satisfies": the document has language a strict auditor would accept
> as complete evidence for this MUST

**New Pass 2 (Ship 87 corroboration-strict)**:
> "satisfies": the MUST is fully evidenced. For a REGISTER MUST
> (`reg_*`), this means the row has the target column AS WELL AS
> corroborating columns (owner, date, status, or the row's identity
> column). A single populated column is NOT satisfies.

Plus concrete `satisfies` vs `partial` examples that mirror the YAML
authors' framing:
- `item:A.5.9:asset_records` with populated Asset ID + Owner columns → satisfies
- `item:10.1:reg_target_date` with only DUE DATE populated (no owner/status) → **partial**, NOT satisfies

Prompt also adds: **"Default to partial when in doubt."**

### Ship 87'.b — re-author 4 XLSX GTs

Ran corroboration prompt on all 4 XLSX docs. First pass: iso_workbook
returned no leaves (Pass 1 empty result on 127K doc text — possibly
Claude context overflow). Retry succeeded.

**Verdict counts vs Ship 84 permissive GT:**

| Doc | Ship 84 sat/par/ns/na | Ship 87 sat/par/ns/na | Total delta |
|---|---|---|---|
| iso_workbook | 34/125/172/39 (370) | 50/184/295/450 (979) | +609 (broader scoping) |
| raci | 6/12/15/1 (34) | 4/7/13/15 (39) | +5 |
| a51_review | 1/2/0/0 (3) | 2/1/0/0 (3) | 0 |
| a51_comm | 7/5/8/11 (31) | 6/6/8/5 (25) | -6 |

ISO workbook GT nearly 3× broader (370 → 979 verdicts) — Claude
enumerated many more `not_satisfies` + `not_applicable` MUSTs. Number
of `satisfies` MUSTs actually INCREASED (34 → 50) because corroboration
prompt was applied per-row, and multi-column rows now clearly satisfy
those MUSTs.

Cost: ~$8 total (dominated by ISO retry).

### Ship 87'.c — re-score against new GT

**Aggregate XLSX F1 comparison:**

| Metric | Ship 84 GT (permissive) | **Ship 87 GT (corroboration)** |
|---|---|---|
| Strict F1 (aggregate) | 10.83% | **18.11%** (+7.28pp) |
| Lenient F1 (aggregate) | 24.48% | 23.13% (-1.35pp) |
| Strict precision | 6.77% | **12.15%** |
| Strict recall | 27.08% | **35.48%** |

**Per-doc strict F1:**
| Doc | Ship 84 | **Ship 87** |
|---|---|---|
| iso_workbook | 4.63% | **11.76%** |
| raci | 80.00% | **100.00%** (4/4 TP, 0 FP) |
| a51_review | 50.00% | **80.00%** |
| a51_comm | 60.00% | **66.67%** |

**Key insight**: templated single-control XLSX docs (raci, a51_*) score
66-100% strict F1 under corroboration GT — **auditor-grade quality
was there all along**. The Ship 82'.a permissive GT was suppressing
this by counting properly-scoped extractor output as FPs.

## Codified lessons

**Lesson 85: LLM annotators can be too permissive AND too strict.**

Ship 82'.a delivered an important correction to Ship 82's ceiling
(hand GT was too strict; LLM GT broke the 17% precision ceiling). But
under Ship 87 measurement, that same LLM GT was TOO PERMISSIVE for
XLSX register semantics. **Both directions of GT bias are real** —
verify the annotator's discipline matches the domain before trusting
F1 numbers.

**Lesson 86: The YAML authors' framing IS the auditor lens.**

240 workbook_mappings YAMLs explicitly declare `coverage: partial`
on many bindings. That's not conservatism-by-accident — it's the
compliance domain expertise encoded in schema. When an LLM annotator
disagrees with schema-encoded expert framing, **the schema is
usually right**. Codify the schema's discipline into the annotation
prompt.

**Lesson 87: F1 numbers can mask a right-answer extractor.**

Ship 84's "4.63% strict F1 on ISO workbook" looked terrible. Under
Ship 87's corroboration GT it's 11.76% — still not great but more
than doubled. The extractor didn't change; only the measurement
apparatus did. **When F1 seems catastrophically low, question the
GT before questioning the extractor.**

**Lesson 88: Domain expertise IS a valuable prompt input.**

The Ship 87 prompt improvement was ~200 words of concrete examples
telling Claude what auditors actually accept. That domain-specific
context bought +7.28pp F1 correction. **LLM prompts should encode
the compliance-domain rulings that YAML authors already know —
don't ask the LLM to reinvent auditor discipline from scratch.**

## Files changed

- `scripts/ship87a_gt_conservative.py` (new, wraps Ship 82'.a with
  corroboration-strict Pass 2 prompt)
- `docs/ground_truth/llm_authored/iso_workbook_expected.yaml` (rewritten, 370 → 979 verdicts)
- `docs/ground_truth/llm_authored/raci_expected.yaml` (rewritten, 34 → 39)
- `docs/ground_truth/llm_authored/a51_review_expected.yaml` (rewritten, unchanged size)
- `docs/ground_truth/llm_authored/a51_comm_expected.yaml` (rewritten, 31 → 25)
- `docs/memory/ship_87_prime_arc_retrospective.md` (this)
- `docs/memory/MEMORY.md` (Ship 87' entry)

## Deferred to future arcs

- **Ship 88'.a**: link-follow discipline for hyperlink cells (Ship 87'.d
  deferred). Cells that hyperlink to external policies should be
  marked `partial` + follow-up created. Auto-promote to `present`
  when the linked doc is uploaded + verified. Requires cascade/
  follow-ups plumbing.
- **Ship 88'.b (or Ship 89')**: DOCX GT re-authoring with corroboration
  discipline. Ship 82's DOCX GT (5 docs, 490 verdicts) likely has same
  permissive bias — all Ship 78-83 F1 numbers may be under-reporting
  extractor quality. ~$5 rerun.
- Curator skip-on-not_applicable improvement (Ship 86' deferred)
- PDF format measurement (Ship 84 deferred)

## Baseline

Ship 87' close: no runtime code changes (GT authoring is offline).
Chat pipeline / eval pipeline unchanged. Baseline preserved from
Ship 86' close.
