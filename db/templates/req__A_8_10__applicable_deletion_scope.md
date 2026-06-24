---
leaf_id: req:A.8.10:applicable_deletion_scope
control_ref: A.8.10
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Deletion Scope

> Upstream — what information classes have what retention triggers (drawn from A.5.33 records retention schedule), which media classes need which deletion method

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Information classes enumerated with retention trigger source per class (cross-link to A.5.33)

<<MUST item:A.8.10:scope_classes>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Media classes enumerated with required deletion method per class

<<MUST item:A.8.10:scope_media_methods>>
_Why: 27002:8.10 — appropriate_

<<TEXT>>

## 3. Vendor-managed data delegated to A.5.19/A.5.20 supplier obligations (contractual deletion-on-termination)

<<MUST item:A.8.10:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, new data class, new regulator requirement)

<<SHOULD item:A.8.10:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
