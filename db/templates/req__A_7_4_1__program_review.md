---
leaf_id: req:A.7.4.1:program_review
control_ref: A.7.4.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Collection Limitation Program Review

> Annual verification — collection inventory current, necessity rationales defensible, privacy-by-default holds across surfaces, no unnecessary fields silently added (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.1:program_review -->
<!-- column: item:A.7.4.1:rev_date -->
<!-- column: item:A.7.4.1:rev_reviewer -->
<!-- column: item:A.7.4.1:rev_necessity_audit -->
<!-- column: item:A.7.4.1:rev_default_state_audit -->
<!-- column: item:A.7.4.1:rev_drift_sweep -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.1:program_review -->
| Rev Date | Rev Reviewer | Rev Necessity Audit | Rev Default State Audit | Rev Drift Sweep |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.4.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Privacy Engineering)

### Rev Necessity Audit

<<MUST item:A.7.4.1:rev_necessity_audit>>
_Why: §7.4.1 — for identified purposes_

> _Standard text:_ Necessity audit — sampled fields reviewed against current purpose register

### Rev Default State Audit

<<MUST item:A.7.4.1:rev_default_state_audit>>
_Why: §7.4.1 — disabled by default_

> _Standard text:_ Default-state audit — optional fields default off across surfaces

### Rev Drift Sweep

<<MUST item:A.7.4.1:rev_drift_sweep>>
_Why: Change control_

> _Standard text:_ Drift sweep — new fields added since last review flagged for necessity review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
