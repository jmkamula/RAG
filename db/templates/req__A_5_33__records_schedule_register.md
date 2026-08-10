---
leaf_id: req:A.5.33:records_schedule_register
control_ref: A.5.33
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Records Schedule (Per-Class Retention and Protection Register)

<<DOC_CONTROL>>

> The operational register at the heart of A.5.33. Without a records schedule listing every record class with retention, driver, owner and protection assignment, the policy is theoretical. The schedule is queried at audit time to demonstrate that the organisation knows what records it holds, why it holds them, and for how long

<!-- TABLE-COLUMNS leaf:req:A.5.33:records_schedule_register -->
<!-- column: item:A.5.33:records_schedule -->
<!-- column: item:A.5.33:retention_periods -->
<!-- column: item:A.5.33:retention_drivers -->
<!-- column: item:A.5.33:reg_protection_class -->
<!-- column: item:A.5.33:reg_owner_per_class -->
<!-- column: item:A.5.33:reg_last_verified -->
<!-- column: item:A.5.33:reg_storage_location -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you create a clear, organized register of all your record types, showing how long you keep them, why, who is responsible, and how they are protected. It’s essential for demonstrating control over your information assets during audits.

## When to use it

Use this register whenever you need to document and manage your records retention and protection practices. Update it as needed to reflect changes in your records or policies, as it should always be current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each record class you list. Completing the register from scratch can take several hours, depending on the number of record types in your organization.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.33:records_schedule_register -->
| Records Schedule | Retention Periods | Retention Drivers | Reg Protection Class | Reg Owner Per Class | Reg Last Verified | Reg Storage Location |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.33:records_schedule_register -->

## Column guidance — what to fill in

### Records Schedule

<<MUST item:A.5.33:records_schedule>>
_Why: 27002:5.33 — records_

> _Standard text:_ Records inventory or schedule listing every record class the organisation holds (HR records, financial records, customer records, contract records, security/audit logs, processing-activity records, system records, training records, incident records, etc.)

<<GUIDANCE>>

### Retention Periods

<<MUST item:A.5.33:retention_periods>>
_Why: 27002:5.33 — retention_

> _Standard text:_ Retention period per record class (concrete duration — years/months, with start-trigger and end-trigger defined)

<<GUIDANCE>>

### Retention Drivers

<<MUST item:A.5.33:retention_drivers>>
_Why: 27002:5.33 — legal driver_

> _Standard text:_ Legal/regulatory driver per retention period stated (statute, regulator guidance, contractual obligation, business need — never an arbitrary number)

<<GUIDANCE>>

### Reg Protection Class

<<MUST item:A.5.33:reg_protection_class>>
_Why: 27002:5.33 — protection per class_

> _Standard text:_ Protection class per record class (which classification + protection profile from the procedure applies) — drives the access-control / encryption / immutability decision

<<GUIDANCE>>

### Reg Owner Per Class

<<MUST item:A.5.33:reg_owner_per_class>>
_Why: Accountability_

> _Standard text:_ Owner per record class (named role responsible for the class — HR for personnel records, Finance for financial records, etc.)

<<GUIDANCE>>

### Reg Last Verified

<<MUST item:A.5.33:reg_last_verified>>
_Why: 27002:5.33 — kept current_

> _Standard text:_ Last-verified date per class (proves the entry is current; missing dates surface stale classes at review)

<<GUIDANCE>>

### Reg Storage Location

<<MUST item:A.5.33:reg_storage_location>>
_Why: 27002:5.33 — storage media_

> _Standard text:_ Storage location per class (system / repository / physical archive — needed at disposal and at legal-hold invocation)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Pii Flag

<<SHOULD item:A.5.33:reg_pii_flag>>
_Why: ISO × GDPR integration_

> _Standard text:_ PII flag per class (drives GDPR Art.5.1.e storage-limitation overlay — cross-link to the procedure's PII overlay)

<<GUIDANCE>>

### Reg Legal Hold Flag

<<SHOULD item:A.5.33:reg_legal_hold_flag>>
_Why: Litigation readiness_

> _Standard text:_ Active legal-hold flag per class (rows currently under hold are visible at-a-glance)

<<GUIDANCE>>

### Reg Volume

<<SHOULD item:A.5.33:reg_volume>>
_Why: Operational realism_

> _Standard text:_ Approximate volume per class (drives prioritisation when storage costs or e-discovery demand it)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
