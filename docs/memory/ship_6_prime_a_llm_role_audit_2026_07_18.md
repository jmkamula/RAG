---
name: ship-6-prime-a-llm-role-audit-2026-07-18
description: "Ship 6'.a — role audit of every LLM site, classified by hallucination risk in a compliance context; safeguard inventory + gap analysis"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6'.a (2026-07-18) — opens Ship 6 arc. Companion to Ship
5'.a but with a different lens: instead of "is the mechanism
consistent," the question is "**should this LLM be here at all,
given the compliance stakes?**"

A security-compliance platform cannot tolerate hallucinated
controls, verdicts, or evidence. Every LLM call site is a
potential vector — but not equally. This memo classifies every
site by the ROLE its output plays in downstream compliance
decisions, inventories the anti-hallucination safeguards in
place, and identifies gaps.

## Role classification framework

Four risk tiers, based on what happens with the LLM's output:

- **DETERMINATIVE** — the LLM's output becomes compliance
  DATA. A finding written to `document_findings`, a posture
  verdict, a persisted evidence claim. Highest stakes;
  hallucination = fake compliance data auditors could rely on.
- **NAVIGATIONAL** — the LLM's output ROUTES or CLASSIFIES.
  Wrong output → wrong retrieval or wrong query type. Medium
  stakes; consensus + retrieval typically dominate.
- **COMPOSITIONAL** — the LLM's output is PROSE to a human.
  Human reads and interprets. Low stakes for the platform's
  correctness; matters for UX + defensibility of what the
  auditor sees.
- **DIAGNOSTIC** — the LLM's output is TELEMETRY or METADATA
  used as a signal, not a fact. Wrong output biases downstream
  signals but doesn't determine them alone.

## Per-site inventory (10 sites)

### 1. `llm_answer.py` compose — chat answer generation
- **Model:** `gpt-4o`  |  **temp:** 0.4  |  **Purpose:** `chat`
- **Role:** COMPOSITIONAL (prose to human)
- **Hallucination surface:**
  * Fabricated control refs in the answer body
  * Missing / wrong verdict tag near a real ref (NC → OFI)
  * Missing [DRAFT] tag on unconfirmed postures
  * Missing cross-framework bridges
  * Off-namespace refs (2013 ISO refs from training data)
- **Safeguards in place:**
  * [[ship-2-prime-casefile-arc-2026-07-15]] preservation-check
    + APPEND-ONLY repair pass — deterministic footer adds any
    dropped required_refs, [DRAFT] tags, verdicts, bridge lines
  * `framework_scope_guard` — post-answer strip of off-namespace
    refs (Layer A namespace validity + Layer B context provenance)
  * `posture_claim_guard` — post-answer strip of unjustified
    verdict adjacencies
  * Case-file digest limits what the LLM sees to compact
    per-turn facts (~2k tokens vs. the 21k-token pre-Ship 2'
    prompts) — reduces the surface area
- **Gap analysis:** The safeguards are strong. The repair pass
  is APPEND-ONLY (never rewrites prose), which preserves human
  interpretability. Off-namespace refs are stripped. Unfounded
  verdict tags are stripped.
  * Residual risk: the LLM could still fabricate PROSE around
    a real ref (e.g. "A.5.18 requires biometric MFA"). The
    prose isn't audit evidence, but a tenant reading it could
    misunderstand their obligations.
  * Mitigation posture: tenant knows the auditor evidence
    lives in Stage-2 / posture_status_log, not chat prose.
    Chat is an EXPLANATION layer over the deterministic facts.
- **Recommendation:** ACCEPT WITH GUARDS. This is the correct
  role for an LLM. Consider a per-turn evaluation signal for
  "prose claims not backed by the digest" (future arc, not
  urgent).

### 2. `llm_answer.py` verify — verification pass
- **Model:** `gpt-4o-mini`  |  **temp:** 0.0  |  **Purpose:** `chat`
- **Role:** NAVIGATIONAL (verdict on the answer)
- **Hallucination surface:** says "pass" when answer is bad,
  or "fail" when answer is fine.
- **Safeguards:**
  * Deprecated in Ship 2' case-file flow (see llm_answer.py:1090)
    — "preservation-check IS our verification"
  * Only runs on non-implementation queries
  * Its output triggers a `correct` pass, not a data write
- **Gap:** minimal — it's a soft signal now
- **Recommendation:** ACCEPT. Consider deprecating entirely
  once we're sure the preservation check subsumes it.

### 3. `llm_answer.py` correct — correction pass
- **Model:** `gpt-4o`  |  **temp:** 0.4  |  **Purpose:** `chat`
- **Role:** COMPOSITIONAL (rewritten prose)
- **Hallucination surface:** same as compose
- **Safeguards:** same as compose (preservation + guards run
  on the corrected output too)
- **Gap:** temperature could be lower on corrections (currently
  inherits the compose temperature); Ship 5'.c already
  identified this. Not shipped in 5'.c because correction
  needs some creative rewriting to fix a bad answer.
- **Recommendation:** ACCEPT. Consider `temperature=0.1-0.2`
  for correction (deterministic-ish rewrite) as a future tune.

### 4. `classifier.py` — intent routing
- **Model:** `gpt-4o-mini`  |  **temp:** 0.1  |  **Purpose:** `classifier`
- **Role:** NAVIGATIONAL (routes to retrieval strategy)
- **Hallucination surface:** wrong intent → wrong short-circuit
  path or wrong retrieval; wrong ref extraction → wrong
  citations
- **Safeguards:**
  * [[ship-1-consensus-arc-2026-07-15]] — 7 deterministic
    signals aggregate BEFORE the LLM. Explicit refs (regex),
    curated lexicon (DOCUMENT_TOPIC_MAP), and retrieval
    dominate. LLM classifier fires only on `insufficient`
    verdict.
  * Curator lexicon is TOP-TIER weight (1.00, per CLAUDE.md
    consensus notes) — curator additions override the LLM
- **Gap:** the LLM classifier is still the fallback. When
  none of the 7 signals fire cleanly, the LLM's decision is
  authoritative for routing.
- **Recommendation:** ACCEPT. The bounded-arbiter design is
  correct. Grow the curator lexicon as new query patterns
  surface. Route selection is not compliance data.

### 5. `consensus/gatekeeper.py` — bounded arbiter
- **Model:** `gpt-4o-mini` (env-overridable)  |  **temp:** 0.0  |  **Purpose:** `consensus_gatekeeper`
- **Role:** NAVIGATIONAL (approves/modifies aggregator's
  tentative decision)
- **Hallucination surface:** could override a signal's decision
- **Safeguards:**
  * Signal C's `question_type` HARD-LOCKED against override
    (`_signals_lock_question_type`)
  * Signal B's `framework` HARD-LOCKED against override
  * Applied only when signals need arbitration (insufficient
    verdict); hard-anchor early-exit skips it
  * Bounded: approves / modifies / rejects — CANNOT invent
- **Gap:** none material for the compliance surface. It's a
  disagreement-resolver, not a fact-writer.
- **Recommendation:** ACCEPT. Well-designed guardrails.

### 6. `intake/enricher.py` — doc metadata JSON
- **Model:** `claude-haiku-4-5-20251001`  |  **temp:** 0.0  |  **Purpose:** `enricher`
- **Role:** DIAGNOSTIC (signal into fingerprint match)
- **Hallucination surface:** wrong doc_type, wrong
  topic_tokens, wrong scope
- **Safeguards:**
  * Output feeds into `signal_precision.py` as ONE signal
    among 4 (target_controls / semantic_controls /
    explicit_refs / llm_extract / topic_tokens)
  * ≥2 signals must corroborate for `fingerprint_match`
    auto-approval
  * Non-corroborated findings go to Stage-1 HITL
- **Gap:** if the LLM confidently mis-types a doc, downstream
  fingerprint matches on other signals could still auto-approve
  the wrong controls. Rare.
- **Recommendation:** ACCEPT. The 2-of-N corroboration gate
  is the right layer.

### 7. `intake/extractor.py` pass1 — extract findings from doc
- **Model:** `claude-sonnet-4-6`  |  **temp:** 0.0  |  **Purpose:** `extractor`
- **Role:** **DETERMINATIVE (highest stakes site in the system)**
- **Hallucination surface:**
  * Fake finding — LLM invents evidence for a control
  * Fake excerpt — LLM writes a quote that isn't in the doc
  * Wrong control_ref binding — LLM binds valid evidence to
    the wrong ref
  * Confidence inflation — LLM says "high confidence" on
    ambiguous match
- **Safeguards:**
  * **Grounding contract** (extractor.py:1541,1591,1603-1605):
    "For each MUST you can ground in verbatim text — Omit any
    MUST you cannot ground. Do not invent quotes. Do not guess."
  * **Excerpt is a required field** — every finding must carry
    verbatim doc text
  * **Post-extract grounding check** — signal_precision.py
    validates the excerpt appears in the doc's text
  * **Critic verifier pass** (site 9 below) — second LLM
    reviews the extractor's output
  * **HITL Stage-1 gate** — every LLM-extracted finding lands
    `pending`; tenant confirms before it counts
  * **Auto-approve requires 2-of-N signal corroboration** —
    LLM alone is not sufficient
  * `inference_source='extracted'` tags LLM-produced findings
    for downstream discipline
- **Gap analysis:**
  * The grounding contract is prompt-only ("do not invent
    quotes"). Verified externally by post-extract check
    that the excerpt actually appears in the source doc.
  * If the LLM invents a quote AND that quote happens to
    substring-match somewhere in the doc, it could pass
    verification while binding to the wrong context.
    Low-probability but non-zero.
  * The critic verifier is a MITIGATION not a hard check.
  * Stage-1 HITL is the strongest safeguard — nothing lands
    without human confirm.
- **Recommendation:** ACCEPT WITH GUARDS. The layered defense
  (grounding + excerpt verify + critic + HITL) is appropriate
  for a determinative site. Consider tightening:
  * Fuzzy-match tolerance on excerpt verification — if the
    LLM misses spacing/punctuation, don't reject; but if the
    LLM synthesizes a plausible-but-fake quote, reject
  * A `document_findings.excerpt_verified: bool` column
    with strict = "verbatim substring" and fuzzy = "≥95%
    match" boolean checks
  * NEW work — worth a Ship 6'.b sub-arc

### 8. `intake/extractor.py` pass2 — per-leaf refinement
- Same as pass1 (same model, temp, prompt shape)
- **Recommendation:** same as pass1

### 9. `intake/critic_verifier.py` — verify extractor output
- **Model:** `claude-sonnet-4-6`  |  **temp:** 0.0  |  **Purpose:** `extractor`
- **Role:** NAVIGATIONAL (confirm / reject / extend
  pre-existing extractions)
- **Hallucination surface:**
  * Rejects a valid finding as "unfounded" → tenant loses
    evidence
  * Confirms an invalid finding as "grounded" → false
    confidence
  * Adds a `flagged_missing_control` that doesn't apply
- **Safeguards:**
  * Rejection is soft — downgrades to Stage-1 pending, not
    permanent removal
  * HITL Stage-1 gate covers both approve + reject paths
  * The critic's own output is prompt-only grounded — it
    doesn't have a hard external check
- **Gap:** the critic is asked to be conservative but there's
  no external verification of its verdicts. It relies on the
  same doc + extractor's excerpts to judge.
- **Recommendation:** ACCEPT. The critic is a soft-signal
  additional layer; HITL is the hard gate.

### 10. `enrichment/tier2_generator.py` — offline node metadata
- **Model:** `gpt-4o-mini`  |  **temp:** 0.2  |  **Purpose:** `enrichment_tier2`
- **Role:** DIAGNOSTIC (metadata baked into RequirementNode
  properties; used as prompt context / retrieval signal)
- **Hallucination surface:**
  * Wrong business_description → tenant reads a wrong
    plain-language paraphrase in chat
  * Wrong query_keywords → biased retrieval for that node
- **Safeguards:**
  * Offline generation with human review of samples before
    full run (see `print_sample_review()` in the module)
  * Doesn't run in tenant runtime — pre-baked once, checked
    in
  * Output is METADATA context, not persisted per-tenant
    compliance data
- **Gap:** the "human review of samples" step depends on the
  operator actually running the sample first. Not enforced
  in code.
- **Recommendation:** ACCEPT. Enrichment is a build-time
  artefact; the compliance stakes are indirect (biases chat
  prose, doesn't produce data).

## Cross-cutting safeguards inventory

Anti-hallucination mechanisms currently in place across the
platform:

1. **Preservation-check + repair pass** (Ship 2') —
   deterministic APPEND-ONLY footer adds dropped refs +
   verdicts + [DRAFT] tags + bridges to chat answers.
2. **framework_scope_guard** — post-answer strip of off-
   namespace refs.
3. **posture_claim_guard** — post-answer strip of unjustified
   verdicts.
4. **Taxonomy short-circuits** — 3 intents (`document_
   inventory` etc.) bypass the LLM entirely with pure DB
   answers. `can_short_circuit + allow_short_circuit` in
   `rag/taxonomy.py`.
5. **Consensus layer** (Ship 1) — 7 deterministic signals
   dominate; LLM classifier + gatekeeper are bounded
   arbiters. Curator lexicon is top-tier weight.
6. **Extractor grounding contract** — required-quote-excerpt +
   post-extract verify the excerpt is in the doc.
7. **Engine verdict is DETERMINISTIC** — per-leaf MUST
   fulfilment logic in `rag/posture/fulfilment_engine.py`; no
   LLM involvement in computing NC/OFI/Comply/N/A.
8. **HITL Stage-1** — every extracted finding lands `pending`;
   tenant confirms.
9. **HITL Stage-2** — engine verdicts land `proposed`; tenant
   approves before they become posture.
10. **Confirmation state machine** — DB triggers enforce
    legal transitions (see [[hitl-two-stage-rollout-gotchas]]).
11. **posture_status_log** — append-only compliance evidence
    audit trail (Ship 4'.b addendum locked this in).
12. **Case-file digest** — LLM sees ~2k-token compact facts,
    not the full 21k-token raw context. Reduces the
    hallucination surface by ~10×.
13. **Auto-approve corroboration gate** —
    `signal_precision.py` requires ≥2-of-N signals to agree
    before an LLM finding auto-approves.

## Where LLM is CORRECTLY absent

Some places the LLM would be tempting but IS NOT used, by
design:

- **Engine verdict computation** — pure Python logic in
  `fulfilment_engine.py`. Compares per-leaf MUST satisfaction
  against thresholds. Deterministic.
- **Posture status writes** — writer sets `finding` based on
  engine output or HITL decision; never an LLM inference.
- **Cascade event triggers** — `rag/cascade/engine.py` fires
  events from CURATED rules (Neo4j edges) + verification-log
  writes. No LLM in the trigger path.
- **Notification producers** (Ship 3') — all deterministic
  triggers on database state changes.
- **API scope checks** (Ship 4') — deterministic policy layer.

This is the load-bearing observation of the audit: **every
compliance-load-bearing decision in the system is
deterministic**. LLMs sit around the edges: reading, summarising,
routing, and drafting evidence proposals that a human confirms.

## Gap summary — Ship 6'.b+ candidates

### Priority 1 — Extractor excerpt-in-doc verification

Right now the extractor prompt says "do not invent quotes."
The post-extract check verifies excerpts substring into the
doc — but the check's rigor isn't documented and I haven't
audited it. Ship 6'.b:
- Confirm the verify happens on EVERY extracted finding
  (not just some paths)
- Add a `document_findings.excerpt_verified` boolean and
  wire the writer to require it
- Fail-loud on unverified findings — never auto-approve them

### Priority 2 — Retrospective on the preservation check

Ship 2's preservation-check has been running for months. How
often does it fire? Is the LLM regularly dropping refs, or is
it rare? Data-driven analysis of `chat_casefile_log` would
tell us whether the LLM is stable enough to trust more, or
brittle enough to constrain more.

### Priority 3 — Chat prose "claim-check"

The compose LLM can generate prose statements that aren't
backed by any digest fact ("A.5.18 requires biometric MFA").
No current mechanism catches this. It's not evidence, but a
tenant could misunderstand their obligations. Consider a
lightweight post-answer scan for claim-shaped statements
(regex: `[Xx] requires ...`, `[Xx] mandates ...`) and either
strip or fact-check against the digest.

### Priority 4 — LLM decision audit trail

Not everything the LLM decides is easily queryable. When did
the classifier route this query? Which gatekeeper decision
modified it? A joined view over `chat_consensus_log` +
`chat_casefile_log` + `ai_call_log` would surface the LLM's
decision path per turn. Useful for auditor review + regression
diagnosis.

### Priority 5 — Model-tier verification per role

The role classification here is my analysis. Codifying it —
maybe as a check that ensures `MODEL_EXTRACTOR` uses a
high-tier model (never `gpt-4o-mini`) — prevents future
regressions.

## Recommendation

**The LLM's role in the platform is correctly bounded today.**
All compliance-load-bearing decisions are deterministic; LLMs
draft, route, and summarize but never decide. The layered
safeguards (grounding + guards + preservation-check + HITL +
deterministic engine) are architecturally right.

**Ship 6 sub-arcs should focus on:**
1. Making the safeguards VISIBLE and MEASURABLE — the
   `excerpt_verified` bool, the preservation-check retrospective
2. Building auditor-facing tools that show the LLM's
   decision trail — supports the eventual "auditor view"
   persona
3. Data-driven tuning — is the LLM stable enough to relax
   guards? Or should we tighten?

No single site needs urgent rework. The system is more mature
than the framing "no room for control hallucination" might
imply — because the compliance data is written by
deterministic code, not by LLMs.

## Ship 6 roadmap ahead

| Sub-arc | Scope |
|---|---|
| **6'.a Audit** | **✓ this arc** |
| 6'.b Extractor excerpt-verification hardening | Priority 1 |
| 6'.c Preservation-check retrospective | Priority 2 (data-driven; how often does repair fire?) |
| 6'.d Chat prose claim-check | Priority 3 (if 6'.c shows the LLM drifts) |
| 6'.e LLM decision-trail joined view | Priority 4 |
| 6'.f Arc retrospective | close |

## Related

- [[ship-5-prime-arc-retrospective-2026-07-18]] — companion
  arc on LLM CONSISTENCY (Ship 5' answered "is the plumbing
  clean"; Ship 6' answers "is the role right")
- [[ship-2-prime-casefile-arc-2026-07-15]] — preservation-check
- [[ship-1-consensus-arc-2026-07-15]] — consensus layer
- [[hitl-two-stage-approval-design]] — HITL gates
- `rag/guards/framework_scope_guard.py` + `posture_claim_guard`
- `rag/casefile/preservation.py` + `rag/casefile/repair.py`
