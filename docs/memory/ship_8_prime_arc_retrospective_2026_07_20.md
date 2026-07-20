---
name: ship-8-prime-arc-retrospective-2026-07-20
description: "Ship 8' arc retrospective — ISO 27701 gap-close; 2 sub-arcs shipped, 1 dropped as false alarm"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 8' arc — ISO 27701 gap-close. Entry-point for future work
on 27701 specifically or on backfilling/data-hygiene work
against the output gateway.

**Arc window:** 2026-07-20. 2 sub-arcs (8'.a + 8'.b) delivered
+ 1 hypothesis dropped, all in one day.

## Motivation

The user's ask after Ship 7' closed:

> "We did have some gaps we needed to go back to to strengthen
> ISO 27701."

CLAUDE.md's build-sequence line claimed "ISO 27701 ARC FULLY
COMPLETE across Phases 0-4." The gap audit surfaced four
candidates:

1. **`program_review` mapping void** — 49 leaves (one per anchor)
   fall through to LLM extraction
2. **Eval coverage anemic** — 3 cases vs GDPR's 47 and ISO 27001's
   ~85
3. **B.8 posture-seed correctness** — hypothesis that Arion is
   controller-only and B.8.x NC postures are wrong
4. **Markdown-escape DB backfill** — Ship 7'.d fixed the gateway,
   but DB rows still had `\-`, `\(`, `\.` artifacts

User picked the "bundle" option: eval + B.8 fix + backfill. What
actually shipped was different from what was planned — see the
false-alarm lesson below.

## Sub-arc inventory

| Sub-arc | Kind | Key win |
|---|---|---|
| 8'.a | DB one-shot | `scripts/backfill_markdown_escapes.py` — Python transform for scrub semantics, Postgres regex as WHERE filter. Idempotent. Backfilled 18 posture_controls + 1110 document_findings rows on demo tenant. |
| — | Investigation | B.8 posture-seed hypothesis DISCARDED. Verified against `client_facts`: Arion is BOTH `role_controller = true` AND `role_processor = true`. B.8 NC postures are correct. |
| 8'.b | Eval expansion | 12 new cases (#204-215) covering Phase 2 Batches 1/2/3 + first B.8 processor-mirror coverage + A.7 ambiguity. Suite 208 → 220. iso27701 tag 3 → 15. All 12 PASS on first eval run. |
| **8'.c** | **Retrospective** | This document. |

**Delivered:** 1 script + 1 memory doc per sub-arc + this
retrospective + 12 EvalCase entries. Baseline floor: 205/208 →
**217/220**.

## The false-alarm lesson

Ship 8's opening audit hypothesized: **"Arion is a controller
(compliance software vendor), but the tenant has 16 NC + 2 OFI
on B.8.x processor-mirror anchors — should mostly be N/A."**

Two problems with the hypothesis:

1. **Wrong reading of `client_facts`.** Arion's fact row shows
   `role_controller = true` AND `role_processor = true`.
   ArionComply's platform holds customer PII (uploaded
   compliance docs, tenant profile data) → processor role.
2. **Wrong reading of B.8.x gap_descriptions.** They explicitly
   describe Arion as a processor: "PII processed under a client
   contract (e.g., compliance documents uploaded to
   ArionComply)", "customer support-access + integration
   disclosures", etc.

The hypothesis was invalidated in 4 queries (client_facts + spot-
check of gap_descriptions). Zero code changes made.

**Lesson: verify data-driven hypotheses against DATA before
building the fix.** The audit had a plausible narrative
("Arion is a controller"); the data disagreed. Cost of the
false alarm was ~10 minutes; cost of building the "fix" first
would have been an entire sub-arc of misdirected work.

The AskUserQuestion decision tree from Ship 7'.a's discipline
(anchor + question before code) prevented the false-alarm
version from being locked in — the user picked "Bundle" without
knowing the B.8 piece would evaporate; I informed them and
rescoped in-arc.

## Coverage that shipped

**Eval coverage** by 27701 batch, post-Ship 8'.b:

| Section | Anchors | Eval cases | Coverage |
|---|---|---|---|
| Batch 1 (A.7.2 controller) | 7 | 5 (#202, #203, #204, #205, #206) | 71% |
| Batch 2 subject rights (A.7.3) | 10 | 2 (#207, #208) | 20% |
| Batch 2 PbD (A.7.4) | 9 | 2 (#209, #210) | 22% |
| Batch 3 transfers (A.7.5) | 4 | 2 (#211, #212) | 50% |
| B.8 processor (all subsections) | 19 | 2 (#213, #214) | 11% |
| Phase 3 integration | — | 1 (#201) | — |
| A.7 ambiguity | — | 1 (#215) | — |

Structural cases only. All target refs surface without
clarify-hedging. State-drift-tolerant per
[[feedback-eval-state-drift]].

## What still needs closing

- **`program_review` mapping void** (49 leaves) — the biggest
  remaining structural gap. Would need a curation batch to
  author doc_mappings + workbook_mappings per anchor. Own arc
  (~1 week).
- **B.8 subject-rights / retention / transfers mirror coverage**
  (B.8.3.x/B.8.4.x/B.8.5.x, 12 anchors). Same shape as A.7 —
  quick eval-only follow-up.
- **Bridge-fanout assertions** — 112 bridges have no eval. The
  bridge footer is data-driven so bridges do surface; nothing
  asserts they surface FOR SPECIFIC anchors.
- **27701 SoA (Statement of Applicability)** — worth checking if
  we have a scaffold for the tenant's SoA under 27701 (analogous
  to ISO 27001's SoA leaf). Not visited this arc.
- **27701 demo documents** — Arion has no dedicated 27701 docs.
  Every 27701 posture is either NC (no evidence) or copy-pasted
  from GDPR docs. Adding 2-3 real PIMS documents (privacy
  program charter, DPIA register, transfer register) would
  exercise the doc_mappings + workbook_mappings.

## Lessons carried forward

- **Verify data hypotheses against data.** The B.8 false alarm
  was ~10 minutes to check; skipping the check would have cost
  a sub-arc.
- **Complementary fixes are worth doing.** Ship 7'.d fixed
  markdown escapes at serialization. 8'.a fixed the DB. Both
  needed. Missing one leaves a hole visible to anyone taking a
  non-standard path.
- **Eval coverage should track curation depth.** ISO 27001's
  ~85 cases mirror its ~118 controls (72%). 27701's pre-arc
  3 cases mirrored 49 controls (6%). Post-arc: 15 cases (31%).
  Still below the ISO 27001 ratio but materially better.
- **Structural assertions age well.** All 12 new cases target
  refs + forbid clarify-hedging, no strict phrase matches per
  the state-drift rule. Should stay stable through prompt
  tuning + LLM-tier changes.

## Ship 8' close

| Sub-arc | Status |
|---|---|
| 8'.a Markdown-escape DB backfill | ✓ |
| — B.8 posture-seed fix | DROPPED (false alarm) |
| 8'.b ISO 27701 eval coverage expansion | ✓ |
| **8'.c Arc retrospective** | **✓ (this doc)** |

## Related

- [[ship-7-prime-arc-retrospective-2026-07-19]] — previous arc
- [[ship-7-prime-d-evaluation-checkpoint-2026-07-19]] — 7'.d
  markdown-escape fix that 8'.a complements
- [[ship-8-prime-a-markdown-backfill-2026-07-20]] — 8'.a
- [[ship-8-prime-b-iso27701-eval-expansion-2026-07-20]] — 8'.b
- [[feedback-eval-state-drift]] — the structural-assertion
  discipline the eval expansion follows
