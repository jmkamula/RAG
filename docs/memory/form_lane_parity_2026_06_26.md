---
name: form-lane-parity-2026-06-26
description: "SHIPPED 2026-06-26 (2a9ac19): form lane auto-approve parity with templated lane. Form INSERT/UPDATE now set confirmed_by + confirmed_at (was missing — left form rows audit-incomplete + invisible in the panel). /api/v1/stage1/auto-approved widened to inference_source IN ('templated','form'). Closes the asymmetry surfaced after [[templated-lane-discipline-2026-06-25]]."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The asymmetry

Before today, two intake lanes were both tenant-authored (no
inference uncertainty) but only one had a complete audit trail:

| Lane       | review_status | confirmed_by | confirmed_at | Visible in panel? |
|------------|---------------|--------------|--------------|-------------------|
| templated  | approved      | uuid         | NOW()        | yes               |
| form       | approved      | NULL         | NULL         | no                |

Form rows already landed `approved` (set in
`dashboard_control_template_save`), but the visibility filter on
`/api/v1/stage1/auto-approved` was:

    df.inference_source = 'templated'
    AND df.confirmed_at > now() - days * interval

So form rows were:
- Audit-incomplete (no `confirmed_by` to point at the saver)
- Invisible in the panel (no `confirmed_at`, no inference_source match)

## Two-line fix

1. Form INSERT + UPDATE in `api_server.py` set
   `confirmed_by = %s::uuid` + `confirmed_at = NOW()`, mirroring
   `posture_writer:370`.
2. Panel filter widened to
   `inference_source IN ('templated', 'form')`.

Smoke verified: form save → row has audit fields populated, panel
returns it. Re-save UPDATE refreshes both timestamps.

## Carry-forward

The `inference_source IN ('templated', 'form')` predicate is now in
two places (panel + write logic). If a third tenant-authored lane
appears (in-product wizard? cascade-fill from related controls?),
refactor to a single helper `is_tenant_authored(src) -> bool` rather
than chasing every callsite. Not urgent at two callsites, worth
doing at three.

## Related

- [[templated-lane-discipline-2026-06-25]] — the templated-lane
  auto-approve write + edit-zone markers. This entry extends it
  to the form lane.
- [[templates-hybrid-2026-06-15]] — origin of the form lane
  (per-MUST web form sharing storage with the downloadable doc).
