---
leaf_id: req:A.7.5:applicable_sites_scope
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Sites and Threat Catalogue Scope

> The upstream that drives the register. Documents which sites are in scope and the threat catalogue considered per site type

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Sites in scope (drawn from A.7.1 applicable-sites scope)

<<MUST item:A.7.5:scope_sites>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Threat catalogue considered (natural disasters per geography, intentional acts per threat-intel landscape, unintentional per ops history)

<<MUST item:A.7.5:scope_threat_catalogue>>
_Why: 27002:7.5 — threats_

<<TEXT>>

## 3. Geographic risk overlay (seismic zone, floodplain, climate band, civil-stability index per site location)

<<MUST item:A.7.5:scope_geography>>
_Why: Site-specific applicability_

<<TEXT>>

## 4. Sectoral drivers (data-centre industry standards, healthcare facility codes)

<<MUST item:A.7.5:scope_sectoral_drivers>>
_Why: 27002:7.5 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (climate event reclassification, new geography, sectoral standard update)

<<SHOULD item:A.7.5:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
