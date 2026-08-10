---
leaf_id: req:A.8.31:environment_separation_procedure
control_ref: A.8.31
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Development, Test, Production Environment Separation Procedure

<<DOC_CONTROL>>

> A.8.31 requires environments separated + secured. Procedure documents distinct environments, network/identity separation, data-handling rules, promotion process, per-env access. Per-environment register, applicable scope, program review are sibling leaves

## What this template gives you

This template helps you clearly document how your development, test, and production environments are separated and secured, including rules for data handling and access in each environment. It's designed to support compliance with ISO 27001 requirements.

## When to use it

Use this template when your organization needs to formally describe how you separate and manage different technical environments, especially if your risk profile or compliance obligations require it. Update the document whenever your environment setup or related processes change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this template from scratch, depending on the complexity of your environment and the amount of detail needed for each required section.

## 1. Distinct environments enumerated (dev / test / staging / production) with purpose per environment

<<MUST item:A.8.31:distinct_environments>>
_Why: 27002:8.31 — separated_

<<GUIDANCE>>

<<TEXT>>

## 2. Network + identity separation between environments (cross-link to A.8.22 network segregation)

<<MUST item:A.8.31:network_separation>>
_Why: 27002:8.31 — separated_

<<GUIDANCE>>

<<TEXT>>

## 3. Data-handling rules between environments — NO raw production data in lower environments (cross-link to A.8.11 masking + A.8.33 test info)

<<MUST item:A.8.31:data_handling>>
_Why: 27002:8.31 — secured_

<<GUIDANCE>>

<<TEXT>>

## 4. Promotion / deployment process between environments (cross-link to A.8.32 change management)

<<MUST item:A.8.31:promotion_process>>
_Why: 27002:8.31 — secured_

<<GUIDANCE>>

<<TEXT>>

## 5. Access controls per environment (dev access ≠ prod access; production-access is privileged-access per A.8.2)

<<MUST item:A.8.31:per_env_access>>
_Why: 27002:8.31 — secured_

<<GUIDANCE>>

<<TEXT>>

## 6. Infrastructure-as-code for environment reproducibility (modern baseline)

<<MUST item:A.8.31:iac>>
_Why: Consistency (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ephemeral environments where supported (e.g. per-PR preview environments)

<<SHOULD item:A.8.31:ephemeral>>
_Why: Modern practice_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
