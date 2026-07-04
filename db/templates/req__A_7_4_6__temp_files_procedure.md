---
leaf_id: req:A.7.4.6:temp_files_procedure
control_ref: A.7.4.6
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 4
should_count: 1
---

# Temporary Files Disposal Procedure

> §7.4.6 requires temporary files created during PII processing to be disposed of within a specified, documented period. Covers file-system journals, roll-back files, in-flight application state, and app-specific temp files.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Temp file taxonomy (application temp / file-system journal / database roll-back / cache / in-memory dump)

<<MUST item:A.7.4.6:proc_temp_file_taxonomy>>
_Why: §7.4.6 other information — system + application temp_

<<TEXT>>

## 2. Disposal period stated per taxonomy category

<<MUST item:A.7.4.6:proc_disposal_period>>
_Why: §7.4.6 — specified, documented period_

<<TEXT>>

## 3. Garbage-collection procedure — identifies unused temp files + last-use timestamp

<<MUST item:A.7.4.6:proc_garbage_collection>>
_Why: §7.4.6 — garbage collection procedure_

<<TEXT>>

## 4. Periodic check that unused temp files are deleted within the identified period

<<MUST item:A.7.4.6:proc_periodic_check>>
_Why: §7.4.6 — periodic checks_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Infrastructure + Application Ops)

<<SHOULD item:A.7.4.6:proc_owner>>
_Why: Accountability_

<<TEXT>>
