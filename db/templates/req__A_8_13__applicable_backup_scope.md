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

> Upstream — which systems / datasets are in scope with what RPO tier. Drawn from A.5.30 BIA. Documents what's vendor-managed (delegated to A.5.19/A.5.21 supplier)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems / datasets enumerated with RPO tier per row (drawn from A.5.30 BIA)

<<MUST item:A.8.13:scope_systems>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Vendor-managed backups delegated to A.5.19/A.5.21 supplier obligations

<<MUST item:A.8.13:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale where backup not required (ephemeral / reconstructable / public)

<<MUST item:A.8.13:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, RPO change, new vendor)

<<SHOULD item:A.8.13:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
