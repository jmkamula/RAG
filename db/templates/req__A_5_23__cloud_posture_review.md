---
leaf_id: req:A.5.23:cloud_posture_review
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Cloud Service Posture Review

> A.5.23 expects ongoing monitoring, review and evaluation of cloud service use. The posture review captures the planned-interval check: refreshed CSP attestations, configuration-drift assessment against the shared-responsibility split, geographic-location compliance check, incident review, and resulting action items

<!-- TABLE-COLUMNS leaf:req:A.5.23:cloud_posture_review -->
<!-- column: item:A.5.23:rev_date -->
<!-- column: item:A.5.23:rev_reviewer -->
<!-- column: item:A.5.23:rev_attestation -->
<!-- column: item:A.5.23:rev_config_drift -->
<!-- column: item:A.5.23:rev_geo_compliance -->
<!-- column: item:A.5.23:rev_incidents -->
<!-- column: item:A.5.23:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.23:cloud_posture_review -->
| Rev Date | Rev Reviewer | Rev Attestation | Rev Config Drift | Rev Geo Compliance | Rev Incidents | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.23:cloud_posture_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.23:rev_date>>
_Why: 27002:5.23g — monitoring_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.5.23:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (typically platform lead + InfoSec lead jointly)

### Rev Attestation

<<MUST item:A.5.23:rev_attestation>>
_Why: 27002:5.23 — CSP assurance_

> _Standard text:_ CSP attestation refresh checked per service (current vs stale)

### Rev Config Drift

<<MUST item:A.5.23:rev_config_drift>>
_Why: 27002:5.23d,g_

> _Standard text:_ Configuration-drift assessment against the shared-responsibility split (what the org owns is configured correctly)

### Rev Geo Compliance

<<MUST item:A.5.23:rev_geo_compliance>>
_Why: 27002:5.23 — geo_

> _Standard text:_ Geographic-location compliance check (data has not silently drifted to non-approved regions)

### Rev Incidents

<<MUST item:A.5.23:rev_incidents>>
_Why: 27002:5.23f_

> _Standard text:_ Cloud-incidents in the period reviewed (own + CSP-disclosed)

### Rev Actions

<<MUST item:A.5.23:rev_actions>>
_Why: 27002:5.23g_

> _Standard text:_ Action items captured per service

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Threat Intel

<<SHOULD item:A.5.23:rev_threat_intel>>
_Why: Audit defensibility_

> _Standard text:_ External threat-intel input considered (link to A.5.7)

### Rev Next Date

<<SHOULD item:A.5.23:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
