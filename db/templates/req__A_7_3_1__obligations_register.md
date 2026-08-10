---
leaf_id: req:A.7.3.1:obligations_register
control_ref: A.7.3.1
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Applicable Obligations Register

<<DOC_CONTROL>>

> Per-obligation row — enumeration of every subject-rights obligation the org is subject to, with citation, jurisdiction, fulfilment channel, and response-time SLA. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.1:obligations_register -->
<!-- column: item:A.7.3.1:reg_obligation_id -->
<!-- column: item:A.7.3.1:reg_citation -->
<!-- column: item:A.7.3.1:reg_jurisdiction -->
<!-- column: item:A.7.3.1:reg_fulfilment_channel -->
<!-- column: item:A.7.3.1:reg_sla -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of every privacy-related obligation your organization must meet, including details like legal citations, jurisdictions, and response deadlines, all in one organized table.

## When to use it

Use this register when your organization is subject to privacy obligations that match specific criteria, and plan to update it about once a year to keep the information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each obligation you list, so the total time depends on how many obligations your organization needs to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.1:obligations_register -->
| Reg Obligation Id | Reg Citation | Reg Jurisdiction | Reg Fulfilment Channel | Reg Sla |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.1:obligations_register -->

## Column guidance — what to fill in

### Reg Obligation Id

<<MUST item:A.7.3.1:reg_obligation_id>>
_Why: Referenceability_

> _Standard text:_ Unique obligation identifier per row

<<GUIDANCE>>

### Reg Citation

<<MUST item:A.7.3.1:reg_citation>>
_Why: §7.3.1 — determine and document_

> _Standard text:_ Legal / regulatory / business citation per row

<<GUIDANCE>>

### Reg Jurisdiction

<<MUST item:A.7.3.1:reg_jurisdiction>>
_Why: §7.3.1 — vary from one jurisdiction_

> _Standard text:_ Applicable jurisdiction per row

<<GUIDANCE>>

### Reg Fulfilment Channel

<<MUST item:A.7.3.1:reg_fulfilment_channel>>
_Why: §7.3.1 — provide the means_

> _Standard text:_ Fulfilment channel per row (which A.7.3.2-10 procedure handles it)

<<GUIDANCE>>

### Reg Sla

<<MUST item:A.7.3.1:reg_sla>>
_Why: §7.3.1 — timely manner_

> _Standard text:_ Response-time SLA per row

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Last Reviewed

<<SHOULD item:A.7.3.1:reg_last_reviewed>>
_Why: Currency_

> _Standard text:_ Last review date per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
