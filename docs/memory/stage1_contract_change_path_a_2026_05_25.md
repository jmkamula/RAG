---
name: stage1-contract-change-path-a-2026-05-25
description: "Phase D of [[posture-engine-alignment-plan-2026-05-22]] shipped 2026-05-25 via 'Path A': revert 27 Stage-1-driven flips + strip stage1_review_chat.py finding mutations + schema_v28. Sequencing deviated from plan (shipped before Phase B curation)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 05fd0622-fbff-4999-9132-e4622a40b0f2
---

Phase D ("Stage-1 contract change") of [[posture-engine-alignment-plan-2026-05-22]] shipped 2026-05-25 in commit d6329c4 alongside the [[engine-to-posture-controls-wiring-fix]] (9ac0ac3) and the eval baseline lock-in (6f3f1b8). The session ran the user's "Path A" choice from a question framed around the 7 eval failures (6 FAIL + 1 WARN) the wiring fix exposed.

**What landed:**
- `rag/posture/stage1_review_chat.py` — both mutation sites stripped:
  - `approve_findings_for_control` (~line 225): UPDATE no longer sets `finding = headline`; the posture_status_log INSERT removed entirely
  - `_recompute_posture_for_control` (~line 486): same strip; function kept because `approve_findings_by_ids` still calls it for the per-id variant, but now it only flips `confirmation_status='document_confirmed'` + audit fields
- `render_stage1_answer` copy: "Posture flipped from X to Y" → "The extracted evidence indicates X — the engine will propose a posture update for your Stage-2 review."
- `db/schema_v28_posture_log_revert_kind.sql` — adds `'revert'` to posture_status_log.change_kind CHECK so cleanup operations have a distinct audit token vs `'extraction'`.
- Data: 27 controls reverted on Arion Networks tenant by replaying earliest `status_before` from `posture_status_log` rows where `change_kind='extraction'` AND `status_before IS NOT NULL`. Audit row inserted per revert with `change_kind='revert'`, `source='document'`, `evidence_citation='Path A cleanup 2026-05-25: revert Stage-1 finding mutation per active plan'`. Restored: A.5.18 NC, A.5.26 NC, A.8.19 OFI, A.5.30/34/37/4 Comply, A.7.11/12 + A.8.21..33 N/A, Art.28 'Not assessed', etc.

**Why the sequencing deviated.** The plan said "Stage-1 contract change ships AFTER curation is complete" to avoid the UX cliff of 410 uncurated controls flipping to UNKNOWN. The user overrode that to fix the immediate eval-baseline regression — 6 prior known-stale cases plus the new label-fix case all needed the revert + strip to pass. The UX cliff concern remains: tenants viewing chat right now see the restored pre-Stage-1 posture state for the 27 reverted controls, not engine-computed verdicts (since most are single-leaf-no-derived and don't get engine proposals).

**What did NOT ship from the plan's Path A scope:**
- 111 PIMS-excerpt approved findings still in `document_findings` with `review_status='approved'`. Plan calls for `is_active=false` + `rejection_reason='extractor noise — single-token cell; mass-rejected during Stage-1 contract cleanup'`. Untouched this session.
- Extractor bug at `rag/intake/extractor.py:113` (reverse the `gap_description or evidence_text` precedence). Untouched.
- Re-extract from existing workbook uploads. Untouched.
- Post-Stage-1 engine-kick that immediately writes `engine_proposed_finding` after evidence confirmation. The chat copy now promises this ("the engine will propose a posture update for your Stage-2 review") but the trigger isn't wired — it relies on the next `load_posture` call to run the overlay. Acceptable for now but creates a perception gap if the tenant reads the chat response and doesn't see a Stage-2 proposal queued immediately.

**Eval state:** 39/39 PASS on `results/eval_20260525_1314_path_a.csv`. Prior known-stale cases (#2, #3, #4, #24, #25, #28) all restored.

**How to apply:** When touching Stage-1 chat surfaces or the writer (`rag/intake/posture_writer.py`), respect the new contract — Stage-1 confirms evidence (document_confirmed) and the engine + Stage-2 own `finding`. The writer still writes `finding` at extraction time (draft) which is the source data Stage-1 confirms — that path is unchanged. When picking up Phase B (bulk curation), the 27 reverted controls become the chat baseline; engine proposals will start landing as curation lands more multi-leaf or derives_from compositions.

Related: [[posture-engine-alignment-plan-2026-05-22]], [[engine-to-posture-controls-wiring-fix]], [[hitl-two-stage-approval-design]], [[hitl-two-stage-rollout-gotchas]], [[human-in-the-loop-positioning]].
