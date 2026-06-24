---
leaf_id: req:A.5.21:ict_component_register
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# ICT Component / Vendor Register

> A.5.21 requires the org to know which ICT components are in use, who supplies them, which are critical, when they reach end-of-life, and what sub-suppliers stand behind them. The register is the live source of truth — feeding the periodic review and EOL-replacement leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Component / service identified per row (vendor, product, version)

<<MUST item:A.5.21:reg_component>>
_Why: 27002:5.21e — track_

<<TEXT>>

## 2. Critical-component flag per row (drives 27002:5.21e scrutiny)

<<MUST item:A.5.21:reg_critical_flag>>
_Why: 27002:5.21e_

<<TEXT>>

## 3. End-of-support / end-of-life date per row

<<MUST item:A.5.21:reg_eol_date>>
_Why: 27002:5.21i_

<<TEXT>>

## 4. Disclosed sub-suppliers / fourth parties per row

<<MUST item:A.5.21:reg_subsupplier>>
_Why: 27002:5.21b,c_

<<TEXT>>

## 5. Named internal owner per component (typically architecture or platform team)

<<MUST item:A.5.21:reg_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. SBOM hash / version reference per software component

<<SHOULD item:A.5.21:reg_sbom_ref>>
_Why: Modern supply-chain hygiene_

<<TEXT>>

### 2. Approved-vendor / banned-vendor list check stamp per row

<<SHOULD item:A.5.21:reg_vendor_check>>
_Why: 27002:5.21a_

<<TEXT>>
