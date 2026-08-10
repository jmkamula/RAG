---
leaf_id: req:A.7.3.4:applicable_scope
control_ref: A.7.3.4
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Consent-Basis Activities Scope

<<DOC_CONTROL>>

> The upstream — which activities rely on consent (from A.7.2.3 / A.7.2.4 registers) and therefore need withdrawal channels. Non-consent bases (contract, legal obligation) don't populate this scope.

## What this template gives you

This template helps you clearly identify which of your activities depend on user consent, making it easier to manage withdrawal options and stay compliant with privacy standards.

## When to use it

Use this document whenever your activities involve collecting or processing personal data based on consent, especially when your privacy profile or data processing activities change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, depending on how many activities you need to review and document.

## 1. Consent-based activities enumerated (link to A.7.2.2 lawful basis register)

<<MUST item:A.7.3.4:scope_consent_activities>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-activity collection channel → withdrawal channel map

<<MUST item:A.7.3.4:scope_channel_map>>
_Why: §7.3.4 — same as collection_

<<GUIDANCE>>

<<TEXT>>

## 3. Jurisdiction-specific variations (some jurisdictions restrict when withdrawal is possible)

<<MUST item:A.7.3.4:scope_jurisdiction_variance>>
_Why: §7.3.4 — some jurisdictions impose restrictions_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new consent-based activity)

<<SHOULD item:A.7.3.4:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
