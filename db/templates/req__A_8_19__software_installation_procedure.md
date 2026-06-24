---
leaf_id: req:A.8.19:software_installation_procedure
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Software Installation on Operational Systems Procedure

> A.8.19 requires procedures + measures to securely manage software installation. Procedure documents approved-software list, approval workflow, integrity verification, post-install verification, role-restriction. Per-installation register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Approved software list maintained (positive list — only approved software permitted)

<<MUST item:A.8.19:approved_list>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 2. Approval workflow for new software (security review + licence check + integration test)

<<MUST item:A.8.19:approval_workflow>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 3. Integrity / signature verification before installation (no unsigned packages on production)

<<MUST item:A.8.19:integrity>>
_Why: 27002:8.19 — securely_

<<TEXT>>

## 4. Installation by privileged role only (cross-link to A.8.2 — uses privileged-access procedure)

<<MUST item:A.8.19:privileged_role>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 5. Post-install verification (functional test + vulnerability scan + baseline-drift check)

<<MUST item:A.8.19:post_install>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 6. Allowlisting on operational systems where supported (modern baseline)

<<MUST item:A.8.19:allowlisting>>
_Why: 27002:8.19 — measures (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Software-inventory tooling for ongoing visibility

<<SHOULD item:A.8.19:inventory_tooling>>
_Why: Drift detection_

<<TEXT>>
