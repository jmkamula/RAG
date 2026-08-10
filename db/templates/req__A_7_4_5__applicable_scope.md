---
leaf_id: req:A.7.4.5:applicable_scope
control_ref: A.7.4.5
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable End-of-Processing Scope

<<DOC_CONTROL>>

> The upstream — which processing activities have foreseeable end-points (customer churn / consent withdrawal / retention lapse) and which are open-ended (ongoing customer relationships).

## What this template gives you

This template helps you clearly define which of your data processing activities have a foreseeable end-point and which continue as long as your customer relationships do. It's useful for understanding and documenting your data retention responsibilities.

## When to use it

Use this document whenever your business activities match situations where you need to clarify the end or continuation of data processing, such as customer churn or consent withdrawal. Update it as needed when your processing activities or customer relationships change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended element.

## 1. End-trigger enumeration per activity type

<<MUST item:A.7.4.5:scope_end_triggers>>
_Why: §7.4.5 — no longer necessary_

<<GUIDANCE>>

<<TEXT>>

## 2. Backup + DR system coverage (PII in backups within scope; deletion propagation policy documented)

<<MUST item:A.7.4.5:scope_backup_coverage>>
_Why: Comprehensiveness_

<<GUIDANCE>>

<<TEXT>>

## 3. Exceptions (legal-hold / active litigation / regulator inspection) with rationale

<<MUST item:A.7.4.5:scope_exceptions>>
_Why: GDPR Art.17.3_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (retention policy change / new activity)

<<SHOULD item:A.7.4.5:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
