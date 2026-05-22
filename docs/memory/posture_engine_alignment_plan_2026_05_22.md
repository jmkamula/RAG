---
name: posture-engine-alignment-plan-2026-05-22
description: "Phased plan agreed 2026-05-22 to fix Stage-1 contract violation, complete Neo4j curation, add polite gap messaging; supersedes provisional state in [[hitl-two-stage-approval-design]]"
metadata: 
  node_type: memory
  type: project
  originSessionId: f7c71005-682b-4044-b08a-31f8be272dc2
---

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

**Phase D — Stage-1 contract change (ships after curation completes)**
- Strip `_recompute_posture_for_control` and `UPDATE posture_controls SET finding` from `stage1_review_chat.py`.
- Stage-1 then only sets `document_findings.review_status='approved'` + `posture_controls.confirmation_status='document_confirmed'`. No posture_status_log row.
- Wire post-Stage-1 engine kick that writes `engine_proposed_finding`, `engine_proposal_status='proposed'`, snapshot `engine_proposal_reason`.
- Stage-2 becomes the only path that mutates `posture_controls.finding`. Log entry there is `change_kind='engine'`.

**Arion Networks cleanup (sequenced with D)**
- Revert the 39 Stage-1-driven posture flips logged from 2026-05-20 onward by replaying `status_before` from `posture_status_log`.
- Reject the 111 "PIMS"-excerpt approved findings (`review_status='rejected'`, `is_active=false`, `rejection_reason='extractor noise — single-token cell; mass-rejected during Stage-1 contract cleanup'`). Audit-preserving.
- Fix the one-line excerpt bug at `rag/intake/extractor.py:113` — reverse the `gap_description or evidence_text` precedence so the Justification column beats the Notes column when both are present.
- Re-extract from existing workbook uploads to backfill substantive excerpts.

**Alternatives rejected on 2026-05-22:**
- "Workbook is assessor-grade, bypasses engine" → rejected; user wants single source of truth (engine + Stage-2).
- "Engine falls back to flat status-to-finding for uncurated controls" → rejected; same garbage-in-garbage-out as today's Stage-1 path.
- "Hand-curate everything" → rejected as primary; LLM-draft with per-family human review is the chosen path.

**Sequencing decision:** Stage-1 contract change ships AFTER curation is complete, not in parallel. Avoids the UX cliff of 410 controls flipping to UNKNOWN while curation catches up.

**How to apply:** This is the active plan. When touching Stage-1/Stage-2/engine code or curation files, work the phase you're in and don't shortcut past D's prerequisites. Future considerations (e.g. document templates) noted at [[curation-document-templates-idea]].
