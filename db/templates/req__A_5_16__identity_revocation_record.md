---
leaf_id: req:A.5.16:identity_revocation_record
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Per-Identity Revocation Record

> A.5.16 expects every identity termination to be evidenced — not just procedurally promised. The revocation record evidences each disable/remove event: identity id, trigger type, effective date, actual revocation timestamp, SLA-met flag, dual signoff, residual-cleanup status (mailbox forwarding, file-share access transfer). One record per terminated identity, traceable back to the identity register and to the originating trigger (A.5.11 leaver register, contractor expiry, security event)

<!-- TABLE-COLUMNS leaf:req:A.5.16:identity_revocation_record -->
<!-- column: item:A.5.16:rev_identity_ref -->
<!-- column: item:A.5.16:rev_trigger_type -->
<!-- column: item:A.5.16:rev_effective_date -->
<!-- column: item:A.5.16:rev_actual_timestamp -->
<!-- column: item:A.5.16:rev_sla_met -->
<!-- column: item:A.5.16:rev_dual_signoff -->
<!-- column: item:A.5.16:rev_residual_cleanup -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.16:identity_revocation_record -->
| Rev Identity Ref | Rev Trigger Type | Rev Effective Date | Rev Actual Timestamp | Rev Sla Met | Rev Dual Signoff | Rev Residual Cleanup |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.16:identity_revocation_record -->

## Column guidance — what to fill in

### Rev Identity Ref

<<MUST item:A.5.16:rev_identity_ref>>
_Why: 27002:5.16 — traceability_

> _Standard text:_ Identity identifier per record (links to identity register entry)

### Rev Trigger Type

<<MUST item:A.5.16:rev_trigger_type>>
_Why: 27002:5.16 — trigger taxonomy_

> _Standard text:_ Trigger type per record (termination / contract_end / suspension_to_disable / incident_revocation / orphan_cleanup)

### Rev Effective Date

<<MUST item:A.5.16:rev_effective_date>>
_Why: Timeliness anchor_

> _Standard text:_ Effective date per record (last working day OR contract expiry OR incident decision time)

### Rev Actual Timestamp

<<MUST item:A.5.16:rev_actual_timestamp>>
_Why: 27002:5.16 — timeliness verification_

> _Standard text:_ Actual revocation timestamp per record (drives SLA-met calculation)

### Rev Sla Met

<<MUST item:A.5.16:rev_sla_met>>
_Why: 27002:5.16 — auditor-critical SLA proof_

> _Standard text:_ SLA-met flag per record (yes / no_with_reason — gap between effective and actual must be within stated SLA, or exception logged)

### Rev Dual Signoff

<<MUST item:A.5.16:rev_dual_signoff>>
_Why: Accountability_

> _Standard text:_ Dual signoff per record (IT identity-owner + HR or hiring manager — captures even when in-person handover impossible)

### Rev Residual Cleanup

<<MUST item:A.5.16:rev_residual_cleanup>>
_Why: 27002:5.16 — full lifecycle closure_

> _Standard text:_ Residual-cleanup status per record (mailbox forwarding configured, file-share access transferred or revoked, group memberships cleared)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Post Disable Audit

<<SHOULD item:A.5.16:rev_post_disable_audit>>
_Why: Continual assurance_

> _Standard text:_ Post-disable verification window noted (e.g. 30-day check that no stale access reappears via service-account chains)

### Rev Credential Link

<<SHOULD item:A.5.16:rev_credential_link>>
_Why: Closing loop with [[A.5.17]]_

> _Standard text:_ Cross-reference to A.5.17 credential-revocation record (paired event; both must complete to close the loop)
