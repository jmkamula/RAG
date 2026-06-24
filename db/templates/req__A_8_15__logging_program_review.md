---
leaf_id: req:A.8.15:logging_program_review
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Logging Program Review

> Periodic verification — source-register currency, silent-source detection, retention compliance, integrity-verification spot-checks (freshness=180; threat landscape volatile)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.15:rev_date>>
_Why: 27002:8.15 — periodic_

<<TEXT>>

## 2. Reviewer identity (Security Operations + Infrastructure)

<<MUST item:A.8.15:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Silent-source detection — sources missing recent events triaged

<<MUST item:A.8.15:rev_silent_sources>>
_Why: Detection gap closure_

<<TEXT>>

## 4. Retention compliance check (no premature deletion; no over-retention of personal data)

<<MUST item:A.8.15:rev_retention_compliance>>
_Why: 27002:8.15 — stored_

<<TEXT>>

## 5. Integrity-verification spot-check (hash chain or signature validates against retained logs)

<<MUST item:A.8.15:rev_integrity_check>>
_Why: Forensic defensibility_

<<TEXT>>

## 6. Findings propagated to procedure / source register / scope

<<MUST item:A.8.15:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.15:rev_next_date>>
_Why: Planning_

<<TEXT>>
