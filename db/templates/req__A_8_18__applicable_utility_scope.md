---
leaf_id: req:A.8.18:applicable_utility_scope
control_ref: A.8.18
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Utility Programs Scope

> Upstream — what counts as a privileged utility program in this org (debuggers / sysinternals / disk-rescue tools / SQL-direct-access / vendor diagnostic tools)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Utility classes enumerated (debuggers / sysinternals / disk tools / DB direct-access / vendor diagnostic / penetration-testing)

<<MUST item:A.8.18:scope_classes>>
_Why: 27002:8.18 — utility programs_

<<TEXT>>

## 2. Inclusion test (any program with 'can override control' capability is in scope, regardless of source)

<<MUST item:A.8.18:scope_inclusion_test>>
_Why: Boundary clarity_

<<TEXT>>

## 3. Exclusion rationale (admin tools already governed under A.8.2 PAM)

<<MUST item:A.8.18:scope_exclusions>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new utility class, new vendor diagnostic, new investigation tool)

<<SHOULD item:A.8.18:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
