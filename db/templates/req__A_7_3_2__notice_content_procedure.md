---
leaf_id: req:A.7.3.2:notice_content_procedure
control_ref: A.7.3.2
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Privacy Notice Content Determination Procedure

> §7.3.2 requires the org to decide + document what information goes into subject-facing notices + when it's provided. Covers the field catalog (purposes / contact / basis / obtained-from / statutory-or-contractual / rights / withdrawal / transfers / recipients / retention / automated decisions / complaint / frequency) and update-on-change trigger.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Field catalog — every information item that must be provided (purposes + controller identity + basis + source + statutory/contractual + rights + withdrawal + transfers + recipients + retention + automated decisions + complaint route + frequency)

<<MUST item:A.7.3.2:proc_field_catalog>>
_Why: §7.3.2 implementation guidance — examples_

<<TEXT>>

## 2. Timing rules — when information is provided (prior to processing / at collection / within X days of request / just-in-time / periodic frequency)

<<MUST item:A.7.3.2:proc_timing_rules>>
_Why: §7.3.2 — timing of such a provision_

<<TEXT>>

## 3. Medium selection — which channels (privacy notice URL, layered notices, in-product prompts, contract clauses)

<<MUST item:A.7.3.2:proc_medium_selection>>
_Why: GDPR Art.12 — appropriate measures_

<<TEXT>>

## 4. Update-on-change — purpose changes / new processing trigger a notice update within stated SLA

<<MUST item:A.7.3.2:proc_update_on_change>>
_Why: §7.3.2 — updated information if purposes changed_

<<TEXT>>

## 5. DPO + Legal signoff for notice text changes before deploy

<<MUST item:A.7.3.2:proc_signoff>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. UX / accessibility review before deploy (icons, plain language, layered notice)

<<SHOULD item:A.7.3.2:proc_ux_review>>
_Why: §7.3.3 — intelligible + accessible_

<<TEXT>>
