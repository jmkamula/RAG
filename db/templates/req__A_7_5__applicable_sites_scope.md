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

<<DOC_CONTROL>>

> The upstream that drives the register. Documents which sites are in scope and the threat catalogue considered per site type

## What this template gives you

This template helps you clearly identify which sites are included in your security program and outlines the specific threats relevant to each type of site. It ensures your risk register is based on accurate and current information.

## When to use it

Use this document whenever you need to define or update the scope of your sites and the threats they face. It should always reflect your current environment and be refreshed whenever there are changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill out thoughtfully.

## 1. Sites in scope (drawn from A.7.1 applicable-sites scope)

<<MUST item:A.7.5:scope_sites>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Threat catalogue considered (natural disasters per geography, intentional acts per threat-intel landscape, unintentional per ops history)

<<MUST item:A.7.5:scope_threat_catalogue>>
_Why: 27002:7.5 — threats_

<<GUIDANCE>>

<<TEXT>>

## 3. Geographic risk overlay (seismic zone, floodplain, climate band, civil-stability index per site location)

<<MUST item:A.7.5:scope_geography>>
_Why: Site-specific applicability_

<<GUIDANCE>>

<<TEXT>>

## 4. Sectoral drivers (data-centre industry standards, healthcare facility codes)

<<MUST item:A.7.5:scope_sectoral_drivers>>
_Why: 27002:7.5 — applicability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (climate event reclassification, new geography, sectoral standard update)

<<SHOULD item:A.7.5:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
