---
name: llm-narrative-under-discovery-audit-2026-06-26
description: "AUDIT 2026-06-26, CORRECTED: original 17% median was wrong (bad denominator — counted catalog MUSTs across ALL leaves of a control, but most docs only address one or two). Real per-leaf median = 57%. Oracle ground-truth on low-yield docs: 94-100% of unfilled MUSTs are NOT IN THE DOC (wrong evidence type), only 0-6% are real extraction failures. Semantic-search arc closed — solving a problem ~5% of what I'd claimed. schema_v48 telemetry + MUST embedding index retained as foundation; G3-G6 gap catalog superseded."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## ⚠ CORRECTION — original audit was wrong

The initial audit reported **median 17% yield** as evidence of widespread
LLM under-discovery. That number was real-as-measured but
wrong-as-interpreted:

- **Denominator bug**: I summed MUSTs across ALL leaves of a control,
  but most docs only address one or two leaves of a multi-leaf
  control. E.g. A.5.18 has 31 MUSTs across 4 leaves; HR Security
  Policy addresses only the **procedure** leaf (8 MUSTs). One
  finding → audit reported 1/31 = 3%. Real per-leaf yield: 1/8 = 12%.
- **Re-computed with per-leaf denominator**: median yield is **57%**,
  mean is **57%**. 26% of (doc, leaf) pairs are above 75% yield.
  Only 16% are below 25%.
- **Oracle ground-truth on 2 low-yield docs**:
  - HR Security Policy (3460 chars): 39 unfilled MUSTs, **0** evidenced
    in the doc on full-doc-context check
  - Access Management Process (7249 chars): 34 unfilled MUSTs, **2**
    evidenced (6%) — both small misses ("Shared accounts are prohibited")

**The current single-shot LLM extractor is finding 94-100% of what's
actually in the docs.** The "missing" MUSTs aren't extraction failures —
they're **wrong evidence type for the doc that was uploaded** (the
tenant uploaded a policy; the missing MUSTs need procedure / register /
review-record evidence in different docs).

## What the data definitively says

| Question | Answer |
|---|---|
| Is the extractor missing evidence that's in the docs? | Mostly no (0-6% miss rate on the worst-yielding docs) |
| Are the docs missing the necessary evidence? | Yes — the gap is overwhelmingly "wrong doc type for the missing MUSTs" |
| Did the semantic-search prototype find anything? | Zero grounded findings on 2 docs, 132 verify calls |
| Was the original audit signal real? | The 17% was real; the *interpretation* (= extraction problem) was wrong. Real signal: tenants need to upload more doc types per control. |

## What this means for next direction

**Stop the extraction-engine improvement arc.** The under-discovery
gap at the magnitude originally claimed doesn't exist. The MUST
embedding index + schema_v48 telemetry are retained as foundation —
they correctly measure per-leaf yield going forward — but no more
Phase 2/3 work.

**The real product lever** is the user-facing evidence-class
breakdown surface that the templating arc has been building toward:

    A.5.18 Access Rights (NC)
      Policy:    5/8  MUSTs covered by Access Control Policy.docx
      Procedure: 0/12 → you need procedure evidence; use the template
      Register:  0/6  → use the form/template for revocation register
      Review:    0/5  → upload quarterly review record

That maps onto the templating arc's tenant-authored lanes (templated
upload, form). The 43% gap at median yield is mostly addressable by
**telling the tenant which evidence type they're missing**, not by
re-engineering extraction.

## Artifact ledger

What's kept (foundation cost paid, future surfaces may use):

| Artifact | Status | Future use |
|---|---|---|
| schema_v48 yield/pass-2 telemetry | KEEP | Honest per-leaf yield tracking going forward; UX denominator source |
| `musts_arioncomply` Chroma collection (4133 vectors) | KEEP | Could power "match tenant text → MUST" inside templating wizard; not a re-extraction lever |
| `scripts/build_must_index.py` | KEEP | Rebuild script; idempotent |
| `scripts/prototype_semantic_extract.py` | KEEP | Reference/diagnostic; not productionised |
| /tmp/ground_truth_check.py | NOT COMMITTED | Diagnostic for future "is this MUST in this doc?" questions |
| Original "G3-G6 gap catalog" in this memo | SUPERSEDED | At ≤6% real extraction-failure rate, the gap catalog is over-fitting |

## Carry-forward

**The lesson is itself worth memory** — see
[[feedback-validate-the-denominator]]. I anchored hours of work on a
30-minute query result without validating the denominator. A flawed
denominator can make a moderate problem look catastrophic and
motivate work that misses the real lever.

## Related

- [[feedback-validate-the-denominator]] — the meta-lesson from this
  arc. Validate the denominator of any ratio metric BEFORE building
  infrastructure on it.
- [[tabular-evidence-rows-2026-06-26]] — sibling under-discovery
  fix; that one was a real, mechanically-identifiable gap (multi-row
  evidence thrown away by first-non-empty-per-column logic).
- [[templates-v2-anchors-complete-2026-06-25]] — where the actual
  product win lives. The evidence-class breakdown UI uses the same
  per-leaf MUST counts that this arc surfaced.
- [[must-embedding-index-2026-06-26]] — the index built during this
  arc. Retained; may power templating-wizard text→MUST suggestions
  rather than extraction.
