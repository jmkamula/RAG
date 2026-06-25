---
leaf_id: req:A.8.23:filtering_event_register
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Web Filtering Event Register

> Aggregate event view — blocked-access trending, override events, malware-category hits. Drives 'does the filter actually work' visibility

<!-- TABLE-COLUMNS leaf:req:A.8.23:filtering_event_register -->
<!-- column: item:A.8.23:reg_volume -->
<!-- column: item:A.8.23:reg_top_blockers -->
<!-- column: item:A.8.23:reg_overrides -->
<!-- column: item:A.8.23:reg_malware_hits -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.23:filtering_event_register -->
| Reg Volume | Reg Top Blockers | Reg Overrides | Reg Malware Hits |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.23:filtering_event_register -->

## Column guidance — what to fill in

### Reg Volume

<<MUST item:A.8.23:reg_volume>>
_Why: 27002:8.23 — managed_

> _Standard text:_ Aggregate blocked-event volume per category (rolling window)

### Reg Top Blockers

<<MUST item:A.8.23:reg_top_blockers>>
_Why: Operational visibility_

> _Standard text:_ Top-blocked-sites view (signal for category-tuning opportunity)

### Reg Overrides

<<MUST item:A.8.23:reg_overrides>>
_Why: Auditability_

> _Standard text:_ Override events captured (user / site / justification / approval)

### Reg Malware Hits

<<MUST item:A.8.23:reg_malware_hits>>
_Why: 27002:8.23 — malicious content_

> _Standard text:_ Malware-category hits (signal for incident handoff)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Dashboard

<<SHOULD item:A.8.23:reg_dashboard>>
_Why: Operational visibility_

> _Standard text:_ Dashboard linked (coverage % / block rate / override volume)
