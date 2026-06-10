---
name: feedback-telemetry-before-trouble
description: "Build observability into new pipeline stages from day one. Today's under-extraction bug (107K-token doc → 1 finding) went undetected because the pipeline had no per-upload quality signals — found only when a human noticed the number looked low."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When shipping a new pipeline stage (extractor, classifier, writer,
xfw_proposer, etc.) — or significantly changing an existing one —
ship the **observability signals** alongside the feature, not as a
post-hoc fix-up after the first incident.

## Why

The intake pipeline shipped without per-upload extraction-quality
metrics. On 2026-06-09 we discovered that a 107K-token risk-
management procedure had extracted only 1 finding because the
docx reader's paragraph walk missed table content. The
`extraction_status='completed'` row looked indistinguishable from
a successful 50-finding extraction. The only reason we caught it:
a human noticed `1 finding` looked low for a procedure doc that
size.

That's not a sustainable detection model. The shape-match bug
(normalizer collision) and the section-narrowing bug were both
caught the same way: a careful human eye on numbers that looked
off. No alert fired. No metric crossed a threshold.

**After the fact** we shipped schema_v35 + the `/quality` endpoint
([[intake-quality-telemetry]]). It now catches the same shape of
bug automatically — drop bucket counters, markdown/paragraph ratio,
candidate vs kept yield. But if those signals had existed BEFORE
the Risk-Integrated doc was uploaded, the under-extraction would
have flagged on the first run rather than after I noticed it
manually.

## Proof points — telemetry caught real bugs same day

The 2026-06-09 schema_v35 quality endpoint caught two extractor
bugs in production within hours of shipping, without manual log
inspection:

1. **Business Continuity and Disruption Response Plan.docx (red)**
   — 0 findings / 2 hallucinated. Red flag pointed straight at the
   grounding check using `doc.full_text` only when the LLM was fed
   `doc.markdown`. Fix: `_evidence_grounded` checks both sources
   (commit f5a4f95). Then yellow on the same doc (1 finding /
   2 hallucinated) → `_evidence_grounded` punctuation-normalises
   before substring match (commit 64cdcc8). Doc went 0 → 3 findings.

2. **HR Security Policy.docx (yellow)** — 9 findings / 50
   candidates = 18% yield. Yellow flag pointed at the union-of-
   matches inflating the denominator. Fix: schema_v36 +
   `primary_candidate_controls` from the top-confidence
   doc_mappings match; only count the umbrella's tight target
   list (commit b248a2b). Also surfaced a missing umbrella YAML
   for HR-shape docs (commit 97e3a93).

Both bugs would have been silent before telemetry — the chat
surface said "completed". They flagged automatically afterwards.

**3rd proof point (2026-06-10): diagnose before generalising.**
ISMS Automation Process.docx looked "table-heavy" (markdown_chars
269K vs paragraph_chars 2K, ratio 113×). I shipped SECTION_BASED
override (commit 8738c0e) + table-prose synthesis (commit e777846)
expecting more findings. Eval was unchanged. THEN inspected the
markdown content: **98.8% was a single embedded base64 screenshot
of all the doc's tables**. The doc isn't table-heavy in the
markdown sense — it's IMAGE-heavy. The real fix was a base64
strip (commit 8aee775). Lesson: the headline metric (md/para
ratio) signalled a problem but not its shape; reading the actual
content was necessary. Telemetry gives you the alert, not the
diagnosis.

## How to apply

When designing or modifying a pipeline stage:

- **Sketch the failure modes upfront**: empty output, partial
  output, hallucinated output, wrong-shape output. For each, what
  numeric signal would catch it?
- **Persist the signals**: a row per pipeline run with the counts.
  Existing pattern: `intake_trace_log` per-stage row + new columns
  for new signals. Don't rely on log-grep — logs are ephemeral and
  not aggregatable.
- **Expose them via an admin endpoint**: per-tenant flag derived
  from thresholds. Operators should be able to ask "show me recent
  runs that look wrong" in one query.
- **Set thresholds conservatively** at first. Tune as patterns
  emerge. Better to flag a few green-runs as yellow than miss a
  real red-run.

## Don't apply this rule when

- The stage is a tiny, in-memory transformer with no failure modes
  (e.g. a string normalizer). Telemetry overhead exceeds benefit.
- The stage is throwaway / experimental and will be deleted within
  the week.
- The stage already inherits telemetry from a parent (e.g. a
  helper called by `extract()` benefits from `intake_trace_log`'s
  drop counts without its own row).

## Related

- [[intake-quality-telemetry]] — the after-the-fact instance of
  this rule being applied.
- [[feedback-eval-with-each-feature]] — the parallel rule for
  evals: ship the test alongside the feature, not as a follow-up.
- [[table-heavy-docx-rescue]] — the under-extraction bug that
  prompted this rule.
