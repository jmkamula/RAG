---
leaf_id: req:A.7.11:utility_register
control_ref: A.7.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Per-Site Utility Register

> The catalogue of critical utilities per site — feed type, redundancy in place, last test, provider, owner

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row site + utility pair

<<MUST item:A.7.11:reg_site_utility>>
_Why: 27002:7.11 — supporting utilities_

<<TEXT>>

## 2. Per-row redundancy in place (matches the policy's required redundancy)

<<MUST item:A.7.11:reg_redundancy_in_place>>
_Why: 27002:7.11 — protected_

<<TEXT>>

## 3. Per-row provider with SLA reference

<<MUST item:A.7.11:reg_provider>>
_Why: 27002:7.11 — maintenance_

<<TEXT>>

## 4. Per-row last test date and outcome

<<MUST item:A.7.11:reg_last_test>>
_Why: Continuity validation_

<<TEXT>>

## 5. Per-row next-test date scheduled

<<MUST item:A.7.11:reg_next_test>>
_Why: Planning_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row autonomous-runtime stat (UPS minutes, generator fuel days)

<<SHOULD item:A.7.11:reg_runtime>>
_Why: Realism check_

<<TEXT>>
