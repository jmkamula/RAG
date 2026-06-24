---
leaf_id: req:A.6.1:applicable_roles_scope
control_ref: A.6.1
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Applicable Roles and Check-Depth Scope

> The upstream that drives the procedure. Documents which role tiers exist, which checks each tier requires, and the legal/regulatory drivers for sectoral check requirements (financial-services PEP + sanctions, healthcare credentialing, government clearance levels)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Role tiers defined (junior office, standard, sensitive [access to special-category PII or financial systems], privileged [admin / production access], executive)

<<MUST item:A.6.1:scope_role_tiers>>
_Why: 27002:6.1a — proportional_

<<TEXT>>

## 2. Check matrix — which check types apply to which role tier (matrix is the spec; rows show consistency)

<<MUST item:A.6.1:scope_check_matrix>>
_Why: 27002:6.1 — proportional checks_

<<TEXT>>

## 3. Jurisdictions covered (where checks happen — local legal constraints apply; some checks unavailable in some jurisdictions)

<<MUST item:A.6.1:scope_jurisdictions>>
_Why: 27002:6.1 — applicable laws per jurisdiction_

<<TEXT>>

## 4. Sectoral drivers stated (PCI for payment-card roles, HIPAA for healthcare, financial-services PEP/sanctions, government clearance)

<<MUST item:A.6.1:scope_sectoral_drivers>>
_Why: 27002:6.1 — applicable laws / sectoral_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.5.31 legal/regulatory register — jurisdictional and sectoral check requirements should be sourced from the single legal-obligations register

<<SHOULD item:A.6.1:scope_a531_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Trigger list for re-scoping (new geography, new sector entry, new regulator action affecting screening)

<<SHOULD item:A.6.1:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
