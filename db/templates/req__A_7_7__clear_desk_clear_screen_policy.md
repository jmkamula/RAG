---
leaf_id: req:A.7.7:clear_desk_clear_screen_policy
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Clear Desk and Clear Screen Policy

<<DOC_CONTROL>>

> A.7.7 requires clear-desk rules for papers/removable media plus clear-screen rules for information processing facilities. The policy states both rules and enforcement. The audit register, applicable-locations scope and periodic review are sibling leaves

## What this template gives you

This template helps you create a policy that sets out clear desk and clear screen rules, ensuring sensitive information is protected in your workplace and on your devices. It covers both the rules and how they are enforced.

## When to use it

Use this template whenever you need to establish or update your organization's approach to keeping desks and screens clear of sensitive information. Review and refresh the policy as needed to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours drafting this policy from scratch, as each required section takes around 10-15 minutes to complete.

## 1. Clear-desk rule for papers and removable media when desk unattended

<<MUST item:A.7.7:clear_desk_rule>>
_Why: 27002:7.7 — clear desk rules_

<<GUIDANCE>>

<<TEXT>>

## 2. Clear-screen rule (screen lock on leaving, automatic lockout after N minutes)

<<MUST item:A.7.7:clear_screen_rule>>
_Why: 27002:7.7 — clear screen rules_

<<GUIDANCE>>

<<TEXT>>

## 3. Removable media handling rules (locked away when unattended)

<<MUST item:A.7.7:removable_media>>
_Why: 27002:7.7 — removable storage media_

<<GUIDANCE>>

<<TEXT>>

## 4. Locked storage requirements per classification level (links to A.5.12)

<<MUST item:A.7.7:locked_storage>>
_Why: 27002:7.7 — appropriately enforced_

<<GUIDANCE>>

<<TEXT>>

## 5. Enforcement approach (spot checks, awareness, sanctions)

<<MUST item:A.7.7:enforcement>>
_Why: 27002:7.7 — appropriately enforced_

<<GUIDANCE>>

<<TEXT>>

## 6. Specific rules for meeting rooms and shared spaces (whiteboard wipe, printout collection)

<<MUST item:A.7.7:meeting_rooms>>
_Why: Common gap_

<<GUIDANCE>>

<<TEXT>>

## 7. Printer / multifunction device rules (pull-print, collect immediately, fax-line policy)

<<MUST item:A.7.7:printer_rules>>
_Why: Often-leaked artefacts_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Home-office overlay (clear-desk rules adapted for remote workers — cross-link to A.6.7)

<<SHOULD item:A.7.7:home_office_overlay>>
_Why: Hybrid work realism_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
