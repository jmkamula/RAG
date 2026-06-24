---
leaf_id: req:7.5:isms_document_register
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 1
---

# ISMS Document Register

> Per-document record — every controlled ISMS document with owner, version, approval date, next review date. The live inventory that proves the policy is being applied. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Unique document identifier per row

<<MUST item:7.5:reg_doc_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Document title per row

<<MUST item:7.5:reg_title>>
_Why: Discoverability_

<<TEXT>>

## 3. Document owner per row

<<MUST item:7.5:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Current version per row

<<MUST item:7.5:reg_version>>
_Why: Clause 7.5.3 — control_

<<TEXT>>

## 5. Last approval date per row

<<MUST item:7.5:reg_approval_date>>
_Why: Currency_

<<TEXT>>

## 6. Next review date per row (drives staleness alerts)

<<MUST item:7.5:reg_next_review>>
_Why: Currency_

<<TEXT>>

## 7. Information classification per row (cross-link to A.5.12)

<<MUST item:7.5:reg_classification>>
_Why: Clause 7.5.3 — protected_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Retention period per row (cross-link to A.5.33 / A.5.34)

<<SHOULD item:7.5:reg_retention>>
_Why: Clause 7.5.3 — retention_

<<TEXT>>
