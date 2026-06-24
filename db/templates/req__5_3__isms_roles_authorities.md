---
leaf_id: req:5.3:isms_roles_authorities
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: responsibility_matrix
trigger_type: universal
template_version: 2
must_count: 6
should_count: 1
---

# ISMS Roles, Responsibilities and Authorities Matrix

## What this template gives you

A **one-page table** that tells anyone — auditor, customer, new hire —
who does what in your ISMS, and what decision authority each role
carries. Auditors check this matches the org chart and your A.5.2
operational security roles. A clean matrix closes "who's responsible
for X?" interview questions on the spot.

## When to use it

You're producing the ISMS Roles + Responsibilities matrix required
by **ISO/IEC 27001:2022 Clause 5.3**. This is the *management-system*
view (ISMS governance) — distinct from **A.5.2** which captures
operational security roles. Both exist; this one is one layer up.

## Before you start

- [ ] **4.3 ISMS Scope** defined (you're assigning roles within scope)
- [ ] **5.2 Information Security Policy** approved (this matrix
      implements the responsibility commitments stated there)
- [ ] **Current org chart** — for the cross-link in MUST 7

## Cross-references

- **5.1 Top management commitment** — the matrix names the
  top-management role accountable for the ISMS
- **A.5.2 Operational security roles** — different document, different
  altitude; this matrix flags consistency between the two
- **9.3 Management review** — the matrix is reviewed at every
  management review (named reviewer per A.5.36)

## Estimated effort

**2-3 hours** for v1; **30 min** for refresh after org changes.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Assign the role for ISMS conformance to ISO 27001:2022

<<MUST item:5.3:isms_conformance>>
_Clause 5.3(a) — responsibility for ensuring conformance._

This is the role accountable for: "the ISMS conforms to the standard."
Usually the **ISMS Manager** in mid-size orgs; can be split between
ISMS Manager + ISMS Owner. State which role, who currently holds it,
what authority they have.

**✓ Good**: "ISMS Manager. Currently <<ISMS_MANAGER_NAME>>. Accountable
for: maintaining ISMS-wide alignment with ISO/IEC 27001:2022,
preparing certification audits, owning the SoA and risk treatment
plan. Authority: convene management review, request resources from
budget owners, escalate conformance gaps directly to ISMS Owner."

**✗ Avoid**: Vague "Information Security Team" (un-named — not
auditable).

<<TEXT>>

## 2. Assign the role for reporting ISMS performance to top management

<<MUST item:5.3:performance_reporting>>
_Clause 5.3(b) — performance reporting upward._

The role who **delivers the ISMS performance pack to top management**.
Often the same as MUST 1 (ISMS Manager); can be split when there's a
dedicated ISMS reporting analyst.

**✓ Good**: "ISMS Manager. Frequency: quarterly to the ISMS Steering
Committee, annually to the Board via the CEO. Report content
defined in the ISMS Performance Reporting standard (link)."

**✗ Avoid**: Unclear cadence or recipient.

<<TEXT>>

## 3. Document authorities for each role

<<MUST item:5.3:authorities_assigned>>
_Clause 5.3 — authorities assigned._

Beyond responsibility, name the **decision rights** each role carries:
who can approve risk acceptance? Who can authorise an exception?
Who can suspend an asset from service?

**✓ Good** (table excerpt):

| Decision | Authority |
|---|---|
| Accept residual risk > target | ISMS Owner |
| Approve risk treatment plan | ISMS Manager (proposes) + Risk Owners (ratify) |
| Authorise control exceptions (time-limited) | CISO / DPO if PII |
| Declare an information security incident | Incident Manager on call |
| Approve emergency/break-glass access | Engineering Manager + retroactive DPO review |

**✗ Avoid**: Listing roles without saying what they can *decide*.

<<TEXT>>

## 4. Communicate the matrix across the organisation

<<MUST item:5.3:communicated>>
_Clause 5.3 — communicated within the organisation._

Same expectation as 5.2: communication is a control, not an
artefact-property. State how role-holders + their colleagues know
who carries each responsibility.

**✓ Good**: "Communication: (1) Always available at <intranet link>.
(2) New joiners see the matrix in security induction. (3) When a
role-holder changes, all-staff change-notice issued + matrix updated
the same day (per the change-record sibling leaf)."

<<TEXT>>

## 5. Name the document owner

<<MUST item:5.3:owner>>
_Accountability — every controlled doc needs a named owner._

The **ISMS Manager** owns the matrix as an artefact (keeps it
current). Top management approves it (carries weight). Don't confuse
the two.

**✓ Good**: "Document owner: ISMS Manager
(<<ISMS_MANAGER_NAME>>). Approver: ISMS Owner (<<CEO_NAME>>).
Review cadence: annual + on significant org change."

<<TEXT>>

## 6. Flag consistency with A.5.2 operational security roles

<<MUST item:5.3:a52_consistency>>
_Cross-control coherence._

The Clause 5.3 matrix (management-system altitude) and the A.5.2
operational roles must not contradict each other — same person can't
be both incident-on-call and the appeal authority for that incident,
for example. Call out the cross-link.

**✓ Good**: "Consistency with A.5.2: The operational roles in A.5.2
(Incident Manager, Vulnerability Owner, Asset Owner, etc.) are
assigned per the Roles & Responsibilities standard (link). Each
A.5.2 role names the Clause 5.3 person it reports to. Cross-checked
at every annual review of either artefact."

<<TEXT>>

---

## Recommended additions

### Link each role to a real org-chart position

<<SHOULD item:5.3:org_chart_link>>
_Visibility — auditors and joiners trace ISMS roles to the people on
the org chart._

For each role, add a column or line that names the org-chart position
that currently holds it (e.g. "ISMS Manager = VP Engineering's
report → Information Security Lead"). When a role-holder leaves, this
makes the gap obvious immediately.

<<TEXT>>
