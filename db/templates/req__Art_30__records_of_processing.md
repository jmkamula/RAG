---
leaf_id: req:Art.30:records_of_processing
control_ref: Art.30
standard_id: GDPR:2016/679
evidence_type: records_of_processing
trigger_type: universal
template_version: 2
must_count: 9
should_count: 3
table_shape: hybrid
---

# Records of Processing Activities (RoPA)

<<DOC_CONTROL>>

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

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**2-4 weeks** for v1 (data-flow discovery is the bulk); **ongoing operational cost** to maintain.

---

## Per-activity table

This is the **per-processing-activity register**. One row per
activity. Most MUSTs are per-row columns. Controller identity +
processor-side records are document-level (filled below the table).

<!-- TABLE-COLUMNS leaf:req:Art.30:records_of_processing -->
<!-- column: item:Art.30:purposes -->
<!-- column: item:Art.30:categories_ds -->
<!-- column: item:Art.30:categories_data -->
<!-- column: item:Art.30:recipients -->
<!-- column: item:Art.30:transfers -->
<!-- column: item:Art.30:retention -->
<!-- column: item:Art.30:security -->
<!-- /TABLE-COLUMNS -->

<!-- EDIT-ZONE-START leaf:req:Art.30:records_of_processing -->
| Purposes | Data Subjects | Data Categories | Recipients | Transfers + Safeguards | Retention | T&O Measures |
|---|---|---|---|---|---|---|
|          |               |                 |            |                        |           |              |
|          |               |                 |            |                        |           |              |
|          |               |                 |            |                        |           |              |
<!-- EDIT-ZONE-END leaf:req:Art.30:records_of_processing -->

## Column guidance — what to fill in

### Purposes

<<MUST item:Art.30:purposes>>

> _Standard text:_ Purposes of the processing stated per activity
> (Art.30(1)(b))

Each activity row gets one or more purposes. Purposes must be
specific, explicit, legitimate (Art.5.1.b).

**✓ Good**: `Customer account management — service delivery
(Art.6.1.b contract); customer support (Art.6.1.b); billing
(Art.6.1.b); security monitoring (Art.6.1.f LIA documented).`

**✗ Avoid**: "Various business purposes" — purpose-limitation
violation by definition.

<<GUIDANCE>>

### Data Subjects

<<MUST item:Art.30:categories_ds>>

> _Standard text:_ Categories of data subjects per activity
> (Art.30(1)(c))

Defined classes, not individual names.

**✓ Good**: `Customer end-users; Customer admin users; Prospective
customers (sales leads); Employees + contractors of <<TENANT_NAME>>;
Job applicants`

**✗ Avoid**: "Users" alone — too broad.

<<GUIDANCE>>

### Data Categories

<<MUST item:Art.30:categories_data>>

> _Standard text:_ Categories of personal data per activity
> (Art.30(1)(c))

Categories, not raw field lists. Distinguish identifiers from
behavioural data from special-category.

**✓ Good**: `Identifiers (name, email, phone); Account-related
(login, password hash, MFA factor); Usage/behavioural (action logs,
IPs); Service-content (instructed by customer per Art.28).`

**✗ Avoid**: "Personal data" — too vague.

<<GUIDANCE>>

### Recipients

<<MUST item:Art.30:recipients>>

> _Standard text:_ Categories of recipients per activity (including
> processors and third parties) (Art.30(1)(d))

Internal recipients + external processors + third-party recipients.
Cross-link to A.5.20 supplier register.

**✓ Good**: `Internal: customer success, support, finance.
Processors: AWS (DPA + SCC), Okta (identity), Stripe (billing — DPF).`

**✗ Avoid**: "Service providers" without naming them.

<<GUIDANCE>>

### Transfers + Safeguards

<<MUST item:Art.30:transfers>>

> _Standard text:_ Transfers to third countries or international
> organisations with safeguards identified (Art.30(1)(e))

Per row: which transfers occur, to where, on what Art.45-49 basis.

**✓ Good**: `AWS eu-west-1 (EU residency); Okta EU pod
(Frankfurt); Stripe US (DPF + SCC stand-by). No transfers to
non-adequacy countries without Art.46 + TIA per EDPB 01/2020.`

**✗ Avoid**: "Global processors" without per-vendor breakdown.

<<GUIDANCE>>

### Retention

<<MUST item:Art.30:retention>>

> _Standard text:_ Envisaged time limits for erasure per category
> (Art.30(1)(f))

When does deletion happen? Cross-link to A.5.33 retention schedule.

**✓ Good**: `Customer account: contract end + 7y (tax). Usage logs:
13 months rolling. Service-content: per customer DPA (30d post-term
default). Marketing prospect: 24 months from last engagement.`

**✗ Avoid**: "Indefinite" — fails storage-limitation (Art.5.1.e).

<<GUIDANCE>>

### T&O Measures

<<MUST item:Art.30:security>>

> _Standard text:_ General description of technical and
> organisational security measures (Art.32) (Art.30(1)(g))

General description — detail lives in Art.32
risk_appropriate_measures_register. This is the summary.

**✓ Good**: `Encryption at rest (AES-256) + in transit (TLS 1.2+);
RBAC + MFA per A.5.15-18; audit logging A.8.15; backup A.8.13; IR
per A.5.24 with GDPR Art.33 72h SLA; full register at Art.32.`

**✗ Avoid**: "Appropriate measures" — vague.

---

<<GUIDANCE>>

## Document-level fields

### Controller + DPO Identity

<<MUST item:Art.30:controller_name>>

> _Standard text:_ Name and contact details of controller (and DPO/
> representative where appointed) (Art.30(1)(a))

Legal entity, registered address, DPO contact, representative contact
if non-EU controller.

**✓ Good**:
```
Controller: <<TENANT_NAME>> Limited
Registered office: <<REGISTERED_ADDRESS>>
Company number: <<COMPANY_NUMBER>>
DPO: <<DPO_NAME>>, dpo@<<TENANT_DOMAIN>>
Joint controllers: [list per activity where applicable, with Art.26
  arrangement referenced]
EU representative: N/A (EU-established)
```

<!-- EDIT-ZONE-START item:Art.30:controller_name -->

<<GUIDANCE>>

<<TEXT>>
<!-- EDIT-ZONE-END item:Art.30:controller_name -->

### Processor-side Records (if applicable)

<<MUST item:Art.30:processor_records>>

> _Standard text:_ If the org also acts as processor, processor-side
> records per Art.30.2.a-d are included or kept as a parallel
> register

If <<TENANT_NAME>> processes data on behalf of customers, the
Art.30(2) processor-side register applies — one row per controller
served, capturing controller identity + processing categories +
transfers + T&O measures.

**✓ Good**: `<<TENANT_NAME>> acts as processor for customer instances
of the SaaS. Art.30(2) register maintained separately, with one row
per customer controller. Customer DPAs serve as the authoritative
cross-reference.`

<!-- EDIT-ZONE-START item:Art.30:processor_records -->

<<GUIDANCE>>

<<TEXT>>
<!-- EDIT-ZONE-END item:Art.30:processor_records -->

---

## Recommended additional context

### Maintenance Procedure Reference

<<SHOULD item:Art.30:maintained>>

> _Standard text:_ Pair with the Art.30 ropa_maintenance_procedure
> sibling leaf

State that the RoPA is maintained per the documented procedure
(ropa_maintenance_procedure leaf).

<<GUIDANCE>>

### Availability Commitment

<<SHOULD item:Art.30:availability>>

> _Standard text:_ Art.30(4) — made available to the supervisory
> authority on request

SLA for making the RoPA available (typically immediate electronic
transfer).

<<GUIDANCE>>

### Register Versioning

<<SHOULD item:Art.30:reg_versioning>>

> _Standard text:_ Version + changelog — auditors want to see this
> evolves with the business

Standard versioning + change-log columns on each row.

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
