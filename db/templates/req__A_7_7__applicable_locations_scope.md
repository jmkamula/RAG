---
leaf_id: req:A.7.7:applicable_locations_scope
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Locations Scope

<<DOC_CONTROL>>

> The upstream — which locations are covered by clear-desk/clear-screen rules (offices, meeting rooms, lab benches, home offices, shared coworking spaces)

## What this template gives you

This template helps you clearly define which physical locations are covered by your clear-desk and clear-screen rules, such as offices, meeting rooms, labs, home offices, and shared coworking spaces.

## When to use it

Use this document whenever you need to clarify or update which areas your clear-desk and clear-screen policies apply to, and review it whenever your workspace arrangements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required elements about your covered locations.

## 1. Locations enumerated (offices, meeting rooms, lab benches, home offices, coworking spaces, customer-site visits)

<<MUST item:A.7.7:scope_locations>>
_Why: 27002:7.7 — relevant_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-location overlay against information-classification handled (Class III docs require locked storage, etc.)

<<MUST item:A.7.7:scope_classification_overlay>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 3. Screen-lock baseline per location (auto-lock after N minutes — varies by location risk)

<<MUST item:A.7.7:scope_screen_lock_baseline>>
_Why: 27002:7.7 — clear screen_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new location, new work-pattern — return to office, hot-desking)

<<SHOULD item:A.7.7:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
