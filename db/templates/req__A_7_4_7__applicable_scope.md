---
leaf_id: req:A.7.4.7:applicable_scope
control_ref: A.7.4.7
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Retention Contexts Scope

> The upstream — which PII categories × activity combinations require dedicated retention schedules vs which follow defaults.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Regulated PII categories (health / financial / employment / tax / other jurisdiction-specific)

<<MUST item:A.7.4.7:scope_regulated_data>>
_Why: §7.4.7 — legal + regulatory_

<<TEXT>>

## 2. Business PII categories with business retention rationale

<<MUST item:A.7.4.7:scope_business_data>>
_Why: §7.4.7 — business requirements_

<<TEXT>>

## 3. Default retention period for uncategorised PII

<<MUST item:A.7.4.7:scope_default_period>>
_Why: Comprehensiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new regulation / new business requirement)

<<SHOULD item:A.7.4.7:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
