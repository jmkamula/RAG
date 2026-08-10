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
table_shape: true
---

# Periodic Evidence-Handling Program Review

<<DOC_CONTROL>>

> The evidence-handling program creates value only if it actually holds up — chain-of-custody integrity must survive scrutiny by regulators and counsel. The review captures the planned-interval check: integrity-verification results, custody-incident analysis, competence/training status of authorised personnel, alignment with current legal-admissibility standards, and resulting program adjustments. Annual cadence — evidence-handling discipline is forensically stable

<!-- TABLE-COLUMNS leaf:req:A.5.28:evidence_program_review -->
<!-- column: item:A.5.28:rev_date -->
<!-- column: item:A.5.28:rev_reviewer -->
<!-- column: item:A.5.28:rev_integrity_audit -->
<!-- column: item:A.5.28:rev_custody_incidents -->
<!-- column: item:A.5.28:rev_competence -->
<!-- column: item:A.5.28:rev_legal_alignment -->
<!-- column: item:A.5.28:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document a thorough review of your evidence-handling program, including checks on chain-of-custody, incident analysis, staff training, and legal compliance. It’s designed to show your program’s reliability to regulators and legal counsel.

## When to use it

Use this template once a year to record your scheduled review of evidence-handling practices. It applies to all environments where evidence integrity and legal standards matter.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, depending on the amount of detail and the number of incidents or changes to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.28:evidence_program_review -->
| Rev Date | Rev Reviewer | Rev Integrity Audit | Rev Custody Incidents | Rev Competence | Rev Legal Alignment | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.28:evidence_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.28:rev_date>>
_Why: 27002:5.28 — periodic_

> _Standard text:_ Review date within the planned annual interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.28:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec lead + legal/compliance counsel jointly)

<<GUIDANCE>>

### Rev Integrity Audit

<<MUST item:A.5.28:rev_integrity_audit>>
_Why: 27002:5.28 — preservation integrity_

> _Standard text:_ Integrity-verification audit (sample of register rows re-hashed; mismatches investigated)

<<GUIDANCE>>

### Rev Custody Incidents

<<MUST item:A.5.28:rev_custody_incidents>>
_Why: 27002:5.28 — chain of custody_

> _Standard text:_ Custody-incident analysis (any broken-seal events, missing-handover signatures, unauthorised access flagged for review)

<<GUIDANCE>>

### Rev Competence

<<MUST item:A.5.28:rev_competence>>
_Why: 27002:5.28 — competence_

> _Standard text:_ Competence/training status of authorised personnel reviewed (certifications current, new staff onboarded properly)

<<GUIDANCE>>

### Rev Legal Alignment

<<MUST item:A.5.28:rev_legal_alignment>>
_Why: 27002:5.28 — admissibility_

> _Standard text:_ Alignment-with-current-legal-standards check (jurisdictional updates, regulator guidance, case law shifts considered)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.28:rev_actions>>
_Why: 27002:5.28 — program adjustments_

> _Standard text:_ Action items captured for the program (e.g. retrain on new tooling, update jurisdiction tagging, refresh legal-counsel input)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev External Input

<<SHOULD item:A.5.28:rev_external_input>>
_Why: Audit defensibility_

> _Standard text:_ External benchmark or industry-practice input considered (peer review, forensic-community guidance)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.28:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
