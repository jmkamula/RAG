---
leaf_id: req:A.8.1:user_endpoint_devices_policy
control_ref: A.8.1
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# User Endpoint Devices Policy

> A.8.1 requires protection of information stored on, processed by, or accessible via user endpoint devices. The policy defines device classes in scope, baseline protections per class, and the authorisation model for endpoint enrolment. The endpoint register, applicable-classes scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope — device classes in scope (corporate-owned, BYOD, contractor)

<<MUST item:A.8.1:scope>>
_Why: 27002:8.1 — user end point devices_

<<TEXT>>

## 2. Full-disk or storage encryption required

<<MUST item:A.8.1:encryption>>
_Why: 27002:8.1 — protected_

<<TEXT>>

## 3. Anti-malware / EDR required and current (cross-link to A.8.7)

<<MUST item:A.8.1:malware>>
_Why: 27002:8.1 — protected_

<<TEXT>>

## 4. Patch level / OS-version requirements stated (cross-link to A.8.8)

<<MUST item:A.8.1:patch_level>>
_Why: 27002:8.1 — protected_

<<TEXT>>

## 5. Authentication and screen-lock requirements (cross-link to A.5.17 / A.7.7)

<<MUST item:A.8.1:authentication>>
_Why: 27002:8.1 — accessible via end point devices_

<<TEXT>>

## 6. Remote wipe / lock capability for lost or stolen devices

<<MUST item:A.8.1:remote_wipe>>
_Why: 27002:8.1 — protected_

<<TEXT>>

## 7. MDM enrolment required before access to corporate information

<<MUST item:A.8.1:mdm_enrollment>>
_Why: Modern baseline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Jailbreak / root detection where mobile

<<SHOULD item:A.8.1:jailbreak_detection>>
_Why: Compromise signal_

<<TEXT>>

### 2. Application allowlisting / blocklisting on managed endpoints

<<SHOULD item:A.8.1:app_controls>>
_Why: Reduces attack surface_

<<TEXT>>
