---
name: ship-24-prime-arc-retrospective-2026-07-24
description: "Ship 24' arc closer — ISO 27001 cross-role coverage 55.6% → 92.9% linked via 59 new edges; codified 'catalog is tenant-agnostic' discipline that reframed 'defensible' from Arion-shaped to structural"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 24' arc retrospective — 3 sub-arcs across one day
(2026-07-24) completing the ISO 27001 cross-role coverage
that Ship 23'.b started. Every ISO 27001 control that has a
real cross-role relationship now has an authored edge; the 9
remaining unlinked are structurally defensible container
refs + one non-PII control.

The user's mid-arc reframe was arc-defining: **the catalog
is tenant-agnostic**. What looks "defensible" through demo-
tenant reasoning may be a real gap for a bank / hospital /
manufacturer onboarding next month.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 24'.a | Design memo + explicit mapping table (revised mid-arc from ~35 to ~54 edges after user challenge) | c37e960 |
| 24'.b | 59 edges across 5 batches + Neo4j load | c37e960 |
| **24'.c** | **Eval + retrospective (this doc)** | pending |

## The user's reframe

Initial Ship 24 plan (~35 edges): fill A.5 + A.6 + ISMS-with-
obvious-ties. **User challenge**: "A.7 is N/A for Arion but
it is a valid candidate for many, am I getting this wrong?"

I was applying tenant-specific reasoning to a catalog
decision. A.7 physical + ISMS 4-5 Context/Leadership ARE
real gaps in the standards — cloud-only demo obscured this,
but the catalog serves every tenant.

Same reframe applied to ISMS 4-5: those clauses have Art.24
accountability relationships even if they're process-shaped.

Post-reframe scope: **59 edges** (not 35). Ship 24'.b
delivered.

## Coverage trajectory across Ship 23 → 24

| Milestone | ISO 27001 linked |
|---|---|
| Pre-Ship-23 | 55/126 (44%) |
| Post-Ship-23'.b (A.8 + 27701 parent) | 70/126 (55.6%) |
| Post-Ship-24 initial mapping (~54 edges) | 112/126 (88.9%) |
| **Post-Ship-24 completeness (59 edges)** | **117/126 (92.9%)** |

Neo4j edges: 670 → 725 → 779 → 784.

## 5 batches, 59 edges

1. **A5_A6_ISMS_GDPR_EDGES (27)** — original scope. A.5 org
   10 + A.6 people 4 + ISMS 6-10 with obvious GDPR ties 13.
   Every edge cites Art.24 accountability / Art.32 security /
   Art.25 privacy-by-design / Art.35 DPIA / Art.30 RoPA /
   Art.13 transparency / Art.29 controlled processing / Art.39
   DPO tasks / Art.33 breach notification / Art.5 principles.
2. **A7_PHYSICAL_GDPR_EDGES (12)** — every A.7 physical
   control → Art.32 with the right leg (confidentiality /
   integrity / availability). Added post-user-reframe.
3. **ISMS_CONTEXT_LEADERSHIP_GDPR_EDGES (7)** — ISMS 4-5
   Context + Leadership → Art.24 accountability (+ 5.3 → Art.37
   DPO designation). Added post-user-reframe.
4. **SHIP24_COMPLETENESS_EDGES (5)** — post-first-audit surfaced
   5 controls missed by the mapping table (7.1 Resources, 8.2/
   8.3 Risk assessment/treatment, 10.2 NC/corrective, A.7.9
   Off-premises). Each has clear GDPR relevance.
5. **ISO27701_WEAK_TIES_EDGES (8)** — SUPPORTS edges tying
   existing 27701 extensions to 27001 controls where PII overlay
   is real but the extension standard was designed additive not
   annotative (identity, auth, incident learning, deletion,
   contract-adjacent).

Each edge carries rationale + citation. Neo4j idempotent
merge — safe to re-run.

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to
Ship 15'.e / 18'.c / 19'.d / 20'.e / 21'.c / 22'.d / 23'.c
baselines. Zero regression from 59 new edges.

Sanity check: adding cross-role edges means the role-grouped
chat surface (Ship 23'.c) now surfaces MORE cards on obligation
queries + on any ISO 27001 program query. Ship 22'.d
demonstrator auto-inject + Ship 23'.c neighbor fetch handle
the additions automatically. No code changes needed in this
arc — just data.

## The remaining 9 unlinked (all defensible)

**8 umbrella clause refs (structural)**:
`4`, `5`, `6`, `6.1`, `7`, `8`, `9`, `10` — container refs
for their sub-clauses; edges belong on `4.1/4.2/4.3/4.4`,
`5.1/5.2/5.3`, etc. — which are all now linked.

**1 A.5.32 Intellectual property**: IP protection is scoped
to the org's own IP (trade secrets, patents), not personal
data. No natural GDPR overlay.

Post-Ship-24, "why is X unlinked?" has a defensible answer for
every remaining control.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | REINFORCED — 27 new obligation-role bridges + 13 program-role bridges from A.7 + 8 program→extension SUPPORTS. All flow through Ship 23'.c's role-grouped surface. |
| Parallel CaseFile view? | YES — no digest changes; edges are structural metadata read at composition time. |
| Deterministic routing? | YES — no LLM emission of role metadata; cf.role_of() + fetch_cross_role_neighbors handle everything. |
| Guidance-normative discipline? | YES — every edge cites source standard clause. |

## Codified 4 lessons

### 1. The catalog is tenant-agnostic

Ship 23'.d's retrospective codified "audit-first prevents
empty-section UX". Ship 24 codified the deeper discipline:
**what's defensibly unlinked has to be defensible in
STANDARDS terms, not TENANT terms.** Arion is cloud-only so
A.7 was legitimate N/A on their posture — but the standard
still says A.7 physical demonstrates Art.32. A bank / hospital
/ manufacturer tenant would see empty `## Obligations`
sections on their A.7 queries if the edges don't exist.

Rule: when curating cross-role edges, ask "does the RELATIONSHIP
exist in the standards?" not "does the DEMO have this in
scope?". Save the tenant-specific applicability for the
posture engine, not the graph.

### 2. Explicit mapping tables prevent audit gaps

Ship 24'.a wrote out every source→target→rationale before
implementation. Even so, the first-run audit surfaced 5
controls missed by the table (7.1/8.2/8.3/10.2/A.7.9). Written
tables help but aren't perfect — always re-audit after
implementation, treat the audit as the source of truth.

### 3. Same discipline scales linearly

Ship 23'.b batched 55 edges. Ship 24 batched 59. Same
authoring cadence, same citation format, same commit shape.
Curation-fill arcs are now a repeatable pattern:
- audit → identify gaps
- explicit mapping table with rationales
- author edges in a new named batch in relationship_catalog.py
- load_to_neo4j.py + re-audit
- eval regression check
- retro

The pattern scales to whole new standards (ISO 27002 §5.x
integration, SOC 2 CC-series enrollment, DORA articles)
without needing new tooling — just new edges.

### 4. User challenges reframe scope more than any prompt

Twice in Ship 23-24, user pushback (once on text enrichment,
once on tenant-N/A) fundamentally changed the arc:
- Ship 23 user reframe: "deterministic composition beats
  text enrichment" — cut Gap 2 (49 nodes of text authoring)
  entirely.
- Ship 24 user reframe: "catalog is tenant-agnostic" — grew
  the batch from 35 to 59 edges.

Both times the reframe made the arc BETTER: cleaner scope in
Ship 23, more honest coverage in Ship 24. Lesson: propose the
plan, but leave room for the user to catch the tenant-vs-
catalog / narrative-vs-structure distinctions I might miss.

## What Ship 24 did NOT do

- **Fill A.5.32 Intellectual property.** No PII overlay; IP
  is a different data class. Keeping unlinked is honest.
- **Retire the umbrella clause refs** (4/5/6/7/8/9/10 without
  sub-numbers). These serve as navigation nodes in the graph;
  edges belong on sub-clauses.
- **Update the chat prompt.** No prompt changes — Ship 23'.c's
  role-grouped surface reads the new edges directly.
- **Change the UI.** Same Ship 23'.c render; more cards now
  populate the sections.
- **Fill GDPR sub-articles.** GDPR (obligation) coverage stayed
  at 17% because most nodes are sub-articles (Art.5.1.a etc.)
  that inherit from parents. Article-level coverage is the
  right granularity for now.

## Ship 24 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 24'.a | Design + mapping table (revised mid-arc via user reframe) | 59-edge scope locked with rationales + citations |
| 24'.b | 5 batches in relationship_catalog.py + Neo4j load | Edges 725 → 784; ISO 27001 55.6% → 92.9% linked |
| **24'.c** | **Eval + retrospective (this)** | **231/232 PASS + 1 WARN + 0 FAIL confirmed; arc closed** |

## Related

- [[ship-23-prime-arc-retrospective-2026-07-24]] — arc whose
  audit + first-batch fill this arc completes
- [[ship-23-prime-b-curation-fill-2026-07-24]] — pattern this
  arc extended
- [[ship-24-prime-a-bridge-design-2026-07-24]] — design memo
  with explicit mapping table
- [[framework-role-model-arc]] — role model whose ISO 27001
  edges are now near-complete
