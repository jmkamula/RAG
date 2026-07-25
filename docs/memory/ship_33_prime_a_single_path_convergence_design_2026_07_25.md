---
name: ship-33-prime-a-single-path-convergence-design-2026-07-25
description: "Ship 33'.a — design memo for converging the extractor's parallel fp_findings + llm_findings paths into a single critic-verified path. Ship 11'.d designed critic-verifier as THE path; the concat at extractor.py:309 was a shortcut that reintroduced two-path shape. Ship 32 measurement exposed the cost: 121 fingerprint findings on Processor Ops passed through without semantic-fit review; 9% evidence_text uniqueness. Ship 33'.b implements the convergence."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 33'.a — opens Ship 33 arc (single-path extraction convergence).
Direct response to Ship 32'.b's finding + user pushback: "I thought
we had converged on a single path."

Ship 32 documented the surface: 265 findings, 100% deterministic
grounding_method, but sentence-level multi-attribution (43 fingerprint
findings on one bullet line, 9% evidence_text uniqueness on Processor
Ops). Ship 33 addresses it not by adding another filter but by
completing the convergence Ship 11'.d intended.

## What Ship 11'.d designed vs what shipped

**Design** (`docs/critic_verifier_design_2026_07_11.md`, lines 40-47):

> LLM becomes a **critic-verifier + discoverer**:
> 1. **Critic**: reviews provisional findings from deterministic
>    signals. Confirms with fresh grounding OR rejects.
> 2. **Verifier**: for each confirmed finding, provides a verbatim
>    quote from the document.
> 3. **Discoverer**: extends by identifying additional controls the
>    signals missed.

The intent: fingerprint findings are **inputs to the critic** (not
outputs of extraction). The critic confirms/rejects each; only
confirmed ones survive.

**What shipped** (`rag/intake/extractor.py:290-309`):

```python
if _critic_flag not in ("0", ...):
    llm_findings = _run_critic_verifier_pass(doc, scoped, fp_findings, fp_covered)
...
findings = fp_findings + llm_findings   # ← both sets returned, in parallel
```

Two-path pattern reintroduced. Also inside
`_run_critic_verifier_pass`:

```python
priming = _build_priming_set(fingerprint_hits, ..., max_size=10)
```

The critic only sees 10 fingerprint hits (regardless of how many
exist). On Processor Ops: 121 fingerprint findings, of which the
critic reviewed 10; the other 111 sailed through the concat.

## What convergence looks like

The critic path already contains the right gate:
`_semantic_fit_ok(quote, anchor_desc, embed_fn)` at
`critic_verifier.py:111`. It runs on the LLM's confirmed + extended
output today. In the converged shape, it also runs on the
fingerprint findings that don't make the LLM's priming cap.

Two implementation choices:

### Choice A — raise the priming cap

`_build_priming_set(..., max_size=UNBOUNDED)` — every fingerprint
finding becomes a priming for the LLM. LLM confirms/rejects each.
Retire the concat.

**Cost**: LLM prompt bloats proportionally to `n_fingerprint_findings`.
Processor Ops would need a ~130-priming prompt (~10× current). At
GPT-4o pricing, this is $0.05-0.10 more per doc — trivial in
absolute terms.

**Risk**: LLM context budget. Priming is currently a small section
of the prompt; scaling to 130 primings might crowd out extend_pool
+ instructions.

### Choice B — apply `_semantic_fit_ok` to fp_findings inline (Recommended)

Apply the same embedding gate as the critic's post-LLM step, but
BEFORE the critic call, on every fp_finding. Fp_findings that pass
semantic-fit → survive. Fp_findings that fail → drop. The critic's
LLM pass still runs on the priming subset (top 10) and extend pool
(top 100) as today.

Return path: `_run_critic_verifier_pass` returns
`(semantic-fit-passing fp_findings) ∪ (critic-confirmed) ∪ (critic-extended)`.
Dedupe on `(control_ref, checklist_item_id, evidence_text[:80])`.

The concat at line 309 is retired.

**Cost**: embedding call per fp_finding. Batched, ~100/s. Processor
Ops: ~1s extra latency. No LLM cost delta.

**Risk**: threshold tuning. The semantic-fit threshold in
`_semantic_fit_ok` was tuned for LLM-quote-vs-MUST-description; it
may need re-calibration for fingerprint-match-quote-vs-MUST-description.
The critic-verifier's current use scored a bullet-list sentence
vs "Records of processing MUST includes purposes, categories,
recipients" — same shape.

### Recommendation: Choice B

Simpler, cheaper, aligns with the original single-path intent
without amplifying LLM prompt size. Threshold tuning risk is
bounded — same function that already passes for the LLM path
should carry to the fingerprint path.

## Ship 33'.b implementation plan

1. Extract the fp_finding semantic-fit filter into a helper
   `_filter_fp_findings_by_semantic_fit(fp_findings, priming,
   extend_pool, doc)` inside `_run_critic_verifier_pass`.
2. Apply BEFORE the LLM call so the pruned set is what actually
   contributes to results.
3. Merge into the results list: LLM-confirmed + LLM-extended +
   semantic-fit-passing-fp-findings (dedupe on
   `(control_ref, checklist_item_id, evidence_text[:80])`).
4. Retire the concat at line 309 —
   `findings = _run_critic_verifier_pass(doc, scoped, fp_findings, fp_covered)`
5. Telemetry: add `fp_findings_semantic_fit_kept` /
   `fp_findings_semantic_fit_dropped` counters.
6. Fail-open: if `_semantic_fit_ok` errors on an fp_finding, keep
   it (defensive; don't lose evidence to embedding infra hiccups).

## Ship 33'.c success signals

Re-run measure_ship11_reextraction on the 5-doc corpus:

| Metric | Ship 32 (today) | Ship 33 target |
|---|---|---|
| Total findings | 265 | 150-200 |
| Processor Ops findings | 143 | 40-70 |
| Processor Ops unique evidence_text | 11 (9%) | ≥ 50% |
| Deterministic grounding_method % | 100% | 100% (stays) |
| `fp_findings_semantic_fit_dropped` | — | 60-100 (new counter) |

Failure signals:
- Deterministic % drops (bug in the wiring — findings taking wrong
  extraction_path)
- Findings on a legitimate MUST drop below Ship 10's approve count
  for that MUST (over-tight filter)
- Cost spike (semantic-fit embedding path bottleneck)

## What Ship 33 does NOT do

- **Change the fingerprint catalog** — Ship 28 + 29 shipped the
  catalog fixes; Ship 33 works on the runtime consumer of that
  catalog.
- **Add a per-evidence-text cap** — considered in Ship 32'.c
  retro; retired in favor of Choice B because it's a
  more-independent-filter shape rather than a convergence.
- **Retire the fingerprint path entirely** — fingerprint remains
  the deterministic first pass; only its OUTPUT gets pushed
  through the critic-verifier's gate.
- **Raise priming cap** — deferred; if Choice B under-performs,
  Choice A becomes the follow-on.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **33'.a** (this) | Design memo | Choice B locked; success/failure signals set |
| 33'.b | Implement + re-measure | Semantic-fit applied to fp_findings; measurement shows Ship 32 numbers move to target |
| 33'.c | Eval + retro | Baseline holds; convergence pattern codified |

## Related

- [[ship-32-prime-arc-retrospective-2026-07-25]] — measurement arc
  that surfaced the multi-attribution pattern
- [[ship-11-prime-arc-retrospective-2026-07-21]] — the critic-verifier
  arc whose single-path intent this arc completes
- `docs/critic_verifier_design_2026_07_11.md` — the original design
  doc for the critic-verifier
- [[ship-29-prime-arc-retrospective-2026-07-24]] — anchor injection
  arc that widened the multi-attribution surface
