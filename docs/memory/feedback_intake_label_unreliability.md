---
name: feedback-intake-label-unreliability
description: "Strategic position 2026-06-11: workbook sheet titles AND doc filenames AND column headers are unreliable signals for evidence-type identification — tenants name things by convention, not by spec vocabulary. Fingerprint matching catches the obvious cases; reaching deeper evidence requires data-shape inspection + (optionally) leaf-driven scan. Surfaced by 'so since the headlines and labels cannot be relied on, how will we make sure that we can extract the real value from documents?'"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

User question 2026-06-11, end of the workbook-intake refresh
arc:

  > "so since the headlines and labels cannot be relied on, how
  > will we make sure that we can extract the real value from
  > documents?"

The right strategic frame for current intake architecture.

## What today's session proved about labels

  - **Sheet titles lie.** "Business Partners Assessment" turned
    out to hold per-person NDA / training attestation —
    personnel evidence, not supplier evidence. The title
    suggested A.5.22 supplier review; the data was A.6.3 + A.6.6.
  - **Column headers vary wildly.** "Required Competence" ≠
    "Competency Area" ≠ "Skill"; "Reg ID" ≠ "Risk ID" ≠ "Event
    ID" — all the same semantic role.
  - **Doc filenames vary too.** Security Test Report.docx
    contained `[Example: ...]` placeholder text alongside real
    signoffs and dates; the LLM extracted summary prose as
    evidence; the bridge cascade fired 4 GDPR proposals, 2 of
    them wrong-actor.
  - **Workbook self-metadata sheets** ("This Doc Chng Control")
    match ISMS-change fingerprints on `[doc, change, control]`
    tokens but are workbook-internal version histories, not
    compliance evidence.

Every layer of identification we use — sheet name, column
header, file name — was caught misleading at least once today.
Fingerprint matching catches the common case but is brittle by
design: it trusts labels.

## Failure modes by category

  - **False positive**: fingerprint matches a YAML; data
    underneath doesn't fit. HITL Stage-1 catches these — tenant
    rejects. The visible failure mode today.
  - **False negative**: fingerprint matches nothing; real
    evidence sits unrecognised. HITL doesn't catch these —
    tenant never sees a proposal to reject. The invisible
    failure mode. Today only revealed because we audited the
    proposal table looking for 0-finding orphans.

## Architectural levers we have (today)

  - **Fingerprint matcher** — cheap, fast, deterministic.
    Catches 70-90% on a well-named workbook.
  - **HITL Stage-1 review** — tenant judges each proposal.
    Catches false positives, not false negatives.
  - **`/api/v1/admin/intake/unmatched-patterns`** — logs
    filename token tuples that fell through doc_mappings.
    Surfaces some false negatives but only at the filename
    layer.
  - **Quality telemetry** (schema_v35) — drop buckets +
    coverage signals on intake_trace_log; surfaces docs that
    extracted poorly.

## Architectural levers we don't have (deferred)

  - **Sample-row inspection.** Inspect actual data values in
    the first 3-5 rows of unmatched/low-confidence columns.
    "Joseph Kamula" + "Libor Ballaty" in a "Partner Name"
    column → people, not vendors. Deterministic, no LLM,
    ~50 LOC in workbook_discovery.py. Cheapest improvement.
  - **LLM second-pass on low-confidence matches** (40-60% conf).
    Send sheet header + 3 sample rows to a small LLM,
    judge: "does this fit the leaf's MUSTs?" Per-call cost
    matters; only fires when fingerprint is uncertain.
  - **Leaf-driven scan.** Currently each sheet/doc commits to
    one mapping. Inverse: for each leaf's MUST items, scan
    ALL sheets/docs for evidence of each MUST. Decouples
    extraction from sheet-naming entirely. Bigger refactor;
    biggest payoff against false negatives.
  - **Cross-validation across sources.** Same evidence often
    appears in both workbook AND doc. Agreement raises
    confidence; disagreement flags for review.
  - **Surface low-confidence matches in admin endpoint.**
    Extend `/admin/intake/unmatched-patterns` to also log
    sheets that matched at <40% confidence — those are the
    false-negative risk pool.

## Where to start

Sequence recommendation:

  1. Sample-row inspection + extended unmatched logging
     (cheap, deterministic, observable).
  2. Measure false-negative rate after #1; if still high,
     escalate to LLM second-pass on uncertain matches.
  3. Defer leaf-driven scan until the cheaper signals are
     exhausted — it's a real refactor, not a tweak.

Don't reach for LLM-everywhere until cheap signals are
exhausted. The fingerprint+sample-row combination is the
deterministic floor; LLM is the flexible ceiling. Build the
floor first.

## Related

- [[workbook-orphan-disposition-2026-06-11]] — the project
  work that surfaced this position.
- [[intake-determinism-levers]] — the related "how do we get
  to deterministic state" arc.
- [[intake-quality-telemetry]] — the telemetry layer we'd
  extend.
- [[feedback-telemetry-before-trouble]] — sibling rule: build
  observability alongside new pipeline stages.
