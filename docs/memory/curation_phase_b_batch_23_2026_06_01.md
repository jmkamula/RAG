---
name: curation-phase-b-batch-23-2026-06-01
description: Phase B batch 23 — A.8 Technological Controls 33-pack. LARGEST batch yet (2.4× batch 22). 33 promotions + A.8.2 Style v2 alignment = 34 controls all 4-leaf. 132 new evidence requirements. Closes A.8 block.
metadata: 
  node_type: memory
  type: project
  originSessionId: e616419f-f804-435c-89a9-52c1d411073d
---

Phase B batch 23 — A.8 Technological Controls 33-pack bulk promotion. All
33 single-leaf A.8.x controls (A.8.1 + A.8.3 through A.8.34) promoted from
single-leaf to 4-leaf, plus A.8.2 Style v2 alignment. Closes the A.8 block.
LARGEST batch yet by 2.4× (previous: batch 22 A.7 14-pack with 56 leaves;
this batch: 132 leaves).

**Why:** User chose "33-pack mega-batch" after batch 22 closed A.7. A.8 was
the largest remaining ISO block. The 33-control scale is the upper bound of
single-batch viability so far.

**How to apply:** 33-control batches work end-to-end (single commit, single
memory file, single eval-suite update). Key tactic at this scale:
**compact-style elaboration** (5-7 MUSTs per leaf, 1-2 SHOULDs) inherited
from batch 22. Two additional patterns that emerged:

1. **Tombstone consolidation pattern**. Three controls (A.8.11, A.8.24,
   A.8.25) had pre-existing single-leaf entries at non-numeric positions
   in `document_requirements.py` (in the "Universal" section, not the A.8
   block). Tombstone-stub-comment replaces each, then full 4-leaf set is
   added in the consolidated A.8 block. Item-id preservation is critical
   for the SPEC-referenced controls — A.8.11 (3 items via SPEC_ART_25),
   A.8.24 (4 items via SPEC_ART_32). A.8.25 had no SPEC refs (clean).

2. **Style v2 alignment for A.8.2 in same batch as 33 promotions**. A.8.2
   was already 4-leaf from calibration era (2026-05-26). Same-batch
   alignment (parallels A.5.1 batch 7, A.5.18 batch 20, but here as part
   of bulk batch rather than dedicated): bl_pam_tool / bl_jit_capability
   SHOULD→MUST; log_anomaly_alert / log_tamper_protect SHOULD→MUST;
   new rc_sla_met MUST (auditor-critical 24h revocation proof, parallel
   to A.5.16); new rc_a518_pairing MUST (cross-link to A.5.18 general
   access review — closes "privileged subset orphaned" gap).

**Spine mix across the 33 promotions:**
- 8×policy_program (A.8.1/18/20/23/24/25/27/34)
- 20×op_process (A.8.3/7/8/9/10/11/13/15/16/17/19/21/22/26/28/29/30/31/32/33)
- 5×technical_control (A.8.4/5/6/12/14)

Plus A.8.2 alignment (still technical_control) = 34 controls × 4 leaves = 136
EvidenceRequirement nodes in Neo4j post-batch.

**Lifecycle-end record variants used (3 of 33):**
- A.8.10 disposal_record (parallels A.5.28 + A.7.14 disposal pattern;
  also satisfies SPEC_ART_25 storage-limitation comment reference via
  `item:A.8.10:scope_systems` preserved)
- A.8.13 restore_test_record (parallels A.5.30 ICT readiness recovery-
  test pattern; `rec_success_status` parallel: `reg_rpo_met` MUST is
  auditor-critical "RPO actually met" proof)
- A.8.32 change_record (per-change captured with risk tier + approval
  lineage + outcome; emergency-flag + post-hoc-review reference)

**Item-id preservation (critical):**
- **A.8.24** (4 items, referenced by SPEC_ART_32 GDPR Art.32): preserved
  `personal_data`, `pii_keys`, `at_rest`, `in_transit` on the new policy
  leaf (`req:A.8.24:cryptography_policy`)
- **A.8.11** (3 items, referenced by SPEC_ART_25 GDPR Art.25 DPbD):
  preserved `scope`, `techniques`, `personal_data` on the new procedure
  leaf (`req:A.8.11:data_masking_procedure`)
- **A.8.10** (1 item, referenced by SPEC_ART_25 comment): preserved
  `scope_systems` on the new procedure leaf

**Orphan EvidenceRequirement cleanup (new gap surfaced):**
13 A.8.x controls had their primary-leaf `id` field RENAMED during
promotion (e.g. `req:A.8.24:encryption_policy` → `cryptography_policy`).
The loader prunes orphan ChecklistItems and stale MUST/SHOULD edges
per leaf, but does NOT prune orphan EvidenceRequirement nodes whose
ids no longer appear in the registry. Result: 12 stale EvidenceRequirement
nodes left attached to A.8.x controls. Engine reported "0/5 children
satisfied" for A.8.24/A.8.34 (4 real leaves + 1 ghost) before cleanup.

Resolution: one-shot Cypher cleanup deleted the 12 orphans + 49 orphan
ChecklistItems. After cleanup all 33 controls return "0/4 children
satisfied" as expected. Follow-up: see
[[loader-er-orphan-cleanup-followup]] — loader should prune orphan
EvidenceRequirement nodes the same way it prunes orphan ChecklistItems.

Note: orphan list also included 5 GDPR EvidenceRequirements
(req:Art.16/17/25/32/6 various) that look like stale entries from prior
curation passes. NOT in batch 23 scope — left in place for separate
cleanup.

**Live posture and Stage-2 surfacing:**
Predominantly Comply (Arion has decent IT discipline). Live A.8 posture
distribution (post-batch):
- ~28 Comply → engine NC differs → all 28 surface in Stage-2
- A.8.25 N/A (profile_fact: Arion does not develop external software)
  → engine NC differs → surfaces in Stage-2
- A.8.1 OFI, A.8.19 OFI → engine NC differs → both surface

All 33 engine verdicts: NC 0/4 children satisfied. None suppressed via
engine-agreement (which only kicks in for NC == live NC; see
[[engine-agreement-suppression]]).

**Eval cases added (33: cases 100-132):**
Cases inserted at top of EVAL_CASES (descending-id-within-batch + newest-
batch-first convention from batch 22). Each follows the standard
"pending engine verdict for A.8.X" pattern with must_contain checks
for `"engine proposes"`, `"'NC'"`, `"0/4 children satisfied"`. Case
mapping: A.8.1→132, A.8.3→131, A.8.4→130, ..., A.8.34→100. A.8.2
not added — existing case #42 already locks it.

Eval baseline pre-batch: 97/99 (only #24 + #25 known-stale). Post-batch
eval target: 130/132 (same 2 known-stale; all 33 new cases PASS).

**Cross-control link web (compact-style, key links only):**
- A.8.1 → A.7.7 (authentication MUST); A.8.7 (malware); A.5.17 (auth-info)
- A.8.2 → A.5.18 (rc_a518_pairing new MUST — closes "privileged subset orphan" gap)
- A.8.3 → A.5.15 + A.5.16 + A.5.18 (access policy / identity / review)
- A.8.4 → A.5.16 offboarding + A.8.31 environment separation
- A.8.5 → A.5.17 + A.5.25/A.5.26 (incident detection from auth anomalies)
- A.8.6 → A.5.30 (RPO/RTO sizing); A.8.32 (capacity expansion change)
- A.8.7 → A.5.25/A.5.26 (incident handoff); A.6.3 (awareness)
- A.8.8 → A.5.7 (threat intel) + A.5.9 (asset coverage)
- A.8.9 → A.5.19 (vendor-managed delegated); A.8.32 (baseline changes)
- A.8.10 → A.5.33 retention + A.5.34 PII (GDPR Art.17 erasure path MUST)
- A.8.11 → A.5.34 + A.5.12 + A.8.31 + A.8.33
- A.8.13 → A.8.24 (encryption); A.5.30 (RPO alignment); A.5.19 (vendor)
- A.8.15 → A.8.17 (time-sync) + A.8.16 (analysis integration)
- A.8.16 → A.5.7 + A.5.25/A.5.26; MITRE ATT&CK use-case mapping
- A.8.20 → A.8.22 (zones) + A.8.32 (change control)
- A.8.21 → A.5.19/A.5.20/A.5.22 (supplier-managed services)
- A.8.24 → A.5.34 (PII) + GDPR Art.32 + Art.5.1.f (via SPEC_ART_32)
- A.8.25 → A.5.8 (project security) + A.8.26/A.8.27/A.8.28/A.8.29/A.8.30/A.8.31
- A.8.30 → A.5.19/A.5.20 (supplier) + A.5.22 (supplier review) + A.6.5
- A.8.31 → A.8.11 (masking) + A.8.33 (test info) + A.8.32 (promotion)
- A.8.32 → A.5.26 (change-induced incident); A.8.8 (vuln-driven change)

**Three insights from the 33-pack:**

1. **33-control batches work end-to-end** with the disconnect risk
   mitigated by methodical Edit-per-control, lots of intermediate
   verification, and aggressive task tracking. ~3,300 lines of new
   curation code shipped in one commit. Per-control Edit is safer
   than mega-replace; total runtime ~2hr of focused editing.

2. **Loader orphan-cleanup gap**: id-rename promotions leave orphan
   EvidenceRequirement nodes. Manifested as engine "0/5 children
   satisfied" instead of "0/4" for renamed controls. Manual Cypher
   cleanup resolved this batch; loader fix tracked as follow-up.

3. **Tombstone consolidation pattern proven at scale.** Pre-existing
   single-leaf entries scattered in non-numeric positions consolidate
   cleanly via stub-comment + new 4-leaf in consolidated block.
   Item-id preservation only needs surgical attention for SPEC-
   referenced controls (3 of 3 here). Sub-pattern locked in for any
   future bulk-consolidation work.

**Where this leaves the curation arc (post batch 23):**
- **A.5** — fully multi-leaf at Style v2 (37/37)
- **A.6** — fully multi-leaf (8/8)
- **A.7** — fully multi-leaf (14/14)
- **A.8** — fully multi-leaf (34/34) ← closed by this batch
- **All of Annex A multi-leaf complete: 93/93 controls.**
- **GDPR** — mixed: ~4 already multi-leaf (Art.15/Art.28/Art.30 +
  derived articles); rest mixed. ~10-15 articles remaining.
- **Clauses 4-10** — single-leaf placeholders from Phase B initial draft;
  promotion not yet started.

Phase B program is now ~85-90% complete. Remaining work:
- GDPR remaining articles (~10-15 controls)
- ISO 27001 Clauses 4-10 if user wants management-system depth
  (clauses are conceptually different from Annex A; may stay single-leaf)
- Style v2 alignment for any remaining calibration-era multi-leafs
  (Art.15, Art.28, Art.30 — check if needed)

The Annex A organisational + people + physical + technological
control families are now ALL fully multi-leaf at Style v2.
