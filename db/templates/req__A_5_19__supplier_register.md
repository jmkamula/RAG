---
leaf_id: req:A.5.19:supplier_register
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Supplier Register

> A.5.19 requires the org to know who its suppliers are, what they provide, the nature of access they hold, and their risk classification. The register is the live source of truth — feeding the periodic review and offboarding leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each supplier captured: identity, products/services, criticality

<<MUST item:A.5.19:reg_inventory>>
_Why: 27002:5.19a — types_

<<TEXT>>

## 2. Supplier type per row (ICT service / ICT infra component / logistics / utilities / etc.)

<<MUST item:A.5.19:reg_supplier_type>>
_Why: 27002:5.19a_

<<TEXT>>

## 3. Access type per row (logical / physical / network / application / app-to-app)

<<MUST item:A.5.19:reg_access_type>>
_Why: 27002:5.19g_

<<TEXT>>

## 4. Risk classification (tier or category) per row

<<MUST item:A.5.19:reg_classification>>
_Why: 27002:5.19b,d_

<<TEXT>>

## 5. Named internal owner accountable per supplier (relationship owner + InfoSec contact)

<<MUST item:A.5.19:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Critical-supplier flag (drives audit + continuity scrutiny — link to A.5.29 / A.5.30)

<<SHOULD item:A.5.19:reg_critical_flag>>
_Why: 27002:5.19j_

<<TEXT>>

### 2. Disclosed sub-suppliers / fourth parties tracked per row

<<SHOULD item:A.5.19:reg_subsupplier>>
_Why: Supply-chain depth_

<<TEXT>>
