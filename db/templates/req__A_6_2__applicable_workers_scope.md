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

> The upstream that drives which template variants exist. Documents the worker categories the org engages (employees, contractors, interns, secondees, agency workers) and which template each uses

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Worker categories enumerated (employees, fixed-term, contractors, interns, secondees from suppliers, agency workers)

<<MUST item:A.6.2:scope_worker_categories>>
_Why: 27002:6.2 — relevant workers_

<<TEXT>>

## 2. Template-to-category mapping (which categories use the master template; which use a variant — contractor-lite NDA-only path is common)

<<MUST item:A.6.2:scope_template_mapping>>
_Why: 27002:6.2 — applicability_

<<TEXT>>

## 3. Jurisdictions covered (employment-law variations per country drive local-language and clause variants)

<<MUST item:A.6.2:scope_jurisdictions>>
_Why: 27002:6.2 — applicable laws_

<<TEXT>>

## 4. Supplier-worker overlap noted (contractors brought in via suppliers may sign supplier-NDA + org-NDA both — cross-link to A.5.20 supplier agreement)

<<MUST item:A.6.2:scope_supplier_overlap>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new worker category — gig workers, M&A bringing new categories, new geography with distinct employment law)

<<SHOULD item:A.6.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
