---
name: ship-68-prime-arc-2026-08-13
description: "Ship 68'.a Phase 0 — scope_items schema + writer scope-aware filter + curator CLI. Ships bridge_writer's ability to honor per-MUST-pair scope when authored, cross-product fallback otherwise. Zero existing behavior change; unblocks 68'.b pilot + 68'.d bulk authoring."
metadata:
  type: project
  ship: "68'"
---

# Ship 68'.a — scope_items schema + writer + curator tooling

## What the investigation surfaced

Ship 67' fixed a terminology collision but Ship 68'.a's dogfood
investigation exposed a deeper issue: Ships 60–62's bridge-
attribution UX built numeric coverage claims on top of a data
model that only knows *whole-source-control → whole-target-control*.
Ship 59'.b's writer cross-products every satisfied source MUST with
every target MUST, so counts like `(N/M MUSTs bridge-covered)` are
trivial restatements of `(target.n_total − target.n_satisfied)`.

**But** the graph also carries **curator-authored rationale** on
100% of bridge edges (452 total: 258 IMPLEMENTS + 158 SUPPORTS +
22 ENABLES + 14 GOVERNANCE). Sample rationales:

- `A.5.18 → Art.32`: *"Access rights management implements Art.32.1.b
  ongoing confidentiality of processing systems."*
- `A.8.13 → Art.32.1.c`: *"Information backup is the primary
  technical control for restoring personal data availability."*

The rationale is *specific* — often pointing to a sub-clause. The
missing piece is per-MUST-pair `scope_items`: which source MUSTs
specifically implement which target MUSTs.

## The arc plan

| Ship | Deliverable | Est |
|---|---|---|
| **68'.a Phase 0** | Schema + writer scope-aware + curator CLI. Zero behavior change on unauthored edges. | shipped this commit |
| 68'.b Pilot | Author scope_items for ~7 Art.32 bridges. Validate model on Arion. | ~2-3 hrs (curator time) |
| 68'.c Reader migration | Digest DEMONSTRATED BY: use pair-specific counts + rationale when authored; honest fallback otherwise. Retire Ship 60'.j's coverage suffix. | ~1 day |
| 68'.d Bulk authoring | Remaining ~450 edges. LLM-assisted with curator review is the realistic path. | multi-week |
| 68'.e Full migration | Once ≥90% authored, migrate all readers (SPA chip, Evidence Package) + retire cross-product fallback. | ~2 days |

## 68'.a delivered

**Schema (Neo4j property, no DDL required)**

Bridge edges gain an optional `scope_items` property:
```
[
  {"sr": "item:A.5.18:asset_owner_authorization", "tg": "item:Art.32:reg_owner"},
  {"sr": "item:A.5.18:least_privilege",           "tg": "item:Art.32:reg_measures"}
]
```

Stored as a list of JSON-encoded strings (Neo4j's homogeneous-
array constraint on properties). The reader helper
`rag/posture_loader._parse_scope_items` accepts both the on-disk
list-of-string shape and (defensively) list-of-dict, so future
tooling can write either.

**Writer (`_persist_bridge_coverage` in `rag/posture_loader.py`)**

For each bridge edge:
- If `scope_items` is populated: emit `bridge_coverage` rows only for
  pairs where the source MUST is satisfied AND the target MUST is in
  scope. Bad-entry defensiveness: malformed pairs are silently
  skipped; if zero pairs parse, the edge falls back to cross-product
  so a bad blob doesn't lose attribution.
- Otherwise: existing cross-product behavior (each satisfied source
  MUST × each target MUST × edge type).

**Curator CLI (`scripts/curation/scope_items_editor.py`)**

Four commands:
- `list [--unscoped] [--short]` — full edge inventory + scope
  progress. Currently 0 of 452 edges scoped.
- `show <src_id> <edge> <dst_id>` — read-only inspection of one
  edge's rationale + scope_items.
- `edit <src_id> <edge> <dst_id>` — interactive session showing
  source MUSTs + target MUSTs (numbered) + current pairs; commands
  `s<N> t<M>` add pair, `del s<N> t<M>` remove, `save` / `quit`.
- `validate` — assert every authored `scope_items` reference
  points to a real MUST id on both sides. Exits non-zero on any
  invalid ref.

## Verification (Arion demo)

1. **Baseline**: bridge writer produces 40,018 rows (Ship 59'.d
   count preserved).
2. **Test author**: added 2 scope_items pairs to
   `A.5.18 IMPLEMENTS Art.32` (`asset_owner_authorization →
   reg_owner`, `least_privilege → reg_measures`) via direct Cypher.
3. **After rebuild**: `A.5.18 IMPLEMENTS Art.32` produces exactly
   2 bridge rows (matched the authored pairs, dropped the other 318
   cross-product combinations).
4. **Rollback**: removed the test scope_items; edge falls back to
   320 cross-product rows.

Round-trip: authored → filtered → rolled back → cross-product
restored. Behavior change is opt-in per edge.

## What Ship 68'.a costs

- Schema migrations: 0 (Neo4j property)
- Wall clock: ~2 hrs (design + writer + CLI + tests)
- Files touched: 2 (`rag/posture_loader.py`,
  `scripts/curation/scope_items_editor.py` NEW)
- Lines: ~360 (writer scope-aware ~60; parser helper ~40; CLI ~260)
- Eval regression: none (zero behavior change on unauthored edges,
  which is currently every edge on all tenants).

## Codified lesson

### 32. Data-model assertion granularity ≠ UX assertion granularity

Ships 60–62 designed UX around a claim (*"your ISO covers N of
your GDPR obligations"*) that presumed per-MUST-pair semantic
mapping. The data model held only whole-control-to-whole-control
edges + rationale text. The gap surfaced in dogfood
(*"the 40% false-alarm rate"*) and again in the Ship 68'
investigation (*"the number was a fake proxy"*). The retrofit is
scope_items authoring — but the lesson is prospective: when
designing a UX narrative, walk the data model's assertion
granularity first. If your claim is at finer granularity than
the model's edges, either add authoring capacity (this arc) or
frame the UX at the model's actual granularity.

## Follow-ons

- Ship 68'.b (pilot) — author scope_items for Art.32's ~7
  incoming bridges. Compare Art.32 chat digest pre- vs post-
  authoring on Arion.
- Ship 68'.c (reader migration) — DEMONSTRATED BY section renders
  scope-aware counts + rationale; XFW BRIDGES retires Ship 60'.j's
  suffix.
- Retire H4 and part of C1 from the dogfood punchlist once 68'.c
  ships (they become curator-authoring problems, not code
  problems).
