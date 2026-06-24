---
leaf_id: req:A.8.13:backup_procedure
control_ref: A.8.13
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Information Backup Procedure

> A.8.13 requires backups maintained and regularly tested. Procedure documents scope, frequency, retention, storage separation, encryption. Per-restore-test register (lifecycle-end), applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope — which information, software, systems are backed up (with frequency tier per class)

<<MUST item:A.8.13:scope>>
_Why: 27002:8.13 — backup copies_

<<TEXT>>

## 2. Frequency per asset class (continuous / hourly / daily / weekly aligned to RPO)

<<MUST item:A.8.13:frequency>>
_Why: 27002:8.13 — maintained_

<<TEXT>>

## 3. Retention period per asset class (drives storage cost + recovery range)

<<MUST item:A.8.13:retention>>
_Why: 27002:8.13 — maintained_

<<TEXT>>

## 4. Storage separation (offsite OR air-gapped OR immutable-storage) — 3-2-1 rule applied

<<MUST item:A.8.13:storage_separation>>
_Why: 27002:8.13 — maintained (modern ransomware threat)_

<<TEXT>>

## 5. Encryption of backups at rest + in transit (cross-link to A.8.24)

<<MUST item:A.8.13:encryption>>
_Why: 27002:8.13 — maintained_

<<TEXT>>

## 6. Restore-test cadence stated per asset class (annual minimum; quarterly for tier-1)

<<MUST item:A.8.13:restore_test_cadence>>
_Why: 27002:8.13 — regularly tested_

<<TEXT>>

## 7. RPO alignment with A.5.30 ICT readiness (each system's BIA RPO ≤ backup frequency)

<<MUST item:A.8.13:rpo_alignment>>
_Why: Continuity coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Backup Operations lead with Infrastructure partner)

<<SHOULD item:A.8.13:owner>>
_Why: Accountability_

<<TEXT>>
