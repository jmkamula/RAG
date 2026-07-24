---
name: ship-23-prime-c-role-grouped-surface-2026-07-24
description: "Ship 23'.c — role-grouped chat surface (## Programs / ## Extensions / ## Obligations sections) via deterministic Neo4j composition from Ship 23'.b's structural edges"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 23'.c — role-aware chat surface end-to-end. Backend +
frontend + prose deliver role-labeled sections
(`## Programs` / `## Extensions` / `## Obligations` /
`## Management-system clauses` / `## Related controls`) via
deterministic Neo4j composition from the structural edges
Ship 23'.b filled. Commit `fb2d087`.

## Backend (rag/casefile/answer_augment.py)

### fetch_cross_role_neighbors(refs)
New Neo4j helper returning every cross-standard neighbor of a
set of refs. Rows: `{source_ref, neighbor_ref,
neighbor_standard_id, neighbor_title, edge_type, direction}`.
Direction is `outbound` or `inbound` (both matter because
SUPPORTS is authored one-way ext→program but the program
query wants inbound). Deterministic single query; silent-fail.

### _classify_relation extended (role-aware slugs)
Legacy `demonstrated_by` label collapsed program + extension
into one bucket. Ship 23'.c splits by role via `cf.role_of()`:
- `program` — cross-standard ref whose owning standard is
  program-role (ISO 27001, etc.)
- `extension` — cross-standard ref whose owning standard is
  extension-role (ISO 27701, etc.)
- `obligation` — cross-standard ref whose owning standard is
  obligation-role (GDPR, NIS2, etc.)
- `cross_framework_bridge` fallback for role_of=unknown
- `isms_clause` unchanged (same-standard 4.x-10.x)
- `context` for same-standard sub-articles

Applied to BOTH demonstrator refs AND generic cross-standard
neighbors — the role model wins over the historical
DEMONSTRATED_BY overlay semantic.

### _relation_display + _relation_display_for
Role-aware labels: "Program (implementing standard)",
"Extension (privacy overlay)", "Obligation (legal/regulatory)".

### build_related_cards changes
1. **primary_ref normalisation** — LLM sometimes emits
   `"GDPR Art. 32"` instead of canonical `"Art.32"`. Without
   normalisation the classifier misses primary_sid and every
   cross-role card falls through to `context`. Now normalised
   via `_refs_in(raw_primary)` and written back to the intro
   so downstream (frontend chip, SDK) see the canonical form.
2. **Auto-inject cross-role neighbors** via
   `fetch_cross_role_neighbors(list(cited))` — mirrors Ship
   22'.d demonstrator auto-inject, extended to the extension
   + program directions (SUPPORTS inbound for programs;
   SUPPORTS outbound for extensions; DEMONSTRATES/IMPLEMENTS
   both directions for obligations).
3. **Neighbor metadata caching** — fetch results also carry
   title + standard_id, cached for short-circuit
   CaseFileShim path (no resolver nodes) to render cards
   with metadata.

### Card ordering (Ship 23'.c updated _ORDER)
primary → program → extension → obligation → demonstrated_by
→ cross_framework_bridge → isms_clause → context.

### structured_to_prose (role-labeled sections)
Split the previous `## Related controls` monolithic section
into role-labeled sections:
- `## Programs` — cards with relation=program
- `## Extensions` — cards with relation=extension
- `## Obligations` — cards with relation=obligation
- `## Management-system clauses` — cards with
  relation=isms_clause
- `## Related controls` — everything else (context,
  cross_framework_bridge)

Sections omitted when their group is empty. Primary card
renders without a header (it's the auditor's own focus).
`demonstrated_by` cards route to the appropriate role bucket
via each card's `role` field (for legacy compat).

## Frontend (static/arioncomply.html)

`renderStructuredAnswer` groups cards into visual sections
matching the prose structure. Same section keys + headers;
per-card render unchanged from Ship 19'.c.

## Bug fix (rag/casefile/digest.py:344)

Pre-existing `NoneType.lower()` at digest.py:344.
`dict.get(k, default)` returns `None` when the key exists
with value `None`; the new SUPPORTS edges Ship 23'.b added
populate `via_edge=None` for some entries, tripping this on
Art.32 queries. Fix: `(src.get("via_edge") or "").lower()`.
Trivial one-char change; surfaced only because Ship 23'.b
increased the neighbor density.

## Verified end-to-end

- **A.5.34** (program query — Privacy and protection of PII):
  Primary + **21 Extensions** (all A.7.x + B.8.x that
  SUPPORTS A.5.34 post Ship 23'.b) + 7 Obligations (Art.15-21
  data subject rights) + 2 ISMS clauses (10.1/10.2).
- **A.7.2.6** (extension query — Contracts with PII
  processors): Primary + 4 Programs (A.5.19/20/22/36 supplier
  family) + 2 Obligations (Art.5/Art.28) + 1 ISMS clause (7.5).
- **Art.32** (obligation query — Security of processing):
  Primary + **22 Programs** (including newly-added
  A.8.1/6/17-19/21-23/28/30-34/4/5 from Ship 23'.b) + 4
  Extensions (A.7.2.1/A.7.4.5/A.7.4.9/B.8.2.2) + 2 Related
  (Art.27 sibling + Art.32.1.d sub-article).
- **primary_ref normalisation**: LLM emitted `"GDPR Art. 32"`
  → chat displays canonical `"Art.32"` ✓.

## Eval

Full eval: **231/232 PASS + 1 WARN (#200) + 0 FAIL** —
identical to Ship 15'.e / 18'.c / 19'.d / 20'.e / 21'.c /
22'.d baselines. Zero regression from role-grouped surface +
curation fill.

## Codified property

Role split is now FIRST-CLASS in the chat UI — sections are
role-labeled, not just a per-card badge. This is the visible
expression of the framework-role-model-arc that Ship 14
codified structurally. Deterministic augmentation via
`fetch_cross_role_neighbors` + `_classify_relation` reads
the structural edges Ship 23'.b filled; no LLM emission of
role metadata.

## Ship 23 progress

| Sub-arc | Status |
|---|---|
| 23'.a Audit + gap report | ✓ (3a730d1) |
| 23'.b Fill 55 edges | ✓ (cf7e417) |
| **23'.c Role-grouped chat surface (this)** | **✓ (fb2d087)** |
| 23'.d Eval + retro | next |

## Related

- [[ship-23-prime-a-audit-2026-07-24]] — audit
- [[ship-23-prime-b-curation-fill-2026-07-24]] — the fills
  that made this surface data-rich
- [[framework-role-model-arc]] — the role model this surface
  makes user-visible
- [[ship-19-prime-arc-retrospective-2026-07-23]] — card
  polish that this arc's sections render into
- [[ship-22-prime-arc-retrospective-2026-07-24]] — the arc
  whose demonstrator auto-inject Ship 23'.c extended to the
  extension + program directions
