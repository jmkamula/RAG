---
leaf_id: req:A.6.2:employment_terms_template
control_ref: A.6.2
standard_id: ISO27001:2022
evidence_type: agreement_template
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
---

# Employment Contract Information Security Terms (Template)

> A.6.2 requires employment contractual agreements to state both personnel's and the organisation's information security responsibilities. The template carries the standard clauses (personnel duties, org duties, policy references, duration, signature requirement). The signed-terms register, applicable-workers scope and periodic template review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Personnel's information security responsibilities stated (confidentiality, acceptable use, access discipline, incident reporting obligation)

<<MUST item:A.6.2:personnel_responsibilities>>
_Why: 27002:6.2 — personnel's responsibilities_

<<TEXT>>

## 2. Organization's information security responsibilities stated (training provision, tools, protection of personal data, fair-treatment of reported events)

<<MUST item:A.6.2:organization_responsibilities>>
_Why: 27002:6.2 — organization's responsibilities_

<<TEXT>>

## 3. Reference to InfoSec policy and topic-specific policies binding the personnel (A.5.1 master policy, A.5.10 acceptable use, A.5.15 access control)

<<MUST item:A.6.2:policy_reference>>
_Why: 27002:6.2 — for information security_

<<TEXT>>

## 4. Duration of obligations stated (during employment AND surviving obligations cross-link to A.6.5 post-employment)

<<MUST item:A.6.2:duration>>
_Why: 27002:6.2 + A.6.5_

<<TEXT>>

## 5. Signature requirement before employment commences (no access granted without signed terms)

<<MUST item:A.6.2:signature>>
_Why: 27002:6.2 — contractual agreements_

<<TEXT>>

## 6. Named owner of the template (HR with InfoSec + Legal joint sign-off on the clauses)

<<MUST item:A.6.2:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Links to Acceptable Use Policy (A.5.10) by reference (so AUP updates don't require contract amendment)

<<SHOULD item:A.6.2:aup_link>>
_Why: Cross-control consistency_

<<TEXT>>

### 2. Links to disciplinary process (A.6.4) by reference

<<SHOULD item:A.6.2:disciplinary_link>>
_Why: Enforcement clarity_

<<TEXT>>

### 3. Cross-link to A.6.6 NDA template (employment terms + NDA together form the personnel info-security contract package)

<<SHOULD item:A.6.2:nda_link>>
_Why: Cross-control coherence_

<<TEXT>>
