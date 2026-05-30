---
name: curation-phase-b-batch-1-2026-05-29
description: "SHIPPED 2026-05-29 (commit b354e16): first Phase B bulk drafting batch — A.5.5/A.5.6/A.5.9/A.5.31/A.5.32 records_program 4-leaf + global review-title cadence-label normalisation to 'Periodic'. Eval 44/45 → 49/50."
metadata: 
  node_type: memory
  type: project
  originSessionId: a20ce676-21d0-4092-b52c-855d9bbf0170
---

First Phase B bulk drafting batch after the calibration arc ([[curation-session-state-2026-05-26]]). All five ISO A.5 register-style controls promoted from single-leaf to records_program 4-leaf in one pass.

**Five controls promoted (commit b354e16):**

| Control | Spine application | Review freshness |
|---|---|---|
| A.5.5  Authority contacts | register + maintenance + applicable_authorities_scope + review | 365d |
| A.5.6  SIG contacts | register + engagement_procedure + risk_topic_scope + review | 365d |
| A.5.9  Asset inventory | register + lifecycle + discovery_upstream + reconciliation | 90d * |
| A.5.31 Legal register | register + maintenance + applicable_obligations_scope + review | 180d |
| A.5.32 IPR | procedure + inventory + acquired_works_upstream + audit | 365d † |

* A.5.9 also keeps freshness=90 on the register itself (dual freshness, deviates from records_program default of review-only freshness). Asset drift is daily and A.5.9 is the foundation for half of Annex A — stricter cadence justified.

† A.5.32 is the adapted variant. IPR has both procedural duties (usage controls, third-party respect) and inventory aspects (licensed software, open-source, owned IPR), so the existing procedure leaf id is retained alongside a new inventory leaf. `licensed_inventory` + `renewal_tracking` items moved off the procedure leaf onto the new inventory; `audit_cadence` moved to the new audit leaf. The declarative orphan-prune from [[loader-orphan-cleanup-followup]] handled the stale edge cleanup automatically (1 MUST + 2 SHOULD pruned, 0 orphan items).

**Cadence-label normalisation (companion change in same commit):**

All review-leaf titles renamed to `"Periodic <thing> Review"` everywhere. Was a 3-way mix of "Annual" / "Semi-Annual" / "Periodic" — drift from drafting different controls at different times.

**Why:** `freshness_days` enforces the cadence contract; the title shouldn't duplicate or pre-commit. If freshness changes (e.g. tighten 365→180 for hot controls), the title shouldn't follow. Standards themselves say "at planned intervals" — they don't mandate annual.

**How to apply:** Future review-leaf titles use `Periodic` only. Cadence-as-content lives in the description body (e.g. "...typically annual" or "...semi-annual given regulatory churn") — never in the title. 7 titles renamed: A.5.1, A.5.2, A.5.5, A.5.6, A.5.31, A.5.32, Art.15, Art.30.

**Eval result:** 44/45 → 49/50 PASS. Cases 46-50 added to lock the 5 new promotions via the same Stage-2 list_one + "0/4 children satisfied" assertion shape as 42-45. Case #25 remains the known-stale fail.

**Engine + Stage-2 verification done before commit:** Re-ran posture_loader to refresh engine_proposal_reason for the five controls — all moved from "ALL: 0/1 children satisfied" (single-leaf pre-state) to "ALL: 0/4 children satisfied" (4-leaf signature). All 5 stay at engine_proposal_status='proposed' for user Stage-2 review.

**Phase B remaining (post-batch tally):**
- ISO 27001: ~107 thin single-leaf controls remaining (117 − 5 calibration − 5 this batch)
- GDPR: ~297 empty articles still untouched (303 − 6 already curated through derived chains)
- Pace: solo review ~5-10/day. This batch was 5 controls; one bulk batch per session is sustainable.

**Spine model after this batch:** unchanged from [[curation-session-state-2026-05-26]] — records_program promoted from "sixth candidate" to "validated sixth spine" after surviving 5 fresh applications. No new spines proposed.

**Next-likely batch candidates** (records_program-shaped, in numeric A.5 order):
- A.5.27 (lessons learned register) — but currently framed as procedure; may need spine choice between operational_process and records_program
- A.5.33 (records protection) — policy-shaped, probably policy_program not records
- A.6.x screening records, A.6.4 disciplinary records — records, but in A.6 not A.5
- A.8.8 (vulnerability register), A.8.15 (logging), A.8.16 (monitoring) — registers but technical_control natural fit

Next bulk batch probably switches spine to either operational_process (A.5.7 threat intel, A.5.19 supplier risk) or policy_program (A.5.3, A.5.4, A.5.10 acceptable use).
