---
name: ship-62-prime-arc-2026-08-12
description: "Ship 62' — Evidence Package bridge source excerpts. Auditor now sees the actual ISO evidence text under each cross-framework attribution, not just the ref. Per-package deduplication keeps repeated sources compact."
metadata:
  type: project
  ship: "62'"
---

# Ship 62' — Bridge source excerpts on the Evidence Package

## The arc in one sentence

Ship 62' closes Ship 61'.a's deferred item: when the Evidence
Package renders `↗ Covered via ISO 27001:2022 A.5.15 (IMPLEMENTS)`,
the actual A.5.15 evidence excerpt now appears underneath, so the
auditor sees what specifically covers the GDPR obligation without
navigating to another artifact.

## Delivery

**Batch source-excerpt fetch** — a single Postgres query pulls
excerpts for every `source_must_id` that will feature in the top-3
bridge groups across all bridged MUSTs in the leaf. `DISTINCT ON
(checklist_item_id)` returns one representative per source MUST,
scoped to the tenant's approved findings. Cost: one extra query per
package build; scoped to what actually renders (no fanout with
bridge cardinality).

**Render** — per bridged MUST, per grouped source
`(standard, control_ref, edge_type)` in the top-3:
```
  ↳ Covered via _ISO 27001:2022 A.5.18_ (IMPLEMENTS)
     > vendor access to PII requires a DPA, role-based accounts,
       least privilege, time-bound validity and prompt revocation
       after use.
     From _Access Control Policy.docx_
```

**Per-package deduplication** — `quoted_source_refs` set tracks
`(standard_id, source_control_ref)` pairs already quoted in this
package. First bridged MUST that references A.5.18 shows the
excerpt; every subsequent reference collapses to a compact
`(source excerpt shown under _ISO 27001:2022 A.5.18_ above)`
pointer. Auditor scans top-to-bottom without re-reading the same
ISO paragraph 4×.

## Verified on Arion demo

Art.32:program_review leaf: 1 direct-satisfied + 4 bridged MUSTs.
The first bridged MUST (`Review date within the planned interval`)
shows verbatim excerpts from A.5.18 / 6.1.2 / A.5.1 with filenames.
The three subsequent bridged MUSTs each show
`(source excerpt shown under _<ref>_ above)` under the same three
attribution lines. Package length shrinks by roughly 60% vs the
naive "quote everything every time" approach while preserving
every attribution claim.

## Codified lessons

### 21. Batch across the render surface, not per-item

The naive shape was one Postgres query per bridged MUST's
`source_must_ids` — potentially 5+ queries per leaf. Ship 62'
collects `source_must_ids_needed` in a single walk of `ssot_
verdicts` before rendering, then one query serves the whole
package. Rule: when a per-item render needs a per-item fetch,
walk the item list first to gather the fetch keys, then batch.

### 22. Deduplicate at the reader's cadence, not the writer's

The bridge coverage data legitimately says "A.5.18 IMPLEMENTS
every one of Art.32's 4 unmet MUSTs." Rendering that faithfully
would repeat A.5.18's excerpt 4× — technically accurate,
practically hostile. Ship 62' dedupes at *read time* per output
artifact (`quoted_source_refs` scoped to one Evidence Package
build). The underlying data stays maximally-attributed for other
consumers (Ship 60's per-MUST `bridge_sources` on the case-file
card still shows all attributions). Rule: normalize for storage,
denormalize for auditors — the anti-repetition discipline lives at
the presentation layer, not the data layer.

## Follow-ons

Ship 61'.a's other deferrals still stand:
- Recommended-additions SSoT parity (blocked: SSoT doesn't track
  SHOULDs; needs writer + schema thought).

## What Ship 62' costs to reproduce

- Schema migrations: 0
- Wall clock: ~30 minutes (fetch + render + dedup + retro)
- Files touched: 1 (`rag/posture/evidence_package.py`)
- Lines: ~70 (batch fetch + render change + dedup tracker)
- Eval regression: Evidence Package isn't in the eval suite;
  adjacent surfaces unchanged this ship.
