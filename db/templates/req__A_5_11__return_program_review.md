---
leaf_id: req:A.5.11:return_program_review
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Asset-Return Program Review

> The return process creates value only if it actually closes — unreturned-asset rates, delayed-access-revocation incidents, BYOD-wipe failures all signal the program is leaking. The review captures the planned-interval check: unreturned rate, access-revocation latency, exception/write-off analysis, workforce-model coverage, and resulting program adjustments. Annual cadence — HR methodology stability

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned annual interval

<<MUST item:A.5.11:rev_date>>
_Why: 27002:5.11 — periodic_

<<TEXT>>

## 2. Reviewer identity (HR head + IT head + InfoSec lead jointly)

<<MUST item:A.5.11:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Unreturned-asset rate analysed (count of leavers with status=exception or written_off; root cause per cluster)

<<MUST item:A.5.11:rev_unreturned_rate>>
_Why: Program effectiveness_

<<TEXT>>

## 4. Access-revocation latency analysed (gap between effective_date and access_revoke_timestamp; investigate outliers)

<<MUST item:A.5.11:rev_revoke_latency>>
_Why: 27002:5.11 — timeliness of logical handling_

<<TEXT>>

## 5. BYOD-wipe health check (sample of recent BYOD leavers re-verified for selective-wipe success or org-data presence)

<<MUST item:A.5.11:rev_byod_health>>
_Why: Workforce-model coverage_

<<TEXT>>

## 6. Write-off audit (any leaver row written off — was risk acceptance appropriately authorised? what value was lost?)

<<MUST item:A.5.11:rev_writeoff_audit>>
_Why: Risk discipline_

<<TEXT>>

## 7. Action items captured (e.g. tighten access-revoke automation, expand asset checklist, retrain managers)

<<MUST item:A.5.11:rev_actions>>
_Why: 27002:5.11 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Workforce-model shift considered (e.g. step-change in remote-work proportion or contractor mix that changes risk surface)

<<SHOULD item:A.5.11:rev_workforce_shift>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.11:rev_next_date>>
_Why: Planning_

<<TEXT>>
