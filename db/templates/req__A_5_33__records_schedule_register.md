---
leaf_id: req:A.5.33:records_schedule_register
control_ref: A.5.33
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Records Schedule (Per-Class Retention and Protection Register)

> The operational register at the heart of A.5.33. Without a records schedule listing every record class with retention, driver, owner and protection assignment, the policy is theoretical. The schedule is queried at audit time to demonstrate that the organisation knows what records it holds, why it holds them, and for how long

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Records inventory or schedule listing every record class the organisation holds (HR records, financial records, customer records, contract records, security/audit logs, processing-activity records, system records, training records, incident records, etc.)

<<MUST item:A.5.33:records_schedule>>
_Why: 27002:5.33 — records_

<<TEXT>>

## 2. Retention period per record class (concrete duration — years/months, with start-trigger and end-trigger defined)

<<MUST item:A.5.33:retention_periods>>
_Why: 27002:5.33 — retention_

<<TEXT>>

## 3. Legal/regulatory driver per retention period stated (statute, regulator guidance, contractual obligation, business need — never an arbitrary number)

<<MUST item:A.5.33:retention_drivers>>
_Why: 27002:5.33 — legal driver_

<<TEXT>>

## 4. Protection class per record class (which classification + protection profile from the procedure applies) — drives the access-control / encryption / immutability decision

<<MUST item:A.5.33:reg_protection_class>>
_Why: 27002:5.33 — protection per class_

<<TEXT>>

## 5. Owner per record class (named role responsible for the class — HR for personnel records, Finance for financial records, etc.)

<<MUST item:A.5.33:reg_owner_per_class>>
_Why: Accountability_

<<TEXT>>

## 6. Last-verified date per class (proves the entry is current; missing dates surface stale classes at review)

<<MUST item:A.5.33:reg_last_verified>>
_Why: 27002:5.33 — kept current_

<<TEXT>>

## 7. Storage location per class (system / repository / physical archive — needed at disposal and at legal-hold invocation)

<<MUST item:A.5.33:reg_storage_location>>
_Why: 27002:5.33 — storage media_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. PII flag per class (drives GDPR Art.5.1.e storage-limitation overlay — cross-link to the procedure's PII overlay)

<<SHOULD item:A.5.33:reg_pii_flag>>
_Why: ISO × GDPR integration_

<<TEXT>>

### 2. Active legal-hold flag per class (rows currently under hold are visible at-a-glance)

<<SHOULD item:A.5.33:reg_legal_hold_flag>>
_Why: Litigation readiness_

<<TEXT>>

### 3. Approximate volume per class (drives prioritisation when storage costs or e-discovery demand it)

<<SHOULD item:A.5.33:reg_volume>>
_Why: Operational realism_

<<TEXT>>
