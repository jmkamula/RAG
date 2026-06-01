---
name: curation-phase-b-batch-22-2026-06-01
description: Phase B batch 22 — A.7 Physical Controls 14-pack. LARGEST batch yet — 14 controls × 4 leaves = 56 new evidence requirements. Closes A.7 block. Eval 83/85 → 97/99 (all 14 new cases PASS).
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 22 — A.7 Physical Controls 14-pack bulk promotion. All
14 A.7.x controls promoted from single-leaf to 4-leaf. Closes the A.7
block. LARGEST batch yet by a wide margin (previous: batch 21 with 7
controls; batch 3 with 5 controls).

**Why:** User chose "A.7 Physical 14-pack" after batch 21 closed A.6.
Multi-control bulk batching pattern proven repeatedly (batches 1, 3,
4, 19, 21). The 14-control scale tests the pattern's upper bound.

**How to apply:** 14-control batches work. Key tactic at this scale:
**compact-style elaboration** — 5-7 MUSTs per leaf, 1-2 SHOULDs (vs
single-control batches with 8+ MUSTs per leaf, elaborate descriptions
with cross-references). Bulk-batch pragmatism: each control's spec is
complete and follows the spine pattern, but doesn't carry the same
depth of cross-control narrative that a focused single-control batch
allows. This is the right tradeoff at scale.

**Shipped (commit pending — current session 2026-06-01):**
- 56 leaves total (14 × 4-leaf):
  - A.7.1 perimeters (policy_program): policy + perimeter_register +
    applicable_sites_scope + program_review
  - A.7.2 entry (op_process): procedure + entry_event_register +
    applicable_areas_scope + program_review
  - A.7.3 offices/rooms (op_process): procedure + room_register +
    applicable_rooms_scope + program_review
  - A.7.4 monitoring (op_process): procedure + monitoring_event_register
    + monitoring_scope + program_review
  - A.7.5 environmental (op_process): procedure + threat_register +
    applicable_sites_scope + program_review
  - A.7.6 secure work (op_process): procedure + work_session_register
    + applicable_areas_scope + program_review
  - A.7.7 clear desk (policy_program): policy + audit_register +
    applicable_locations_scope + program_review
  - A.7.8 equipment siting (op_process): procedure + siting_register
    + applicable_equipment_scope + program_review
  - A.7.9 off-premises (policy_program): policy + off_premises_register
    + applicable_classes_scope + program_review
  - A.7.10 storage media (op_process): procedure + media_register +
    applicable_media_scope + program_review
  - A.7.11 utilities (op_process): procedure + utility_register +
    applicable_sites_scope + program_review
  - A.7.12 cabling (op_process): procedure + cabling_register +
    applicable_runs_scope + program_review
  - A.7.13 maintenance (op_process): procedure (freshness=365) +
    maintenance_event_register + applicable_equipment_scope +
    program_review
  - A.7.14 disposal (op_process with lifecycle-end): procedure +
    disposal_scope + disposal_record (per-equipment lifecycle-end) +
    program_review
- All 14 engine verdicts: NC 0/4 children satisfied. Live postures:
  8×N/A + 4×Comply + 2×missing-rows. All 14 surface in Stage-2
  (engine NC differs from live N/A and live Comply both).
- 14 eval cases added (86-99), all PASS on first run.
- Eval 83/85 → 97/99 (#24 + #25 known-stale fail, both non-blocking).

**Item-id preservation:**
NO DerivedSpec references to any A.7.x items. Only the 14 primary-
leaf ids need preservation — all preserved. Cleanest preservation
batch yet.

**Spine variant mix:**
- 11 op_process (procedure-as-primary)
- 3 policy_program (policy-as-primary: A.7.1 perimeters, A.7.7 clear
  desk, A.7.9 off-premises)
- 1 with lifecycle-end (A.7.14 disposal_record, parallel to A.5.28)

The 3:11 policy:procedure ratio reflects A.7's operational nature —
most physical security is procedural execution (entry, monitoring,
maintenance) with a few policy umbrellas (perimeters, clear desk,
off-premises).

**N/A live-posture handling (new insight):**
Many of Arion's A.7 controls are live-posture N/A (Arion is cloud-
only). The "pending engine verdict for A.7.X" query surfaces engine
NC 0/4 in Stage-2 for N/A controls too — verified via direct API
probe before adding eval cases. Engine NC ≠ live N/A → Stage-2
surfaces. This is the same surfacing logic as Comply → NC, just with
a different "live finding" string ("N/A" vs "Comply").

For tenants like Arion this means: engine surfaces a verdict suggesting
NC, reviewer can either accept the engine verdict (making it NC) OR
reject and keep N/A (with rationale). The reviewer-owns-posture
principle holds.

**Cross-control link web (compact-style):**
- A.7.1 → A.5.18 access rights (logical_integration MUST)
- A.7.2 → A.5.18 access reviews (periodic_review MUST)
- A.7.3 ↔ A.7.1 (room_register draws from perimeter_register)
- A.7.4 → A.5.26 SIEM (siem_integration MUST) + A.5.28 evidence
  (reg_evidence_link SHOULD)
- A.7.5 → A.5.27/A.5.29/A.5.30 BCP family (recovery MUST)
- A.7.6 → A.7.1 (secure_area_definition)
- A.7.7 → A.5.12 classification (locked_storage MUST) + A.6.7
  remote-work (home_office_overlay SHOULD)
- A.7.8 → A.5.9 asset register + A.7.3 rooms + A.7.12 cabling
- A.7.9 → A.6.7 remote-working + A.6.8 event reporting (theft/loss)
- A.7.10 → A.5.13 labelling + A.5.7.14 disposal (handoff)
- A.7.11 → A.5.29/A.5.30 BCP (bcp_integration MUST)
- A.7.12 (no major cross-control links — self-contained)
- A.7.13 → A.5.9 asset register
- A.7.14 → A.5.9 retired asset entries + A.5.28 evidence-disposal
  pattern (parallel lifecycle-end)

**Three insights from the largest batch:**

1. **Compact-style works at scale.** 5-7 MUSTs per leaf is sufficient
   for bulk batches. Single-control batches can afford 8-10+ MUSTs
   per leaf for depth; bulk batches need the discipline of compact
   shape. Validated by 14×4=56 leaves all loading, validating, and
   eval-passing first try.

2. **N/A live-posture surfaces in Stage-2.** Engine-agreement
   suppression is specifically NC==NC, not NC vs any other status.
   Engine NC against live N/A surfaces normally. New tenant-side UX
   pattern: "engine thinks NC, you said N/A — review?"

3. **Lifecycle-end variant works for physical disposal (A.7.14).**
   The op_process spine accommodates the disposal_record lifecycle-
   end naturally — same pattern as A.5.28 evidence handling. This
   confirms the lifecycle-end-as-fourth-leaf pattern is robust across
   both information-domain (A.5.28) and physical-domain (A.7.14)
   controls.

**Where this leaves the curation arc (post batch 22):**
- **A.5** — fully multi-leaf at Style v2 (37/37)
- **A.6** — fully multi-leaf (8/8)
- **A.7** — fully multi-leaf (14/14) ← closed by this batch
- **A.8** — mixed: 6 already multi-leaf (A.8.2/A.8.11/A.8.24/A.8.25/
  A.8.26/A.8.27); rest single-leaf
- **GDPR** — mixed: ~4 already multi-leaf (Art.15/Art.28/Art.30 +
  derived articles); rest mixed

Phase B program is now ~75-80% complete. Remaining work:
- A.8 mixed bulk (largest remaining ISO block)
- GDPR remaining articles
- A.8 alignment for the 6 calibration-era multi-leaf controls (Style
  v2 alignment pattern from batch 7 / batch 20)

A.8 is the largest remaining ISO block — possibly the next batch
candidate. Or a "Style v2 alignment for all calibration-era multi-
leaf controls" batch to bring the existing multi-leaf controls up
to modern conventions before adding more.
