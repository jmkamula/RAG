---
leaf_id: req:Art.10:criminal_data_processing_register
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Criminal Data Processing Register

> Per-activity register for every Art.10 processing operation — which Member State law applies, what safeguards, what retention. Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Activity identifier per row (links to Art.30 RoPA)

<<MUST item:Art.10:reg_activity_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-row legal basis (official authority OR specific Member State law citation)

<<MUST item:Art.10:reg_legal_basis>>
_Why: Art.10_

<<TEXT>>

## 3. Per-row purpose (must be narrow — pre-employment screening, sanctions check, regulatory KYC, fraud investigation)

<<MUST item:Art.10:reg_purpose>>
_Why: Art.10 — appropriate safeguards_

<<TEXT>>

## 4. Per-row safeguards (retention limit, access restrictions, separate-system storage)

<<MUST item:Art.10:reg_safeguards>>
_Why: Art.10_

<<TEXT>>

## 5. Per-row approval signature + date

<<MUST item:Art.10:reg_approval>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row cross-reference to Art.30 RoPA entry

<<SHOULD item:Art.10:reg_ropa_xref>>
_Why: Cross-article coherence_

<<TEXT>>
