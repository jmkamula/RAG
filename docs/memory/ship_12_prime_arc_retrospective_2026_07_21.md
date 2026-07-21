---
name: ship-12-prime-arc-retrospective-2026-07-21
description: "Ship 12' arc retrospective — ISO 27000-family grounding expansion; 3 sub-arcs + closer; audit + enrollment stub within source-text constraint"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 12' arc — ISO 27000-family grounding expansion. Answers the
user's direct question: "we have used 27002 for Implementation
guidance for the Annex A controls, what is our grounding regarding
27003 — Guidance on the management-system clauses, 27004 —
Monitoring, measurement, analysis, evaluation and especially
27005 risk register — Guidance on managing information security
risks? are we missing something?"

Answer verified in 12'.a: **yes, all three guidance standards
were absent** (0 codebase refs). Ship 12 closes that gap within
the constraint that source texts are not available.

**Arc window:** 2026-07-21. 3 sub-arcs + closer, single day.

## Sub-arc inventory

| Sub-arc | Delivery | Commit |
|---|---|---|
| 12'.a | Audit memo — 0 refs to 27003/27004/27005; enumerated 38 unique target leaves across 3 guidance families | `24c936d` (combined with 12'.b) |
| 12'.b | Enrollment — `schema_v84` inserts 3 guidance rows into `standards`; `rag/output/vocab/iso2700{3,4,5}_*.json` register display conventions for output gateway | `24c936d` |
| 12'.c | Citation stub backfill — `scripts/backfill_iso27000_guidance_citations.py` appends `[Related guidance: …]` footer to 38 Neo4j leaves' `business_description`; idempotent | `2b143b2` |
| **12'.d Arc retrospective** | **This doc** | (next commit) |

## What ships from Ship 12'

**Registry surface:**
- 3 new rows in `standards` table (ISO27003:2017 / 27004:2016 /
  27005:2022) with `role='guidance'` + `standard_type='code_of_practice'`.
- 3 new vocab JSON files in `rag/output/vocab/` — display names,
  short names, § conventions. Gateway now humanizes the new
  standard IDs anywhere they surface.

**Data surface:**
- 38 Neo4j `RequirementNode.business_description` values enriched
  with authority-citation footers. Surfaces on Evidence Package
  "What this is about" + external API `/posture/{ref}` drill-in.

**Tooling:**
- `scripts/backfill_iso27000_guidance_citations.py` — one-shot,
  idempotent, dry-run capable. Documents the target-leaf mapping
  as data (not scattered magic strings).

**Schema:**
- `schema_v84_ship12b_iso27000_guidance_enrollment.sql`

**Documentation:**
- 4 memos (12'.a audit, 12'.c citations, this retro, + implicit
  12'.b via 12'.a target list).

## What did NOT ship (deferred to Ship 13+)

Scope discipline held — the whole arc was framed as "audit +
enrollment + citation stubs" precisely because full MUST-level
curation requires the source texts. The user picked that
constrained scope in 12'.a AskUserQuestion. Deferred:

1. **MUST-level enrichment from 27005** on 6.1.2 / 6.1.3 / 8.2 /
   8.3 — methodology declaration, likelihood-consequence matrix,
   risk-acceptance criteria, register schema, ownership register,
   review triggers.
2. **MUST-level enrichment from 27004** on 9.1 + monitoring-
   adjacent Annex A — KPI selection framework, information-need
   → measure → decision chain, presentation cadence.
3. **MUST-level enrichment from 27003** across ISMS clauses —
   context workshop patterns, scope-boundary documentation,
   competence planning specifics.
4. **§ pointers on individual citations** once texts land. Current
   citations are standard-level only.
5. **Chat digest promotion** — either flip
   `_render_obligations` priority (obligation_text →
   business_description), or land guidance obligation_text on
   separate `guidance:` line so LLM sees authority attribution
   at chat time. Today it only surfaces on auditor-facing
   surfaces.
6. **Chroma collections** for each guidance standard (queryable
   for retrieval), following the ISO 27701 pattern.
7. **Eval cases** citing guidance (chat asks "risk methodology
   per 27005" → citation surfaces in answer).

## Codified lessons

### 1. Enrollment stubs beat waiting

The temptation was to defer *everything* until texts land. Ship
12 instead delivered a thin, non-breaking layer that makes the
system *aware* of the guidance standards. Now:

- Output gateway recognises the new IDs
- External API can list the guidance rows in `/frameworks`
- Evidence Package auditor prose points at the right authority
- Future curator arc doesn't have to litigate "is this standard
  enrolled?" — it starts from an existing row

The pattern generalises: **when downstream code needs to
recognise a new entity but the entity's content isn't ready,
stub the registry entry first**. Cheap; unblocks parallel work.

### 2. Data-only changes preserve the LLM safety envelope

Ship 12'.c added text to 38 Neo4j nodes but didn't change any
code path. The eval was unaffected (225/226 unchanged) because
the chat digest doesn't consume `business_description` when
`obligation_text` is populated. Auditor surfaces do consume it.

That's the right layering: **speculative content lands on
auditor-facing prose surfaces first, chat surfaces only after
the content is curator-verified**. The chat digest's
`obligation_text` priority acts as an implicit gate against
premature guidance leaking into LLM prompts.

### 3. Section-level pointer discipline

The 12'.a memo proposed `[Guidance: ISO 27005:2022 §7-8]` style
citations. 12'.c dropped § specificity because we don't have
the source texts — a wrong § pointer would be worse than none.
The final format is standard-level: `[Related guidance: ISO
27005:2022]`.

**Lesson**: don't publish specificity you can't verify. It's
easier to add § pointers later (per-leaf, from real texts) than
to backfill-correct wrong ones from auditor-visible prose.

### 4. Verify the gap before proposing the fix

Ship 12'.a spent time proving the gap empirically (grep for
"27003", "27004", "27005" across the codebase; check `standards`
table). All returned zero. That's what unlocked the scoping
question — is this a design decision (we chose to ignore them),
a rollout gap (we haven't gotten to them yet), or a legit hole
(never on radar)? Answer: legit hole. That framing made the
scoping conversation short.

Pair-rule with [[ship-8-prime-arc-retrospective-2026-07-20]]'s
"verify data-driven hypotheses BEFORE building". Same principle,
different direction: verify absences (Ship 12) as thoroughly as
you verify presences (Ship 8).

## What surfaced from the arc

- **Two paths for `business_description` population** —
  `enrichment/tier1_iso_controls.py` covers 18 explicit refs;
  `enrichment/enrich_from_standards.py` fills fallback from
  obligation_text truncated to 500 chars. Most ISMS clauses are
  on the fallback path. Curator work should promote them to
  explicit tier1 entries when texts land.
- **Chat digest priority** — `_render_obligations` prefers
  `obligation_text` over `business_description`. That's a hard
  design choice; the citation stubs from 12'.c don't reach chat
  by design. When 27003/27004/27005 land properly, the design
  question becomes: separate `guidance:` line, or promote
  business_description priority? Design decision deferred.
- **Standards table already had `role='guidance'`** — the schema
  was ready. 12'.b was just data insertion, no schema evolution
  needed. Ship 7'.b's framework-role-model discipline paying off.

## Baseline throughout

225/226 PASS + 1 WARN + 0 FAIL. Chat-side eval unchanged. Ship
12 introduced zero code-path risk.

## Ship 12' close

| Sub-arc | Status |
|---|---|
| 12'.a Grounding audit memo | ✓ |
| 12'.b Standards enrollment + vocab | ✓ |
| 12'.c Citation stub backfill | ✓ |
| **12'.d Arc retrospective** | **✓ (this doc)** |

Total: 3 delivery sub-arcs + closer, all in one day. Shortest
Ship arc yet, matched with Ship 5' and Ship 8' (though Ship 8'
dropped one sub-arc, this arc completed all four cleanly).

## Related

- User's opening question (2026-07-21) — grounding audit request
  after Ship 11 close
- [[ship-12-prime-a-iso27000-grounding-audit-2026-07-21]] —
  audit + design
- [[ship-12-prime-c-iso27000-citation-stubs-2026-07-21]] — citations
- [[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] — the
  vocabulary-as-data infrastructure Ship 12'.b reused
- [[ship-8-prime-a-markdown-backfill-2026-07-20]] — the one-shot
  backfill script pattern Ship 12'.c reused
- Ship 13+ candidate: full MUST-level curation from 27003 /
  27004 / 27005 source texts once available
