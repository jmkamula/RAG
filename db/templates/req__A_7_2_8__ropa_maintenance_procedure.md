---
leaf_id: req:A.7.2.8:ropa_maintenance_procedure
control_ref: A.7.2.8
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# RoPA Maintenance Procedure

> The procedure that keeps the RoPA accurate — how new activities are added, changes captured, retired activities removed, cadence for reconciliation against source-of-truth systems.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. New-activity intake trigger + workflow (new product launch / new integration / new data source)

<<MUST item:A.7.2.8:proc_add_activity>>
_Why: §7.2.8 — determine records_

<<TEXT>>

## 2. Change-capture — activity changes trigger RoPA update within stated SLA

<<MUST item:A.7.2.8:proc_change_capture>>
_Why: Currency_

<<TEXT>>

## 3. Retirement — activities that stop generate a retirement record (not deletion) for audit history

<<MUST item:A.7.2.8:proc_retire_activity>>
_Why: Audit trail_

<<TEXT>>

## 4. Reconciliation cadence — against §7.2.1 purpose register + §7.2.2 basis register + §7.2.5 PIA register

<<MUST item:A.7.2.8:proc_reconciliation>>
_Why: Cross-register integrity_

<<TEXT>>

## 5. Secure maintenance — access control + integrity for the RoPA itself

<<MUST item:A.7.2.8:proc_secure_maintenance>>
_Why: §7.2.8 — securely maintain_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + Privacy Office)

<<SHOULD item:A.7.2.8:proc_owner>>
_Why: §7.2.8 owner_

<<TEXT>>
