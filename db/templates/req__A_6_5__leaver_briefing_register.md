---
leaf_id: req:A.6.5:leaver_briefing_register
control_ref: A.6.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Leaver Briefing Register

> The operational catalogue of exit briefings and role-change briefings. Each event: leaver identifier, trigger (termination / contract end / role change), briefing date, briefer, signed acknowledgment of surviving obligations. Drives 'show me every leaver acknowledged their post-employment obligations' audit

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row leaver identifier (links to identity register A.5.16; cross-link to A.5.11 return-of-assets record + A.5.16 identity revocation)

<<MUST item:A.6.5:reg_leaver_id>>
_Why: Cross-control coherence_

<<TEXT>>

## 2. Per-row trigger (termination / contract end / role change within org / retirement)

<<MUST item:A.6.5:reg_trigger>>
_Why: 27002:6.5 — termination or change_

<<TEXT>>

## 3. Per-row briefing date (typically last working day or shortly after; for role change, at point of role transition)

<<MUST item:A.6.5:reg_briefing_date>>
_Why: 27002:6.5 — communicated_

<<TEXT>>

## 4. Per-row briefer identity (HR partner; line manager joins for role-change cases)

<<MUST item:A.6.5:reg_briefer>>
_Why: Accountability_

<<TEXT>>

## 5. Per-row signed acknowledgment evidence (digital signature / signed PDF / recorded receipt of intranet artefact)

<<MUST item:A.6.5:reg_acknowledgment>>
_Why: 27002:6.5 — communicated_

<<TEXT>>

## 6. Per-row covered obligations list (confidentiality + IP + non-poach + non-compete where applicable per jurisdiction)

<<MUST item:A.6.5:reg_obligations_covered>>
_Why: 27002:6.5 — duties that remain_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row post-briefing check (30/90/180-day check that no breach has occurred — proportional to role seniority)

<<SHOULD item:A.6.5:reg_post_briefing_check>>
_Why: Continual assurance_

<<TEXT>>

### 2. Per-row cross-link to A.5.11 return-of-assets register (same leaver event)

<<SHOULD item:A.6.5:reg_a5_11_link>>
_Why: Cross-control coherence_

<<TEXT>>
