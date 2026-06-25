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
table_shape: true
---

# Supplier Information Security Review Records

> A.5.22 requires regular monitoring, review and evaluation of supplier information security practices and service delivery. Each review record evidences the activity for one supplier in one period: performance monitored, reports reviewed, audit conducted, incidents and audit-trails examined, corrective actions tracked. The schedule register, program meta-review and change-response log are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.22:supplier_review_record -->
<!-- column: item:A.5.22:rev_scope -->
<!-- column: item:A.5.22:rev_performance -->
<!-- column: item:A.5.22:rev_reports -->
<!-- column: item:A.5.22:rev_audit -->
<!-- column: item:A.5.22:rev_incidents -->
<!-- column: item:A.5.22:rev_audit_trails -->
<!-- column: item:A.5.22:rev_problems -->
<!-- column: item:A.5.22:rev_subsupplier -->
<!-- column: item:A.5.22:rev_continuity -->
<!-- column: item:A.5.22:rev_compliance -->
<!-- column: item:A.5.22:rev_corrective -->
<!-- column: item:A.5.22:rev_findings -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.22:supplier_review_record -->
| Rev Scope | Rev Performance | Rev Reports | Rev Audit | Rev Incidents | Rev Audit Trails | Rev Problems | Rev Subsupplier | Rev Continuity | Rev Compliance | Rev Corrective | Rev Findings |
|---|---|---|---|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.22:supplier_review_record -->

## Column guidance — what to fill in

### Rev Scope

<<MUST item:A.5.22:rev_scope>>
_Why: 27002:5.22a,b_

> _Standard text:_ Scope of review (security practices, service delivery, changes since last review)

### Rev Performance

<<MUST item:A.5.22:rev_performance>>
_Why: 27002:5.22a_

> _Standard text:_ Service performance monitored against agreement (SLAs, incidents, breaches)

### Rev Reports

<<MUST item:A.5.22:rev_reports>>
_Why: 27002:5.22b_

> _Standard text:_ Supplier-provided service reports reviewed + progress meetings held

### Rev Audit

<<MUST item:A.5.22:rev_audit>>
_Why: 27002:5.22c_

> _Standard text:_ Audit conducted (own audit or independent attestation accepted) with follow-up on issues

### Rev Incidents

<<MUST item:A.5.22:rev_incidents>>
_Why: 27002:5.22d_

> _Standard text:_ Information exchanged about InfoSec incidents; joint review documented

### Rev Audit Trails

<<MUST item:A.5.22:rev_audit_trails>>
_Why: 27002:5.22e_

> _Standard text:_ Supplier audit trails / event records reviewed (operational problems, failures, disruption)

### Rev Problems

<<MUST item:A.5.22:rev_problems>>
_Why: 27002:5.22f_

> _Standard text:_ Identified problems / incidents managed through to resolution

### Rev Subsupplier

<<MUST item:A.5.22:rev_subsupplier>>
_Why: 27002:5.22g_

> _Standard text:_ Supplier's own supplier relationships reviewed (sub-supplier / fourth-party oversight)

### Rev Continuity

<<MUST item:A.5.22:rev_continuity>>
_Why: 27002:5.22h_

> _Standard text:_ Supplier continuity capability verified (link to A.5.29 / A.5.30)

### Rev Compliance

<<MUST item:A.5.22:rev_compliance>>
_Why: 27002:5.22i_

> _Standard text:_ Supplier's compliance-review / enforcement responsibilities confirmed

### Rev Corrective

<<MUST item:A.5.22:rev_corrective>>
_Why: 27002:5.22j_

> _Standard text:_ Corrective actions raised for deficiencies, tracked to closure

### Rev Findings

<<MUST item:A.5.22:rev_findings>>
_Why: 27002:5.22 — record_

> _Standard text:_ Findings recorded per review with severity

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Metrics

<<SHOULD item:A.5.22:metrics>>
_Why: Measurable monitoring_

> _Standard text:_ KPIs / metrics tracked per supplier (incidents, SLA breaches, time-to-remediate)

### Attestations Accepted

<<SHOULD item:A.5.22:attestations_accepted>>
_Why: Efficiency_

> _Standard text:_ Third-party attestations accepted in lieu of direct audit (with criteria)
