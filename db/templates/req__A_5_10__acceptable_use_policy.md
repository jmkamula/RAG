---
leaf_id: req:A.5.10:acceptable_use_policy
control_ref: A.5.10
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
---

# Acceptable Use Policy

<<DOC_CONTROL>>

> A.5.10 requires rules for acceptable use and procedures for handling information and associated assets. The AUP covers both general principles and the handling rules per asset/information class. Approval, communication and periodic review are sibling leaves

## What this template gives you

This template helps you set clear rules for how information and company assets should be used, ensuring everyone understands what is and isn’t acceptable in your organization.

## When to use it

Use this whenever you need to define or update rules for acceptable use of information and assets in your environment. Review and refresh the policy as needed to keep it current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours drafting this policy from scratch, depending on how many details you need to cover for your organization.

## 1. Scope of the policy (which assets, which users — employees / contractors / third parties — which information classes)

<<MUST item:A.5.10:scope>>
_Why: 27002:5.10 — scope_

<<GUIDANCE>>

<<TEXT>>

## 2. Acceptable use rules stated (work purposes, identified personal-use boundaries, BYOD where applicable)

<<MUST item:A.5.10:acceptable_uses>>
_Why: 27002:5.10a_

<<GUIDANCE>>

<<TEXT>>

## 3. Prohibited use rules stated (unlawful, harmful, security-bypassing activities, unauthorised software)

<<MUST item:A.5.10:prohibited_uses>>
_Why: 27002:5.10b_

<<GUIDANCE>>

<<TEXT>>

## 4. Handling procedures per information class (storage, transmission, retention, disposal) aligned with A.5.12

<<MUST item:A.5.10:handling_procedures>>
_Why: 27002:5.10 — handling_

<<GUIDANCE>>

<<TEXT>>

## 5. Monitoring expectations stated transparently (what the org may inspect, under what conditions)

<<MUST item:A.5.10:monitoring>>
_Why: 27002:5.10c — monitoring transparency_

<<GUIDANCE>>

<<TEXT>>

## 6. Enforcement and disciplinary consequences referenced (link to A.6.4 disciplinary process)

<<MUST item:A.5.10:enforcement>>
_Why: 27002:5.10 — implemented_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. BYOD provisions where personal devices are used for work

<<SHOULD item:A.5.10:byod>>
_Why: Modern workforce_

<<GUIDANCE>>

<<TEXT>>

### 2. Social media usage and corporate-information disclosure rules

<<SHOULD item:A.5.10:social_media>>
_Why: Reputational risk_

<<GUIDANCE>>

<<TEXT>>

### 3. Remote and teleworking provisions where physical environment is outside the org's control

<<SHOULD item:A.5.10:remote_work>>
_Why: 27002:5.10 — context_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
