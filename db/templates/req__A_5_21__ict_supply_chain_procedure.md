---
leaf_id: req:A.5.21:ict_supply_chain_procedure
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 9
should_count: 2
---

# ICT Supply Chain Information Security Procedure

> A.5.21 requires processes to manage information security risks in the ICT products and services supply chain. The procedure covers sourcing, integrity verification, sub-supplier visibility, requirements propagation and identification of critical components. The component register, periodic review and EOL-replacement records are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Sourcing controls (approved vendor list, banned-vendor list, country-of-origin considerations)

<<MUST item:A.5.21:sourcing_controls>>
_Why: 27002:5.21a_

<<TEXT>>

## 2. ICT service / product suppliers required to propagate requirements through their sub-contractors / component suppliers

<<MUST item:A.5.21:requirements_propagation>>
_Why: 27002:5.21b,c_

<<TEXT>>

## 3. Monitoring and validation methods for conformance to stated security requirements

<<MUST item:A.5.21:monitoring_validation>>
_Why: 27002:5.21d_

<<TEXT>>

## 4. Identification of critical components needing special scrutiny (especially when outsourced)

<<MUST item:A.5.21:critical_components>>
_Why: 27002:5.21e_

<<TEXT>>

## 5. Traceability of critical components through the supply chain (end-to-end provenance)

<<MUST item:A.5.21:traceability>>
_Why: 27002:5.21f_

<<TEXT>>

## 6. Component integrity verification on delivery (signed firmware, signed packages, hash verification)

<<MUST item:A.5.21:integrity_verification>>
_Why: 27002:5.21g_

<<TEXT>>

## 7. Sub-supplier visibility expectations (disclosure of components, fourth-party listing)

<<MUST item:A.5.21:subsupplier_visibility>>
_Why: 27002:5.21b,c_

<<TEXT>>

## 8. Support and patching expectations stated for each ICT product/service

<<MUST item:A.5.21:patching_expectations>>
_Why: 27002:5.21i_

<<TEXT>>

## 9. Rules for sharing information about supply chain issues or compromises with suppliers and within own group

<<MUST item:A.5.21:incident_sharing>>
_Why: 27002:5.21h_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure development practice expectations for software vendors

<<SHOULD item:A.5.21:secure_development>>
_Why: Vendor maturity bar_

<<TEXT>>

### 2. SBOM expectations for software components and infrastructure

<<SHOULD item:A.5.21:sbom_expectation>>
_Why: Modern supply-chain hygiene_

<<TEXT>>
