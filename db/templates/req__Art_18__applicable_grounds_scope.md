---
leaf_id: req:Art.18:applicable_grounds_scope
control_ref: Art.18
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Restriction Grounds Scope

<<DOC_CONTROL>>

> The upstream — operational interpretation of the four Art.18.1 grounds, what the restriction looks like per data class, exception handling per Art.18.2

## What this template gives you

This template helps you clearly define which restriction grounds under GDPR Article 18.1 apply to your data, how these restrictions work for different types of data, and how to handle exceptions.

## When to use it

Use this document whenever you need to outline or review the scope of data processing restrictions in your environment. Update it as needed to stay current with any changes in your data or processes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as each required section takes roughly 10-15 minutes to write.

## 1. Art.18.1 grounds catalog (a-d) with practical examples

<<MUST item:Art.18:scope_grounds_catalog>>
_Why: Art.18.1_

<<GUIDANCE>>

<<TEXT>>

## 2. Data classes covered (each with implementation pattern — flag / partition / lock)

<<MUST item:Art.18:scope_data_classes>>
_Why: Implementation_

<<GUIDANCE>>

<<TEXT>>

## 3. Art.18.2 exceptions enumerated (subject consent / legal claims / protection of rights / important public interest)

<<MUST item:Art.18:scope_art18_2_exceptions>>
_Why: Art.18.2_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new data class, new system surfacing)

<<SHOULD item:Art.18:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
