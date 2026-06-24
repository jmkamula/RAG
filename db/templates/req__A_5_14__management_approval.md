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

> Transfer-policy authority is needed when rules are enforced against users (refusing to send / requiring encryption) or against external counterparties (mandating agreements before disclosure). Management approval establishes the legitimate authority for the policy and the consequences of violation. Approval names a signatory at the appropriate management level, a date, and the specific policy version

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Signatory at appropriate management level (typically CISO with executive endorsement; CIO co-sign where transfer mechanisms involve IT systems)

<<MUST item:A.5.14:approval_signatory>>
_Why: 27002:5.14 + clause 5.1_

<<TEXT>>

## 2. Approval date recorded

<<MUST item:A.5.14:approval_date>>
_Why: Clause 5.1_

<<TEXT>>

## 3. Reference to the specific version of the transfer policy being approved

<<MUST item:A.5.14:approval_target>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Statement of the signatory's authority (delegation chain if not top-management; legal department consultation noted if cross-border scope)

<<SHOULD item:A.5.14:approval_authority>>
_Why: Accountability + cross-border defence_

<<TEXT>>
