---
leaf_id: req:A.5.28:evidence_program_review
control_ref: A.5.28
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Evidence-Handling Program Review

> The evidence-handling program creates value only if it actually holds up — chain-of-custody integrity must survive scrutiny by regulators and counsel. The review captures the planned-interval check: integrity-verification results, custody-incident analysis, competence/training status of authorised personnel, alignment with current legal-admissibility standards, and resulting program adjustments. Annual cadence — evidence-handling discipline is forensically stable

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned annual interval

<<MUST item:A.5.28:rev_date>>
_Why: 27002:5.28 — periodic_

<<TEXT>>

## 2. Reviewer identity (InfoSec lead + legal/compliance counsel jointly)

<<MUST item:A.5.28:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Integrity-verification audit (sample of register rows re-hashed; mismatches investigated)

<<MUST item:A.5.28:rev_integrity_audit>>
_Why: 27002:5.28 — preservation integrity_

<<TEXT>>

## 4. Custody-incident analysis (any broken-seal events, missing-handover signatures, unauthorised access flagged for review)

<<MUST item:A.5.28:rev_custody_incidents>>
_Why: 27002:5.28 — chain of custody_

<<TEXT>>

## 5. Competence/training status of authorised personnel reviewed (certifications current, new staff onboarded properly)

<<MUST item:A.5.28:rev_competence>>
_Why: 27002:5.28 — competence_

<<TEXT>>

## 6. Alignment-with-current-legal-standards check (jurisdictional updates, regulator guidance, case law shifts considered)

<<MUST item:A.5.28:rev_legal_alignment>>
_Why: 27002:5.28 — admissibility_

<<TEXT>>

## 7. Action items captured for the program (e.g. retrain on new tooling, update jurisdiction tagging, refresh legal-counsel input)

<<MUST item:A.5.28:rev_actions>>
_Why: 27002:5.28 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External benchmark or industry-practice input considered (peer review, forensic-community guidance)

<<SHOULD item:A.5.28:rev_external_input>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.28:rev_next_date>>
_Why: Planning_

<<TEXT>>
