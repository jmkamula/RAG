---
name: doc-reextraction-workstream-2026-06-23
description: "SHIPPED 2026-06-23 (commits pending): re-ran 29 deduped doc uploads through Direction-C-era extractor. Net: extracted bound findings 22 → 313 (+291). Writer-side supersede (0e510cf) verified end-to-end via 22 active rows flipped to rejected on Access Control Policy. 3 docs produced 0 findings (Access_Control_Policy.docx [old], TOC, Training and Awareness) — extractor follow-up. 26 active unbound remain (control-ref hits without per-MUST binding) — separate Direction-C extractor follow-up."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What and why

Last open follow-up from the multipath cleanup arc. The pre-Direction-C
doc extracts (mostly 2026-05-16 → 2026-06-09) produced unbound
findings; today's earlier cleanup soft-deleted those, leaving the
docs at 0-22 bound active each. Direction C (commits 2026-06-07/08)
ships per-MUST binding + grounding, but the docs hadn't been
re-extracted with it. This workstream did that re-extraction.

## Execution

1. **Pre-checks**: eval 198/199 (above 197 restart threshold);
   identified 29 deduped non-test non-workbook upload_ids
2. **API restart**: loaded writer-side supersede code from `0e510cf`
3. **Pilot**: re-extracted ISO 27001 Awareness Program.docx →
   5 new bound findings in ~15s
4. **Batch**: queued remaining 28 via `POST
   /api/v1/admin/uploads/{id}/reextract`, polled for completion
5. **Verify**: tallied bound/unbound state per source

## Results

Tenant-wide `inference_source` rollup AFTER workstream:

```
inference_source | bound_active | unbound_active | writer_superseded
extracted        |          313 |             26 |                22
workbook         |          204 |              0 |                 0
leaf_scan        |           51 |              0 |                 0
xfw_bridge       |            0 |            101 |                 0   (by-design)
```

Lift on `extracted`: 22 → 313 (**+291 bound active findings**).

**Writer-supersede verified end-to-end**: 22 rows on Access
Control Policy.docx were active going into the re-extract (the only
doc with prior-active extracted findings); the writer's UPDATE
flipped them to `is_active=FALSE`, `review_status='rejected'`,
`rejection_reason='superseded_by_extract_batch:<timestamp>'` BEFORE
the new INSERT loop. No other doc had pre-active findings to
supersede (today's earlier cleanup had already retired them).

## Three zero-finding docs — extractor follow-up

| Doc | Findings written | Probable cause |
|---|---|---|
| Access_Control_Policy.docx (underscored) | 0 | Pre-Direction-C policy mirror; likely topic-enrichment skip or doc_mappings miss |
| TOC Information Security Documents.docx | 0 | Table of contents; minimal extractable content |
| Training and Awareness Policy.docx | 0 | Topic-enricher miss? Worth re-checking with content inspection |

Not blocking — they're just at 0 bound, same as before re-extract. Logged as future bug-class follow-up: "docs that pass extraction-status='completed' with findings_written=0 — surface in admin-quality dashboard".

## 26 active unbound — Direction-C residual

Sample unbound findings produced by the re-extract:

| Doc | control_ref | standard_id | Issue |
|---|---|---|---|
| Vendor Security Assessment Report.docx | Art.28 | ISO27001:2022 | Cross-framework ref labelled with wrong standard |
| Vendor Security Assessment Report.docx | A.5.19 | ISO27001:2022 | Control-level match, no MUST binding |
| HR Security Policy.docx | A.6.3 | ISO27001:2022 | Control-level match, no MUST binding |

Direction C is supposed to drop control-level-only matches in favor
of per-MUST hits, but a path still emits them. Engine ignores
unbound rows post Phase-1 retirement so no posture impact, but
they clutter the Stage-1 surface.

**Follow-up to consider**: tighten extractor post-process to either
(a) drop unbound findings entirely when the doc has any bound
findings, or (b) downgrade them to xfw_bridge-style proposals.

## Eval

Pre-workstream: 198/199 (only #21 stochastic).
Post-workstream: eval re-run pending at commit time; expected stable
since the workstream only adds pending findings (not active engine
verdicts).

## Related

- [[multipath-data-cleanup-2026-06-23]] — today's earlier cleanup;
  this workstream closes its last open follow-up
- [[doc-curation-engine-v1]] — Direction C extractor that this
  workstream finally exercised on the existing doc corpus
- writer-side supersede in `0e510cf` — the prerequisite that
  made re-extracts safe (no duplicate-batch accumulation)
- [[intake-quality-telemetry]] — admin-quality dashboard where the
  3 zero-finding docs would have surfaced sooner
