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

> The upstream — which processing activities carry portability rights (Art.20 — consent-basis or contract-basis + automated). Copy-of-PII (Art.15.3) is broader — all subjects.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Art.15.3 (copy) universe — all subjects with PII processed

<<MUST item:A.7.3.8:scope_art_15_universe>>
_Why: GDPR Art.15.3_

<<TEXT>>

## 2. Art.20 (portability) universe — subset where basis=consent OR contract AND processing is automated

<<MUST item:A.7.3.8:scope_art_20_universe>>
_Why: GDPR Art.20.1_

<<TEXT>>

## 3. Derived/inferred data handling — original PII in scope; derived analytics + third-party enrichment typically out of scope

<<MUST item:A.7.3.8:scope_derived_data>>
_Why: EDPB Guidelines on right to data portability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new consent/contract-basis processing)

<<SHOULD item:A.7.3.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
