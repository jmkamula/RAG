---
leaf_id: req:A.6.6:nda_template
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: agreement_template
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 3
---

# Confidentiality / Non-Disclosure Agreement Template

<<DOC_CONTROL>>

> A.6.6 requires confidentiality or non-disclosure agreements appropriate to the organisation's information protection needs, regularly reviewed, and signed by personnel and relevant interested parties. The template carries the clauses (parties, info classes, duration, return/destruction, signature, last-reviewed date). The signature register, applicable-parties scope and periodic review are sibling leaves

## What this template gives you

This template provides a ready-to-use confidentiality or non-disclosure agreement, ensuring your organization’s sensitive information is protected and that all relevant parties understand their responsibilities regarding information security.

## When to use it

Use this template whenever you need to formalize confidentiality commitments with employees, contractors, or partners. Review and update it about once a year to keep it current with your organization’s needs.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this template from scratch, depending on the number of parties involved and the detail required for each section.

## 1. Parties covered (employees, contractors, suppliers, visitors with access to sensitive info, M&A counterparties)

<<MUST item:A.6.6:parties_covered>>
_Why: 27002:6.6 — personnel + interested parties_

<<GUIDANCE>>

<<TEXT>>

## 2. Information classes protected (cross-link to A.5.12 classification — confidential / restricted / trade-secret tiers; PII overlay where applicable)

<<MUST item:A.6.6:info_classes>>
_Why: 27002:6.6 — protection of information_

<<GUIDANCE>>

<<TEXT>>

## 3. Duration of confidentiality obligation (indefinite for trade secrets; time-limited for non-trade-secret confidential info — typically 3-5 years post-termination)

<<MUST item:A.6.6:duration>>
_Why: 27002:6.6 — needs for protection_

<<GUIDANCE>>

<<TEXT>>

## 4. Return or destruction obligation at end of relationship (with certified-destruction option for paper, secure-deletion for digital — links to A.8.10)

<<MUST item:A.6.6:return_destruction>>
_Why: 27002:6.6 — protection_

<<GUIDANCE>>

<<TEXT>>

## 5. Signature requirement enforced before access granted (no access without signed NDA — gates A.5.18 access grant for non-employees)

<<MUST item:A.6.6:signature_requirement>>
_Why: 27002:6.6 — signed_

<<GUIDANCE>>

<<TEXT>>

## 6. Last-reviewed date on the template (review evidence — drives the freshness check)

<<MUST item:A.6.6:last_reviewed>>
_Why: 27002:6.6 — regularly reviewed_

<<GUIDANCE>>

<<TEXT>>

## 7. Named owner of the template (Legal counsel with InfoSec partner)

<<MUST item:A.6.6:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Jurisdiction and remedies clauses (governing law, injunctive relief, liquidated damages where lawful)

<<SHOULD item:A.6.6:jurisdiction_remedies>>
_Why: Enforceability_

<<GUIDANCE>>

<<TEXT>>

### 2. Tiered NDA variants (employee NDA — lighter; contractor — full; supplier — bilateral; M&A counterparty — heavy with extended duration)

<<SHOULD item:A.6.6:variant_tiers>>
_Why: Proportionality_

<<GUIDANCE>>

<<TEXT>>

### 3. Cross-link to A.6.2 employment terms — for employees the NDA and employment terms together form the personnel info-security contract package

<<SHOULD item:A.6.6:a6_2_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
