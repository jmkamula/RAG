---
name: ship-59-prime-arc-2026-08-11
description: "Ship 59' arc pointer — P/E/O SSoT with bidirectional bridge attribution + Ship 59'.e stub roll-down. Full retro at /data/arioncomply/docs/memory/ship_59_prime_arc_2026_08_11.md."
metadata: 
  node_type: memory
  type: project
  ship: "59'"
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 59' extends the Ship 58' per-MUST SSoT (`posture_must_verdicts`)
with framework role denormalization + bidirectional cross-framework
bridge coverage as a parallel attribution layer. Engine unchanged —
`posture_controls.finding` still strict direct-only satisfaction.

**Sub-arcs**
- 59'.a — schema_v96 (framework_role + posture_must_bridge_coverage)
- 59'.b — writer walks 318 xfw edges (IMPLEMENTS/SUPPORTS/ENABLES/
  GOVERNANCE) via cross-product source-satisfied × target-MUSTs
- 59'.c — `MustVerdict.bridge_sources` + `.covered` opt-in property
  + `.state='bridged'` five-way categorical
- 59'.d — data audit + retro
- 59'.e — stub roll-down (schema_v96b + v96c, `_load_stub_effective_
  musts` via DERIVES_FROM depth 1..3 + `Art.X.Y.Z→Art.X` fallback,
  writer emits parallel `stub_rollup` verdict rows + stub-scoped
  bridge rows; SSoT now answers "how is Art.32.1.b covered?"
  self-contained with 16 MUSTs surfaced, 40k bridge rows on Arion)

**Codified lessons**
- (11) Definitional vs evidence-bridging edges — different walk
  disciplines. Engine walks DERIVES_FROM transitively; bridge writer
  walks xfw edges one-hop only.
- (12) Attribution surfaces without changing engine verdict — the
  three-property model (`.satisfied` strict / `.bridge_sources`
  attribution / `.covered` opt-in) keeps backward compat + adds
  attribution power in one shape.
- (13) Prefer new properties over redefining old ones.
- (14) Cross-product without `scope_items` is verbose but correct —
  35k+ rows on Arion, each defensible.
- (15) SSoT self-containment — see [[feedback-ssot-self-containment]].
- (16) Reader semantics differ by scope selector — `must_ids` returns
  canonical; `control_ref` returns context-scoped.

**Follow-ons deferred** (unchanged from 59'.d retro):
Ship 60' (advisory refactor via SSoT + bridge awareness), Ship 61'.a
(Evidence Package hybrid), consumer UX for `state='bridged'`,
granular transitivity, engine evolution E1.

Full retro (with sub-arc detail, coverage numbers, and codified
lessons in narrative form): `/data/arioncomply/docs/memory/
ship_59_prime_arc_2026_08_11.md`.
