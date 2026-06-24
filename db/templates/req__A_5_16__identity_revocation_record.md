---
leaf_id: req:A.5.16:identity_revocation_record
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Per-Identity Revocation Record

> A.5.16 expects every identity termination to be evidenced — not just procedurally promised. The revocation record evidences each disable/remove event: identity id, trigger type, effective date, actual revocation timestamp, SLA-met flag, dual signoff, residual-cleanup status (mailbox forwarding, file-share access transfer). One record per terminated identity, traceable back to the identity register and to the originating trigger (A.5.11 leaver register, contractor expiry, security event)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Identity identifier per record (links to identity register entry)

<<MUST item:A.5.16:rev_identity_ref>>
_Why: 27002:5.16 — traceability_

<<TEXT>>

## 2. Trigger type per record (termination / contract_end / suspension_to_disable / incident_revocation / orphan_cleanup)

<<MUST item:A.5.16:rev_trigger_type>>
_Why: 27002:5.16 — trigger taxonomy_

<<TEXT>>

## 3. Effective date per record (last working day OR contract expiry OR incident decision time)

<<MUST item:A.5.16:rev_effective_date>>
_Why: Timeliness anchor_

<<TEXT>>

## 4. Actual revocation timestamp per record (drives SLA-met calculation)

<<MUST item:A.5.16:rev_actual_timestamp>>
_Why: 27002:5.16 — timeliness verification_

<<TEXT>>

## 5. SLA-met flag per record (yes / no_with_reason — gap between effective and actual must be within stated SLA, or exception logged)

<<MUST item:A.5.16:rev_sla_met>>
_Why: 27002:5.16 — auditor-critical SLA proof_

<<TEXT>>

## 6. Dual signoff per record (IT identity-owner + HR or hiring manager — captures even when in-person handover impossible)

<<MUST item:A.5.16:rev_dual_signoff>>
_Why: Accountability_

<<TEXT>>

## 7. Residual-cleanup status per record (mailbox forwarding configured, file-share access transferred or revoked, group memberships cleared)

<<MUST item:A.5.16:rev_residual_cleanup>>
_Why: 27002:5.16 — full lifecycle closure_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Post-disable verification window noted (e.g. 30-day check that no stale access reappears via service-account chains)

<<SHOULD item:A.5.16:rev_post_disable_audit>>
_Why: Continual assurance_

<<TEXT>>

### 2. Cross-reference to A.5.17 credential-revocation record (paired event; both must complete to close the loop)

<<SHOULD item:A.5.16:rev_credential_link>>
_Why: Closing loop with [[A.5.17]]_

<<TEXT>>
