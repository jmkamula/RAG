---
leaf_id: req:A.8.10:information_deletion_procedure
control_ref: A.8.10
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Information Deletion Procedure

> A.8.10 requires information deleted when no longer required. Procedure documents retention triggers, deletion methods per media class, verification approach. Per-deletion register (lifecycle-end), applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Retention trigger source (cross-link to A.5.33 records protection retention schedule)

<<MUST item:A.8.10:retention_trigger>>
_Why: 27002:8.10 — when no longer required_

<<TEXT>>

## 2. Deletion methods per media class (logical delete / overwrite / crypto-erase / physical destruction)

<<MUST item:A.8.10:deletion_methods>>
_Why: 27002:8.10 — deleted_

<<TEXT>>

## 3. Verification of deletion (audit log entry / sample re-read / certificate of destruction for hardware)

<<MUST item:A.8.10:verification>>
_Why: 27002:8.10 — deleted_

<<TEXT>>

## 4. Scope covers backups + replicas + caches + audit copies (NOT only primary systems — common GDPR pitfall)

<<MUST item:A.8.10:scope_systems>>
_Why: 27002:8.10 — any other storage media + SPEC_ART_25 storage-limitation reference_

<<TEXT>>

## 5. Legal-hold integration overriding deletion (with documented hold rationale and termination criteria)

<<MUST item:A.8.10:legal_hold>>
_Why: Litigation readiness_

<<TEXT>>

## 6. GDPR Art.17 erasure path (DSAR-triggered deletion) cross-link to A.5.34 PII protection

<<MUST item:A.8.10:gdpr_erasure_path>>
_Why: GDPR Art.17 integration_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Automated retention enforcement where supported (TTL / lifecycle-policy / scheduled job)

<<SHOULD item:A.8.10:automated_retention>>
_Why: Scale_

<<TEXT>>
