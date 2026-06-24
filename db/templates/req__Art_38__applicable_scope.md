---
leaf_id: req:Art.38:applicable_scope
control_ref: Art.38
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Art.38 Position Scope

> The upstream — which forums DPO attends, what budget envelope applies, the org's COI matrix

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Forums DPO is invited to (board, exec committee, change-management, incident response, vendor onboarding)

<<MUST item:Art.38:scope_forums>>
_Why: Art.38.1_

<<TEXT>>

## 2. Resource envelope (budget category + escalation threshold for additional spend)

<<MUST item:Art.38:scope_resource_envelope>>
_Why: Art.38.2_

<<TEXT>>

## 3. COI matrix — which other roles DPO cannot also hold (CISO / security architect / product owner of PII flows / etc.)

<<MUST item:Art.38:scope_coi_matrix>>
_Why: Art.38.6_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (org restructure, DPO transition, new business line)

<<SHOULD item:Art.38:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
