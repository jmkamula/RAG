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

> A.8.31 requires environments separated + secured. Procedure documents distinct environments, network/identity separation, data-handling rules, promotion process, per-env access. Per-environment register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Distinct environments enumerated (dev / test / staging / production) with purpose per environment

<<MUST item:A.8.31:distinct_environments>>
_Why: 27002:8.31 — separated_

<<TEXT>>

## 2. Network + identity separation between environments (cross-link to A.8.22 network segregation)

<<MUST item:A.8.31:network_separation>>
_Why: 27002:8.31 — separated_

<<TEXT>>

## 3. Data-handling rules between environments — NO raw production data in lower environments (cross-link to A.8.11 masking + A.8.33 test info)

<<MUST item:A.8.31:data_handling>>
_Why: 27002:8.31 — secured_

<<TEXT>>

## 4. Promotion / deployment process between environments (cross-link to A.8.32 change management)

<<MUST item:A.8.31:promotion_process>>
_Why: 27002:8.31 — secured_

<<TEXT>>

## 5. Access controls per environment (dev access ≠ prod access; production-access is privileged-access per A.8.2)

<<MUST item:A.8.31:per_env_access>>
_Why: 27002:8.31 — secured_

<<TEXT>>

## 6. Infrastructure-as-code for environment reproducibility (modern baseline)

<<MUST item:A.8.31:iac>>
_Why: Consistency (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ephemeral environments where supported (e.g. per-PR preview environments)

<<SHOULD item:A.8.31:ephemeral>>
_Why: Modern practice_

<<TEXT>>
