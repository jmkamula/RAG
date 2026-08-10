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

<<DOC_CONTROL>>

> The supplier agreement template ages: regulations change, threat landscape shifts, internal control baselines evolve. The periodic review captures who reviewed it, when, what changed, and the re-papering plan for existing supplier agreements that need to catch up

<!-- TABLE-COLUMNS leaf:req:A.5.20:template_review -->
<!-- column: item:A.5.20:rev_date -->
<!-- column: item:A.5.20:rev_reviewer -->
<!-- column: item:A.5.20:rev_regulatory -->
<!-- column: item:A.5.20:rev_threat_landscape -->
<!-- column: item:A.5.20:rev_outcome -->
<!-- column: item:A.5.20:rev_repapering -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your supplier agreement documents up to date by recording who reviewed them, when, what was changed, and how you plan to update existing agreements. It supports compliance with ISO 27001 requirements.

## When to use it

Use this template whenever you review your supplier agreement template, which should happen about once a year or whenever regulations, risks, or internal controls change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on how many details and updates you need to document.

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

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.20:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (legal + InfoSec lead jointly)

<<GUIDANCE>>

### Rev Regulatory

<<MUST item:A.5.20:rev_regulatory>>
_Why: 27002:5.20c,p_

> _Standard text:_ Regulatory changes considered (data protection, sector-specific obligations)

<<GUIDANCE>>

### Rev Threat Landscape

<<MUST item:A.5.20:rev_threat_landscape>>
_Why: 27002:5.20 — keep current_

> _Standard text:_ Threat-landscape changes considered (e.g. emergent incident-notification expectations)

<<GUIDANCE>>

### Rev Outcome

<<MUST item:A.5.20:rev_outcome>>
_Why: 27002:5.20_

> _Standard text:_ Outcome (no change / amended; version increment if amended)

<<GUIDANCE>>

### Rev Repapering

<<MUST item:A.5.20:rev_repapering>>
_Why: Operational sufficiency_

> _Standard text:_ Re-papering plan for existing supplier agreements that need to catch up to a new template version

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev External Input

<<SHOULD item:A.5.20:rev_external_input>>
_Why: Audit defensibility_

> _Standard text:_ External counsel or industry-benchmark input considered

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.20:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
