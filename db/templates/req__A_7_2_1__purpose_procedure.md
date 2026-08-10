---
leaf_id: req:A.7.2.1:purpose_procedure
control_ref: A.7.2.1
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Purpose Identification Procedure

<<DOC_CONTROL>>

> §7.2.1 requires each PII processing activity to have its purpose identified and documented before processing begins. The procedure governs how new purposes are identified (upstream trigger events), documented (fields captured), reviewed (legal + DPO signoff), and communicated (to §7.3.2 notice + §7.2.3 consent + §7.2.8 RoPA). Without a clear, documented purpose per activity, consent + notice cannot be validly given.

## What this template gives you

This template helps you clearly define and document the purpose for every activity where you process personal data, ensuring your records are complete and compliant with privacy requirements.

## When to use it

Use this whenever you start a new activity involving personal data or when an existing activity changes, and update it as needed if your processing purposes evolve.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, as each required section takes around 10–15 minutes to fill in thoughtfully.

## 1. Intake triggers listed (new product launch, new processing activity, new data source, new integration)

<<MUST item:A.7.2.1:proc_intake_trigger>>
_Why: §7.2.1 — purposes identified before processing_

<<GUIDANCE>>

<<TEXT>>

## 2. Documentation fields per purpose (purpose text, categories of PII, categories of subjects, retention, recipients, legal basis link)

<<MUST item:A.7.2.1:proc_documentation_fields>>
_Why: §7.2.1 — documented_

<<GUIDANCE>>

<<TEXT>>

## 3. Specificity test — purpose statements must be sufficiently clear + detailed for use in §7.3.2 notice + §7.2.3 consent

<<MUST item:A.7.2.1:proc_specificity_test>>
_Why: §7.2.1 implementation guidance_

<<GUIDANCE>>

<<TEXT>>

## 4. Review + signoff step (DPO + legal counsel) before purpose enters production register

<<MUST item:A.7.2.1:proc_review_signoff>>
_Why: §5.4.1.3 accountability_

<<GUIDANCE>>

<<TEXT>>

## 5. Change-control — extending or changing a purpose requires re-review + potentially new consent (§7.2.2)

<<MUST item:A.7.2.1:proc_change_control>>
_Why: §7.2.2 implementation guidance — changing purposes_

<<GUIDANCE>>

<<TEXT>>

## 6. Downstream notice — purpose changes propagate to notice + consent + RoPA + PIA

<<MUST item:A.7.2.1:proc_downstream_notice>>
_Why: §7.2.1 — usable in required information_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO or Privacy Office)

<<SHOULD item:A.7.2.1:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
