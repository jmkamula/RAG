---
name: posture-assertions-phase-1b
description: "Phase 1b actor-model migration — posture_loader writes engine proposals to posture_assertions, Stage-2 readers JOIN; PC.engine_proposed_* kept as legacy bridge for pre-1a terminal-lifecycle controls."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6eab9acf-b813-4ddd-9b19-4c99f569ad55
---

**Phase 1b of the actor-model rework — SHIPPED 2026-06-03**

The writer + reader swap that landed on top of [[posture-assertions-phase-1a]] (commit 6d07048, schema_v29).

**Writer (rag/posture_loader.py:_persist_engine_proposals)**
* Stops writing `posture_controls.engine_proposed_finding` / `engine_proposal_reason`.
* Calls `set_assertion(source='engine', status='pending', finding=..., gap_description=reason, set_by='engine')` instead — verdict (finding + reason + set_at) lives in `posture_assertions` from here on.
* Still bumps `posture_controls.engine_proposal_status='proposed'` + `engine_proposed_at=NOW()` as the lifecycle marker (the approve/reject flow toggles `engine_proposal_status`; the supersession model owns only the verdict, not lifecycle).
* Reverse-sync trigger (Phase 1a) does NOT fire on lifecycle column updates — it watches `finding/source/gap_description/confidence` — so no trigger loop.

**Readers**
* `rag/posture/stage2_approval_chat.py` — `list_pending_proposals`, `get_proposal_for_control`, `approve_engine_proposal`, `reject_engine_proposal` all LEFT JOIN `posture_assertions pa ON ... AND pa.source='engine' AND pa.status='pending'` to pull `pa.finding AS proposed_finding`, `pa.gap_description AS reason`, `pa.set_at AS proposed_at`. PC still owns `engine_proposal_status` (lifecycle) and `engine_approved_by/at`.
* `api_server.py:dashboard_posture` migrated to the same JOIN pattern.

**Why:** [[posture-assertions-phase-1a]] flagged the engine-proposal write as the only writer that wasn't mirrored to `posture_assertions` via the reverse-sync trigger (the trigger watches the live `finding` column, not the `engine_proposed_finding` snapshot column). Phase 1b closes that gap by making `set_assertion()` the primary writer. User chose "migrate Stage-2 readers in 1b too — close all loose ends" over the narrower options.

**How to apply:** When extending Stage-2 surfaces, read engine proposal finding/reason from `posture_assertions` pending engine rows; read lifecycle (proposed/approved/rejected/none) from `posture_controls.engine_proposal_status`. Don't write to `posture_controls.engine_proposed_finding` / `engine_proposal_reason` from new code — those columns are kept only as a transitional read-side bridge (see below).

**Legacy PC.engine_proposed_* bridge — load-bearing footgun**

Phase 1a's backfill captured pending engine PA rows ONLY where `engine_proposal_status='proposed'` (2 rows on Arion). Pre-1a approved (167 rows) and rejected (0 rows on Arion) controls had `engine_proposed_finding/reason` on PC but NO corresponding PA row.

First Phase 1b sweep without the bridge fix re-proposed all 167 approved controls (flipped lifecycle 'approved' → 'proposed'), because the writer's "skip no-op" check looked only at PA pending (none for approved) and the live-finding-agreement skip (`live_finding == posture and cur_status in ("none", None)`) didn't match (`cur_status='approved'`). Fix:

```python
# Resolve the prior-proposal snapshot. PA pending is the new canonical
# source; PC.engine_proposed_* is a legacy bridge for controls whose
# lifecycle was already approved/rejected at Phase 1a backfill time.
if pending is not None:
    prior_finding = pending["finding"]
    prior_reason  = pending["gap_description"] or ""
else:
    prior_finding = legacy_finding   # PC.engine_proposed_finding
    prior_reason  = legacy_reason or ""
if prior_finding is not None:
    if prior_finding == posture and prior_reason == reason:
        continue
```

`get_proposal_for_control` also COALESCEs `pa.finding` with `pc.engine_proposed_finding` so the 'approved' / 'rejected' renderers still surface the historical proposed verdict ("engine verdict 'NC' already approved. Live finding: 'NC'.").

**Recovery from 167-row regression (2026-06-03 session):** restored via `UPDATE posture_controls SET engine_proposal_status='approved' WHERE engine_approved_at IS NOT NULL AND finding = engine_proposed_finding` (matching = was approved; mismatch = was rejected; Arion happened to have 0 rejected). Plus superseded the 167 errant pending PA rows the buggy writer had created.

**Eval result:** 194/198 PASS on `results/eval_20260603_1406_phase_1b.csv`. Four failures:
* #25 known-stale (anti-hallucination)
* #24 known-stale (Art.32 A.5-bridge LLM-stochastic)
* #2 LLM-stochastic (A.5.26 in top-N NC list — re-verified 2/3 hits)
* #33 LLM-stochastic (OFI literal in answer — re-verified 3/3 hits)

No Phase 1b functional regression.

**Phase 1c deferred items** (per [[hitl-two-stage-approval-design]] decision in this session):
1. Approve/reject paths should supersede the pending PA row on decision (currently the lingering pending row + lifecycle column drift).
2. Once 1c lands, the legacy PC.engine_proposed_finding/engine_proposal_reason bridge can be retired — Stage-2 readers will pull historical approved/rejected verdicts from PA superseded/active rows instead.
3. Related to [[engine-agreement-suppression]] — preserved at PA layer in 1b (same `live_finding == posture` skip), still product debt.
