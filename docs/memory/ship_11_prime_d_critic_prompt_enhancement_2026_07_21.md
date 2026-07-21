---
name: ship-11-prime-d-critic-prompt-enhancement-2026-07-21
description: "Ship 11'.d — critic prompt enhancement: business_description + MUST-prefix taxonomy + wrong-attribution examples (Pattern 2 from Ship 11'.a)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11'.d (2026-07-21) — Layer-2 fix from the Ship 11'.a
extractor quality plan. Enriches the critic-verifier system
prompt with signals the LLM lacked to verify quote-to-anchor
semantic fit. Targets Pattern 2 (cross-anchor keyword drift, 16%
of Ship 10 rejects).

## Motivation

Ship 10 HITL surfaced 8 rejects where the critic-verifier
confirmed a control because a keyword matched, but the sentence
didn't address the anchor's CORE obligation:

- "Technical safeguards (encryption, access controls, data
  minimization)" → confirmed for A.7.4.1 (Limit collection) + A.7.4.4
  (Minimisation objectives) via mention of "data minimization"
- "Clarify in contracts who is responsible for data accuracy" →
  confirmed for A.7.2.6 (processor contracts) via mention of
  "contracts"
- "Collect only verifiable data where possible" → confirmed for
  A.7.4.1 (collection limit) via mention of "collect"

The critic's design contract is quote-grounding (verbatim) + MUST-
binding. It doesn't verify semantic fit: does the quote's meaning
address WHAT the anchor requires?

Root causes:
- Priming set didn't include anchor `business_description` (the
  curator-authored one-line summary of the anchor's obligation).
  LLM couldn't check semantic alignment.
- MUST-prefix semantics (`proc_` / `reg_` / `rev_` / `scope_` /
  `ropa_`) weren't documented in the prompt. LLM couldn't match
  quote-SHAPE to MUST-shape.

## What shipped

Three targeted enrichments to the critic-verifier prompt +
supporting data flow:

### 1. `business_description` in `control_meta`

`build_control_meta_from_neo4j` now fetches
`RequirementNode.business_description` (coalescing with
`obligation_text` as fallback). Added to the meta dict as
`business_description` key.

### 2. `business_description` on `PrimingControl` + priming block

`PrimingControl` dataclass gains a `business_description` field
(default `""`). `_build_priming_set` populates it from the meta.

`_format_priming_block` renders it as an `obligation:` line under
each control, capped at 300 chars:

    - control_ref: "A.7.2.6"  title: "Contracts with PII processors"  signals: fingerprint + semantic  strength: 3
          obligation: Identify, document + agree the additional Art.28 obligations on the PII processor
          * item:A.7.2.6:proc_contract_terms  [catalog]  DPA references processor obligations

### 3. Enhanced `_CRITIC_SYSTEM_PROMPT` with two new sections

**ANCHOR SEMANTIC FIT — MOST CRITICAL RULE:**
Documents that keyword-overlap is necessary but not sufficient.
Includes 3 concrete Ship 10 wrong-attribution examples as
negative training:
- Subprocessors label → A.7.2.6 (Reject)
- Technical safeguards bullet → A.7.4.1/A.7.4.4 (Reject)
- Contract-accuracy clause → A.7.2.6 (Reject; should be A.7.4.3)

**MUST-BINDING SEMANTICS — MATCH SHAPE TO PREFIX:**
Documents the 5 MUST-prefix families with expected evidence shape
per family:
- `proc_*` needs procedure content
- `reg_*` needs register field data (table cells legitimately satisfy)
- `rev_*` needs review record OUTPUT (audit records with reviewer +
  date + finding), not just documentation of the review
- `scope_*` needs applicability prose
- `ropa_*` needs RoPA-specific register fields

## Prompt cost impact

Pre-11'.d system prompt: ~2100 chars.
Post-11'.d system prompt: ~4900 chars (+130% ≈ +700 tokens).

Per-control priming addition: 1 obligation line, up to 300 chars.
For 10 priming controls, that's ~3000 chars ≈ 750 additional
tokens in the user prompt.

Total addition: ~1500 tokens per critic call. At GPT-4o pricing
this is ~$0.0015 additional per call. Trivial cost for the
expected quality improvement.

## Design bounded by the observable

The prompt change is LLM behavior, not deterministic code. Ship
11'.d makes NO promises about specific catch rates — those depend
on how the LLM responds to the new signals. Ship 11'.e's re-
extraction checkpoint is where we measure impact.

Two things we're specifically watching:

1. **Does the LLM actually leverage `business_description`?** If
   the LLM ignores the obligation line, we've just increased
   token cost without benefit. Signal: does critic REJECT count
   go up after 11'.d?
2. **Does the MUST-prefix taxonomy tighten binding?** Prior data
   showed some findings bound to `rev_` MUSTs with procedure-
   shaped quotes — the taxonomy should push those to `proc_`
   MUSTs or to REJECT.

## What we did NOT change

- Prompt structure — kept confirm/reject/extend/flagged-missing
  contract intact
- Response JSON schema — same shape
- Extend pool logic — unchanged
- Threshold on confidence values — unchanged
- Downstream filters (Ship 11'.b bridge gate, 11'.c content-shape)
  — unchanged; they still run after the critic

## Tests

No new unit tests for the prompt itself — LLM behavior isn't
unit-testable. Ship 11'.e re-extraction against the Ship 10
dataset IS the test: does the reject rate drop to target?

Sanity-checked that:
- Prompt renders end-to-end (imports + string builders work)
- `business_description` fetches from Neo4j via the extended query
- Priming block renders with the new `obligation:` line

## Baseline

Full eval running. Prompt change should not affect chat-side
evals since only the extraction pipeline critic prompt was
touched. Regression signal: if 225/226 drops, some chat surface
happened to depend on extraction state that shifted.

## Ship 11' progress

| Sub-arc | Status |
|---|---|
| 11'.a Extractor quality plan | ✓ |
| 11'.b Bridge source-quality gate | ✓ |
| 11'.c Content-shape filter (MUST-aware) | ✓ |
| **11'.d Critic prompt enhancement** | **✓** |
| 11'.e Re-extraction measurement checkpoint | next |
| 11'.f Arc retrospective | pending |

## Related

- [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] — parent
  plan
- [[ship-11-prime-c-content-shape-filter-2026-07-20]] — the MUST-
  prefix taxonomy `_must_prefix()` used in 11'.c aligns with the
  taxonomy documented in this prompt
- Ship 6'.a LLM role audit — the critic-verifier's "compositional
  with bounded verifier gates" role is preserved; this arc
  enriches the input the LLM sees, not the verifier gates
