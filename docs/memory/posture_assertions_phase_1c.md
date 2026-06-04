---
name: posture-assertions-phase-1c
description: "Phase 1c actor-model migration — PC engine bridge cols DROPPED via schema_v30; engine_authored_only filter on PA must exclude both 'trigger:%' and 'backfill:%' set_by, or the wrong-text v29 backfill row outranks the correct superseded engine row."
metadata: 
  node_type: memory
  type: project
  originSessionId: cb718a38-e78c-4d50-bc70-1d098a96b212
---

**Phase 1c of the actor-model rework — SHIPPED 2026-06-03 (commit 75278ce)**

Closes [[posture-assertions-phase-1b]] by dropping the legacy PC engine bridge columns and migrating the last readers/writers to posture_assertions. schema_v30 + 4 files: `db/schema_v30_drop_engine_proposal_bridge.sql`, `rag/posture/assertions.py`, `rag/posture/stage2_approval_chat.py`, `rag/posture_loader.py`.

**Why:** the bridge cols (`engine_proposed_finding`, `engine_proposal_reason`) were a transitional read-side fallback for pre-1a terminal-lifecycle controls (167-row scar). Phase 1c retires them so PA is the single source of truth for engine verdicts.

**How to apply:** Engine proposal verdict (finding + reason) lives in `posture_assertions` source='engine' rows. Lifecycle stays on `posture_controls.engine_proposal_status` + `engine_proposed_at` + `engine_approved_by/at`. The dashboard endpoint preserves the JSON response shape via `SELECT pa.finding AS engine_proposed_finding, pa.gap_description AS engine_proposal_reason` from a PA-pending JOIN — frontend keys unchanged.

**Non-obvious scar — schema_v29 backfill conflated gap_description sources**

The Phase 1a backfill rolled the bridge state into PA with `set_by='backfill:schema_v29'` and `gap_description = pc.gap_description`. But `pc.gap_description` is the LIVE tenant narrative (often Stage-1-confirmed text like "Contact with relevant authorities maintained..."), NOT the engine's verdict reason (which would be "ALL: 0/4 children satisfied"). Same control got a status='active' PA row with the live narrative text under `set_by='backfill:schema_v29'`.

`get_latest_engine_assertion` orders status='pending' > 'active' > 'superseded'. So the wrong-text 'active' backfill row outranks the correct 'superseded' engine row in the no-op comparison. First Phase 1c sweep flipped 165 approved → proposed because the no-op check kept comparing engine's current reason against the live-narrative-text backfill row and seeing a mismatch.

**The fix:** rename `exclude_trigger_writes` → `engine_authored_only` and extend its filter to exclude BOTH `'trigger:%'` AND `'backfill:%'` set_by. Trigger writes capture PC.gap_description live, backfill writes capture PC.gap_description as-of backfill time — both are PC-snapshot text, not engine-authored text.

**Recovery from 165-row regression:** match candidates by `engine_proposal_status='proposed' AND engine_approved_at IS NOT NULL AND pending PA finding == PC.finding`. Restore `engine_proposal_status='approved'` + supersede the errant pending PA with `metadata->>'recovery' = 'phase_1c_165_row_regression'`. Two legitimate pending proposals (A.5.23 + A.5.34 partial-evidence OFI 1/4) correctly excluded — live=Comply ≠ engine=OFI breaks the match.

**Eval:** 196/198 on `results/eval_20260603_1646_phase_1c_v2.csv` (#25 known-stale; #17 LLM-stochastic citation-list, same bucket as #3/#21/#33). 196 ≥ 195 baseline ✓.

**Related:** [[engine-agreement-suppression]] still preserved at PA layer (live_finding == posture + cur_status in 'none'/None skips proposal). Not closed in 1c — still product debt.
