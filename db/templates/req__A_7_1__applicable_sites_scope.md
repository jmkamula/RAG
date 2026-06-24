---
leaf_id: req:A.7.1:applicable_sites_scope
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Sites Scope

> The upstream that drives the register. Documents the sites in scope, the operational/regulatory drivers for physical security per site type, and the exclusions (cloud-only deployments, home offices handled via A.6.7 + A.7.9)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Sites enumerated (HQ, regional offices, owned data centres, co-located rack space, lab facilities)

<<MUST item:A.7.1:scope_sites>>
_Why: 27002:7.1 — relevant_

<<TEXT>>

## 2. Exclusions stated explicitly (home offices → A.6.7 remote-working / A.7.9 off-premises; pure-cloud workloads with no physical footprint)

<<MUST item:A.7.1:scope_exclusions>>
_Why: 27002:7.1 — applicability_

<<TEXT>>

## 3. Sectoral/regulatory drivers per site type (data-centre PCI requirements, healthcare HIPAA, finance regulator inspection rights)

<<MUST item:A.7.1:scope_drivers>>
_Why: 27002:7.1 — applicable laws_

<<TEXT>>

## 4. Per-site information-classification footprint (drives which areas need which protection class — cross-link to A.5.12)

<<MUST item:A.7.1:scope_classification>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new site, sub-letting, M&A, sectoral re-classification)

<<SHOULD item:A.7.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
