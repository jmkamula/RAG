---
leaf_id: req:A.7.2.7:program_review
control_ref: A.7.2.7
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Joint Controller Program Review

> Annual verification — every joint arrangement has a current documented arrangement, essence publications reachable, rights-routing functional (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.7:program_review -->
<!-- column: item:A.7.2.7:rev_date -->
<!-- column: item:A.7.2.7:rev_reviewer -->
<!-- column: item:A.7.2.7:rev_coverage_check -->
<!-- column: item:A.7.2.7:rev_essence_publication_audit -->
<!-- column: item:A.7.2.7:rev_rights_routing_test -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.7:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Essence Publication Audit | Rev Rights Routing Test |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.7:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.7:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.2.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal)

### Rev Coverage Check

<<MUST item:A.7.2.7:rev_coverage_check>>
_Why: §7.2.7 — every joint controller_

> _Standard text:_ Coverage check — every joint arrangement identified is documented

### Rev Essence Publication Audit

<<MUST item:A.7.2.7:rev_essence_publication_audit>>
_Why: Art.26.2_

> _Standard text:_ Essence-publication audit — sampled arrangements verified to have published essence reachable by subjects

### Rev Rights Routing Test

<<MUST item:A.7.2.7:rev_rights_routing_test>>
_Why: Art.26.3_

> _Standard text:_ Rights-routing test — sampled subject requests verified to route correctly regardless of party addressed

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
