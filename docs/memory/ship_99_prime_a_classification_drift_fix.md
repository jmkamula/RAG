---
name: ship-99-prime-a-classification-drift-fix
description: Ship 99'.a — fixed 3 classification drift cases from Ship 98'.a diagnostic. "what does A.5.18 say?" was routing to document_content; "am I compliant?" + "are we compliant?" were routing to cross_framework. 2 new CLEAR_INTENT_PHRASES entries hard-anchor these to definition + posture_check respectively. 3 regression eval cases lock the behavior.
metadata:
  type: project
---

# Ship 99'.a — Classification drift fix (2026-08-27)

## Framing

Ship 98'.a diagnostic surfaced 4 misclassified queries. Ship
99'.a fixes 3 of them (the 4th, FREE_ASSESSMENT → gap_analysis,
is arguably correct — a "where do I stand" query IS effectively
a broad gap-analysis).

## Root cause

The consensus layer's decisions look at 7 signals + gatekeeper.
For the 3 broken queries, no signal was firing with a
question_type opinion:

| Query | Signals fired | Missing |
|---|---|---|
| "what does A.5.18 say?" | posture_boost, explicit_refs, retrieval, graph_tightness | No signal claimed `definition` |
| "am I compliant?" | posture_boost, graph_tightness, retrieval | No signal claimed `posture_check` |
| "are we compliant?" | (same) | (same) |

Signal C (`curated_lexicon`, weight 1.00 — top-tier) is where
CLEAR_INTENT_PHRASES + DOCUMENT_TOPIC_MAP live. When it doesn't
fire, retrieval-based inference dominates — which for these
queries picked the "wrong" intent because ambient tenant content
tipped the vector similarity.

The `DEFINITION_VERBS` regex existed at classifier.py:471 and
matched "what does" — but only as a HELPER regex for the LLM
classifier's fallback path. Not a CLEAR_INTENT_PHRASES entry.
Same for `POSTURE_VERBS` on "compliant" — helper, not
hard-anchor.

## Delivered

**2 new CLEAR_INTENT_PHRASES entries** in `rag/classifier.py`:

```python
# Bare compliance queries
(re.compile(r'\b(?:am\s+i|are\s+we)\s+(?:compliant|in\s+compliance)\b',
            re.IGNORECASE),
 "posture_check", []),

# Definition — "what does X say/mean/require/state/contain"
(re.compile(r'\bwhat\s+does\s+\S.*\s+(?:say|mean|require|state|contain)\b',
            re.IGNORECASE),
 "definition", []),
```

Both are Signal C hard-anchors. Curator-authored, top-tier
weight — deterministic routing per Ship 1' discipline.

## Dogfood

4/4 queries route correctly post-fix:

| Query | Was | Now |
|---|---|---|
| "what does A.5.18 say?" | document_content | **definition** ✓ |
| "am I compliant?" | cross_framework | **posture_check** ✓ |
| "am I compliant with A.5.18?" | (worked via existing "compliant with" pattern) | posture_check ✓ |
| "are we compliant?" | cross_framework | **posture_check** ✓ |

## Regression eval cases

3 new locks added to `tests/eval_suite.py`:

- **#230**: "what does A.5.18 say?" — expected_type=definition
- **#231**: "am I compliant?" — expected_type=posture_check
- **#232**: "are we compliant?" — expected_type=posture_check

All 3 would have failed pre-99'.a; PASS post-99'.a. Baseline
grows from 233 → 236 PASS.

## Eval

236 PASS + 1 WARN + 0 FAIL — baseline expanded.

## What NOT flagged (kept in scope discipline)

- **FREE_ASSESSMENT → gap_analysis** — Ship 98'.a's 4th case
  ("where do I stand overall?", "where do I stand on access?").
  These are broad program-wide queries; routing to gap_analysis
  is arguably correct — "where do I stand" IS asking about gaps
  and posture holistically. Not a bug, kept as-is.

## Codified lessons

**Lesson 152: Helper regexes are not hard-anchors.** The
`DEFINITION_VERBS` and `POSTURE_VERBS` regexes at classifier.py:
471-487 EXISTED and would have matched these queries — but they
were used only as helpers to the LLM classifier's fallback path,
not as CLEAR_INTENT_PHRASES entries. The consensus layer never
saw them as Signal C hard-anchors. Rule: when a helper regex
already captures the intent shape, promote it to
CLEAR_INTENT_PHRASES so Signal C can hard-anchor — don't rely on
the LLM classifier to notice the same pattern.

**Lesson 153: The absence of a Signal C fire is diagnostic.**
Ship 98'.a's per-query signal dump made this fix trivial. Every
misclassified query had NO `curated_lexicon` signal firing —
Signals A/D/E were dominating decisions where curator vocabulary
should have led. Rule: when auditing classifier drift, look
first at which signal fired the question_type. If none did (or
only weight-0.10-0.20 signals did), the fix is almost certainly
"add a CLEAR_INTENT_PHRASES entry."

## Related

- [[ship-98-prime-a-diagnostic]] — the diagnostic that flagged
  these 4 misclassifications; Ship 99'.a fixes 3
- Ship 1' consensus architecture — the 7-signal + gatekeeper
  layer this fix targets
- Ship 1'.d — the CLEAR_INTENT_PHRASES pattern this arc extends
- [[dejargonize-ux-pass-2026-07-01]] — the "curator vocab
  dominates" discipline Ship 1' codified
