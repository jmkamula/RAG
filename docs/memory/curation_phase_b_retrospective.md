---
name: curation-phase-b-retrospective
description: Phase B curation arc retrospective. 24 batches over 2026-05-26→2026-06-02. ISO 27001 + GDPR fully multi-leaf at Style v2. 617 ERs + 15 DerivedSpecs + 198 eval cases. Full writeup in docs/curation_phase_b_retrospective.md.
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B curation arc complete 2026-06-02. Full retrospective at
`docs/curation_phase_b_retrospective.md` (versioned with the repo).

**Why:** User asked for a retrospective writeup after batch 30 (final
batch) shipped. The arc shape, patterns proven, problems fixed, and
open follow-ups deserve a single coherent doc rather than living
scattered across 24 batch memos.

**How to apply:** When future conversations reference "Phase B", "the
curation arc", "Style v2 promotion program", or ask "what worked when
we promoted X to multi-leaf?", the retrospective is the canonical
answer. Specific batch memos (`curation_phase_b_batch_*.md`) carry
per-batch detail; the retrospective carries the arc-level view.

**Key facts captured in the retrospective:**
- 24 batches shipped (numbered 1-30 with calibration interleaving for
  alignments like batches 7 + 20)
- Started 2026-05-26 with case #1 (A.5.18 OG NC) → curation program
  expanded; first multi-control batch 2026-05-29 (records-family)
- Closed 2026-06-02 with batch 30 (GDPR Ch V Transfers)
- Final state: 617 ERs + 15 DerivedSpecs + 198 eval cases
- Patterns proven: 4-leaf spine (op_process / policy_program /
  records_program), DerivedSpec expansion, profile_fact + N/A,
  primary-id preservation, fast-data/slow-meta freshness
- Bugs fixed mid-arc: loader orphan EvidenceRequirement pruning
  (batch 23), `_CONTROL_RE` regex for 10.x (batch 26)
- Active follow-ups: ChromaDB re-indexing, posture-seed automation,
  per-leaf eval coverage, stochastic eval handling for #2/#3/#24,
  faster-data/slower-meta retrofit
- Deferred to Phase C: cross-framework (HIPAA/NIS2/DORA), tenant-
  specific MUST overlays, curation document templates

**Three carry-forward insights:**
1. The shape of compliance is more uniform than expected — 4-leaf
   universal spine + 3 spine variants + DerivedSpec covers everything.
2. profile_fact + N/A is the right product surface for "voluntary or
   conditional" obligations — most tenants resolve a meaningful
   fraction of GDPR to N/A; documented N/A is stronger than silence.
3. Fast-data/slow-meta freshness pattern emerged organically (9.1
   measurement_record 90d + procedure_review 365d) and should be
   retrofitted to existing specs with signal-velocity differential
   (Art.30 RoPA candidate).

See also: [[curation-program-full-multi-leaf]] (program decision
2026-05-26 that set this arc in motion), [[curation-phase-b-batch-30
-2026-06-02]] (final batch), individual batch memos for per-batch
detail.
