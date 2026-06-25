---
leaf_id: req:A.5.36:compliance_review_record
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Compliance Review Records (Policies, Rules, Standards)

> A.5.36 requires regular review of compliance with the InfoSec policy, topic-specific policies, rules and standards. Each review record evidences the activity for one cycle: schedule honoured, scope covered, method used, findings recorded, corrective actions opened. The schedule register, program meta-review and nonconformity register are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.36:compliance_review_record -->
<!-- column: item:A.5.36:schedule -->
<!-- column: item:A.5.36:scope -->
<!-- column: item:A.5.36:method -->
<!-- column: item:A.5.36:findings -->
<!-- column: item:A.5.36:corrective_actions -->
<!-- column: item:A.5.36:owner -->
<!-- column: item:A.5.36:review_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.36:compliance_review_record -->
| Schedule | Scope | Method | Findings | Corrective Actions | Owner | Review Date |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.36:compliance_review_record -->

## Column guidance — what to fill in

### Schedule

<<MUST item:A.5.36:schedule>>
_Why: 27002:5.36 — regularly reviewed_

> _Standard text:_ Schedule honoured for this cycle (each planned policy/rule/standard actually reviewed in the period; gaps flagged for next cycle)

### Scope

<<MUST item:A.5.36:scope>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

> _Standard text:_ Scope of this cycle (which policies / rules / standards were reviewed — typically a slice of the full catalogue if rotated across cycles)

### Method

<<MUST item:A.5.36:method>>
_Why: 27002:5.36 — reviewed_

> _Standard text:_ Method used per item (control sampling, formal audit, automated check, attestation, walkthrough); rationale for method choice given the item type

### Findings

<<MUST item:A.5.36:findings>>
_Why: 27002:5.36 — review_

> _Standard text:_ Findings recorded per review with severity (compliance vs. nonconformity vs. opportunity-for-improvement; concrete, evidenced)

### Corrective Actions

<<MUST item:A.5.36:corrective_actions>>
_Why: Closes the loop_

> _Standard text:_ Corrective actions opened per nonconformity finding (with owner, target date) — feeds the nonconformity register

### Owner

<<MUST item:A.5.36:owner>>
_Why: Accountability_

> _Standard text:_ Named owner of this review cycle (the person who ran it — typically compliance lead or designate)

### Review Date

<<MUST item:A.5.36:review_date>>
_Why: 27002:5.36 — regularly_

> _Standard text:_ Review date and period covered (start/end of the review activity)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Continuous Compliance

<<SHOULD item:A.5.36:continuous_compliance>>
_Why: Scale and timeliness_

> _Standard text:_ Continuous-compliance monitoring tooling output considered (where used — config drift, control health checks, CSPM signal)

### Method Evidence

<<SHOULD item:A.5.36:method_evidence>>
_Why: Audit defensibility_

> _Standard text:_ Method evidence retained (sample selection notes, attestation responses, audit working papers) for audit defensibility
