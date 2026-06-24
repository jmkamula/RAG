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

> Upstream — which code repositories in scope, which languages, what tooling per language

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Repositories in scope (drawn from A.8.4 repo inventory)

<<MUST item:A.8.28:scope_repos>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Languages in use with tooling stack per language (SAST tool / linter / formatter)

<<MUST item:A.8.28:scope_languages>>
_Why: 27002:8.28 — appropriate_

<<TEXT>>

## 3. Exclusion rationale (vendor-shipped code / generated code with documented review path)

<<MUST item:A.8.28:scope_exclusions>>
_Why: Boundary clarity_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new language, new framework, new vulnerability class)

<<SHOULD item:A.8.28:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
