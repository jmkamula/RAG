---
name: reextract-endpoint-2026-06-23
description: "SHIPPED 2026-06-23 (3fde996): POST /api/v1/admin/uploads/{id}/reextract re-runs the extraction pipeline on existing upload bytes without requiring re-upload. UI duplicate-card extended with clarifying text + 'Re-extract with latest engine' button calling the new endpoint. Operational path to leverage extractor improvements (filters, prompts, per-MUST binding, PDF Layer A) on existing docs."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Surfaced 2026-06-23: tenant tried to re-upload Access Control Policy
to test a workflow; the file was byte-identical to an earlier upload,
sha256 dedup correctly returned 409. The 409 was correct behavior but
the UX was opaque ("Identical file already uploaded") with no
actionable path forward.

Real concern: as extractor code improves (filters, prompts, per-MUST
binding), existing uploads don't automatically benefit. Pre-fix the
only workaround was modifying the file to change the hash and
re-uploading — disruptive.

## What landed

### Endpoint (api_server.py)

```
POST /api/v1/admin/uploads/{upload_id}/reextract
```

- Tenant-scoped (RLS); requires API key with default scope
- Looks up the upload's storage_path, verifies file exists
- Refuses on `extraction_status='duplicate'` uploads (re-extract the canonical)
- Queues `_run_pipeline` on the existing bytes in a background task
- Reuses the same upload_id (pipeline writes new findings rows;
  prior approved findings stay active — tenant decides whether to
  reject the old ones via Stage-1 after seeing the new shape)

### Deliberate MVP limitations

- Does NOT auto-supersede prior findings. Two sets coexist until
  tenant triages. Add `supersede=true` flag here when operationally
  needed.
- Does NOT bypass content-shape filters (questionnaire / TOC) —
  same filters apply on re-extract.

### UI enhancement (static/arioncomply.html)

Duplicate notice card now shows:
- Original message: "Identical file already uploaded as X on date"
- NEW: clarifying paragraph ("Even a small content change produces
  a different file. If the extractor has improved since this file
  was first processed and you want to re-run it with the latest
  logic, use the action below.")
- NEW: "Re-extract with latest engine" button → calls the endpoint
- Button shows loading state + result message inline

## Operational use cases

1. **Code improvements**: when a new extractor feature ships (PDF Layer
   A, prompt tightening, Direction C pass-2), trigger re-extract on
   high-value uploads to gain the lift without re-uploading bytes.
2. **Failed extractions**: a doc that returned 0 findings due to a
   bug can be re-extracted after the fix without losing the upload
   record / audit trail.
3. **Catalog refinement**: when must_fingerprints YAMLs are refined,
   re-extract surfaces the better crosscheck signal.
4. **Pre-MVP tenant migration**: when onboarding a new framework
   (27701, SOC 2), legacy uploads can be re-evaluated against the
   new scope.

## Today's first use

Triggered re-extract on Access Control Policy.docx during the
Direction C work. Re-extract was the operational lever that:
- Validated PDF Layer A wasn't a regression (same 14 findings on docx)
- Surfaced the prompt+cap need (LLM emitting more output, hitting
  max_tokens=2000 truncation)
- Exercised Direction C end-to-end with measurable lift (14 → 22 findings)

## Related

- [[pdf-layer-a-2026-06-19]] — the kind of improvement re-extract
  is designed to roll out
- [[per-must-recall-direction-c-2026-06-23]] — same-day shipment
  that needed re-extract for empirical validation
- [[per-must-binding-in-extractor-2026-06-15]] — the B path that
  re-extract makes retroactively applicable
