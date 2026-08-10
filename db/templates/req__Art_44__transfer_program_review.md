---
leaf_id: req:Art.44:transfer_program_review
control_ref: Art.44
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Transfer Program Review

<<DOC_CONTROL>>

> Annual verification — every active transfer has a current Art.45/46/47/49 mechanism, register reflects current vendor landscape, Schrems II-style TIA considerations applied (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.44:transfer_program_review -->
<!-- column: item:Art.44:rev_date -->
<!-- column: item:Art.44:rev_reviewer -->
<!-- column: item:Art.44:rev_register_currency -->
<!-- column: item:Art.44:rev_mechanism_validity -->
<!-- column: item:Art.44:rev_silent_transfer_sweep -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all your active data transfers, making sure each one has the right legal safeguards and is up to date with GDPR requirements.

## When to use it

Use this template whenever you need to review your international data transfers, typically once a year, to ensure your records and risk assessments are current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes filling this out from scratch, depending on how many transfers you need to document and review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.44:transfer_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Mechanism Validity | Rev Silent Transfer Sweep |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.44:transfer_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.44:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.44:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel + procurement)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:Art.44:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency — every flagged transfer in last-assessment freshness window

<<GUIDANCE>>

### Rev Mechanism Validity

<<MUST item:Art.44:rev_mechanism_validity>>
_Why: Art.44-49_

> _Standard text:_ Mechanism-validity sample — Art.45 adequacy decisions, Art.46 SCCs, Art.47 BCRs all current versions / approvals

<<GUIDANCE>>

### Rev Silent Transfer Sweep

<<MUST item:Art.44:rev_silent_transfer_sweep>>
_Why: Drift detection_

> _Standard text:_ Silent-transfer sweep — verify no new vendor or service-shape change created an unflagged transfer

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.44:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
