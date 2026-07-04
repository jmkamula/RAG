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

> §7.2.1 requires each PII processing activity to have its purpose identified and documented before processing begins. The procedure governs how new purposes are identified (upstream trigger events), documented (fields captured), reviewed (legal + DPO signoff), and communicated (to §7.3.2 notice + §7.2.3 consent + §7.2.8 RoPA). Without a clear, documented purpose per activity, consent + notice cannot be validly given.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Intake triggers listed (new product launch, new processing activity, new data source, new integration)

<<MUST item:A.7.2.1:proc_intake_trigger>>
_Why: §7.2.1 — purposes identified before processing_

<<TEXT>>

## 2. Documentation fields per purpose (purpose text, categories of PII, categories of subjects, retention, recipients, legal basis link)

<<MUST item:A.7.2.1:proc_documentation_fields>>
_Why: §7.2.1 — documented_

<<TEXT>>

## 3. Specificity test — purpose statements must be sufficiently clear + detailed for use in §7.3.2 notice + §7.2.3 consent

<<MUST item:A.7.2.1:proc_specificity_test>>
_Why: §7.2.1 implementation guidance_

<<TEXT>>

## 4. Review + signoff step (DPO + legal counsel) before purpose enters production register

<<MUST item:A.7.2.1:proc_review_signoff>>
_Why: §5.4.1.3 accountability_

<<TEXT>>

## 5. Change-control — extending or changing a purpose requires re-review + potentially new consent (§7.2.2)

<<MUST item:A.7.2.1:proc_change_control>>
_Why: §7.2.2 implementation guidance — changing purposes_

<<TEXT>>

## 6. Downstream notice — purpose changes propagate to notice + consent + RoPA + PIA

<<MUST item:A.7.2.1:proc_downstream_notice>>
_Why: §7.2.1 — usable in required information_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO or Privacy Office)

<<SHOULD item:A.7.2.1:proc_owner>>
_Why: Accountability_

<<TEXT>>
