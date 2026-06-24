---
leaf_id: req:Art.29:applicable_scope
control_ref: Art.29
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Art.29 Scope

> The upstream — which personnel categories act under controller/processor authority (employees + contractors + embedded vendor staff), distinct from sub-processors (Art.28 territory)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Personnel categories in scope (employees + contractors + embedded third-party staff)

<<MUST item:Art.29:scope_personnel_categories>>
_Why: Art.29 — persons under authority_

<<TEXT>>

## 2. Org-role classification — does the org act as processor for any customer (Art.29 binds the org's own staff in that capacity)?

<<MUST item:Art.29:scope_processor_role>>
_Why: Art.29 — processor + persons_

<<TEXT>>

## 3. Sub-processor boundary — sub-processors are Art.28 territory not Art.29

<<MUST item:Art.29:scope_subprocessor_boundary>>
_Why: Cross-article coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new role processing PII, contractor onboarding)

<<SHOULD item:Art.29:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
