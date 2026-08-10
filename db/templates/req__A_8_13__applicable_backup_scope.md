---
leaf_id: req:A.8.13:applicable_backup_scope
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Backup Scope

<<DOC_CONTROL>>

> Upstream — which systems / datasets are in scope with what RPO tier. Drawn from A.5.30 BIA. Documents what's vendor-managed (delegated to A.5.19/A.5.21 supplier)

## What this template gives you

This template helps you clearly identify which systems and datasets are covered by your backup processes, including their recovery point objectives and any parts managed by vendors.

## When to use it

Use this document whenever you need to define or update the scope of your backup coverage for your environment, especially after significant changes to your systems or data landscape.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on how easily you can gather information about your systems and vendor-managed components.

## 1. Systems / datasets enumerated with RPO tier per row (drawn from A.5.30 BIA)

<<MUST item:A.8.13:scope_systems>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Vendor-managed backups delegated to A.5.19/A.5.21 supplier obligations

<<MUST item:A.8.13:scope_vendor_managed>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale where backup not required (ephemeral / reconstructable / public)

<<MUST item:A.8.13:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, RPO change, new vendor)

<<SHOULD item:A.8.13:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
