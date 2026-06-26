---
name: llm-narrative-under-discovery-audit-2026-06-26
description: "AUDIT 2026-06-26: median yield = 17% on Arion's 80 (doc, control) extracted-source pairs (66% under 25%, 96% under 50%). Real, large, observable. SHIPPED schema_v48 + extractor finalizer + pipeline whitelist to surface pass-2 + per-doc yield ratio per intake — closes the silent-loss gap on the recall pass. 4 more gaps (G3-G6) catalogued for follow-ups."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## Headline numbers (Arion, 2026-06-26)

80 (document, control) pairs from `document_findings` with
`inference_source='extracted'`, joined to the catalog's
`must_contain` totals per control:

- Median yield = **17%** (1 in 6 MUSTs captured) where catalog ≥ 6 MUSTs
- **66% of pairs under 25% yield**
- **96% of pairs under 50% yield**

All extracts were post-Phase B (2026-06-24+) — NOT a stale-catalog
effect. Worst cases (e.g. HR Security Policy at 1/31 A.5.18 MUSTs =
3%, Access Management Process at 1/30 A.5.17 = 3%) are docs that
clearly evidence most of those MUSTs. The LLM is missing them.

## The key insight

**Under-discovery is invisible by construction.** Today's drop
counters (`dropped_short_quote`, `dropped_hallucinated`,
`dropped_low_conf`, `dropped_unknown_ref`, `dropped_questionnaire`)
all track MIS-BINDING — the LLM said something the validator
rejected. None of them track what the LLM never saw in the first
place. Under-discovery leaves no trace by definition; you have to
go looking for it.

The proxy signal is **yield ratio**: distinct MUSTs bound / catalog
MUSTs in scope for the doc's target leaves. That's now persisted on
every extract.

## Six gaps catalogued

| # | Gap | Status |
|---|---|---|
| G1 | Pass-2 metrics computed but dropped at trace write | SHIPPED 2026-06-26 (schema_v48) |
| G2 | Per-doc yield ratio (distinct/total) not measured | SHIPPED 2026-06-26 (schema_v48) |
| G3 | Pass-2 requires doc_mappings match — 8% of uploads get no recall | OPEN |
| G4 | Single LLM call per chunk; large docs starve on attention | OPEN |
| G5 | Crosscheck 75% disagreement rate (mis-binding noise) | OPEN |
| G6 | Pass-2 fires on PARTIALLY-bound leaves only — zero-bound leaves get no recall | OPEN |

## What G1+G2 actually ship

schema_v48 adds 5 nullable columns to `intake_trace_log`:

- `distinct_musts_bound` — the numerator (count(DISTINCT
  checklist_item_id) in findings)
- `leaf_musts_in_scope` — the denominator (sum of `must_contain`
  across `target_leaves`)
- `yield_ratio_pct` — 0-100 integer, clamped (pass-2 can over-bind)
- `pass2_leaves_targeted` — partial-leaf count fed to recall pass
- `pass2_findings` — additional findings from pass-2

Extractor: `_finalize_yield_metrics(doc, findings)` called before
each return path of `extract()`. Excludes unbound (Phase-1 coarse)
findings from the numerator.

Pipeline: `tracer.write("extract", ...)` passes the new keys
explicitly + `_TraceWriter.allowed` whitelist updated (silent-drop
gap that hid pass-2 metrics for as long as `_run_pass2` has existed).

**Smoke result on real upload**: yield = 17% on a multi-control HR
policy. Pass-2 fired, found 0 additional findings. Matches the audit
median exactly. The metric is honest.

## Non-obvious decisions

### Yield denominator = target_leaves' MUSTs, not all leaves' MUSTs

A doc that maps to ONE leaf of a 5-leaf control should be measured
against that one leaf's MUSTs, not all 5 leaves' combined. When
doc_mappings doesn't match (8% of Arion's uploads, 45% have NULL =
pre-instrumentation), `leaf_musts_in_scope` is NULL and
`yield_ratio_pct` is NULL — honest "we don't have a denominator"
signal, not a fake number.

### Cap at 100%, not raw ratio

Pass-2 can bind MUSTs from leaves outside the doc_mappings target
set (unusual but possible — the prompt doesn't strictly forbid it).
That would produce yield > 100%. Cap at 100% so the metric stays
comparable across uploads.

### Exclude unbound findings from numerator

Pre-2026-06-13 (Phase-1 retirement) extracts produced findings with
NULL `checklist_item_id`. Those still satisfy a control coarsely
but don't bind a specific MUST — don't count them toward yield.
Otherwise the metric falsely inflates on legacy data.

## Carry-forward

**The drop-counter pattern** was already a known anti-pattern (see
[[feedback-telemetry-before-trouble]] — we instrument *what we
caught*, not *what we missed*). This audit is the strongest evidence
yet for that lesson: 5 drop counters running for months, none of
them surfaced a 17%-yield problem.

**Next investigation** (after G1+G2 collect real-world data): G3-G6
in order of cheapness. G6 (zero-bound recall) is probably the next
biggest win — pass-2 already exists and works, just needs its
trigger broadened. G4 (multi-pass on large docs) is the harder
structural fix.

## Related

- [[tabular-evidence-rows-2026-06-26]] — same arc (under-discovery
  fix), different class. That was templated-tabular multi-row;
  this is LLM-narrative.
- [[feedback-telemetry-before-trouble]] — the rule: track absence,
  not just rejection.
- [[templated-lane-discipline-2026-06-25]] — auto-approve trust:
  for templated/form lanes there's no under-discovery (tenant
  authored directly); this audit applies only to inference paths.
