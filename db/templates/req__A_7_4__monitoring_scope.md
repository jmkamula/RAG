---
leaf_id: req:A.7.4:monitoring_scope
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Monitoring Scope

> The upstream that drives the procedure. Documents which sites and which areas within sites are monitored, by which mechanisms, and the rationale per area

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Sites covered by monitoring (drawn from A.7.1 applicable-sites scope)

<<MUST item:A.7.4:scope_sites_covered>>
_Why: 27002:7.4 — premises_

<<TEXT>>

## 2. Per-site area-to-mechanism mapping (which CCTV cameras cover which areas, which IDS sensors per zone)

<<MUST item:A.7.4:scope_area_mapping>>
_Why: 27002:7.4 — monitored_

<<TEXT>>

## 3. Known blind spots identified with compensating controls (e.g. patrol coverage where CCTV impractical)

<<MUST item:A.7.4:scope_blind_spots>>
_Why: Honest scoping_

<<TEXT>>

## 4. Legal constraints on monitoring (changing-area exclusions, employee-privacy minima per jurisdiction)

<<MUST item:A.7.4:scope_legal_constraints>>
_Why: 27002:7.4 — applicable laws_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new site, new building wing, employee-privacy regulator action)

<<SHOULD item:A.7.4:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
