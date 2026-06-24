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

> Upstream — which platform domains have separated environments. SDLC platform yes. Internal-tools dev/prod proportional. Vendor SaaS sandboxes governed via A.5.19/A.5.21

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Platforms in scope with environment-tiering rules per platform

<<MUST item:A.8.31:scope_platforms>>
_Why: 27002:8.31 — appropriate_

<<TEXT>>

## 2. Exclusion rationale (e.g. SaaS-only platforms with vendor-managed environments)

<<MUST item:A.8.31:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new platform, new environment class)

<<SHOULD item:A.8.31:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
