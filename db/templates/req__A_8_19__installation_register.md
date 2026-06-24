---
leaf_id: req:A.8.19:installation_register
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Software Installation Register

> Per-installation record — what was installed, when, where, by whom, verification artefact

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-install unique identifier

<<MUST item:A.8.19:reg_install_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-install software name + version + source (from approved list)

<<MUST item:A.8.19:reg_software>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 3. Per-install target system

<<MUST item:A.8.19:reg_target>>
_Why: 27002:8.19 — operational systems_

<<TEXT>>

## 4. Per-install authorised actor (privileged role assignment)

<<MUST item:A.8.19:reg_actor>>
_Why: Accountability_

<<TEXT>>

## 5. Per-install verification artefacts (signature check / functional test / vuln-scan result)

<<MUST item:A.8.19:reg_verification>>
_Why: 27002:8.19 — securely_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-install cross-link to A.8.32 change record where applicable

<<SHOULD item:A.8.19:reg_change_link>>
_Why: Cross-control coherence_

<<TEXT>>
