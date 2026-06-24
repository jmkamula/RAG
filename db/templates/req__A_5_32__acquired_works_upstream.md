---
leaf_id: req:A.5.32:acquired_works_upstream
control_ref: A.5.32
standard_id: ISO27001:2022
evidence_type: intake_process
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Acquired Works Intake Upstream

> The upstream that feeds the inventory. Where the procedure covers ongoing protection and the inventory holds the current state, the intake upstream documents how new IPR enters the org — software procurement, open-source dependency adoption, third-party content licensing, M&A IPR transfer — and how each route results in an inventory entry

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Procurement intake — every commercial software purchase routes through licence review and inventory registration before deployment

<<MUST item:A.5.32:intake_procurement>>
_Why: Operational sufficiency_

<<TEXT>>

## 2. Open-source adoption path — dependency additions pass a licence-compatibility gate; results recorded in the inventory

<<MUST item:A.5.32:intake_opensource>>
_Why: 27002:5.32 — third-party_

<<TEXT>>

## 3. Third-party content licensing (images, fonts, datasets, AI training data) — intake confirms permitted use and records terms

<<MUST item:A.5.32:intake_content>>
_Why: 27002:5.32 — protect IPR_

<<TEXT>>

## 4. M&A or contractor-handover intake — IPR transferred in is inventoried and ownership re-confirmed

<<MUST item:A.5.32:intake_ma>>
_Why: 27002:5.32 — completeness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Block path for non-compliant intake (e.g., GPL component in a closed-source product) — rejection and alternatives sourcing process

<<SHOULD item:A.5.32:intake_block_path>>
_Why: Drift prevention_

<<TEXT>>

### 2. Cross-link to A.5.19 supplier risk — supplier-supplied IPR follows the supplier-onboarding flow

<<SHOULD item:A.5.32:intake_a519_link>>
_Why: Cross-control coherence_

<<TEXT>>
