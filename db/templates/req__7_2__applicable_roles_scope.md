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

<<DOC_CONTROL>>

> The upstream that bounds the record — which roles actually affect ISMS performance (per clause 7.2 'whose work affects'). Not every role in the org — but more than just InfoSec staff

## What this template gives you

This template helps you clearly identify which roles in your organization have a direct impact on your information security management system, going beyond just the InfoSec team.

## When to use it

Use this document whenever you need to define or update the list of roles that influence your ISMS, and review it whenever your organizational structure or responsibilities change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes to complete this from scratch, as you'll need to thoughtfully consider and describe each relevant role.

## 1. ISMS-team roles enumerated (CISO, ISMS Manager, InfoSec analyst, auditor)

<<MUST item:7.2:scope_isms_roles>>
_Why: Clause 7.2 — affect ISMS performance_

<<GUIDANCE>>

<<TEXT>>

## 2. Supporting roles enumerated (engineering with InfoSec responsibilities, HR with onboarding, IT ops with access provisioning)

<<MUST item:7.2:scope_supporting_roles>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Out-of-scope roles stated explicitly (purely-administrative roles with no ISMS touchpoint)

<<MUST item:7.2:scope_exclusions>>
_Why: Defensible bounding_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Contractor coverage rules where contractors fill ISMS-affecting roles

<<SHOULD item:7.2:scope_contractors>>
_Why: Common scope edge_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
