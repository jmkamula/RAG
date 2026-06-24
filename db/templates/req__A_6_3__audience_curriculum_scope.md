---
leaf_id: req:A.6.3:audience_curriculum_scope
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Audience and Curriculum Scope

> The upstream that drives the programme. Documents the role-to-curriculum mapping: which audience segments need which training modules. Drives both the curriculum catalogue and the completion-register expected-modules computation

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Audience segments enumerated (all-staff baseline, role-specific tiers — developers, admins, finance, HR, executives, contractors, board)

<<MUST item:A.6.3:scope_audience_segments>>
_Why: 27002:6.3 — relevant audiences_

<<TEXT>>

## 2. Module catalogue stated (every training module the org delivers — baseline awareness, role-specific deep dives, special topics — DPbD, secure coding, fraud, PII handling)

<<MUST item:A.6.3:scope_module_catalogue>>
_Why: 27002:6.3 — curriculum_

<<TEXT>>

## 3. Role-to-module matrix (which audience segment receives which modules — drives the completion-register expected-set)

<<MUST item:A.6.3:scope_role_module_matrix>>
_Why: 27002:6.3 — relevant for job function_

<<TEXT>>

## 4. Special-topic modules tied to specific compliance regimes (GDPR for PII handlers, PCI for payment-card handlers, HIPAA for healthcare)

<<MUST item:A.6.3:scope_special_topics>>
_Why: 27002:6.3 + sectoral_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Third-party audience handling (where contractors/visitors with access need awareness — typically a lighter onboarding briefing rather than full curriculum)

<<SHOULD item:A.6.3:scope_third_party_audiences>>
_Why: 27002:6.3 — interested parties_

<<TEXT>>

### 2. Trigger list for re-scoping (new role/function, new compliance regime, new technology adoption requiring training)

<<SHOULD item:A.6.3:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
