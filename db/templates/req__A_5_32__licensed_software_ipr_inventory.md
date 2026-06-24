---
leaf_id: req:A.5.32:licensed_software_ipr_inventory
control_ref: A.5.32
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Licensed Software and IPR Inventory

> The register at the heart of IPR protection. Without an inventory of what's licensed, what's open-source, what's internally created, A.5.32 enforcement is theoretical. The inventory tracks entitlements, expiry, attribution obligations and ownership for each entry

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Inventory of licensed commercial software with entitlements (seats / cores / sites) and expiry per licence

<<MUST item:A.5.32:licensed_inventory>>
_Why: 27002:5.32 — protect_

<<TEXT>>

## 2. Open-source components inventory with licence type per component (drives attribution and obligation handling — feeds SBOM)

<<MUST item:A.5.32:opensource_inventory>>
_Why: 27002:5.32 — third-party IPR_

<<TEXT>>

## 3. Organisation-owned IPR entries (trademarks, patents, trade secrets, copyrighted works) with status and protection scope

<<MUST item:A.5.32:owned_ipr>>
_Why: 27002:5.32 — own IPR_

<<TEXT>>

## 4. Linkage to A.5.9 asset register — each licensed item is also an information asset; the two registers must not drift

<<MUST item:A.5.32:asset_link>>
_Why: A.5.9 coherence_

<<TEXT>>

## 5. Named owner per entry (procurement / legal / engineering lead) responsible for renewal and compliance

<<MUST item:A.5.32:owner_per_entry>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Renewal dates tracked with lead-time alerts (so expiring licences are renewed before lapse)

<<SHOULD item:A.5.32:renewal_tracking>>
_Why: Continuity of use_

<<TEXT>>

### 2. Link to SBOM tooling output for open-source components (A.8.29 secure-development linkage)

<<SHOULD item:A.5.32:sbom_link>>
_Why: Tool-driven currency_

<<TEXT>>
