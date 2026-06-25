---
leaf_id: req:A.5.7:intel_product_record
control_ref: A.5.7
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Per-Product Intelligence Records

> A.5.7 expects intelligence to actually reach consumers and inform defensive action — not just be produced and filed. The per-product record evidences each delivered artefact: product id, layer, source feeds aggregated, named consumer(s), distribution date, action taken downstream (firewall rule pushed / IDS signature added / risk register entry / exec briefing). One record per published product, traceable back to the feed register and forward to the consumer's control

<!-- TABLE-COLUMNS leaf:req:A.5.7:intel_product_record -->
<!-- column: item:A.5.7:prod_id -->
<!-- column: item:A.5.7:prod_layer -->
<!-- column: item:A.5.7:prod_sources -->
<!-- column: item:A.5.7:prod_consumer -->
<!-- column: item:A.5.7:prod_distribution -->
<!-- column: item:A.5.7:prod_action_taken -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.7:intel_product_record -->
| Prod Id | Prod Layer | Prod Sources | Prod Consumer | Prod Distribution | Prod Action Taken |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.7:intel_product_record -->

## Column guidance — what to fill in

### Prod Id

<<MUST item:A.5.7:prod_id>>
_Why: 27002:5.7 — produce threat intelligence_

> _Standard text:_ Product identifier per record (unique, sequenced)

### Prod Layer

<<MUST item:A.5.7:prod_layer>>
_Why: 27002:5.7 — three layers_

> _Standard text:_ Intelligence layer per record (strategic / tactical / operational)

### Prod Sources

<<MUST item:A.5.7:prod_sources>>
_Why: 27002:5.7 — sources traceability_

> _Standard text:_ Source feeds aggregated per record (links to feed register entries)

### Prod Consumer

<<MUST item:A.5.7:prod_consumer>>
_Why: 27002:5.7 — communication_

> _Standard text:_ Named consumer(s) per record (sec ops, IT/network, risk owners, exec briefing)

### Prod Distribution

<<MUST item:A.5.7:prod_distribution>>
_Why: 27002:5.7 — delivered_

> _Standard text:_ Distribution date and channel per record (email, ticket, briefing)

### Prod Action Taken

<<MUST item:A.5.7:prod_action_taken>>
_Why: 27002:5.7 — informed defensive action_

> _Standard text:_ Action taken downstream per record (firewall rule / IDS signature / risk register entry / control update / no-op)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Prod Effectiveness

<<SHOULD item:A.5.7:prod_effectiveness>>
_Why: Continual improvement_

> _Standard text:_ Effectiveness check planned or recorded (post-distribution validation that the product drove the intended action)

### Prod Retention End

<<SHOULD item:A.5.7:prod_retention_end>>
_Why: Operational discipline_

> _Standard text:_ Retention end-date noted (IOC libraries age fast — old products marked for archive/disposal)
