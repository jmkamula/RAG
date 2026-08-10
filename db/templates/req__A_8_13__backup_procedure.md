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

<<DOC_CONTROL>>

> A.8.13 requires backups maintained and regularly tested. Procedure documents scope, frequency, retention, storage separation, encryption. Per-restore-test register (lifecycle-end), applicable scope, program review are sibling leaves

## What this template gives you

This template helps you create a clear, step-by-step procedure for backing up important information, including how often backups happen, how long they're kept, and how they're protected. It ensures your backup process meets ISO 27001 requirements.

## When to use it

Use this whenever you need to document or update your organization's backup procedures, as these requirements always apply to your environment. Review and refresh the document whenever your backup process changes or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, as you'll need to address several required elements and set up a register for restore tests.

## 1. Scope — which information, software, systems are backed up (with frequency tier per class)

<<MUST item:A.8.13:scope>>
_Why: 27002:8.13 — backup copies_

<<GUIDANCE>>

<<TEXT>>

## 2. Frequency per asset class (continuous / hourly / daily / weekly aligned to RPO)

<<MUST item:A.8.13:frequency>>
_Why: 27002:8.13 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 3. Retention period per asset class (drives storage cost + recovery range)

<<MUST item:A.8.13:retention>>
_Why: 27002:8.13 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 4. Storage separation (offsite OR air-gapped OR immutable-storage) — 3-2-1 rule applied

<<MUST item:A.8.13:storage_separation>>
_Why: 27002:8.13 — maintained (modern ransomware threat)_

<<GUIDANCE>>

<<TEXT>>

## 5. Encryption of backups at rest + in transit (cross-link to A.8.24)

<<MUST item:A.8.13:encryption>>
_Why: 27002:8.13 — maintained_

<<GUIDANCE>>

<<TEXT>>

## 6. Restore-test cadence stated per asset class (annual minimum; quarterly for tier-1)

<<MUST item:A.8.13:restore_test_cadence>>
_Why: 27002:8.13 — regularly tested_

<<GUIDANCE>>

<<TEXT>>

## 7. RPO alignment with A.5.30 ICT readiness (each system's BIA RPO ≤ backup frequency)

<<MUST item:A.8.13:rpo_alignment>>
_Why: Continuity coherence_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Backup Operations lead with Infrastructure partner)

<<SHOULD item:A.8.13:owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
