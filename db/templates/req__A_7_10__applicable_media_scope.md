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

<<DOC_CONTROL>>

> The upstream — which media classes are in scope, applicable use cases, exclusions

## What this template gives you

This template helps you clearly define which types of media are covered by your security program, including what is included, excluded, and the relevant use cases.

## When to use it

Use this document whenever you need to clarify the scope of media classes in your environment, and update it whenever there are changes to your media handling practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to address three required elements and possibly one recommended detail.

## 1. Media classes (USB drives, external HDDs, optical disks, tape, paper-with-PII, mobile devices with data)

<<MUST item:A.7.10:scope_media_classes>>
_Why: 27002:7.10 — relevant media_

<<GUIDANCE>>

<<TEXT>>

## 2. Use cases enumerated (backup transport, courier-of-data, demo loaners, archive)

<<MUST item:A.7.10:scope_use_cases>>
_Why: 27002:7.10 — use_

<<GUIDANCE>>

<<TEXT>>

## 3. Exclusions (cloud storage handled by A.8.10 information deletion; in-band system storage)

<<MUST item:A.7.10:scope_exclusions>>
_Why: 27002:7.10 — applicability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list for re-scoping (new media format, deprecation of media class)

<<SHOULD item:A.7.10:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
