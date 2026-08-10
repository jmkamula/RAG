---
leaf_id: req:A.8.24:applicable_crypto_scope
control_ref: A.8.24
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Cryptography Scope

<<DOC_CONTROL>>

> Upstream — which data classes require encryption (drawn from A.5.12 + A.5.34 PII inventory). Vendor-managed encryption (cloud-provider-managed keys) delegated to A.5.19/A.5.21

## What this template gives you

This template helps you clearly define which types of data in your environment need to be encrypted, based on your inventory of sensitive information and relevant compliance requirements.

## When to use it

Use this document whenever you need to outline your encryption requirements for different data classes in your environment, and update it whenever there are changes to your data inventory or encryption practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, as you'll need to identify and describe each required element in detail.

## 1. Data classes enumerated with encryption obligation per class (drawn from A.5.12 classification + A.5.34 PII)

<<MUST item:A.8.24:scope_data_classes>>
_Why: 27002:8.24 — sensitive information_

<<GUIDANCE>>

<<TEXT>>

## 2. Vendor-managed key handling boundaries (BYOK / HYOK / vendor-only options with risk acceptance)

<<MUST item:A.8.24:scope_vendor_managed>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale + compensating controls (e.g. public-classification data)

<<MUST item:A.8.24:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new data class, algorithm deprecation, PQC transition trigger)

<<SHOULD item:A.8.24:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
