---
leaf_id: req:A.5.20:coverage_register
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Supplier Agreement Coverage Register

> An approved template alone does not protect the org — each supplier agreement must actually carry the relevant clauses. The coverage register tracks, per supplier, the template version applied, the date the agreement was signed, the agreement term, and the supplier tier — so it is auditable that the agreed clauses are in force

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Template version applied per supplier

<<MUST item:A.5.20:cov_template_version>>
_Why: 27002:5.20 — agreed_

<<TEXT>>

## 2. Signed-date of the active agreement per supplier

<<MUST item:A.5.20:cov_signed_date>>
_Why: Accountability_

<<TEXT>>

## 3. Agreement term and renewal/expiry date per row

<<MUST item:A.5.20:cov_term>>
_Why: Lifecycle_

<<TEXT>>

## 4. Supplier tier per row (drives which clause variant is required)

<<MUST item:A.5.20:cov_tier>>
_Why: Proportionality_

<<TEXT>>

## 5. Named owner accountable for the agreement (typically procurement or legal partner)

<<MUST item:A.5.20:cov_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Approved sub-processors per supplier tracked (link to A.5.19 supplier register)

<<SHOULD item:A.5.20:cov_subprocessors>>
_Why: 27002:5.20j_

<<TEXT>>

### 2. Governing jurisdiction per agreement

<<SHOULD item:A.5.20:cov_jurisdiction>>
_Why: 27002:5.20c,p_

<<TEXT>>
