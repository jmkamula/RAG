---
name: ship-9-prime-arc-retrospective-2026-07-20
description: "Ship 9' arc retrospective — closes ISO 27701 to 100% coverage in one day + 3 sub-arcs"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 9' arc — completes ISO 27701. Entry-point for future 27701
follow-ups or SoA-template evolution.

**Arc window:** 2026-07-20. 3 sub-arcs delivered (9'.a + 9'.b +
9'.c) + 1 skipped (9'.d demo docs) + closer, all in one day.

## Motivation

Ship 8'.c's retrospective flagged four remaining ISO 27701 gaps:

1. `program_review` mapping void (49 leaves fall through to LLM)
2. B.8.3-5 eval mirrors uncovered
3. SoA template didn't mention 27701
4. No demo 27701 documents on the Arion tenant

Ship 8 closed the first three of those as follow-ups. Ship 9
tackled them.

## Sub-arc inventory

| Sub-arc | Kind | Key win |
|---|---|---|
| 9'.a | Eval expansion | 6 new cases (#216-221) covering B.8.3.1 subject rights, B.8.4.1/2 retention, B.8.5.1/4/8 transfers. First eval coverage of B.8.3-5. |
| 9'.b | Curator prose | Extended SoA template with 700-word PIMS extension section — enumerates all 49 27701 anchors by batch + role-based applicability rules + example rows. Template loaded (unchanged: 843, updated: 1). |
| 9'.c | Mapping generator | Extended `generate_doc_mappings.py` with `_is_review_doc()` predicate. Generated **189 new YAML files** covering 49 27701 program_reviews + 140 bonus ISO 27001 ISMS + Annex A review leaves. Total doc_mappings: 402 → 591. |
| — | 9'.d Demo docs | SKIPPED per user direction — synthetic docs would prove what unit tests already prove; real customer docs come with deployment. |
| **9'.e** | **Retrospective** | This document. |

## Coverage numbers

### ISO 27701 leaf mapping coverage — 75% → 100%

| | Pre | Post | Delta |
|---|---|---|---|
| Doc-mapped 27701 leaves | 98 | 147 | +49 |
| Workbook-mapped | 49 | 49 | — |
| Union | 147 | **196** | +49 |
| Total 27701 leaves | 196 | 196 | — |
| Coverage | 75% | **100%** | +25pp |
| Fall-through to LLM | 49 | **0** | -49 |

The LLM extractor is no longer the default path for any 27701
leaf. Every anchor has a deterministic mapping.

### Eval coverage — 220 → 226

| | Pre | Post |
|---|---|---|
| `iso27701` tag | 15 | **21** |
| Total suite | 220 | **226** |
| PASS baseline | 219/220 | **225/226** |
| Baseline floor | 217/220 | **223/226** |

The 6 new B.8 cases passed on first eval run — no phrasing
tweaks needed.

### File-level delta

| Path | Change |
|---|---|
| `tests/eval_suite.py` | +6 EvalCase entries (#216-221) |
| `db/templates/req__6_1_3__statement_of_applicability.md` | +75 lines PIMS extension |
| `scripts/generate_doc_mappings.py` | +25 lines `_is_review_doc` predicate + wire-up |
| `db/doc_mappings/*.yaml` | +189 new files (auto-generated) |

## Architectural properties confirmed

1. **The framework-aware generator scales linearly.** Adding a
   new evidence_type family (`review_record` doc-shape subset)
   took 25 lines + 1 run. The 189 new files were essentially
   free; the constraint was recognizing the shape existed. Same
   pattern will apply when SOC 2 / NIS2 / DORA / HIPAA land.

2. **Template hardening is a curator task, not a code task.**
   The SoA update was a Markdown edit + template reload. No
   schema change, no code change. The `soa_external_controls`
   SHOULD field was already the right architectural hook — the
   arc just filled it in for 27701 specifically.

3. **Coverage percentages should be tracked.** The 75% → 100%
   number was legible to the user + reviewer. Every framework
   arc from now on should report leaf-mapping coverage as a
   post-condition. The metric is the derived union of
   doc_mappings + workbook_mappings over Neo4j
   EvidenceRequirements per standard_id.

4. **Eval doesn't need per-anchor coverage.** B.8.3-5 has 12
   anchors; we tested 6 (one per subsection + representative
   findings). Structural regression is the goal, not
   completeness. Locking every anchor would 3x the eval
   runtime for marginal signal.

## Lessons carried forward

- **The audit-hypothesis discipline held.** Ship 8'.c's
  retrospective codified "verify hypotheses against data
  before building." Ship 9 tested the `program_review` void
  claim (49 leaves fall through) against real data before
  authoring — the number checked out. Zero re-scoping this arc.
- **Skip work when unit tests already prove it.** 9'.d was
  planned for authoring 2-3 realistic 27701 docs. The user
  correctly flagged this as demo-quality overhead. Skipping
  saved ~3 hours; deferred to real customer engagements.
- **Bonus coverage is real value.** 9'.c's generator extension
  targeted 49 27701 leaves but delivered 189 (140 bonus for
  ISO 27001 ISMS + Annex A review leaves). Cheap extension
  → broad coverage.

## Deferred / follow-up

- **Bridge-fanout eval assertions** — 112 27701 bridges have no
  eval. Bridge footer surfaces them data-driven; nothing
  asserts they surface FOR SPECIFIC anchors.
- **Demo 27701 documents** — never worth building synthetic;
  will come with real customer engagements.
- **SoA per-tenant customization** — currently the SoA template
  is one-size-fits-all. When we add SOC 2 / NIS2 the same
  extension pattern applies (add a new section for each
  enrolled framework). If the tenant enrolls in 4 frameworks,
  the template gets long. Consider tenant-scoped SoA rendering
  as a future arc.
- **Test the generator's bonus coverage.** 140 new mappings for
  ISO 27001 program_review + periodic_review leaves — no
  regression detected but no explicit eval covers them either.
  Could be a smaller follow-up arc.

## Ship 9' close

| Sub-arc | Status |
|---|---|
| 9'.a B.8.3-5 eval mirrors | ✓ |
| 9'.b SoA template 27701 extension | ✓ |
| 9'.c program_review doc_mappings | ✓ |
| 9'.d Demo 27701 documents | SKIPPED |
| **9'.e Arc retrospective** | **✓ (this doc)** |

## Related

- [[ship-9-prime-a-b-c-iso27701-close-2026-07-20]] — sub-arc
  detail
- [[ship-8-prime-arc-retrospective-2026-07-20]] — the arc that
  identified these gaps
- [[ship-7-prime-arc-retrospective-2026-07-19]] — output gateway
  arc; the SoA template rendering runs through it
