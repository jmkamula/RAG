---
leaf_id: req:A.5.15:periodic_review
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Periodic Access Control Policy Review

> Access control policies decay as the IT estate grows — new systems, new cloud services, new federated identity sources all stress the policy. Review checks whether the rules still cover the actual estate, whether least-privilege is still operationalised correctly, and whether downstream A.5.18 provisioning is aligned

<!-- TABLE-COLUMNS leaf:req:A.5.15:periodic_review -->
<!-- column: item:A.5.15:review_date -->
<!-- column: item:A.5.15:review_reviewer -->
<!-- column: item:A.5.15:review_outcome -->
<!-- column: item:A.5.15:review_estate -->
<!-- column: item:A.5.15:review_a518_link -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.15:periodic_review -->
| Review Date | Review Reviewer | Review Outcome | Review Estate | Review A518 Link |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.15:periodic_review -->

## Column guidance — what to fill in

### Review Date

<<MUST item:A.5.15:review_date>>
_Why: Periodic review_

> _Standard text:_ Review date within the planned interval

### Review Reviewer

<<MUST item:A.5.15:review_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (typically CISO with IT and identity-management input)

### Review Outcome

<<MUST item:A.5.15:review_outcome>>
_Why: Periodic review_

> _Standard text:_ Outcome captured (no change / amended / re-issued) with rationale per amendment

### Review Estate

<<MUST item:A.5.15:review_estate>>
_Why: Drift catch_

> _Standard text:_ Estate-alignment check — new systems / cloud services added since last review reflected in policy

### Review A518 Link

<<MUST item:A.5.15:review_a518_link>>
_Why: Cross-control coherence_

> _Standard text:_ A.5.18 provisioning procedure cross-checked for alignment with policy changes

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Review Triggers

<<SHOULD item:A.5.15:review_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc triggers listed (M&A, new identity provider, major SaaS adoption, access-related incident)

### Review Next Date

<<SHOULD item:A.5.15:review_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
