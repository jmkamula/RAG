---
leaf_id: req:A.6.6:nda_template_review
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic NDA Template Review

> Periodic verification that the template still reflects current information classification (A.5.12), current jurisdictional enforceability (Schrems-style impacts on cross-border NDAs), and that all active signers are on a current-enough version. Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.6:rev_date>>
_Why: 27002:6.6 — regularly reviewed_

<<TEXT>>

## 2. Reviewer identity (Legal counsel + InfoSec lead jointly)

<<MUST item:A.6.6:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Information-classification drift check — has A.5.12 classification scheme changed in ways affecting NDA info_classes?

<<MUST item:A.6.6:rev_classification_drift>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Enforceability check per jurisdiction (legal counsel input — case-law shifts, Schrems-style impacts on cross-border data flows in NDA scope)

<<MUST item:A.6.6:rev_enforceability>>
_Why: 27002:6.6 — applicable laws_

<<TEXT>>

## 5. Signer-currency analysis (% on current template version; plan for re-signing the gap where material clauses changed)

<<MUST item:A.6.6:rev_signer_currency>>
_Why: 27002:6.6 — current_

<<TEXT>>

## 6. Changes propagated to the live template and to the signer-re-signing plan

<<MUST item:A.6.6:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (material classification change, case-law shift, M&A bringing new counterparty types)

<<SHOULD item:A.6.6:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.6:rev_next_date>>
_Why: Planning_

<<TEXT>>
