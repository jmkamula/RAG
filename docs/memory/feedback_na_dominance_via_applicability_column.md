---
name: feedback-na-dominance-via-applicability-column
description: "N/A is a scoping decision, NOT an evidence assessment. It's carried by posture_controls.applicability_status ('applicable' | 'na'), not by posture_controls.finding. Every consumer that gates on N/A should read applicability_status; finding='N/A' is deprecated-legal (Ship 66' arc). Supersedes feedback-engine-should-not-clobber-tenant-na."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

**N/A is a scoping decision, not an evidence assessment.** Ship 66'
(2026-08-12) added `posture_controls.applicability_status` as a
separate column with values `applicable | na` (default `applicable`).
This is the authoritative signal for scope.

`posture_controls.finding IN ('NC', 'OFI', 'Comply', 'Not assessed',
'N/A')` still allows `'N/A'` for backward compat. **Do not use
`finding='N/A'` in new code.** It's deprecated-legal — will be
retired after the last consumer migrates.

**Why:** The pre-Ship-66' schema mixed evidence assessment (NC / OFI
/ Comply) with scope (N/A) in one column. Every consumer had to
remember N/A was special. A 2026-06-03 Phase B mass-approval flipped
`engine_proposal_status='approved'` on 17 Arion controls that were
tenant-declared N/A. The engine overlay honored the approval and
clobbered the N/A → NC. The codified rule at the time
([[feedback-engine-should-not-clobber-tenant-na]]) was documented
but not structurally enforced. Ship 65's Art.32 dogfood surfaced
the visible symptom (LLM recommending physical controls on a
cloud-only tenant); Ship 66'.a–.e closed the class of bugs by
schema split.

**How to apply:**

- **Reading scope**: check `posture_controls.applicability_status
  == 'na'` (or the corresponding field on the loaded posture rec,
  which `load_posture` returns since Ship 66'.a). Do NOT check
  `finding == 'N/A'` in new code.
- **Writing scope**: setting `applicability_status = 'na'` is the
  authoritative scoping change. The tenant's tooling should touch
  this column; the engine + Stage-2 approval must not.
- **Stage-2 approval** on an N/A control is refused at
  `approve_engine_proposal` (Ship 66'.d). Any new approval-shaped
  workflow (bulk, per-standard, per-role) must respect the same
  guard.
- **Engine overlay + SSoT writer + bridge writer** all short-
  circuit on `applicability_status == 'na'` (Ship 66'.b). Any new
  writer path against `posture_controls` / `posture_must_verdicts`
  / `posture_must_bridge_coverage` must respect the same guard.
- **Digest / advisory / evidence package** filter N/A from
  obligation rendering (Ship 66'.c). Include N/A refs in POSTURE
  only when explicitly cited, so the LLM can say "X is Not
  Applicable per your scope" instead of hallucinating.

**Deferred consumer migrations** (as of 2026-08-12) — sites still
checking `finding == 'N/A'` that should switch to
`applicability_status == 'na'`:

- `rag/scope_filter.py:93`
- `rag/resolver.py:718`
- `rag/arion_graph.py:2229 + 2249`
- `rag/posture_loader.py:198 + 215`

The Ship 66'.e grep guard flags any NEW consumer using
`finding == 'N/A'`; the 5 deferred sites are allowlisted with a
Ship 66' comment. Migrating a deferred site to
`applicability_status` = drop the allowlist entry.

Related:
- Ship 66' retro: [[ship-66-prime-arc-2026-08-12]]
- Ship 66' dogfood punchlist: [[dogfood-art32-2026-08-12]]
- Superseded rule: [[feedback-engine-should-not-clobber-tenant-na]]
  (kept for history; the tactical guard it described was regressed
  by the 2026-06-03 mass-approval; Ship 66' fixed this structurally).
