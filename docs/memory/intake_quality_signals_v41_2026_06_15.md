---
name: intake-quality-signals-v41-2026-06-15
description: "SHIPPED 2026-06-15 (7d5c30d + 45f20fa, schema_v41): the admin uploads-quality dashboard couldn't see its own catches — both 2026-06-12 questionnaire + 2026-06-15 TOC incidents showed green. Persisted dropped_questionnaire + skipped_as_toc, added inert-findings signal (active>0 AND bound=0), and suppressed yield-ratio false-positives on legacy doc_mappings fallback. Net: Arion went from 2 yellow to 13 honest yellow."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The intake-quality dashboard had three blind spots after the past
week's filter work. The 2026-06-12 questionnaire and 2026-06-15 TOC
incidents — the ones that prompted new filters — both showed
`quality_flag=green` because `findings_kept` was non-zero. The
dashboard couldn't see its own catches.

## Four gaps closed

### Gap 1 — `dropped_questionnaire` not persisted

The 2026-06-12 filter incremented `doc.extraction_metrics["dropped_
questionnaire"]` but the `IntakeTracer.write()` allowed-list
(`doc_pipeline.py:107`) didn't include it. Silently dropped at trace
write time.

### Gap 2 — `skipped_as_toc` not persisted

Same shape, added 2026-06-15. The TOC filter set
`doc.extraction_metrics["skipped_as_toc"] = reason_str`. The doc
returns `[]` from extract, doc_pipeline writes the extract trace row
unconditionally (good — captures the skip), but the reason string
never reached the trace log because the allowed-list missed it.

### Gap 3 — inert findings invisible

The harder gap. A doc with N findings whose `checklist_item_id IS
NULL` for all N is producing **inert output** — post Phase-1
retirement (2026-06-13), unbound findings can't feed the engine.
The dashboard counted `findings_kept` without distinguishing
"found stuff" from "found stuff that matters". 

The 2026-06-12 Vendor questionnaire and 2026-06-15 TOC both hit this:
- Vendor: 22 findings_kept, 7 active, 0 bound (all Phase-1 fallback)
- TOC: 18 findings_kept, originally 47 active, 0 bound

### Gap 4 — yield-ratio false-positive on legacy fallback

When `doc_mappings_match_count = 0`, the legacy `_scope_controls`
fallback fired. The denominator is then a broad 50-control clause-
scope, NOT a meaningful "expected" set. Yield ratio < 20% against
that is noise.

Two long-standing YELLOWs (Lead Sales + 214427 Client Report) were
flagged for this reason but were legitimate low-yield extractions.

## What the schema looks like

`schema_v41_intake_quality_shape_signals.sql`:

```sql
ALTER TABLE intake_trace_log
    ADD COLUMN IF NOT EXISTS dropped_questionnaire INTEGER,
    ADD COLUMN IF NOT EXISTS skipped_as_toc        TEXT;
```

Plus an extended `idx_intake_trace_quality` covering the new
columns so needs-attention queries stay cheap.

## What the new flag logic looks like

`_extraction_quality_flag` in `api_server.py`:

| signal | tier | reason text |
|---|---|---|
| `skipped_as_toc IS NOT NULL` | **red** | `skipped as TOC (<reason>)` |
| `findings == 0 AND candidates > 0` | red | `0 findings from N scoped controls` |
| `dropped_questionnaire >= 2*kept` | **yellow** | `questionnaire drops dominate` |
| `dropped_hallucinated > kept` | yellow | `hallucinated > kept` |
| **`active>0 AND bound==0`** | **yellow** | `all N findings unbound` |
| `yield<20% AND mapping_matched > 0` | yellow | `yield ratio < 20%` |
| markdown >> paragraph, under-chunked | yellow | `under-chunked` |
| default | green | `ok` |

Two changes vs prior:
1. TOC skip is the new top-priority RED
2. yield ratio only fires when a doc_mapping actually matched
   (otherwise it's noise on the broad fallback)

## The sha256 bridge

`intake_trace_log.upload_id` references `document_uploads.id`. But
finding-counts live on `document_findings.document_id` which
references `client_documents.id`. No FK between those two tables.

Bridge: both tables persist `sha256` / `checksum_sha256` on the file
bytes — same SHA. The endpoint JOINs on (sha256, tenant_id):

```sql
LEFT JOIN client_documents cd
  ON cd.checksum_sha256 = du.sha256
 AND cd.tenant_id       = du.tenant_id
```

Then a LATERAL aggregate counts active vs bound findings per
`client_documents.id`. The bound-rate signal isn't just about the
trace — it reflects the live state of `document_findings`.

## Where this leaves Arion

Before: 2 yellow (yield-ratio noise on legacy fallback)
After:  13 yellow, all sharing the same root cause

```
all 25 findings unbound (no checklist_item_id)   Confidentiality and NDA Policy
all 12 findings unbound (no checklist_item_id)   HR Security Policy
all 12 findings unbound (no checklist_item_id)   Risk Management Policy
all  8 findings unbound (no checklist_item_id)   BCP and Disruption Response
all  8 findings unbound (no checklist_item_id)   214427 Client Report 27001
all  7 findings unbound (no checklist_item_id)   Vendor Security Assessment Report
all  6 findings unbound (no checklist_item_id)   Risk-Integrated Risk Assessment
all  5 findings unbound (no checklist_item_id)   Internal Audit Policy
all  3 findings unbound (no checklist_item_id)   Supplier Vendor Security Policy
all  2 findings unbound (no checklist_item_id)   Vulnerability Management
all  1 findings unbound (no checklist_item_id)   Internal Audit Report
all  1 findings unbound (no checklist_item_id)   ISO 27001 Awareness Program
all  1 findings unbound (no checklist_item_id)   ISMS Internal Audit Plan
```

All extracted pre-2026-06-13 — before per-MUST `checklist_item_id`
binding was wired across all doc paths. They worked at the time via
the Phase-1 fallback (coarse `(control_ref, evidence_type)` match);
that fallback was retired ([[feedback-phase-1-fallback-masks-gaps]]).

These docs aren't broken; their findings are time-frozen. Going
forward:
- New uploads → bound findings (the binding stack: doc_mappings YAML,
  per-MUST candidate list to LLM, leaf-scan back-bind)
- Old uploads → eligible for [[leaf-scan-catalog-campaign-2026-06-14]]
  re-binding (one-time sweep, not yet automated)

## Pair rule applied

[[feedback-telemetry-before-trouble]] says: build observability
alongside new pipeline stages, not as post-hoc fix-up. This
session was the post-hoc fix-up for two filters shipped without
trace-log columns. The fix-up was easy because the in-memory
metrics already existed — only the bridge to the trace log was
missing.

Going forward: any new filter or stage that adds an in-memory
metric to `doc.extraction_metrics` MUST also be added to the
tracer's allowed-list in the same commit. Same shape as
[[feedback-eval-with-each-feature]].

## Related

- [[intake-quality-telemetry]] — schema_v35 ancestor that this
  builds on
- [[extractor-questionnaire-filter-2026-06-12]] — filter whose
  signal this surfaces
- [[extractor-toc-filter-2026-06-15]] — filter whose signal this
  surfaces
- [[feedback-phase-1-fallback-masks-gaps]] — the architectural
  finding that makes the inert-findings signal load-bearing
- [[feedback-telemetry-before-trouble]] — the pair rule
- [[leaf-scan-catalog-campaign-2026-06-14]] — the back-bind
  campaign that addresses the existing "all findings unbound"
  YELLOWs
