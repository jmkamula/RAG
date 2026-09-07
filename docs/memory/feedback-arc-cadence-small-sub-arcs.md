---
name: feedback-arc-cadence-small-sub-arcs
description: "Ship small focused arcs with .a-.g sub-arcs; multiple per day is normal; deferred items get concrete effort/priority/trigger, never open-ended TODOs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship small focused arcs. Each arc gets sub-arcs `.a` through `.f`/`.g`,
usually 3-7 sub-arcs. Each sub-arc is a self-contained delivery — code
+ tests + optional deploy + closer. Multiple arcs per day is normal
and preferred over one big multi-day feature push.

**Why:** 2026-09-05→06 shipped 6 arcs (Ship 118' → 123') in ~1 day, each
with 3-7 sub-arcs. The pattern surfaces gaps fast (Ship 119' deploy
revealed drift → Ship 120' closed it → Ship 121' closed the follow-ons
→ Ship 122' consolidated the guards → Ship 123' closed the UI gap). A
single "audit-defensibility feature" arc would have front-loaded design
+ back-loaded discovery; small arcs let discovery drive the next arc.

**How to apply:** When breaking work down, ask "can this be split into
3-7 sub-steps that each independently ship?" If yes, split. If no
(e.g. two changes that MUST land atomically), keep as one but still
sub-arc for tracking. For deferred items: every one gets an effort
estimate (min-hours / half-day / arc-sized) + a priority tier (close
now / next arc / wait for trigger) + the trigger condition if trigger-
driven (first customer offboarding / real regulatory demand / etc.).
Never leave a deferred item as "TODO: figure out X someday."

Related: [[feedback-verify-before-assert-live-state]] (arc-close
discipline), [[feedback-auto-compaction-loses-practice-patterns]]
(why saving this rule matters).
