---
name: ship-97-prime-b-chat-scoping-remediation
description: Ship 97'.b — chat response scoping for scoped remediation queries. "how do I remediate 7.2?" was returning 7.2 + 7 unrelated NCs (top-N posture leaked via required_refs, top-N obligation as digest context). Two-file surgical fix in preservation.py + digest.py tightens posture_limit/obligation_limit + skips top-N surfacing when question_type∈{implementation,gap_analysis} AND cited_refs is set. Response cleaned 8 refs → 2 refs (7.2 primary + Art.39 curated cross-role neighbor).
metadata:
  type: project
---

# Ship 97'.b — Chat response scoping for remediation (2026-08-26)

## Framing

Operator pasted the response to "how do I remediate 7.2?" and
asked: are we getting the right response here?

**Prose was on point** — 4 concrete ISO 27003-grounded steps,
advisory tone, no auditor overtones. Ship 96'.c + 97'.a tone
work was paying off.

**Structured surface was bloated.** The response bolted on 7
unrelated controls under "Obligations / Management-system
clauses / Related controls" headers + 8 "Ready-to-use starters"
across those same controls. The tenant asked about 7.2; they got
7.2 + a dump of their program's top NCs.

Root-cause trace: two leak paths feeding
`build_related_cards.extras`:

1. **preservation.py::`_required_refs`** — unions cited refs
   with top-N `_rank_posture_refs` (Ship 2' preservation) + top-N
   `_rank_obligation_refs` (Ship 53'.j definition-query fix).
   For scoped remediation this drags in every top NC across the
   program regardless of relevance to the cited control.
2. **digest.py::`_render_posture`** — with `posture_limit=10`
   the LLM sees 10 posture rows including the top 9 NCs on top
   of 7.2. LLM's system prompt at `llm_answer.py:476` says
   "always include relevant cross-framework nodes when they
   exist in the node list" — so it dutifully surfaces them.

## Delivered

**Two files, one shape**: `question_type in {"implementation",
"gap_analysis"} AND cited_refs` gates a scoped-remediation mode.

### `rag/casefile/digest.py::_plan_for`

New branch before the default plan:

```python
if cf.question_type in ("implementation", "gap_analysis") and cf.cited_refs:
    return _DigestPlan(
        posture_limit       = 1,     # was 10 — cited ref only
        posture_body_chars  = 200,   # generous for this ONE ref
        obligation_limit    = 2,     # was 5 — only genuine bridges
        obligation_chars    = 300,
        obligations_first   = False,
    )
```

`_rank_posture_refs` puts cited refs first, so `limit=1` keeps
7.2 in — no risk of it dropping. xfw bridges + curated Neo4j
cross-role neighbors surface via `_render_xfw_bridges` +
`fetch_cross_role_neighbors` independently.

### `rag/casefile/preservation.py::_required_refs`

Same gate skips feeders 2 + 3:

```python
scoped_remediation = (
    cf.question_type in ("implementation", "gap_analysis")
    and bool(cf.cited_refs)
)
if scoped_remediation:
    return out  # cited-only
# else: original union with top-N posture + top-N obligation
```

`required_refs` drives `extras` passed to `build_related_cards` +
the preservation-repair pass. Both stay minimal.

## Root-cause on the first-fix-miss

My first attempt checked `cf.question_type == "REMEDIATION_GUIDE"`.
Chat log showed 0 impact. Diagnosis: mismatch between
**taxonomy labels** (used in `rag/taxonomy.py::CLASSIFIER_TO_TAXONOMY`
mapping — `"implementation" → "REMEDIATION_GUIDE"`) and
**enum values** (used by `CaseFile.question_type` — returns the
`QuestionType` enum's `.value`, which is `"implementation"` for
IMPLEMENTATION).

`cf.question_type` returns the enum value; my check needed the
enum value string. Fixed after 1 dogfood test.

## Dogfood

Query: "how do I remediate 7.2?"

**Before**:

- 8 related cards: 7.2 (primary) + Art.39, Art.44
  (Obligations) + 10.1, 10.2, 7.5 (Management-system clauses)
  + A.5.22, A.8.32 (Related controls)
- 8 Ready-to-use starters spanning all 8 controls

**After**:

- 2 related cards: 7.2 (primary, OFI) + Art.39 (Obligation via
  Neo4j `DEMONSTRATES` edge — the tenant's competence work
  demonstrates the DPO Tasks obligation)
- 2 starters (7.2 + Art.39 scope)
- LLM prose unchanged — 4 concrete ISO 27003-grounded steps

Verified against Neo4j: 7.2 has exactly ONE cross-standard edge
(`7.2 -[DEMONSTRATES]-> Art.39`). The Art.39 card is
legitimately related; all 7 dropped cards were leaks.

## What Ship 97'.b doesn't change

- **DEFINITION queries** — unchanged. Still lead with obligation
  text; posture is background (`posture_limit=3`, ~unchanged
  effective width). Definition needs the broader context.
- **POSTURE_STATUS / GAP_ANALYSIS without cited_refs** —
  unchanged default plan. Broad queries ("what are our NCs?")
  legitimately want the top-N surface.
- **CROSS_FRAMEWORK / DOCUMENT_STATUS / DOCUMENT_CONTENT /
  ASSESSMENT / TOPIC_BUNDLE** — unchanged.
- **Cross-role neighbor injection** — still fires. Curated
  Neo4j edges (DEMONSTRATES / IMPLEMENTS / SUPPORTS /
  GOVERNANCE) surface as they should. For 7.2 this means Art.39
  survives; the tenant sees the auditor-authored relationship,
  not a data-driven top-N sample.

## Eval

232 PASS + 1 WARN + 0 FAIL — baseline preserved.

## Codified lessons

**Lesson 138: Deterministic context leakage is a chat quality
bug.** Two Ship 2' + Ship 53'.j behaviors (top-N posture in
required_refs; top-10 posture in digest) were correct-by-default
for broad queries but wrong for scoped queries. The LLM's prose
was doing the right thing; the DETERMINISTIC scaffolding around
it was adding noise. Rule: when auditing chat response quality,
separate the LLM's prose from the deterministic scaffolding
(digest structure, required_refs, related-card injection). The
LLM often takes the blame for what the substrate around it is
doing.

**Lesson 139: Enum values vs. taxonomy labels are not
interchangeable.** `QuestionType.IMPLEMENTATION.value =
"implementation"`; the taxonomy label `"REMEDIATION_GUIDE"` maps
FROM `"implementation"` via `CLASSIFIER_TO_TAXONOMY`.
`cf.question_type` returns the enum value. Code checking
against the taxonomy label silently doesn't match. Rule: when
guarding on question_type, prefer checking against `QuestionType`
enum values directly (via `.value` or the string constants used
in the enum definition). Grep for the enum values, not the
taxonomy labels.

**Lesson 140: Scoped-question surfaces need scoped-question
plans.** The chat pipeline had DEFINITION + DEFAULT plans; both
serve broad questions well. Scoped-question shape ("how do I
remediate X?") is different: the tenant wants X and X's genuine
neighbors, not the tenant's whole program state. Rule: when a
new question shape emerges (Ship 1'.a intent scaffolding, Ship
54'.c TOPIC_BUNDLE, Ship 97'.b scoped-remediation) the digest
plan needs a matching branch. Default plans are safe fallbacks,
not one-size-fits-all.

## Deferred

- **Broader tone / structure audit across other question types**
  — this arc surfaced that scoped-question shape is real. Other
  question types (DOCUMENT_STATUS, CROSS_FRAMEWORK) may benefit
  from similar plan tightening. Not urgent; wait until operator
  or eval flags an offender.
- **New eval case for scoped remediation** — Ship 1's
  [[feedback-eval-with-each-feature]] rule says "add an EvalCase
  that would have failed pre-change and passes post-change." The
  eval suite structure prefers structural assertions
  ([[feedback-eval-state-drift]]); a "related-card count ≤ 3"
  assertion for scoped remediation would fit. Log as a
  follow-up.

## Related

- [[ship-97-prime-a-cites-tab-and-drill-in-tone]] — sibling arc;
  drill-in tone rewrite
- Ship 2' — the case-file arc that introduced
  `_rank_posture_refs` + preservation.required_refs
- Ship 53'.j — added `_rank_obligation_refs` to required_refs
  (Case #222 fix); Ship 97'.b scopes it out for
  implementation/gap_analysis with cited refs
- Ship 22'.d + 23'.c — obligation demonstrator + cross-role
  neighbor injection; still fires, unchanged
- Ship 1' consensus architecture — question_type classification
  the scoped mode gates on
- [[feedback-advisory-tone-not-authoritative]] — tone rule
  (unchanged; prose was already advisory)
- [[feedback-eval-with-each-feature]] — deferred eval case
