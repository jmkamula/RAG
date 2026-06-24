---
leaf_id: req:Art.27:applicable_scope
control_ref: Art.27
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Art.27 Scope

> The upstream — whether the controller/processor is in scope for Art.27 (not established in EU AND processing falls under Art.3.2) and any Art.27.2 exceptions (occasional + no large-scale special-category + low risk + public authority)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Establishment analysis — where the controller/processor is established + why Art.3.2 applies (offering goods/services OR monitoring behaviour in Union)

<<MUST item:Art.27:scope_establishment>>
_Why: Art.3.2_

<<TEXT>>

## 2. MS targeted (Art.27.3 — representative MUST be in one of these)

<<MUST item:Art.27:scope_member_state_target>>
_Why: Art.27.3_

<<TEXT>>

## 3. Art.27.2 exception assessment (occasional processing + no special-category-large-scale + low risk → no representative needed). Decision recorded

<<MUST item:Art.27:scope_art27_2_exception>>
_Why: Art.27.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (EU market entry/exit, processing-pattern change)

<<SHOULD item:Art.27:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
