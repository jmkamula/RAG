---
leaf_id: req:A.8.18:utility_register
control_ref: A.8.18
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Privileged Utility Programs Register

> Per-utility inventory — utility id, capability, current location, authorised users, last-use

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row utility identifier (name + version)

<<MUST item:A.8.18:reg_utility_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row capability description (what controls it can override)

<<MUST item:A.8.18:reg_capability>>
_Why: 27002:8.18 — utility programs that can override_

<<TEXT>>

## 3. Per-row current location (systems where installed) — drives removal-where-unneeded principle

<<MUST item:A.8.18:reg_location>>
_Why: 27002:8.18 — restricted_

<<TEXT>>

## 4. Per-row authorised user list (with approval lineage)

<<MUST item:A.8.18:reg_authorised>>
_Why: 27002:8.18 — restricted_

<<TEXT>>

## 5. Per-row last-use timestamp (drives 'still needed' review)

<<MUST item:A.8.18:reg_last_use>>
_Why: Drift detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row JIT-vault availability flag (where applicable, indicates non-standing-install path)

<<SHOULD item:A.8.18:reg_jit_vault>>
_Why: Modern maturity_

<<TEXT>>
