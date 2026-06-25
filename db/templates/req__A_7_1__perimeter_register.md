---
leaf_id: req:A.7.1:perimeter_register
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Per-Site Perimeter Register

> The catalogue of perimeters across all sites — site identifier, perimeter id, area classification, barrier inventory, access-point list, owner. Drives 'show me every site has a defined perimeter' completeness check

<!-- TABLE-COLUMNS leaf:req:A.7.1:perimeter_register -->
<!-- column: item:A.7.1:reg_site_id -->
<!-- column: item:A.7.1:reg_perimeter_id -->
<!-- column: item:A.7.1:reg_classification -->
<!-- column: item:A.7.1:reg_barriers -->
<!-- column: item:A.7.1:reg_last_assessed -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.1:perimeter_register -->
| Reg Site Id | Reg Perimeter Id | Reg Classification | Reg Barriers | Reg Last Assessed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.1:perimeter_register -->

## Column guidance — what to fill in

### Reg Site Id

<<MUST item:A.7.1:reg_site_id>>
_Why: 27002:7.1 — defined_

> _Standard text:_ Site identifier per perimeter row (HQ, regional offices, data centres, co-locations)

### Reg Perimeter Id

<<MUST item:A.7.1:reg_perimeter_id>>
_Why: 27002:7.1 — security perimeters_

> _Standard text:_ Perimeter identifier per row (a site may have multiple perimeters — outer + inner + secure-room)

### Reg Classification

<<MUST item:A.7.1:reg_classification>>
_Why: Cross-leaf coherence_

> _Standard text:_ Area classification per row (matches policy's classification scheme)

### Reg Barriers

<<MUST item:A.7.1:reg_barriers>>
_Why: 27002:7.1 — used to protect_

> _Standard text:_ Barriers in place per row (specific barrier inventory — what walls, what doors, what mechanisms)

### Reg Last Assessed

<<MUST item:A.7.1:reg_last_assessed>>
_Why: 27002:7.1 — maintained_

> _Standard text:_ Last assessment date per row (drives staleness detection)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Remediation

<<SHOULD item:A.7.1:reg_remediation>>
_Why: Operational discipline_

> _Standard text:_ Remediation log per row where barriers fall short of classification requirements
