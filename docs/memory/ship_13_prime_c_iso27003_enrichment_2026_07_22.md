---
name: ship-13-prime-c-iso27003-enrichment-2026-07-22
description: "Ship 13'.c — 26 ISMS clause leaves enriched with ISO 27003:2017 paragraphs; two renumbering traps caught + fixed pre-write"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13'.c (2026-07-22) — third sub-arc of Ship 13. Enriched all
26 ISMS clause leaves (chapters 4-10) with authority-cited
paragraphs paraphrasing ISO 27003:2017 guidance. Each cites a
specific 27003:2017 § pointer verified against source text.

## What ships

`scripts/enrich_iso27003_leaves.py` — idempotent Neo4j enrichment.
Appends per-leaf paragraphs AFTER the Ship 12'.c citation footer
and (for 6.1/6.1.x/6.3/8.x) after the Ship 13'.b 27005 paragraph.
Skips if the `Per ISO 27003:2017` marker is already present.

Applied to demo Neo4j: **26 leaves updated, 0 skipped, 0 missing**.
Second pass reports 26 already-marked, 0 updates — idempotent.

Total added: ~14 KB across the 26 leaves (avg ~540c per paragraph).
Length range: 325c (4.4 ISMS umbrella, thinnest) to 689c (5.1
leadership + commitment, richest — 8 lettered obligations).

## Two ISO 27001:2013 → :2022 renumbering traps caught + fixed

Both surfaced in the dry-run before any live writes.

### Trap 1: §10.1 ↔ §10.2 swap

ISO 27001:2013 §10 subdivided into:
- §10.1 Nonconformity and corrective action
- §10.2 Continual improvement

ISO 27001:2022 restructured to:
- §10.1 Continual improvement  ← was §10.2
- §10.2 Nonconformity and corrective action  ← was §10.1

**ISO 27003:2017 is on the :2013 numbering.** First-draft
enrichment mapped 27003 §10.1 to 27001 §10.1, publishing
nonconformity content under a continual-improvement leaf.
Detected by cross-checking Neo4j titles against the enrichment
content in dry-run. Fixed by swapping: 27001:2022 §10.1 leaf now
cites 27003:2017 §10.2 with an explicit renumbering note; §10.2
leaf cites 27003:2017 §10.1 with the same note. Auditors
following the citation see immediately why the numbers don't
match.

### Trap 2: §6.3 is new in ISO 27001:2022

ISO 27001:2022 added §6.3 (Planning of changes) — this clause
did not exist in ISO 27001:2013 and therefore is absent from
ISO 27003:2017. First-draft enrichment cited a phantom "27003
§6.3". Verified by grepping the extract for §6.[0-9]:

```
667:6.1 Actions to address risks and opportunities
1087:6.2 Information security objectives and planning to achieve them
[no §6.3]
```

Fixed by citing the closest guidance — ISO 27003:2017 §8.1
(Operational planning and control), which covers "planned
changes" and "unintended changes" — with a note that 27003:2017
predates 27001:2022 §6.3.

## Lesson codified

**Curation from a guidance standard requires cross-version
mapping**, especially between an older guidance edition (27003:2017,
which mirrors 27001:2013) and a newer normative edition
(27001:2022). Two failure modes:

1. **Numbering swap** — clauses moved. Same title, different §.
2. **New clause** — guidance doesn't exist yet.

Mitigation: cross-check Neo4j `title` field against the citation
in dry-run BEFORE the live write. Both traps surfaced this way.

Retroactive check on Ship 13'.b (27005): safe — 27005:2022 is
current, aligned to 27001:2022 numbering. No traps found.

## Curation discipline maintained

- **Prose-only.** No new MUSTs or SHOULDs from 27003 content
  (guidance is non-normative).
- **Paraphrase, never verbatim.** Content authored in English
  from source-text reading, then verified against extract.
- **§ pointer accuracy.** Every citation confirmed against
  extracted 27003:2017 text.
- **Reading-order for stacked enrichment.** Leaves that carry
  both 27003 and 27005 paragraphs (6.1, 6.1.1, 6.1.2, 6.1.3,
  6.3, 8.1, 8.2, 8.3) now show:
  - existing prose (from Ship 12'.c backfill or upstream)
  - Ship 12'.c citation footer
  - Ship 13'.b 27005 paragraph
  - Ship 13'.c 27003 paragraph

  Reading progression is honest curation order. Not
  alphabetical by standard — but readable.

## Per-clause enrichment table

| Clause | Neo4j title | 27003 § | Bytes |
|---|---|---|---|
| 4.1 | Understanding org context | §4.1 | 611 |
| 4.2 | Understanding interested parties | §4.2 | 477 |
| 4.3 | Determining ISMS scope | §4.3 | 584 |
| 4.4 | ISMS establishment | §4.4 | 325 |
| 5.1 | Leadership and commitment | §5.1 | 689 |
| 5.2 | Policy | §5.2 | 579 |
| 5.3 | Roles + responsibilities | §5.3 | 592 |
| 6.1 | Risk actions framework | §6.1 | 482 |
| 6.1.1 | General | §6.1.1 | 559 |
| 6.1.2 | Risk assessment | §6.1.2 | 507 |
| 6.1.3 | Risk treatment | §6.1.3 | 507 |
| 6.2 | Objectives | §6.2 | 520 |
| 6.3 | Planning of changes | §8.1 (renum note) | 516 |
| 7.1 | Resources | §7.1 | 437 |
| 7.2 | Competence | §7.2 | 523 |
| 7.3 | Awareness | §7.3 | 437 |
| 7.4 | Communication | §7.4 | 563 |
| 7.5 | Documented information | §7.5 | 555 |
| 8.1 | Operational planning | §8.1 | 642 |
| 8.2 | Op'l risk assessment | §8.2 | 486 |
| 8.3 | Op'l risk treatment | §8.3 | 356 |
| 9.1 | Monitoring + measurement | §9.1 | 511 |
| 9.2 | Internal audit | §9.2 | 600 |
| 9.3 | Management review | §9.3 | 671 |
| 10.1 | Continual improvement | §10.2 (renum note) | 662 |
| 10.2 | Nonconformity + corrective action | §10.1 (renum note) | 584 |

## Surface impact

Same as Ship 13'.b — content surfaces on Evidence Package
"What this is about" + external API `/posture/{ref}` drill-in.
Chat digest promotion is Ship 13'.d.

## Ship 13 progress

| Sub-arc | Status |
|---|---|
| 13'.a Design + 27004 unenrollment | ✓ |
| 13'.b 27005 batch (14 leaves) | ✓ |
| **13'.c 27003 batch (26 ISMS clauses)** | **✓ (this doc)** |
| 13'.d Chroma + chat digest promotion + eval | next |
| 13'.e Arc retrospective | pending |

## Impact on baseline

Data-only change. Chat digest doesn't consume business_description
by default (obligation_text priority). Eval expected unchanged.

Eval run confirmed: **225/226 PASS + 1 WARN + 0 FAIL** — 1 WARN
is the pre-existing #200 gap_analysis vs posture_check mismatch;
baseline unchanged. Zero regressions from the 27003 prose
enrichment despite the two renumbering fixes.

## Related

- [[ship-13-prime-a-iso27000-curation-design-2026-07-21]] — design + sub-arc plan
- [[ship-13-prime-b-iso27005-enrichment-2026-07-21]] — the 27005 companion arc
- Ship 3'.l retrospective — the ISO 27001:2013→2022 renumbering
  fix in source JSONs (2026-07-17). This arc discovers the same
  renumbering trap in a different context (curation from a
  standard indexed to 27001:2013).
- Ship 13'.d: Chroma indexing + chat digest promotion + eval cases
