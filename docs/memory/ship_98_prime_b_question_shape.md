---
name: ship-98-prime-b-question-shape
description: Ship 98'.b — introduced QuestionShape enum (SCOPED/TOPIC/PROGRAM) orthogonal to QuestionType. Classifier populates via pure-function inference on cited_refs + query text. _plan_for + _required_refs branch on shape. Generalizes Ship 97'.b/c one-intent gate to every non-DEFINITION intent. GAP_ANALYSIS scoped 8→2, POSTURE_CHECK scoped 12→6, CROSS_FRAMEWORK scoped 11→5.
metadata:
  type: project
---

# Ship 98'.b — QuestionShape enum (2026-08-27)

## Framing

Ship 98'.a's diagnostic surfaced two facts:

1. The bloat pattern is **shape-specific**, not
   `question_type`-specific. Every SCOPED cell across every
   intent shows the same top-N-NC leak.
2. The shape distinction can be inferred deterministically from
   what the classifier already computes (cited_refs + query
   text). No new signal, no new prompt.

Ship 97'.b/c enumerated one intent (IMPLEMENTATION) into a
scoped-plan branch. Ship 98'.b generalizes: introduce the shape
enum as first-class, populate at classify time, and branch on it.

## Delivered

### `QuestionShape` enum + `infer_question_shape()`

`rag/classifier.py`:

```python
class QuestionShape(Enum):
    SCOPED  = "scoped"
    TOPIC   = "topic"
    PROGRAM = "program"

def infer_question_shape(query: str, cited_refs: list) -> str:
    if not cited_refs:
        return QuestionShape.PROGRAM.value
    q = query or ""
    for ref in cited_refs:
        if ref and ref in q:
            return QuestionShape.SCOPED.value
    return QuestionShape.TOPIC.value
```

Pure function; deterministic. 6/6 sanity cases correct.

### Classify node populates `state["question_shape"]`

`rag/arion_graph.py::classify` — on the confident-verdict
return, compute shape from `state["query"]` + `intent.cited_refs`
and include as a state field alongside `intent_type`.

Other classify-return paths (clarification, ambiguous, unknown,
topic_bundle, short-circuits) don't populate it — the fallback
below handles them.

### `CaseFile.question_shape` property

`rag/casefile/types.py` — reads from `intent["question_shape"]`
when the classify path populated it; falls back to fresh
`infer_question_shape` inference otherwise. Short-circuits +
legacy call sites work unchanged.

### Both consumers branch on shape

`rag/casefile/digest.py::_plan_for`:

```python
if cf.question_shape == "scoped" and cf.question_type != "definition":
    return _DigestPlan(
        posture_limit       = 1,
        posture_body_chars  = 200,
        obligation_limit    = 2,
        obligation_chars    = 300,
        obligations_first   = False,
    )
```

`rag/casefile/preservation.py::_required_refs`:

```python
scoped_remediation = (
    cf.question_shape == "scoped" and cf.question_type != "definition"
)
if scoped_remediation:
    return out  # cited-only
```

**DEFINITION excluded** even when SCOPED — the DEFINITION plan
intentionally leads with obligations + broader context; a
tenant asking "what does X say?" wants the standard's own text,
not the tenant's posture. Same rationale as the Ship 97'.c
narrowing.

## Diagnostic improvement

Ship 98'.a diagnostic re-run post-fix:

| Cell | Pre-97'.b | 97'.b/c | 98'.b |
|---|---|---|---|
| IMPLEMENTATION scoped | 8 | **2** | 2 |
| GAP_ANALYSIS scoped | 8 | 8 | **2** |
| POSTURE_CHECK scoped | 12 | 12 | **6** |
| CROSS_FRAMEWORK scoped | 11 | 11 | **5** |
| DEFINITION scoped | 10 | 10 | 6 |
| DOCUMENT_CONTENT scoped | 13 | 13 | 13 |

The 3 non-fixed SCOPED cells (POSTURE_CHECK at 6, CROSS_FRAMEWORK
at 5, DEFINITION at 6, DOCUMENT_CONTENT at 13) surface primary
+ genuine Neo4j cross-role neighbors + demonstrators. That's
legitimate context — the primary + curated cross-standard
relationships. Not top-N-NC leakage.

DOCUMENT_CONTENT at 13 is the outlier — likely misclassified
into a short-circuit path that doesn't respect the shape gate.
Deferred; Ship 98'.a already flagged 4 classification-drift
cases as separate follow-ups.

TOPIC + PROGRAM cells: unchanged by design. Case #1 stays safe.

## Eval

233 PASS + 1 WARN + 0 FAIL — baseline held. Case #229 (Ship
97'.b lock) PASS — shape-based gate covers the same intent
IMPLEMENTATION scoped tightened.

## Codified lessons

**Lesson 143: When a fix generalizes cleanly across values of
an enum, promote the differentiator to its own enum.** Ship
97'.b/c gated on `question_type == "implementation"`. Ship
98'.a showed the same pattern applies to gap_analysis /
posture_check / cross_framework / document_content when the
tenant typed a ref. Rather than enumerate 4 more `question_type
== X` gates, promoted the differentiator (typed-ref vs
topic-phrase vs no-ref) to `QuestionShape`. One condition
replaces N. Rule: after 2-3 per-value gates share the same
shape of condition, extract the shape into its own type.

**Lesson 144: Diagnostic-driven design beats architect-first.**
The Ship 98' arc opened with a diagnostic run BEFORE choosing
enumerated-gates vs shape-enum. The 16-cell matrix made the
answer obvious (shape pattern uniform across intents) and
sized the fix concretely (15 cells targeted, 3 hit clean).
Rule: when the architectural direction isn't obvious, run a
diagnostic first. A small script that queries reality is worth
more than another design meeting.

**Lesson 145: Pure-function inference from existing state is
the smallest possible new abstraction.** `infer_question_shape`
takes two things already on every intent (query text + cited
refs) and returns an enum value. No new signal, no new
classifier prompt, no new consensus fusion rule. The whole
"new enum" is 3 lines of logic + a fallback in CaseFile. Rule:
before adding a new field to a data class, check if it can be
derived from existing fields via a pure function. Derived data
doesn't need propagation plumbing.

## Deferred

- **Fix the 4 classification-drift cases** flagged in Ship
  98'.a diagnostic:
  * "what does A.5.18 say?" → document_content (should be
    definition)
  * "am I compliant?" → cross_framework (broken)
  * FREE_ASSESSMENT queries → gap_analysis (arguable; may be
    correct behavior)
- **TOPIC-shape tightening** — TOPIC cells run 5-19 cards.
  Some (5) look fine; some (19) look bloated but tightening
  needs the case-#1 lesson — GAP_ANALYSIS TOPIC needs
  adjacent-area context. Would need a finer-grained plan
  than SCOPED/TOPIC/PROGRAM.
- **DOCUMENT_CONTENT scoped 13 cards** — either a
  classification issue (misrouted to a short-circuit that
  bypasses shape) or a legit shape but with extra Neo4j
  neighbors. Investigate.
- **New eval case per shape × non-implementation intent** —
  case #229 covers IMPLEMENTATION scoped; GAP_ANALYSIS
  scoped, POSTURE_CHECK scoped, CROSS_FRAMEWORK scoped could
  each get a lock case per [[feedback-eval-with-each-feature]].

## Related

- [[ship-98-prime-a-diagnostic]] — the input diagnostic
- [[ship-97-prime-b-chat-scoping-remediation]] — the arc that
  fixed the first cell; Ship 98'.b generalizes it
- [[ship-97-prime-c-eval-case-and-dashboard-move]] — the
  narrowing that Ship 98'.b subsumes into the shape gate
- [[feedback-eval-with-each-feature]] — new-eval-case rule
  applies (case #229 covers the pattern; per-intent locks
  deferred)
