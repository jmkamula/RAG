---
leaf_id: req:A.7.3.1:applicable_scope
control_ref: A.7.3.1
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Jurisdictions + Subjects Scope

<<DOC_CONTROL>>

> The upstream — which jurisdictions bind the org (establishment / target-market / monitoring) and which subject categories are covered. Determines the size of the A.7.3.1 obligation catalog.

## What this template gives you

This template helps you clearly define which countries' laws apply to your organization and which types of personal data or subjects are covered. It's useful for understanding the full scope of your privacy compliance obligations.

## When to use it

Use this document whenever your business activities or locations change in a way that might affect which jurisdictions or data subjects are relevant. Update it as needed to keep your compliance scope accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to identify and describe three required elements related to jurisdictions and subject categories.

## 1. Applicable jurisdictions listed with basis per row

<<MUST item:A.7.3.1:scope_jurisdictions>>
_Why: GDPR Art.3 territorial scope + equivalents_

<<GUIDANCE>>

<<TEXT>>

## 2. Subject categories per jurisdiction (customers / employees / minors / patients / etc.)

<<MUST item:A.7.3.1:scope_subject_categories>>
_Why: §7.3.1 — related to processing_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded jurisdictions / subjects with rationale

<<MUST item:A.7.3.1:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new geo entry / new subject category / new regulation)

<<SHOULD item:A.7.3.1:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
