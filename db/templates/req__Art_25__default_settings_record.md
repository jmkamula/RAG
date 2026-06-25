---
leaf_id: req:Art.25:default_settings_record
control_ref: Art.25
standard_id: GDPR:2016/679
evidence_type: configuration_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Privacy-default configuration record (Art.25.2)

> Art.25.2 requires that, by default, only personal data which are necessary for each specific purpose are processed. This is a system property — a record listing the personal-data systems and confirming that their default settings minimise the amount, extent, storage period, and accessibility of personal data. ISO 27001 does not require this as a discrete artifact; Art.25.2 does.

<!-- TABLE-COLUMNS leaf:req:Art.25:default_settings_record -->
<!-- column: item:Art.25:default_systems_inventoried -->
<!-- column: item:Art.25:default_amount -->
<!-- column: item:Art.25:default_extent -->
<!-- column: item:Art.25:default_storage -->
<!-- column: item:Art.25:default_accessibility -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.25:default_settings_record -->
| Default Systems Inventoried | Default Amount | Default Extent | Default Storage | Default Accessibility |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.25:default_settings_record -->

## Column guidance — what to fill in

### Default Systems Inventoried

<<MUST item:Art.25:default_systems_inventoried>>
_Why: Art.25.2 — scope of obligation_

> _Standard text:_ Personal-data systems inventoried (links to Art.30 records)

### Default Amount

<<MUST item:Art.25:default_amount>>
_Why: Art.25.2 — amount of personal data collected_

> _Standard text:_ Default collection minimises the amount of personal data per purpose

### Default Extent

<<MUST item:Art.25:default_extent>>
_Why: Art.25.2 — extent of their processing_

> _Standard text:_ Default processing minimises the extent of processing per purpose

### Default Storage

<<MUST item:Art.25:default_storage>>
_Why: Art.25.2 — period of their storage_

> _Standard text:_ Default storage period set to the minimum necessary per purpose

### Default Accessibility

<<MUST item:Art.25:default_accessibility>>
_Why: Art.25.2 — accessibility_

> _Standard text:_ Default accessibility limited — data not made accessible to indefinite recipients without intervention

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Default Exception Register

<<SHOULD item:Art.25:default_exception_register>>
_Why: Demonstrates accountability_

> _Standard text:_ Exception register for higher-than-default settings with documented justification

### Default Review Dpia Link

<<SHOULD item:Art.25:default_review_dpia_link>>
_Why: Art.35 linkage_

> _Standard text:_ Reference to DPIA process for changes to defaults that increase risk
