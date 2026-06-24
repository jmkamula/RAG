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
---

# Periodic Cloud Service Posture Review

> A.5.23 expects ongoing monitoring, review and evaluation of cloud service use. The posture review captures the planned-interval check: refreshed CSP attestations, configuration-drift assessment against the shared-responsibility split, geographic-location compliance check, incident review, and resulting action items

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.23:rev_date>>
_Why: 27002:5.23g — monitoring_

<<TEXT>>

## 2. Reviewer identity (typically platform lead + InfoSec lead jointly)

<<MUST item:A.5.23:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. CSP attestation refresh checked per service (current vs stale)

<<MUST item:A.5.23:rev_attestation>>
_Why: 27002:5.23 — CSP assurance_

<<TEXT>>

## 4. Configuration-drift assessment against the shared-responsibility split (what the org owns is configured correctly)

<<MUST item:A.5.23:rev_config_drift>>
_Why: 27002:5.23d,g_

<<TEXT>>

## 5. Geographic-location compliance check (data has not silently drifted to non-approved regions)

<<MUST item:A.5.23:rev_geo_compliance>>
_Why: 27002:5.23 — geo_

<<TEXT>>

## 6. Cloud-incidents in the period reviewed (own + CSP-disclosed)

<<MUST item:A.5.23:rev_incidents>>
_Why: 27002:5.23f_

<<TEXT>>

## 7. Action items captured per service

<<MUST item:A.5.23:rev_actions>>
_Why: 27002:5.23g_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External threat-intel input considered (link to A.5.7)

<<SHOULD item:A.5.23:rev_threat_intel>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.23:rev_next_date>>
_Why: Planning_

<<TEXT>>
