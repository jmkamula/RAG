---
leaf_id: req:A.8.33:test_information_procedure
control_ref: A.8.33
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 1
---

# Test Information Management Procedure

<<DOC_CONTROL>>

> A.8.33 requires test information selected, protected, managed. Procedure documents selection criteria, masking requirements, protection equivalence, access controls, lifecycle, PII constraint. Per-dataset register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you document how you select, protect, and manage test information, including criteria for masking, access controls, and handling personal data. It's designed to help you meet ISO 27001 requirements for test data management.

## When to use it

Use this procedure when your organization handles test information that needs to be protected or managed according to ISO 27001, especially if your profile matches specific triggers. Update the document as needed when your processes or data change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, depending on the number of datasets you need to register and the complexity of your test information management processes.

## 1. Selection criteria — synthetic preferred; production-derived only with masking (cross-link to A.8.11)

<<MUST item:A.8.33:selection>>
_Why: 27002:8.33 — appropriately selected_

<<GUIDANCE>>

<<TEXT>>

## 2. Masking requirements when production-derived data is used (cross-link to A.8.11 procedure)

<<MUST item:A.8.33:masking>>
_Why: 27002:8.33 — protected_

<<GUIDANCE>>

<<TEXT>>

## 3. Protection equivalent to production where data warrants it (encryption / access logging / retention)

<<MUST item:A.8.33:protection>>
_Why: 27002:8.33 — protected_

<<GUIDANCE>>

<<TEXT>>

## 4. Access controls on test data (not every developer sees all test data; cross-link to A.8.3)

<<MUST item:A.8.33:access_controls>>
_Why: 27002:8.33 — managed_

<<GUIDANCE>>

<<TEXT>>

## 5. Lifecycle (provisioning + refresh cadence + deletion at end of need; cross-link to A.8.10)

<<MUST item:A.8.33:lifecycle>>
_Why: 27002:8.33 — managed_

<<GUIDANCE>>

<<TEXT>>

## 6. No live PII in lower environments unless masked / pseudonymised (cross-link to A.8.11 + GDPR alignment)

<<MUST item:A.8.33:pii_constraint>>
_Why: 27002:8.33 / GDPR Art.32_

<<GUIDANCE>>

<<TEXT>>

## 7. DPIA / privacy considerations when PII-derived (cross-link to A.5.34 PII protection)

<<MUST item:A.8.33:dpia_consideration>>
_Why: Privacy compliance (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Synthetic-data-generation tooling preferred over masking where feasible (reduces residual risk)

<<SHOULD item:A.8.33:synthetic_tooling>>
_Why: Modern direction_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
