---
leaf_id: req:5.2:isp_approval_record
control_ref: 5.2
standard_id: ISO27001:2022
evidence_type: approval_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Information Security Policy Approval Record

<<DOC_CONTROL>>

> The per-version approval evidence — who signed off, on what date, against what scope. Distinct from the policy file itself: this is the audit trail of top-management approval across versions

<!-- TABLE-COLUMNS leaf:req:5.2:isp_approval_record -->
<!-- column: item:5.2:app_signature -->
<!-- column: item:5.2:app_date -->
<!-- column: item:5.2:app_role -->
<!-- column: item:5.2:app_scope_at_approval -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, auditable record of who approved each version of your Information Security Policy, when they did so, and the scope of their approval. It’s useful for demonstrating top-management oversight to auditors.

## When to use it

Use this template whenever you update or create a new version of your Information Security Policy, and refresh it as needed to capture each new approval or change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes filling this out from scratch, depending on the number of approvals you need to record and the amount of detail required for each entry.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:5.2:isp_approval_record -->
| App Signature | App Date | App Role | App Scope At Approval |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:5.2:isp_approval_record -->

## Column guidance — what to fill in

### App Signature

<<MUST item:5.2:app_signature>>
_Why: Clause 5.2 — approved by top management_

> _Standard text:_ Signature of top management on the latest version

<<GUIDANCE>>

### App Date

<<MUST item:5.2:app_date>>
_Why: Authenticity_

> _Standard text:_ Approval date stated

<<GUIDANCE>>

### App Role

<<MUST item:5.2:app_role>>
_Why: Authority_

> _Standard text:_ Approving role identified (CEO, board chair, or delegated authority with letter of delegation)

<<GUIDANCE>>

### App Scope At Approval

<<MUST item:5.2:app_scope_at_approval>>
_Why: Cross-clause coherence_

> _Standard text:_ Scope statement (4.3) version that was in effect at approval

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### App Prior Versions

<<SHOULD item:5.2:app_prior_versions>>
_Why: Audit defensibility_

> _Standard text:_ Prior approval signatures retained for audit trail (covers turnover)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
