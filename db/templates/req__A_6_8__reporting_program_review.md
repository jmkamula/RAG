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
---

# Periodic Reporting Program Review

> Periodic verification that reports are coming in (under-reporting is the major risk), that triage handoff is working (no reports lost between A.6.8 intake and A.5.25 triage), that reporters are getting acknowledgment, and that the audience-channel surfacing is current. Annual cadence (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.8:rev_date>>
_Why: 27002:6.8 — periodic_

<<TEXT>>

## 2. Reviewer identity (InfoSec lead + HR partner; Legal for whistleblower-territory cases)

<<MUST item:A.6.8:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Volume trend analysis (report rate per segment — sudden drops may indicate under-reporting; sudden spikes may indicate a campaign or a known issue surfacing)

<<MUST item:A.6.8:rev_volume_trend>>
_Why: Reporting culture health_

<<TEXT>>

## 4. Channel-mix analysis (which channels are being used; under-used channels may need awareness promotion or retirement)

<<MUST item:A.6.8:rev_channel_mix>>
_Why: 27002:6.8 — channels effectiveness_

<<TEXT>>

## 5. Triage handoff check — every report reached A.5.25 triage; no reports lost in the handoff; cycle time from report to triage measured

<<MUST item:A.6.8:rev_triage_handoff>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Acknowledgment rate to reporters (where reporter known) — drives reporter satisfaction and ongoing willingness to report

<<MUST item:A.6.8:rev_acknowledgment_rate>>
_Why: Reporting culture_

<<TEXT>>

## 7. Changes propagated to the procedure / scope with reference to this review

<<MUST item:A.6.8:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (major incident exposing under-reporting, regulator enforcement on whistleblower regime, channel outage)

<<SHOULD item:A.6.8:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.8:rev_next_date>>
_Why: Planning_

<<TEXT>>
