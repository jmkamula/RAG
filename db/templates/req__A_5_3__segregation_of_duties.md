---
leaf_id: req:A.5.3:segregation_of_duties
control_ref: A.5.3
standard_id: ISO27001:2022
evidence_type: segregation_matrix
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Segregation of Duties Matrix

<<DOC_CONTROL>>

> A.5.3 requires conflicting duties and conflicting areas of responsibility to be segregated. The matrix identifies conflict pairs and the mechanism preventing one person from holding both. Approval, communication and periodic review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.3:segregation_of_duties -->
<!-- column: item:A.5.3:conflict_pairs -->
<!-- column: item:A.5.3:separation_method -->
<!-- column: item:A.5.3:compensating -->
<!-- column: item:A.5.3:coverage_scope -->
<!-- column: item:A.5.3:owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly map out which job roles or individuals should not have overlapping responsibilities, reducing the risk of errors or fraud by ensuring no one person controls conflicting tasks.

## When to use it

Use this matrix whenever you need to document and review how duties are separated within your organization, and update it whenever roles or responsibilities change to keep it accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of roles and conflict pairs you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.3:segregation_of_duties -->
| Conflict Pairs | Separation Method | Compensating | Coverage Scope | Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.3:segregation_of_duties -->

## Column guidance — what to fill in

### Conflict Pairs

<<MUST item:A.5.3:conflict_pairs>>
_Why: 27002:5.3a_

> _Standard text:_ Conflicting duty pairs identified (e.g. requestor vs approver, developer vs production deployer, vendor relationship vs payment authorisation)

<<GUIDANCE>>

### Separation Method

<<MUST item:A.5.3:separation_method>>
_Why: 27002:5.3b_

> _Standard text:_ Separation mechanism stated per pair (different people, different systems, four-eyes, time-bound role swaps)

<<GUIDANCE>>

### Compensating

<<MUST item:A.5.3:compensating>>
_Why: 27002:5.3c — small organisations_

> _Standard text:_ Compensating controls where full separation is not feasible (small-team exceptions, supervisory review, automated logging)

<<GUIDANCE>>

### Coverage Scope

<<MUST item:A.5.3:coverage_scope>>
_Why: 27002:5.3_

> _Standard text:_ Scope of coverage stated (functional areas, systems, processes covered by the matrix)

<<GUIDANCE>>

### Owner

<<MUST item:A.5.3:owner>>
_Why: Accountability — Clause 5.3_

> _Standard text:_ Named owner of the matrix accountable for its maintenance

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Exception Process

<<SHOULD item:A.5.3:exception_process>>
_Why: Real-world flexibility_

> _Standard text:_ Exception process for temporary or unavoidable conflicts (e.g. on-call coverage breaking normal separation)

<<GUIDANCE>>

### A52 Link

<<SHOULD item:A.5.3:a52_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to A.5.2 responsibility matrix — conflicts identified in A.5.2 inform A.5.3 separation decisions

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
