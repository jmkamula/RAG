---
leaf_id: req:A.5.33:records_categories_scope
control_ref: A.5.33
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Records Categories Scope

<<DOC_CONTROL>>

> The upstream that drives the schedule. Documents the business activities, legal/regulatory drivers, and data categories that determine what counts as a 'record' for the organisation. ISO 27002:2022 § 5.33 expects organisations to know which records they need to keep before claiming to protect them. Drift between the scope and the schedule is the audit failure mode this leaf catches — it surfaces missing classes (e.g., 'we started processing health data; where are the HIPAA records?')

## What this template gives you

This template helps you clearly define which business activities, legal requirements, and types of data are considered official records for your organization. It ensures you know exactly what needs to be protected and retained.

## When to use it

Use this document whenever you need to clarify or update what counts as a record in your organization. Review and refresh it whenever your business activities or data types change, or as needed to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes roughly 10-15 minutes to fill in thoughtfully.

## 1. Business activities considered (HR/employment, finance/tax, sales/customer, operations/security, regulated activities — each may generate distinct record classes)

<<MUST item:A.5.33:scope_business_activities>>
_Why: 27002:5.33 — applicability_

<<GUIDANCE>>

<<TEXT>>

## 2. Legal/regulatory drivers enumerated (statutes mandating record-keeping: corporate law, tax law, employment law, sectoral regulations, GDPR Art.30, AML, etc.) — cross-link to A.5.31 register

<<MUST item:A.5.33:scope_legal_drivers>>
_Why: 27002:5.33 — legal driver_

<<GUIDANCE>>

<<TEXT>>

## 3. Personal/sensitive/regulated data categories handled (drives PII overlay and special-category retention)

<<MUST item:A.5.33:scope_data_categories>>
_Why: GDPR/sectoral linkage_

<<GUIDANCE>>

<<TEXT>>

## 4. Jurisdictions covered (each may impose different minimum-retention or right-to-erasure constraints — HQ, places of business, data-residency destinations)

<<MUST item:A.5.33:scope_jurisdictions>>
_Why: 27002:5.33 — relevant_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.5.31 applicable-obligations scope — same drivers, separate registers; the two should stay aligned

<<SHOULD item:A.5.33:scope_obligations_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

### 2. Trigger list for re-scoping (new geography, new service line, M&A, new regulated activity — adding scope must trigger a schedule update)

<<SHOULD item:A.5.33:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
