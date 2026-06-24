---
leaf_id: req:10.2:nonconformity_register
control_ref: 10.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 8
should_count: 1
---

# Nonconformity Register

> Per-NC record tracking the full lifecycle: identification → root cause → corrective action → effectiveness check → closure. The auditor's most-scrutinised register: an open NC with no closure timeline signals a broken ISMS. Annual refresh (freshness=365). Cross-link to A.5.36 nonconformity register for compliance-with-rules NCs

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique NC identifier per row

<<MUST item:10.2:reg_nc_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row source (9.2 internal audit, surveillance audit, incident lesson, regulator finding, party complaint)

<<MUST item:10.2:reg_source>>
_Why: Cross-clause traceability_

<<TEXT>>

## 3. Per-row nature of NC (what failed against what requirement)

<<MUST item:10.2:reg_nature>>
_Why: Clause 10.2 — nature_

<<TEXT>>

## 4. Per-row immediate-reaction record (containment / correction)

<<MUST item:10.2:reg_react>>
_Why: Clause 10.2 a)_

<<TEXT>>

## 5. Per-row root cause analysis record (5-whys, fishbone, or equivalent)

<<MUST item:10.2:reg_root_cause>>
_Why: Clause 10.2 b)_

<<TEXT>>

## 6. Per-row corrective action(s) with owner + target date

<<MUST item:10.2:reg_corrective_action>>
_Why: Clause 10.2 c)_

<<TEXT>>

## 7. Per-row effectiveness verification (did the action prevent recurrence?)

<<MUST item:10.2:reg_effectiveness_check>>
_Why: Clause 10.2 d)_

<<TEXT>>

## 8. Per-row status (open / in-progress / closed / re-opened)

<<MUST item:10.2:reg_status>>
_Why: Tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row ISMS-change cross-reference (link to 6.3 change record when the NC drove an ISMS amendment)

<<SHOULD item:10.2:reg_isms_change_xref>>
_Why: Clause 10.2 e)_

<<TEXT>>
