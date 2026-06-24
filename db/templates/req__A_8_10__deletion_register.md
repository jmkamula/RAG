---
leaf_id: req:A.8.10:deletion_register
control_ref: A.8.10
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Per-Deletion Disposal Register

> Per-deletion lifecycle-end record — what was deleted, when, by what method, with verification artefact. Parallels A.5.28 evidence handling disposal pattern and A.7.14 secure disposal

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-deletion unique identifier

<<MUST item:A.8.10:reg_event_id>>
_Why: Auditability_

<<TEXT>>

## 2. Per-deletion target identifier (dataset / record class / asset / media id)

<<MUST item:A.8.10:reg_target>>
_Why: 27002:8.10 — deleted_

<<TEXT>>

## 3. Per-deletion trigger (retention expiry / DSAR / asset retirement / legal-hold release / explicit instruction)

<<MUST item:A.8.10:reg_trigger>>
_Why: 27002:8.10 — when no longer required_

<<TEXT>>

## 4. Per-deletion method used (matches procedure's method table for the media class)

<<MUST item:A.8.10:reg_method>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Per-deletion verification artefact reference (log id / certificate / signed attestation)

<<MUST item:A.8.10:reg_verification>>
_Why: 27002:8.10 — deleted_

<<TEXT>>

## 6. Per-deletion backup-sweep confirmation (or rationale if deferred to next backup-cycle deletion)

<<MUST item:A.8.10:reg_backup_sweep>>
_Why: Common GDPR audit failure point_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-deletion actor (person or automated job identifier)

<<SHOULD item:A.8.10:reg_actor>>
_Why: Accountability_

<<TEXT>>
