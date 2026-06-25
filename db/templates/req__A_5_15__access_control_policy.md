---
leaf_id: req:A.5.15:access_control_policy
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 3
must_count: 7
should_count: 3
---

# Access Control Policy

## What this template gives you

The **rules document** that says who gets to access what, why, and
on what basis. A.5.15 is the POLICY; A.5.18 is the PROCEDURE that
implements it (joiner-mover-leaver flows). Auditors check both
exist + are consistent. The policy alone without operational
A.5.16-18 is theatre; the procedure without a clear policy is
ungoverned.

## When to use it

You're producing the Access Control Policy required by **ISO/IEC
27001:2022 A.5.15**. Distinct from A.5.18 access rights procedure
— the policy sets the rules; the procedure operates them.

## Before you start

- [ ] **4.3 ISMS Scope** + **A.5.9 Asset Register** — you can't
      define access rules without knowing what assets exist
- [ ] **A.5.12 Classification Scheme** — access rules vary by class
- [ ] **A.5.2 Roles** + **5.3 RACI** — the policy names the
      authoriser per asset class
- [ ] **A.5.3 Segregation of Duties analysis** — flagged
      combinations referenced in the policy

## Cross-references

- **A.5.16 Identity Management** — identities the rules apply to
- **A.5.17 Authentication Info** — credentials granting access
- **A.5.18 Access Rights Procedure** — operationalises this policy
- **A.5.3 Segregation of Duties** — rules referenced here
- **A.8.2 Privileged Access Management** — privileged-access subset
- **A.8.3-5 Access restrictions** — technical implementations

## Estimated effort

**3-5 hours** for v1; **30 min** for refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. State physical access rules

<<MUST item:A.5.15:physical_rules>>

> _Standard text:_ Physical access rules (premises, server rooms, restricted areas)

_Physical access rules — premises, server rooms, restricted areas._

If you have premises in ISMS scope, define rules for: site entry,
floor zones, server rooms (if any), restricted areas (HR, finance,
incident response war-room), visitor handling. **If cloud-only**:
this MUST is typically marked N/A via tenant_must_overrides; the
overall A.5 family becomes logical-only for you.

**✓ Good (with premises)**: "Physical access rules: (a) Office
entry by employee badge; visitors logged + escorted. (b) Server
room (if applicable) requires badge + role-attestation; access list
reviewed quarterly. (c) Areas processing restricted-class data
require explicit allowlisting; entry logged + reviewed monthly.
(d) Premises access changes follow A.5.18 joiner-mover-leaver flow."

**✓ Good (cloud-only)**: "Not applicable. <<TENANT_NAME>> operates
cloud-only per 4.3 ISMS scope; no premises in scope. Cloud
provider physical security covered by A.5.23 supplier evaluation.
This MUST is marked N/A in the tenant scope overlay."

<<TEXT>>

## 2. State logical access rules

<<MUST item:A.5.15:logical_rules>>

> _Standard text:_ Logical access rules (systems, applications, network segments)

_Logical access rules — systems, applications, network segments._

The core of access control for most orgs. Define rules for:
authentication strength per class, network segmentation, application
authorisation, database/data-store access, administrative actions.

**✓ Good**: "Logical access rules: (a) All production system
access requires SSO via Okta with MFA. (b) Production data access
requires named role assignment + business approval per A.5.18.
(c) Network segmentation: production VPC isolated from corporate;
inter-account access via documented IAM roles only. (d) Database
access uses ephemeral credentials issued by IAM (no shared
credentials). (e) Privileged actions logged + alerted (A.8.15).
(f) Restricted-class data has additional access-time approval
(break-glass workflow)."

<<TEXT>>

## 3. Make RBAC the default access model

<<MUST item:A.5.15:rbac>>

> _Standard text:_ Role-based access control as the default model with stated exceptions (attribute-based, individual grants)

_Default model — RBAC unless explicitly excepted._

State RBAC as the default + the explicit exceptions (when ABAC or
individual grants apply).

**✓ Good**: "RBAC is the default access model. Roles defined per
the A.5.2 operational-roles register; access bundles per role
maintained in Okta. Exceptions: (a) Attribute-based access (ABAC)
for time-bound contract roles where the role boundary depends on
project/contract assignment — documented exception register +
quarterly review. (b) Individual grants for break-glass emergency
access only — auto-expire 24h + post-hoc review per A.8.2."

<<TEXT>>

## 4. State the least-privilege principle

<<MUST item:A.5.15:least_privilege>>

> _Standard text:_ Principle of least privilege stated

_Behavioural principle — give the minimum access needed for the
role to perform its function._

State the principle + how it's enforced. Most orgs default to
over-grant on initial provisioning — the policy must specify the
discipline that prevents this.

**✓ Good**: "Least privilege: Each role's access bundle is the
minimum set of permissions to perform the role's documented
functions. New roles undergo access-design review with the role
owner + security; existing roles re-attested every 90 days for
privileged + annually for standard. Permissions broader than
documented are flagged at attestation + remediated in the next
A.5.18 cycle."

<<TEXT>>

## 5. State the need-to-know principle

<<MUST item:A.5.15:need_to_know>>

> _Standard text:_ Principle of need-to-know stated

_Information-access principle — access to data is on need-to-know,
even within a role's permission scope._

Distinct from least-privilege (about ROLE permissions);
need-to-know is about DATA INSTANCES. Two engineers in the same
role don't access each other's customer support tickets without
business need.

**✓ Good**: "Need-to-know: Access to specific data instances within
a role's permission scope requires demonstrable business need.
Implemented via: (a) ABAC overlays on customer-data systems
(engineers see only the customers they actively support); (b) audit
logging of all data-instance access; (c) periodic data-access
reviews surface unusual patterns to managers."

<<TEXT>>

## 6. Define authorisation rules

<<MUST item:A.5.15:authorisation>>

> _Standard text:_ Authorisation rules — who can authorise access at which level (cross-link to A.5.18 procedure)

_Who can authorise access at which level — cross-link to A.5.18._

State per-class or per-system: who's the authoriser. This is what
A.5.18 provisioning references at decision time.

**✓ Good** (table):

| Asset class | Authoriser | Approval cadence |
|---|---|---|
| Public / Internal systems | Line manager | Per provisioning request |
| Confidential systems | Asset owner + line manager | Per request + annual re-attest |
| Restricted systems | Asset owner + CISO | Per request + quarterly re-attest |
| Privileged production access | Engineering Manager + Asset owner | Per request + 90-day re-attest |
| Privileged identity-admin (Okta admin) | CISO + ISMS Owner | Per request + 90-day re-attest |

<<TEXT>>

## 7. Link to segregation of duties (A.5.3)

<<MUST item:A.5.15:segregation_link>>

> _Standard text:_ Cross-link to A.5.3 segregation of duties — access decisions respect documented separation

_Cross-control coherence — access decisions must respect A.5.3._

State that authorisation decisions respect documented segregation
combinations.

**✓ Good**: "Segregation of duties: Access authorisation respects
the A.5.3 segregation matrix. Flagged combinations (e.g. same
person creates + approves production change; same person provisions
own access; same person is incident-on-call + appeal authority for
that incident) are BLOCKED by the A.5.18 procedure; compensating
controls require explicit ISMS Manager sign-off. The matrix is
reviewed at every role change + annually."

<<TEXT>>

---

## Recommended additions

### Emergency / break-glass access

<<SHOULD item:A.5.15:emergency_access>>

> _Standard text:_ Emergency / break-glass access provisions (with mandatory after-the-fact justification)

_Operational continuity — sometimes "break the rule, fix it after"
is the right answer (e.g. lone-engineer on-call needing prod
access at 3am)._

State break-glass mechanism: short-lived elevated access, mandatory
post-hoc review, full audit trail.

<<TEXT>>

### Third-party / contractor access

<<SHOULD item:A.5.15:third_party>>

> _Standard text:_ Third-party / contractor access rules referenced (link to A.5.19 supplier relationships)

_Coverage — contractors + suppliers operate under same access
rules, with contractual hooks per A.5.19/20._

State how third-party access is provisioned (typically: separate
identity store, time-bound, contract-referenced authorisation).

<<TEXT>>

### Periodic review cadence

<<SHOULD item:A.5.15:review_cadence>>

> _Standard text:_ Periodic access review cadence stated (typically quarterly for privileged, annual otherwise — link to A.5.18)

_Drift prevention — access drifts without cadence._

State review cadence: typically quarterly for privileged, annual
otherwise (matching the A.5.18 procedure).

<<TEXT>>
