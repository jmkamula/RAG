---
leaf_id: req:A.5.18:access_revocation_record
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
table_shape: true
---

# Access Revocation Records

<<DOC_CONTROL>>

> A.5.18 requires that access be removed on change of role, termination, or contract end. Revocation records evidence that those removals actually happened (not just were ordered) — one record per revocation event, traceable back to the register and to the originating trigger. SLA-met flag is auditor-critical — proves not just THAT access was revoked but that the revocation timestamp was within the stated SLA (the famous 'within 24h of role-change' timeliness promise). Identity-pair check enforces bidirectional A.5.16 ↔ A.5.18 lifecycle pairing — closes 'identity disabled but access lingers' gap

<!-- TABLE-COLUMNS leaf:req:A.5.18:access_revocation_record -->
<!-- column: item:A.5.18:rev_trigger -->
<!-- column: item:A.5.18:rev_date_recorded -->
<!-- column: item:A.5.18:rev_disabled_proof -->
<!-- column: item:A.5.18:rev_authoriser -->
<!-- column: item:A.5.18:rev_sla_met -->
<!-- column: item:A.5.18:rev_identity_pair -->
<!-- column: item:A.5.18:rev_residual_cleanup -->
<!-- column: item:A.5.18:rev_completeness -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document every instance where someone's access is removed, showing exactly when and how access was revoked. It also proves that revocations happened on time and are traceable to the original trigger event.

## When to use it

Use this template whenever someone’s role changes, their contract ends, or they leave your organization. Update it each time access is revoked to keep your records current and compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours setting up the first record, with each additional revocation event taking 10-15 minutes to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.18:access_revocation_record -->
| Rev Trigger | Rev Date Recorded | Rev Disabled Proof | Rev Authoriser | Rev Sla Met | Rev Identity Pair | Rev Residual Cleanup | Rev Completeness |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.18:access_revocation_record -->

## Column guidance — what to fill in

### Rev Trigger

<<MUST item:A.5.18:rev_trigger>>
_Why: 27002:5.18d, g — trigger taxonomy_

> _Standard text:_ Revocation trigger captured (termination / role change / contract end / explicit revoke / incident-driven / temporary-expiry / orphan-cleanup)

<<GUIDANCE>>

### Rev Date Recorded

<<MUST item:A.5.18:rev_date_recorded>>
_Why: Timeliness anchor_

> _Standard text:_ Effective date per record (last working day OR contract expiry OR role-change effective date OR explicit revocation decision time)

<<GUIDANCE>>

### Rev Disabled Proof

<<MUST item:A.5.18:rev_disabled_proof>>
_Why: 27002:5.18d — actually removed_

> _Standard text:_ Evidence access was actually disabled (system log entry, RBAC change attestation, confirmation from each affected system) — not just 'we asked'

<<GUIDANCE>>

### Rev Authoriser

<<MUST item:A.5.18:rev_authoriser>>
_Why: 27002:5.18d_

> _Standard text:_ Authoriser of the revocation (named individual; for terminations the dual-signoff pattern of IT + HR/manager applies)

<<GUIDANCE>>

### Rev Sla Met

<<MUST item:A.5.18:rev_sla_met>>
_Why: 27002:5.18d — auditor-critical SLA proof (matches A.5.16:rev_sla_met)_

> _Standard text:_ SLA-met flag per record (yes / no_with_reason) — gap between effective and actual revocation timestamp must be within the procedure's stated SLA, or exception logged; auditor-critical proof of 'within 24h of role change' timeliness

<<GUIDANCE>>

### Rev Identity Pair

<<MUST item:A.5.18:rev_identity_pair>>
_Why: A.5.16 + A.5.17 family coherence_

> _Standard text:_ Identity-pair check per record — confirms A.5.16 identity revocation_record exists for the same identity (where the trigger is termination/contract-end) OR identity remains active (where trigger is role-change/explicit-revoke); closes the bidirectional lifecycle loop

<<GUIDANCE>>

### Rev Residual Cleanup

<<MUST item:A.5.18:rev_residual_cleanup>>
_Why: 27002:5.18 — full lifecycle closure_

> _Standard text:_ Residual cleanup status per record (shared mailbox memberships removed or transferred, file-share access reassigned, distribution-list memberships cleared, OAuth tokens revoked, API keys rotated) — full lifecycle closure, not just primary RBAC revocation

<<GUIDANCE>>

### Rev Completeness

<<MUST item:A.5.18:rev_completeness>>
_Why: 27002:5.18 — completeness_

> _Standard text:_ Completeness check per record — all access rights for the subject (from the register) accounted for (each row statused 'revoked' with its own evidence), not just the primary identity rights

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Hr Link

<<SHOULD item:A.5.18:rev_hr_link>>
_Why: A.6.5 linkage_

> _Standard text:_ Tied to HR off-boarding workflow (A.6.5 linkage) — termination trigger fires from HR system, not from manual IT request

<<GUIDANCE>>

### Rev Timeliness

<<SHOULD item:A.5.18:rev_timeliness>>
_Why: 27002:5.18d — timeliness per trigger_

> _Standard text:_ Timeliness target stated explicitly per trigger type (24h for termination, 5 days for role-change, immediate for incident-driven)

<<GUIDANCE>>

### Rev Post Disable Audit

<<SHOULD item:A.5.18:rev_post_disable_audit>>
_Why: Continual assurance_

> _Standard text:_ Post-disable verification window noted (30-day check that no stale access reappears via service-account chains or forgotten group memberships)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
