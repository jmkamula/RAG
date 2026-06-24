---
leaf_id: req:A.5.20:template_review
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Periodic Supplier Agreement Template Review

> The supplier agreement template ages: regulations change, threat landscape shifts, internal control baselines evolve. The periodic review captures who reviewed it, when, what changed, and the re-papering plan for existing supplier agreements that need to catch up

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.20:rev_date>>
_Why: 27002:5.20 — periodic_

<<TEXT>>

## 2. Reviewer identity (legal + InfoSec lead jointly)

<<MUST item:A.5.20:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Regulatory changes considered (data protection, sector-specific obligations)

<<MUST item:A.5.20:rev_regulatory>>
_Why: 27002:5.20c,p_

<<TEXT>>

## 4. Threat-landscape changes considered (e.g. emergent incident-notification expectations)

<<MUST item:A.5.20:rev_threat_landscape>>
_Why: 27002:5.20 — keep current_

<<TEXT>>

## 5. Outcome (no change / amended; version increment if amended)

<<MUST item:A.5.20:rev_outcome>>
_Why: 27002:5.20_

<<TEXT>>

## 6. Re-papering plan for existing supplier agreements that need to catch up to a new template version

<<MUST item:A.5.20:rev_repapering>>
_Why: Operational sufficiency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External counsel or industry-benchmark input considered

<<SHOULD item:A.5.20:rev_external_input>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.20:rev_next_date>>
_Why: Planning_

<<TEXT>>
