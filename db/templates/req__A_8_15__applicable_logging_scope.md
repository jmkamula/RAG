---
leaf_id: req:A.8.15:applicable_logging_scope
control_ref: A.8.15
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Logging Scope

<<DOC_CONTROL>>

> Upstream — which systems must emit which log classes, what regulatory drivers apply per class (GDPR Art.30 audit trail / sector-specific requirements)

## What this template gives you

This template helps you clearly define which systems need to generate specific types of logs and explains the regulatory reasons for each, such as GDPR or industry-specific rules.

## When to use it

Use this document whenever you need to outline your logging requirements for your environment, and update it whenever there are changes to your systems or regulations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, as each required section takes roughly 10 to 15 minutes to fill out.

## 1. Systems in scope enumerated (drawn from A.5.9 asset register)

<<MUST item:A.8.15:scope_systems>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Log classes required per system class (auth / access / change / fault)

<<MUST item:A.8.15:scope_log_classes>>
_Why: 27002:8.15 — record activities_

<<GUIDANCE>>

<<TEXT>>

## 3. Per-class regulatory drivers (PCI / HIPAA / GDPR Art.30 / DORA / sector audit)

<<MUST item:A.8.15:scope_regulatory_drivers>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

## 4. Exclusion rationale + compensating controls per excluded class

<<MUST item:A.8.15:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new system, new regulator, new attack pattern)

<<SHOULD item:A.8.15:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
