---
leaf_id: req:A.7.3.6:acr_request_register
control_ref: A.7.3.6
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Access / Correction / Erasure Request Register

<<DOC_CONTROL>>

> Per-request row — audit trail of each ACR request with type, resolution, and SLA compliance. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:A.7.3.6:acr_request_register -->
<!-- column: item:A.7.3.6:reg_request_id -->
<!-- column: item:A.7.3.6:reg_subject_id -->
<!-- column: item:A.7.3.6:reg_request_type -->
<!-- column: item:A.7.3.6:reg_received_date -->
<!-- column: item:A.7.3.6:reg_outcome -->
<!-- column: item:A.7.3.6:reg_propagation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of every request you receive to access, correct, or erase personal data, along with how each was handled and whether you met your response deadlines.

## When to use it

Use this register whenever someone asks to access, correct, or erase their personal data, and update it at least once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register from scratch will take about 1 to 1.5 hours for the initial required elements, plus an additional 10-15 minutes for each new request you log.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.6:acr_request_register -->
| Reg Request Id | Reg Subject Id | Reg Request Type | Reg Received Date | Reg Outcome | Reg Propagation |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.6:acr_request_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:A.7.3.6:reg_request_id>>
_Why: Audit trail_

> _Standard text:_ Unique request identifier per row

<<GUIDANCE>>

### Reg Subject Id

<<MUST item:A.7.3.6:reg_subject_id>>
_Why: Traceability_

> _Standard text:_ Subject identifier per row (post identity verification)

<<GUIDANCE>>

### Reg Request Type

<<MUST item:A.7.3.6:reg_request_type>>
_Why: §7.3.6_

> _Standard text:_ Request type per row (access / correction / erasure)

<<GUIDANCE>>

### Reg Received Date

<<MUST item:A.7.3.6:reg_received_date>>
_Why: Currency_

> _Standard text:_ Received date + resolution date per row (SLA measurable)

<<GUIDANCE>>

### Reg Outcome

<<MUST item:A.7.3.6:reg_outcome>>
_Why: §7.3.6 — inform of what changes made_

> _Standard text:_ Outcome per row (granted / refused with reason / partial)

<<GUIDANCE>>

### Reg Propagation

<<MUST item:A.7.3.6:reg_propagation>>
_Why: §7.3.6 — pass to third parties_

> _Standard text:_ Propagation status per row (systems updated / third parties notified)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Verification Method

<<SHOULD item:A.7.3.6:reg_verification_method>>
_Why: Defensibility_

> _Standard text:_ Identity verification method used

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
