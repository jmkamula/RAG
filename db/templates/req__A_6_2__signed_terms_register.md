---
leaf_id: req:A.6.2:signed_terms_register
control_ref: A.6.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Signed Employment Terms Register

> The operational catalogue of who has signed which version of the employment terms. Each row: personnel identifier, template version signed, signature date, current-version check. Drives the 'every active employee has current terms' completeness check

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row personnel identifier (links to identity register A.5.16)

<<MUST item:A.6.2:reg_personnel_id>>
_Why: Accountability_

<<TEXT>>

## 2. Template version signed per row (drives currency check — old-version signers may need recontract on material changes)

<<MUST item:A.6.2:reg_template_version>>
_Why: 27002:6.2 — current_

<<TEXT>>

## 3. Signature date per row (proves signing happened BEFORE access granted per A.5.18)

<<MUST item:A.6.2:reg_signature_date>>
_Why: 27002:6.2 — before access_

<<TEXT>>

## 4. Signature method per row (wet signature scanned / e-signature platform reference; ensures non-repudiation)

<<MUST item:A.6.2:reg_signature_method>>
_Why: Audit defensibility_

<<TEXT>>

## 5. Current-version check flag per row (yes / no-with-rationale-for-grandfathering) — surfaces personnel on outdated terms

<<MUST item:A.6.2:reg_current_version_check>>
_Why: 27002:6.2 — currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Amendment history per row where contracts were amended mid-employment (drives change tracking)

<<SHOULD item:A.6.2:reg_amendment_history>>
_Why: Operational discipline_

<<TEXT>>

### 2. Worker category per row (employee / contractor / intern — different categories may use different templates)

<<SHOULD item:A.6.2:reg_worker_category>>
_Why: Cross-leaf coherence_

<<TEXT>>
