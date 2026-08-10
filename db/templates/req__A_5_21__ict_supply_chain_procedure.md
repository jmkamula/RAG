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

<<DOC_CONTROL>>

> A.5.21 requires processes to manage information security risks in the ICT products and services supply chain. The procedure covers sourcing, integrity verification, sub-supplier visibility, requirements propagation and identification of critical components. The component register, periodic review and EOL-replacement records are sibling leaves

## What this template gives you

This template helps you set up clear procedures for managing information security risks in your ICT supply chain, including supplier selection, integrity checks, and tracking critical components. It supports compliance with ISO 27001 requirements.

## When to use it

Use this document whenever you need to manage or review information security risks related to your ICT suppliers and products. Update it as your supply chain changes or when new risks or components are identified.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2.5 hours drafting this procedure from scratch, depending on the number of suppliers and components you need to document in your registers.

## 1. Sourcing controls (approved vendor list, banned-vendor list, country-of-origin considerations)

<<MUST item:A.5.21:sourcing_controls>>
_Why: 27002:5.21a_

<<GUIDANCE>>

<<TEXT>>

## 2. ICT service / product suppliers required to propagate requirements through their sub-contractors / component suppliers

<<MUST item:A.5.21:requirements_propagation>>
_Why: 27002:5.21b,c_

<<GUIDANCE>>

<<TEXT>>

## 3. Monitoring and validation methods for conformance to stated security requirements

<<MUST item:A.5.21:monitoring_validation>>
_Why: 27002:5.21d_

<<GUIDANCE>>

<<TEXT>>

## 4. Identification of critical components needing special scrutiny (especially when outsourced)

<<MUST item:A.5.21:critical_components>>
_Why: 27002:5.21e_

<<GUIDANCE>>

<<TEXT>>

## 5. Traceability of critical components through the supply chain (end-to-end provenance)

<<MUST item:A.5.21:traceability>>
_Why: 27002:5.21f_

<<GUIDANCE>>

<<TEXT>>

## 6. Component integrity verification on delivery (signed firmware, signed packages, hash verification)

<<MUST item:A.5.21:integrity_verification>>
_Why: 27002:5.21g_

<<GUIDANCE>>

<<TEXT>>

## 7. Sub-supplier visibility expectations (disclosure of components, fourth-party listing)

<<MUST item:A.5.21:subsupplier_visibility>>
_Why: 27002:5.21b,c_

<<GUIDANCE>>

<<TEXT>>

## 8. Support and patching expectations stated for each ICT product/service

<<MUST item:A.5.21:patching_expectations>>
_Why: 27002:5.21i_

<<GUIDANCE>>

<<TEXT>>

## 9. Rules for sharing information about supply chain issues or compromises with suppliers and within own group

<<MUST item:A.5.21:incident_sharing>>
_Why: 27002:5.21h_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Secure development practice expectations for software vendors

<<SHOULD item:A.5.21:secure_development>>
_Why: Vendor maturity bar_

<<GUIDANCE>>

<<TEXT>>

### 2. SBOM expectations for software components and infrastructure

<<SHOULD item:A.5.21:sbom_expectation>>
_Why: Modern supply-chain hygiene_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
