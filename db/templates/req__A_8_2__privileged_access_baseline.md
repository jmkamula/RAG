---
leaf_id: req:A.8.2:privileged_access_baseline
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Privileged Access Baseline

<<DOC_CONTROL>>

> A.8.2 requires identification of users needing privileged access per system and restriction of access to system-administration tools. The baseline defines the privileged role catalogue, the systems in scope, the strong-authentication configuration, and the PAM tooling boundaries — the configuration state against which the procedure operates

## What this template gives you

This template helps you clearly define who needs privileged access, which systems are included, and how strong authentication and access management tools are set up. It's useful if you want to document and control administrative access in your environment.

## When to use it

Use this template whenever you need to establish or update your baseline for privileged access, as it should always reflect your current environment. Review and refresh it whenever there are changes to systems, roles, or access tools.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this template from scratch, as you'll need to provide details for each required section.

## 1. Privileged role catalogue per system (which roles exist, what they grant)

<<MUST item:A.8.2:bl_role_catalogue>>
_Why: 27002:8.2a_

<<GUIDANCE>>

<<TEXT>>

## 2. Systems and processes in scope for privileged access governance

<<MUST item:A.8.2:bl_systems_in_scope>>
_Why: 27002:8.2a, g_

<<GUIDANCE>>

<<TEXT>>

## 3. Strong authentication required for all privileged access (MFA enforced)

<<MUST item:A.8.2:bl_strong_auth>>
_Why: 27002:8.2h_

<<GUIDANCE>>

<<TEXT>>

## 4. Access to system-administration tools restricted to privileged roles only

<<MUST item:A.8.2:bl_admin_tools_restricted>>
_Why: 27002:8.2g_

<<GUIDANCE>>

<<TEXT>>

## 5. PAM tooling configured (vaulting, session recording, command brokering)

<<MUST item:A.8.2:bl_pam_tool>>
_Why: Modern baseline (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

## 6. Just-in-time / time-bound elevation capability available — eliminates standing privilege

<<MUST item:A.8.2:bl_jit_capability>>
_Why: 27002:8.2b modern interpretation (Style v2 promotion)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Session recording active for high-risk privileged actions

<<SHOULD item:A.8.2:bl_session_recording>>
_Why: Forensic readiness_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
