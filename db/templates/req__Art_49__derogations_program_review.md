---
leaf_id: req:Art.49:derogations_program_review
control_ref: Art.49
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Derogations Program Review

<<DOC_CONTROL>>

> Annual verification — invocations defensible against strict construction, frequent-invocation patterns flagged for Art.46 migration (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.49:derogations_program_review -->
<!-- column: item:Art.49:rev_date -->
<!-- column: item:Art.49:rev_reviewer -->
<!-- column: item:Art.49:rev_strict_construction_audit -->
<!-- column: item:Art.49:rev_pattern_detection -->
<!-- column: item:Art.49:rev_sa_notifications -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of when and why you rely on GDPR derogations, making it easier to defend your decisions and spot patterns that may need a different legal basis.

## When to use it

Use this review record if your data transfers sometimes rely on GDPR Article 49 derogations. Plan to update it about once a year, or whenever your activities match certain triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of cases you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.49:derogations_program_review -->
| Rev Date | Rev Reviewer | Rev Strict Construction Audit | Rev Pattern Detection | Rev Sa Notifications |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.49:derogations_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.49:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.49:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

<<GUIDANCE>>

### Rev Strict Construction Audit

<<MUST item:Art.49:rev_strict_construction_audit>>
_Why: EDPB 2/2018_

> _Standard text:_ Strict-construction audit — sampled invocations reviewed against EDPB 2/2018 narrow interpretation

<<GUIDANCE>>

### Rev Pattern Detection

<<MUST item:Art.49:rev_pattern_detection>>
_Why: Art.49 — exceptional use_

> _Standard text:_ Pattern detection — recurring derogation use for same recipient/purpose flagged for Art.46 migration

<<GUIDANCE>>

### Rev Sa Notifications

<<MUST item:Art.49:rev_sa_notifications>>
_Why: Art.49.1 second paragraph_

> _Standard text:_ SA notifications audit — Art.49.1 second-paragraph notifications dispatched as required

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.49:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
