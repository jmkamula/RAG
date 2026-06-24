---
leaf_id: req:Art.47:applicable_scope
control_ref: Art.47
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable BCR Scope

> The upstream — which intra-group flows are covered by BCRs, which entities are bound, third-country expansion handling

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Intra-group flows covered (controller-to-controller / controller-to-processor)

<<MUST item:Art.47:scope_intra_group_flows>>
_Why: Art.47 — group of enterprises_

<<TEXT>>

## 2. Bound entities enumerated (jurisdictions + roles)

<<MUST item:Art.47:scope_entities>>
_Why: Art.47.1.a_

<<TEXT>>

## 3. New-entity onboarding rule — how a newly-acquired or newly-spun-up entity joins the BCRs (or moves to alternative safeguard)

<<MUST item:Art.47:scope_extension>>
_Why: Lifecycle_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (M&A, divestment, regulatory change)

<<SHOULD item:Art.47:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
