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

> §7.4.1 requires the org to limit PII collection to what's adequate, relevant + necessary for identified purposes — including indirect collection (weblogs, system logs). Also encodes privacy-by-default (opt-in for optional collections).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Necessity test per data field — adequate + relevant + necessary for stated purpose

<<MUST item:A.7.4.1:proc_necessity_test>>
_Why: §7.4.1 — adequate, relevant and necessary + Art.5.1.c_

<<TEXT>>

## 2. Indirect collection scoped (weblogs / cookies / device signals / third-party enrichment) — same necessity test applied

<<MUST item:A.7.4.1:proc_indirect_collection>>
_Why: §7.4.1 — indirectly through web logs_

<<TEXT>>

## 3. Privacy-by-default — optional collections disabled by default; enabled only by explicit subject choice

<<MUST item:A.7.4.1:proc_default_off>>
_Why: §7.4.1 — disabled by default + GDPR Art.25.2_

<<TEXT>>

## 4. Data-field review — each new field added to a collection form goes through necessity review before deploy

<<MUST item:A.7.4.1:proc_field_review>>
_Why: Data minimisation_

<<TEXT>>

## 5. Field-removal procedure — periodic sweep of collected fields that are no longer necessary

<<MUST item:A.7.4.1:proc_removal_procedure>>
_Why: §7.4.1 — minimum necessary_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Product / Privacy Engineering)

<<SHOULD item:A.7.4.1:proc_owner>>
_Why: Accountability_

<<TEXT>>
