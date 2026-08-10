---
leaf_id: req:Art.16:applicable_systems_scope
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Systems Scope for Rectification

<<DOC_CONTROL>>

> The upstream — every system holding rectifiable personal data that needs to be touched on a rectification request

## What this template gives you

This template helps you identify and list all systems in your environment that store personal data which may need to be updated or corrected if someone requests a rectification.

## When to use it

Use this document whenever you need to clarify which systems are affected by data rectification requests, and update it whenever your systems or data flows change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to identify and describe at least three relevant systems.

## 1. Systems enumerated (PII inventory cross-reference — A.5.34:pii_inventory + Art.30 RoPA)

<<MUST item:Art.16:scope_systems>>
_Why: Coverage proof_

<<GUIDANCE>>

<<TEXT>>

## 2. Replica + backup handling rules — when rectification reaches them, when supplementary statement substitutes

<<MUST item:Art.16:scope_replicas>>
_Why: Art.16 — all instances_

<<GUIDANCE>>

<<TEXT>>

## 3. Third-party processor handling — where requests propagate via Art.28 DPA flow

<<MUST item:Art.16:scope_third_parties>>
_Why: Cross-article coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new system holding PII, new processor onboarded)

<<SHOULD item:Art.16:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
