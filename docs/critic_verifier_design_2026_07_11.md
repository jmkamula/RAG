# Critic-Verifier + Discoverer — LLM Role Redesign

**Started 2026-07-11.**  Follow-on from the signal-fusion arc.
Shifts the LLM from "primary discovery worker" (scans against candidate
controls to find findings) to "critic-verifier + discoverer" (validates
what deterministic signals proposed, extends where evidence exists in
the body).

## Motivation

Current pass-1 architecture (as of Wave 4c):
- Deterministic signals (fingerprint / semantic / explicit_refs) narrow
  the doc to `scoped_leaf_ids`
- Fingerprints produce findings on some MUSTs, excluding them from LLM scope
- LLM extraction runs on the remaining unbound MUSTs
- Signal-fusion gate (Wave 3 + 4a) decides which auto-approve

Problems this creates:
1. **Fingerprint exclusion locks the LLM out**: DPIA doc got 1 fingerprint
   hit on A.7.2.5:proc_assessment_scope → LLM never saw the other A.7.2.5
   MUSTs (proc_trigger_criteria, reg_dpia_register, rev_dpia_reviewer).
2. **Signals don't self-validate**: fingerprint's hit is trusted verbatim;
   no LLM independent read to confirm the quote actually maps to the MUST.
3. **Anchoring on filename-based scoping**: Consent Management doc had
   `doc_mappings` fail to target the specific consent controls; even
   though semantic top-K + fingerprints DID identify them, the Wave 3
   gate treated target_controls' silence as disagreement.
4. **No LLM-driven discovery**: the LLM sees a narrow scoped list; can't
   independently identify controls signals missed.

Result on Arion:
- DPIA doc: 1 finding (should have been ~4-6)
- Consent Management doc: 25 fingerprint hits, ALL pending Stage-1 (should
  have auto-approved the strongly-corroborated ones)

## Design

### Role shift

LLM becomes a **critic-verifier + discoverer**:

1. **Critic**: reviews provisional findings from deterministic signals.
   Confirms with fresh grounding OR rejects.
2. **Verifier**: for each confirmed finding, provides a verbatim quote
   from the document (same grounding filter as current).
3. **Discoverer**: extends by identifying additional controls the
   signals missed, provided evidence exists in the document.

### Prompt shape

```
DOCUMENT: {doc.markdown or doc.full_text — capped ~50K chars}

DETERMINISTIC SIGNALS SAY THE DOC PROBABLY COVERS THESE CONTROLS:
{priming_set — 5-10 controls, each with:
  - control_ref (e.g. A.7.2.3)
  - control_title (e.g. Consent process determination)
  - signal_source (e.g. "fingerprint + semantic top-K")
  - candidate MUSTs (with descriptions)
}

ADDITIONAL CONTROLS THAT COULD PLAUSIBLY APPLY (extend pool):
{extend_pool — top-100 semantically-close controls, each with:
  - control_ref
  - control_title
  - 1-line description
}

INSTRUCTIONS:
STEP 1 — CONFIRM/REJECT the priming set. For each control:
  * CONFIRM if you can ground the fit in a VERBATIM quote from the
    document. Provide (control_ref, checklist_item_id, verbatim_quote,
    confidence).
  * REJECT if the signal was wrong. Provide (control_ref, reason
    for rejection).

STEP 2 — EXTEND. Identify OTHER controls in the extend pool that this
document covers, based on evidence in the body. For each additional
control:
  * (control_ref, checklist_item_id, verbatim_quote, confidence)
  * Must be from the extend pool. If you believe the doc covers a
    control NOT in the pool, flag with: {"flagged_missing_control":
    "your best guess ref", "reason": "..."} — for catalog feedback.

RULES:
- Every quote must appear verbatim in the document body.
- Rejecting a signal is better than fabricating a confirmation.
- Being wrong is worse than being cautious.
- Do NOT reference control refs outside the extend pool (except
  as a flagged_missing_control).

Respond with JSON:
{
  "confirmed": [
    {"control_ref": "A.7.2.3", "checklist_item_id": "item:A.7.2.3:proc_when_consent_required",
     "quote": "...", "confidence": "high"},
    ...
  ],
  "rejected": [
    {"control_ref": "A.7.5.2", "reason": "no transfer destination content in the doc"},
    ...
  ],
  "extended": [
    {"control_ref": "A.7.2.4", "checklist_item_id": "item:A.7.2.4:proc_freely_given_test",
     "quote": "...", "confidence": "medium"},
    ...
  ],
  "flagged_missing_control": [
    {"guess_ref": "A.5.19", "reason": "doc mentions supplier contract review but ref not in pool"}
  ]
}
```

### Priming set builder

```python
def _build_priming_set(
    doc:             ParsedDocument,
    fingerprint_hits: list[dict],   # from _fingerprint_extract_matches
    semantic_top_k:   set[str],     # from semantic_controls_in_scope
    explicit_refs:    set[str],     # from doc.explicit_refs
    max_size:         int = 10,
) -> list[dict]:
    """Return the priming set — 5-10 controls the deterministic signals
    identified. Each carries its signal source for LLM context.

    Ranking heuristic (highest score first):
      - explicit_refs match      → 3 points (author self-cite is strongest)
      - fingerprint match        → 2 points (deterministic keyword hit)
      - semantic top-K position  → 1 point (fuzzy semantic proximity)

    Cap at max_size. Below-max_size sets are also fine — quality > quantity.
    """
```

### Extend pool builder

```python
def _build_extend_pool(
    doc:         ParsedDocument,
    tenant_stds: list[str],
    pool_size:   int = 100,
) -> list[dict]:
    """Query the leaf-level Chroma collections (iso27001_2022 /
    iso27701_2019 / gdpr_2016_679) with doc content, return top-K
    controls with 1-line descriptions. This is the LLM's escape
    hatch for discovery beyond the priming set.
    """
```

### New pass-1

```python
def _llm_extract_critic_verifier(
    doc:              ParsedDocument,
    priming_set:      list[dict],
    extend_pool:      list[dict],
    api_key:          str,
) -> list[DocumentFinding]:
    """Single focused LLM call. Prompt as above. Parse structured
    response into DocumentFindings. Same grounding filter as current
    pass-1 applies to `quote` field."""
```

### Feature flag

`USE_CRITIC_VERIFIER_PASS` env var. Default False. When True, replaces
current pass-1 in extractor.py's extract_findings pipeline. Old pass-1
+ pass-2 code stays intact as fallback.

### A/B evaluation

Re-extract Arion's ~15 uploaded 27701 docs under both paths:

| Metric | Current pipeline | Critic-verifier | Direction |
|---|---|---|---|
| distinct_musts_bound | baseline | new | Higher is better (discovery) |
| findings_kept | baseline | new | Both should be similar / new higher |
| dropped_hallucinated | baseline | new | Lower is better (precision) |
| Stage-1 rejection rate after 7d | baseline | new | Lower is better (tenant trust) |
| yield_ratio_pct | baseline | new | Higher is better |
| Cost per doc ($) | baseline | new | Bounded — target ≤2x current |

If new pipeline wins on discovery + doesn't regress precision (Stage-1
reject rate) + cost is bounded, flip default. Otherwise iterate on
prompt.

## Not scope

- **Streaming responses**: batch JSON is fine for now.
- **Function-calling API**: JSON schema in the response is simpler than
  Anthropic tool-use / OpenAI functions. Revisit if the LLM misbehaves.
- **Multi-turn refinement**: single-shot with structured output. If we
  see the LLM stumble on complex docs, add a refinement turn later.

## Deferred to sibling arcs

- **Wave B (embedding raw HTTP)**: the extend pool query hits Chroma
  which uses openai SDK for embeddings. Wave B removes that SDK dep.
- **Wave C (local deployment)**: with Wave B done, both LLM + embedding
  endpoints can point at a local vLLM/ollama.

## Success criteria

- DPIA doc: goes from 1 finding to 4+ findings (more A.7.2.5 MUSTs bound)
- Consent Management doc: >50% of the 25 fingerprint hits auto-approve
  (LLM confirms them → 2 body-evidence signals agree → gate passes)
- No regression on evaluation cases the current pipeline handles well
- Cost per doc: ≤2× current baseline
