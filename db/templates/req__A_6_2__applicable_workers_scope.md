---
leaf_id: req:A.6.2:applicable_workers_scope
control_ref: A.6.2
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Worker Categories Scope

<<DOC_CONTROL>>

> The upstream that drives which template variants exist. Documents the worker categories the org engages (employees, contractors, interns, secondees, agency workers) and which template each uses

## What this template gives you

This template helps you clearly identify all the types of workers your organization engages and ensures each group is matched with the right compliance documentation.

## When to use it

Use this whenever you need to define or update which worker categories are present in your organization, and review it whenever your staffing structure changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to fill out.

## 1. Worker categories enumerated (employees, fixed-term, contractors, interns, secondees from suppliers, agency workers)

<<MUST item:A.6.2:scope_worker_categories>>
_Why: 27002:6.2 — relevant workers_

<<GUIDANCE>>

<<TEXT>>

## 2. Template-to-category mapping (which categories use the master template; which use a variant — contractor-lite NDA-only path is common)

<<MUST item:A.6.2:scope_template_mapping>>
_Why: 27002:6.2 — applicability_

<<GUIDANCE>>

<<TEXT>>

## 3. Jurisdictions covered (employment-law variations per country drive local-language and clause variants)

<<MUST item:A.6.2:scope_jurisdictions>>
_Why: 27002:6.2 — applicable laws_

<<GUIDANCE>>

<<TEXT>>

## 4. Supplier-worker overlap noted (contractors brought in via suppliers may sign supplier-NDA + org-NDA both — cross-link to A.5.20 supplier agreement)

<<MUST item:A.6.2:scope_supplier_overlap>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new worker category — gig workers, M&A bringing new categories, new geography with distinct employment law)

<<SHOULD item:A.6.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
