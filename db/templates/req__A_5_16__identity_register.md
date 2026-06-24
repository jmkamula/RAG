---
leaf_id: req:A.5.16:identity_register
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# Identity Register

> A.5.16 requires every identity to be visible to the security function — invisible identities are the ones that go stale, get reused, or persist past their owner's departure. The register catalogues every active identity (human + service + shared + non-human): identity id, type, owner, status, created/modified/last-used timestamps. It is the operational record that proves identity hygiene is org-wide, not just on the systems IT remembered to onboard to the IAM platform

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each active identity captured with a unique identifier (employee id, contractor id, service-account id, shared-account id)

<<MUST item:A.5.16:reg_identity_id>>
_Why: 27002:5.16 — visibility_

<<TEXT>>

## 2. Identity type per row (human_employee / human_contractor / service / shared / system_account) — drives policy variant applied

<<MUST item:A.5.16:reg_identity_type>>
_Why: 27002:5.16 — managed (all types)_

<<TEXT>>

## 3. Named owner per row (human owner accountable for THIS identity — even for service accounts, must be a human)

<<MUST item:A.5.16:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 4. Status per row (active / suspended / disabled / pending_termination) updated as lifecycle events fire

<<MUST item:A.5.16:reg_status>>
_Why: 27002:5.16 — lifecycle tracking_

<<TEXT>>

## 5. Created and last-modified timestamps per row

<<MUST item:A.5.16:reg_created_modified>>
_Why: Audit trail_

<<TEXT>>

## 6. Last-used timestamp per row (drives auto-suspend at N days idle; orphan detection)

<<MUST item:A.5.16:reg_last_used>>
_Why: 27002:5.16 — drift detection_

<<TEXT>>

## 7. HR-record link per row for human identities (joiner/leaver triggers cascade automatically — no manual sync)

<<MUST item:A.5.16:reg_hr_link>>
_Why: 27002:5.16 + cross-link to [[A.5.11]]_

<<TEXT>>

## 8. Expiry date per row for service / shared / temporary identities (forces deliberate renewal rather than indefinite drift)

<<MUST item:A.5.16:reg_service_expiry>>
_Why: 27002:5.16 — managed (service-account discipline)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next attestation date per row (drives the periodic recertification cycle)

<<SHOULD item:A.5.16:reg_attestation_due>>
_Why: Drift prevention_

<<TEXT>>

### 2. Risk tag per row where the identity has elevated privileges or sensitive scope (drives faster-cadence review)

<<SHOULD item:A.5.16:reg_risk_tag>>
_Why: Risk-based attention_

<<TEXT>>
