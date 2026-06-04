---
name: feedback-anchor-before-choices
description: "Anchor the broader roadmap before presenting multiple-choice questions about scope/sequencing. The \"where are we going with this?\" pushback in 2026-06-04 workbook intake session."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 26c1ec2d-8e36-436c-af44-a16367a2126d
---

**Rule:** Anchor the broader roadmap before presenting multiple-choice questions about scope or sequencing. When a design decision sits inside a larger plan, explain the plan first in 4–6 lines (build order, what depends on what, what "X" means concretely in this context) THEN ask. Single anchored question at a time. Not blasted multi-question cards before the user has anchored on the framing.

**Why:** During the 2026-06-04 Phase 2 workbook intake design session, I jumped to `AskUserQuestion` with "Seed scope: 4 vs 12 vs 1?" before the user had a clear picture of what stages I/II/III meant or what "tenant-facing surface" referred to. The choice felt arbitrary without the sequencing context. The user interrupted with "where are we going with this?" — that's the diagnostic signal that I jumped past the anchoring step. Once I explained the roadmap (author YAMLs → Stage I engine → Stage II HITL → Stage III extraction → re-ingest Arion workbook → measure NC delta), they picked the seed-scope option immediately.

**How to apply:**
- Before any `AskUserQuestion`, ask yourself: does the user have the roadmap context to understand why this choice matters? If not, anchor first in 4-6 lines, then ask.
- When there are multiple decisions worth surfacing, ask the most consequential ONE first; don't surface a 3-question card.
- This user's question-answering style is quick, decisive, single-line ("defer override to v2", "1 is fine", "go with revised rule"). They want anchored framing and one decision at a time, not exhaustive option grids.
- The pattern applies even more strongly when the user is in design mode (multi-turn architectural discussion) than in implementation mode (single concrete task).

**Related:** general writing guidance in CLAUDE.md (exploratory questions get 2-3 sentences with recommendation and tradeoff; present as redirect-able, not decided).
