---
leaf_id: req:A.7.4.1:collection_limitation_procedure
control_ref: A.7.4.1
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Collection Limitation Procedure

<<DOC_CONTROL>>

> §7.4.1 requires the org to limit PII collection to what's adequate, relevant + necessary for identified purposes — including indirect collection (weblogs, system logs). Also encodes privacy-by-default (opt-in for optional collections).

## What this template gives you

This template helps you document how your organization limits the collection of personal information to only what is necessary and relevant, including for data gathered indirectly, and ensures privacy-by-default practices.

## When to use it

Use this procedure whenever your organization collects personal information, especially if your activities match specific triggers such as new data collection methods or changes in purpose. Update the document as needed when your practices or systems change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this template from scratch, as each required section will take roughly 10 to 15 minutes to fill out thoughtfully.

## 1. Necessity test per data field — adequate + relevant + necessary for stated purpose

<<MUST item:A.7.4.1:proc_necessity_test>>
_Why: §7.4.1 — adequate, relevant and necessary + Art.5.1.c_

<<GUIDANCE>>

<<TEXT>>

## 2. Indirect collection scoped (weblogs / cookies / device signals / third-party enrichment) — same necessity test applied

<<MUST item:A.7.4.1:proc_indirect_collection>>
_Why: §7.4.1 — indirectly through web logs_

<<GUIDANCE>>

<<TEXT>>

## 3. Privacy-by-default — optional collections disabled by default; enabled only by explicit subject choice

<<MUST item:A.7.4.1:proc_default_off>>
_Why: §7.4.1 — disabled by default + GDPR Art.25.2_

<<GUIDANCE>>

<<TEXT>>

## 4. Data-field review — each new field added to a collection form goes through necessity review before deploy

<<MUST item:A.7.4.1:proc_field_review>>
_Why: Data minimisation_

<<GUIDANCE>>

<<TEXT>>

## 5. Field-removal procedure — periodic sweep of collected fields that are no longer necessary

<<MUST item:A.7.4.1:proc_removal_procedure>>
_Why: §7.4.1 — minimum necessary_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Product / Privacy Engineering)

<<SHOULD item:A.7.4.1:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
