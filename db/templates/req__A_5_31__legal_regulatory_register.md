---
leaf_id: req:A.5.31:legal_regulatory_register
control_ref: A.5.31
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Legal, Statutory, Regulatory and Contractual Requirements Register

> A.5.31 requires applicable legal, statutory, regulatory and contractual requirements relevant to information security to be identified, documented and kept up to date. The register enumerates them and maps each to the compliance approach. Maintenance procedure, applicable-obligations scope and periodic review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.31:legal_regulatory_register -->
<!-- column: item:A.5.31:laws_listed -->
<!-- column: item:A.5.31:jurisdictions -->
<!-- column: item:A.5.31:contractual -->
<!-- column: item:A.5.31:compliance_approach -->
<!-- column: item:A.5.31:owner_per_item -->
<!-- column: item:A.5.31:last_verified -->
<!-- column: item:A.5.31:obligation_type -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.31:legal_regulatory_register -->
| Laws Listed | Jurisdictions | Contractual | Compliance Approach | Owner Per Item | Last Verified | Obligation Type |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.31:legal_regulatory_register -->

## Column guidance — what to fill in

### Laws Listed

<<MUST item:A.5.31:laws_listed>>
_Why: 27002:5.31a_

> _Standard text:_ Applicable laws and regulations enumerated (GDPR, sectoral, jurisdictional, transfer regimes)

### Jurisdictions

<<MUST item:A.5.31:jurisdictions>>
_Why: 27002:5.31a — relevant_

> _Standard text:_ Jurisdictions covered explicitly per entry (HQ, places of operation, customer locations, data residency)

### Contractual

<<MUST item:A.5.31:contractual>>
_Why: 27002:5.31c_

> _Standard text:_ Contractual obligations summarised (customer contracts, regulator agreements, sectoral codes)

### Compliance Approach

<<MUST item:A.5.31:compliance_approach>>
_Why: 27002:5.31b_

> _Standard text:_ Approach for compliance per item (how the obligation is met, which controls/policies/processes evidence it)

### Owner Per Item

<<MUST item:A.5.31:owner_per_item>>
_Why: Accountability_

> _Standard text:_ Owner named per requirement (who tracks change and compliance)

### Last Verified

<<MUST item:A.5.31:last_verified>>
_Why: 27002:5.31 — kept up to date_

> _Standard text:_ Last-verified or last-reviewed date per entry

### Obligation Type

<<MUST item:A.5.31:obligation_type>>
_Why: 27002:5.31 — categorisation_

> _Standard text:_ Obligation type tag (statutory / regulatory / contractual / sectoral-code) to drive review cadence

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Evidence Links

<<SHOULD item:A.5.31:evidence_links>>
_Why: Audit traceability_

> _Standard text:_ Links to evidence of compliance per requirement (policies, audit reports, certifications)

### Change Monitoring

<<SHOULD item:A.5.31:change_monitoring>>
_Why: Currency_

> _Standard text:_ Source for change monitoring per entry (legal counsel, regulator alerts, industry feed)

### Authority Link

<<SHOULD item:A.5.31:authority_link>>
_Why: Cross-control coherence_

> _Standard text:_ Each entry tagged with the authority(ies) responsible — cross-link to A.5.5 authority register
