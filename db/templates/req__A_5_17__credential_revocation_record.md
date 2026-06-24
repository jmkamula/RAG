---
leaf_id: req:A.5.17:credential_revocation_record
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Per-Credential Revocation / Reissue Record

> A.5.17 expects every credential revocation to be evidenced — credentials issued and never retired are the basis of every credential-stuffing risk that materialises years later. The revocation record evidences each disable/reissue event: credential ref, trigger type, effective time, actual revocation timestamp, replacement issued (if applicable), residual-access-cleanup. One record per credential event, paired with the corresponding A.5.16 identity revocation record where the trigger is identity-level. Independent records fire for credential-only events (rotation, lost-token reissue, factor downgrade)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Credential identifier per record (links to credential register entry; specific instance, not just type)

<<MUST item:A.5.17:rev_credential_ref>>
_Why: 27002:5.17 — traceability_

<<TEXT>>

## 2. Trigger type per record (identity_termination / rotation_due / compromise_detected / lost_token / factor_change / decommission)

<<MUST item:A.5.17:rev_trigger_type>>
_Why: 27002:5.17 — trigger taxonomy_

<<TEXT>>

## 3. Effective time per record (when the revocation needed to take effect — immediate for compromise, end-of-day for rotation)

<<MUST item:A.5.17:rev_effective_time>>
_Why: Timeliness anchor_

<<TEXT>>

## 4. Actual revocation timestamp per record (drives the SLA-met calculation analogous to A.5.16; compromise revocations have tighter SLA)

<<MUST item:A.5.17:rev_actual_timestamp>>
_Why: 27002:5.17 — timeliness_

<<TEXT>>

## 5. Replacement-issued status per record where applicable (rotation replaces credential; compromise may force forced re-enrolment, not just rotation)

<<MUST item:A.5.17:rev_replacement>>
_Why: 27002:5.17 — continuity_

<<TEXT>>

## 6. Residual-access check per record (sessions invalidated, refresh tokens revoked, cached credentials purged — not just the credential record disabled)

<<MUST item:A.5.17:rev_residual_check>>
_Why: 27002:5.17 — full revocation_

<<TEXT>>

## 7. Cross-reference to paired A.5.16 identity revocation record where this credential revocation was identity-triggered (closes the loop)

<<MUST item:A.5.17:rev_identity_pair>>
_Why: 27002:5.17 + cross-link to [[A.5.16]]_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Scope-expansion check per compromise record (if a credential was compromised, what else might the actor have accessed? — surfaces lateral-movement concerns to A.5.25/A.5.26)

<<SHOULD item:A.5.17:rev_scope_expansion>>
_Why: Closing loop with [[A.5.25]] / [[A.5.26]]_

<<TEXT>>

### 2. Post-revocation verification window noted (e.g. 7-day check that no stale auth attempts using the revoked credential succeed)

<<SHOULD item:A.5.17:rev_post_revoke_audit>>
_Why: Continual assurance_

<<TEXT>>
