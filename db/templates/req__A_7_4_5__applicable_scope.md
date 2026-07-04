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

> The upstream — which processing activities have foreseeable end-points (customer churn / consent withdrawal / retention lapse) and which are open-ended (ongoing customer relationships).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. End-trigger enumeration per activity type

<<MUST item:A.7.4.5:scope_end_triggers>>
_Why: §7.4.5 — no longer necessary_

<<TEXT>>

## 2. Backup + DR system coverage (PII in backups within scope; deletion propagation policy documented)

<<MUST item:A.7.4.5:scope_backup_coverage>>
_Why: Comprehensiveness_

<<TEXT>>

## 3. Exceptions (legal-hold / active litigation / regulator inspection) with rationale

<<MUST item:A.7.4.5:scope_exceptions>>
_Why: GDPR Art.17.3_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (retention policy change / new activity)

<<SHOULD item:A.7.4.5:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
