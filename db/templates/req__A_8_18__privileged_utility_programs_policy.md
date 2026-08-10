---
leaf_id: req:A.8.18:privileged_utility_programs_policy
control_ref: A.8.18
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Privileged Utility Programs Policy

<<DOC_CONTROL>>

> A.8.18 requires utility programs capable of overriding system/application controls to be restricted and tightly controlled. Policy defines what counts, authorisation model, removal-where-unneeded principle. Per-utility register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you set clear rules for managing powerful utility programs that can bypass normal system controls, ensuring only authorized people have access and unused programs are removed. It supports compliance with ISO 27001 requirements.

## When to use it

Use this policy whenever your environment includes utility programs that could override system or application controls. Review and update the document as needed to keep it accurate and effective.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes drafting this policy from scratch, plus additional time if you need to create or update a register of utility programs.

## 1. Authorisation model — who can approve use per utility class (InfoSec + system owner)

<<MUST item:A.8.18:authorisation_model>>
_Why: 27002:8.18 — restricted_

<<GUIDANCE>>

<<TEXT>>

## 2. JIT-access principle — utilities not standing-installed where avoidable; cross-link to A.8.2 PAM

<<MUST item:A.8.18:jit_principle>>
_Why: 27002:8.18 — tightly controlled_

<<GUIDANCE>>

<<TEXT>>

## 3. Removal-where-unneeded principle — utility programs removed from systems where not required

<<MUST item:A.8.18:removal_principle>>
_Why: Attack-surface reduction (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

## 4. Logging requirement — every utility-program invocation captured (cross-link to A.8.15)

<<MUST item:A.8.18:logging_principle>>
_Why: 27002:8.18 — tightly controlled_

<<GUIDANCE>>

<<TEXT>>

## 5. Named policy authority (InfoSec lead with Infrastructure lead)

<<MUST item:A.8.18:authority>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Vendor-provided utility programs treated under the same rules (no vendor-default-allow)

<<SHOULD item:A.8.18:vendor_utilities>>
_Why: Common gap_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
