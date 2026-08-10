---
leaf_id: req:B.8.2.6:ropa_maintenance_procedure
control_ref: B.8.2.6
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Processor RoPA Maintenance Procedure

<<DOC_CONTROL>>

> How the processor RoPA is kept accurate — new customer onboarding trigger, customer instruction changes, subprocessor changes, retirement of customers, secure maintenance.

## What this template gives you

This template helps you document how you keep your processor Record of Processing Activities (RoPA) accurate and up to date, covering key events like onboarding new customers, handling changes, and maintaining security.

## When to use it

Use this procedure whenever you onboard a new customer, receive customer instructions, change subprocessors, retire customers, or need to securely maintain your RoPA. Update it as needed whenever these events occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in with your specific details.

## 1. New-customer onboarding trigger — RoPA row created per new engagement (link to B.8.2.1)

<<MUST item:B.8.2.6:proc_onboarding_trigger>>
_Why: §8.2.6 — support of demonstrating compliance_

<<GUIDANCE>>

<<TEXT>>

## 2. Instruction-change capture — customer purpose changes trigger RoPA update

<<MUST item:B.8.2.6:proc_instruction_change>>
_Why: §8.2.6 — as specified in applicable contract_

<<GUIDANCE>>

<<TEXT>>

## 3. Subprocessor change — subprocessor additions / removals trigger RoPA update

<<MUST item:B.8.2.6:proc_subprocessor_update>>
_Why: Art.28.2 currency_

<<GUIDANCE>>

<<TEXT>>

## 4. Secure maintenance — access control + integrity for the processor RoPA

<<MUST item:B.8.2.6:proc_secure_maintenance>>
_Why: §8.2.6 — maintain the necessary records_

<<GUIDANCE>>

<<TEXT>>

## 5. Customer-availability path — how a customer requests + receives their RoPA row extract

<<MUST item:B.8.2.6:proc_customer_availability>>
_Why: §8.2.5 audit-support cross-link_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + Trust Ops)

<<SHOULD item:B.8.2.6:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
