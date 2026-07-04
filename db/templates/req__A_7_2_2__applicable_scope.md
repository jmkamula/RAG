---
leaf_id: req:A.7.2.2:applicable_scope
control_ref: A.7.2.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Jurisdictions + Bases Scope

> The upstream — which jurisdictions apply to the org's processing (GDPR, UK GDPR, CCPA, LGPD, etc.) and therefore which lawful-basis catalogs are in play. Handles multi-jurisdictional overlap (e.g. cross-border processing needs bases valid in every applicable jurisdiction).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Applicable jurisdictions listed (with basis for each — establishment / target-market / monitoring)

<<MUST item:A.7.2.2:scope_jurisdictions>>
_Why: §7.2.2 — applicable jurisdictions_

<<TEXT>>

## 2. Per-jurisdiction basis catalog (Art.6.1 GDPR / CCPA opt-out model / LGPD Art.7)

<<MUST item:A.7.2.2:scope_basis_catalogs>>
_Why: §7.2.2 implementation guidance_

<<TEXT>>

## 3. Overlap rules — where an activity spans jurisdictions, most-restrictive-basis policy documented

<<MUST item:A.7.2.2:scope_overlap_rules>>
_Why: Cross-border processing_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new geo entry, new regulation enacted)

<<SHOULD item:A.7.2.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
