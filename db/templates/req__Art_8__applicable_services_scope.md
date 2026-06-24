---
leaf_id: req:Art.8:applicable_services_scope
control_ref: Art.8
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Information-Society Services Scope

> The upstream — which services count as 'offered directly to a child' under Art.8. Critical for B2B / professional-service tenants who may incidentally process minors' data but don't 'offer to' them directly (e.g. a parent purchases on a family-account UI)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Services in scope enumerated (those advertised to / used by minors directly)

<<MUST item:Art.8:scope_in_scope_services>>
_Why: Art.8.1 — offered directly_

<<TEXT>>

## 2. Incidental-minor-data scenarios stated (and why they don't trigger Art.8 — e.g. parent account holder)

<<MUST item:Art.8:scope_incidental_processing>>
_Why: Defensibility_

<<TEXT>>

## 3. Member State age threshold variations (where org operates in multiple Member States)

<<MUST item:Art.8:scope_member_state_thresholds>>
_Why: Art.8.1 — Member State law_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new product line touching minors, new Member State entry)

<<SHOULD item:Art.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
