---
leaf_id: req:A.7.2.8:applicable_scope
control_ref: A.7.2.8
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# RoPA Coverage Scope

<<DOC_CONTROL>>

> The upstream — coverage denominator for the RoPA. Every in-scope activity from A.7.2.1 purpose register must have a corresponding RoPA entry.

## What this template gives you

This template helps you clearly define which activities are covered by your Record of Processing Activities (RoPA), ensuring that every relevant process is properly documented for privacy compliance.

## When to use it

Use this whenever your organization’s activities match the criteria for RoPA documentation, especially after changes to your processing purposes or when updating your privacy profile. Refresh the scope note as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on the number of activities you need to review and describe.

## 1. Covered activities enumerated (all processing activities the org performs)

<<MUST item:A.7.2.8:scope_covered_activities>>
_Why: §7.2.8 — activities that the organization performs_

<<GUIDANCE>>

<<TEXT>>

## 2. Coverage test — RoPA rowcount reconciles against A.7.2.1 purpose register + system inventory

<<MUST item:A.7.2.8:scope_coverage_test>>
_Why: Integrity_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusions — anonymous / aggregate processing not in RoPA with rationale

<<MUST item:A.7.2.8:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new product line / new geo / M&A activity)

<<SHOULD item:A.7.2.8:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
