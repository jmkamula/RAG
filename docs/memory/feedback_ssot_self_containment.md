---
name: feedback-ssot-self-containment
description: An SSoT row should be self-contained for the primary consumer query. Duplication under different context keys is cheaper than making every consumer walk parents to reconstruct the answer.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

An SSoT should answer the literal question the consumer asks. If the
question is *"how is Art.32.1.b covered?"* and the SSoT row's answer
is "walk to Art.32 and look at those rows," consumers regress to
building their own graph walks — exactly what SSoT was meant to
prevent.

**Why:** Ship 59'.d retro documented sub-article stub attribution as a
deferred known limitation ("the parent-article coverage is captured
directly via A.5.15's other bridge to Art.32"). User surfaced the gap
same-day: *"my problem is that SSoT cannot answer a direct question
about Art 32.1.b."* Ship 59'.e closed it: writer emits parallel
`stub_rollup` rows in `posture_must_verdicts` + stub-scoped bridge
coverage rows, both tagged with the *stub's* `control_ref`.
Duplication (same MUST appears once canonical + once per stub context)
is the right price for self-containment.

**How to apply:**
- When designing an SSoT schema, list the primary consumer queries
  first. Every query should be answerable with `WHERE <primary_key>`
  alone — no walking to related nodes.
- When a schema constraint (e.g. UNIQUE) forces one row per
  something, and consumers need multiple context-scoped views of the
  same underlying data, EXPAND THE KEY. Prefer `(tenant, must, ctx)`
  over `(tenant, must)` and a walk-to-context join.
- When adding new rows for a "stub" or "roll-up" context, tag them
  with a discriminator (e.g. `reason='stub_rollup:<parent>'`) so
  scope-selective readers can distinguish canonical vs synthesized.
- Reader semantics differ by scope selector: `must_ids` scope
  should return canonical only (extract owner from must_id shape);
  `control_ref` scope returns whatever matches. Enforce in the
  reader, not each consumer.

Related: [[ship-59-prime-arc-2026-08-11]] for the Ship 59'.e delivery,
[[human-in-the-loop-positioning]] for the auditor per-framework
discipline that Ship 59' preserves via the three-property model
(`.satisfied` strict / `.bridge_sources` attribution / `.covered`
opt-in union).
