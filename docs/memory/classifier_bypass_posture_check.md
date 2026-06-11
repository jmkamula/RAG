---
name: classifier-bypass-posture-check
description: "SHIPPED 2026-06-11 (4d4a2a0): _handle_ambiguous now bypasses clarification when the LLM intake classifier returns POSTURE_CHECK. Saves ~10s clarifier round-trip on posture-status queries whose phrasing wasn't covered by CLEAR_INTENT_PHRASES."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Companion to [[classifier-posture-short-circuit]] — same goal
(skip clarifier for posture queries), different layer (LLM intake
classifier vs regex CLEAR_INTENT_PHRASES).

## Surfaced by

`what is our access control compliance status?` — phrasing wasn't
covered by any CLEAR_INTENT_PHRASES regex (the closest pattern
`\baccess\s+(?:control|review)\s+(?:gaps?|issues?|status)\b` needs
"access control status" adjacency, broken by the intervening
"compliance"). Fell into `_handle_ambiguous` because vector
clusters were close. The clarifier asked (a) POSTURE_STATUS /
(b) REMEDIATION_GUIDE / (c) ... at 10.9s cost before the user
could pick the obvious answer.

## What changed

`rag/classifier.py:_handle_ambiguous` already bypassed
clarification when `_llm_classify_intake` returned
DOCUMENT_INVENTORY or DOCUMENT_CONTENT. Extended the bypass set
to include POSTURE_CHECK:

```python
_BYPASS_CLARIFICATION_TYPES = frozenset({
    QuestionType.DOCUMENT_INVENTORY,
    QuestionType.DOCUMENT_CONTENT,
    QuestionType.POSTURE_CHECK,
})
```

POSTURE_CHECK is intent-unambiguous — the user wants to see
status. They may want remediation next, but that's a follow-up
turn, not an upfront fork.

## Why this is structural, not a treadmill

User constraint: "we will never be able to cover every possible
choice of wording from tenants." Adding regexes to
CLEAR_INTENT_PHRASES is the treadmill. The bypass-set fix
delegates the disambiguation call to the LLM intake classifier
that's *already running* in `_handle_ambiguous` (line 1075). One
new entry covers all phrasings the LLM can recognise as a
posture query — no per-wording maintenance.

## Trade-off accepted

If a user genuinely meant REMEDIATION_GUIDE but phrased it as
posture status, they get status first and need one extra turn
to ask "what should I do?". This is acceptable: status precedes
remediation in the natural conversation arc anyway, and the cost
is one cheap follow-up vs the 10s clarifier round-trip on every
posture query.

## Future bypasses

If the same friction shows up for another intent type, append it
to `_BYPASS_CLARIFICATION_TYPES`. Candidates I'd watch:
- IMPLEMENTATION ("how do we implement X") — user-friction
  query, unambiguous as intent.
- DEFINITION ("what is X") — already handled by
  DEFINITION_VERBS regex, probably not needed.

Add only when a real query falls through, not preemptively.

## Related

- [[classifier-posture-short-circuit]] — sibling: regex layer
  short-circuit for the same intent family.
- [[posture-claim-hallucination-guard]] — L1 hallucination
  guard runs after the bypass routes through to posture
  rank_and_answer.
