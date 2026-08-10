---
leaf_id: req:A.5.35:finding_response_register
control_ref: A.5.35
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Independent Review Finding Response Register

<<DOC_CONTROL>>

> A.5.35 requires management response to findings — but the response promise is theoretical without a per-finding lifecycle tracker. The register catalogues every finding from every independent review: severity, owner, agreed treatment, target date, closure status. This is the audit-defensibility artefact: 'show me what you did with the findings from the 2024 review' has a one-table answer

<!-- TABLE-COLUMNS leaf:req:A.5.35:finding_response_register -->
<!-- column: item:A.5.35:fr_finding_id -->
<!-- column: item:A.5.35:fr_severity -->
<!-- column: item:A.5.35:fr_owner -->
<!-- column: item:A.5.35:fr_treatment -->
<!-- column: item:A.5.35:fr_status -->
<!-- column: item:A.5.35:fr_closure_evidence -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you track every finding from independent reviews, including details like severity, owner, and status. It provides a clear, audit-ready record of how each finding was addressed and closed.

## When to use it

Use this register whenever your organization receives findings from an independent review, and update it as needed to reflect progress or closure of each item. It should always be maintained for your environment.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60-90 minutes to set up the register for the first time, plus 10-15 minutes for each new finding you need to add and update as reviews occur.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.35:finding_response_register -->
| Fr Finding Id | Fr Severity | Fr Owner | Fr Treatment | Fr Status | Fr Closure Evidence |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.35:finding_response_register -->

## Column guidance — what to fill in

### Fr Finding Id

<<MUST item:A.5.35:fr_finding_id>>
_Why: 27002:5.35 — review_

> _Standard text:_ Per-finding unique identifier traceable back to the source review report

<<GUIDANCE>>

### Fr Severity

<<MUST item:A.5.35:fr_severity>>
_Why: 27002:5.35 — review_

> _Standard text:_ Severity recorded per finding (matches the report's severity classification)

<<GUIDANCE>>

### Fr Owner

<<MUST item:A.5.35:fr_owner>>
_Why: Accountability_

> _Standard text:_ Named owner per finding (named individual, not generic team) with target closure date

<<GUIDANCE>>

### Fr Treatment

<<MUST item:A.5.35:fr_treatment>>
_Why: Closes the loop_

> _Standard text:_ Agreed treatment per finding (accept / remediate / transfer with rationale; mirrors the management response committed in the report)

<<GUIDANCE>>

### Fr Status

<<MUST item:A.5.35:fr_status>>
_Why: Operational discipline_

> _Standard text:_ Current status per finding (open / in-progress / closed / aged-overdue) with last-updated date

<<GUIDANCE>>

### Fr Closure Evidence

<<MUST item:A.5.35:fr_closure_evidence>>
_Why: Audit defensibility_

> _Standard text:_ Closure evidence reference per closed finding (link to the artefact that proves the finding was addressed — control change, policy update, training delivered)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Fr Aging Alerts

<<SHOULD item:A.5.35:fr_aging_alerts>>
_Why: Operational discipline_

> _Standard text:_ Aged-overdue alerting (notification when target date passes without closure)

<<GUIDANCE>>

### Fr Cross Review Link

<<SHOULD item:A.5.35:fr_cross_review_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to A.5.36 compliance-review nonconformity register where the two are kept as one artefact (common in mature programs)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
