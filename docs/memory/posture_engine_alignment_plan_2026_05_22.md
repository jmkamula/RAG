---
name: posture-engine-alignment-plan-2026-05-22
description: "Phased plan agreed 2026-05-22 to fix Stage-1 contract violation, complete Neo4j curation, add polite gap messaging. Phase D SHIPPED 2026-05-25 ahead of sequencing — see [[stage1-contract-change-path-a-2026-05-25]]. Phases A/B/C still active."
metadata: 
  node_type: memory
  type: project
  originSessionId: f7c71005-682b-4044-b08a-31f8be272dc2
---

**STATUS 2026-05-25:** Phase D shipped (out of sequence — see [[stage1-contract-change-path-a-2026-05-25]]). Phases A, B, C still pending. The wiring fix that Phase D depended on landed in the same session: see [[engine-to-posture-controls-wiring-fix]].

Active plan agreed 2026-05-22 to align posture per control with the two-stage HITL contract the user defined:
- Stage 1 = "system evaluation is accepted" (the extracted evidence is real)
- Stage 2 = "the control can acquire the suggested posture" (engine verdict applied)

**Why:** today `stage1_review_chat.py` (functions at lines 225 and 486) writes `posture_controls.finding` and logs `posture_status_log` with `change_kind='extraction'`, bypassing the engine + Stage-2 entirely. 39 posture flips since 2026-05-20 went through this path; A.5.26 NC→Comply on a 4-char "PIMS" excerpt is the canonical case. The engine's principled definition of Comply (curated FulfilmentSpec + approved findings + freshness) is being short-circuited by a flat `_DF_STATUS_TO_FINDING` lookup.

**Phase A — extend tooling (no curation policy decisions needed)**
- Add `freshness_days` to `EvidenceRequirement` dataclass + propagate via `enrichment/documents/load_to_neo4j.py`. Today no leaf has freshness, so the engine's freshness gate is a permanent no-op.
- Split `enrichment/documents/document_requirements.py` (640 lines) into per-family files (`req_iso_annex5.py`, `req_iso_annex6.py`, `req_gdpr_chap2.py`, etc.) so each curation PR stays reviewable. Re-export via `ALL_EVIDENCE_REQUIREMENTS`.
- Add curation-lint CI gate: no `RequirementNode` without an explicit `curated` / `explicit_empty` / `deferred_to_findings` decision.

**Phase B — bulk curation content (the big one)**
- LLM-draft `EvidenceRequirement` entries for the 410 uncurated controls (126 ISO − 14 curated = 112; 303 GDPR − 5 curated = 298). Source = `RequirementNode.obligation_text + business_description + cross_framework_summary`, all already in Neo4j.
- Human curator reviews per family (one PR per family). HITL on our side mirrors HITL on the tenant side.
- Loader is idempotent (MERGE-based) — safe to re-run after each merge.

**Phase C — polite gap surface (parallel with B)**
- Extend `ControlVerdict` with `our_gaps` and `tenant_gaps`, splitting the existing `gap_list`.
  - our_gaps: uncurated spec, applies_when references unknown fact, evidence_type missing from catalogue, empty MUST items.
  - tenant_gaps: `items_unrecognised`, freshness fail, no artifact of evidence_type, AT_LEAST_N threshold not met.
- Engine + chat copy distinguishes them per [[human-in-the-loop-positioning]]: first-person plural for our side ("We're still curating…"), neutral observation for theirs ("Your <type> doesn't yet mention…"). Never accuse the tenant for what is a curation gap.

**Phase D — Stage-1 contract change** — SHIPPED 2026-05-25 (commit d6329c4, see [[stage1-contract-change-path-a-2026-05-25]])
- ✓ Stripped `UPDATE posture_controls SET finding` and the posture_status_log INSERT from both mutation sites in `stage1_review_chat.py`.
- ✓ Stage-1 now only sets `document_findings.review_status='approved'` + `posture_controls.confirmation_status='document_confirmed'`. No log row.
- ✗ Post-Stage-1 engine kick NOT wired. Chat copy promises it ("the engine will propose a posture update for your Stage-2 review") but actual write happens lazily on next `load_posture`. Acceptable for now; flag if a tenant expects an immediate Stage-2 proposal queue update.
- ✓ Stage-2 (`stage2_approval_chat.py`) is the only path that mutates `posture_controls.finding`. `change_kind='engine'` on log.

**Arion Networks cleanup (partially shipped 2026-05-25)**
- ✓ Reverted 27 Stage-1-driven flips (plan estimated 39; the 27 was the actual count of rows where `status_before IS NOT NULL` in extraction log entries). `change_kind='revert'` via schema_v28.
- ✗ 111 "PIMS"-excerpt approved findings still active. Need `review_status='rejected'`, `is_active=false`, rejection_reason='extractor noise — single-token cell; mass-rejected during Stage-1 contract cleanup'. NOT done.
- ✗ Extractor bug at `rag/intake/extractor.py:113` NOT fixed.
- ✗ Re-extract from existing workbook uploads NOT done.

**Alternatives rejected on 2026-05-22:**
- "Workbook is assessor-grade, bypasses engine" → rejected; user wants single source of truth (engine + Stage-2).
- "Engine falls back to flat status-to-finding for uncurated controls" → rejected; same garbage-in-garbage-out as today's Stage-1 path.
- "Hand-curate everything" → rejected as primary; LLM-draft with per-family human review is the chosen path.

**Sequencing decision** (original): Stage-1 contract change ships AFTER curation is complete. **Overridden 2026-05-25** — user chose to ship Phase D early to restore the eval baseline. The UX cliff concern remains: tenants now see reverted pre-Stage-1 posture state for 27 controls, not engine-computed verdicts.

**How to apply:** Phases A, B, C still active — work the phase you're in. Phase D done; if touching Stage-1 chat surfaces, see [[stage1-contract-change-path-a-2026-05-25]] for the new contract. Future considerations (e.g. document templates) noted at [[curation-document-templates-idea]].
