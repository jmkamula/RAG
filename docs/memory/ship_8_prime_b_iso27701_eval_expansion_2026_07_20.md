---
name: ship-8-prime-b-iso27701-eval-expansion-2026-07-20
description: "Ship 8'.b — expand ISO 27701 eval coverage from 3 to 15 cases across all Phase 2 curation batches + B.8 processor block"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 8'.b (2026-07-20) — closes the ISO 27701 eval-coverage gap
identified in Ship 8's opening audit.

## The gap

Pre-Ship-8'.b:

- ISO 27001: ~85 eval cases
- GDPR:      47 eval cases (`iso27701` tag: 47 cases)
- ISO 27701: **3 eval cases** (#201-203, Phase 3 chat integration)

The Phase 2 curation batches (Batch 1 controller anchors +
Batch 2 subject rights + PbD + Batch 3 transfers) shipped 196
leaves + 112 bridges but were never locked in with eval
assertions. Same for the B.8 processor block.

## What shipped

**12 new eval cases (IDs 204-215)** — every one structural per
[[feedback-eval-state-drift]] (must_contain the ref, forbid
clarify-hedging, no strict phrase matches).

By batch:

- **Phase 2 Batch 1 controller anchors** (already had #202
  A.7.2.6, #203 A.7.2.5):
  - #204 A.7.2.1 (identify purpose) — NC
  - #205 A.7.2.7 (joint controller) — **N/A** applicability
  - #206 A.7.2.8 (records of processing) — **OFI** partial

- **Phase 2 Batch 2 subject rights** (A.7.3.x, 10 anchors):
  - #207 A.7.3.5 (individual data subject rights) — NC
  - #208 A.7.3.10 (automated decision-making) — **N/A**
    applicability

- **Phase 2 Batch 2 PbD** (A.7.4.x, 9 anchors):
  - #209 A.7.4.5 (PII de-identification at end of processing)
    — **OFI** partial
  - #210 A.7.4.7 (retention) — NC

- **Phase 2 Batch 3 transfers** (A.7.5.x, 4 anchors):
  - #211 A.7.5.1 (basis for transfer) — NC
  - #212 A.7.5.3 (transfer records) — NC

- **B.8 processor mirrors** (first-ever coverage):
  - #213 B.8.2.1 (customer agreement) — NC
  - #214 B.8.2.6 (processor RoPA) — **OFI**

- **A.7 ref-ambiguity**:
  - #215 "what is A.7 about?" — verifies chat doesn't silently
    resolve to ONE framework when A.7.x is used by BOTH ISO
    27001 (physical) + ISO 27701 (PIMS controller)

## Coverage matrix

| Aspect | Cases |
|---|---|
| Batch 1 controller anchors  | 204, 202 (existing), 205, 206, 203 (existing) |
| Batch 2 subject rights      | 207, 208 |
| Batch 2 PbD                 | 209, 210 |
| Batch 3 transfers           | 211, 212 |
| B.8 processor block         | 213, 214 |
| A.7 ambiguity               | 215 |
| Phase 3 chat integration    | 201, 202, 203 (existing) |
| N/A applicability states    | 205, 208 |
| OFI partial-evidence states | 206, 209, 214 |

## Baseline change

Pre-Ship-8'.b: 207/208 PASS + 1 WARN + 0 FAIL. Baseline floor:
205/208 blocks restart.

Post-Ship-8'.b: 220 total cases. Baseline expected: 219/220
PASS + 1 WARN + 0 FAIL (same #200 pre-existing WARN). Baseline
floor updates to 217/220 blocks restart.

## Not covered (deferred)

- **B.8 subject-rights + retention + transfers mirrors**
  (B.8.3.x/B.8.4.x/B.8.5.x, 12 anchors). Same shape as A.7.3-5.
  Could be a Ship 9'.a bulk-add.
- **Cross-framework bridge assertions** — the 112 bridges have
  no eval coverage. The bridge footer is data-driven (Ship 1.14)
  so bridges surface naturally, but no case asserts them.
- **`program_review` leaves** — 49 anchor-level review artefacts
  fall through to LLM extraction. Not eval-tested; needs the
  program_review mapping arc first.

## Baseline

Full eval running. Cases are structural — they should PASS on
the current Arion posture state.

## Ship 8' progress

| Sub-arc | Status |
|---|---|
| 8'.a Markdown-escape DB backfill | ✓ |
| **8'.b ISO 27701 eval coverage expansion** | **✓** |
| 8'.c Arc retrospective | next |

## Related

- [[ship-8-prime-a-markdown-backfill-2026-07-20]] — the DB-side
  fix; this arc locks the state
- [[feedback-eval-state-drift]] — the structural-assertion
  discipline this batch follows
