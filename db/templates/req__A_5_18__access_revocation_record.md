---
leaf_id: req:A.5.18:access_revocation_record
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Access Revocation Records

> A.5.18 requires that access be removed on change of role, termination, or contract end. Revocation records evidence that those removals actually happened (not just were ordered) — one record per revocation event, traceable back to the register and to the originating trigger. SLA-met flag is auditor-critical — proves not just THAT access was revoked but that the revocation timestamp was within the stated SLA (the famous 'within 24h of role-change' timeliness promise). Identity-pair check enforces bidirectional A.5.16 ↔ A.5.18 lifecycle pairing — closes 'identity disabled but access lingers' gap

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Revocation trigger captured (termination / role change / contract end / explicit revoke / incident-driven / temporary-expiry / orphan-cleanup)

<<MUST item:A.5.18:rev_trigger>>
_Why: 27002:5.18d, g — trigger taxonomy_

<<TEXT>>

## 2. Effective date per record (last working day OR contract expiry OR role-change effective date OR explicit revocation decision time)

<<MUST item:A.5.18:rev_date_recorded>>
_Why: Timeliness anchor_

<<TEXT>>

## 3. Evidence access was actually disabled (system log entry, RBAC change attestation, confirmation from each affected system) — not just 'we asked'

<<MUST item:A.5.18:rev_disabled_proof>>
_Why: 27002:5.18d — actually removed_

<<TEXT>>

## 4. Authoriser of the revocation (named individual; for terminations the dual-signoff pattern of IT + HR/manager applies)

<<MUST item:A.5.18:rev_authoriser>>
_Why: 27002:5.18d_

<<TEXT>>

## 5. SLA-met flag per record (yes / no_with_reason) — gap between effective and actual revocation timestamp must be within the procedure's stated SLA, or exception logged; auditor-critical proof of 'within 24h of role change' timeliness

<<MUST item:A.5.18:rev_sla_met>>
_Why: 27002:5.18d — auditor-critical SLA proof (matches A.5.16:rev_sla_met)_

<<TEXT>>

## 6. Identity-pair check per record — confirms A.5.16 identity revocation_record exists for the same identity (where the trigger is termination/contract-end) OR identity remains active (where trigger is role-change/explicit-revoke); closes the bidirectional lifecycle loop

<<MUST item:A.5.18:rev_identity_pair>>
_Why: A.5.16 + A.5.17 family coherence_

<<TEXT>>

## 7. Residual cleanup status per record (shared mailbox memberships removed or transferred, file-share access reassigned, distribution-list memberships cleared, OAuth tokens revoked, API keys rotated) — full lifecycle closure, not just primary RBAC revocation

<<MUST item:A.5.18:rev_residual_cleanup>>
_Why: 27002:5.18 — full lifecycle closure_

<<TEXT>>

## 8. Completeness check per record — all access rights for the subject (from the register) accounted for (each row statused 'revoked' with its own evidence), not just the primary identity rights

<<MUST item:A.5.18:rev_completeness>>
_Why: 27002:5.18 — completeness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Tied to HR off-boarding workflow (A.6.5 linkage) — termination trigger fires from HR system, not from manual IT request

<<SHOULD item:A.5.18:rev_hr_link>>
_Why: A.6.5 linkage_

<<TEXT>>

### 2. Timeliness target stated explicitly per trigger type (24h for termination, 5 days for role-change, immediate for incident-driven)

<<SHOULD item:A.5.18:rev_timeliness>>
_Why: 27002:5.18d — timeliness per trigger_

<<TEXT>>

### 3. Post-disable verification window noted (30-day check that no stale access reappears via service-account chains or forgotten group memberships)

<<SHOULD item:A.5.18:rev_post_disable_audit>>
_Why: Continual assurance_

<<TEXT>>
