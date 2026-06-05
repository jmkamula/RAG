---
name: engine-agreement-suppression
description: "RESOLVED 2026-06-05 (fea23f3): posture_loader writes engine 'active' PA + overlays in-memory on NC/OFI concurrence with live; Comply/N/A concurrence still skipped"
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

**Status:** RESOLVED 2026-06-05 (commit fea23f3, "engine: surface engine reason on NC/OFI concurrence with live").

**What was lossy:** `posture_loader._persist_engine_proposals` skipped proposal persistence when engine agreed with live finding and no proposal existed (`live_finding == posture and cur_status in ("none", None)` → `continue`). Designed to prevent Stage-2 queue flooding with auto-Comply rows, but also discarded the engine's 4-leaf structured reason for NC==NC and OFI==OFI agreement cases. Symmetric blind spot in `_apply_engine_overlay`: gated on `engine_proposal_status='approved'` so the in-memory overlay never fired for concurrence cases either, even when reasoning existed.

**Fix (both halves):**
- **Writer:** at NC/OFI concurrence with no matching prior engine PA, `set_assertion(..., status='active', source='engine', set_by='engine')`. No `engine_proposal_status='proposed'` bump — Stage-2 queue stays clean (there's nothing to decide). Comply / N/A concurrence still skipped.
- **Reader:** overlay gate extended — fires when `verdict.posture in {NC,OFI}` AND `row.finding == verdict.posture`, in addition to the existing `engine_proposal_status='approved'` path. The existing rewrite branch in `_apply_engine_overlay` then replaces `gap_description` with the engine's structured reason + unacked leaf accounting.

**Why:** the 4-leaf reasoning (`'0/4 children satisfied'` + per-role accounting) is strictly more informative than the legacy single-leaf gap_description prose, and the agreement case is exactly where the engine's structured view used to vanish.

**How to apply (future work):**
- On Arion specifically, the change was a no-op at commit time: real NC/OFI concurrence rows all carry `engine_proposal_status='approved'` from the prior Stage-2 mass-approval session (already overlaid via approved-gate path); the 7 'none'-status concurrence rows are synthetic test-section controls (X.XXXX.99) with no curated engine verdict. Forward-looking value: new tenants without Stage-2 history, live postures flipped to NC/OFI outside Stage-2, future re-onboards.
- No eval case appended — a would-fail-pre-change test can't be constructed against current Arion data without reverting a Stage-2 approval. If a real concurrence-without-history case appears later (e.g. new tenant), add the eval then.
- Forward design note from the original suppression analysis still holds: separate `engine_finding` + `engine_reason` (always populated when applicable) from the proposal lifecycle columns. Phase 1b/1c already moved verdict to `posture_assertions`; this commit closes the loop by ensuring the engine PA gets written for concurrence too.

Related: [[posture-assertions-phase-1b]], [[posture-assertions-phase-1c]], [[hitl-two-stage-approval-design]], [[curation-phase-b-batch-4-2026-05-31]] for the originating A.5.26 context.
