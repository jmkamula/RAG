---
leaf_id: req:5.2:isp_approval_record
control_ref: 5.2
standard_id: ISO27001:2022
evidence_type: approval_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Information Security Policy Approval Record

> The per-version approval evidence — who signed off, on what date, against what scope. Distinct from the policy file itself: this is the audit trail of top-management approval across versions

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Signature of top management on the latest version

<<MUST item:5.2:app_signature>>
_Why: Clause 5.2 — approved by top management_

<<TEXT>>

## 2. Approval date stated

<<MUST item:5.2:app_date>>
_Why: Authenticity_

<<TEXT>>

## 3. Approving role identified (CEO, board chair, or delegated authority with letter of delegation)

<<MUST item:5.2:app_role>>
_Why: Authority_

<<TEXT>>

## 4. Scope statement (4.3) version that was in effect at approval

<<MUST item:5.2:app_scope_at_approval>>
_Why: Cross-clause coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Prior approval signatures retained for audit trail (covers turnover)

<<SHOULD item:5.2:app_prior_versions>>
_Why: Audit defensibility_

<<TEXT>>
