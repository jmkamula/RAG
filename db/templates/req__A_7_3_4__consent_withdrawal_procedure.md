---
leaf_id: req:A.7.3.4:consent_withdrawal_procedure
control_ref: A.7.3.4
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 6
should_count: 1
---

# Consent Modification / Withdrawal Procedure

> §7.3.4 requires a mechanism for subjects to modify or withdraw consent + propagation to downstream processing + third parties. Withdrawal channel parity (same as collection).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Channel parity — withdrawal via same medium as collection (email if email, web if web; not phone/fax fallback)

<<MUST item:A.7.3.4:proc_channel_parity>>
_Why: §7.3.4 implementation guidance — same as collection_

<<TEXT>>

## 2. Withdrawal as easy as giving — no additional hurdles beyond original consent process (Art.7.3)

<<MUST item:A.7.3.4:proc_easy_as_giving>>
_Why: GDPR Art.7.3 — as easy to withdraw_

<<TEXT>>

## 3. Modification paths (partial withdrawal / opt-in-to-fewer-purposes / restrict processing)

<<MUST item:A.7.3.4:proc_modification_paths>>
_Why: §7.3.4 — modify or withdraw_

<<TEXT>>

## 4. Response-time SLA stated + honoured

<<MUST item:A.7.3.4:proc_response_sla>>
_Why: §7.3.4 implementation — response time_

<<TEXT>>

## 5. Downstream propagation — withdrawal cascades to systems + authorised users + third parties (see A.7.3.7)

<<MUST item:A.7.3.4:proc_propagation>>
_Why: §7.3.4 — disseminate through systems_

<<TEXT>>

## 6. Pre-withdrawal processing remains valid; post-withdrawal processing halts (Art.7.3 — no retroactive effect)

<<MUST item:A.7.3.4:proc_pre_withdrawal_valid>>
_Why: §7.3.4 additional information_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic reminder that withdrawal is available (in-product / newsletter footer)

<<SHOULD item:A.7.3.4:proc_reminder>>
_Why: Best practice_

<<TEXT>>
