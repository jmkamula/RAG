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

<<DOC_CONTROL>>

> Upstream — what information classes have what retention triggers (drawn from A.5.33 records retention schedule), which media classes need which deletion method

## What this template gives you

This template helps you clearly define which types of information and storage media in your organization require specific retention periods and deletion methods, making it easier to comply with ISO 27001 requirements.

## When to use it

Use this document whenever you need to outline or update the scope of data deletion and retention practices in your environment. Refresh it as needed to reflect changes in your data handling or retention policies.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as each required section takes roughly 10-15 minutes to fill in thoughtfully.

## 1. Information classes enumerated with retention trigger source per class (cross-link to A.5.33)

<<MUST item:A.8.10:scope_classes>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Media classes enumerated with required deletion method per class

<<MUST item:A.8.10:scope_media_methods>>
_Why: 27002:8.10 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 3. Vendor-managed data delegated to A.5.19/A.5.20 supplier obligations (contractual deletion-on-termination)

<<MUST item:A.8.10:scope_vendor_managed>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, new data class, new regulator requirement)

<<SHOULD item:A.8.10:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
