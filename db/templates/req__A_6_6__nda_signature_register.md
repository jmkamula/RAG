---
leaf_id: req:A.6.6:nda_signature_register
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# NDA Signature Register

> The operational catalogue of NDA signings. Each row: signatory identifier, NDA variant signed, template version, signature date. Drives the 'every party with access has signed a current NDA' completeness check; the audit-defensibility gate for A.5.18 access grants to non-employees

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row signatory identifier (links to identity register A.5.16 for employees; supplier register A.5.19 for contractors; visitor-log for visitors)

<<MUST item:A.6.6:reg_signatory_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row NDA variant (employee / contractor / supplier-bilateral / M&A / visitor — matches the template variant_tiers SHOULD)

<<MUST item:A.6.6:reg_variant>>
_Why: 27002:6.6 — proportional_

<<TEXT>>

## 3. Per-row template version (drives currency check — old-version signers may need re-signing on material template changes)

<<MUST item:A.6.6:reg_template_version>>
_Why: 27002:6.6 — current_

<<TEXT>>

## 4. Per-row signature date (proves signing happened BEFORE access granted per A.5.18)

<<MUST item:A.6.6:reg_signature_date>>
_Why: 27002:6.6 — before access_

<<TEXT>>

## 5. Per-row signature method (wet / e-signature platform reference — ensures non-repudiation)

<<MUST item:A.6.6:reg_signature_method>>
_Why: Audit defensibility_

<<TEXT>>

## 6. Per-row status (active / expired-with-surviving-obligations / superseded-by-new-version)

<<MUST item:A.6.6:reg_expiry_or_active>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row cross-link to the offboarding event where applicable (A.6.5 leaver briefing reinforces surviving NDA obligations)

<<SHOULD item:A.6.6:reg_termination_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Per-row breach log (any suspected breach of NDA terms recorded with investigation outcome and enforcement decision)

<<SHOULD item:A.6.6:reg_breach_log>>
_Why: Continual assurance_

<<TEXT>>
