---
leaf_id: req:A.5.17:credential_revocation_record
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Per-Credential Revocation / Reissue Record

<<DOC_CONTROL>>

> A.5.17 expects every credential revocation to be evidenced — credentials issued and never retired are the basis of every credential-stuffing risk that materialises years later. The revocation record evidences each disable/reissue event: credential ref, trigger type, effective time, actual revocation timestamp, replacement issued (if applicable), residual-access-cleanup. One record per credential event, paired with the corresponding A.5.16 identity revocation record where the trigger is identity-level. Independent records fire for credential-only events (rotation, lost-token reissue, factor downgrade)

<!-- TABLE-COLUMNS leaf:req:A.5.17:credential_revocation_record -->
<!-- column: item:A.5.17:rev_credential_ref -->
<!-- column: item:A.5.17:rev_trigger_type -->
<!-- column: item:A.5.17:rev_effective_time -->
<!-- column: item:A.5.17:rev_actual_timestamp -->
<!-- column: item:A.5.17:rev_replacement -->
<!-- column: item:A.5.17:rev_residual_check -->
<!-- column: item:A.5.17:rev_identity_pair -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of every time a credential is revoked or reissued, making it easier to show compliance and reduce long-term security risks from old or unused credentials.

## When to use it

Use this template whenever you disable, rotate, or reissue a credential, including lost tokens or factor downgrades. Update the register as these events happen to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required field for each event, so completing a single record from scratch will likely take around 1.5 to 2 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.17:credential_revocation_record -->
| Rev Credential Ref | Rev Trigger Type | Rev Effective Time | Rev Actual Timestamp | Rev Replacement | Rev Residual Check | Rev Identity Pair |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.17:credential_revocation_record -->

## Column guidance — what to fill in

### Rev Credential Ref

<<MUST item:A.5.17:rev_credential_ref>>
_Why: 27002:5.17 — traceability_

> _Standard text:_ Credential identifier per record (links to credential register entry; specific instance, not just type)

<<GUIDANCE>>

### Rev Trigger Type

<<MUST item:A.5.17:rev_trigger_type>>
_Why: 27002:5.17 — trigger taxonomy_

> _Standard text:_ Trigger type per record (identity_termination / rotation_due / compromise_detected / lost_token / factor_change / decommission)

<<GUIDANCE>>

### Rev Effective Time

<<MUST item:A.5.17:rev_effective_time>>
_Why: Timeliness anchor_

> _Standard text:_ Effective time per record (when the revocation needed to take effect — immediate for compromise, end-of-day for rotation)

<<GUIDANCE>>

### Rev Actual Timestamp

<<MUST item:A.5.17:rev_actual_timestamp>>
_Why: 27002:5.17 — timeliness_

> _Standard text:_ Actual revocation timestamp per record (drives the SLA-met calculation analogous to A.5.16; compromise revocations have tighter SLA)

<<GUIDANCE>>

### Rev Replacement

<<MUST item:A.5.17:rev_replacement>>
_Why: 27002:5.17 — continuity_

> _Standard text:_ Replacement-issued status per record where applicable (rotation replaces credential; compromise may force forced re-enrolment, not just rotation)

<<GUIDANCE>>

### Rev Residual Check

<<MUST item:A.5.17:rev_residual_check>>
_Why: 27002:5.17 — full revocation_

> _Standard text:_ Residual-access check per record (sessions invalidated, refresh tokens revoked, cached credentials purged — not just the credential record disabled)

<<GUIDANCE>>

### Rev Identity Pair

<<MUST item:A.5.17:rev_identity_pair>>
_Why: 27002:5.17 + cross-link to [[A.5.16]]_

> _Standard text:_ Cross-reference to paired A.5.16 identity revocation record where this credential revocation was identity-triggered (closes the loop)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Scope Expansion

<<SHOULD item:A.5.17:rev_scope_expansion>>
_Why: Closing loop with [[A.5.25]] / [[A.5.26]]_

> _Standard text:_ Scope-expansion check per compromise record (if a credential was compromised, what else might the actor have accessed? — surfaces lateral-movement concerns to A.5.25/A.5.26)

<<GUIDANCE>>

### Rev Post Revoke Audit

<<SHOULD item:A.5.17:rev_post_revoke_audit>>
_Why: Continual assurance_

> _Standard text:_ Post-revocation verification window noted (e.g. 7-day check that no stale auth attempts using the revoked credential succeed)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
