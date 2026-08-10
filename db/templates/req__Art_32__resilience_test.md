---
leaf_id: req:Art.32:resilience_test
control_ref: Art.32
standard_id: GDPR:2016/679
evidence_type: test_log
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 3
should_count: 1
table_shape: true
---

# Periodic resilience and restoration test record

<<DOC_CONTROL>>

> Art.32.1.d requires a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of processing.

<!-- TABLE-COLUMNS leaf:req:Art.32:resilience_test -->
<!-- column: item:Art.32:resilience_test_scope -->
<!-- column: item:Art.32:resilience_test_recent -->
<!-- column: item:Art.32:resilience_test_findings -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of your regular tests and checks to make sure your security measures are working as intended. It’s useful for tracking compliance with GDPR requirements on data protection.

## When to use it

Use this template whenever you conduct resilience and restoration tests in your environment, and update it about once a year to stay current with your compliance obligations.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 30 to 45 minutes filling in the required details for each test from scratch, with more time needed if you have multiple tests to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.32:resilience_test -->
| Resilience Test Scope | Resilience Test Recent | Resilience Test Findings |
|---|---|---|
|          |          |          |
|          |          |          |
|          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.32:resilience_test -->

## Column guidance — what to fill in

### Resilience Test Scope

<<MUST item:Art.32:resilience_test_scope>>
_Why: Art.32.1.d_

> _Standard text:_ Test scope covers confidentiality, integrity, availability and resilience

<<GUIDANCE>>

### Resilience Test Recent

<<MUST item:Art.32:resilience_test_recent>>
_Why: Art.32.1.d — 'regularly'_

> _Standard text:_ Test executed within the freshness window (last 12 months)

<<GUIDANCE>>

### Resilience Test Findings

<<MUST item:Art.32:resilience_test_findings>>
_Why: Art.32.1.d evaluation requirement_

> _Standard text:_ Findings recorded and remediated or accepted

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Resilience Test Independent

<<SHOULD item:Art.32:resilience_test_independent>>
_Why: Best practice for credibility_

> _Standard text:_ Test conducted or reviewed by an independent party

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
