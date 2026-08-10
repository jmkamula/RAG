---
leaf_id: req:A.7.2.3:program_review
control_ref: A.7.2.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Consent Determination Program Review

<<DOC_CONTROL>>

> Annual verification — consent artifacts remain compliant, no-bundling holds, children handling correct, dark-pattern regression check (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.3:program_review -->
<!-- column: item:A.7.2.3:rev_date -->
<!-- column: item:A.7.2.3:rev_reviewer -->
<!-- column: item:A.7.2.3:rev_artifact_audit -->
<!-- column: item:A.7.2.3:rev_no_bundling_check -->
<!-- column: item:A.7.2.3:rev_children_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you review and document your consent management practices, ensuring they meet privacy standards and avoid issues like bundled consent or outdated methods, especially for handling children's data.

## When to use it

Use this template when your organization’s profile matches certain privacy triggers, and plan to complete it about once a year to keep your consent records up to date.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.3:program_review -->
| Rev Date | Rev Reviewer | Rev Artifact Audit | Rev No Bundling Check | Rev Children Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + UX + Legal)

<<GUIDANCE>>

### Rev Artifact Audit

<<MUST item:A.7.2.3:rev_artifact_audit>>
_Why: §7.2.3 quality standard_

> _Standard text:_ Artifact audit — sampled consent forms reviewed against quality standard

<<GUIDANCE>>

### Rev No Bundling Check

<<MUST item:A.7.2.3:rev_no_bundling_check>>
_Why: §7.2.3 — not bundled_

> _Standard text:_ No-bundling regression check — no service gated behind unrelated consent

<<GUIDANCE>>

### Rev Children Audit

<<MUST item:A.7.2.3:rev_children_audit>>
_Why: GDPR Art.8_

> _Standard text:_ Children-consent audit — age-gates functioning where age-of-consent applies

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
