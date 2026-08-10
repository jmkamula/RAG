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

<<DOC_CONTROL>>

> The upstream — which third parties have received the org's PII (from A.7.5 sharing/transfer/disclosure) and therefore require notification when subject events occur.

## What this template gives you

This template helps you clearly identify which third parties have received your organization’s personal information, so you know who needs to be notified if there are any privacy-related events.

## When to use it

Use this document whenever your organization shares personal information with outside parties and needs to keep track of who should be notified if something changes. Update it whenever new sharing occurs or existing arrangements change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to gather and describe details for each required element.

## 1. Third-party recipients enumerated (link to A.7.5.4 disclosure register)

<<MUST item:A.7.3.7:scope_recipients_list>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-recipient communication channel (email / API / portal)

<<MUST item:A.7.3.7:scope_channel_map>>
_Why: §7.3.7 — active communication channels_

<<GUIDANCE>>

<<TEXT>>

## 3. Excluded recipients with rationale (e.g. one-time disclosures with PII already destroyed)

<<MUST item:A.7.3.7:scope_exclusions>>
_Why: Defensibility_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new third-party sharing / termination of sharing)

<<SHOULD item:A.7.3.7:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
