---
leaf_id: req:A.5.3:segregation_of_duties
control_ref: A.5.3
standard_id: ISO27001:2022
evidence_type: segregation_matrix
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Segregation of Duties Matrix

> A.5.3 requires conflicting duties and conflicting areas of responsibility to be segregated. The matrix identifies conflict pairs and the mechanism preventing one person from holding both. Approval, communication and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Conflicting duty pairs identified (e.g. requestor vs approver, developer vs production deployer, vendor relationship vs payment authorisation)

<<MUST item:A.5.3:conflict_pairs>>
_Why: 27002:5.3a_

<<TEXT>>

## 2. Separation mechanism stated per pair (different people, different systems, four-eyes, time-bound role swaps)

<<MUST item:A.5.3:separation_method>>
_Why: 27002:5.3b_

<<TEXT>>

## 3. Compensating controls where full separation is not feasible (small-team exceptions, supervisory review, automated logging)

<<MUST item:A.5.3:compensating>>
_Why: 27002:5.3c — small organisations_

<<TEXT>>

## 4. Scope of coverage stated (functional areas, systems, processes covered by the matrix)

<<MUST item:A.5.3:coverage_scope>>
_Why: 27002:5.3_

<<TEXT>>

## 5. Named owner of the matrix accountable for its maintenance

<<MUST item:A.5.3:owner>>
_Why: Accountability — Clause 5.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception process for temporary or unavoidable conflicts (e.g. on-call coverage breaking normal separation)

<<SHOULD item:A.5.3:exception_process>>
_Why: Real-world flexibility_

<<TEXT>>

### 2. Cross-link to A.5.2 responsibility matrix — conflicts identified in A.5.2 inform A.5.3 separation decisions

<<SHOULD item:A.5.3:a52_link>>
_Why: Cross-control coherence_

<<TEXT>>
