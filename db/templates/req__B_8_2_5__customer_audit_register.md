---
leaf_id: req:B.8.2.5:customer_audit_register
control_ref: B.8.2.5
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Customer Audit + Information Support Register

<<DOC_CONTROL>>

> Per-support-request row — the register of customer audits + information requests + responses. Annual refresh (freshness=365).

<!-- TABLE-COLUMNS leaf:req:B.8.2.5:customer_audit_register -->
<!-- column: item:B.8.2.5:reg_request_id -->
<!-- column: item:B.8.2.5:reg_customer_id -->
<!-- column: item:B.8.2.5:reg_request_type -->
<!-- column: item:B.8.2.5:reg_response_date -->
<!-- column: item:B.8.2.5:reg_response_summary -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of customer audit and information requests, along with your responses, in a clear and organized way. It's designed to support privacy compliance and make annual reviews easier.

## When to use it

Use this register whenever you receive a customer audit or information request that matches certain criteria for your organization. Update it at least once a year to ensure your records stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to complete the required sections for each new entry, with additional time needed as you add more requests over time.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.5:customer_audit_register -->
| Reg Request Id | Reg Customer Id | Reg Request Type | Reg Response Date | Reg Response Summary |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.5:customer_audit_register -->

## Column guidance — what to fill in

### Reg Request Id

<<MUST item:B.8.2.5:reg_request_id>>
_Why: Traceability_

> _Standard text:_ Unique request identifier per row

<<GUIDANCE>>

### Reg Customer Id

<<MUST item:B.8.2.5:reg_customer_id>>
_Why: Scope_

> _Standard text:_ Requesting customer identifier per row

<<GUIDANCE>>

### Reg Request Type

<<MUST item:B.8.2.5:reg_request_type>>
_Why: §8.2.5 — appropriate information_

> _Standard text:_ Request type per row (audit / certification-share / DPIA input / DSAR support / configuration query)

<<GUIDANCE>>

### Reg Response Date

<<MUST item:B.8.2.5:reg_response_date>>
_Why: Currency_

> _Standard text:_ Response date per row (vs stated SLA)

<<GUIDANCE>>

### Reg Response Summary

<<MUST item:B.8.2.5:reg_response_summary>>
_Why: Audit trail_

> _Standard text:_ Response summary per row (what was shared / rationale for redaction if any)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Customer Satisfaction

<<SHOULD item:B.8.2.5:reg_customer_satisfaction>>
_Why: Continuous improvement_

> _Standard text:_ Customer satisfaction / follow-up per row

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
