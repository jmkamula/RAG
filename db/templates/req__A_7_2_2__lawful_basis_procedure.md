---
leaf_id: req:A.7.2.2:lawful_basis_procedure
control_ref: A.7.2.2
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Lawful Basis Assessment Procedure

<<DOC_CONTROL>>

> §7.2.2 requires each PII processing activity to have a determined + documented lawful basis and to comply with that basis. The procedure governs how bases are selected from the applicable catalog (consent / contract / legal obligation / vital interests / public interest / legitimate interests), when balancing tests (legitimate interests) are performed, and how basis changes are handled.

## What this template gives you

This template helps you clearly document the legal reason for collecting and using personal data, ensuring your activities meet privacy requirements and are easy to explain to regulators or customers.

## When to use it

Use this whenever you start a new activity involving personal data or when your processing activities change. Update it as needed to keep your records accurate and compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Basis catalog — enumerated permitted bases per applicable jurisdiction (GDPR Art.6.1.a-f; other jurisdictions as applicable)

<<MUST item:A.7.2.2:proc_basis_catalog>>
_Why: §7.2.2 implementation guidance — legal basis catalog_

<<GUIDANCE>>

<<TEXT>>

## 2. Selection test per basis (consent — freely given + specific + unambiguous; contract — necessity; legal obligation — cited law; vital interests — physical safety; public interest — cited task; legitimate interests — LIA with balancing test)

<<MUST item:A.7.2.2:proc_selection_test>>
_Why: §7.2.2 implementation guidance_

<<GUIDANCE>>

<<TEXT>>

## 3. Legitimate-interests balancing test procedure (necessity + balancing against subject rights)

<<MUST item:A.7.2.2:proc_lia_procedure>>
_Why: GDPR Art.6.1.f — balanced against interests + fundamental rights_

<<GUIDANCE>>

<<TEXT>>

## 4. Special-category overlay (Art.9/10 basis required in addition to Art.6 for health, biometric, criminal, etc.)

<<MUST item:A.7.2.2:proc_special_category_overlay>>
_Why: §7.2.2 — special categories more stringent controls_

<<GUIDANCE>>

<<TEXT>>

## 5. Basis change procedure — changing basis requires re-assessment and often subject notice (§7.3.3)

<<MUST item:A.7.2.2:proc_basis_change>>
_Why: §7.2.2 — changing/extending purposes_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. DPO + legal counsel signoff before basis enters production

<<SHOULD item:A.7.2.2:proc_review_signoff>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
