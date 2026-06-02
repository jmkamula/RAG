---
name: curation-phase-b-batch-28-2026-06-02
description: "Phase B batch 28 — GDPR Chapter III Data Subject Rights 11-pack. Largest GDPR batch. 2 promotions (Art.13 single-leaf → policy_program 4-leaf; Art.6-mirror-style DerivedSpec expansions for Art.16/17) + 9 new specs (Art.12/14/18/19/20/21/22/23 + Art.14). Spine mix: 2×policy_program + 7×op_process + 2×DerivedSpec expansion."
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 28 — GDPR Chapter III Data Subject Rights 11-pack. Largest
GDPR batch and one of the largest batches overall. 38 new evidence
requirements (35 in ALL_EVIDENCE_REQUIREMENTS + 6 in DerivedSpec
direct_evidence inline for Art.16/17 — actually 35 ER list + 3 + 3 = 41
total leaves new; with 3 preserved primary leaves on the promotions
(Art.13, Art.16, Art.17), 38 are net-new).

**Why:** User chose "By chapter, 4 batches" plan; this is batch 2 of 4
(after batch 27 closed Ch II Principles). Ch III covers data subject
rights end-to-end — the highest-tenant-touch surface of GDPR.

**How to apply:** Three patterns in one batch:
1. **EvidenceRequirement-based promotion**: Art.13 single-leaf →
   policy_program 4-leaf. Add 3 sibling REQs in source after the
   primary; register in ALL_EVIDENCE_REQUIREMENTS. Primary id
   preserved.
2. **DerivedSpec expansion** (Art.16 + Art.17): add 3 more direct_evidence
   ERs inline within SPEC_ART_16.direct_evidence / SPEC_ART_17.direct_evidence.
   NOT registered in ALL_EVIDENCE_REQUIREMENTS (DerivedSpec direct_evidence
   flows through ALL_DERIVED_SPECS). Engine reports total = deps + direct.
3. **New EvidenceRequirement 4-leaf specs** (Art.12/14/18/19/20/21/22/23):
   standard op_process or policy_program, registered in
   ALL_EVIDENCE_REQUIREMENTS like ISMS clauses.

**Shipped (commit pending — current session 2026-06-02):**

PROMOTIONS:
- Art.13 (privacy notice direct collection) → policy_program 4-leaf.
  Primary leaf id preserved (req:Art.13:privacy_notice + all item:Art.13:*).
  Siblings: publication_record + applicable_collection_points_scope +
  program_review (365d). 4 children.

EXPANSIONS (DerivedSpec):
- Art.16 (rectification): SPEC_ART_16 now 1 ISO dep + 4 direct = 5 children.
  Direct evidence: rectification_procedure (primary, id preserved) +
  rectification_register + applicable_systems_scope + program_review.
- Art.17 (erasure): SPEC_ART_17 now 2 ISO deps + 4 direct = 6 children.
  Direct evidence: erasure_procedure (primary, id preserved) +
  erasure_register + applicable_systems_scope + program_review.

NEW SPECS:
- Art.12 (Transparency / rights modalities) — op_process 4-leaf. Umbrella
  above Art.13-22. Encodes Art.12.3 one-month SLA at MUST level. 4 children.
- Art.14 (privacy notice indirect collection) — policy_program 4-leaf
  (mirror Art.13 with Art.14-specific additions: Art.14.1d categories,
  Art.14.2f source, Art.14.3 deadline, Art.14.5 exceptions). 4 children.
- Art.18 (restriction) — op_process 4-leaf. Art.18.1 four grounds (a-d)
  catalogued in scope leaf; Art.18.2 'storage-only' exceptions enforced.
  4 children.
- Art.19 (recipient notification) — op_process 4-leaf. Triggered by
  Art.16/17/18 events. Impossibility/disproportionality exception
  explicitly captured. 4 children.
- Art.20 (portability) — op_process 4-leaf. Applicability check
  (consent/contract basis AND automated) MUST; EDPB WP242 'provided
  by' interpretation in scope leaf. 4 children.
- Art.21 (objection) — op_process 4-leaf. Splits direct-marketing
  absolute (Art.21.2-3) vs legitimate-interests balancing (Art.21.1).
  Art.21.4 explicit-notice MUST enforced. 4 children.
- Art.22 (automated decisions) — op_process 4-leaf, profile_fact
  (org engages in solely-automated decisions with legal/significant
  effects). Art.22.3 three safeguards all MUSTs (human intervention,
  contest, expression of view). Art.22.4 special-category overlay.
  4 children.
- Art.23 (Member State restrictions) — op_process 4-leaf, profile_fact
  (MS law specifically restricts Art.12-22/34 rights). Art.23.1 a-j
  purposes catalogued; Art.23.2 a-h safeguards enforced. 4 children.

POSTURE SEED:
- Art.12/13/14/16/17/18/19/20/21: OFI (Arion has some flows informally —
  privacy policy on website, support handles ad-hoc rights requests,
  marketing-opt-out via unsubscribe — but no formal procedures /
  registers / SLA tracking).
- Art.22 + Art.23: N/A (no automated decisions; not in regulated
  sector with MS restrictions).

EVAL CASES ADDED (163-173): 11 cases, all probing engine verdicts:
- Art.12/13/14/18/19/20/21/22/23 — `0/4 children satisfied`
- Art.16 — `0/5 children satisfied` (1 dep + 4 direct)
- Art.17 — `0/6 children satisfied` (2 deps + 4 direct)

**Item-id preservation:**
- req:Art.13:privacy_notice + all item:Art.13:* preserved (Art.13
  was the single-leaf REQ_PRIVACY_NOTICE_DIRECT since 2026-05-22).
- req:Art.16:rectification_procedure + all item:Art.16:* preserved
  (Art.16 DerivedSpec direct evidence original id and items kept).
- req:Art.17:erasure_procedure + all item:Art.17:* preserved
  (Art.17 DerivedSpec direct evidence original id and items kept).
- New specs (Art.12/14/18/19/20/21/22/23) have no preservation
  concern — fresh specs, no external references.

**Cross-article link web (GDPR Ch III is densely interconnected):**
- Art.12 → Art.13-22 (modalities umbrella)
- Art.13 ↔ Art.6 + Art.30 (notice content includes lawful basis +
  RoPA-derived recipients)
- Art.14 → Art.13 (mirror structure; Art.14.5 exception layer)
- Art.16 → Art.12 + Art.19 + A.5.34 + Art.30 (rectification handler
  + recipient notification + PII inventory + RoPA-derived systems)
- Art.17 → Art.12 + Art.19 + A.5.34 + A.8.10 + Art.30 (erasure handler
  + recipient notification + PII inventory + deletion mechanism + RoPA)
- Art.18 → Art.12 + Art.19 (restriction handler + recipient notification)
- Art.19 → Art.16 + Art.17 + Art.18 (consumes events from all three)
- Art.20 → Art.6 + Art.30 (basis check + RoPA derivation)
- Art.21 → Art.6 + Art.30 + Art.12 (basis subset + RoPA + objection
  intake handler)
- Art.22 → Art.35 DPIA + Art.9 (DPIA trigger + special-category overlay)
- Art.23 → Art.12-22 (umbrella restriction)

**Three insights from the largest GDPR batch:**

1. **DerivedSpec + EvidenceRequirement expansion patterns are now
   crisp.** Art.6 (batch 27), Art.16, Art.17 (batch 28) all promoted
   via "add direct_evidence ERs inline within SPEC_*.direct_evidence,
   primary leaf id preserved". This pattern will apply uniformly to
   future GDPR DerivedSpec expansions (Art.24, Art.25, Art.32).

2. **Art.12 is the umbrella spec.** Art.12-22 individually capture
   per-right mechanics, but Art.12 captures the rights-portal layer
   that all of them flow through. Rights_request_register at Art.12
   is the centralised log; per-right registers (Art.16/17/18/20/21)
   reference Art.12 register entries. This mirrors ISO's 8.1 / 9.3 /
   10.2 umbrella patterns (top-level procedure that subordinate clauses
   feed into).

3. **profile_fact + N/A live posture works well as a 'did-you-really-
   mean-N/A?' surface.** Art.22 (automated decisions) and Art.23 (MS
   restrictions) are NEVER applicable for many tenants. Setting live
   N/A + curated spec produces an engine NC verdict that surfaces in
   Stage-2 — the reviewer affirmatively rejects the engine proposal
   (defending the N/A) rather than silently ignoring it. This is the
   strongest defensibility position: 'we considered Art.22 and
   determined it doesn't apply' is documented, not assumed.

**Where this leaves the curation arc (post batch 28):**
- ISO 27001: fully closed (118/118)
- GDPR Ch II (Principles): closed in batch 27 (5/5 compliance-relevant)
- GDPR Ch III (Rights): closed in this batch (Art.12+13+14+15+16+17+
  18+19+20+21+22+23 = 12/12; Art.15 already 4-leaf from earlier
  calibration, others done across batches 27-28)
- GDPR Ch IV (Controller/Processor): ~15 articles remaining for
  batch 29 (Art.24-43 — Art.24/25/28/30/32/33 already partly
  curated; Art.26/27/29/31/34/35/36/37/38/39/40-43 mostly new)
- GDPR Ch V (Transfers): ~6 articles for batch 30 (Art.44-49)

**Next batch (batch 29 — GDPR Chapter IV Controller and Processor):**
~15 articles split:
- Already curated (will need expansion / promotion):
  - Art.24 (accountability) — DerivedSpec, 6 deps, 0 direct. Expand
    direct_evidence to 4 leaves.
  - Art.25 (Privacy by Design) — DerivedSpec, 6 deps, 1 direct. Expand
    direct_evidence to 4.
  - Art.28 (DPA) — single-leaf. Promote policy_program 4-leaf.
  - Art.32 (security) — DerivedSpec, 5 deps, 1 direct. Expand to 4
    direct evidence.
  - Art.33 (breach notification to authority) — single-leaf. Promote.
- New (need 4-leaf specs):
  - Art.26 (joint controllers)
  - Art.27 (representative)
  - Art.29 (processor under controller authority)
  - Art.31 (cooperation with supervisory authority)
  - Art.34 (breach communication to subjects)
  - Art.35 (DPIA)
  - Art.36 (prior consultation)
  - Art.37 (DPO designation)
  - Art.38 (DPO position)
  - Art.39 (DPO tasks)
  - Art.40-43 (codes + certification — often N/A for most orgs;
    consider grouping or skipping certification-only flows)

~15-19 articles is a big batch — may need splitting into 29a + 29b
when the time comes.

See also: [[curation-phase-b-batch-27-2026-06-02]] (Ch II Principles —
established DerivedSpec expansion + profile_fact-+-N/A patterns),
[[curation-phase-b-batch-26-2026-06-02]] (ISO 27001 fully closed),
[[engine-agreement-suppression]] (NC==NC suppression).
