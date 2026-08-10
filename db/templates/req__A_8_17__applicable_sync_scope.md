---
leaf_id: req:A.8.17:applicable_sync_scope
control_ref: A.8.17
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 2
should_count: 1
---

# Applicable Sync Scope

<<DOC_CONTROL>>

> Upstream — which system classes need sync, what drift tolerance per class (sub-second for forensics-critical; seconds acceptable elsewhere)

## What this template gives you

This template helps you clearly define which system classes need to be kept in sync and how quickly, ensuring your environment meets compliance requirements for data consistency and integrity.

## When to use it

Use this document whenever you need to specify or update the systems that require synchronization in your environment. Review and refresh it as your systems or requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 20 to 30 minutes completing this from scratch, as you'll need to address two required elements and possibly one recommended element.

## 1. System classes enumerated with drift tolerance per class

<<MUST item:A.8.17:scope_classes>>
_Why: 27002:8.17 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Exclusion rationale (network-isolated systems with documented offline-clock procedure)

<<MUST item:A.8.17:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system class, new regulator drift requirement)

<<SHOULD item:A.8.17:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
