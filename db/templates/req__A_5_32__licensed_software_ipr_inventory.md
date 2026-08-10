---
leaf_id: req:A.5.32:licensed_software_ipr_inventory
control_ref: A.5.32
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Licensed Software and IPR Inventory

<<DOC_CONTROL>>

> The register at the heart of IPR protection. Without an inventory of what's licensed, what's open-source, what's internally created, A.5.32 enforcement is theoretical. The inventory tracks entitlements, expiry, attribution obligations and ownership for each entry

<!-- TABLE-COLUMNS leaf:req:A.5.32:licensed_software_ipr_inventory -->
<!-- column: item:A.5.32:licensed_inventory -->
<!-- column: item:A.5.32:opensource_inventory -->
<!-- column: item:A.5.32:owned_ipr -->
<!-- column: item:A.5.32:asset_link -->
<!-- column: item:A.5.32:owner_per_entry -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all your licensed, open-source, and internally developed software, including ownership, entitlements, expiry dates, and any obligations. It’s essential for protecting your intellectual property and meeting compliance requirements.

## When to use it

Use this register at all times to maintain an up-to-date inventory of your software and intellectual property. Update it whenever you add, change, or retire software, or whenever your entitlements or obligations change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each software entry. Completing the initial inventory may take a few hours, depending on how many software products you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.32:licensed_software_ipr_inventory -->
| Licensed Inventory | Opensource Inventory | Owned Ipr | Asset Link | Owner Per Entry |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.32:licensed_software_ipr_inventory -->

## Column guidance — what to fill in

### Licensed Inventory

<<MUST item:A.5.32:licensed_inventory>>
_Why: 27002:5.32 — protect_

> _Standard text:_ Inventory of licensed commercial software with entitlements (seats / cores / sites) and expiry per licence

<<GUIDANCE>>

### Opensource Inventory

<<MUST item:A.5.32:opensource_inventory>>
_Why: 27002:5.32 — third-party IPR_

> _Standard text:_ Open-source components inventory with licence type per component (drives attribution and obligation handling — feeds SBOM)

<<GUIDANCE>>

### Owned Ipr

<<MUST item:A.5.32:owned_ipr>>
_Why: 27002:5.32 — own IPR_

> _Standard text:_ Organisation-owned IPR entries (trademarks, patents, trade secrets, copyrighted works) with status and protection scope

<<GUIDANCE>>

### Asset Link

<<MUST item:A.5.32:asset_link>>
_Why: A.5.9 coherence_

> _Standard text:_ Linkage to A.5.9 asset register — each licensed item is also an information asset; the two registers must not drift

<<GUIDANCE>>

### Owner Per Entry

<<MUST item:A.5.32:owner_per_entry>>
_Why: Accountability_

> _Standard text:_ Named owner per entry (procurement / legal / engineering lead) responsible for renewal and compliance

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Renewal Tracking

<<SHOULD item:A.5.32:renewal_tracking>>
_Why: Continuity of use_

> _Standard text:_ Renewal dates tracked with lead-time alerts (so expiring licences are renewed before lapse)

<<GUIDANCE>>

### Sbom Link

<<SHOULD item:A.5.32:sbom_link>>
_Why: Tool-driven currency_

> _Standard text:_ Link to SBOM tooling output for open-source components (A.8.29 secure-development linkage)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
