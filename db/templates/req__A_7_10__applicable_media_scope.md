---
leaf_id: req:A.7.10:applicable_media_scope
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Media Classes Scope

> The upstream — which media classes are in scope, applicable use cases, exclusions

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Media classes (USB drives, external HDDs, optical disks, tape, paper-with-PII, mobile devices with data)

<<MUST item:A.7.10:scope_media_classes>>
_Why: 27002:7.10 — relevant media_

<<TEXT>>

## 2. Use cases enumerated (backup transport, courier-of-data, demo loaners, archive)

<<MUST item:A.7.10:scope_use_cases>>
_Why: 27002:7.10 — use_

<<TEXT>>

## 3. Exclusions (cloud storage handled by A.8.10 information deletion; in-band system storage)

<<MUST item:A.7.10:scope_exclusions>>
_Why: 27002:7.10 — applicability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new media format, deprecation of media class)

<<SHOULD item:A.7.10:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
