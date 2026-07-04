---
leaf_id: req:A.7.4.5:end_of_processing_procedure
control_ref: A.7.4.5
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# End-of-Processing Deletion / De-identification Procedure

> §7.4.5 requires deletion or de-identification when original PII is no longer necessary. Complements A.7.4.7 retention + A.7.4.8 disposal.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. End-of-processing trigger definition per activity (purpose fulfilled / consent withdrawn / retention lapsed / no further processing anticipated)

<<MUST item:A.7.4.5:proc_end_of_processing_trigger>>
_Why: §7.4.5 — no longer necessary_

<<TEXT>>

## 2. Delete-or-de-identify decision rule per activity

<<MUST item:A.7.4.5:proc_delete_or_deidentify>>
_Why: §7.4.5 — either delete or render de-identified_

<<TEXT>>

## 3. De-identification standard — resulting data cannot reasonably permit re-identification

<<MUST item:A.7.4.5:proc_deidentification_standard>>
_Why: §7.4.5 — cannot reasonably permit re-identification_

<<TEXT>>

## 4. Verification — post-action verification that PII is actually gone / de-identified across all systems + backups

<<MUST item:A.7.4.5:proc_verification>>
_Why: Effectiveness_

<<TEXT>>

## 5. Record of end-of-processing action (link to A.7.4.5 register)

<<MUST item:A.7.4.5:proc_records>>
_Why: Audit trail_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Data Ops + Privacy Engineering)

<<SHOULD item:A.7.4.5:proc_owner>>
_Why: Accountability_

<<TEXT>>
