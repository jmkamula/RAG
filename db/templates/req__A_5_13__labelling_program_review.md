---
leaf_id: req:A.5.13:labelling_program_review
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Labelling Program Review

<<DOC_CONTROL>>

> The labelling program creates value only if labels actually stick across the estate — systems where coverage drops, transformations that strip labels, training gaps where users mis-apply, and new platforms that came online without labelling enabled all signal the program is leaking. The review captures the planned-interval check: coverage-trend analysis, drop-detection, scheme-alignment audit, training-effectiveness sample, and resulting program adjustments. Annual cadence — cascades from A.5.12 classification scheme review

<!-- TABLE-COLUMNS leaf:req:A.5.13:labelling_program_review -->
<!-- column: item:A.5.13:rev_date -->
<!-- column: item:A.5.13:rev_reviewer -->
<!-- column: item:A.5.13:rev_coverage_trend -->
<!-- column: item:A.5.13:rev_persistence_audit -->
<!-- column: item:A.5.13:rev_scheme_alignment -->
<!-- column: item:A.5.13:rev_training_sample -->
<!-- column: item:A.5.13:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically review and improve your labelling program by tracking coverage, identifying gaps, and ensuring your labelling practices stay effective and aligned with your policies.

## When to use it

Use this template once a year to check how well your labelling program is working, especially after your annual classification scheme review or if you notice issues with label coverage or accuracy.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this review from scratch, depending on how many systems you need to check and how much information you need to gather for each required section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.13:labelling_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Trend | Rev Persistence Audit | Rev Scheme Alignment | Rev Training Sample | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.13:labelling_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.13:rev_date>>
_Why: 27002:5.13 — periodic_

> _Standard text:_ Review date within the planned annual interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.13:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec + Data Protection Officer where PII overlays apply jointly)

<<GUIDANCE>>

### Rev Coverage Trend

<<MUST item:A.5.13:rev_coverage_trend>>
_Why: Program effectiveness_

> _Standard text:_ Coverage-trend analysis (per-system coverage % delta since last review; investigate any drop)

<<GUIDANCE>>

### Rev Persistence Audit

<<MUST item:A.5.13:rev_persistence_audit>>
_Why: 27002:5.13 — persistence_

> _Standard text:_ Persistence audit (sample of transformed/exported items re-checked — does the label survive copy/export/conversion?)

<<GUIDANCE>>

### Rev Scheme Alignment

<<MUST item:A.5.13:rev_scheme_alignment>>
_Why: 27002:5.13 + cross-link to [[A.5.12]]_

> _Standard text:_ Scheme-alignment audit (labels in active systems match A.5.12 levels; drift triggers re-mapping)

<<GUIDANCE>>

### Rev Training Sample

<<MUST item:A.5.13:rev_training_sample>>
_Why: 27002:5.13 — implemented_

> _Standard text:_ Training-effectiveness sample (small sample of newly created items per level — labelled correctly?)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.13:rev_actions>>
_Why: 27002:5.13 — program adjustments_

> _Standard text:_ Action items captured (e.g. extend labelling to platform X, tighten automation, refresh training module, address drop)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Tooling Landscape

<<SHOULD item:A.5.13:rev_tooling_landscape>>
_Why: Audit defensibility_

> _Standard text:_ Tooling-landscape check (vendor releases, new sensitivity-label features, capability gaps the program should consider)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.13:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
