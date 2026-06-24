---
leaf_id: req:Art.27:representative_designation
control_ref: Art.27
standard_id: GDPR:2016/679
evidence_type: designation_document
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Representative Designation

> Art.27 requires non-EU controllers/processors targeting EU data subjects under Art.3.2 to designate a representative in the EU in writing. The designation document is the canonical artefact

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Identity and contact details of designated representative (EU establishment)

<<MUST item:Art.27:representative_identity>>
_Why: Art.27.1 + Art.27.4_

<<TEXT>>

## 2. Member State where representative is established (one of the MS where subjects targeted)

<<MUST item:Art.27:member_state>>
_Why: Art.27.3_

<<TEXT>>

## 3. Mandate covering Art.27.4 functions (point of contact for SA + subjects)

<<MUST item:Art.27:mandate_scope>>
_Why: Art.27.4_

<<TEXT>>

## 4. Representative without prejudice to controller/processor liability (Art.27.5 acknowledged)

<<MUST item:Art.27:liability>>
_Why: Art.27.5_

<<TEXT>>

## 5. Designation in writing with date and signature

<<MUST item:Art.27:designation_in_writing>>
_Why: Art.27.1 — in writing_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Representative contact published in privacy notice (Art.13.1.a / Art.14.1.a integration)

<<SHOULD item:Art.27:publicly_listed>>
_Why: Cross-article coherence_

<<TEXT>>
