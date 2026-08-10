---
leaf_id: req:A.5.14:management_approval
control_ref: A.5.14
standard_id: ISO27001:2022
evidence_type: approval
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Management Approval of Information Transfer Policy

<<DOC_CONTROL>>

> Transfer-policy authority is needed when rules are enforced against users (refusing to send / requiring encryption) or against external counterparties (mandating agreements before disclosure). Management approval establishes the legitimate authority for the policy and the consequences of violation. Approval names a signatory at the appropriate management level, a date, and the specific policy version

## What this template gives you

This template helps you formally document management approval for your information transfer policy, ensuring there is clear authority and accountability for how sensitive information is shared or protected.

## When to use it

Use this whenever your organization needs to enforce rules on sending information, such as requiring encryption or agreements with external parties. Update the approval whenever there are changes to the policy or management signatory.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to provide details like the signatory, approval date, and specific policy version.

## 1. Signatory at appropriate management level (typically CISO with executive endorsement; CIO co-sign where transfer mechanisms involve IT systems)

<<MUST item:A.5.14:approval_signatory>>
_Why: 27002:5.14 + clause 5.1_

<<GUIDANCE>>

<<TEXT>>

## 2. Approval date recorded

<<MUST item:A.5.14:approval_date>>
_Why: Clause 5.1_

<<GUIDANCE>>

<<TEXT>>

## 3. Reference to the specific version of the transfer policy being approved

<<MUST item:A.5.14:approval_target>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Statement of the signatory's authority (delegation chain if not top-management; legal department consultation noted if cross-border scope)

<<SHOULD item:A.5.14:approval_authority>>
_Why: Accountability + cross-border defence_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
