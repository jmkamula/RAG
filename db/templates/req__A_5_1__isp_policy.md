---
leaf_id: req:A.5.1:isp_policy
control_ref: A.5.1
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 3
must_count: 5
should_count: 2
---

# Information Security Policy (Annex A.5.1)

## What this template gives you

The **operational policy** that sits one layer below your Clause 5.2
top-level Information Security Policy. A.5.1 is where the *policy
family* gets defined — the topic-specific policies (acceptable use,
classification, access, etc.) that govern day-to-day behaviour.
Where Clause 5.2 is what top management commits to, A.5.1 is what
the policy framework actually contains.

## When to use it

You're producing the Annex A.5.1 Information Security Policy
referenced by every other A.5 topic-specific policy. **Don't confuse
with Clause 5.2** — the two co-exist by design (one is
management-system level, one is operational).

## Before you start

- [ ] **Clause 5.2 InfoSec Policy** approved (this one supports it)
- [ ] **4.3 ISMS Scope** clear
- [ ] **5.3 Roles** defined (this policy names them)
- [ ] **A.5.31 Compliance register** under way

## Cross-references

- **Clause 5.2** — this A.5.1 policy implements + operationalises
  the Clause 5.2 commitments
- **A.5.10 Acceptable Use** — flows from this policy
- **A.5.12 Classification** — flows from this policy
- **A.5.15 Access Control** — flows from this policy
- **A.6 People Controls** — references this policy in
  onboarding/training material

## Estimated effort

**4-6 hours** for v1; **1 hour** for annual refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define the policy scope

<<MUST item:A.5.1:scope>>

> _Standard text:_ Scope of the policy defined (which assets, locations, personnel)

_Scope clarity — which assets, locations, personnel does this
policy apply to?_

State scope in terms of: assets in scope (data + systems +
infrastructure), locations, personnel categories, third-party
relationships subject to the policy.

**✓ Good**: "Scope: This policy applies to (a) all
<<TENANT_NAME>> employees, contractors and consultants; (b) all
information assets in scope of the ISMS per Clause 4.3 — production
SaaS platform, supporting cloud infrastructure, corporate IT systems,
personal data of customers + end-users; (c) all locations covered by
the ISMS scope (<<TENANT_COUNTRY>> offices + AWS regions per 4.3);
(d) all third parties processing in-scope information under
<<TENANT_NAME>> direction, who must accept this policy by reference
in their agreements (per A.5.20)."

<<TEXT>>

## 2. State principles + objectives

<<MUST item:A.5.1:principles>>

> _Standard text:_ Information security principles and objectives stated

_The behavioural backbone — what does <<TENANT_NAME>> commit to in
operating its information security?_

State the principles in 5-7 bullets. These will be quoted in
training (A.6.3), referenced in incident response (A.5.24), and
recited at customer trust reviews.

**✓ Good**: "Principles: (1) Confidentiality, integrity and
availability of information are foundational to the trust our
customers place in us. (2) Security is everyone's responsibility,
with named accountability per the Clause 5.3 matrix and A.5.2
operational roles. (3) Access is granted on the basis of least
privilege and need-to-know, with periodic review. (4) Personal
data is processed only on a lawful basis with the data subject's
rights honoured. (5) Risk is assessed deliberately, treated with
documented controls, and the residual is consciously accepted.
(6) Incidents are reported promptly, investigated systematically,
and feed lessons into continual improvement. (7) Compliance with
applicable law and contracts is non-negotiable."

<<TEXT>>

## 3. Assign roles + responsibilities

<<MUST item:A.5.1:roles>>

> _Standard text:_ Roles and responsibilities for information security

_Operational roles — who DOES the security work day-to-day._

Distinct from the Clause 5.3 ISMS-governance roles. A.5.1 names the
operational roles + their security duties: ISMS Manager, ISMS Owner,
CISO, DPO, Asset Owners, line managers, employees, contractors.

**✓ Good**: "Operational roles: **ISMS Manager**
(<<ISMS_MANAGER_NAME>>) operates the ISMS day-to-day. **ISMS Owner**
(<<CEO_NAME>>) carries top-management accountability. **CISO**
(<<CISO_NAME>>) leads security operations. **DPO**
(<<DPO_NAME>>) leads privacy. **Asset Owners**: business or
product role accountable for an asset's security state. **Line
managers**: enforce policy within their team, complete control
attestations. **Employees + contractors**: complete training,
report incidents, honour access rules. Detailed RACI in Clause 5.3
matrix + A.5.2 operational roles."

<<TEXT>>

## 4. Commit to legal, regulatory, contractual compliance

<<MUST item:A.5.1:legal_compliance>>

> _Standard text:_ Commitment to legal, regulatory and contractual compliance

_Operational expression of the Clause 5.2(c) commitment._

Where Clause 5.2 makes the high-level commitment, A.5.1 names the
mechanism: A.5.31 register, A.5.32 IP, A.5.33/34 records + PII,
A.5.36 compliance reviews.

**✓ Good**: "Compliance commitment: We satisfy applicable legal,
statutory, regulatory and contractual requirements through: (a) the
A.5.31 compliance requirements register maintained by the DPO and
ISMS Manager, reviewed annually + on regulatory change; (b) A.5.33
records retention + A.5.34 PII protection programs; (c) periodic
A.5.36 compliance reviews of each requirement family; (d) explicit
contract clauses cascaded to suppliers per A.5.20."

<<TEXT>>

## 5. List topic-specific policies that flow from this one

<<MUST item:A.5.1:topic_refs>>

> _Standard text:_ References to topic-specific policies that flow from this one (e.g. A.5.10 AUP, A.5.12 classification, A.6.4 disciplinary)

_A.5.1 is the umbrella — name the children._

The topic-specific policies under A.5: the A.5.10 AUP, A.5.12
classification, A.5.15 access control, A.5.19 supplier, A.5.34
privacy, A.6.7 remote working, A.7.6 working areas (if in scope).
This cross-link list lets readers follow the policy framework.

**✓ Good** (table):

| Topic | Policy | Anchor |
|---|---|---|
| Acceptable Use | A.5.10 AUP | DOC-AUP |
| Classification | A.5.12 Classification Policy | DOC-CL |
| Access Control | A.5.15 Access Control Policy | DOC-AC |
| Supplier Security | A.5.19 Supplier Security Policy | DOC-SUP |
| Privacy + PII | A.5.34 Privacy + PII Policy | DOC-PRI |
| Remote Working | A.6.7 Remote Working Policy | DOC-RW |
| Cryptography | A.8.24 Cryptography Policy | DOC-CRY |

**✗ Avoid**: A vague "various topic policies exist" (the auditor
needs the explicit cross-reference list).

<<TEXT>>

---

## Recommended additions

### Version + approval metadata

<<SHOULD item:A.5.1:version>>

> _Standard text:_ Version number and effective date

_Document control._

Standard header block with version, approval date, next review.

<<TEXT>>

### Named owner

<<SHOULD item:A.5.1:owner>>

> _Standard text:_ Policy owner named (typically CISO or equivalent)

_Accountability._

Document owner + approver named explicitly.

<<TEXT>>
