---
leaf_id: req:Art.85:applicable_activities_scope
control_ref: Art.85
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Art.85 Activities Scope

<<DOC_CONTROL>>

> The upstream — which of the organisation's processing activities fall under Art.85 categories (journalism / academic / artistic / literary expression). Critical for tenants with mixed activities (e.g. a publisher that also runs e-commerce — only the editorial activities qualify)

## What this template gives you

This template helps you clearly identify which of your organisation’s activities fall under the special GDPR rules for journalism, academic, artistic, or literary expression. It’s especially useful if your business has both editorial and non-editorial operations.

## When to use it

Use this document whenever your organisation’s activities might include journalism, academic, artistic, or literary work, especially if you also run other types of business. Update it whenever your activities change or new types of work are added.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to describe and categorise at least three key activities.

## 1. Activities in scope enumerated, classified by Art.85 category (journalism / academic / artistic / literary)

<<MUST item:Art.85:scope_in_scope_activities>>
_Why: Art.85.1 — purposes enumerated_

<<GUIDANCE>>

<<TEXT>>

## 2. Adjacent activities explicitly out of scope (e.g. subscriber-management, advertising — these don't qualify as expression)

<<MUST item:Art.85:scope_out_of_scope_activities>>
_Why: Defensibility — scope boundary_

<<GUIDANCE>>

<<TEXT>>

## 3. List of Member States in which Art.85-qualifying activities occur (drives the per-jurisdiction lookup workload)

<<MUST item:Art.85:scope_jurisdiction_list>>
_Why: Art.85.2 — per-Member-State law_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new editorial product, expansion into new Member State, acquisition of journalism arm)

<<SHOULD item:Art.85:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
