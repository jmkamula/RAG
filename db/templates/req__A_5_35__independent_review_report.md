---
leaf_id: req:A.5.35:independent_review_report
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: audit_report
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 3
---

# Independent Information Security Review Report

> A.5.35 requires the organisation's approach to information security to be reviewed independently at planned intervals (or on significant change). Each review report evidences the activity for one review cycle: reviewer independence demonstrated, scope covering people/processes/technology, findings recorded with severity, recommendations stated, management response documented. The review schedule register, program meta-review and finding-response register are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Independence of the reviewer demonstrated (separate function, external auditor, or rotating internal reviewer with no operational ownership of the reviewed areas)

<<MUST item:A.5.35:independence>>
_Why: 27002:5.35 — reviewed independently_

<<TEXT>>

## 2. Scope covers people, processes, and technologies (not just one dimension — auditor-defensible reviews must touch all three)

<<MUST item:A.5.35:scope>>
_Why: 27002:5.35 — including people, processes and technologies_

<<TEXT>>

## 3. Review date and period covered (start/end of the review activity + observation window)

<<MUST item:A.5.35:review_date>>
_Why: 27002:5.35 — planned intervals_

<<TEXT>>

## 4. Findings listed with severity (concrete, evidenced, traceable to the underlying observation — not just generic recommendations)

<<MUST item:A.5.35:findings>>
_Why: 27002:5.35 — review_

<<TEXT>>

## 5. Recommendations stated (with priority and owner suggestion — actionable, not abstract)

<<MUST item:A.5.35:recommendations>>
_Why: 27002:5.35 — review_

<<TEXT>>

## 6. Management response to findings (accept / remediate / transfer / risk-accept with rationale); response is documented IN the report, not deferred

<<MUST item:A.5.35:management_response>>
_Why: Closes the loop_

<<TEXT>>

## 7. Significant-change trigger check stated (whether this review was triggered by planned cadence OR by a significant change — M&A, major architectural shift, regulatory upheaval, major breach)

<<MUST item:A.5.35:significant_change_check>>
_Why: 27002:5.35 — planned intervals or on significant change_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External auditor accreditation or internal reviewer qualifications stated (CISA, ISO 27001 LA/LI, sector-specific credentials)

<<SHOULD item:A.5.35:reviewer_credentials>>
_Why: Reviewer credibility_

<<TEXT>>

### 2. Comparison or movement from prior review's findings (open / closed / aged) — proves the program returns value across cycles

<<SHOULD item:A.5.35:prior_review_compare>>
_Why: Progress tracking_

<<TEXT>>

### 3. Executive summary section addressed to leadership (audit-defensible communication of overall posture, not just the detailed findings list)

<<SHOULD item:A.5.35:executive_summary>>
_Why: Stakeholder communication_

<<TEXT>>
