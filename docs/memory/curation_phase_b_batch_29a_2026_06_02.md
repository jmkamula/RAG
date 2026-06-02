---
name: curation-phase-b-batch-29a-2026-06-02
description: Phase B batch 29a — GDPR Ch IV Controller and Processor 11-pack (core articles). 3 DerivedSpec expansions (Art.24 / Art.25 / Art.32) + 2 promotions (Art.28 / Art.33) + 6 new specs (Art.26 / Art.27 / Art.29 / Art.31 / Art.34 / Art.35). Sets up batch 29b for DPO + codes/certification (Art.36-43).
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 29a — GDPR Chapter IV (Controller and Processor) core
articles. 11 articles in this sub-batch; 8 more (Art.36-43) deferred to
batch 29b (DPIA prior consultation + DPO cluster + codes + certification).

**Why:** User split Ch IV into 29a (10-11 actively-tenant-facing
articles) + 29b (8 articles: Art.36-43 — DPO + codes + certification,
mostly profile_fact / often N/A). 29a covers the articles most tenants
will actively work on.

**How to apply:** Largest mix of structural patterns to date:
- 3 DerivedSpec expansions (Art.24/25/32) — direct_evidence added inline
- 2 promotions (Art.28/33) — single-leaf → 4-leaf
- 6 new specs (Art.26/27/29/31/34/35) — fresh EvidenceRequirement-based

Art.24 is the FIRST DerivedSpec to go from 0 direct_evidence to 4 in one
batch — engine reports `0/10 children satisfied` (6 ISO deps + 4 direct).
Largest verdict surface in any spec to date.

**Shipped (commit pending — current session 2026-06-02):**

DERIVEDSPEC EXPANSIONS:
- Art.24 (accountability): 6 ISO deps + 4 NEW direct (privacy_programme
  _charter + gdpr_compliance_register + controller_processor_decision_
  record + accountability_program_review). 10 children. The compliance
  register is the meta-tracker across all GDPR articles in scope.
- Art.25 (DPbD): 6 ISO deps + 1 existing direct (default_settings_record
  primary id preserved) + 3 new direct (dpbd_procedure + applicable_
  design_scope + program_review). 10 children. Art.25.3 certification
  reliance covered.
- Art.32 (security): 5 ISO deps + 1 existing direct (resilience_test_
  record primary id preserved) + 3 new direct (risk_appropriate_measures_
  register + applicable_scope_note + program_review). 9 children. New
  measures register is the per-activity proportionality argument.

PROMOTIONS:
- Art.28 (DPA): single-leaf → policy_program 4-leaf. Primary id preserved
  (req:Art.28:data_processing_agreement + all item:Art.28:*). Adds
  processor_register + applicable_processors_scope + program_review.
  Controller-vs-processor decision criteria in scope MUST. 4 children.
- Art.33 (breach to authority): single-leaf → op_process 4-leaf. Primary
  id preserved (req:Art.33:breach_notification + all item:Art.33:*).
  Primary leaf stays trigger_type=operational (fires per-breach);
  siblings universal. 72h SLA enforced in procedure; A.5.24 exercise
  integration in review. 4 children.

NEW SPECS:
- Art.26 (joint controllers) — op_process 4-leaf, profile_fact. Arrangement
  + register + scope + review. EDPB Guidelines 7/2020 controller-vs-
  processor-vs-joint test in scope MUST.
- Art.27 (representative) — op_process 4-leaf, profile_fact (non-EU
  controllers). Designation + operations record + applicable scope
  (Art.27.2 exception assessment) + review.
- Art.29 (processing under authority) — op_process 4-leaf, profile_fact.
  Instructions procedure + personnel authorisation register + applicable
  scope + review. Cross-links to A.6.3 / 7.3 training + Art.28 DPA flow.
- Art.31 (SA cooperation) — op_process 4-leaf, universal. Cooperation
  procedure + interaction register + scope (lead SA per Art.56) +
  review.
- Art.34 (breach to subject) — op_process 4-leaf, universal. Companion
  to Art.33 with different threshold (high risk only) + different audience
  (data subjects). Art.34.3 exceptions (encryption / mitigation /
  disproportionate effort) audited in review.
- Art.35 (DPIA) — op_process 4-leaf, profile_fact. Procedure + register
  + applicable scope (Art.35.3 mandatory + SA Art.35.4 list + EDPB 9-
  criteria) + review. Art.36 escalation pathway in MUST.

POSTURE SEED:
- Art.24/25/28/29/31/32/33/34/35: OFI on Arion (Arion has informal flows
  — privacy policy on website, DPAs with major cloud processors, ad-hoc
  breach response in security playbook — but no formal procedures /
  registers / SLA tracking)
- Art.26/27: N/A on Arion (no joint controllers; EU established)

ENGINE VERDICTS:
- Art.24: 0/10 children (6 deps + 4 direct)
- Art.25: 0/10 children (6 deps + 4 direct)
- Art.32: 0/9 children (5 deps + 4 direct)
- Art.26/27/28/29/31/33/34/35: 0/4 children each

EVAL CASES ADDED (174-184): 11 cases, all probing engine verdicts.

**Item-id preservation:**
- req:Art.28:data_processing_agreement + all item:Art.28:* preserved
- req:Art.33:breach_notification + all item:Art.33:* preserved
- Art.25 existing direct_evidence (default_settings_record) preserved
- Art.32 existing direct_evidence (resilience_test_record) preserved
- Art.24 had no direct_evidence pre-batch — 4 new added (no preservation
  concern)
- New specs (Art.26/27/29/31/34/35): fresh, no preservation concern

**Spine variant mix in 29a:**
- 1×policy_program (Art.28)
- 7×op_process (Art.26/27/29/31/33/34/35)
- 3×DerivedSpec expansion (Art.24/25/32)

**Cross-article web (Ch IV is the most interconnected):**
- Art.24 → ISO 5.1/5.3/9.3/A.5.1/A.5.34/A.5.36 (governance umbrella)
- Art.25 → ISO 6.1.2/6.1.3/A.5.34/A.5.36/A.8.10/A.8.25 (DPbD)
- Art.26 ↔ Art.28 (joint controllers vs controller-processor boundary
  documented in Art.26 scope leaf)
- Art.28 → Art.32 + Art.30 (DPA terms reference Art.32 security + RoPA)
- Art.29 → A.6.3 + A.7.3 training; → Art.28 DPA flow
- Art.31 → Art.36 (SA cooperation channel for prior consultation)
- Art.32 → ISO 27001 entire (security implementation framework)
- Art.33 ↔ Art.34 (Art.33 = SA notification, Art.34 = subject
  communication; different thresholds, paired in incident response)
- Art.35 → Art.36 (DPIA → prior consultation when residual high risk);
  → Art.9 + Art.10 (DPIA usually triggered for special-category + criminal
  data); → Art.22 (DPIA triggered for automated decisions)

**Three insights from the Ch IV core batch:**

1. **0-direct-evidence DerivedSpec expansion is now proven.** Art.24
   went from "6 deps, 0 direct" to "6 deps, 4 direct" in one batch.
   Pattern: when a DerivedSpec has been pure derivation (no direct
   artefacts), expansion adds direct evidence that captures the
   GDPR-specific artefacts NOT in the ISO derivations (e.g. Art.24's
   privacy programme charter is NOT in ISO; A.5.1 InfoSec policy is
   in ISO and derives from there). This shape will apply to future
   pure-derivation DerivedSpecs (Art.5.x family, Art.5.2).

2. **The compliance register pattern is reusable.** Art.24's GDPR
   compliance register is a per-article tracker — same shape as the
   SoA for ISO controls. Both serve "demonstrability" at audit time.
   Future regulatory frameworks (HIPAA, NIS2, DORA) will need
   equivalent register-as-canonical-artefact patterns.

3. **profile_fact + N/A pattern continues to do real work.** Art.26 +
   Art.27 are the second batch of profile_fact + N/A surfaces
   (after batch 27's Art.8/9/10 and batch 28's Art.22/23). The
   reviewer-affirmatively-rejects-engine-NC pattern is now well-
   established. For tenants like Arion, ~6 GDPR articles end up as
   N/A — each documented + each surfaces in Stage-2 for affirmative
   confirmation.

**Where this leaves the curation arc (post batch 29a):**
- ISO 27001: fully closed
- GDPR Ch II Principles (batch 27): closed
- GDPR Ch III Rights (batch 28): closed
- GDPR Ch IV core (batch 29a, this batch): closed — Art.24/25/26/27/28/29/30/31/32/33/34/35 done
- GDPR Ch IV DPO + meta (batch 29b — next): Art.36 + Art.37 + Art.38 +
  Art.39 + Art.40 + Art.41 + Art.42 + Art.43
- GDPR Ch V Transfers (batch 30): Art.44-49

**Next batch (batch 29b):**
- Art.36 (prior consultation) — op_process 4-leaf, profile_fact (DPIA
  flagged residual high risk). Few specs because only triggered by Art.35
  outcome.
- Art.37 (DPO designation) — op_process 4-leaf, profile_fact (must
  designate per Art.37.1 a-c criteria).
- Art.38 (DPO position) — op_process 4-leaf, profile_fact (paired with
  Art.37). Could merge with Art.37/39 as a DPO cluster but keeping
  separate per per-article curation principle.
- Art.39 (DPO tasks) — op_process 4-leaf, profile_fact (paired).
- Art.40 (codes of conduct) — op_process 4-leaf, profile_fact (org
  adheres to one). N/A for many.
- Art.41 (monitoring of approved codes) — op_process 4-leaf, profile_fact
  (org IS the monitoring body — rare). Almost always N/A.
- Art.42 (certification) — op_process 4-leaf, profile_fact (org seeks /
  holds certification).
- Art.43 (certification bodies) — op_process 4-leaf, profile_fact
  (org IS a cert body — extremely rare). Almost always N/A.

After batch 29b, Ch IV closes and only Ch V (Art.44-49 transfers) remains
for batch 30.

See also: [[curation-phase-b-batch-28-2026-06-02]] (Ch III closed —
established the 3-pattern batch shape), [[curation-phase-b-batch-27-2026
-06-02]] (DerivedSpec expansion pattern established).
