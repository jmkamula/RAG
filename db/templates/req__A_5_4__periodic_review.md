---
leaf_id: req:A.5.4:periodic_review
control_ref: A.5.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Periodic Review of the Management Directive

> The directive must stay aligned with the policy framework it references — when policies are renamed, retired, or added the directive becomes stale. Review captures who reviewed, when, and whether the policy references and enforcement linkages still hold

<!-- TABLE-COLUMNS leaf:req:A.5.4:periodic_review -->
<!-- column: item:A.5.4:review_date -->
<!-- column: item:A.5.4:review_reviewer -->
<!-- column: item:A.5.4:review_outcome -->
<!-- column: item:A.5.4:review_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.4:periodic_review -->
| Review Date | Review Reviewer | Review Outcome | Review Actions |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.4:periodic_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.4:review_date>>
_Why: Periodic review_

> _Standard text:_ Review date within the planned interval

### Review Reviewer

<<MUST item:A.5.4:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically CISO or compliance lead, validated by top management)

### Review Outcome

<<MUST item:A.5.4:review_outcome>>
_Why: Periodic review_

> _Standard text:_ Outcome captured (no change / amended / re-issued) and policy-reference drift checked

### Review Actions

<<MUST item:A.5.4:review_actions>>
_Why: Continual improvement_

> _Standard text:_ Actions captured where the directive needed amendment (policy reorg, scope change, new personnel categories)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.4:review_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers listed (major policy reorg, M&A, regulatory change) prompting unscheduled review

### Review Next Date

<<SHOULD item:A.5.4:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
