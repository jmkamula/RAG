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

> A.8.18 requires utility programs capable of overriding system/application controls to be restricted and tightly controlled. Policy defines what counts, authorisation model, removal-where-unneeded principle. Per-utility register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Authorisation model — who can approve use per utility class (InfoSec + system owner)

<<MUST item:A.8.18:authorisation_model>>
_Why: 27002:8.18 — restricted_

<<TEXT>>

## 2. JIT-access principle — utilities not standing-installed where avoidable; cross-link to A.8.2 PAM

<<MUST item:A.8.18:jit_principle>>
_Why: 27002:8.18 — tightly controlled_

<<TEXT>>

## 3. Removal-where-unneeded principle — utility programs removed from systems where not required

<<MUST item:A.8.18:removal_principle>>
_Why: Attack-surface reduction (Style v2 promotion)_

<<TEXT>>

## 4. Logging requirement — every utility-program invocation captured (cross-link to A.8.15)

<<MUST item:A.8.18:logging_principle>>
_Why: 27002:8.18 — tightly controlled_

<<TEXT>>

## 5. Named policy authority (InfoSec lead with Infrastructure lead)

<<MUST item:A.8.18:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Vendor-provided utility programs treated under the same rules (no vendor-default-allow)

<<SHOULD item:A.8.18:vendor_utilities>>
_Why: Common gap_

<<TEXT>>
