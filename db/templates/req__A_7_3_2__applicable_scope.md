---
leaf_id: req:A.7.3.2:applicable_scope
control_ref: A.7.3.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Notice Contexts Scope

<<DOC_CONTROL>>

> The upstream — which processing contexts require a notice (direct collection vs indirect / customer vs employee / EU vs non-EU) and which fields differ per context.

## What this template gives you

This template helps you clearly define which situations require a privacy notice, such as collecting information directly from customers or employees, and highlights any differences based on region or context.

## When to use it

Use this document whenever your organization needs to clarify when and how privacy notices apply, especially if your data processing activities or business profile change over time.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and consider different processing scenarios.

## 1. Notice contexts enumerated (direct / indirect / cookie / marketing / employee / minor / etc.)

<<MUST item:A.7.3.2:scope_contexts>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-context field differences (e.g. indirect collection triggers additional Art.14 fields; children triggers plain-language obligation)

<<MUST item:A.7.3.2:scope_field_diffs>>
_Why: §7.3.2 — target audience_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded contexts with rationale

<<MUST item:A.7.3.2:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new processing activity / new audience segment)

<<SHOULD item:A.7.3.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
