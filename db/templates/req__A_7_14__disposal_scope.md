---
leaf_id: req:A.7.14:disposal_scope
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Equipment Disposal Scope

> The upstream — equipment classes in scope, disposal triggers, exclusions

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Equipment classes in scope (anything with storage — explicit list)

<<MUST item:A.7.14:scope_classes>>
_Why: 27002:7.14 — equipment containing storage media_

<<TEXT>>

## 2. Disposal triggers (end-of-life, replacement, return-from-lease, sale, donation, scrap)

<<MUST item:A.7.14:scope_triggers>>
_Why: 27002:7.14 — disposal or re-use_

<<TEXT>>

## 3. Destination scenarios (recycler / charity donation / re-sale / internal re-use / certified destruction)

<<MUST item:A.7.14:scope_destinations>>
_Why: 27002:7.14 — appropriate handling_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new equipment class entering EOL, regulatory change on disposal)

<<SHOULD item:A.7.14:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
