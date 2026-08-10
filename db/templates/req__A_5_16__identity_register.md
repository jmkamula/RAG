---
leaf_id: req:A.5.16:identity_register
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Identity Register

<<DOC_CONTROL>>

> A.5.16 requires every identity to be visible to the security function — invisible identities are the ones that go stale, get reused, or persist past their owner's departure. The register catalogues every active identity (human + service + shared + non-human): identity id, type, owner, status, created/modified/last-used timestamps. It is the operational record that proves identity hygiene is org-wide, not just on the systems IT remembered to onboard to the IAM platform

<!-- TABLE-COLUMNS leaf:req:A.5.16:identity_register -->
<!-- column: item:A.5.16:reg_identity_id -->
<!-- column: item:A.5.16:reg_identity_type -->
<!-- column: item:A.5.16:reg_owner -->
<!-- column: item:A.5.16:reg_status -->
<!-- column: item:A.5.16:reg_created_modified -->
<!-- column: item:A.5.16:reg_last_used -->
<!-- column: item:A.5.16:reg_hr_link -->
<!-- column: item:A.5.16:reg_service_expiry -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a complete and up-to-date list of all identities in your organization, making it easier to manage who has access and to demonstrate good security practices.

## When to use it

Use this register at all times to track every identity in your environment, updating it whenever new identities are created, changed, or removed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours setting up the initial register, plus additional time for each identity you add; ongoing updates will take just a few minutes per change.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.16:identity_register -->
| Reg Identity Id | Reg Identity Type | Reg Owner | Reg Status | Reg Created Modified | Reg Last Used | Reg Hr Link | Reg Service Expiry |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.16:identity_register -->

## Column guidance — what to fill in

### Reg Identity Id

<<MUST item:A.5.16:reg_identity_id>>
_Why: 27002:5.16 — visibility_

> _Standard text:_ Each active identity captured with a unique identifier (employee id, contractor id, service-account id, shared-account id)

<<GUIDANCE>>

### Reg Identity Type

<<MUST item:A.5.16:reg_identity_type>>
_Why: 27002:5.16 — managed (all types)_

> _Standard text:_ Identity type per row (human_employee / human_contractor / service / shared / system_account) — drives policy variant applied

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.5.16:reg_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per row (human owner accountable for THIS identity — even for service accounts, must be a human)

<<GUIDANCE>>

### Reg Status

<<MUST item:A.5.16:reg_status>>
_Why: 27002:5.16 — lifecycle tracking_

> _Standard text:_ Status per row (active / suspended / disabled / pending_termination) updated as lifecycle events fire

<<GUIDANCE>>

### Reg Created Modified

<<MUST item:A.5.16:reg_created_modified>>
_Why: Audit trail_

> _Standard text:_ Created and last-modified timestamps per row

<<GUIDANCE>>

### Reg Last Used

<<MUST item:A.5.16:reg_last_used>>
_Why: 27002:5.16 — drift detection_

> _Standard text:_ Last-used timestamp per row (drives auto-suspend at N days idle; orphan detection)

<<GUIDANCE>>

### Reg Hr Link

<<MUST item:A.5.16:reg_hr_link>>
_Why: 27002:5.16 + cross-link to [[A.5.11]]_

> _Standard text:_ HR-record link per row for human identities (joiner/leaver triggers cascade automatically — no manual sync)

<<GUIDANCE>>

### Reg Service Expiry

<<MUST item:A.5.16:reg_service_expiry>>
_Why: 27002:5.16 — managed (service-account discipline)_

> _Standard text:_ Expiry date per row for service / shared / temporary identities (forces deliberate renewal rather than indefinite drift)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Attestation Due

<<SHOULD item:A.5.16:reg_attestation_due>>
_Why: Drift prevention_

> _Standard text:_ Next attestation date per row (drives the periodic recertification cycle)

<<GUIDANCE>>

### Reg Risk Tag

<<SHOULD item:A.5.16:reg_risk_tag>>
_Why: Risk-based attention_

> _Standard text:_ Risk tag per row where the identity has elevated privileges or sensitive scope (drives faster-cadence review)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
