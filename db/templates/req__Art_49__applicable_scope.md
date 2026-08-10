---
leaf_id: req:Art.49:applicable_scope
control_ref: Art.49
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Derogations Scope

<<DOC_CONTROL>>

> The upstream — which Art.49.1 derogations the org actually relies on, with strict-construction analysis

## What this template gives you

This template helps you clearly document which specific GDPR Article 49.1 derogations your organization relies on, along with a concise explanation of why each applies.

## When to use it

Use this whenever your data transfer activities match situations where GDPR derogations are needed, and update it whenever your reliance on these derogations changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes around 10-15 minutes to write.

## 1. Derogations actually relied on enumerated (most orgs: a explicit consent + b contract; some: e legal claims)

<<MUST item:Art.49:scope_derogations_used>>
_Why: Art.49.1_

<<GUIDANCE>>

<<TEXT>>

## 2. Derogations explicitly NOT relied on (rationale)

<<MUST item:Art.49:scope_excluded>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 3. Operational interpretation of 'non-repetitive' for last-resort derogation

<<MUST item:Art.49:scope_repetitive_test>>
_Why: Art.49.1 second paragraph_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new business case requiring derogation, regulatory change)

<<SHOULD item:Art.49:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
