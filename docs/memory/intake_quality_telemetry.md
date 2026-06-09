---
name: intake-quality-telemetry
description: "SHIPPED 2026-06-09 (b74ece7, schema_v35): 7 new columns on intake_trace_log capturing per-upload drop buckets + coverage signals; GET /api/v1/admin/uploads/quality returns red/yellow/green flagged list."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The Risk-Integrated procedure's 1-finding-from-107K-tokens problem
went unnoticed until manually inspected. The fix landed [[table-
heavy-docx-rescue]], but the broader question — "how do we catch
the next silent under-extraction?" — needed a telemetry layer.

## What's captured

schema_v35 adds these columns to `intake_trace_log` (filled on the
`extract` stage row):

| Column                | Source                  | What it tells you |
|-----------------------|-------------------------|-------------------|
| `dropped_low_conf`    | parse-side filter       | LLM confidence too low |
| `dropped_short_quote` | parse-side filter       | Evidence quote < 40 chars |
| `dropped_hallucinated`| parse-side filter       | Quote not in doc text |
| `dropped_unknown_ref` | parse-side filter (NEW) | LLM ref outside candidate list |
| `markdown_chars`      | `doc.markdown` length   | Total content available |
| `paragraph_chars`     | `doc.full_text` length  | Content via paragraph walk |
| `candidate_controls`  | post-doc_mappings scope | What we asked LLM about |

Combined with the existing `llm_calls` and `findings_kept`, this is
enough to compute a yield ratio and detect under-chunking.

## How it flows

1. `extract(doc, controls, api_key)` populates
   `doc.extraction_metrics` as it runs (counter increments on every
   parse pass).
2. `doc_pipeline.run` reads `doc.extraction_metrics` and passes the
   relevant fields into `tracer.write("extract", ...)`.
3. Trace row lands in `intake_trace_log` with stage='extract'.

The metrics dict is keyed by the trace_log column names so the
tracer's `allowed` set accepts them directly. Adding a new metric:
extend `allowed` in `doc_pipeline.py:_Tracer.write`, add column to
schema, increment in the extractor.

## Quality flag rules

`_extraction_quality_flag` in `api_server.py`:

  - 🔴 RED:    `candidates > 0 AND findings = 0` — zero-yield scoped extraction
  - 🟡 YELLOW: any of —
      - `hallucinated > kept` — LLM citing made-up text
      - `kept * 5 < candidates` — yield < 20%
      - `md > para*3 AND md > 2000 AND llm_calls < md/50000` — markdown
        under-chunked (rescue should have fired or chunks too few)
  - 🟢 GREEN: otherwise

These are conservative starting points. Adjust thresholds when real
patterns emerge — e.g. if certain doc-shapes legitimately yield
<20% (highly specialised procedures), tighten the yellow gate.

## Endpoint

`GET /api/v1/admin/uploads/quality?limit=N&flag=red|yellow`

Lists recent uploads, red-first then yellow then green, newest
within each flag. Per-upload payload includes the raw drop counts
+ the derived flag + a one-line reason string.

## Historical rows (pre-v35)

Show NULL for all new columns; the quality function treats NULL as
0, so they flag as green. Expected — they're frozen audit-log
artefacts, not actionable diagnostics.

## How to apply

- When debugging an upload that looks "off", query the trace row
  and check the drop buckets BEFORE diving into per-chunk logs.
  High `dropped_hallucinated` = wrong scope; high `dropped_short_quote`
  = LLM paraphrasing instead of citing; high `dropped_unknown_ref`
  = LLM not echoing input refs (older code paths or model drift).
- When evaluating a tenant's onboarding doc corpus, run the admin
  endpoint with `flag=red` and `flag=yellow` to triage which docs
  need pipeline tuning vs which can stay as-is.
- Future work flagged in [[/Users/.../convo-history]] — surface these
  in a tenant dashboard tile, not just admin.

## Related

- [[table-heavy-docx-rescue]] — the trigger case for needing
  telemetry.
- [[doc-curation-engine-v1]] — the doc_mappings layer that
  populates `candidate_controls`.
