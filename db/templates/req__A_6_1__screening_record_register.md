---
leaf_id: req:A.6.1:screening_record_register
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Per-Candidate Screening Record Register

> The operational catalogue of screening events. Every candidate / new hire / re-screened employee has a row: candidate identifier, role tier, checks performed, outcome, decision authority, decision date. Drives the audit-defensibility 'show me you screened this person before they got access' question

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-record candidate identifier (links to identity register A.5.16 once hired; anonymised pre-hire to comply with data minimisation)

<<MUST item:A.6.1:reg_candidate_id>>
_Why: Accountability_

<<TEXT>>

## 2. Role tier per record (drives the proportional check-depth applied; junior / standard / sensitive / privileged)

<<MUST item:A.6.1:reg_role_tier>>
_Why: 27002:6.1a — proportional_

<<TEXT>>

## 3. Checks performed per record (identity / employment-history / education / criminal / financial / sanctions — actual checks run, not just planned)

<<MUST item:A.6.1:reg_checks_performed>>
_Why: 27002:6.1a — verification_

<<TEXT>>

## 4. Outcome per record (cleared / cleared-with-conditions / blocked / superseded by waiver)

<<MUST item:A.6.1:reg_outcome>>
_Why: 27002:6.1 — decision_

<<TEXT>>

## 5. Decision date per record (proves the screening completed BEFORE access was granted per A.5.18)

<<MUST item:A.6.1:reg_decision_date>>
_Why: Audit defensibility_

<<TEXT>>

## 6. Authoriser per record (named individual making the accept/reject decision)

<<MUST item:A.6.1:reg_authoriser>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Last rescreen date per record (for roles with ongoing-check obligations)

<<SHOULD item:A.6.1:reg_rescreen_date>>
_Why: Operational discipline_

<<TEXT>>

### 2. Third-party provider reference per record where used

<<SHOULD item:A.6.1:reg_provider_ref>>
_Why: Traceability_

<<TEXT>>
