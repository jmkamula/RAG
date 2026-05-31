---
name: curation-phase-b-batch-7-2026-05-31
description: "SHIPPED 2026-05-31 — A.5.1 (master InfoSec policy) Style v1 → v2 alignment. Not a promotion — A.5.1 was already 4-leaf (first multi-leaf spec ever). Aligned to Phase B policy_program conventions: added freshness_days=365, updated citation format. Zero engine drift, zero MUST/SHOULD churn"
metadata: 
  node_type: memory
  type: project
  originSessionId: a86c2e60-8f0c-4055-b47a-4d07e510249f
---

Seventh Phase B batch — first **alignment** rather than a **promotion**. A.5.1 (Policies for information security) was the very first multi-leaf spec ever curated in this codebase (originally commit 3, "first full multi-leaf spec"), so its leaves already match the modern Phase B policy_program spine shape — but the legacy citation format and missing freshness on the review leaf both pre-dated the Phase B conventions established in batch 2 ([[curation-phase-b-batch-2-2026-05-30]]).

**Spine (unchanged):**

| Control | Primary leaf | Approval | Communication | Review (freshness) |
|---|---|---|---|---|
| A.5.1 | isp_policy | management_approval | communication_record | annual_review **(365d added)** |

**What changed (id-preserving — engine signature unchanged):**
- `freshness_days = 365` added to annual_review (original spec had no freshness)
- Citation rationale strings: "A.5.1 — defined" → "27002:5.1 — defined" (Phase B format)
- Cross-control example list added inline on `topic_refs` MUST (A.5.10/A.5.12/A.6.4)
- Section header refreshed to document the v1→v2 alignment provenance
- `annual_review` description extended to call out the annual cadence rationale (master policy stable; topic-specific policies move faster on independent cycles)

**What did NOT change:**
- MUST/SHOULD ids and counts preserved exactly: 5/2 policy, 3/1 approval, 3/2 communication, 3/2 review
- Leaf evidence_type unchanged
- REQUIRES_EVIDENCE / ChecklistItem counts identical: 206/201/1546/206
- Engine verdict on tenant Arion: OFI at 1/4 children satisfied (policy leaf 5/5; approval/communication/review 0/3 each). Identical to pre-alignment.

**Why no new eval case:**
- The alignment is internal (citation format strings) plus latent (freshness only activates once review evidence exists). Currently the review leaf is `satisfied=False` so freshness is irrelevant.
- Existing cases **33/34/36/38** already lock the A.5.1 OFI verdict end-to-end across the chat surface and approval surface. All four passed in the post-alignment run.
- A new "pending engine verdict for A.5.1" case would not work: case 38 runs before it and approves the engine verdict (idempotent), after which Stage-2 list_one returns "already approved" not "1/4 children satisfied".

**Pattern for future Style v1 → v2 alignments:**
- Same precautions apply to any other legacy 4-leaf control found pre-Phase B (none known yet — A.5.1 was the only pre-program multi-leaf).
- Always run `compute_engine_verdicts` BEFORE and AFTER to confirm signature unchanged.
- 0 stale edges + 0 orphan items at loader = correct signal that alignment was id-preserving.
- Skip new eval case unless the alignment introduces an observable behaviour change.

**Eval result: 63/64 PASS** run-time (#25 known-stale; #24 and #21 happened to pass). All A.5.1 cases (33/34/36/38) PASS post-alignment.

**Phase B remaining (unchanged — A.5.1 already counted as multi-leaf):**
- ISO 27001: ~92 thin single-leaf controls remaining
- GDPR: ~297 empty articles still untouched
- policy_program applied to 6 controls now (A.5.1 + A.5.3/4/10/12/15 from batch 2)
- operational_process applied to 11 controls (A.5.18 + supplier 4-pack + A.5.23 + incident 3-pack + A.5.7 + A.5.28)

**Next-likely candidates (still single-leaf):**
- A.5.8 project security integration (op_process)
- A.5.11 return of assets (op_process)
- A.5.14 information transfer (could be op_process or policy_program)
- A.5.13 labelling of information (op_process)
