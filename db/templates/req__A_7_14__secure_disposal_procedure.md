---
leaf_id: req:A.7.14:secure_disposal_procedure
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Secure Disposal and Re-Use of Equipment Procedure

> A.7.14 requires equipment containing storage media to be verified for data and licensed-software removal before disposal or re-use. The procedure documents verification methods, certificates, chain of custody, approved providers, destruction method per class. The disposal scope + disposal-record register (lifecycle-end) + periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope (all equipment containing any form of storage media — laptops, servers, phones, printers/MFDs with storage, network gear)

<<MUST item:A.7.14:scope>>
_Why: 27002:7.14 — equipment containing storage media_

<<TEXT>>

## 2. Verification of data removal method per classification (overwrite, degauss, physical destruction)

<<MUST item:A.7.14:verification>>
_Why: 27002:7.14 — securely overwritten_

<<TEXT>>

## 3. Licensed software removal step before disposal or re-use

<<MUST item:A.7.14:software_removal>>
_Why: 27002:7.14 — licensed software removed_

<<TEXT>>

## 4. Certificate of destruction obtained where applicable

<<MUST item:A.7.14:certificate>>
_Why: Auditability_

<<TEXT>>

## 5. Chain of custody from collection to disposal

<<MUST item:A.7.14:chain_of_custody>>
_Why: 27002:7.14 — securely_

<<TEXT>>

## 6. Approved disposal providers list with security expectations

<<MUST item:A.7.14:approved_providers>>
_Why: 27002:7.14 — securely_

<<TEXT>>

## 7. Destruction method matched to data classification (shred/melt/degauss for highest)

<<MUST item:A.7.14:destruction_method>>
_Why: Proportionality_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Decision criteria for in-house vs external disposal

<<SHOULD item:A.7.14:internal_vs_external>>
_Why: Operational pragmatism_

<<TEXT>>
