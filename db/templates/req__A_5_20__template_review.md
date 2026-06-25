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
table_shape: true
---

# Periodic Supplier Agreement Template Review

> The supplier agreement template ages: regulations change, threat landscape shifts, internal control baselines evolve. The periodic review captures who reviewed it, when, what changed, and the re-papering plan for existing supplier agreements that need to catch up

<!-- TABLE-COLUMNS leaf:req:A.5.20:template_review -->
<!-- column: item:A.5.20:rev_date -->
<!-- column: item:A.5.20:rev_reviewer -->
<!-- column: item:A.5.20:rev_regulatory -->
<!-- column: item:A.5.20:rev_threat_landscape -->
<!-- column: item:A.5.20:rev_outcome -->
<!-- column: item:A.5.20:rev_repapering -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.20:template_review -->
| Rev Date | Rev Reviewer | Rev Regulatory | Rev Threat Landscape | Rev Outcome | Rev Repapering |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.20:template_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.20:rev_date>>
_Why: 27002:5.20 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.5.20:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (legal + InfoSec lead jointly)

### Rev Regulatory

<<MUST item:A.5.20:rev_regulatory>>
_Why: 27002:5.20c,p_

> _Standard text:_ Regulatory changes considered (data protection, sector-specific obligations)

### Rev Threat Landscape

<<MUST item:A.5.20:rev_threat_landscape>>
_Why: 27002:5.20 — keep current_

> _Standard text:_ Threat-landscape changes considered (e.g. emergent incident-notification expectations)

### Rev Outcome

<<MUST item:A.5.20:rev_outcome>>
_Why: 27002:5.20_

> _Standard text:_ Outcome (no change / amended; version increment if amended)

### Rev Repapering

<<MUST item:A.5.20:rev_repapering>>
_Why: Operational sufficiency_

> _Standard text:_ Re-papering plan for existing supplier agreements that need to catch up to a new template version

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev External Input

<<SHOULD item:A.5.20:rev_external_input>>
_Why: Audit defensibility_

> _Standard text:_ External counsel or industry-benchmark input considered

### Rev Next Date

<<SHOULD item:A.5.20:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
