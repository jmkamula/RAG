---
leaf_id: req:A.8.2:privileged_access_recertification
control_ref: A.8.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# Privileged Access Recertification

<<DOC_CONTROL>>

> A.8.2 calls for periodic review of privileged access — typically more frequent than the general access review at A.5.18 (this curation sets freshness at 180 days; tenants with high-risk processing may run quarterly). The recertification record evidences that each privileged grant was re-confirmed by the asset owner

<!-- TABLE-COLUMNS leaf:req:A.8.2:privileged_access_recertification -->
<!-- column: item:A.8.2:rc_date -->
<!-- column: item:A.8.2:rc_reviewer -->
<!-- column: item:A.8.2:rc_per_account -->
<!-- column: item:A.8.2:rc_actions -->
<!-- column: item:A.8.2:rc_sla_met -->
<!-- column: item:A.8.2:rc_a518_pairing -->
<!-- column: item:A.8.2:rc_role_change_trigger -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of who has privileged access in your systems and confirms that each access grant has been reviewed and approved by the appropriate asset owner. It's designed to support your compliance with ISO 27001 requirements for privileged access reviews.

## When to use it

Use this template whenever you need to review privileged access in your environment, which should happen about twice a year, or more often if your organization handles higher-risk data or processes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element, plus additional time for each privileged user you need to review. Completing the register from scratch may take a few hours, depending on the number of privileged accounts.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.2:privileged_access_recertification -->
| Rc Date | Rc Reviewer | Rc Per Account | Rc Actions | Rc Sla Met | Rc A518 Pairing | Rc Role Change Trigger |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.2:privileged_access_recertification -->

## Column guidance — what to fill in

### Rc Date

<<MUST item:A.8.2:rc_date>>
_Why: 27002:8.2k_

> _Standard text:_ Recertification date within the planned interval (≤180 days since last)

<<GUIDANCE>>

### Rc Reviewer

<<MUST item:A.8.2:rc_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (asset owner or delegated authority)

<<GUIDANCE>>

### Rc Per Account

<<MUST item:A.8.2:rc_per_account>>
_Why: 27002:8.2k_

> _Standard text:_ Per-privileged-account outcome (re-confirmed / amended / revoked)

<<GUIDANCE>>

### Rc Actions

<<MUST item:A.8.2:rc_actions>>
_Why: 27002:8.2k_

> _Standard text:_ Revocation/modification actions completed for non-reconfirmed access

<<GUIDANCE>>

### Rc Sla Met

<<MUST item:A.8.2:rc_sla_met>>
_Why: 27002:8.2k modern interpretation (Style v2)_

> _Standard text:_ Revocation-actions-within-SLA flag per row (auditor-critical timeliness proof, parallel to A.5.16 rev_sla_met)

<<GUIDANCE>>

### Rc A518 Pairing

<<MUST item:A.8.2:rc_a518_pairing>>
_Why: Cross-control coherence (Style v2)_

> _Standard text:_ Cross-link to A.5.18 general access review — every privileged subject also appears under their general access row (no orphan privileged paths)

<<GUIDANCE>>

### Rc Role Change Trigger

<<MUST item:A.8.2:rc_role_change_trigger>>
_Why: 27002:8.2g (Style v2 promotion)_

> _Standard text:_ Role-change events trigger ad-hoc recertification outside the interval

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rc Next Date

<<SHOULD item:A.8.2:rc_next_date>>
_Why: Planning_

> _Standard text:_ Next planned recertification date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
