---
name: curation-phase-c-batch-1-2026-06-02
description: Phase C batch 1 — first batch after Phase B retrospective declared the arc complete. Art.15 (DSAR) + A.5.26 (incident response) Style v2 alignment; Stage-2 mass-approval of all Phase B engine proposals in same session; new audit_derived_spec_refs.py script
metadata: 
  node_type: memory
  type: project
  originSessionId: ee9d5de5-a7ef-486c-bc75-9bb38cbe6229
---

Phase C batch 1 shipped 2026-06-02, committed `33e0668` on 2026-06-03.
First batch after the Phase B retrospective
([[curation-phase-b-retrospective]]) closed out the curation arc. Two
distinct things bundled into the same session.

**Why:** Phase B retrospective flagged Art.15 + A.5.26 as Deferred —
both were 4-leaf already but pre-dated the A.5.16-family modern
conventions (fast-data register freshness, structured SLA-met flags,
bidirectional pair MUSTs). Same Stage-2 review session — the user
mass-approved every pending engine NC proposal on Arion (~45 controls
queued from Phase B); eval suite needed to reflect post-approval state.

**How to apply:** Phase C is for alignment + cross-framework expansion,
not multi-leaf promotion (Phase B closed that work). When a future
batch touches a Phase-B-era spec, check whether it predates the modern
conventions and align freshness + SLA-met + pair-MUST patterns first.

**Two alignments (NOT promotions — both controls were already 4-leaf):**

1. **Art.15 DSAR** — register freshness 180d (high-volume, no prior
   freshness), new `item:Art.15:sla_met` MUST on response leaf
   (boolean against Art.12.3 1-month clock), `proc_identity_pair_30`
   MUST + `rev_identity_pair_30` MUST on procedure+review enforce
   bidirectional Art.15↔Art.30 RoPA coherence. 2 SHOULD→MUST
   promotions (`identity_check`, `proc_inventory_link`). All 31
   existing item-ids preserved.

2. **A.5.26 incident response** — register freshness 90d (fast-data,
   matches A.5.24/A.5.25/A.5.27 incident-family), new
   `gdpr_72h_trigger_check` MUST on procedure (cross-control to
   `req:Art.33:breach_notification`), new `severity_tier_matrix`
   MUST + `rev_72h_feasibility` MUST on review (parity with
   `A.5.24:rev_gdpr_72h_feasibility`), new
   `rev_identity_pair_25` MUST closes A.5.25→A.5.26 handoff gap. 1
   SHOULD→MUST promotion (`authority_contacts`). All 22 existing
   item-ids preserved.

**Stage-2 mass-approval lock-in:**
User approved every pending Phase B engine proposal in same session
(~45 controls). Eval suite mass-flipped `must_contain` from
`"engine proposes 'NC' 0/N children satisfied"` →
`"already approved 'NC'"`. One A.5.30 posture-discipline case
(case 75-style flip) Comply→NC because the engine NC was approved,
making it the new live finding. Dup-label forbids relaxed for A.5.30
"is NC" / "[NC]" — those are now CORRECT labels, not bugs.

**New audit script — `scripts/audit_derived_spec_refs.py`:**
Generalizes the DerivedSpec item-id preservation pattern from
[[curation-phase-b-batch-18-2026-06-01]] (A.5.34 two-way preservation).
Walks every DerivedSpec and reports which control's items are cited
via `DerivedFrom.scope_items`. Usage:
```
python3 scripts/audit_derived_spec_refs.py A.5.26
python3 scripts/audit_derived_spec_refs.py Art.15 Art.30
python3 scripts/audit_derived_spec_refs.py --all
```
Use BEFORE any control alignment/promotion to spot item-ids the
DerivedSpecs cite (rename or removal silently breaks derivations at
load time). Caught zero issues on Art.15 + A.5.26 this batch (Art.15
not referenced by any DerivedSpec; A.5.26 likewise — both are
operational leaf-side controls, not foundational items GDPR derives
from).

**Eval result (v5, 2026-06-02): 197/198 PASS — clean upper bound.**
Only #25 (Art.5 anti-hallucination) failed (known-stale since
2026-05-27). #24 PASSed this run (stochastic, usually fails).

**Style v2 alignment pattern (now three exemplars):**
- Batch 7 (A.5.1) — earliest single-leaf-era spec
- Batch 20 (A.5.18) — original Phase B promotion before conventions matured
- Phase C batch 1 (Art.15 + A.5.26) — first cross-framework alignment

All three share: keep all existing item-ids, add new MUSTs (don't
demote existing ones), add `freshness_days` where missing, add
SLA-met / pair-MUST where the family expects them.

**Carry-forward for Phase C:**
- More A.5.16-family alignments likely (any 4-leaf op_process spec
  without freshness on register, without SLA-met where there's a
  clock, without pair-MUST where there's a natural sibling control)
- Cross-framework expansion (HIPAA / NIS2 / DORA per retrospective)
- Tenant-specific MUST overlays still deferred
- ChromaDB re-indexing still pending from Phase B

See also: [[curation-phase-b-retrospective]] (arc-level view),
[[curation-program-full-multi-leaf]] (program decision),
[[curation-phase-b-batch-18-2026-06-01]] (DerivedSpec preservation
precedent that the new audit script generalizes).
