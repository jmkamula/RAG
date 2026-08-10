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

<<DOC_CONTROL>>

> The upstream that drives the register. Documents the sites in scope, the operational/regulatory drivers for physical security per site type, and the exclusions (cloud-only deployments, home offices handled via A.6.7 + A.7.9)

## What this template gives you

This template helps you clearly define which physical sites are covered by your security program, why each site type is included, and any exceptions such as cloud-only or home office setups.

## When to use it

Use this document whenever you need to outline or update the list of sites in your security scope. It should be reviewed and refreshed whenever your environment changes or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes roughly 10-15 minutes to fill in thoughtfully.

## 1. Sites enumerated (HQ, regional offices, owned data centres, co-located rack space, lab facilities)

<<MUST item:A.7.1:scope_sites>>
_Why: 27002:7.1 — relevant_

<<GUIDANCE>>

<<TEXT>>

## 2. Exclusions stated explicitly (home offices → A.6.7 remote-working / A.7.9 off-premises; pure-cloud workloads with no physical footprint)

<<MUST item:A.7.1:scope_exclusions>>
_Why: 27002:7.1 — applicability_

<<GUIDANCE>>

<<TEXT>>

## 3. Sectoral/regulatory drivers per site type (data-centre PCI requirements, healthcare HIPAA, finance regulator inspection rights)

<<MUST item:A.7.1:scope_drivers>>
_Why: 27002:7.1 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

## 4. Per-site information-classification footprint (drives which areas need which protection class — cross-link to A.5.12)

<<MUST item:A.7.1:scope_classification>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new site, sub-letting, M&A, sectoral re-classification)

<<SHOULD item:A.7.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
