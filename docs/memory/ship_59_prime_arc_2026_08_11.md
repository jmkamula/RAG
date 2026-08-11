---
name: ship-59-prime-arc-2026-08-11
description: "Ship 59' arc retrospective — P/E/O SSoT with bidirectional bridge
  coverage attribution. Extends the Ship 58' single source of truth with
  framework_role denormalization (PROGRAM/EXTENSION/OBLIGATION) + a new
  posture_must_bridge_coverage table that captures per-tenant one-hop
  cross-framework bridge coverage via IMPLEMENTS/SUPPORTS/ENABLES/
  GOVERNANCE edges. Engine remains unchanged — bridge coverage is a
  parallel attribution layer, not a satisfaction substitution. Codified
  lessons: distinguish definitional vs evidence-bridging relationships;
  attribution surfaces without changing engine verdict; three properties
  (.satisfied strict, .covered opt-in, .state five-way categorical) for
  richer consumer surfaces without breaking backward compat."
metadata:
  type: project
  ship: "59'"
---

# Ship 59' — P/E/O SSoT with bidirectional bridge coverage attribution

## The arc in one sentence

Ship 59' extends the Ship 58' per-MUST SSoT to capture the framework
role model (Program / Extension / Obligation) + one-hop cross-framework
bridge coverage (IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE) as a
parallel attribution layer — engine unchanged, `posture_controls.finding`
unchanged, but auditors and consumers can now trace *which* other-
framework evidence contributes to a MUST's coverage.

## Motivation

Ship 58' shipped the per-MUST SSoT (`posture_must_verdicts`) as
per-tenant direct-fulfillment truth. Ship 58's audit documented Gap 1:
*"cross-framework bridges don't propagate satisfaction (intentional —
auditor per-framework dossier discipline)."*

Product feedback (2026-08-11): the framework role model needs to be
captured in SSoT, with bidirectional bridging. Not to replace the
engine's strict direct-only satisfaction — auditor per-framework
discipline stands — but to surface the attribution *"how is this GDPR
obligation covered? Via ISO A.5.15's rbac evidence."*

## Sub-arcs

| Sub-arc | Deliverable |
|---|---|
| 59'.a | schema_v96 — `framework_role` column on `posture_must_verdicts` (with CHECK constraint on P/E/O/OTHER) + new `posture_must_bridge_coverage` table (`target_must_id`, `source_must_id`, plus role + control_ref + standard_id + edge_type on each side) + RLS + indexes for forward (target lookup), reverse (source lookup), and framework-cross queries |
| 59'.b | Writer extension in `rag/posture_loader._persist_must_verdicts` — direct pass gains `framework_role` denormalization; new second pass iterates 318 Neo4j xfw edges (222 IMPLEMENTS + 62 SUPPORTS + 20 ENABLES + 14 GOVERNANCE), emits one bridge_coverage row per (source-satisfied-MUST × target-control-MUST × edge_type) triple. Delete + insert atomic replacement per tenant. Best-effort; never blocks direct pass |
| 59'.c | Extended `rag/posture/must_verdicts` — new `BridgeSource` dataclass; `MustVerdict` gains `framework_role` + `bridge_sources: tuple[BridgeSource, ...]`; new `.covered` property (direct OR bridge); `.state` gains new `'bridged'` value; `read_must_verdicts` fetches bridges in a second query and joins on the Python side; new `read_bridge_contributions()` helper for reverse-direction queries |
| 59'.d | Data audit on Arion demo — 35,516 bridge_coverage rows populated. Sample: Art.32 has 16 MUSTs, 6 direct-`present` + 10 `bridged` from ISO/ISO27701. Verified auditor attribution reads correctly (e.g. `Art.32:rev_date` shows 107 bridge sources from A.5.23 and other Program controls) |

## Key architectural decisions

**1. Engine remains unchanged.**
Ship 58's design invariant preserved. `evaluate_one_control`,
`compute_engine_verdicts`, `posture_controls.finding` — all unchanged.
Bridge coverage is written by `_persist_must_verdicts` after the engine
returns; the engine doesn't know about bridges.

Consequence: `posture_controls.finding = NC` still means "engine says
no direct evidence." A tenant seeing Art.32 as NC but with bridge
coverage from ISO evidence sees an honest picture: "you have overlapping
ISO work, but you need to also author Art.32-native artefacts if the
GDPR audit will look for them."

**2. Three-property model for consumer semantics.**
`MustVerdict` distinguishes three orthogonal concepts:

- **`.satisfied`** — strict direct fulfillment only. Backward-compat
  with all Ship 58 consumers. Matches engine's per-MUST recognition.
- **`.bridge_sources`** — list of BridgeSource dataclasses; empty when
  no bridge coverage. Attribution.
- **`.covered`** — `.satisfied OR bool(.bridge_sources)`. Opt-in for
  consumers that want the "covered somehow" view without opting into
  bridge-substitution semantics on `.satisfied`.

Plus `.state: str` — five-way categorical (`'present'` | `'stale'` |
`'partial'` | `'bridged'` | `'missing'`). Consumers that want a single
signal use `.state`; consumers that want membership checks use
`.satisfied` or `.covered`.

**3. One-hop bridge walking, no transitivity.**
Discussion 2026-08-11 established: xfw bridges are evidence links
(curator's judgment "same artefact serves both"), not definitional
links (unlike DerivedSpec `derives_from` which the engine walks
transitively). Each bridge is a discrete claim; chaining A→B→C without
a direct A→C edge would over-claim, because B might have its own MUSTs
that A doesn't address. Attribution is a *union of one-hop
contributors*, not a chain: C might be bridge-covered by A, D, and E
simultaneously, each a direct edge.

Future work (deferred): granularity-aware transitivity — chain A→B→C
where B is a pure pass-through (no additional MUSTs of its own). Not
this ship.

**4. Framework role denormalization.**
Both `posture_must_verdicts.framework_role` and `posture_must_bridge_
coverage.{source_role, target_role}` are denormalized. Fast filtering
without joining a role-derivation lookup. Enables queries like:

  SELECT count(*) FROM posture_must_bridge_coverage
   WHERE target_role='OBLIGATION' AND source_role='PROGRAM';

Cross-framework coverage dashboards become trivial SQL.

**5. Absence-of-row is still valid for N/A.**
Ship 58 codified lesson #2 (absence-of-row as valid N/A encoding)
preserved. Bridge coverage rows only exist when source MUSTs are
direct-satisfied AND target controls have MUSTs (see limitation
below). N/A MUSTs remain unwritten in `posture_must_verdicts` and
never appear as either source or target of bridge_coverage.

## Coverage on Arion demo

35,516 bridge_coverage rows across framework role pairs:

| target_role | source_role | edge_type | count |
|---|---|---|---:|
| PROGRAM | EXTENSION | SUPPORTS | 10,369 |
| OBLIGATION | EXTENSION | IMPLEMENTS | 8,768 |
| OBLIGATION | PROGRAM | IMPLEMENTS | 7,835 |
| OBLIGATION | PROGRAM | SUPPORTS | 3,426 |
| PROGRAM | OBLIGATION | IMPLEMENTS | 1,783 |
| OBLIGATION | PROGRAM | GOVERNANCE | 1,332 |
| OBLIGATION | PROGRAM | ENABLES | 919 |
| PROGRAM | OBLIGATION | SUPPORTS | 770 |
| PROGRAM | OBLIGATION | GOVERNANCE | 207 |
| PROGRAM | OBLIGATION | ENABLES | 107 |

Sample query on Art.32 (GDPR OBLIGATION):
- 16 MUSTs total in `posture_must_verdicts`
- 6 direct `'present'` (Arion has some Art.32 evidence uploaded)
- 10 `'bridged'` (not directly satisfied, but bridge coverage from ISO)
- Example: `item:Art.32:rev_date` has 107 bridge sources from A.5.23
  (Personal data), 6.1.2 (Risk assessment), etc.

## Codified lessons

### 11. Distinguish definitional relationships from evidence bridges

Two edge families exist in Neo4j: `derives_from` (definitional
delegation — the derived spec IS its sources algebraically; engine
walks transitively) and IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE
(evidence-bridging assertions — curator judgment that same artefact
serves both; engine does NOT walk).

Treating them the same is a category error. Ship 59'.b writer walks
xfw bridges *one-hop* to emit attribution rows, respecting that each
bridge is a discrete claim. Engine walks `derives_from` transitively
because definitional delegation composes algebraically.

Rule: when adding graph-walking logic, first classify the edge
semantically (definitional vs evidence-linking). Different walk
disciplines follow.

### 12. Attribution surfaces without changing engine verdict

The Ship 58 audit deferred cross-framework bridge propagation as
"intentional — auditor per-framework dossier discipline." Ship 59'
demonstrates that attribution can be captured and surfaced without
compromising that discipline: `.satisfied` stays strict direct-only,
`.covered` is opt-in, `.state='bridged'` is a distinct signal.

This gives us *tenant-facing communication* ("your ISO work
contributes to GDPR — here's the mapping") without *false
compliance claims* ("your GDPR is automatically Comply because ISO
is Comply"). Auditor per-framework discipline preserved.

Rule: when a data-layer feature could break an invariant, design
the API to expose the feature as opt-in and keep the invariant on
the default path. Backward-compat + new capability, no trade-off.

### 13. Three-property model beats overloading one property

Overloading `.satisfied` to mean "direct OR bridge" would have
broken every consumer that treats `.satisfied` as engine's verdict.
Three distinct properties (`.satisfied` strict / `.bridge_sources`
attribution / `.covered` opt-in union) let consumers choose semantics
per surface without breaking anyone.

Rule: when adding a new dimension to a truth object, prefer new
properties over redefining old ones.

### 14. Cross-product without scope_items is verbose but correct

Neo4j audit (2026-08-11) found: xfw edges lack `scope_items`
properties in the current graph. Writer emits full cross-product:
every direct-satisfied source MUST × every target-control MUST.
Result: 35,516 rows on Arion. Verbose, but each row is a
defensible auditor-facing claim.

If curators later add `scope_items` per edge (Ship 1.14 provided
the schema), the writer trivially filters and the row count drops.
Correctness stays; row count improves.

Rule: when curator-intent metadata (like `scope_items`) is optional
in the schema, ship the writer assuming absence and honor presence
opportunistically. Don't require curator work before shipping.

## Known limitation — sub-article stub nodes

Neo4j graph has sub-article stub nodes (e.g. `Art.32.1.b`, `Art.5.1.f`)
that have IMPLEMENTS bridges pointing to them but ZERO MUSTs of their
own. Writer's cross-product `source_MUSTs × target_MUSTs = N × 0 = 0`,
so bridges TO these stubs emit no rows.

Example: ISO A.5.15 IMPLEMENTS GDPR Art.32.1.b (specific sub-clause on
confidentiality). Writer walks this edge, finds Art.32.1.b has 0
MUSTs, emits 0 bridge rows. A.5.15's satisfied MUSTs correctly
bridge-cover Art.32 (the parent article, 16 MUSTs), just not the
sub-clause Art.32.1.b explicitly.

Future work: sub-article roll-up — treat a stub node's bridges as
implicit bridges to the parent article's MUSTs. Requires either
- string-based ref-parsing (`Art.32.1.b` → `Art.32`), or
- explicit `parent_ref` edges added to Neo4j.

Deferred; the parent-article coverage is captured directly via A.5.15's
other bridge to Art.32 (or via engine walk on the DerivedSpec parent).

## What's now different in the product

- **SSoT models P/E/O + bidirectional bridges** — matches the mental
  model curators + auditors use.
- **`MustVerdict.bridge_sources`** available on the shared reader —
  consumers can render attribution (once they opt in).
- **`state='bridged'`** — new signal for consumers to render "covered
  via other framework's evidence" distinctly from "still needed" or
  "present".
- **Reverse queries via `read_bridge_contributions()`** — "what does
  my ISO A.5.15 work contribute to?" now answerable in one SQL call.
- **Framework role denormalized** — dashboards can group by role
  trivially.

Consumer UX (template ticks, wizard progress, chat footers,
dashboard leaf chip) is unchanged — Ship 59' is a **pure data layer**.
Consumers opt into bridge awareness later (Ship 60' handles some of
this; the tick indicator opt-in is a separate product call).

## Follow-ons deferred

- **Ship 60' — Advisory refactor** — `build_per_must_advisory_data`
  reads SSoT (direct + bridge) instead of running the engine; 5
  advisory sites inherit the fix.
- **Ship 61'.a — Evidence Package hybrid** — raw findings for
  verbatim excerpts + SSoT for coverage summary.
- **Consumer UX for `state='bridged'`** — tick indicator variant (↗?),
  advisory attribution panel, dashboard cross-framework coverage.
  Product call to determine visual + copy.
- **Sub-article stub roll-up** — implicit parent-article bridging for
  Art.32.1.b-style stub nodes.
- **Granular transitivity** — future arc: chain A→B→C only when B is
  a pure pass-through (no additional MUSTs).
- **Engine evolution E1** — if adopted, engine emits its own
  `item_ids_bridge_covered` on `LeafVerdict`, simplifying Ship 59's
  writer. Still additive (no verdict change), safest engine evolution.

## What Ship 59' costs to reproduce

- Schema migration: 1 (schema_v96)
- Wall clock: ~1 hour design + ~1 hour implementation + ~30 min
  audit + retro
- Human time: ~2.5 hours across the arc
- Files touched: 3 (schema_v96.sql, rag/posture_loader.py,
  rag/posture/must_verdicts.py)
- Lines: ~350 insertions
- Data volume: 35,516 bridge_coverage rows on Arion demo (bootstrap
  populates other tenants when their engine walks land)
- Eval regression: same 231/232 baseline, zero engine changes
