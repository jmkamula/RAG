---
leaf_id: req:A.7.11:applicable_sites_scope
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Sites for Utility Continuity Scope

> The upstream — which sites are in scope and what drives the continuity requirements per site

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Sites in scope (drawn from A.7.1 register — typically data centres + key office sites)

<<MUST item:A.7.11:scope_sites>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-site criticality tier (drives redundancy depth)

<<MUST item:A.7.11:scope_criticality>>
_Why: 27002:7.11 — proportional_

<<TEXT>>

## 3. Exclusions (cloud workloads → cloud provider handles utilities; co-located rack space → provider responsibility)

<<MUST item:A.7.11:scope_exclusions>>
_Why: 27002:7.11 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new site, criticality re-tier, BCP scope change)

<<SHOULD item:A.7.11:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
