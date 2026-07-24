---
name: ship-23-prime-arc-retrospective-2026-07-24
description: "Ship 23' arc closer — role-aware chat surface end-to-end via audit-first + structural curation fill + deterministic composition; 55 new edges, role-grouped sections, 231/232 baseline held"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 23' arc retrospective — 4 sub-arcs across one day
(2026-07-24) delivering the role-aware chat surface via
audit-first curation + deterministic composition. Every chat
response with cross-role relatives now surfaces them in
role-labeled sections. The framework-role-model that Ship 14
codified structurally is now user-visible in every chat turn.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 23'.a | Audit script + gap report | 3a730d1 |
| 23'.b | Fill 55 structural edges (Gap 1 + Gap 3) | cf7e417 |
| 23'.c | Role-grouped chat surface + Neo4j composition | fb2d087 |
| **23'.d** | **Retrospective (this doc)** | pending |

## The user's ask

> "when there is an ISO 27001, the intro should not contain a
> control, it should just carry a summary of the status
> followed by cards with per MUST status. we should also see
> where it has EXTENSIONS and or OBLIGATIONS. the same should
> be for EXTENSIONS eg an ISO 27701 query should surface an
> intro, cardwise control treatment and the touched PROGRAMS
> and OBLIGATIONS. An OBLIGATION query follows the same
> pattern, eg for GDPR: intro, cardwise Art. and related
> PROGRAMS and EXTENSIONS. for this to come out without
> relying on LLMs, we need to audit our curated texts and see
> if there is a gap in bringing out these relations and if we
> can extend the system with our case file architecture and
> without bloating the prompt"

Two threads bundled:
1. Audit curation for cross-role gaps
2. Redesign chat surface as role-aware

User pushed back on my initial "fill text enrichment" plan —
correctly noting that adding narrative to `cross_framework_
summary` would bloat the digest AND that if we can compose
relationships deterministically from structural edges, we
don't need the text. That reframing was arc-defining.

## Audit findings (Ship 23'.a)

Read-only `scripts/audit_cross_role_edges.py` surveyed:

| Standard | Nodes | Linked | Coverage |
|---|---|---|---|
| ISO 27701 (extension) | 49 | 49 | 100% |
| ISO 27001 (program) | 126 | 55 | 44% |
| GDPR (obligation) | 303 | 51 | 17% |

Text enrichment surprise: **ISO 27701 has 0/49
`cross_framework_summary`** while ISO 27001 + GDPR are both
100/100%. Asymmetric loading omission from Phase 2.

Three concrete gaps identified:
- **Gap 1** — ISO 27701 SUPPORTS → parent ISO 27001 edges:
  only 26 of 49 extensions had a documented parent (23
  extensions unlinked).
- **Gap 2** — ISO 27701 `cross_framework_summary` text field:
  0/49.
- **Gap 3** — A.8 Tech GDPR bridges: 15/34 unlinked (44%).

## Curation fill (Ship 23'.b) — 55 structural edges

**Gap 1** (`ISO27701_BATCH4_PARENT_EDGES`): **40 SUPPORTS
edges** across the 30 previously-unlinked extensions.
Mapping strategy: controller-side (A.7.2.x, A.7.3.x, A.7.4.x)
→ A.5.34 primary parent (Privacy and protection of PII, ISO
27001 privacy anchor); processor-side (B.8.x) → A.5.19/A.5.20
supplier controls; specific secondaries where the clause text
made the relationship explicit (A.5.31 legal, 6.1.2 risk,
A.5.9 records, A.8.10 deletion, A.5.14 transfer).

Coverage: **26 → 66 SUPPORTS edges; 53% → 100% extensions
with parent**.

**Gap 3** (`A8_TECH_GDPR_BRIDGE_EDGES`): **19 DEMONSTRATES
edges** across the 15 unlinked A.8 tech controls. Every A.8
tech control DEMONSTRATES at least Art.32 (Security of
processing); A.8.28 secure coding + A.8.31 environment
separation also DEMONSTRATES Art.25 (Privacy by design);
A.8.30 outsourced development also DEMONSTRATES Art.28
(Processor); A.8.33 test information also DEMONSTRATES
Art.5 (Purpose limitation).

Coverage: **A.8 unlinked 15/34 (44%) → 0/34 (0%);
ISO 27001 total linked 44% → 55.6%**.

**Gap 2 skipped** per user directive — deterministic
composition from Gap 1 + Gap 3 fills gives the same UX
outcome without ~10-25KB of text-bloat in the digest.

## Role-grouped surface (Ship 23'.c)

**Backend** — `fetch_cross_role_neighbors(refs)` new Neo4j
helper returning every cross-standard neighbor. Wired into
`build_related_cards` alongside the demonstrator auto-inject.
`_classify_relation` extended with role-aware slugs
(`program` / `extension` / `obligation`) replacing legacy
`demonstrated_by`. `primary_ref` now normalised via
`_refs_in()` so LLM's `"GDPR Art. 32"` becomes canonical
`"Art.32"` — without this fix, the classifier missed
primary_sid and every cross-role card fell to `context`.

**Prose** — `structured_to_prose` splits the previous
monolithic `## Related controls` into role-labeled sections:
`## Programs` / `## Extensions` / `## Obligations` /
`## Management-system clauses` / `## Related controls`.
Sections omit when empty; primary card renders without a
header.

**Frontend** — `renderStructuredAnswer` groups cards into
visual sections matching the prose structure. Same
per-card render (leaf checklist, verdict badge, drill-in)
from Ship 19'.c.

**Bug fix** — Pre-existing `NoneType.lower()` at
digest.py:344 surfaced by new SUPPORTS edges populating
`via_edge=None`. One-char fix: `(src.get("via_edge") or "").lower()`.

## Verified end-to-end

- **A.5.34 (program query)**: Primary + 21 Extensions + 7
  Obligations + 2 ISMS clauses.
- **A.7.2.6 (extension query)**: Primary + 4 Programs + 2
  Obligations + 1 ISMS clause.
- **Art.32 (obligation query)**: Primary + 22 Programs + 4
  Extensions + 2 Related (Art.27 sibling + Art.32.1.d
  sub-article).

All three role directions surface deterministically without
LLM emission of role metadata.

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to
Ship 15'.e / 18'.c / 19'.d / 20'.e / 21'.c / 22'.d
baselines. Zero regression across all 3 delivery sub-arcs.

The role-grouped surface + 55 new edges + primary_ref
normalisation + NoneType fix delivered a UX shape change
without any behavioural regression on the existing 232 eval
cases. Same idiom as prior UX arcs — additive-only
composition + deterministic augmentation.

## Codified 5 lessons

### 1. Deterministic composition beats text enrichment

User's reframe of "structural edges over narrative text"
was arc-defining. The final Ship 23 surface renders roles
via `_classify_relation` reading Neo4j edges — 0 KB added
to the digest, all UX gain. Ship 22'.d already codified
"structural invariants over prose-repair"; Ship 23 extends
that to "structural composition over text enrichment".

Pattern: when the LLM is being asked to cite or describe a
relationship, ask first whether the relationship is a graph
edge. If yes, derive at composition time; if no, curate the
edge, don't teach the LLM.

### 2. Audit-first prevents empty-section UX

Path A (curation-fill before UI) was the right call. Had we
done Path B (redesign + fill on-demand), the first tenant
query on ISO 27701 would have surfaced empty `## Programs`
sections for 47% of extensions — exactly the query surface
where the new UX is most visible. The `scripts/audit_cross_
role_edges.py` tool gave 3 defined-scope gap counts (23 + 15
+ 0 skipped = ~38 curator additions) that fit inside a
single sub-arc. Investigation cost was minutes; the
alternative would have been debugging "why is this section
empty?" for weeks.

### 3. Curator batch mappings deserve documented strategy

Ship 23'.b's edge additions weren't ad-hoc — controller-side
→ A.5.34 (privacy anchor); processor-side → A.5.19/A.5.20
(supplier); A.8 tech → Art.32 (TOM). Each rationale + citation
field carries the mapping logic. Future arcs adding new
extensions or frameworks can follow the same pattern without
guessing.

### 4. LLM output format drift is a real pattern

`"GDPR Art. 32"` (with space + framework prefix) vs
canonical `"Art.32"` — the LLM emits variants despite the
prompt asking for the canonical form. Prompt tuning is
soft; deterministic normalisation is hard. `_refs_in()` was
already normalising in-text refs; extending it to
`primary_ref` on the intro was the fix.

Generalises: every LLM-emitted field that carries a
canonical identifier should be normalised before use.

### 5. Curation-side changes surface latent code bugs

The `NoneType.lower()` bug at digest.py:344 was pre-existing
but only surfaced when Ship 23'.b's new SUPPORTS edges
populated `via_edge=None` on demonstrator overlays. Rich
data → new edge cases → dormant defensive-coding gaps
appear.

The lesson isn't "test more" — it's "curation-fill can be a
diagnostic tool for hidden fragility". Watch stderr on
first-run after every catalog batch.

## What Ship 23 did NOT do

- **Fill Gap 2** (ISO 27701 `cross_framework_summary`) —
  intentional; deterministic composition covers the UX outcome.
- **Fill ISMS clauses (88% unlinked)** — defensible per
  audit; management-system clauses (4-10) have looser
  cross-framework relationships than Annex A controls.
- **Fill A.7 Physical (93% unlinked)** — Arion is cloud-only;
  low signal.
- **Cap cross-role neighbors on high-fanout queries** — Art.5
  now produces 25+ related cards; UI can scroll. Cap decision
  deferred to future arc if problematic.
- **Update the LLM prompt** — no prompt changes; Ship 23 is
  pure structural composition on the backend + role-grouped
  render on the frontend.
- **Retire the prose `answer` field** — kept for backward
  compat.

## Ship 23 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 23'.a | Read-only audit + gap classification | 3 gaps enumerated: 23+15 structural + 49 text (skipped) |
| 23'.b | Structural curation fill (55 edges) | 27701→27001 parent 53% → 100%; A.8 GDPR 56% → 100%; ISO 27001 44% → 55.6% |
| 23'.c | Role-grouped surface (backend + prose + frontend) | 3 query directions verified; 231/232 baseline held |
| **23'.d** | **Eval + retrospective (this)** | **231/232 PASS + 1 WARN + 0 FAIL confirmed; arc closed** |

## Related

- [[ship-23-prime-a-audit-2026-07-24]] — audit + gap
  classification
- [[ship-23-prime-b-curation-fill-2026-07-24]] — 55 new edges
- [[ship-23-prime-c-role-grouped-surface-2026-07-24]] — the
  visible UX shape change
- [[framework-role-model-arc]] — role model that Ship 23
  made user-visible
- [[ship-22-prime-arc-retrospective-2026-07-24]] — the
  demonstrator auto-inject pattern Ship 23 extends
- [[feedback-anchor-before-choices]] — user's audit-first
  push was the right call; codified the discipline for
  future arcs
