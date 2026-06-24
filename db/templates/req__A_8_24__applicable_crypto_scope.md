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

> Upstream — which data classes require encryption (drawn from A.5.12 + A.5.34 PII inventory). Vendor-managed encryption (cloud-provider-managed keys) delegated to A.5.19/A.5.21

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Data classes enumerated with encryption obligation per class (drawn from A.5.12 classification + A.5.34 PII)

<<MUST item:A.8.24:scope_data_classes>>
_Why: 27002:8.24 — sensitive information_

<<TEXT>>

## 2. Vendor-managed key handling boundaries (BYOK / HYOK / vendor-only options with risk acceptance)

<<MUST item:A.8.24:scope_vendor_managed>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale + compensating controls (e.g. public-classification data)

<<MUST item:A.8.24:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new data class, algorithm deprecation, PQC transition trigger)

<<SHOULD item:A.8.24:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
