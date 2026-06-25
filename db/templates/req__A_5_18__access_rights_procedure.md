---
leaf_id: req:A.5.18:access_rights_procedure
control_ref: A.5.18
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 3
must_count: 8
should_count: 3
---

# Access Rights Procedure

## What this template gives you

The **operational runbook** for provisioning, modifying, and
revoking access. A.5.15 is the policy (the rules); this is the
procedure (how the rules are operated day-to-day). It's
joiner-mover-leaver + privileged access + service accounts. The
auditor traces sample tickets through this procedure end-to-end —
each step needs evidence (approver name, date, system change record,
acknowledgement).

## When to use it

You're producing the Access Rights Procedure required by **ISO/IEC
27001:2022 A.5.18**. Operates the A.5.15 policy.

## Before you start

- [ ] **A.5.15 Access Control Policy** approved — this procedure
      implements its rules
- [ ] **A.5.16 Identity Management Procedure** in place — every
      access right binds to a managed identity
- [ ] **A.5.2 Operational Roles** + **5.3 RACI** — authoriser
      identities resolve to named roles
- [ ] **A.5.3 Segregation Matrix** — provisioning honours flagged
      combinations
- [ ] **A.8.2 Privileged Access** procedure — privileged route
      handed off here

## Cross-references

- **A.5.15 policy** (the rules)
- **A.5.16 Identity Management** (the actor side)
- **A.5.17 Authentication Information** (the credentials side)
- **A.5.11 Return of Assets** (revocation flow)
- **A.8.2 Privileged Access** (PAM subset)
- **A.6.1 Screening** (joiner prerequisite)
- **A.6.4 Disciplinary** (escalation when access violated)

## Estimated effort

**4-6 hours** for v1; **1 hour** for refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Require asset-owner authorisation before granting access

<<MUST item:A.5.18:asset_owner_authorization>>

> _Standard text:_ Asset owner authorization required before access is granted (named authoriser per asset class, not generic 'IT manager')

_Authorisation point — the named authoriser per asset class is the
gating decision, not a generic "IT manager"._

State the authorisation rule per asset class (typically from the
A.5.15 policy table), how the request reaches the authoriser, what
the authoriser sees, and how their decision is recorded.

**✓ Good**: "Provisioning request flow: (1) Requester submits via
the access portal selecting target role + business justification.
(2) Portal routes to the authoriser per A.5.15 class — manager
auto-CC'd. (3) Authoriser sees: requester identity, current
roles, requested role, A.5.3 segregation conflicts flagged
inline, business justification. (4) Approve/deny decision
recorded with timestamp + identity; denial requires reason.
(5) Approved request → provisioning system applies the role +
notifies requester within SLA per MUST 6."

**✗ Avoid**: "Provisioning by IT" (generic owner — auditor will
ask who exactly approved this and you can't say)."

<<TEXT>>

## 2. Apply least privilege + segregation checks

<<MUST item:A.5.18:least_privilege>>

> _Standard text:_ Provisioning applies least privilege and segregation-of-duties checks (cross-link to A.5.3 segregation of duties — flagged combinations are blocked or compensated)

_Procedural enforcement of A.5.15 principles — the procedure must
block obvious violations + flag less obvious ones._

State HOW least privilege is applied (role-based bundles, not
ad-hoc grants) and HOW segregation conflicts are detected.

**✓ Good**: "Least-privilege enforcement: (a) Provisioning only via
defined role bundles in Okta — no ad-hoc permission grants.
(b) Bundle changes require A.5.15 review + ISMS Manager sign-off.
(c) Segregation conflicts (cross-checked against A.5.3 matrix) are
flagged inline at request time; provisioning blocks if conflict is
in the 'never combine' set; warns + requires explicit override
sign-off if in the 'flag for review' set; passes if not in the
matrix."

<<TEXT>>

## 3. Reference the A.5.15 policy

<<MUST item:A.5.18:policy_reference>>

> _Standard text:_ References the topic-specific access control policy (A.5.15) — drives consistency between policy and operational practice

_Consistency — procedure should explicitly cite the policy it
implements._

Cross-link to the A.5.15 policy and state which sections of it this
procedure operationalises.

**✓ Good**: "This procedure operationalises the rules stated in the
A.5.15 Access Control Policy (DOC-AC v3.2). Specifically: the
authoriser table (Section 6 of A.5.15) drives MUST 1 above; the
RBAC default (Section 3 of A.5.15) drives MUST 2; the segregation
linkage (Section 7 of A.5.15) drives the conflict-check in MUST 2."

<<TEXT>>

## 4. Define modification path (joiner-mover-leaver)

<<MUST item:A.5.18:modification_path>>

> _Standard text:_ Path for modification of access on role or responsibility change (joiner-mover-leaver flows; mover is the typically-missed leg)

_Lifecycle flows — the MOVER leg is the most-missed; spell it out._

Three lifecycles + the trigger for each. Mover is missed most often
(role change without access change) — auditors hunt for this.

**✓ Good** (table):

| Lifecycle | Trigger | Steps |
|---|---|---|
| Joiner | HR offer accepted → ID issued | Identity created (A.5.16) → role bundles assigned per documented role-fit → manager approves → access live within SLA |
| Mover (role change) | HRIS role-change event | Old role bundles revoked → new role bundles requested + approved → segregation re-checked → access reconfigured within SLA — **mover trigger fires within 5 business days of the role-change event** |
| Leaver | HR last-day notification | Access frozen at COB on last day → all roles + identities revoked within 24h SLA → manager attestation of completion → A.5.11 return of assets follows |

<<TEXT>>

## 5. Route privileged access through A.8.2

<<MUST item:A.5.18:privileged_route>>

> _Standard text:_ Privileged access requests route through the A.8.2 privileged-access process (separate intake, separate approval, separate logging)

_Privileged access is a separate lane — separate intake, separate
approval, separate logging._

State the handoff: privileged-access requests don't go through this
procedure; they go through the A.8.2 PAM process and come back here
only for the identity record.

**✓ Good**: "Privileged access (admin, root, production-write,
identity-admin, security-admin, finance-admin) is handled by the
A.8.2 Privileged Access Management procedure (DOC-PAM). This
procedure (A.5.18) handles the standard-role lane only. A request
flagged 'privileged' at intake is routed to PAM; once approved
there, the resulting identity + role assignment is recorded in
the A.5.16 identity register; this procedure does NOT independently
approve privileged requests."

<<TEXT>>

## 6. State SLA targets per operation

<<MUST item:A.5.18:sla_targets>>

> _Standard text:_ SLA targets stated per operation (grant within X days, modification within Y days, revocation within Z hours of trigger — drives the rev_sla_met flag on revocation_record)

_Time targets — turn "we revoke access promptly" into "we revoke
within 24h of the last-day event"._

The SLA targets drive the rev_sla_met flag on revocation records.
Auditor compares sampled revocations against SLA to assess
discipline.

**✓ Good**: "SLA targets: (a) New-joiner grant: within 1 business
day of identity creation. (b) Mover modification: within 5 business
days of role-change event. (c) Leaver revocation: within 24 hours
of role termination (last day COB + 24h max). (d) Privileged
request: within 1 business day of A.8.2 approval. SLA performance
reported at quarterly ISMS Steering Committee."

<<TEXT>>

## 7. Handle service accounts / non-human identities

<<MUST item:A.5.18:service_account_handling>>

> _Standard text:_ Service account / non-human identity handling stated (provisioning, owner attribution, periodic re-attestation — service accounts are the weakest spot in most access programs)

_Service accounts are typically the weakest lane — they get
provisioned at integration time + forgotten._

State: provisioning, owner attribution, periodic re-attestation,
rotation.

**✓ Good**: "Service accounts (CI service principals, app-to-app
API keys, scheduled-job identities) are managed under this
procedure with specific overlays: (a) Each service account has a
named HUMAN owner (system owner or platform team lead — never
"the service"). (b) Provisioning requires explicit A.5.16
identity-management procedure entry + scope-of-use documentation.
(c) Re-attestation every 90 days: owner confirms the account is
still needed + scope unchanged. (d) Credentials rotated per
A.5.17 (key rotation policy)."

<<TEXT>>

## 8. Link every access right to a registered identity

<<MUST item:A.5.18:identity_link>>

> _Standard text:_ Explicit linkage to A.5.16 identity management (every access right attaches to a registered identity; no orphan access)

_No orphan access — every grant binds to an A.5.16 identity record._

State the policy + the enforcement mechanism.

**✓ Good**: "Every access right granted by this procedure binds to
a registered identity in the A.5.16 identity register. Provisioning
system rejects requests targeting unregistered identities. Quarterly
reconciliation: identities in access systems vs identity register;
discrepancies trigger A.5.18 program review."

<<TEXT>>

---

## Recommended additions

### Temporary / time-bound access

<<SHOULD item:A.5.18:temporary_access>>

> _Standard text:_ Temporary access provisions for time-bound tasks or third parties (expiry date mandatory; automated revocation at expiry)

_Auto-expiry mechanism for short-term needs (contractor stints,
incident-response elevation, etc.)._

State the temporary-access mechanism: max duration, auto-expiry,
extension procedure if longer needed.

<<TEXT>>

### Approval-record retention

<<SHOULD item:A.5.18:approval_retention>>

> _Standard text:_ Retention period for approval evidence stated (drives the audit trail for who-approved-what-when)

_The approval-decision record is the audit artefact — retain it
for the documented period._

Per A.5.33 records retention.

<<TEXT>>

### Emergency / break-glass

<<SHOULD item:A.5.18:emergency_access>>

> _Standard text:_ Emergency-access ('break-glass') procedure stated separately (pre-approved accounts with mandatory post-use justification + audit)

_Pairs with A.5.15's emergency provision — the procedure side._

State break-glass mechanism + post-hoc review.

<<TEXT>>
