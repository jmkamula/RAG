---
leaf_id: req:A.8.31:environment_register
control_ref: A.8.31
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Environment Register

> Per-environment catalogue — env id, purpose, data classes permitted, owner, access list reference

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row environment unique identifier

<<MUST item:A.8.31:reg_env_id>>
_Why: Identification_

<<TEXT>>

## 2. Per-row purpose (dev / test / staging / production / sandbox / training)

<<MUST item:A.8.31:reg_purpose>>
_Why: 27002:8.31 — separated_

<<TEXT>>

## 3. Per-row data classes permitted (drives masking obligations from A.8.11)

<<MUST item:A.8.31:reg_data_allowed>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Per-row named owner (technology lead with InfoSec partner for production)

<<MUST item:A.8.31:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 5. Per-row access-list reference (cross-link to A.8.3 access matrix)

<<MUST item:A.8.31:reg_access_ref>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row last-audited timestamp

<<SHOULD item:A.8.31:reg_last_audited>>
_Why: Drift detection_

<<TEXT>>
