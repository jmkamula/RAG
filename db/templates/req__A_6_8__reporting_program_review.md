---
leaf_id: req:A.6.8:reporting_program_review
control_ref: A.6.8
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Reporting Program Review

> Periodic verification that reports are coming in (under-reporting is the major risk), that triage handoff is working (no reports lost between A.6.8 intake and A.5.25 triage), that reporters are getting acknowledgment, and that the audience-channel surfacing is current. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.8:reporting_program_review -->
<!-- column: item:A.6.8:rev_date -->
<!-- column: item:A.6.8:rev_reviewer -->
<!-- column: item:A.6.8:rev_volume_trend -->
<!-- column: item:A.6.8:rev_channel_mix -->
<!-- column: item:A.6.8:rev_triage_handoff -->
<!-- column: item:A.6.8:rev_acknowledgment_rate -->
<!-- column: item:A.6.8:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.8:reporting_program_review -->
| Rev Date | Rev Reviewer | Rev Volume Trend | Rev Channel Mix | Rev Triage Handoff | Rev Acknowledgment Rate | Rev Register Update |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.8:reporting_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.8:rev_date>>
_Why: 27002:6.8 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.6.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec lead + HR partner; Legal for whistleblower-territory cases)

### Rev Volume Trend

<<MUST item:A.6.8:rev_volume_trend>>
_Why: Reporting culture health_

> _Standard text:_ Volume trend analysis (report rate per segment — sudden drops may indicate under-reporting; sudden spikes may indicate a campaign or a known issue surfacing)

### Rev Channel Mix

<<MUST item:A.6.8:rev_channel_mix>>
_Why: 27002:6.8 — channels effectiveness_

> _Standard text:_ Channel-mix analysis (which channels are being used; under-used channels may need awareness promotion or retirement)

### Rev Triage Handoff

<<MUST item:A.6.8:rev_triage_handoff>>
_Why: Cross-control coherence_

> _Standard text:_ Triage handoff check — every report reached A.5.25 triage; no reports lost in the handoff; cycle time from report to triage measured

### Rev Acknowledgment Rate

<<MUST item:A.6.8:rev_acknowledgment_rate>>
_Why: Reporting culture_

> _Standard text:_ Acknowledgment rate to reporters (where reporter known) — drives reporter satisfaction and ongoing willingness to report

### Rev Register Update

<<MUST item:A.6.8:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / scope with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.8:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (major incident exposing under-reporting, regulator enforcement on whistleblower regime, channel outage)

### Rev Next Date

<<SHOULD item:A.6.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
