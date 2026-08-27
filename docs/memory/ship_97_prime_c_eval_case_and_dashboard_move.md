---
name: ship-97-prime-c-eval-case-and-dashboard-move
description: Ship 97'.c — close-out sub-arc bundling two Ship 97 loose ends. EvalCase #229 locks scoped-remediation behavior; Dashboard action panels removed completing the Lesson 135 semantic split. Mid-arc regression forced narrowing the Ship 97'.b gate from {implementation, gap_analysis} → implementation only.
metadata:
  type: project
---

# Ship 97'.c — Eval case + Dashboard panel move (2026-08-27)

## Framing

Two Ship 97 close-outs bundled:

- **EvalCase deferred from Ship 97'.b** per
  [[feedback-eval-with-each-feature]] — every user-facing chat
  change should have a test that would have failed pre-change +
  passes post-change.
- **Dashboard action-panel duplication noted in Ship 96'.b** —
  `renderTriggeredImplicationsPanel` +
  `renderExpectedFollowupsPanel` still lived on Dashboard
  alongside the Cascade timeline copy. Ship 97'.a Lesson 135
  (semantic split: Dashboard = looking) makes the call.

## Delivered

### EvalCase #229

`tests/eval_suite.py`:

```python
EvalCase(
    id=229,
    query="how do I remediate 7.2?",
    tags=["ship97b", "scoped_remediation", "control_focused"],
    expected_type="implementation",
    expected_refs=["7.2"],
    forbidden_refs=["A.5.5", "A.5.22", "A.8.32", "A.5.27"],
    must_contain=["7.2"],
)
```

Forbidden refs chosen from the pre-97'.b bloat set — Arion NCs
with zero Neo4j edge to 7.2 that were pure top-N-NC noise:

- `A.5.5`  Contact with authorities
- `A.5.22` Supplier monitoring/review
- `A.8.32` Change management
- `A.5.27` Learning from information security incidents

Would have failed pre-97'.b; PASS post-97'.b/c.

### Dashboard panel removal

`static/arioncomply.html`:

- `renderTriggeredImplicationsPanel(implications)` call removed
  from `renderDashboard`
- `renderExpectedFollowupsPanel(followups)` call removed from
  `renderDashboard`
- 3 unused API fetches dropped from `loadDashboard()`:
  triggered-implications + expected-followups (pending +
  overdue)

The Follow-ups KPI tile still surfaces the count — reads from
`/api/v1/dashboard/cascade-kpis`, not the detail endpoints.

**Dashboard is now truly summary-only**: heatmap + KPI tile row
(Follow-ups / Coverage / Cites) + framework summary. Every
per-item action moved to its semantic home:

| Action | Home |
|---|---|
| Cites | Review queue > Cites tab (Ship 97'.a) |
| Follow-ups | Cascade timeline > Follow-ups due section (Ship 96'.b) |
| Coverage | Dashboard > Coverage tab (Ship 93'.c) |
| Stage-1/2 review | Review queue tabs |

## Mid-arc regression

First eval failed case #1:

    "what are our access rights gaps?" →
    "FORBIDDEN phrase present: 'physical'"

Case #1 tests a `gap_analysis` query on a cloud-only tenant.
"physical" must not leak.

**Root cause**: my Ship 97'.b gate `question_type in
{implementation, gap_analysis} AND cited_refs` was too broad.
For "what are our access rights gaps?" the classifier resolves
cited_refs = ["A.5.18"] via `DOCUMENT_TOPIC_MAP`. Scoped-mode
kicked in with `posture_limit=1` — LLM saw only A.5.18 in
POSTURE, lost the adjacent-NC context that had been anchoring
it away from generic "physical access control" prose.

**GAP_ANALYSIS is broader than IMPLEMENTATION.** "What are my
gaps for X area?" wants adjacent-NC context to say "you have
gaps here + here + here in this area." "How do I remediate X?"
wants pure scoped focus. Different question shapes.

**Fix**: narrowed both gates
(`preservation._required_refs` +  `digest._plan_for`) from
`{implementation, gap_analysis}` → `implementation` only.
GAP_ANALYSIS reverts to the default plan.

Verified:
- "how do I remediate 7.2?" → 2 related cards (scoped)
- "what are our access rights gaps?" → broader answer, no "physical" leak

## Eval

233 PASS + 1 WARN + 0 FAIL. Case #1 restored; case #229 PASS.

## Codified lessons

**Lesson 141: Scoped-question gates must be as narrow as the
question shape.** Two `question_type` values with cited_refs
aren't automatically the same shape. "How do I remediate X?"
(narrow) and "what are my gaps in X area?" (broad) both have
cited_refs but want opposite context breadth. Rule: express the
intent SHAPE explicitly in the gate; don't equate "has
cited_ref" with "wants narrow context."

**Lesson 142: The eval suite catches breadth-of-scope
regressions the dogfood misses.** Ship 97'.b dogfooded only
"how do I remediate 7.2?" — the gap_analysis case #1 was never
in the dogfood loop. Rule: when tightening a gate that fires on
multiple `question_type` values, dogfood one query per value.
"Passing on the one I care about" isn't enough when the gate
spans more than one intent.

## Ship 97 arc close

Three sub-arcs delivered:
- 97'.a — Cites tab + drill-in tone (Lessons 135, 136, 137)
- 97'.b — Chat scoping for remediation (Lessons 138, 139, 140)
- 97'.c — Eval + Dashboard move + narrowing (Lessons 141, 142)

**8 codified lessons across the arc.** Dashboard is now
looking-only. Chat has a first scoped-plan branch. Eval locks
the scoped behavior.

**Wider architectural pattern surfaced**: the chat pipeline
treats every question as broad by default. Ship 97'.b/c carved
out one narrow shape (implementation + cited). CROSS_FRAMEWORK,
POSTURE_CHECK-fallthrough, GAP_ANALYSIS may also want scoped
variants — that's Ship 98' territory.

## Related

- [[ship-97-prime-b-chat-scoping-remediation]] — the arc this
  closes out
- [[ship-97-prime-a-cites-tab-and-drill-in-tone]] — Lesson 135
  semantic split this arc completes for Dashboard
- [[ship-96-prime-b-cascade-timeline-ux]] — added the
  "Follow-ups due" section that made Dashboard duplication
  removable
- [[feedback-eval-with-each-feature]] — the rule that made
  case #229 a scheduling priority
- [[feedback-verify-stability-claims]] — the discipline that
  caught the case #1 regression as genuine (not "stochastic")
