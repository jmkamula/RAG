---
leaf_id: req:B.8.2.2:purpose_limitation_procedure
control_ref: B.8.2.2
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Customer-Purpose Adherence Procedure

<<DOC_CONTROL>>

> §8.2.2 requires the processor to process PII ONLY for the purposes expressed in the customer's documented instructions — no side-purposes, no leverage of customer PII for own analytics or training. Governs how customer instructions are captured, cascaded internally, and audited.

## What this template gives you

This template helps you document how your organization ensures personal data is only used for the purposes your customers have approved, and how you capture, communicate, and check those instructions internally.

## When to use it

Use this procedure whenever your organization processes personal data on behalf of customers and needs to show that you follow their documented instructions. Update it whenever your data handling practices or customer requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to complete this template from scratch, as it covers five required elements and may need input from different teams.

## 1. Instruction capture — customer purposes recorded per engagement (contract + change-notices)

<<MUST item:B.8.2.2:proc_instruction_capture>>
_Why: §8.2.2 — documented instructions_

<<GUIDANCE>>

<<TEXT>>

## 2. Technical binding — engineering controls that prevent processing beyond stated purposes (tenant isolation / data-tag enforcement / access scoping)

<<MUST item:B.8.2.2:proc_technical_binding>>
_Why: §8.2.2 — only processed for purposes_

<<GUIDANCE>>

<<TEXT>>

## 3. No-side-purpose rule — customer PII not used for own analytics / ML training / product improvement without express permission

<<MUST item:B.8.2.2:proc_no_side_purpose>>
_Why: §8.2.2 — organization or subcontractors_

<<GUIDANCE>>

<<TEXT>>

## 4. Technical-justification carve-out procedure — where processor must choose method for capacity reasons (per §8.2.2 implementation), justification documented + surfaced to customer

<<MUST item:B.8.2.2:proc_technical_justification>>
_Why: §8.2.2 implementation guidance_

<<GUIDANCE>>

<<TEXT>>

## 5. Customer verification pathway — customer can audit purpose-limitation compliance

<<MUST item:B.8.2.2:proc_customer_verification>>
_Why: §8.2.2 — allow customer to verify_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Engineering + Privacy Engineering)

<<SHOULD item:B.8.2.2:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
