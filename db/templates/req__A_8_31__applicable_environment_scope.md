---
leaf_id: req:A.8.31:applicable_environment_scope
control_ref: A.8.31
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 2
should_count: 1
---

# Applicable Environment Separation Scope

<<DOC_CONTROL>>

> Upstream — which platform domains have separated environments. SDLC platform yes. Internal-tools dev/prod proportional. Vendor SaaS sandboxes governed via A.5.19/A.5.21

## What this template gives you

This template helps you clearly define which parts of your technology environment are separated for development, testing, and production, making it easier to show compliance with environment separation requirements.

## When to use it

Use this document whenever your systems or applications need to demonstrate separated environments, especially if your setup or compliance profile changes. Update it as needed to stay accurate.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 20 to 30 minutes completing this from scratch, as you'll need to describe two key elements about your environment separation.

## 1. Platforms in scope with environment-tiering rules per platform

<<MUST item:A.8.31:scope_platforms>>
_Why: 27002:8.31 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 2. Exclusion rationale (e.g. SaaS-only platforms with vendor-managed environments)

<<MUST item:A.8.31:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new platform, new environment class)

<<SHOULD item:A.8.31:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
