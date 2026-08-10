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

<<DOC_CONTROL>>

> The upstream — which sites are in scope and what drives the continuity requirements per site

## What this template gives you

This template helps you clearly identify which of your sites are included in your utility continuity planning and explains why each site is covered.

## When to use it

Use this document whenever you need to define or update the list of sites that fall under your utility continuity requirements, and refresh it whenever there are changes to your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in.

## 1. Sites in scope (drawn from A.7.1 register — typically data centres + key office sites)

<<MUST item:A.7.11:scope_sites>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-site criticality tier (drives redundancy depth)

<<MUST item:A.7.11:scope_criticality>>
_Why: 27002:7.11 — proportional_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusions (cloud workloads → cloud provider handles utilities; co-located rack space → provider responsibility)

<<MUST item:A.7.11:scope_exclusions>>
_Why: 27002:7.11 — applicability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new site, criticality re-tier, BCP scope change)

<<SHOULD item:A.7.11:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
