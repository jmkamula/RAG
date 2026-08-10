---
leaf_id: req:A.7.3.6:acr_procedure
control_ref: A.7.3.6
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 7
should_count: 1
---

# Access / Correction / Erasure Procedure

<<DOC_CONTROL>>

> §7.3.6 requires the umbrella procedure for the three core subject-rights operations. Bridges to GDPR Art.15 (access), Art.16 (rectification), Art.17 (erasure). Companion to A.7.3.9 (request handling).

## What this template gives you

This template helps you document how your organization handles requests from individuals to access, correct, or erase their personal data. It ensures you meet key privacy requirements and provides a clear, step-by-step procedure.

## When to use it

Use this template whenever your organization needs to outline or update its process for handling data subject requests, such as access, correction, or erasure. Update the document as needed when your procedures or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 70 to 105 minutes to complete this template from scratch, as each required section will take roughly 10 to 15 minutes to fill in thoughtfully.

## 1. Identity verification step (proportionate — avoids granting rights to imposters)

<<MUST item:A.7.3.6:proc_identity_verification>>
_Why: GDPR Art.12.6 + §7.3.9_

<<GUIDANCE>>

<<TEXT>>

## 2. Access flow — Art.15 fields + copy of PII processed (link to A.7.3.8)

<<MUST item:A.7.3.6:proc_access_flow>>
_Why: GDPR Art.15.1 + Art.15.3_

<<GUIDANCE>>

<<TEXT>>

## 3. Correction flow — including subject-dispute path when correction is disputed

<<MUST item:A.7.3.6:proc_correction_flow>>
_Why: §7.3.6 — dispute about accuracy_

<<GUIDANCE>>

<<TEXT>>

## 4. Erasure flow — including retention-limit + legal-obligation exceptions

<<MUST item:A.7.3.6:proc_erasure_flow>>
_Why: GDPR Art.17.3_

<<GUIDANCE>>

<<TEXT>>

## 5. Downstream propagation — corrections/erasures pushed to systems + third parties (see A.7.3.7)

<<MUST item:A.7.3.6:proc_downstream_propagation>>
_Why: §7.3.6 — pass to third parties_

<<GUIDANCE>>

<<TEXT>>

## 6. Response-time SLA stated + honoured (undue delay standard)

<<MUST item:A.7.3.6:proc_response_sla>>
_Why: §7.3.6 — without undue delay + Art.12.3_

<<GUIDANCE>>

<<TEXT>>

## 7. Refusal reasoning — where request refused / cannot be met, subject informed of reasons + right to complain

<<MUST item:A.7.3.6:proc_refusal_reasoning>>
_Why: §7.3.6 — reasons why corrections cannot be made + Art.12.4_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Self-service surface where feasible (subject portal for direct access/correction)

<<SHOULD item:A.7.3.6:proc_self_service>>
_Why: Efficiency + Art.15.3_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
