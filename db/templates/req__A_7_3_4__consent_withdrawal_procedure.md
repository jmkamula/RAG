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

<<DOC_CONTROL>>

> §7.3.4 requires a mechanism for subjects to modify or withdraw consent + propagation to downstream processing + third parties. Withdrawal channel parity (same as collection).

## What this template gives you

This template helps you document how individuals can change or withdraw their consent, and how you ensure those changes are communicated to all relevant parties, including third parties, in line with privacy standards.

## When to use it

Use this procedure whenever your organization needs to provide a clear way for people to modify or withdraw their consent, especially if your activities match specific privacy triggers. Update the document whenever your processes or legal requirements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this template from scratch, as each required section will take roughly 10 to 15 minutes to draft thoughtfully.

## 1. Channel parity — withdrawal via same medium as collection (email if email, web if web; not phone/fax fallback)

<<MUST item:A.7.3.4:proc_channel_parity>>
_Why: §7.3.4 implementation guidance — same as collection_

<<GUIDANCE>>

<<TEXT>>

## 2. Withdrawal as easy as giving — no additional hurdles beyond original consent process (Art.7.3)

<<MUST item:A.7.3.4:proc_easy_as_giving>>
_Why: GDPR Art.7.3 — as easy to withdraw_

<<GUIDANCE>>

<<TEXT>>

## 3. Modification paths (partial withdrawal / opt-in-to-fewer-purposes / restrict processing)

<<MUST item:A.7.3.4:proc_modification_paths>>
_Why: §7.3.4 — modify or withdraw_

<<GUIDANCE>>

<<TEXT>>

## 4. Response-time SLA stated + honoured

<<MUST item:A.7.3.4:proc_response_sla>>
_Why: §7.3.4 implementation — response time_

<<GUIDANCE>>

<<TEXT>>

## 5. Downstream propagation — withdrawal cascades to systems + authorised users + third parties (see A.7.3.7)

<<MUST item:A.7.3.4:proc_propagation>>
_Why: §7.3.4 — disseminate through systems_

<<GUIDANCE>>

<<TEXT>>

## 6. Pre-withdrawal processing remains valid; post-withdrawal processing halts (Art.7.3 — no retroactive effect)

<<MUST item:A.7.3.4:proc_pre_withdrawal_valid>>
_Why: §7.3.4 additional information_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic reminder that withdrawal is available (in-product / newsletter footer)

<<SHOULD item:A.7.3.4:proc_reminder>>
_Why: Best practice_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
