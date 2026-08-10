---
leaf_id: req:Art.10:criminal_data_program_review
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Criminal Data Program Review

<<DOC_CONTROL>>

> Annual verification that every Art.10 activity still has a current Member State law basis, safeguards remain in force, retention limits are being honoured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.10:criminal_data_program_review -->
<!-- column: item:Art.10:rev_date -->
<!-- column: item:Art.10:rev_reviewer -->
<!-- column: item:Art.10:rev_law_currency -->
<!-- column: item:Art.10:rev_retention_audit -->
<!-- column: item:Art.10:rev_access_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review your use of criminal data, ensuring you have a lawful basis, proper safeguards, and up-to-date retention practices in line with GDPR Article 10.

## When to use it

Use this template if your organization processes criminal data and your activities match specific legal triggers. It should be completed about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 1 to 1.5 hours filling this out from scratch, depending on the number of activities you need to review and record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.10:criminal_data_program_review -->
| Rev Date | Rev Reviewer | Rev Law Currency | Rev Retention Audit | Rev Access Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.10:criminal_data_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.10:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.10:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

<<GUIDANCE>>

### Rev Law Currency

<<MUST item:Art.10:rev_law_currency>>
_Why: Currency_

> _Standard text:_ Member State law currency — every cited law still in force; any new MS authorisations swept in

<<GUIDANCE>>

### Rev Retention Audit

<<MUST item:Art.10:rev_retention_audit>>
_Why: Art.10 — appropriate safeguards_

> _Standard text:_ Retention audit — past-retention-limit records purged

<<GUIDANCE>>

### Rev Access Audit

<<MUST item:Art.10:rev_access_audit>>
_Why: Art.10_

> _Standard text:_ Access audit — restricted-access requirements being enforced (no broad access to criminal-data stores)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.10:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
