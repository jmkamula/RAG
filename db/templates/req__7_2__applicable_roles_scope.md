---
leaf_id: req:7.2:applicable_roles_scope
control_ref: 7.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable ISMS-Affecting Roles Scope

> The upstream that bounds the record — which roles actually affect ISMS performance (per clause 7.2 'whose work affects'). Not every role in the org — but more than just InfoSec staff

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. ISMS-team roles enumerated (CISO, ISMS Manager, InfoSec analyst, auditor)

<<MUST item:7.2:scope_isms_roles>>
_Why: Clause 7.2 — affect ISMS performance_

<<TEXT>>

## 2. Supporting roles enumerated (engineering with InfoSec responsibilities, HR with onboarding, IT ops with access provisioning)

<<MUST item:7.2:scope_supporting_roles>>
_Why: Coverage_

<<TEXT>>

## 3. Out-of-scope roles stated explicitly (purely-administrative roles with no ISMS touchpoint)

<<MUST item:7.2:scope_exclusions>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Contractor coverage rules where contractors fill ISMS-affecting roles

<<SHOULD item:7.2:scope_contractors>>
_Why: Common scope edge_

<<TEXT>>
