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

> §7.2.2 requires each PII processing activity to have a determined + documented lawful basis and to comply with that basis. The procedure governs how bases are selected from the applicable catalog (consent / contract / legal obligation / vital interests / public interest / legitimate interests), when balancing tests (legitimate interests) are performed, and how basis changes are handled.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Basis catalog — enumerated permitted bases per applicable jurisdiction (GDPR Art.6.1.a-f; other jurisdictions as applicable)

<<MUST item:A.7.2.2:proc_basis_catalog>>
_Why: §7.2.2 implementation guidance — legal basis catalog_

<<TEXT>>

## 2. Selection test per basis (consent — freely given + specific + unambiguous; contract — necessity; legal obligation — cited law; vital interests — physical safety; public interest — cited task; legitimate interests — LIA with balancing test)

<<MUST item:A.7.2.2:proc_selection_test>>
_Why: §7.2.2 implementation guidance_

<<TEXT>>

## 3. Legitimate-interests balancing test procedure (necessity + balancing against subject rights)

<<MUST item:A.7.2.2:proc_lia_procedure>>
_Why: GDPR Art.6.1.f — balanced against interests + fundamental rights_

<<TEXT>>

## 4. Special-category overlay (Art.9/10 basis required in addition to Art.6 for health, biometric, criminal, etc.)

<<MUST item:A.7.2.2:proc_special_category_overlay>>
_Why: §7.2.2 — special categories more stringent controls_

<<TEXT>>

## 5. Basis change procedure — changing basis requires re-assessment and often subject notice (§7.3.3)

<<MUST item:A.7.2.2:proc_basis_change>>
_Why: §7.2.2 — changing/extending purposes_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. DPO + legal counsel signoff before basis enters production

<<SHOULD item:A.7.2.2:proc_review_signoff>>
_Why: Accountability_

<<TEXT>>
