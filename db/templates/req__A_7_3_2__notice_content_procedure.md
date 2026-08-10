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

<<DOC_CONTROL>>

> §7.3.2 requires the org to decide + document what information goes into subject-facing notices + when it's provided. Covers the field catalog (purposes / contact / basis / obtained-from / statutory-or-contractual / rights / withdrawal / transfers / recipients / retention / automated decisions / complaint / frequency) and update-on-change trigger.

## What this template gives you

This template helps you clearly decide and document what information should be included in privacy notices for individuals, ensuring you cover all the key topics required by privacy standards.

## When to use it

Use this procedure whenever your organization needs to determine or update the content of privacy notices, especially when there are changes in your data practices or when specific triggers in your privacy profile occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to write.

## 1. Field catalog — every information item that must be provided (purposes + controller identity + basis + source + statutory/contractual + rights + withdrawal + transfers + recipients + retention + automated decisions + complaint route + frequency)

<<MUST item:A.7.3.2:proc_field_catalog>>
_Why: §7.3.2 implementation guidance — examples_

<<GUIDANCE>>

<<TEXT>>

## 2. Timing rules — when information is provided (prior to processing / at collection / within X days of request / just-in-time / periodic frequency)

<<MUST item:A.7.3.2:proc_timing_rules>>
_Why: §7.3.2 — timing of such a provision_

<<GUIDANCE>>

<<TEXT>>

## 3. Medium selection — which channels (privacy notice URL, layered notices, in-product prompts, contract clauses)

<<MUST item:A.7.3.2:proc_medium_selection>>
_Why: GDPR Art.12 — appropriate measures_

<<GUIDANCE>>

<<TEXT>>

## 4. Update-on-change — purpose changes / new processing trigger a notice update within stated SLA

<<MUST item:A.7.3.2:proc_update_on_change>>
_Why: §7.3.2 — updated information if purposes changed_

<<GUIDANCE>>

<<TEXT>>

## 5. DPO + Legal signoff for notice text changes before deploy

<<MUST item:A.7.3.2:proc_signoff>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. UX / accessibility review before deploy (icons, plain language, layered notice)

<<SHOULD item:A.7.3.2:proc_ux_review>>
_Why: §7.3.3 — intelligible + accessible_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
