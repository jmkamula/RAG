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

<<DOC_CONTROL>>

> The upstream — which jurisdictions apply to the org's processing (GDPR, UK GDPR, CCPA, LGPD, etc.) and therefore which lawful-basis catalogs are in play. Handles multi-jurisdictional overlap (e.g. cross-border processing needs bases valid in every applicable jurisdiction).

## What this template gives you

This template helps you clearly identify which privacy laws and regulations apply to your organization, and explains which legal bases you need to consider for data processing across different regions.

## When to use it

Use this document when your organization operates in multiple countries or regions, or whenever your business activities change in a way that might affect which privacy laws apply. Update it as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this template from scratch, depending on how many jurisdictions and legal bases you need to cover.

## 1. Applicable jurisdictions listed (with basis for each — establishment / target-market / monitoring)

<<MUST item:A.7.2.2:scope_jurisdictions>>
_Why: §7.2.2 — applicable jurisdictions_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-jurisdiction basis catalog (Art.6.1 GDPR / CCPA opt-out model / LGPD Art.7)

<<MUST item:A.7.2.2:scope_basis_catalogs>>
_Why: §7.2.2 implementation guidance_

<<GUIDANCE>>

<<TEXT>>

## 3. Overlap rules — where an activity spans jurisdictions, most-restrictive-basis policy documented

<<MUST item:A.7.2.2:scope_overlap_rules>>
_Why: Cross-border processing_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new geo entry, new regulation enacted)

<<SHOULD item:A.7.2.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
