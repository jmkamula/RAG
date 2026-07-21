---
name: ship-12-prime-c-iso27000-citation-stubs-2026-07-21
description: "Ship 12'.c — citation stubs appended to 38 target leaves' business_description; auditor + external-API surfaces now point at 27003/27004/27005 as guidance authority"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 12'.c (2026-07-21) — third sub-arc of Ship 12'. Ship 12'.a
audited the gap (0 refs to 27003/27004/27005); Ship 12'.b enrolled
the standards in the registry + vocabulary. This sub-arc appends
authority-citation pointers to the 38 target 27001 leaves' Neo4j
`business_description` so auditor-facing surfaces show what
guidance underpins each leaf.

## What ships

`scripts/backfill_iso27000_guidance_citations.py` — one-shot,
idempotent Neo4j backfill. Appends
`\n\n[Related guidance: ISO 27005:2022]` (or multi-family variant
where a leaf spans multiple guidance standards) to each target
leaf's `business_description`.

Applied on demo Neo4j: **38 leaves updated, 0 misses**. Second
pass reports 38 already-marked, 0 updates — idempotent.

## Citation mix

Each leaf gets exactly one footer line combining its applicable
guidance standards, ordered 27003 → 27004 → 27005 for readability:

| Group | Leaves | Footer |
|---|---|---|
| ISMS clauses (excl. risk/monitoring) | 4.1-4.4, 5.1-5.3, 6.2, 7.1-7.5, 9.2, 9.3, 10.1, 10.2 (17) | `[Related guidance: ISO 27003:2017]` |
| ISMS clauses spanning risk | 6.1, 6.1.1, 6.1.2, 6.1.3, 6.3, 8.1, 8.2, 8.3 (8) | `[Related guidance: ISO 27003:2017 · ISO 27005:2022]` |
| ISMS clause spanning monitoring | 9.1 (1) | `[Related guidance: ISO 27003:2017 · ISO 27004:2016]` |
| Monitoring-only Annex A | A.5.22, A.5.36, A.5.37, A.7.4, A.8.15, A.8.16 (6) | `[Related guidance: ISO 27004:2016]` |
| Risk-only Annex A | A.5.5, A.5.7, A.5.24, A.5.29, A.5.30, A.7.5 (6) | `[Related guidance: ISO 27005:2022]` |

Total 38 unique leaves matching the audit memo's target list.

## Design decisions

**Standard-level, not §-level.** The memo in 12'.a floated a
`§7-8` sub-section pointer format. Dropped that in the write pass
because we don't have the source texts to verify which sub-sections
land on which leaf; a wrong § would be worse than none. When Ship
13+ curates from real texts, § pointers can be added per-leaf as
part of that arc.

**Ordered by standard number.** Multi-family citations render
`27003 · 27004 · 27005` regardless of which family drives the
leaf. Reader gets a consistent left-to-right of least to most
specialised.

**Appended, not replaced.** Existing `business_description`
content stays intact; footer follows a `\n\n` blank line so it
reads as a "See also" note rather than part of the main prose.

**Neo4j-direct, not source-file edit.** The 27001 curation source
is fragmented across `tier1_iso_controls.py` (18 leaves),
`enrich_from_standards.py` (fallback path), and defaults from
`obligation_text`. A dedicated backfill script (like Ship 8'.a's
markdown backfill) is the cleanest injection point — the citations
are static pointers, not iterative curator content.

**Idempotent by fingerprint.** Script checks for the string
`[Related guidance:` in existing `business_description` and skips
if present. Safe to re-run.

## What surfaces where

The citation footer now shows on:

- **Evidence Package** "What this is about" section — auditor-
  facing prose routed through the `evidence_prose` output-gateway
  surface. Verified: gateway preserves the citation intact
  (Ship 7'.c humanize chain doesn't strip square brackets).
- **External API** `/posture/{ref}` drill-in — same field.
- **Neo4j queryable state** — future retrieval / Signal C /
  fingerprint index that pulls business_description sees the
  pointer.

Does NOT surface on:

- **Chat digest** — `rag/casefile/digest.py::_render_obligations`
  prefers `obligation_text` over `business_description` in its
  fallback chain (line 240-244). Most ISMS clauses have
  populated `obligation_text` so the LLM doesn't see the
  citation footer at chat time. This is acceptable — chat
  content is derived from the raw standard clause + curated
  MUSTs; the citation stub is auditor + curator infrastructure,
  not chat prompt fuel. Ship 13+ curated content will land in
  MUSTs proper.

## Impact on eval baseline

No code paths changed. The citation is pure data (Neo4j
`business_description`). Chat digest doesn't consume the field
by default (obligation_text priority). Eval should be unchanged.

Full eval suite run: 225/226 PASS + 1 WARN + 0 FAIL — matches
Ship 9' / Ship 11' baseline. No regressions.

## Ship 12 progress

| Sub-arc | Status |
|---|---|
| 12'.a Grounding audit memo | ✓ |
| 12'.b Standards enrollment + vocab | ✓ |
| **12'.c Citation stub backfill** | **✓ (this doc)** |
| 12'.d Arc retrospective | next |

## Deferred (still awaiting source texts)

- MUST-level enrichment on 6.1.2 / 6.1.3 from 27005 (methodology
  declaration, likelihood-consequence matrix, acceptance criteria,
  register schema)
- MUST-level enrichment on 9.1 from 27004 (KPI selection framework,
  information-need → measure → decision chain)
- MUST-level enrichment on 27003 across ISMS clauses (context
  workshop patterns, scope-boundary documentation, competence
  planning specifics)
- § pointers on individual citations once texts land
- Chat digest promotion — either flip priority in
  `_render_obligations` or land 27003/27004/27005 obligation_text
  as separate `guidance:` lines

## Related

- [[ship-12-prime-a-iso27000-grounding-audit-2026-07-21]] — audit + design
- Ship 12'.b commit `24c936d` — standards registry + vocab
- [[dejargonize-ux-pass-2026-07-01]] — output-gateway surface conventions
- [[ship-7-prime-c-mixed-site-migration-2026-07-19]] — `evidence_prose` surface
