---
leaf_id: req:A.5.36:compliance_program_meta_review
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

# Periodic Compliance Review Program Meta-Review

> The compliance review program itself needs review — is the catalogue current, is the method choice right, are findings being closed, are continuous-compliance signals being used effectively? The meta-review evidences periodic self-assessment and the resulting adjustments

<!-- TABLE-COLUMNS leaf:req:A.5.36:compliance_program_meta_review -->
<!-- column: item:A.5.36:pgm_date -->
<!-- column: item:A.5.36:pgm_reviewer -->
<!-- column: item:A.5.36:pgm_catalogue_check -->
<!-- column: item:A.5.36:pgm_coverage -->
<!-- column: item:A.5.36:pgm_closure -->
<!-- column: item:A.5.36:pgm_method_review -->
<!-- column: item:A.5.36:pgm_outcome -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.36:compliance_program_meta_review -->
| Pgm Date | Pgm Reviewer | Pgm Catalogue Check | Pgm Coverage | Pgm Closure | Pgm Method Review | Pgm Outcome |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.36:compliance_program_meta_review -->

## Column guidance — what to fill in

### Pgm Date

<<MUST item:A.5.36:pgm_date>>
_Why: 27002:5.36 — periodic_

> _Standard text:_ Meta-review date within the planned interval

### Pgm Reviewer

<<MUST item:A.5.36:pgm_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (compliance program owner + InfoSec lead jointly)

### Pgm Catalogue Check

<<MUST item:A.5.36:pgm_catalogue_check>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

> _Standard text:_ Catalogue currency check — did new policies / rules / standards land without entering the schedule? are retired items still scheduled?

### Pgm Coverage

<<MUST item:A.5.36:pgm_coverage>>
_Why: 27002:5.36 — regularly_

> _Standard text:_ Coverage check — did the schedule actually run? what fraction of catalogue reviewed in period?

### Pgm Closure

<<MUST item:A.5.36:pgm_closure>>
_Why: Operational discipline_

> _Standard text:_ Findings-closure rate across the program (open / aged / closed)

### Pgm Method Review

<<MUST item:A.5.36:pgm_method_review>>
_Why: 27002:5.36 — adjustments_

> _Standard text:_ Method effectiveness review — are the chosen methods surfacing real nonconformities, or is the program rubber-stamping?

### Pgm Outcome

<<MUST item:A.5.36:pgm_outcome>>
_Why: 27002:5.36 — adjustments_

> _Standard text:_ Cadence-adjustment or method-adjustment decisions (tighten / loosen / change method per item type)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Pgm A535 Alignment

<<SHOULD item:A.5.36:pgm_a535_alignment>>
_Why: Cross-control coherence_

> _Standard text:_ Alignment check with A.5.35 independent review program (shared reviewer pool? shared finding register? leverage opportunities)

### Pgm Next Date

<<SHOULD item:A.5.36:pgm_next_date>>
_Why: Planning_

> _Standard text:_ Next planned meta-review date stated
