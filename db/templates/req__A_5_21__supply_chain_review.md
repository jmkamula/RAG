---
leaf_id: req:A.5.21:supply_chain_review
control_ref: A.5.21
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Periodic ICT Supply Chain Review

<<DOC_CONTROL>>

> ICT supply chains are volatile — vendor M&A, EOL pipelines, new vulnerability disclosures and sub-supplier shifts can move risk significantly inside a year. The review record captures the planned-interval review of the component register, the vendor-maturity assessment, the EOL pipeline and the resulting action items

<!-- TABLE-COLUMNS leaf:req:A.5.21:supply_chain_review -->
<!-- column: item:A.5.21:rev_date -->
<!-- column: item:A.5.21:rev_reviewer -->
<!-- column: item:A.5.21:rev_eol_pipeline -->
<!-- column: item:A.5.21:rev_maturity -->
<!-- column: item:A.5.21:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically review and document the health and risks of your ICT supply chain, including vendor changes, end-of-life issues, and new vulnerabilities. It provides a clear record of your findings and action items.

## When to use it

Use this template whenever you need to review your ICT supply chain, which should be about every six months. It’s designed for regular, planned assessments to keep your records current and risks managed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of components and vendors you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.21:supply_chain_review -->
| Rev Date | Rev Reviewer | Rev Eol Pipeline | Rev Maturity | Rev Actions |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.21:supply_chain_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.21:rev_date>>
_Why: 27002:5.21 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.21:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (typically architecture lead + InfoSec lead)

<<GUIDANCE>>

### Rev Eol Pipeline

<<MUST item:A.5.21:rev_eol_pipeline>>
_Why: 27002:5.21i_

> _Standard text:_ EOL pipeline review (which components reach EOL in the next planning horizon, replacement status)

<<GUIDANCE>>

### Rev Maturity

<<MUST item:A.5.21:rev_maturity>>
_Why: 27002:5.21d_

> _Standard text:_ Vendor maturity review (recent attestations, incidents, sub-supplier disclosures)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.21:rev_actions>>
_Why: 27002:5.21d,i_

> _Standard text:_ Action items captured per critical component (e.g. tighten monitoring, push for upgrade, replan replacement)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Threat Intel

<<SHOULD item:A.5.21:rev_threat_intel>>
_Why: Audit defensibility_

> _Standard text:_ External threat intelligence input considered (link to A.5.7)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.21:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
