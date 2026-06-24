---
leaf_id: req:Art.45:applicable_scope
control_ref: Art.45
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Adequacy Scope

> The upstream — which destinations covered by Art.45.3 decisions the org actually relies on + recipient-eligibility verification approach

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Adequate destinations in use (e.g. UK, Japan, US-DPF certified)

<<MUST item:Art.45:scope_destinations>>
_Why: Art.45.3_

<<TEXT>>

## 2. Eligibility-proof method per destination (Commission register / DPF list / etc.)

<<MUST item:Art.45:scope_eligibility_proof>>
_Why: Defensibility_

<<TEXT>>

## 3. Destinations specifically NOT relying on adequacy (fall to Art.46/49)

<<MUST item:Art.45:scope_excluded>>
_Why: Defensible bounding_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new adequacy decision, repeal, vendor change of certification)

<<SHOULD item:Art.45:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
