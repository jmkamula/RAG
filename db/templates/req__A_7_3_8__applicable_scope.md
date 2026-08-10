---
leaf_id: req:A.7.3.8:applicable_scope
control_ref: A.7.3.8
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Copy Contexts Scope

<<DOC_CONTROL>>

> The upstream — which processing activities carry portability rights (Art.20 — consent-basis or contract-basis + automated). Copy-of-PII (Art.15.3) is broader — all subjects.

## What this template gives you

This template helps you clearly define which of your data processing activities are covered by data portability rights and which are subject to broader access rights for individuals.

## When to use it

Use this document whenever your organization needs to clarify which processing activities allow individuals to request their data, especially when your data handling profile changes or new activities are added.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended detail.

## 1. Art.15.3 (copy) universe — all subjects with PII processed

<<MUST item:A.7.3.8:scope_art_15_universe>>
_Why: GDPR Art.15.3_

<<GUIDANCE>>

<<TEXT>>

## 2. Art.20 (portability) universe — subset where basis=consent OR contract AND processing is automated

<<MUST item:A.7.3.8:scope_art_20_universe>>
_Why: GDPR Art.20.1_

<<GUIDANCE>>

<<TEXT>>

## 3. Derived/inferred data handling — original PII in scope; derived analytics + third-party enrichment typically out of scope

<<MUST item:A.7.3.8:scope_derived_data>>
_Why: EDPB Guidelines on right to data portability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new consent/contract-basis processing)

<<SHOULD item:A.7.3.8:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
