---
name: ship-93-prime-z-housekeeping
description: Ship 93'.z — housekeeping bundle before Ship 94'.a arbiter cutover; retention sweep + arbiter partial explainability + closure trail.
metadata:
  type: project
---

# Ship 93'.z — housekeeping bundle (2026-08-24)

See commit `1513db00` for the full change. Summary in MEMORY.md.

## 93'.z.i — retention sweep for cite_attestation_prompt

- `schema_v108`: sweep_log allowlist gains `cite_attestation_retention`; adds app_permissive USING policy on `cite_attestation_prompt` (mirror of Ship 3'.f cascade policies)
- `rag/scheduler/tick.py::sweep_cite_attestation_retention` — walks pending prompts past `expires_at` → `status='auto_expired'` with `resolved_at=NOW()`. Preserves row for audit; no delete
- Closes the loose end promised in Ship 92'.b retro

## 93'.z.ii — LLM arbiter partial explainability

- New `partial_explainer.explain_arbiter_partial(must_id, evidence_text, sheet_name, source_column)` — third branch `arbiter_incomplete`
- Arbiter partials carry LLM's verbatim evidence quote (post-Ship 6'.b verifier gate). Prose frames as "LLM found corroborating text but judged insufficient; upload doc or amend workbook"
- `stage1_review_chat.list_pending_for_control` routes by `inference_source`: `workbook` → `explain_partial`, `workbook_llm_arbiter` → `explain_arbiter_partial`
- UI adds purple "LLM-judged incomplete" branch badge
- **Test**: 12/12 arbiter partials on 9.2 get completeness prose with LLM's evidence quote inline

## 93'.z.iii — closure trail (resolved_by_upload_id)

- `schema_v109`: `document_findings.resolved_by_upload_id UUID` (FK document_uploads, ON DELETE SET NULL) + `resolved_at TIMESTAMPTZ` + `resolution_reason TEXT`
- New `rag/posture/finding_closure.py::stamp_closures_from_upload` — best-effort post-write hook. For every new `status='present'` finding produced by an upload, stamps all prior active `status='partial'` findings on the same tenant + MUST from OTHER documents with the linkage
- Doesn't auto-approve or supersede — Ship 93'.b design keeps both provenance chains active; the stamp adds the linkage only
- `doc_pipeline` **Stage 4.9** runs the sweep after Stage 4 commits
- `list_pending_for_control` returns `resolved_*` fields; Stage-1 detail renders green "Resolved by upload" badge with reason + date
- **Test**: synthetic upload with present finding on `item:10.1:reg_target_date` → 2 prior partials on same MUST correctly stamped with reason narrative + `resolved_at`

## Related

- [[ship-92-prime-b-cite-attestation]] — retention sweep closes 92'.b's promised follow-up
- [[ship-91-prime-arc-retrospective]] — arbiter partial explainability closes 91's deferred item
- [[ship-93-prime-a-partial-explainability]] — closure trail attaches to the same UI surface
- [[ship-94-prime-a-arbiter-cutover]] — housekeeping complete; cutover follows
