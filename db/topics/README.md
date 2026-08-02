# db/topics/ — topic bundles

## What this is

Curator-authored bundles that group per-leaf templates into
compliance-topic workflows. Ship 54'.a (2026-08-02) opened this as
an **additive overlay** — the per-leaf templates in `db/templates/`
remain the source of truth; topics reference them but never modify
them.

## Design shape

Each `*.yaml` file defines one topic. Topics reference leaves by
`leaf_id`. The same leaf can appear in multiple topics with
different roles (e.g., `A.5.15` is `primary_procedure` in Access
Rights Lifecycle but `supporting_iso_mirror` in DSR Management).

## Schema

```yaml
slug: <kebab-case-identifier>              # required, PK
title: <human title>                       # required
description: |                             # required — plain prose, 2-4 sentences
  ...
primary_framework: ISO27001:2022|GDPR:2016/679|ISO27701:2019|multi
display_order: <int>                       # optional; lower = higher priority
auditor_expects: |                         # required — consultant-grade narrative
  ...

leaves:                                    # required, ≥1 entry
  - leaf_id: req:X:Y                       # required — must exist in the catalog
    role: primary_policy|primary_procedure|primary_register|
          supporting_prerequisite|supporting_iso_mirror|supporting_cross_framework|
          form|log|review_record|evidence
    workflow_order: <int>                  # 1..N; ties allowed for parallel steps
    role_note: |                           # optional; short curator note
      ...
```

## Loading

```
PYTHONPATH=/data/arioncomply python3 enrichment/topics/load_to_postgres.py
```

Fails loud on:
- unknown `leaf_id` (not in `ALL_EVIDENCE_REQUIREMENTS` union with
  `ALL_DERIVED_SPECS.direct_evidence`)
- missing required fields
- duplicate leaf_id within one topic

## Ship 54'.a starter set

12 topics covering the highest-frequency ISO 27001 + GDPR real-world
compliance flows. Add topics per customer engagement; the loader is
idempotent + orphan-sweeping so deletion works cleanly.

| Slug | Framework | Description |
|---|---|---|
| `dsr_management` | GDPR | Subject access & data subject rights (Chap III) |
| `incident_response` | multi | Security incident lifecycle end-to-end |
| `breach_notification` | GDPR | Personal data breach 72h notification workflow |
| `risk_assessment_treatment` | ISO27001 | Risk cycle (6.1.2, 6.1.3, 8.2, 8.3) |
| `dpia_workflow` | GDPR | Data Protection Impact Assessment (Art.35) |
| `supplier_onboarding` | multi | Vendor / processor onboarding (Art.28 + A.5.19-23) |
| `employee_lifecycle` | multi | HR onboarding / offboarding (A.6.x + A.5.11 + A.5.16-18) |
| `business_continuity` | ISO27001 | BCP + ICT readiness (A.5.29 + A.5.30 + A.8.13) |
| `access_rights_lifecycle` | multi | Identity + access (A.5.15-18) |
| `records_of_processing` | GDPR | RoPA maintenance (Art.30) |
| `change_management` | ISO27001 | Change control (6.3 + A.8.32) |
| `continual_improvement` | ISO27001 | Nonconformity + corrective action + audit + MR |
