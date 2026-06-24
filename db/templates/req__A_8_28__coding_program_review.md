---
leaf_id: req:A.8.28:coding_program_review
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Secure Coding Program Review

> Annual verification — finding-pattern trending, tooling currency, language-standard updates (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.28:rev_date>>
_Why: 27002:8.28 — periodic_

<<TEXT>>

## 2. Reviewer identity (Engineering leads + Security Champions)

<<MUST item:A.8.28:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Finding-pattern trending (recurring patterns → training / tooling action)

<<MUST item:A.8.28:rev_finding_patterns>>
_Why: Continuous improvement_

<<TEXT>>

## 4. Tooling-stack currency (SAST / SCA rules current; new tooling adopted)

<<MUST item:A.8.28:rev_tooling_currency>>
_Why: 27002:8.28 — applied_

<<TEXT>>

## 5. Findings propagated to language standards / training

<<MUST item:A.8.28:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.28:rev_next_date>>
_Why: Planning_

<<TEXT>>
