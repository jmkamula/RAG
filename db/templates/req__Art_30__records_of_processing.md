---
leaf_id: req:Art.30:records_of_processing
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: records_of_processing
trigger_type: universal
template_version: 2
must_count: 9
should_count: 3
---

# Records of Processing Activities (RoPA)

## What this template gives you

The **GDPR Art.30 register** that lists every processing activity
your organisation runs, with its purposes, categories, recipients,
transfers, retention, and security measures. The single most-asked-
for artefact by data-protection regulators. Auditors trace
processing → RoPA → DPA → security controls in a single chain. A
weak RoPA is a finding in every GDPR audit.

## When to use it

You're producing the RoPA required by **GDPR Article 30**. Required
if you have ≥250 employees OR if processing is not occasional OR if
processing includes special categories. In practice: most
organisations need one. Maintained as a **live register**, not a
one-off document.

## Before you start

- [ ] **A.5.9 Asset Register** — assets holding PII drive activity
      rows (cross-link)
- [ ] **A.5.31 Compliance Register** — applicable jurisdictions +
      legal bases reference
- [ ] **A.5.12 Classification Scheme** — drives data-category
      labelling
- [ ] **A.5.20 Supplier Agreements** + **Art.28 DPAs** — drive
      processor recipients
- [ ] **Art.44-49 transfer mechanisms** in place where applicable

## Cross-references

- **Art.32 Security Measures** — RoPA references the T&O measures
  applied
- **Art.5.1.b Purpose Limitation** — purposes column enables
  enforcement
- **Art.5.1.e Storage Limitation** — retention column enables
  enforcement
- **Art.28 Processor Agreements** — recipients column maps to
  signed DPAs
- **Art.44-49 Transfers** — transfer-mechanism column where
  cross-border
- **A.5.34 Privacy Programme** — overall stewardship

## Estimated effort

**2-4 weeks** for v1 (data-flow discovery is the bulk); **ongoing
operational cost** to maintain (each new activity, processor,
purpose creates an RoPA row).

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Record controller name + DPO contact

<<MUST item:Art.30:controller_name>>
_Art.30(1)(a) — identity of the controller, joint controllers,
representative, DPO._

State the legal entity name, registered address, DPO contact (if
appointed), representative contact (if non-EU controller).

**✓ Good**: "Controller: <<TENANT_NAME>>, <<TENANT_LEGAL_NAME>>
Limited (registered office: <<REGISTERED_ADDRESS>>, company number
<<COMPANY_NUMBER>>). DPO: <<DPO_NAME>>, contact dpo@<<TENANT_DOMAIN>>.
Joint controllers (if applicable): listed per processing activity
where joint relationship exists, with the Art.26 arrangement
referenced. EU representative (if non-EU controller): not applicable
— <<TENANT_NAME>> is EU-established."

<<TEXT>>

## 2. State purposes of processing per activity

<<MUST item:Art.30:purposes>>
_Art.30(1)(b) — purposes of processing._

Each activity row gets one or more purposes. Purposes must be
specific, explicit, legitimate (Art.5.1.b).

**✓ Good** (activity-row sample): "Activity: Customer-account
management. Purposes: (1) Service delivery — operating the SaaS
platform contracted to the customer. (2) Customer support —
resolving service incidents. (3) Billing + revenue collection.
(4) Account-security monitoring (Art.32 alignment). Lawful basis:
contract (Art.6.1.b) for purposes 1-3; legitimate interest (Art.6.1.f
+ Recital 49) for purpose 4 with documented LIA."

**✗ Avoid**: "Various business purposes" (purpose-limitation
violation by definition).

<<TEXT>>

## 3. State categories of data subjects per activity

<<MUST item:Art.30:categories_ds>>
_Art.30(1)(c) — categories of data subjects._

Identify the subject categories per activity — not individual
names, but defined classes.

**✓ Good**: "Per-activity data-subject categories: Customer
end-users (the people using customer instances); Customer admin
users (the people managing customer instances); Prospective
customers (sales leads); Employees + contractors of
<<TENANT_NAME>>; Job applicants; Service-provider personnel (when
direct-named in DPAs). Children: not knowingly processed — see
A.6.3 + Art.8 stance."

<<TEXT>>

## 4. State categories of personal data per activity

<<MUST item:Art.30:categories_data>>
_Art.30(1)(c) — categories of personal data._

Data categories, not raw field lists. Distinguish identifiers from
behavioural data from special-category data.

**✓ Good**: "Per-activity data categories: (a) Identifiers (name,
email, phone, work address). (b) Account-related (login identifier,
password hash, MFA factor). (c) Usage / behavioural (action logs,
session timestamps, IP, user-agent). (d) Service-content (data the
end-user inputs into <<TENANT_NAME>> as part of using the service —
processed under instruction per Art.28). (e) Communications
(support tickets, sales emails). (f) Financial (billing contact,
payment-instrument reference — full PAN handled by Stripe processor
only, never by <<TENANT_NAME>>). Special category: not processed
unless customer instance content includes it (covered by DPA
restrictions)."

<<TEXT>>

## 5. State categories of recipients per activity

<<MUST item:Art.30:recipients>>
_Art.30(1)(d) — recipients including processors._

Internal recipients (departments / role classes) + external
processors + third-party recipients.

**✓ Good** (recipient table sample):

| Activity | Recipients |
|---|---|
| Customer account mgmt | Internal: customer success, support, finance. Processors: AWS (IaaS — DPA + SCC), Okta (identity), Stripe (billing — DPA + DPF) |
| Marketing comms | Internal: marketing. Processors: HubSpot (CRM — DPA + SCC) |
| HR / payroll | Internal: HR + finance. Processors: payroll provider (DPA, EU-hosted) |
| Customer support | Internal: support. Processors: Zendesk (DPA + SCC) |

<<TEXT>>

## 6. State third-country transfers + safeguards

<<MUST item:Art.30:transfers>>
_Art.30(1)(e) — international transfers + safeguards._

Per activity: which transfers occur, to where, on what
Art.45-49 basis.

**✓ Good** (transfer table sample):

| Activity / Recipient | Destination | Mechanism |
|---|---|---|
| AWS (IaaS) | eu-west-1 / eu-west-2 primary; us-east-1 for DR-only | EU residency primary; SCC + supplementary measures per Schrems II for any rare US fallback |
| Okta (identity) | EU pod (Frankfurt) | EU residency; SCC stand-by |
| Stripe (billing) | US | EU-US DPF certified; SCC stand-by |
| HubSpot (CRM) | US | EU-US DPF certified |
| Zendesk (support) | EU pod | EU residency; SCC stand-by |

No transfers to non-adequacy countries without explicit
Art.46 safeguards + TIA per EDPB 01/2020.

<<TEXT>>

## 7. State retention periods per category

<<MUST item:Art.30:retention>>
_Art.30(1)(f) — envisaged time limits for erasure._

Per data category (or activity) — when does deletion happen?
Cross-link to A.5.33 retention schedule.

**✓ Good** (retention sample):

| Category | Retention | Trigger |
|---|---|---|
| Customer account identifiers | Duration of contract + 7 years (records / tax) | Contract end |
| Customer usage logs | 13 months rolling | Time-based |
| Customer service-content | Per customer DPA (default: 30 days post-termination, then deletion confirmed in writing) | Contract end + grace |
| Marketing prospect data | 24 months from last engagement | Inactivity |
| Job applicant data (unsuccessful) | 12 months | Decision date |
| Employee HR data | Duration of employment + 7 years | Employment end |
| Support tickets | 5 years | Closure date |
| Billing / financial records | 7 years (statutory) | Record date |

Cross-link to A.5.33 records retention schedule for the
authoritative source.

<<TEXT>>

## 8. State technical + organisational security measures

<<MUST item:Art.30:security>>
_Art.30(1)(g) — general description of T&O measures (Art.32)._

General description — the detail lives in Art.32
risk_appropriate_measures_register; this is the summary.

**✓ Good**: "General T&O measures: (a) Encryption at rest (AES-256
on storage; envelope encryption for sensitive data) + in transit
(TLS 1.2+ baseline, 1.3 preferred). (b) Access control per
A.5.15-18: RBAC default, MFA mandatory, quarterly privileged
review. (c) Logging + monitoring per A.8.15 — write-only immutable
sink; 90-day hot, 6-year cold. (d) Backups per A.8.13 — encrypted,
geo-redundant, tested restore quarterly. (e) Incident response per
A.5.24 with GDPR Art.33 72h SLA. (f) Supplier discipline per
A.5.19-23. (g) Training per A.6.3 with privacy module mandatory.
(h) DPO + privacy team operating per A.5.34. Full register: Art.32
risk_appropriate_measures_register."

<<TEXT>>

## 9. Include processor-side records if applicable

<<MUST item:Art.30:processor_records>>
_Art.30(2) — if you act as processor for others, the Art.30(2)
parallel register applies._

If <<TENANT_NAME>> processes data on behalf of customers (as a
processor), you also maintain Art.30(2) records per controller you
serve.

**✓ Good**: "<<TENANT_NAME>> acts as processor for customer
instances of the SaaS product. The Art.30(2) processor-side
register is maintained separately, with one row per customer
controller, capturing: (a) controller identity + DPO contact; (b)
categories of processing on their behalf; (c) cross-border
transfers within the processing (we are EU-hosted by default);
(d) general T&O measures. Customer DPAs serve as the
authoritative cross-reference."

<<TEXT>>

---

## Recommended additions

### Maintenance procedure cross-link

<<SHOULD item:Art.30:maintained>>
_Pair with the Art.30 ropa_maintenance_procedure sibling leaf._

State that the RoPA is maintained per the documented procedure.

<<TEXT>>

### Availability commitment

<<SHOULD item:Art.30:availability>>
_Art.30(4) — made available to the supervisory authority on request._

State the SLA for making the RoPA available (typically immediate
electronic transfer).

<<TEXT>>

### Register versioning

<<SHOULD item:Art.30:reg_versioning>>
_Version + changelog — auditors want to see this evolves with
the business._

Standard versioning + change-log columns on each row.

<<TEXT>>
