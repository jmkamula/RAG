---
name: posture-writer-drop-fuzzy-match-2026-06-12
description: "SHIPPED 2026-06-12 (014e557): removed the fuzzy title-keyword overlap step from posture_writer.py's upload→client_documents linking. The '≥ 2 overlapping significant words' rule conflated genuinely different docs sharing generic tokens (e.g. ISMS+Process), silently overwrote evidence_type, and surfaced as posture regression on control 6.3. Linking now deterministic only: DOC-prefix / exact filename / orphan fallback."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The fuzzy-match step at `posture_writer.py:171-196` was the
third of four rules used to link an upload to a registered
client_documents row. It worked by computing word-overlap
between the upload filename and existing document_title fields,
matching when ≥ 2 significant words (len > 3) overlapped.

## The failure mode

Surfaced 2026-06-12 by a real conflation:

  Existing (2026-06-10): "ISMS Change Management Process.docx"
                         keywords: {isms, change, management, process}
                         evidence_type: 'procedure'

  New upload (2026-06-12): "ISMS Policy and Process Documents Acknowledgment.xlsx"
                           keywords: {isms, policy, process, documents, acknowledgment}
                           tag: 'policy'

Shared: {isms, process} = 2 → threshold met → linked to same
client_documents row. The new upload's enricher tag ('policy')
overwrote the existing row's evidence_type ('procedure'). The
engine's Phase-1 fallback at `leaf_evaluators.py:192-214`
matches by `cd.evidence_type` against the leaf's evidence_type;
control 6.3 has leaves of types {procedure, register,
review_record, scope_note} — none of which is 'policy' — so
0/4 satisfied → engine proposed NC. Live was OFI → Stage-2
proposal "OFI → NC" surfaced and looked like a posture
regression. The original evidence hadn't disappeared; just got
mislabelled.

## The fix

Step 3 deleted. Linking is now deterministic only:

  1. DOC-prefix in filename → match by external_ref (explicit)
  2. Exact filename match against registered rows (with
     external_ref or platform_ref)
  4. Orphan filename fallback for re-uploads of the same file

If none match, the upload gets its own fresh client_documents
row. Tenants who want consolidation across filename changes use
the registry's `external_ref` / `platform_ref` or rename the
upload to match the registered title exactly. No more silent
conflation by word-bag overlap.

Plus immediate data restore: client_documents row 6e33e455-...
evidence_type set back to 'procedure'. Engine re-evaluated 6.3
→ 1/4 children satisfied → OFI proposal supersedes the bogus
NC proposal. Live OFI matches engine OFI; no Stage-2 flip
pending.

## What this doesn't solve

The underlying architectural quirk: the engine's Phase-1
fallback (leaf_evaluators.py:192-214) consults
`cd.evidence_type`. As long as that path runs, a stomped
evidence_type can shift posture without anyone touching the
findings. This fix removes the most common way evidence_type
gets stomped; it doesn't remove the dependency.

Long-term direction (option #3 from the
[[feedback-intake-label-unreliability]] discussion): retire
Phase-1 fallback. Every extraction path now populates
`checklist_item_id`; the engine's Phase-2 path consumes
`checklist_item_id` directly with no document_type filter.
Legacy approved findings without `checklist_item_id` (like the
2-day-old 6.3 finding) would need backfill or be allowed to
decay until tenants re-upload through the modern pipeline.

## Operational note

The 7 workbook-discovery findings written by Stage 4.6 today
on the Acknowledgment.xlsx are bound to `checklist_item_id`
and reach the engine via Phase-2 — they don't care what
client_documents.evidence_type says. The 1 LLM-extracted
finding on A.5.1 (no checklist_item_id) does care, and is
mildly mis-shaped now that the row says 'procedure' instead
of 'policy'. The cost is a small Phase-1 lookup mismatch on
that single finding — accepted as edge case, not worth
splitting the client_documents row.

## Related

- [[feedback-intake-label-unreliability]] — the strategic
  framing where this fix was scoped as option #1.
- [[doc-pipeline-stage-4-6-2026-06-12]] — Stage 4.6 ran at the
  same time today and exposed the latent conflation by
  triggering an engine sweep that re-evaluated 6.3.
- [[leaf-evaluators-phase2-evidence-type-drop]] — earlier fix
  in the same direction (dropped evidence_type filter from
  Phase-2). Phase-1 fallback still uses it.
