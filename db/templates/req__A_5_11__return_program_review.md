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
table_shape: true
---

# Periodic Asset-Return Program Review

> The return process creates value only if it actually closes — unreturned-asset rates, delayed-access-revocation incidents, BYOD-wipe failures all signal the program is leaking. The review captures the planned-interval check: unreturned rate, access-revocation latency, exception/write-off analysis, workforce-model coverage, and resulting program adjustments. Annual cadence — HR methodology stability

<!-- TABLE-COLUMNS leaf:req:A.5.11:return_program_review -->
<!-- column: item:A.5.11:rev_date -->
<!-- column: item:A.5.11:rev_reviewer -->
<!-- column: item:A.5.11:rev_unreturned_rate -->
<!-- column: item:A.5.11:rev_revoke_latency -->
<!-- column: item:A.5.11:rev_byod_health -->
<!-- column: item:A.5.11:rev_writeoff_audit -->
<!-- column: item:A.5.11:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.11:return_program_review -->
| Rev Date | Rev Reviewer | Rev Unreturned Rate | Rev Revoke Latency | Rev Byod Health | Rev Writeoff Audit | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.11:return_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.11:rev_date>>
_Why: 27002:5.11 — periodic_

> _Standard text:_ Review date within the planned annual interval

### Rev Reviewer

<<MUST item:A.5.11:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR head + IT head + InfoSec lead jointly)

### Rev Unreturned Rate

<<MUST item:A.5.11:rev_unreturned_rate>>
_Why: Program effectiveness_

> _Standard text:_ Unreturned-asset rate analysed (count of leavers with status=exception or written_off; root cause per cluster)

### Rev Revoke Latency

<<MUST item:A.5.11:rev_revoke_latency>>
_Why: 27002:5.11 — timeliness of logical handling_

> _Standard text:_ Access-revocation latency analysed (gap between effective_date and access_revoke_timestamp; investigate outliers)

### Rev Byod Health

<<MUST item:A.5.11:rev_byod_health>>
_Why: Workforce-model coverage_

> _Standard text:_ BYOD-wipe health check (sample of recent BYOD leavers re-verified for selective-wipe success or org-data presence)

### Rev Writeoff Audit

<<MUST item:A.5.11:rev_writeoff_audit>>
_Why: Risk discipline_

> _Standard text:_ Write-off audit (any leaver row written off — was risk acceptance appropriately authorised? what value was lost?)

### Rev Actions

<<MUST item:A.5.11:rev_actions>>
_Why: 27002:5.11 — program adjustments_

> _Standard text:_ Action items captured (e.g. tighten access-revoke automation, expand asset checklist, retrain managers)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Workforce Shift

<<SHOULD item:A.5.11:rev_workforce_shift>>
_Why: Audit defensibility_

> _Standard text:_ Workforce-model shift considered (e.g. step-change in remote-work proportion or contractor mix that changes risk surface)

### Rev Next Date

<<SHOULD item:A.5.11:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
