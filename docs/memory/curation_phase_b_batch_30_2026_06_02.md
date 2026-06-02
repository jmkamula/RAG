---
name: curation-phase-b-batch-30-2026-06-02
description: Phase B batch 30 — GDPR Chapter V Transfers 6-pack — FINAL BATCH OF THE CURATION ARC. Art.44-49 international transfers. Closes GDPR. Phase B curation arc complete — ISO 27001 + GDPR fully multi-leaf at Style v2.
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 30 — FINAL BATCH OF THE CURATION ARC. GDPR Chapter V
International Transfers — Art.44 + Art.45 + Art.46 + Art.47 + Art.48 +
Art.49. 6 new op_process 4-leaf specs. 24 new evidence requirements.

**Why:** User said "ready" after batch 29b closed GDPR Ch IV. Ch V is
the last unfinished chapter — transfers (international flows of personal
data outside EU/EEA). After this batch lands, the Phase B curation arc
(started 2026-05-26 with A.5.18) is COMPLETE.

**How to apply:** Same pattern as batch 29b — uniform spine (all 6
op_process 4-leaf). No promotions, no DerivedSpec expansions, no spine
variation. Just 6 fresh standard specs.

Transfer mechanism hierarchy encoded in procedure MUSTs:
- Art.44 (umbrella) — any transfer outside EU/EEA triggers chapter
- Art.45 (adequacy) — preferred when destination covered by Commission
  decision
- Art.46 (safeguards) — most common; SCCs are the workhorse
- Art.47 (BCRs) — intra-group, requires lead SA approval
- Art.48 (foreign authority) — defensive: refuse non-treaty-based
  requests
- Art.49 (derogations) — last resort, EDPB-strict construction

**Shipped (commit pending — current session 2026-06-02):**

- Art.44 (general principle, universal): transfer_procedure + transfer_
  register + applicable_scope + program_review. EDPB 05/2021 three-
  criteria transfer definition + Schrems II TIA in MUSTs.

- Art.45 (adequacy, profile_fact): adequacy_procedure + adequacy_register
  + applicable_scope + program_review. Partial-adequacy handling (US-DPF
  recipient-eligibility check) + Schrems-invalidation watch + Art.46
  fallback readiness.

- Art.46 (appropriate safeguards, profile_fact): safeguards_procedure +
  safeguards_register + applicable_scope + program_review. 2021/914 SCCs
  modules (1-4) + TIA per Schrems II + supplementary measures per EDPB
  01/2020 + enforceable rights verification.

- Art.47 (BCRs, profile_fact): bcr_procedure + bcr_register + applicable_
  scope + program_review. Art.47.2 a-n content checklist + Art.47.2.i
  complaint handling.

- Art.48 (foreign authority disclosures, universal): foreign_authority_
  procedure + foreign_request_register + applicable_scope + program_review.
  International agreement check + Art.49 derogation overlay + refusal
  path. Tabletop test required even when register has zero rows.

- Art.49 (derogations, profile_fact): derogations_procedure + invocation_
  register + applicable_scope + program_review. Art.49.1 a-g catalog +
  EDPB 2/2018 strict construction + non-repetitive constraint for
  second-paragraph compelling-legitimate-interests route + SA notification.

POSTURE SEED:
- Art.44: OFI (Arion uses AWS/Azure US — transfers happen, register
  informal, no formal TIA)
- Art.45: OFI (some US-DPF certified providers, reliance not tracked)
- Art.46: OFI (2021/914 SCCs in major DPAs but no formal safeguards
  register + no per-transfer TIA + supplementary measures analysis)
- Art.47: N/A (not a multi-national group with EU-approved BCRs)
- Art.48: OFI (informal pathway in security playbook; never invoked;
  no formal procedure)
- Art.49: N/A (Art.46 SCCs cover all transfers; no derogations invoked)

ENGINE VERDICTS: all 6 propose NC 0/4 (engine NC ≠ live OFI / N/A).

EVAL CASES ADDED (193-198): 6 cases. Case 193 (Art.49) is the FINAL
eval case of the Phase B curation arc.

**Item-id preservation:** All 6 specs are new — no preservation concerns.

**Spine variant mix:** 6×op_process. Most uniform batch since 29b.

**Cross-article web:**
- Art.44 ↔ Art.45/46/47/48/49 (umbrella + mechanism selection)
- Art.45 → Art.46 fallback (when adequacy decision invalidated)
- Art.46 ↔ Art.30 (RoPA recipient column drives safeguard register)
- Art.46 → Schrems II → EDPB 01/2020 (supplementary measures)
- Art.47 → Art.63 consistency (lead SA cooperation for BCR approval)
- Art.48 → Art.49 (last-resort overlay when no international agreement)
- Art.49 → Art.46 (frequent invocation signals Art.46 should be used
  instead)

**Three insights from the final batch:**

1. **Defensive curation works for low-frequency obligations.** Art.48
   (foreign authority disclosures) and Art.49 (derogations) are
   articles most tenants will never invoke. But each needs a documented
   procedure that can be activated on short notice when challenged.
   The tabletop-test MUST in Art.48 review acknowledges this — the
   procedure is exercised against hypothetical scenarios, not just
   real-event activations.

2. **Transfer mechanism hierarchy is operationally meaningful.** GDPR's
   Art.44-49 form a clear preference order (adequacy → safeguards →
   derogations) that the curation encodes explicitly in Art.44's
   procedure MUST 'mechanism-selection decision tree'. This isn't just
   documentation neatness — it shapes how a tenant should choose between
   reliance on US-DPF (Art.45) vs SCCs (Art.46) when both are available
   (rule: prefer Art.45 because narrower legal exposure).

3. **The curation arc closes with the right shape.** All 6 GDPR Ch V
   articles ended up as op_process 4-leaf — same as Ch II/III/IV core.
   The Phase B program's bet on '4-leaf op_process/policy_program/
   records_program as the universal shape' has held across 200+ specs.
   The pattern's coverage of GDPR was non-obvious at batch 27 (would
   DerivedSpecs dominate? would profile_fact handling vary?) — it's now
   clear the same shape works for both ISO 27001 and GDPR end-to-end.

**Where this leaves the curation arc (post batch 30 — FINAL):**
- ISO 27001: FULLY CLOSED (118 controls/clauses multi-leaf at Style v2)
- GDPR: FULLY CLOSED across all chapters:
  - Ch I (Art.1-4): structural / definitions — explicit_empty by design
  - Ch II Principles (Art.5-11): closed (batch 27 + earlier DerivedSpecs)
  - Ch III Rights (Art.12-23): closed (batch 28)
  - Ch IV Controller/Processor (Art.24-43): closed (batches 29a + 29b)
  - Ch V Transfers (Art.44-49): closed (THIS BATCH)
  - Ch VI Independent SAs (Art.51-59): explicit_empty (institutional)
  - Ch VII Cooperation (Art.60-76): explicit_empty (institutional)
  - Ch VIII Remedies (Art.77-84): explicit_empty (institutional)
  - Ch IX Special situations (Art.85-91): explicit_empty (sector-specific)
  - Ch X Delegated acts (Art.92-93): explicit_empty (institutional)
  - Ch XI Final (Art.94-99): explicit_empty (transitional)

**Phase B curation arc total statistics:**
- 24 batches shipped (batch 1 records-family 2026-05-29 → batch 30 today)
- Across the arc: ~200 controls/articles brought from single-leaf or
  empty to multi-leaf Style v2
- ISO 27001: 118 controls (Annex A 93 + ISMS clauses 25)
- GDPR: ~50 compliance-relevant articles
- Total specs in ALL_EVIDENCE_REQUIREMENTS at close: 617
- Total DerivedSpecs at close: 15 (Art.5/5.1/5.1.a-f/5.2/6/16/17/24/25/32)
- Eval suite: 198 cases (started 2026-05-26 with case #1, the OG A.5.18 NC)

**What's NOT in scope of Phase B (potential future work):**
- ChromaDB re-indexing of the expanded ER set (engine works via Neo4j
  but vector search may not surface new MUSTs efficiently — see
  performance over time)
- Eval coverage for the DerivedSpec expansion patterns specifically
  (currently every batch-promoted DerivedSpec has 1 eval case probing
  Stage-2 verdict; no eval probes the per-leaf MUST checking yet)
- Phase C: cross-framework derivations beyond what already exists
  (e.g. HIPAA, NIS2, DORA mapping to ISO 27001 / GDPR base)
- Phase C: tenant-specific overrides (e.g. industry-specific MUSTs
  layered on top of the universal Style v2)

See also: [[curation-phase-b-batch-29b-2026-06-02]] (Ch IV close-out),
[[curation-phase-b-batch-1-2026-05-29]] (records-family batch — first
of the arc), [[curation-program-full-multi-leaf]] (program-level
decision that set this arc in motion 2026-05-26).
