---
name: extractor-catalog-crosscheck-2026-06-15
description: "SHIPPED 2026-06-15 (732d0a5 + 2251a03, schema_v42): extractor↔catalog crosscheck — when the LLM emits a checklist_item_id, validate the evidence quote against the must_fingerprints catalog's keyword sets for that MUST. Soft signal (no drop), surfaced via crosscheck_confirmed / crosscheck_disagreements / crosscheck_unavailable counters and a new yellow dashboard flag. Catalogs are now dual-purpose: back-bind matcher + extractor 2nd opinion."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The B fix earlier today wired per-MUST binding into the LLM extractor.
Once the LLM emits a `checklist_item_id` we validate it against the
**valid set** (hallucinated ids → drop). But validity-of-id doesn't
catch SEMANTIC misalignment: the LLM can pick a legitimate MUST id
whose intent doesn't match the evidence it cited.

Crosscheck is the second check: does the cited evidence actually
match what the MUST is about?

## Mechanism

```
for each LLM-emitted (must_id, evidence):
    if must_id not in valid_set_for_control: drop (B-handled)
    keyword_sets = load_must_fingerprints().get(must_id)
    if not keyword_sets:
        crosscheck_unavailable += 1
    elif _excerpt_matches(evidence, keyword_sets):
        crosscheck_confirmed += 1
    else:
        crosscheck_disagreements += 1
        # SOFT signal — binding kept, not dropped
```

Three counters flow through `doc.extraction_metrics` →
`IntakeTracer.write` → `intake_trace_log` (schema_v42) → quality
dashboard.

## Why soft (no drop)

The autogen catalog cohort (64 of 310, shipped earlier today as part
of [[per-must-binding-in-extractor-2026-06-15]]) is precision-poor.
A hard drop would silently lose real bindings on which the LLM was
correct but the catalog's keyword pattern is too narrow.

Soft mode means:
- Tenant still sees the binding in Stage-1
- Telemetry surfaces docs with high disagreement rates
- Dashboard flag (`crosscheck_disagreement` yellow) fires when
  `disagreements >= confirmed`
- Catalog refinement pass can target the highest-disagreement MUSTs
  empirically rather than guessing

If catalog quality improves over time, the crosscheck signal becomes
more reliable — and at that point a hard-drop mode is a one-line
config flag away.

## Honest limitation

The 5 spurious leaf-scan bindings from this morning (Art.26 ×3,
Art.32:reg_risk_assessment, Art.37:reg_publication_evidence) would
NOT be caught by the crosscheck because their catalogs are
autogen-loose. The same `[activity]` / `[register]` keyword that
mis-fires in leaf-scan would mis-confirm in crosscheck.

What crosscheck buys today:
1. **Telemetry** — per-doc counts let us measure catalog quality
   empirically across uploads. Each disagreement is a triage hint.
2. **Future leverage** — every tightened catalog improves both
   leaf-scan precision AND crosscheck precision simultaneously.
   One-time catalog refinement work compounds.
3. **Dual-purpose catalog asset** — the same `must_fingerprints/*.yaml`
   set now feeds leaf-scan AND extractor. Investment in catalog
   refinement pays in both paths.

## What it adds to multi-framework strategy

At multi-framework scale, catalog refinement becomes the highest-
leverage investment per the [[intake-pipeline-architecture]]
shared-vs-framework-specific split. Crosscheck makes that investment
visible: a tenant in framework N can see crosscheck disagreement rate
as a quality signal on framework N's catalogs.

Specifically as the ISO 27701 / SOC 2 onboarding progresses:
- New framework data lands with autogen catalogs (skeleton)
- Crosscheck disagreement rate measures their precision empirically
- Refinement passes target the high-disagreement MUSTs first

This makes catalog quality testable, not speculative.

## What's still not solved

- **Catalog quality** itself — crosscheck reports the gap, doesn't close it
- **Cross-doc target-side fanout** — when one MUST attracts many
  spurious bindings across docs (today's Art.26 pattern), crosscheck
  doesn't notice because each pair looks fine in isolation. Worth
  a separate `--cap-target-fanout` filter on the leaf-scan runner
  and a similar aggregate check on extractor output.
- **Legacy fallback uploads** — when no doc_mapping matches, the
  LLM doesn't get the per-MUST candidate list, doesn't emit
  `checklist_item_id`, crosscheck doesn't run. Findings stay unbound.

## Pair-rule applied (already documented in arch diagram)

The new metric was wired through ALL three layers in the same commit:
1. `IntakeTracer.write` allowed-list (`doc_pipeline.py`)
2. `intake_trace_log` schema (schema_v42)
3. Dashboard flag logic (`_extraction_quality_flag`) + endpoint payload

Per the telemetry-coordination rule established this morning by
[[intake-quality-signals-v41-2026-06-15]]. The questionnaire and TOC
filters were 3 days late on this; the crosscheck shipped right.

## Related

- [[per-must-binding-in-extractor-2026-06-15]] — the B fix this
  builds on
- [[intake-quality-signals-v41-2026-06-15]] — the dashboard work
  this extends
- [[leaf-scan-catalog-campaign-2026-06-14]] — the catalog set this
  reuses dual-purpose
- [[intake-pipeline-architecture]] — diagram, now updated with this row
