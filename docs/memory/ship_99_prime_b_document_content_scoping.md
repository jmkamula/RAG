---
name: ship-99-prime-b-document-content-scoping
description: Ship 99'.b — DOCUMENT_CONTENT gets its own tighter plan in _plan_for + gets added to preservation._required_refs cited-only branch. Ship 98'.b's SCOPED gate was firing correctly for "what must A.5.15 contain?" (3 cards) but TOPIC-shape DOCUMENT_CONTENT queries ("what must an access control policy contain?") were surfacing 11-13 cards. Fix: DOCUMENT_CONTENT is always doc-checklist-shaped regardless of shape enum.
metadata:
  type: project
---

# Ship 99'.b — DOCUMENT_CONTENT scoping (2026-08-28)

## Framing

Ship 98'.b's shape-aware SCOPED gate fires correctly for
"what must A.5.15 contain?" (3 cards). But TOPIC-shape
DOCUMENT_CONTENT queries ("what must an access control policy
contain?") were surfacing 11-13 related cards — because TOPIC
falls through to the default plan (posture_limit=10 + top-N
obligation surfacing).

Semantic problem: DOCUMENT_CONTENT is always a "give me the
doc's MUST checklist" ask, regardless of whether the tenant
typed the ref or the topic phrase. Broad top-N NC context is
noise for this intent — the tenant is drafting a policy, not
surveying their program state.

## Delivered

**Two-file fix.**

`rag/casefile/digest.py::_plan_for` — new DOCUMENT_CONTENT
branch between the Ship 98'.b SCOPED gate and the default plan:

```python
if cf.question_type == "document_content":
    return _DigestPlan(
        posture_limit       = 3,
        posture_body_chars  = 150,
        obligation_limit    = 3,
        obligation_chars    = 300,
        obligations_first   = False,
    )
```

Sits after the SCOPED gate, so SCOPED DOCUMENT_CONTENT
(explicit ref in query) still gets Ship 98'.b's tight-1 plan.

`rag/casefile/preservation.py::_required_refs` — extended the
cited-only path to also cover `question_type ==
"document_content"` regardless of shape:

```python
scoped_remediation = (
    (cf.question_shape == "scoped" and cf.question_type != "definition")
    or cf.question_type == "document_content"
)
```

This is where the top-N tenant NC leak was flowing in.

## Dogfood

| Query | Pre-99'.b | Post-99'.b |
|---|---|---|
| "what must an access control policy contain?" | 13 | **9** (A.5.15 + 6 GDPR articles it DEMONSTRATES per curated Neo4j + 2 ISO access controls — all legit cross-standard mapping) |
| "what must A.5.15 contain?" | 3 | 3 (SCOPED gate unchanged) |
| "what must an incident response policy include?" | 11 | **1** (A.5.24 has one Neo4j neighbor) |

Response now scales with the primary's actual cross-standard
graph. A.5.15's 9 cards are legit (it's cross-cutting security
control). A.5.24's 1 card is legit (few curated edges).

## Regression

**EvalCase #233** — "what must an incident response policy
include?" with forbidden_refs = [A.6.8, A.8.15, A.5.28]
(top-N NC injection pre-99'.b that had no Neo4j edge to A.5.24).

**Baseline expanded**: 236 → **237 PASS** + 1 WARN + 0 FAIL.

## Codified lessons

**Lesson 154: Question-type semantics can override shape.**
Ship 98'.b introduced `question_shape` for cases where the same
`question_type` legitimately wants different context breadth
(remediation is scoped, but gap analysis wants adjacent
context). But some `question_type`s have a *fundamentally
narrow* semantic regardless of shape — DOCUMENT_CONTENT is a
doc-checklist ask whether the tenant types the ref or the
topic phrase. Rule: not every question_type needs shape-
sensitive plans. Some are shape-invariant (always narrow or
always broad); those get a direct `question_type` branch.

**Lesson 155: Cross-role neighbor breadth is emergent, not
configurable.** After Ship 99'.b: A.5.15 shows 9 related cards,
A.5.24 shows 1. Both DOCUMENT_CONTENT + TOPIC. The difference
isn't in the plan — it's in the underlying Neo4j graph. A.5.15
DEMONSTRATES 6 GDPR articles; A.5.24 has one. Rule: when
tightening related-card output, verify the remaining breadth
reflects genuine curated relationships, not top-N injection.
Fixed-count caps mask this; graph-driven emergence surfaces it.

## Related

- [[ship-98-prime-b-question-shape]] — introduced the shape
  enum; this arc adds a `question_type`-based override for a
  shape-invariant intent
- [[ship-97-prime-b-chat-scoping-remediation]] — the arc that
  introduced the two-file scoped-mode pattern
  (digest._plan_for + preservation._required_refs)
- Ship 22'.d, Ship 23'.c — where the `_collect_demonstrators`
  + `fetch_cross_role_neighbors` injection points live (they
  still fire, unchanged; Ship 99'.b only stops the top-N
  preservation feeder leak)
