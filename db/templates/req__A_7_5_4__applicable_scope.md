---
leaf_id: req:A.7.5.4:applicable_scope
control_ref: A.7.5.4
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Disclosure Contexts Scope

<<DOC_CONTROL>>

> The upstream — every context where PII is disclosed to a third party (normal course + investigation + audit + subpoena / court order).

## What this template gives you

This template helps you clearly define and document every situation where personal information is shared with third parties, including routine operations, investigations, audits, or legal requests.

## When to use it

Use this document whenever your organization’s activities match specific criteria that require you to disclose personal data externally, and update it whenever those circumstances change or new disclosure scenarios arise.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to provide details for three required elements and one recommended element.

## 1. Normal-course disclosures enumerated (recurring integrations)

<<MUST item:A.7.5.4:scope_normal_disclosures>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Investigation contexts (internal + external law enforcement)

<<MUST item:A.7.5.4:scope_investigation>>
_Why: §7.5.4 — lawful investigations_

<<GUIDANCE>>

<<TEXT>>

## 3. External audit disclosures (regulatory + customer audits)

<<MUST item:A.7.5.4:scope_audit>>
_Why: §7.5.4 — external audits_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new integration / new regulator inquiry)

<<SHOULD item:A.7.5.4:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
