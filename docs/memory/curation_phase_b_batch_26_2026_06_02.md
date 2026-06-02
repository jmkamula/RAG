---
name: curation-phase-b-batch-26-2026-06-02
description: Phase B batch 26 — ISMS chapters 8 + 9 + 10 close-out 8-pack. FINAL ISO 27001 BATCH. Operation + Performance Evaluation + Improvement. Most uniform single-batch spine (all 8×op_process). Closes ISO 27001 ISMS clauses fully. Includes a load-bearing regex bug fix for two-digit clause refs (10.1/10.2).
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 26 — chapters 8 + 9 + 10 close-out 8-pack. FINAL ISO 27001
batch. ISMS Operation + Performance Evaluation + Improvement clauses
promoted to 4-leaf Style v2. 24 new evidence requirements (32 total
leaves; 8 primary leaves preserved/replaced in-place).

**Why:** User chose "start batch 26" after batches 24 + 25 closed
chapters 4-7. This is the third and final batch in the "three batches
by theme" plan. After this lands, ISO 27001 will be fully curated
(Annex A 93/93 + ISMS clauses 25/25), and the curation arc moves to
GDPR.

**How to apply:** Most uniform single-batch spine to date — all
8×op_process. Chapters 8/9/10 are the operational PDCA cycle in
action (Plan → Do → Check → Act mapped to Operation / Eval /
Improvement). The op_process spine variant fits everything:
- 8.1 operational planning (procedure-as-primary)
- 8.2 operational risk assessment (per-assessment record as primary)
- 8.3 operational risk treatment (per-treatment record as primary)
- 9.1 monitoring + measurement (procedure-as-primary)
- 9.2 internal audit (programme-as-primary; primary id preserved)
- 9.3 management review (minutes-as-primary; primary id preserved)
- 10.1 continual improvement (procedure-as-primary)
- 10.2 NC + corrective action (procedure-as-primary)

**Two new freshness conventions in this batch:**
- 8.3 review freshness=180 (operational tempo; faster than typical
  annual 365d on review leaves). Operational treatment execution
  needs semi-annual program-review oversight, not annual.
- 9.1 measurement_record freshness=90 (quarterly tempo). FIRST
  freshness=90 in any ISMS clause promotion. Reflects that measurement
  signals decay fastest — a 365d-stale measurement is useless. The 9.1
  PROCEDURE review still runs annually (365d); the measurement RECORD
  refreshes quarterly. This pattern (faster-data, slower-meta) may
  apply elsewhere when there's a high-frequency data leaf and a
  lower-frequency methodology leaf in the same spec.

**LOAD-BEARING REGEX BUG FIX:**
The control-ref regex in 3 places (stage1_review_chat.py,
stage2_approval_chat.py, acknowledge_chat.py) used:
```
r"\d\.\d+(?:\.\d+)?"
```
The leading `\d` (single digit) means "10.1", "10.2" don't match —
they parse as "0.1", "0.2" which fail the word boundary. So before
this batch, the chat surface for clauses 4-9.x worked but 10.x didn't.
Smoke-test caught it on first 10.2 query (returned the full
127-control list instead of single-control verdict). Changed to
`\d+\.\d+` in all three copies. API restart required to pick up the
new regex.

Lesson: when introducing a new ref-shape range, smoke-test the
HIGHEST value, not just the lowest. The lowest (8.1) worked through
the same regex that broke on 10.1.

**Shipped (commit pending — current session 2026-06-02):**
- 32 leaves total (8 × 4-leaf), 24 new (8 primary leaves preserved
  on existing single-leaf REQs at top-of-file or bulk section)
- 8.1 op_process: planning_procedure + execution_register +
  applicable_processes_scope + program_review (365d)
- 8.2 op_process: assessment_record (freshness=365) +
  trigger_procedure + applicable_scope + program_review (365d).
  Trigger procedure is the operational link to 6.1.2 — codifies
  what "significant change" means in practice
- 8.3 op_process: treatment_record (freshness=180) +
  execution_procedure + applicable_plan_scope + program_review (180d).
  FIRST batch with 180d on BOTH primary record and program review —
  operational tempo throughout
- 9.1 op_process: monitoring_procedure (freshness=365) +
  measurement_record (freshness=90) + applicable_scope +
  program_review (365d). FIRST ISMS clause with freshness=90
- 9.2 op_process: internal_audit_programme (primary, id preserved) +
  audit_execution_record (freshness=365) + coverage_scope +
  program_review (365d). Coverage scope leaf encodes
  surveillance-cycle expectations (which processes audited each year
  in the 3-year cycle) — surveillance auditors look for this
  explicitly
- 9.3 op_process: management_review_minutes (primary, id preserved;
  freshness=365 annual minimum) + review_procedure +
  applicable_inputs_outputs_scope + program_review (365d). Inputs
  scope encodes 9.3.2 a-g MUST inputs at scope level (cycle-level)
  separate from per-minute MUSTs (per-review level)
- 10.1 op_process: improvement_procedure + action_register +
  applicable_triggers_scope + program_review (365d). 10.1/10.2
  boundary explicit in scope leaf
- 10.2 op_process: nc_ca_procedure + nc_register +
  applicable_nc_sources_scope + program_review (365d). Root-cause-
  quality MUST in program review enforces blame-free systemic
  analysis (not "human error" as the only documented cause).
  Recurrence-check MUST closes the loop on whether corrective
  actions actually worked
- All 8 engine verdicts: NC 0/4 children satisfied
- All 8 surface in Stage-2 (engine NC ≠ live OFI on every clause)
- 8 eval cases added (150-157), all PASS expected
- Stale-edge prunes: 0 (clean state — all item ids preserved on
  primary leaves)

**Item-id preservation:**
NO DerivedSpec references to any chapter 8/9/10 items (confirmed
once at batch 24). Primary-leaf ids preserved on the anchor REQs:
req:9.2:internal_audit_programme + req:9.3:management_review (along
with all item:9.2:* and item:9.3:* ids). All 8 primary leaves keep
their pre-batch ids.

**Posture-seed step (continuing batches 24/25 pattern):**
9.2 already had an active OFI posture row (created in an earlier
session via Stage-1 chat path or similar). 7 other clauses (8.1, 8.2,
8.3, 9.1, 9.3, 10.1, 10.2) had no rows — seeded with finding='OFI'
matching Arion's pre-ISMS narrative.

**Total spine variant mix across ISO 27001 ISMS clauses (25 total):**
- 14×op_process (6.1.1, 6.1.2, 6.1.3, 6.3, 7.3, 7.4, 8.1, 8.2, 8.3,
  9.1, 9.2, 9.3, 10.1, 10.2)
- 5×records_program (4.1, 4.2, 6.2, 7.1, 7.2)
- 6×policy_program (4.3, 4.4, 5.1, 5.2, 5.3, 7.5)

op_process dominates (14/25 = 56%) — reflects that ISMS clauses are
mostly procedural execution + record-keeping. Policy_program is
chapter-4/5-heavy (direction-setting). Records_program is mostly
chapter-4/7-heavy (inventory-style records).

**Cross-control link web (operational PDCA):**
- 8.1 → 6.1.1 (planning handoff); 8.1 → A.5.19/A.5.20 (outsourced
  processes)
- 8.2 → 6.1.2 (uses 6.1.2 methodology, doesn't redefine it); 8.2 →
  6.1.3 (new risks flow to treatment plan)
- 8.3 → 6.1.3 (implements 6.1.3 plan); 8.3 → SoA (newly implemented
  controls reflected in SoA)
- 9.1 → 9.3 (measurements feed management review per 9.3.2c)
- 9.2 → 10.2 (audit findings that are NCs route to 10.2);
  9.2 → 9.3 (audit results feed mgmt review per 9.3.2a)
- 9.3 → 10.1 (mgmt review decisions drive continual improvement
  per 9.3.3); 9.3 → 6.3 (mgmt review decisions can drive ISMS
  changes)
- 10.1 → 6.3 (improvement actions may drive ISMS changes); 10.1 ↔
  10.2 boundary (observations route here, NCs to 10.2)
- 10.2 → A.5.26 + A.5.27 (incident response + lessons cross-links);
  10.2 → 6.3 (systemic NCs drive ISMS-level changes)

**Three insights from the final ISO batch:**

1. **All-op_process batches are possible at scale.** When the
   underlying clauses share an operational shape (every clause in
   chapters 8/9/10 maps to a Do/Check/Act activity), forcing variety
   in the spine would be inauthentic. The op_process spine generalises
   well — primary procedure, supporting record, scope note, review.
   Don't artificially diversify when the standard doesn't.

2. **Faster-data/slower-meta is a recurring pattern.** 9.1's
   measurement_record (90d) + monitoring_procedure (annual review)
   captures it most explicitly. 8.3's 180d on both primary and review
   shows a different version (uniformly faster). The freshness choice
   should match how often the underlying signal actually changes —
   not the spine's default.

3. **Two-digit clause refs revealed a long-standing regex bug.**
   The `\d\.\d+` pattern in three chat-parser modules predates batch
   24 — it always failed on 10.x but no one noticed because chapter
   10 wasn't curated yet. New ref-shape ranges should always be
   smoke-tested at both LOW and HIGH bounds, not just the lowest.

**Where this leaves the curation arc (post batch 26):**
- **ISO 27001 FULLY CLOSED** — Annex A 93/93 + ISMS clauses 25/25 =
  118/118 total controls multi-leaf. The full curation arc that
  started 2026-05-26 with A.5.18 (case #1, the OG NC) is now complete
  for ISO.
- GDPR: mixed (~5 already multi-leaf from earlier calibrations:
  Art.15, Art.28, Art.30 + a few derived). Most articles still
  single-leaf or empty. Next batches will tackle GDPR.

**Next batch (batch 27 — GDPR begins):**
GDPR is a fundamentally different shape from ISO. Most articles are
derivation-based (Art.5/Art.32/Art.25 already use DerivedSpec).
Direct-evidence articles (Art.13/Art.30/Art.15/Art.34) are
process/document-shaped, similar to ISMS clauses. The first GDPR
batch should probably tackle either:
(a) Art.5 principles (Art.5.1.a-f + Art.5.2) — already derivation-
    shaped, this would just be cleaning up consistency, OR
(b) Art.13 / Art.14 privacy notices — direct-evidence policy_program
    promotion.

See also: [[curation-phase-b-batch-25-2026-06-02]] (chs 6+7
close-out), [[curation-phase-b-batch-24-2026-06-02]] (chs 4+5
close-out; posture-seed pattern established), [[curation-program-
full-multi-leaf]] (program-level decision).
