# Per-MUST Recall Strategy

Strategic placeholder drafted 2026-06-23 after empirically hitting the
ceiling of single-pass LLM extraction. The previous strategy docs
(intake architecture, LLM provider, framework readiness, road to MVP)
established the *shape* of the platform; this one addresses the
*recall* of evidence extraction — the structural ceiling above which
prompt tweaks no longer help.

## The problem

The product narrative says "upload your policy, the system extracts
evidence per MUST". The engineering reality is:

- LLM extraction is **recall-imperfect by nature**
- Even with per-MUST candidate lists, crosscheck telemetry, and a
  raised emission cap, the LLM misses some MUSTs visible in the text
- Structural blind spots persist regardless of prompt tightening:
  - **Cross-section linking** (e.g. "Version 1.1" in revision history
    + "Approved 22 June 2026" in sign-off row → `approval_target`
    MUST that references the version being approved)
  - **Treating tables as separate per-cell evidence** (sign-off rows
    contain signatory + date + version as distinct MUSTs)
  - **Implicit metadata** (the act of being in a "Reviewed" row
    means review_outcome was satisfied, even without explicit text)

The engine requires per-MUST binding to flip posture. Missed MUSTs =
posture stays NC even when the doc plainly evidences the control.

## Empirical evidence (today's iteration)

Same Access Control Policy.docx, same content, same controls in scope
(A.5.15/16/17/18), three iterations:

| Iteration | Cap | Prompt | Findings | A.5.15 closest leaf |
|---|---|---|---|---|
| 1 (morning) | 15 | original | 14 | management_approval 1/3 |
| 2 (re-extract, same code) | 15 | original | 14 | 1/3 (no change — stable LLM) |
| 3 (cap=60, sign-off prompt) | 60 | with sign-off + revision-history guidance | **17** | management_approval **2/3** (caught approval_date) |

Critical metadata bindings missed in all three:

- `A.5.15:approval_target` (version reference is in revision history, not in approval row)
- `A.5.15:review_date`, `:review_reviewer`, `:review_outcome`, `:review_a518_link` (Reviewed-row + revision history bullets)
- `A.5.16:rev_completeness`, `:rev_residual_cleanup` (revision history bullet text)

The lift from iteration 3 was real (+3 findings, +1 critical metadata
MUST) but still left **A.5.15 at NC**. No leaf reached full satisfaction.

**Conclusion**: prompt tightening + cap raising helped but exposed the
ceiling. A single-pass LLM extraction will never reliably cover
every-MUST-the-doc-evidences, because the LLM optimizes for the most
salient bindings, not for exhaustive recall against a per-MUST list.

## Three architectural directions

### Direction A — Make the form the deterministic completion surface

Reframe the product contract: extraction is *best-effort discovery*,
not *guaranteed coverage*. The form (shipped 2026-06-15, schema_v40)
is the deterministic source of truth for posture.

What changes:
- Product narrative: "extraction-assisted self-assessment" (not "auto-extraction")
- Dashboard makes the per-MUST advisory more aggressive — when extraction
  yields N MUSTs on a leaf but the leaf has N+M unfilled, prominently
  surface "Your doc covers X. Does it also cover Y? [pre-filled form]"
- The form pre-fills with quote candidates the LLM didn't bind but had
  in candidates (cheap retrieval over already-extracted excerpts)

**Pros**: low cost, mostly UX work, honest about LLM limits, gives tenant ownership
**Cons**: tenant burden; doesn't fix recall; relies on tenant attention to fill forms
**Effort**: ~1-2 days (UX surface + pre-fill logic)

### Direction B — Inverted retrieval per unmet MUST

For each unmet MUST on a control with partial evidence, run a focused
LLM call:
> *"Among the uploaded corpus, does any text evidence this specific MUST: '<MUST description>'? Quote verbatim if yes; otherwise return 'no'."*

Guarantees every unmet MUST is *considered* by the LLM. Misses only
where the LLM genuinely judges the doc doesn't have the evidence.

**Pros**: theoretical ceiling = "100% recall on what's actually in docs"
**Cons**: high cost (~150 unmet MUSTs × LLM call per scan = ~$0.50 per
  tenant); needs scheduled-sweep infrastructure (cron / job queue)
**Effort**: ~3-5 days (job queue + per-MUST querying + result writing)
**Cost model**: $0.50 × 1000 tenants × monthly sweep = $500/month at moderate scale

### Direction C — Two-pass extraction at upload time

Pass 1 (current): LLM extraction with per-MUST candidate list (broad)
Pass 2 (new): For each leaf with partial evidence (1+ but <N MUSTs
bound), targeted LLM call:
> *"You previously extracted these MUSTs from this doc: [list]. The leaf '<leaf_label>' has these remaining MUSTs unfilled: [list]. Does the doc evidence any of them? Quote verbatim if yes."*

Doc-scoped (not corpus-scoped). Runs at upload time, not as a periodic
sweep. Targets only leaves where evidence is *adjacent* (partial
coverage) — highest signal-to-noise.

**Pros**:
- Uses everything already built (doc_mappings scope, per-MUST list,
  crosscheck signal)
- Modest cost (~5-10 extra LLM calls per upload, ~$0.10)
- Real-time at upload (no scheduled-sweep infrastructure)
- Has a clear theoretical bound: doc contains the evidence OR it doesn't

**Cons**:
- Doesn't help when LLM passes 1 *misses the whole leaf* (no partial signal to target)
- Adds complexity to `_extract_full` and `_extract_sections`
- Iterative LLM-on-LLM has correlated failure modes

**Effort**: ~1-2 days

## My recommendation

**Ship C as primary; A concurrent.**

C is the highest-leverage fix. It addresses the structural problem
(LLM misses MUSTs adjacent to ones it caught) without changing the
product narrative or shipping new infrastructure. It costs ~$0.10 per
upload at the most expensive case, has a tight theoretical bound, and
plugs into the architecture cleanly.

A is concurrent because **even with C, some recall gap will remain**
(LLM passes 1+2 still miss what the LLM can't see). The form needs to
be a first-class completion path, not a hidden drill-in.

B as future option when:
- Corpus is large enough that "did anything cover this MUST" is hard
  to answer at upload time
- Scheduled-sweep infrastructure exists for other reasons (re-eval
  after framework updates, periodic audit refreshes, etc.)
- A tenant explicitly requests "comprehensive coverage" as a tier

## Cost model

| Path | Per-upload cost | Per-tenant monthly cost (50 uploads) |
|---|---|---|
| Current (pass 1 only) | ~$0.02 | ~$1 |
| **Direction C (pass 1+2)** | **~$0.10** | **~$5** |
| Direction B (corpus sweep) | n/a (per scan) | ~$0.50 per scan × N scans |
| Direction A (form UX) | $0 | $0 (tenant time only) |

At 1000 tenants × 50 uploads/month:
- Current: ~$1,000/month
- With C: ~$5,000/month
- With C + monthly B sweep: ~$5,500/month + $500/month

**Honest framing**: the lift in coverage from C will probably justify
the cost in customer-perceived quality and posture-flip frequency.

## What we DON'T promise

To make this concrete and defensible to customers:

- **Auto-extraction**: we extract what we can; tenant validates
- **100% recall**: we promise *high recall on directly-stated evidence*,
  not perfect recall on inferred / implicit / cross-section linked items
- **No tenant review**: every approved finding requires Stage-1 confirmation
- **Posture flips automatically**: posture flips when *evidence is sufficient
  per the engine model* (multi-leaf, per-MUST), which may require multiple
  artefacts the tenant must understand

This is the boundary between "magic" and "diligent assistance". Compliance
products that promise the former lose audit defensibility.

## Architectural sequence

1. **Now**: write this strategy doc (done — this file)
2. **Next thread (1-2 days)**: implement Direction C — second-pass extraction
   on partial leaves. Eval-gated; baseline on Access Control Policy.docx
   should show post-C extraction at 3/3 management_approval + meaningful
   progress on periodic_review.
3. **Concurrent (1-2 days)**: Direction A UX — dashboard surfaces
   "fill the gaps" prominently; form pre-fill from LLM-extracted candidates
4. **Future**: Direction B when scheduled-sweep infrastructure is needed
   for another reason (re-eval, audit refresh, etc.)

## Open decisions before C is built

1. **Trigger condition for pass 2**: every partial leaf? Or only when
   crosscheck disagreements signal the LLM was confident-but-wrong on
   pass 1? Crosscheck-gated reduces cost but skips legitimately-missed
   leaves. Recommend: **every leaf with 1+ but <N MUSTs covered**.

2. **Pass 2 candidate list**: only unfilled MUSTs (cheapest) or all MUSTs
   (catches re-reading)? Recommend **only unfilled** — cheaper, and pass
   1's bindings are already in document_findings.

3. **Pass 2 confidence threshold**: should pass-2 emissions be auto-tagged
   `confidence='medium'` to reflect the iterative nature? Or trust the
   LLM's self-reported confidence?

4. **Cost capping**: max N pass-2 calls per upload? Recommend **cap at
   leaves-with-partial-coverage; no extra cap**. Doc-scoped naturally bounds.

5. **Telemetry**: new schema column `pass2_findings INT`? Or just
   `extraction_path = 'two_pass'`?

## Prerequisites for executing

1. **Baseline eval**: snapshot current 197-199/199 eval state
2. **Per-doc smoke test set**: Access Control Policy + 2-3 other docs
   with known coverage gaps; measure pre-C and post-C recall
3. **Cost budget agreement**: confirm ~5× cost lift is acceptable
4. **Recall acceptance criteria**: what's "good enough"? 80% of MUSTs
   visible in text? 90%? Quantifies success.

## What this doc isn't

- Not a commit to ship. The architectural pause is the deliverable;
  execution comes when the team decides to invest.
- Not a vendor evaluation. C uses the same Anthropic API as current.
  Direction B may surface vendor cost concerns that loop back to
  `[[llm-provider-strategy]]`.
- Not a UX spec. Direction A's UX needs design work; this only frames it.

## Related

- `[[intake-pipeline-architecture]]` — the architecture this fits into
- `[[per-must-binding-in-extractor-2026-06-15]]` — the B path that
  exposed this ceiling
- `[[extractor-catalog-crosscheck-2026-06-15]]` — the telemetry that
  could gate Direction C's pass-2 trigger
- `[[templates-hybrid-2026-06-15]]` — the form path that makes
  Direction A possible
- `[[feedback-eval-state-drift]]` — eval discipline that gates any new
  extraction path

## Next-thread starter

When this work begins:
1. Baseline current Access Control Policy.docx extraction:
   - Findings count, MUSTs covered per leaf, posture impact
2. Implement pass-2 in `_extract_full` and `_extract_sections`:
   - Detect partial leaves from pass-1 findings
   - Per-partial-leaf focused LLM call with unfilled MUSTs only
   - Merge into findings list with existing dedup logic
3. Re-extract Access Control Policy.docx; compare to baseline
4. If lift is real: eval-validate on the 199-case suite
5. Ship + monitor crosscheck telemetry to validate quality
