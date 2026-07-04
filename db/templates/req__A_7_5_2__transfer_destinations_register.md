---
leaf_id: req:A.7.5.2:transfer_destinations_register
control_ref: A.7.5.2
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Transfer Destinations Register

> Per-destination row — countries + international orgs where PII may be transferred. Annual refresh (freshness=365). Directly consumed by public notice.

<!-- TABLE-COLUMNS leaf:req:A.7.5.2:transfer_destinations_register -->
<!-- column: item:A.7.5.2:reg_destination_id -->
<!-- column: item:A.7.5.2:reg_transfer_type -->
<!-- column: item:A.7.5.2:reg_basis_link -->
<!-- column: item:A.7.5.2:reg_effective_date -->
<!-- column: item:A.7.5.2:reg_public_disclosure -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.5.2:transfer_destinations_register -->
| Reg Destination Id | Reg Transfer Type | Reg Basis Link | Reg Effective Date | Reg Public Disclosure |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.5.2:transfer_destinations_register -->

## Column guidance — what to fill in

### Reg Destination Id

<<MUST item:A.7.5.2:reg_destination_id>>
_Why: Referenceability_

> _Standard text:_ Destination identifier per row (country ISO code or international org name)

### Reg Transfer Type

<<MUST item:A.7.5.2:reg_transfer_type>>
_Why: §7.5.2 — normal operations_

> _Standard text:_ Transfer type per row (direct storage / subprocessing / support access / M&A)

### Reg Basis Link

<<MUST item:A.7.5.2:reg_basis_link>>
_Why: §7.5.2 — considered in relation to 7.5.1_

> _Standard text:_ Basis link per row (link to A.7.5.1 register)

### Reg Effective Date

<<MUST item:A.7.5.2:reg_effective_date>>
_Why: Currency_

> _Standard text:_ Effective date per row (when destination added)

### Reg Public Disclosure

<<MUST item:A.7.5.2:reg_public_disclosure>>
_Why: §7.5.2 — available to customers_

> _Standard text:_ Public-disclosure status per row (in privacy notice / DPA schedule)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Subcontractor

<<SHOULD item:A.7.5.2:reg_subcontractor>>
_Why: §7.5.2 — subcontracted processing_

> _Standard text:_ Subcontractor per row where the destination is via a subprocessor
