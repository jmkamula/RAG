---
leaf_id: req:4.3:isms_scope
control_ref: 4.3
standard_id: ISO27001:2022
evidence_type: scope_statement
trigger_type: universal
template_version: 2
must_count: 6
should_count: 2
---

# ISMS Scope Statement

## What this template gives you

A one-page Scope Statement defining where your ISMS applies. This is
the **first artefact every auditor looks for** — they read it before
anything else. A weak scope statement makes every other control hard
to audit; a clear one closes most "where does this apply?" questions
upfront.

## When to use it

You're authoring (or refreshing) the Statement of Scope per **ISO/IEC
27001:2022 Clause 4.3**. Either: (a) this is a new ISMS and you're
producing the first version, or (b) you're refreshing because of a
significant change (new product line, new geography, M&A, divestment).

## Before you start

You'll write a stronger scope statement if you've already done these:

- [ ] **Clause 4.1 issues register** — what internal and external issues
      affect your information security objectives. The scope flows from
      these issues.
- [ ] **Clause 4.2 interested parties register** — who has expectations
      of your ISMS and what those expectations are. The interfaces in
      this scope statement should match this list.
- [ ] **A sponsor at top management** — someone whose signature carries
      weight (CEO / CISO / ISMS Owner) and who can sign off on
      exclusions.

## Cross-references

This scope statement feeds and constrains:

- **5.1 / 5.2** — Top management commitment and InfoSec Policy explicitly
  reference "the ISMS scope as defined in section 4.3"
- **6.1.2 / 6.1.3** — Risk assessment is performed **within the scope**;
  the SoA columns include scope-applicability
- **A.5 / A.7 / A.8 controls** — many controls' "applicable" decision
  depends on whether the asset/process is in-scope (e.g. A.7 physical
  controls N/A if you have no premises in scope)
- **9.2 audit** — the audit programme covers everything *in scope*; an
  unclear scope causes audit findings

## Estimated effort

**2-4 hours** to author from scratch with the inputs above; **30 min**
to refresh.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define the ISMS boundary

<<MUST item:4.3:boundaries>>
_ISO/IEC 27001:2022 Clause 4.3(a) — boundaries must be determined._

The boundary is what is **inside** your ISMS. State it in business
terms before you state it in IT terms. Auditors care about
defensibility — does the boundary make organisational sense?

**✓ Good**: "The ISMS covers Arion Networks Ltd's UK and Czech
operations, specifically: (a) the SaaS platform offered to enterprise
customers including all production cloud workloads on AWS eu-west-1,
(b) the corporate IT supporting platform engineering and customer
operations teams, (c) the personal data of users and customer
end-users processed by these systems."

**✗ Avoid**: "All information systems and processes" (too vague to
audit). "Everything except finance" (defines by exclusion only —
state inclusion first).

<<NAME>>

## 2. Document interfaces and dependencies

<<MUST item:4.3:interfaces>>
_ISO/IEC 27001:2022 Clause 4.3(b) — interfaces with other organisations._

This is **where your ISMS meets the outside world** — cloud providers,
managed services, customer data exchanges, contractor relationships.
The auditor will trace these to A.5.19-23 supplier controls.

**✓ Good**: "Interfaces: AWS (IaaS provider, DPA in place, SOC2 reviewed
annually); Okta (identity provider, BAA + processor agreement);
Stripe (payment processor, PCI scope inheritance); HR outsourcer
(personnel data processor); ISO 27001 certification body (audit
relationship)."

**✗ Avoid**: A list of vendor names with no context on what data or
trust flows across each interface.

<<NAME>>

## 3. State exclusions with justification

<<MUST item:4.3:exclusions>>
_ISO/IEC 27001:2022 Clause 4.3(c) — exclusions must be justified._

If you EXCLUDE part of the organisation from the ISMS, you must
justify why and convince the auditor that the exclusion doesn't
undermine the rest. Common defensible exclusions: a divested
subsidiary (regulatory separation), R&D labs running on isolated
networks (no customer data), legacy products in run-out (compensating
contractual controls).

**✓ Good**: "Exclusions: (1) the legacy on-prem platform serving 3
remaining customers under managed-exit until 2027 — these customers
have separate contractual security clauses and dedicated infra
isolated from the ISMS-in-scope cloud platform. Justification:
isolation eliminates information flow into in-scope systems."

**✗ Avoid**: Excluding without justification, or excluding parts of
the organisation that DO process in-scope data (the auditor will
catch this through interfaces).

<<NAME>>

## 4. Enumerate physical and logical locations

<<MUST item:4.3:locations>>
_The scope statement must be unambiguous about where it applies._

List the physical sites + the logical environments (AWS regions, SaaS
tenants, network segments). This becomes the inventory the auditor
uses to sample.

**✓ Good**: "Physical locations: UK (London — corporate HQ, 35 staff);
Czech Republic (Prague — engineering office, 22 staff). Logical
locations: AWS eu-west-1 (production), AWS eu-west-2 (DR), Okta
(identity), Google Workspace (corporate productivity), Atlassian
Cloud (engineering tooling). Cloud-only — no on-prem data centres."

**✗ Avoid**: "Global" or "All offices" without enumeration. The
auditor cannot sample what you cannot list.

<<NAME>>

## 5. List products and services in scope

<<MUST item:4.3:products_services>>
_The "what we do" half of scope, paired with the "where" of locations._

What products and services do you offer that fall under the ISMS?
This drives every downstream control's "applicability" decision.

**✓ Good**: "Products: (1) ArionComply Compliance SaaS — multi-tenant
RAG platform delivered to enterprise customers under signed MSAs.
Services: (a) implementation services (consulting), (b) managed-
service support tier for enterprise customers (24/7 incident response
in scope). Out of scope: marketing website, free public demo
environment, internal HR & finance tooling that doesn't touch customer
data."

**✗ Avoid**: Vague product names without context on what data flows
through them.

<<NAME>>

## 6. Name the document owner

<<MUST item:4.3:owner>>
_Accountability — every controlled doc needs a named owner._

The owner is typically the **ISMS Manager** or equivalent senior
information security role. They're responsible for keeping the scope
statement current and triggering reviews on significant changes.

**✓ Good**: "Document owner: ISMS Manager (currently <<ISMS_MANAGER_NAME>>).
Approval: ISMS Owner (CEO). Review cadence: annual + on significant
change."

**✗ Avoid**: "ISMS team" (ownership must be personal). "TBD" (a
scope statement without an owner is not a controlled document).

<<NAME>>

---

## Recommended additions

_These items strengthen the artefact but aren't strictly required
for the MUST checks._

### Reference key interested parties (link to Clause 4.2)

<<SHOULD item:4.3:stakeholders>>
_Cross-link to your Clause 4.2 register — the parties whose
expectations are addressed by the ISMS._

Listing top stakeholders within the scope statement makes it
self-contained for an external reader (auditor / customer) who hasn't
seen your 4.2 register.

<<TEXT>>

### Add version + review metadata

<<SHOULD item:4.3:version>>
_Document control discipline — required by Clause 7.5._

Standard top-of-document metadata: version, approval date, next
planned review date, change history.

**Example header block**:

```
Version:        v1.2
Approved:       <<APPROVAL_DATE>> by <<ISMS_OWNER_NAME>>
Next review:    <<NEXT_REVIEW_DATE>>
Change history: v1.0 initial — v1.1 added Czech office — v1.2 ...
```

<<TEXT>>
