---
leaf_id: req:A.7.2.5:applicable_scope
control_ref: A.7.2.5
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Applicable PIA Triggers Scope

<<DOC_CONTROL>>

> The upstream — which processing activities crossed the PIA-required threshold. Handles the Art.35.3 mandatory list + SA-published lists + org-specific high-risk indicators.

## What this template gives you

This template helps you clearly identify which of your data processing activities require a Privacy Impact Assessment, based on legal and organizational high-risk criteria.

## When to use it

Use this document whenever your activities might meet privacy risk thresholds, such as those listed in regulations or by your supervisory authority. Update it whenever your processing profile changes or new high-risk activities are introduced.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes around 10-15 minutes to fill in thoughtfully.

## 1. Art.35.3 mandatory categories mapped (systematic evaluation + Art.9/10 large-scale + systematic public monitoring)

<<MUST item:A.7.2.5:scope_art35_3_mandatory>>
_Why: GDPR Art.35.3_

<<GUIDANCE>>

<<TEXT>>

## 2. SA-published mandatory-DPIA lists per applicable jurisdiction (Art.35.4)

<<MUST item:A.7.2.5:scope_sa_lists>>
_Why: GDPR Art.35.4_

<<GUIDANCE>>

<<TEXT>>

## 3. Org-specific high-risk indicators (novel tech / vulnerable subjects / large-scale)

<<MUST item:A.7.2.5:scope_org_indicators>>
_Why: §7.2.5 — risks to PII principals_

<<GUIDANCE>>

<<TEXT>>

## 4. Out-of-scope processing (low-risk / legacy) with rationale

<<MUST item:A.7.2.5:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new AI model / new geo / new data source)

<<SHOULD item:A.7.2.5:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
