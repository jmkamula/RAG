---
name: curation-phase-b-batch-27-2026-06-02
description: "Phase B batch 27 — FIRST GDPR BATCH. Chapter II Principles 5-pack (Art.6 + Art.7 + Art.8 + Art.9 + Art.10). Mix of DerivedSpec expansion (Art.6: 3→6 children) and new EvidenceRequirement-based 4-leaf specs (Art.7/8/9/10). Profile_fact triggering pattern established for Art.8/9/10."
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 27 — FIRST GDPR BATCH after ISO 27001 fully closed. GDPR
Chapter II Principles 5-pack. 16 new evidence requirements (4 new
direct-evidence leaves on Art.6 DerivedSpec + 16 on Art.7-10 — well,
12 NEW since Art.6's direct evidence count went from 1 to 4 → +3 new
leaves on Art.6, plus 4 fresh 4-leaf specs for Art.7-10 = +19 new
evidence requirements total).

**Why:** User chose "By chapter, 4 batches" plan for GDPR after ISO
27001 closed in batch 26. Batch 27 = Ch II Principles + Lawfulness
(Art.6 already partly curated, Art.7/8/9/10 uncurated). Subsequent
batches: 28 = Ch III Rights (~10 articles), 29 = Ch IV Controller +
Processor (~15), 30 = Ch V Transfers (~6).

**How to apply:** GDPR has two structural shapes vs ISO:
1. **DerivedSpec articles**: Art.5.x family, Art.24, Art.25, Art.32
   (and now also Art.6, Art.16, Art.17 from earlier). These derive
   from ISO controls + may have direct_evidence leaves. To "promote"
   a DerivedSpec to deeper coverage, ADD more direct_evidence leaves
   inline within the DerivedSpec definition — NOT a separate
   EvidenceRequirement registered in ALL_EVIDENCE_REQUIREMENTS.
2. **Direct-evidence articles**: Art.13/15/28/30/33 (curated single-
   leaf or multi-leaf) and Art.7/8/9/10 (NEW 4-leaf specs in this
   batch). These are standard EvidenceRequirement-based — same
   pattern as ISMS clauses.

For Art.6 specifically: it was a DerivedSpec with 2 ISO deps + 1
direct evidence (lawful_basis_register). Promotion added 3 more
direct_evidence leaves inline within SPEC_ART_6.direct_evidence —
the engine now reports "0/6 children satisfied" (2 deps + 4 direct).
Primary-leaf id preserved (req:Art.6:lawful_basis_register + all
item:Art.6:* ids unchanged).

For Art.7-10 (new specs): standard EvidenceRequirement 4-leaf,
registered in ALL_EVIDENCE_REQUIREMENTS like any ISMS clause.
trigger_type field is the gating layer — Art.7 is universal, Art.8/
9/10 are profile_fact.

**Shipped (commit pending — current session 2026-06-02):**
- Art.6 (DerivedSpec expanded): added 3 direct_evidence ERs to
  SPEC_ART_6:
  - req:Art.6:lawful_basis_register (primary, id preserved; 6 MUSTs)
  - req:Art.6:lawful_basis_determination_procedure (4 MUSTs;
    documents HOW the lawful basis is chosen — addresses the
    "default to consent" failure mode)
  - req:Art.6:applicable_activities_scope (3 MUSTs; Art.30 RoPA
    cross-reference + Art.9 special-category overlay rule +
    Member State law)
  - req:Art.6:lawful_basis_program_review (5 MUSTs, freshness=365)
  - 6 children total in engine view (2 ISO deps + 4 direct)

- Art.7 (NEW op_process 4-leaf, universal): consent_procedure +
  consent_register (freshness=365) + applicable_activities_scope +
  program_review. Withdrawal mechanism + demonstrability MUSTs
  enforce the Art.7 standards (often the weakest spots in real
  implementations).

- Art.8 (NEW op_process 4-leaf, profile_fact): child_consent_procedure
  + child_consent_register (freshness=365) + applicable_services_scope
  + program_review. Member State age threshold variations MUST in
  scope leaf (16 default, some MS lower to 13/14/15).

- Art.9 (NEW op_process 4-leaf, profile_fact): authorisation_procedure
  + processing_register (freshness=365) + applicable_categories_scope
  + program_review. Each register row cites the Art.9.2 condition
  (a-j) being relied on + Art.9.3 safeguards.

- Art.10 (NEW op_process 4-leaf, profile_fact): authorisation_procedure
  + processing_register (freshness=365) + applicable_legal_basis_scope
  + program_review. Member State law citation per activity (Art.10
  requires either official authority OR specific MS authorisation).

- All 5 engine verdicts surfaced in Stage-2:
  - Art.6: 0/6 children
  - Art.7: 0/4 children (live OFI)
  - Art.8: 0/4 children (live N/A — engine NC ≠ N/A, surfaces)
  - Art.9: 0/4 children (live N/A — surfaces)
  - Art.10: 0/4 children (live N/A — surfaces)

- 5 eval cases added (158-162), all PASS expected.

**Item-id preservation:**
Critical for Art.6 — the existing item:Art.6:* ids are referenced
nowhere else (no scope_items or direct_evidence cross-refs in other
DerivedSpecs), BUT they are referenced via the lawful_basis_register
filename pattern + the existing privacy-policy ChromaDB indexing.
All preserved. Art.7-10 are new specs, no preservation concern.

**Posture-seed (extending the batch-24/25/26 pattern to GDPR):**
- Art.6: had an active OFI row already → updated description, kept OFI.
- Art.7: had an inactive 'Not assessed' row → updated to OFI active.
- Art.8/9/10: had inactive 'Not assessed' rows → updated to **N/A**
  active. Arion is B2B, no minors / no special-category / no
  criminal data — N/A is the honest posture, distinct from the
  ISMS-clauses pattern where everything was OFI.

The N/A live posture demonstrates a new pattern for profile_fact
GDPR articles: when a tenant's narrative explicitly excludes the
profile fact (Arion is "B2B, no minors"), live posture should be N/A.
Engine still proposes NC because the spec exists and is empty — but
the reviewer can confidently reject the engine proposal (or accept
to flip to NC). The surface acts as a "did you really mean N/A?"
checkpoint without forcing the answer.

**Spine variant mix:**
- 5×op_process (procedure-as-primary for Art.7-10, expanded direct
  evidence on the existing DerivedSpec for Art.6)

Conceptually all five are "operational compliance with a specific
GDPR article" — op_process fits uniformly. Records_program would
fit Art.7's consent register as primary, but the procedure (capture
mechanism + withdrawal mechanism + demonstrability) is the upstream
that produces the register correctly, so procedure-as-primary is
right here.

**Cross-article link web:**
- Art.6 ↔ Art.30 RoPA (every activity needs a basis; basis register
  cross-references RoPA)
- Art.6 → Art.7 (consent-based activities link to consent register)
- Art.6 → Art.13 (basis must be communicated in privacy notice)
- Art.7 → Art.6 (consent register is the supporting evidence for
  consent-based Art.6 entries)
- Art.7 → Art.8 overlay (when service may attract minors)
- Art.9 → Art.6 (Art.9.2 condition is IN ADDITION TO Art.6 basis, not
  instead of)
- Art.9 → Art.35 DPIA (Art.9 processing usually triggers DPIA)
- Art.10 → Art.35 DPIA (Art.10 processing usually triggers DPIA)

**Three insights from the first GDPR batch:**

1. **DerivedSpec promotion is structurally different from EvidenceRequirement
   promotion.** The ISMS clauses promoted by adding sibling REQs to
   ALL_EVIDENCE_REQUIREMENTS. DerivedSpecs expand by adding more entries
   to SPEC_*.direct_evidence inline. The engine treats both deps AND
   direct_evidence as children of the same DerivedSpec for verdict
   computation. Format: "0/N children satisfied" where N = deps + direct.

2. **profile_fact + live N/A is a clean GDPR pattern.** Arion legitimately
   doesn't process minors / special-category / criminal data. The N/A
   live finding accurately reflects this. The engine proposes NC anyway
   (no evidence = no satisfaction), surfacing as "did you really mean
   N/A? engine sees a curated spec with no evidence." This is the
   right product surface — the user owns the N/A decision and can
   reject with rationale, the engine surfaces the question without
   forcing the answer.

3. **GDPR has way more cross-article references than ISMS clauses had.**
   Art.6 references Art.30 + Art.7 + Art.13 + Art.9. Art.7 references
   Art.6 + Art.8. Art.9 references Art.6 + Art.35. Each spec needs
   explicit cross-references in scope leaves or MUSTs. The compact-style
   from batches 22-23 (5-7 MUSTs per leaf, 1-2 SHOULDs) still works but
   the cross-references multiply quickly. Watch for this in later GDPR
   batches.

**Where this leaves the curation arc (post batch 27):**
- ISO 27001: fully closed (118/118)
- GDPR Chapter II Principles: 5/5 compliance-relevant articles
  promoted to 4-leaf (Art.5.x family already DerivedSpec; Art.6 + 7/
  8/9/10 done in this batch). Chapter II effectively closed.
- GDPR remaining: Ch III (Art.12-23 rights — 10 articles), Ch IV
  (Art.24-43 controller/processor — 15 articles), Ch V (Art.44-49
  transfers — 6 articles). ~31 articles for batches 28-30.

**Next batch (batch 28 — GDPR Chapter III Data Subject Rights):**
~10 articles: Art.12 transparency, Art.13 promote, Art.14 new, Art.15
already 4-leaf (skip), Art.16 promote, Art.17 promote, Art.18 new,
Art.19 new, Art.20 new, Art.21 new, Art.22 new, Art.23 new. Most are
op_process (rights-handling procedures). Art.13/14 (privacy notices)
likely policy_program. Art.16/17 already DerivedSpec — extend with
direct_evidence (mirror Art.6 pattern).

See also: [[curation-phase-b-batch-26-2026-06-02]] (ISO 27001 fully
closed), [[curation-program-full-multi-leaf]] (program decision),
[[engine-agreement-suppression]] (NC==NC suppression specifically).
