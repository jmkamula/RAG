---
leaf_id: req:5.2:information_security_policy
control_ref: 5.2
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 3
must_count: 7
should_count: 2
---

# Information Security Policy

<<DOC_CONTROL>>

## What this template gives you

The **top-of-stack policy** for your entire ISMS. It's the document
every employee should be able to find within 10 seconds, and the one
top management formally signs. Auditors check that it (a) exists,
(b) has top-management approval, (c) is actually communicated, and
(d) sets meaningful expectations — not boilerplate.

## When to use it

You're producing the **top-level Information Security Policy** required by **ISO/IEC 27001:2022 Clause 5.2**. Distinct from A.5.1 (the
*policy framework / supporting policies*) — Clause 5.2 is the single
overarching statement.

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**3-5 hours** for v1 (drafting + top-management socialisation + approval); **30 min** for annual refresh.

---

## 1. State how the policy fits the organisation's purpose

<<MUST item:5.2:purpose>>

> _Standard text:_ Appropriate to the purpose of the organisation

_Clause 5.2(a) — appropriate to the purpose of the organisation._

Connect the policy to **what your business does** and **why information security matters for that mission**. Generic statements
fail auditors because they could be lifted onto any company's letter.

**✓ Good**: "<<TENANT_NAME>> provides <<PRODUCT_OR_SERVICE>> to
enterprise customers in <<INDUSTRY>>. Our customers entrust us with
their operational data, personal data of their end-users, and
confidential business information. The integrity, confidentiality,
and availability of this data is foundational to our business. This
policy establishes how we discharge that trust."

**✗ Avoid**: "We are committed to information security." (Means
nothing — every org "is committed.")

<<GUIDANCE>>

<<TEXT>>

## 2. Set security objectives (or the framework for setting them)

<<MUST item:5.2:objectives>>

> _Standard text:_ Information security objectives or framework for setting them

_Clause 5.2(b) — provides framework for setting objectives._

State either current security objectives (concrete, measurable) or
the framework by which they are set. Objectives should be
demonstrably tied to risk and to the business goals from MUST 1.

**✓ Good**: "Security objectives are set annually by top management,
reviewed quarterly at the ISMS steering committee, and measured
against the metrics in the ISMS Performance Dashboard. Current
objectives: (1) Maintain ISO 27001 certification with zero major
nonconformities. (2) >99.9% platform availability. (3) <72h MTTR for
critical vulnerabilities. (4) Zero confirmed unauthorised data
disclosures."

**✗ Avoid**: Aspirational language with no measure ("strive to
protect", "best-in-class security").

<<GUIDANCE>>

<<TEXT>>

## 3. Commit to satisfying applicable requirements

<<MUST item:5.2:commitment_req>>

> _Standard text:_ Commitment to satisfy applicable requirements

_Clause 5.2(c) — commitment to applicable requirements._

Acknowledge the regulatory, contractual, and standards obligations
you operate under. Reference the **A.5.31 Compliance Register** —
commit to the discipline; don't enumerate every law here.

**✓ Good**: "<<TENANT_NAME>> is committed to satisfying all applicable
legal, statutory, regulatory and contractual requirements relating to
information security and personal-data protection. The register of
applicable requirements is maintained per Annex A.5.31 and reviewed
annually. Significant obligations include: UK GDPR / EU GDPR
2016/679, Data Protection Act 2018, and customer-specific obligations
captured in Data Processing Agreements."

**✗ Avoid**: Listing every law (the register does that; the policy
commits to the discipline).

<<GUIDANCE>>

<<TEXT>>

## 4. Commit to continual improvement

<<MUST item:5.2:commitment_imp>>

> _Standard text:_ Commitment to continual improvement of the ISMS

_Clause 5.2(d) — commitment to continual improvement._

The Clause 10.1 hook in the policy. Phrase as behaviour, not slogan
— what mechanisms drive improvement?

**✓ Good**: "We commit to continual improvement through: (a) Annex
A.5.27 lessons-learned after every incident, (b) the Clause 10.1
corrective-action register tracking findings from audits and reviews
to closure, (c) annual management review per Clause 9.3 that
triggers explicit improvement actions, (d) risk-driven control
refresh as the threat landscape evolves."

**✗ Avoid**: "We continuously improve" (passive marketing language).

<<GUIDANCE>>

<<TEXT>>

## 5. Document top-management approval

<<MUST item:5.2:approved>>

> _Standard text:_ Approved by top management

_Top-management commitment — the signature is the audit evidence._

Signed approval by a named member of top management (CEO, CISO, or
equivalent role with authority to allocate ISMS resources). Without
the signature, the policy is a draft.

**✓ Good**: "Approved by: <<CEO_NAME>>, Chief Executive Officer, on
<<APPROVAL_DATE>>. Next approval required: on significant change or
no later than <<APPROVAL_DATE_PLUS_1_YEAR>>."

**✗ Avoid**: "Approved by Management" (un-named — not auditable).

<<GUIDANCE>>

<<TEXT>>

## 6. Communicate the policy across the organisation

<<MUST item:5.2:communicated>>

> _Standard text:_ Communicated within the organisation

_Clause 5.2(f) — communication is part of the control._

The policy isn't communicated by existing — a deliberate mechanism
must be in place. Common patterns: new-joiner induction packs +
annual refresh through training (A.6.3) + always-on availability
(intranet / SharePoint).

**✓ Good**: "Communication: (1) Mandatory section of new-joiner
induction, acknowledged via HR onboarding workflow. (2) Annual
re-acknowledgement in the security awareness module per A.6.3.
(3) Always available at <intranet location>. (4) Sent to contractors
at engagement start and acknowledged in the contractor agreement per
A.6.6."

**✗ Avoid**: "Published on the intranet" (publishing isn't
communication — evidence that people received it is required).

<<GUIDANCE>>

<<TEXT>>

## 7. Name the document owner

<<MUST item:5.2:owner>>

> _Standard text:_ Named owner of the policy (ISMS Manager)

_Accountability — every controlled doc needs a named owner._

The **ISMS Manager** (or equivalent) owns the artefact. Top
management approves but doesn't operate day-to-day.

**✓ Good**: "Document owner: ISMS Manager (<<ISMS_MANAGER_NAME>>).
Reviewer: Data Protection & Risk Manager. Approver: <<CEO_NAME>>, CEO."

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

### Make the policy available to interested parties

<<SHOULD item:5.2:available>>

> _Standard text:_ Available to interested parties as appropriate

_Clause 5.2(g) — available to interested parties as appropriate._

If customers, regulators, or auditors are likely to request your
InfoSec Policy, state how they get a copy (often the
customer-trust-centre URL or NDA-gated portal).

**Example**: "External availability: Summary available at
<trust-centre-url>; full policy under NDA to customers and prospects
on request via <legal@>; provided to certification body during audit."

<<GUIDANCE>>

<<TEXT>>

### State review frequency

<<SHOULD item:5.2:review_date>>

> _Standard text:_ Review date or frequency stated

_Document-control discipline — required by Clause 7.5._

Note next planned review date + conditions that trigger ad-hoc review
(significant change, major incident, regulatory update).

<<GUIDANCE>>

<<TEXT>>

---

## Revision history

<<REVISION_HISTORY>>
