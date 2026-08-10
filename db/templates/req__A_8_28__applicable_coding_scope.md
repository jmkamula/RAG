---
leaf_id: req:A.8.28:applicable_coding_scope
control_ref: A.8.28
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Secure Coding Scope

<<DOC_CONTROL>>

> Upstream — which code repositories in scope, which languages, what tooling per language

## What this template gives you

This template helps you clearly define which code repositories, programming languages, and security tools are included in your secure coding program. Use it to document your scope for compliance and audit purposes.

## When to use it

Complete this document whenever your secure coding requirements are triggered by your compliance profile, and update it as needed if your repositories, languages, or tooling change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes filling this out from scratch, as you'll need to provide details for each required element.

## 1. Repositories in scope (drawn from A.8.4 repo inventory)

<<MUST item:A.8.28:scope_repos>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Languages in use with tooling stack per language (SAST tool / linter / formatter)

<<MUST item:A.8.28:scope_languages>>
_Why: 27002:8.28 — appropriate_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusion rationale (vendor-shipped code / generated code with documented review path)

<<MUST item:A.8.28:scope_exclusions>>
_Why: Boundary clarity_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new language, new framework, new vulnerability class)

<<SHOULD item:A.8.28:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
