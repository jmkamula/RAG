---
leaf_id: req:A.5.36:compliance_review_record
control_ref: A.5.36
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Compliance Review Records (Policies, Rules, Standards)

> A.5.36 requires regular review of compliance with the InfoSec policy, topic-specific policies, rules and standards. Each review record evidences the activity for one cycle: schedule honoured, scope covered, method used, findings recorded, corrective actions opened. The schedule register, program meta-review and nonconformity register are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Schedule honoured for this cycle (each planned policy/rule/standard actually reviewed in the period; gaps flagged for next cycle)

<<MUST item:A.5.36:schedule>>
_Why: 27002:5.36 — regularly reviewed_

<<TEXT>>

## 2. Scope of this cycle (which policies / rules / standards were reviewed — typically a slice of the full catalogue if rotated across cycles)

<<MUST item:A.5.36:scope>>
_Why: 27002:5.36 — InfoSec policy + topic-specific policies + rules + standards_

<<TEXT>>

## 3. Method used per item (control sampling, formal audit, automated check, attestation, walkthrough); rationale for method choice given the item type

<<MUST item:A.5.36:method>>
_Why: 27002:5.36 — reviewed_

<<TEXT>>

## 4. Findings recorded per review with severity (compliance vs. nonconformity vs. opportunity-for-improvement; concrete, evidenced)

<<MUST item:A.5.36:findings>>
_Why: 27002:5.36 — review_

<<TEXT>>

## 5. Corrective actions opened per nonconformity finding (with owner, target date) — feeds the nonconformity register

<<MUST item:A.5.36:corrective_actions>>
_Why: Closes the loop_

<<TEXT>>

## 6. Named owner of this review cycle (the person who ran it — typically compliance lead or designate)

<<MUST item:A.5.36:owner>>
_Why: Accountability_

<<TEXT>>

## 7. Review date and period covered (start/end of the review activity)

<<MUST item:A.5.36:review_date>>
_Why: 27002:5.36 — regularly_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Continuous-compliance monitoring tooling output considered (where used — config drift, control health checks, CSPM signal)

<<SHOULD item:A.5.36:continuous_compliance>>
_Why: Scale and timeliness_

<<TEXT>>

### 2. Method evidence retained (sample selection notes, attestation responses, audit working papers) for audit defensibility

<<SHOULD item:A.5.36:method_evidence>>
_Why: Audit defensibility_

<<TEXT>>
