---
leaf_id: req:A.5.22:supplier_review_record
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 12
should_count: 2
---

# Supplier Information Security Review Records

> A.5.22 requires regular monitoring, review and evaluation of supplier information security practices and service delivery. Each review record evidences the activity for one supplier in one period: performance monitored, reports reviewed, audit conducted, incidents and audit-trails examined, corrective actions tracked. The schedule register, program meta-review and change-response log are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope of review (security practices, service delivery, changes since last review)

<<MUST item:A.5.22:rev_scope>>
_Why: 27002:5.22a,b_

<<TEXT>>

## 2. Service performance monitored against agreement (SLAs, incidents, breaches)

<<MUST item:A.5.22:rev_performance>>
_Why: 27002:5.22a_

<<TEXT>>

## 3. Supplier-provided service reports reviewed + progress meetings held

<<MUST item:A.5.22:rev_reports>>
_Why: 27002:5.22b_

<<TEXT>>

## 4. Audit conducted (own audit or independent attestation accepted) with follow-up on issues

<<MUST item:A.5.22:rev_audit>>
_Why: 27002:5.22c_

<<TEXT>>

## 5. Information exchanged about InfoSec incidents; joint review documented

<<MUST item:A.5.22:rev_incidents>>
_Why: 27002:5.22d_

<<TEXT>>

## 6. Supplier audit trails / event records reviewed (operational problems, failures, disruption)

<<MUST item:A.5.22:rev_audit_trails>>
_Why: 27002:5.22e_

<<TEXT>>

## 7. Identified problems / incidents managed through to resolution

<<MUST item:A.5.22:rev_problems>>
_Why: 27002:5.22f_

<<TEXT>>

## 8. Supplier's own supplier relationships reviewed (sub-supplier / fourth-party oversight)

<<MUST item:A.5.22:rev_subsupplier>>
_Why: 27002:5.22g_

<<TEXT>>

## 9. Supplier continuity capability verified (link to A.5.29 / A.5.30)

<<MUST item:A.5.22:rev_continuity>>
_Why: 27002:5.22h_

<<TEXT>>

## 10. Supplier's compliance-review / enforcement responsibilities confirmed

<<MUST item:A.5.22:rev_compliance>>
_Why: 27002:5.22i_

<<TEXT>>

## 11. Corrective actions raised for deficiencies, tracked to closure

<<MUST item:A.5.22:rev_corrective>>
_Why: 27002:5.22j_

<<TEXT>>

## 12. Findings recorded per review with severity

<<MUST item:A.5.22:rev_findings>>
_Why: 27002:5.22 — record_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. KPIs / metrics tracked per supplier (incidents, SLA breaches, time-to-remediate)

<<SHOULD item:A.5.22:metrics>>
_Why: Measurable monitoring_

<<TEXT>>

### 2. Third-party attestations accepted in lieu of direct audit (with criteria)

<<SHOULD item:A.5.22:attestations_accepted>>
_Why: Efficiency_

<<TEXT>>
