---
leaf_id: req:A.7.3.7:applicable_scope
control_ref: A.7.3.7
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Third-Party Sharing Scope

> The upstream — which third parties have received the org's PII (from A.7.5 sharing/transfer/disclosure) and therefore require notification when subject events occur.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Third-party recipients enumerated (link to A.7.5.4 disclosure register)

<<MUST item:A.7.3.7:scope_recipients_list>>
_Why: Coverage_

<<TEXT>>

## 2. Per-recipient communication channel (email / API / portal)

<<MUST item:A.7.3.7:scope_channel_map>>
_Why: §7.3.7 — active communication channels_

<<TEXT>>

## 3. Excluded recipients with rationale (e.g. one-time disclosures with PII already destroyed)

<<MUST item:A.7.3.7:scope_exclusions>>
_Why: Defensibility_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new third-party sharing / termination of sharing)

<<SHOULD item:A.7.3.7:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
