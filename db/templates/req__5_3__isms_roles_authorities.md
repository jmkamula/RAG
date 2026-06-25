---
leaf_id: req:5.3:isms_roles_authorities
control_ref: 5.3
standard_id: ISO27001:2022
evidence_type: responsibility_matrix
trigger_type: universal
template_version: 2
must_count: 6
should_count: 1
table_shape: hybrid
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
- [ ] **Current org chart** — for the cross-link

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

## Decision authority table

This is the **load-bearing** part of the matrix — the per-decision
rows that say who can make each call. Fill one row per decision-type.

<!-- TABLE-COLUMNS leaf:req:5.3:isms_roles_authorities -->
<!-- column: item:5.3:isms_conformance -->
<!-- column: item:5.3:performance_reporting -->
<!-- column: item:5.3:authorities_assigned -->
<!-- /TABLE-COLUMNS -->

<!-- EDIT-ZONE-START leaf:req:5.3:isms_roles_authorities -->
| ISMS Conformance Role | Performance Reporting Role | Decision Authorities (decision → authority) |
|---|---|---|
|                        |                            |                                              |
|                        |                            |                                              |
|                        |                            |                                              |
<!-- EDIT-ZONE-END leaf:req:5.3:isms_roles_authorities -->

## Column guidance — what to fill in

### ISMS Conformance Role

<<MUST item:5.3:isms_conformance>>

> _Standard text:_ Role assigned for ensuring the ISMS conforms to
> ISO 27001:2022 (Clause 5.3a)

The role accountable for: "the ISMS conforms to the standard."
Usually the **ISMS Manager** in mid-size orgs; can be split between
ISMS Manager + ISMS Owner.

**✓ Good**: `ISMS Manager (<<ISMS_MANAGER_NAME>>). Accountable for:
maintaining ISMS-wide alignment with ISO/IEC 27001:2022, preparing
certification audits, owning the SoA and risk treatment plan.
Authority: convene management review, request resources from budget
owners, escalate conformance gaps directly to ISMS Owner.`

**✗ Avoid**: "Information Security Team" — un-named, not auditable.

### Performance Reporting Role

<<MUST item:5.3:performance_reporting>>

> _Standard text:_ Role assigned for reporting on ISMS performance
> to top management (Clause 5.3b)

Who **delivers the ISMS performance pack to top management**. Often
the same as Conformance Role; can be split when there's a dedicated
ISMS reporting analyst.

**✓ Good**: `ISMS Manager. Frequency: quarterly to ISMS Steering
Committee, annually to the Board via the CEO. Report content per
the ISMS Performance Reporting standard (link).`

**✗ Avoid**: Unclear cadence or recipient.

### Decision Authorities

<<MUST item:5.3:authorities_assigned>>

> _Standard text:_ Authorities assigned for each role (decision
> rights, sign-off authority)

For each decision-type, the named authority. Drives provisioning,
incident response, risk acceptance.

**Example rows** (fill out with your own):

```
Accept residual risk > target              → ISMS Owner
Approve risk treatment plan                → ISMS Manager + Risk Owners
Authorise control exceptions (time-bound)  → CISO / DPO if PII
Declare an InfoSec incident                → Incident Manager on call
Approve emergency/break-glass access       → Eng Manager + retro DPO review
```

**✗ Avoid**: Listing roles without saying what they can *decide*.

---

## Document-level fields

These are the **single-value** MUSTs — they don't belong in the
decision-authority table above. Fill the narrative below.

### Communication

<<MUST item:5.3:communicated>>

> _Standard text:_ Roles communicated within the organization
> (Clause 5.3 — communicated)

How role-holders + their colleagues know who carries each
responsibility. Communication is a control, not an
artefact-property.

<!-- EDIT-ZONE-START item:5.3:communicated -->
<<TEXT>>
<!-- EDIT-ZONE-END item:5.3:communicated -->

### Owner

<<MUST item:5.3:owner>>

> _Standard text:_ Named owner of the matrix (typically ISMS Manager)

The **ISMS Manager** owns the matrix as an artefact (keeps it
current). Top management approves it (carries weight).

<!-- EDIT-ZONE-START item:5.3:owner -->
<<TEXT>>
<!-- EDIT-ZONE-END item:5.3:owner -->

### Consistency with A.5.2

<<MUST item:5.3:a52_consistency>>

> _Standard text:_ Consistency with A.5.2 operational security
> roles flagged inline (cross-control coherence)

The Clause 5.3 matrix (management-system altitude) and the A.5.2
operational roles must not contradict each other. Call out the
cross-link explicitly.

<!-- EDIT-ZONE-START item:5.3:a52_consistency -->
<<TEXT>>
<!-- EDIT-ZONE-END item:5.3:a52_consistency -->

---

## Recommended additional context

### Org-chart linkage

<<SHOULD item:5.3:org_chart_link>>

> _Standard text:_ Integration with the organizational chart (link
> from each role to a real org-chart position)

For each role, add a column or line that names the org-chart position
that currently holds it.
