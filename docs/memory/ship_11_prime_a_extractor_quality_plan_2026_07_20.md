---
name: ship-11-prime-a-extractor-quality-plan-2026-07-20
description: "Ship 11'.a — extractor quality enhancement plan from Ship 10 HITL review; 5-pattern taxonomy + hybrid architecture"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11'.a (2026-07-20) — enhancement plan for the intake
extraction pipeline. Follows a 97-finding Ship-10 HITL review
that surfaced 5 systematic patterns in the 49 rejected
findings.

## Origin — Ship 10 HITL review

On 2026-07-20, walked through 44 controls / 97 pending
document_findings across 5 documents (Data Quality Accuracy,
DPIA Procedure, RoPA, Consent Management, Processor
Operations). Session outcome: **48 approved, 49 rejected**.

The rejects clustered into 5 patterns; the critic-verifier
(Ship 2026-07-11 to 2026-07-13, Phase 6 A/B validated +40%)
IS running on the pipeline and doing its designed job — the
gaps are next-tier concerns the arbiter design doesn't cover.

## What the critic-verifier catches (design contract)

The critic-verifier pattern in `rag/intake/critic_verifier.py`
runs a bounded LLM arbiter + extender on the priming set from
deterministic signals (fingerprint / semantic / explicit refs):

- **Arbiter (confirm/reject)** for each priming control:
  verbatim-quote grounding + MUST-binding selection
- **Extender**: propose ADDITIONAL controls from a grounded
  top-100-pool (can't invent refs)
- **Flag-missing**: catalog feedback signal for refs the doc
  covers but that aren't in the pool

Post-critic gates already in place:
- `_evidence_grounded()` (Ship 6'.b) — punctuation-normalised
  verbatim substring check
- MUST-binding validity (only bind to MUSTs in the anchor's
  MUST_CONTAIN set)
- `strip_markdown_escapes` on stored excerpt (Ship 7'.d + 8'.a)

## What it doesn't catch — the 5 patterns

### Pattern 1 — Field-label matching (8 rejects, 16%)

RoPA/table field labels get bound to specific-content MUSTs.
Verbatim quote IS the label; critic can't distinguish
structural markup from substantive prose.

- "Subprocessors / Any third parties involved" → A.7.2.6 processor contracts
- "Retention Period / Timeframe for keeping the data" → A.7.4.7 retention schedule
- "International Transfers / Details of transfers outside the EU/EEA" → A.7.5.1/2 transfer basis

**Root cause:** No content-shape signal reaches the critic.

### Pattern 2 — Cross-anchor keyword drift (8 rejects, 16%)

Single keyword drags a sentence to the wrong anchor. LLM
confirms because quote is verbatim, but the sentence doesn't
address the anchor's core obligation.

- "Technical safeguards (encryption, access controls, data minimization)" → A.7.4.1 collection limit + A.7.4.4 minimisation objectives
- "Clarify in contracts who is responsible for data accuracy" → A.7.2.6 processor contracts (should be A.7.4.3 accuracy)
- "Collect only verifiable data where possible" → A.7.4.1 (should be A.7.4.3)

**Root cause:** Critic prompt lacks anchor semantic scope —
`business_description` from Neo4j not surfaced; MUST-prefix
taxonomy (`proc_/reg_/rev_/scope_`) not exposed.

### Pattern 3 — Fingerprint fragment matches (8 rejects, 16%)

Fingerprint layer matches short fragments and section headers.
Critic confirms because header IS verbatim.

- "Return, Transfer or Deletion of PII (A.8.3.2 / B.8.4.2)" — bare section header
- "This procedure applies to all processing activities..." — scope-statement fragment
- "obtains, records, and manages consent" — verb-fragment mid-sentence

**Root cause:** Fingerprint proposals aren't filtered by
match-substring substance before priming set is built.

### Pattern 4 — Bridge multiplier (17 rejects, 35% — biggest source)

Cross-framework bridges propagate weak source findings 3-4x
across target controls.

- A.7.2.6 (subprocessor label) → A.5.19 + A.5.20 + A.5.22 across 4 docs = **12 rejects**
- A.7.2.8 (wrong-anchor Consent Register) → A.5.9 asset register bridge = 2 rejects
- A.7.4.7 (retention label) → A.5.33 records-protection bridge = 2 rejects
- A.7.4.8 (Odoo-only tenant) → A.7.14 physical-disposal bridge = 1 reject

**Root cause:** Bridges fire in a separate xfw expansion stage
AFTER the critic-verifier. Not gated by the critic verdict; not
gated by source-finding confidence, shape, or MUST-binding
state.

### Pattern 5 — Tenant applicability ignored (1 reject, 2%)

Bridges + extended findings fire regardless of `client_facts`
applicability flags.

- A.7.14 (physical disposal of equipment) proposed for
  Odoo-only tenant → should be N/A per applicability

**Root cause:** No `client_facts` consultation in extraction or
bridge stages.

## Hybrid architecture — 3 layers

Rather than one big fix, the patterns naturally split across 3
architectural layers:

### Layer 1: Pre-critic filters (deterministic, no LLM)

Filters that constrain the priming set before it reaches the
critic prompt.

- **Content-shape tagging** (Pattern 1): mammoth markdown
  carries structural cues — `|` for table cells, `#` for
  headings. Extractor tags each candidate excerpt with its
  structural role; critic prompt only accepts `prose_sentence`
  quotes for confirmation.
- **Fingerprint minimum-substance** (Pattern 3): fingerprint
  proposals whose match-substring is <40 chars OR matches a
  header/bullet pattern get dropped before priming.
- **Tenant applicability** (Pattern 5): at extraction start,
  load `client_facts`. Suppress anchors from priming when
  facts contradict (A.7.3.10 when
  `automated_decision_making=false`, A.7.14 when
  `physical_infrastructure=false`, etc.).

Cheap, mechanical, low LLM cost. Catches ~34% of rejects.

### Layer 2: Critic prompt enhancement (LLM in-loop)

Enrich the arbiter prompt with signals the LLM can act on.

- **Anchor semantic scope** (Pattern 2): include
  `RequirementNode.business_description` (curator-authored,
  already in Neo4j) per priming control. Instruct: "The quote
  must address the CORE OBLIGATION described in
  business_description, not tangential mentions."
- **MUST-prefix taxonomy** (Pattern 2): expose the
  `proc_/reg_/rev_/scope_` semantic to the LLM. Instruct:
  "When picking MUST binding, match quote-shape to MUST
  prefix: `proc_*` needs procedure prose, `reg_*` needs
  register field entries, `rev_*` needs review-record content."
- **Reject-preferred instruction reinforcement**: existing
  prompt says "rejecting a wrong signal is better than
  fabricating a confirmation" — reinforce this with concrete
  examples of over-attribution in the prompt.

More prompt tokens (~+400 per call). Catches ~16% of rejects.

### Layer 3: Post-critic gates (deterministic, no LLM)

Gates that filter after the critic has spoken.

- **Bridge source-quality gate** (Pattern 4): xfw bridges only
  propagate when the source finding satisfies:
  - `confidence >= medium`
  - `checklist_item_id IS NOT NULL` (MUST-bound) OR
    `LENGTH(excerpt) >= 40` (substantive)
  - `inference_source != 'xfw_bridge'` (no bridge-of-bridges)
- **Tenant applicability re-check** (Pattern 5): bridges also
  respect `client_facts` — physical bridges suppressed for
  Odoo-only tenants, joint-controller bridges suppressed
  when `role_joint_controller=false`, etc.

No LLM. Catches ~35% of rejects.

## Sub-arc sequencing

Recommended order — impact-first, then progressive coverage:

**11'.a — Design memo** (this doc)

**11'.b — Bridge source-quality gate (Layer 3)** — biggest hit
Standalone gate in xfw expansion path. Deterministic,
low-risk, ~1 day. Catches Pattern 4 (17 rejects, 35%).
Success metric: bridge rejection rate on next HITL review
drops below 5.

**11'.c — Pre-critic filters bundle (Layer 1)** — mechanical wins
Content-shape tagging + fingerprint min-substance + tenant
applicability. Deterministic, ~2-3 days. Catches Patterns
1/3/5 (17 rejects, 34%).
Success metric: field-label + fragment + non-applicable
rejects drop to near-zero.

**11'.d — Critic prompt enhancement (Layer 2)** — semantic layer
`business_description` + MUST-prefix taxonomy + reinforced
reject-preferred instruction. LLM change with A/B evaluation.
~1-2 days.
Success metric: cross-anchor drift rejects drop below 3.

**11'.e — Measurement checkpoint** — re-extract Ship 10 docs
Re-run extraction on the 5 docs Ship 10 reviewed. Measure new
rejection rate. Confirm the 3 layers compose without
regression. ~half day.

**11'.f — Arc retrospective** — codify what worked

## Success metrics

- **Overall rejection rate**: baseline 49/97 = **51%** →
  target < 25%
- **Per-pattern rejection reduction**:
  - Bridges: 17 → < 5 (post-11'.b)
  - Field labels: 8 → < 2 (post-11'.c)
  - Fingerprint fragments: 8 → < 2 (post-11'.c)
  - Tenant applicability: 1 → 0 (post-11'.c)
  - Cross-anchor drift: 8 → < 3 (post-11'.d)
- **No regression** in existing approves: re-extract must not
  drop findings the Ship 10 review approved.

## What Ship 11 does NOT tackle

- **New signals beyond client_facts**: e.g. tenant industry,
  scope of enrolment. Deferred — client_facts already carries
  most applicability flags.
- **Re-training the semantic embedding**: separate arc if
  needed.
- **Critic verdict caching**: same doc + same signals should
  yield same critic verdict; a cache would reduce cost. Not
  urgent.
- **Multi-turn critic** (critic sees its own output + a follow-
  up prompt): too complex for the return; would need a full
  ablation study.

## Open design questions

1. **Bridge propagation source-quality threshold**: is
   `confidence >= medium` the right bar, or should we require
   `high`? Ship 10 data: most rejected bridges were `medium`
   confidence. Might need `high` — but that would also drop
   some legitimate mediums.

2. **Content-shape signal**: mammoth's markdown output
   preserves table structure, but PDFs and TXT files don't
   carry table markup. Fallback heuristics needed for those
   paths (line-length, punctuation density, colon-separator
   detection).

3. **Critic prompt token budget**: adding
   `business_description` per priming control could inflate
   prompt to 4-5x current size when the priming set is large.
   Ship 11'.d needs a mechanism to summarise or truncate.

## Baseline

No code. Design memo only.

## Related

- Ship 10 HITL review session (2026-07-20, no dedicated memo —
  this doc IS the follow-up)
- Critic-verifier arc (2026-07-11 to 2026-07-13, Phase 6
  A/B validation)
- Ship 6'.b `_evidence_grounded` gate
- Ship 7'.d + 8'.a `strip_markdown_escapes` chain
- Ship 9'.c `program_review` doc_mappings — could reduce
  extraction fallback further
