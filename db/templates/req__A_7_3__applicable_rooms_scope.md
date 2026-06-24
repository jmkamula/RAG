---
leaf_id: req:A.7.3:applicable_rooms_scope
control_ref: A.7.3
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Rooms Scope

> The upstream that drives the register. Documents which rooms across all sites are in scope and what drives the classification of each

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Inventory of rooms across all sites in scope (from facilities inventory)

<<MUST item:A.7.3:scope_rooms_inventory>>
_Why: 27002:7.3 — facilities_

<<TEXT>>

## 2. Drivers for room classification (information class stored/processed, equipment held, personnel access level required)

<<MUST item:A.7.3:scope_classification_drivers>>
_Why: 27002:7.3 — designed_

<<TEXT>>

## 3. Exclusions stated (common areas, lobbies, parking — not in 'rooms' scope but covered by A.7.1 perimeter)

<<MUST item:A.7.3:scope_exclusions>>
_Why: 27002:7.3 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (renovation, repurposing, new tenant fit-out)

<<SHOULD item:A.7.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
