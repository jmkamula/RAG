# LLM Provider Strategy (skeleton, 2026-06-15)

Strategic placeholder for the LLM abstraction + multi-provider work.
Drafted at end-of-day pause; not yet a plan to execute. When the
investment turn comes, fill in details and convert to a real strategy
doc + ADR.

## The two drivers

1. **Privacy** — compliance docs contain tenant-sensitive content; some
   sectors (financial, healthcare, EU public) can't contractually send
   data to US-hosted third parties. Multi-tenant + multi-framework
   makes this a hard requirement, not a nice-to-have.
2. **Vendor independence** — protect against price increases, API
   deprecation, vendor strategic shifts. Provide negotiation leverage.
   Both drivers converge on the same architectural answer: provider
   abstraction.

Cost is NOT a driver at our current scale (see § Cost framing). Don't
sell this to the business as cost savings.

## Current state — where Anthropic is locked in

Hardcoded Claude calls across 4-5 modules (auditable via
`grep -rn "anthropic\.\|claude-sonnet" rag/`):

| Module | Purpose | Switch cost |
|---|---|---|
| `rag/intake/extractor.py` | LLM extraction (with per-MUST candidate list) | High — most prompt-engineered surface |
| `rag/intake/enricher.py` | Doc-type + topic-token classification | Medium |
| `rag/classifier.py` | Query intent routing | Medium — eval-sensitive |
| `rag/llm_answer.py` | User-facing answer composition | High — UX-sensitive prose |
| `rag/intake/doc_discovery.py` (indirect) | Filename → leaf matching | Low — mostly deterministic |

Each calls Anthropic's HTTP API directly via `urllib.request`. No
abstraction. Switching providers means refactoring each call site
and reconciling prompt formats.

## Target state — provider abstraction

```python
# rag/llm/provider.py
class LLMProvider(Protocol):
    def chat(
        self,
        system: str,
        messages: list[dict],
        *,
        model_hint: str | None = None,
        max_tokens: int = 2000,
    ) -> str: ...

    def extract_with_document(
        self,
        system: str,
        user: str,
        document_bytes: bytes,
        document_type: str,  # 'application/pdf' etc.
    ) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def supports_vision(self) -> bool: ...

    @property
    def max_context(self) -> int: ...

class AnthropicProvider(LLMProvider): ...
class MistralCloudProvider(LLMProvider): ...      # eu.api.mistral.ai
class MistralSelfHostedProvider(LLMProvider): ... # vLLM endpoint
class OpenAIProvider(LLMProvider): ...            # optional, for diversity
```

Provider selected per-tenant via `tenants.llm_provider` column.

## Investment phases

| Phase | What | Effort | Unblocks |
|---|---|---|---|
| **1. Abstraction** | Pull all call sites behind `LLMProvider`. Eval must stay 197-199/199 | ~2 days | All subsequent phases |
| **2. Second provider** | Plug in Mistral cloud (EU-hosted). Re-run eval. Document per-case quality delta. | ~3 days | Privacy story for EU tenants |
| **3. Per-tenant choice** | `tenants.llm_provider` + provider routing in abstraction layer | ~1-2 days | Per-tenant sovereignty |
| **4. Self-hosted** | vLLM + Mistral Small + monitoring + failover | ~1-2 weeks | Air-gap tenants; full vendor independence |
| **5. Per-task selection** | Different tasks use different models (extractor=Sonnet, enricher=Haiku, classifier=Mistral) | ~1 week | Cost optimization at scale |

**Strict order**: 1 → 2 → 3 → (4 or 5 based on demand).

Doing Phase 2 before Phase 1 means hardcoding a second vendor — same
lock-in problem, different vendor. Phase 1 must come first.

## Eval discipline

Eval suite (`tests/eval_suite.py`, currently 199 cases) is the
validation gate for any provider change. Per phase:

- **Phase 1**: re-run with abstraction enabled, Anthropic provider.
  Expect 197-199/199 (within LLM jitter band).
- **Phase 2**: re-run with Mistral cloud as extraction provider.
  Document case-by-case pass/fail delta. Some cases will fail —
  decide per case whether to (a) accept the regression, (b) loosen
  the assertion to structural, (c) keep Sonnet for this task path.
- **Phase 3**: regression-test the routing logic, not provider quality.
- **Phase 4**: per-case eval with self-hosted endpoint. Expect more
  failures than Phase 2; document and decide.

The 199-case suite is the operational definition of "ready to ship".

## Cost framing

| Scale | Anthropic Sonnet | Mistral Cloud | Self-hosted (GPU 24/7) |
|---|---|---|---|
| Arion today (~50/yr) | ~$2/yr | ~$0.50/yr | $6K-24K/yr |
| 100 tenants × 50/yr | ~$200/yr | ~$50/yr | $6K-24K/yr |
| 10K tenants × 100/yr | ~$50K/yr | ~$12K/yr | $6K-24K/yr (shared) |

**Self-hosted only beats cloud at ~10K tenants.** Below that, it's a
strategic investment funded by privacy/sovereignty budget, not by cost
savings.

Per-task model selection (Phase 5) can shave the cloud bill by 30-50%
by sending classification + enrichment to Haiku-tier models and
keeping Sonnet only for the prompt-sensitive extraction work.

## Pragmatic deployment matrix

Once Phase 3 ships:

| Tenant requirement | Provider |
|---|---|
| Default | Anthropic Sonnet (best quality) |
| EU data residency | Mistral cloud (EU API) |
| Air-gap / regulated | Self-hosted Mistral (vLLM) |

Three providers, one abstraction. Each tenant picks based on their
own compliance posture.

## Open decisions

1. **Cloud Mistral vs self-hosted as the second provider.** Mistral
   cloud (EU API) ships faster, addresses most privacy concerns, has
   better quality than self-hosted Small. Self-hosted is the only path
   for hard air-gap. **Recommend cloud Mistral first**, self-hosted
   when first tenant demands it.

2. **Which Mistral model.** Mistral Small 3.1+ (24B) is the standard
   choice. Pixtral 12B is lighter but vision-only. Mistral Medium 3
   (newer, larger) is closer to Sonnet quality but heavier to host.
   **Recommend Small 3.1+ as the baseline**, escalate to Medium if
   eval gap is unacceptable.

3. **vLLM vs TGI vs Ollama for self-hosting.** vLLM is the production
   standard (OpenAI-compatible API, batched inference, tensor
   parallelism). TGI is similar, HuggingFace-backed. Ollama is dev-
   friendly but not production-grade.
   **Recommend vLLM** for any tenant-facing self-hosted deployment.

4. **PDF extraction split.** Even with vision-capable Mistral
   self-hosted, Sonnet vision is meaningfully better on complex
   layouts. May want PDF extraction to stay on Anthropic for non-
   sensitive tenants even when text extraction goes to Mistral. The
   per-task selection in Phase 5 enables this.

5. **Fallback chains.** When self-hosted GPU is down, do we fall back
   to cloud Mistral? Anthropic? Block the request? **Recommend block
   for air-gap tenants** (their threat model excludes cloud); fallback
   to cloud Mistral for non-air-gap.

## Related

- `[[intake-pipeline-architecture]]` — the intake side that depends on
  the LLM call surface
- `[[per-must-binding-in-extractor-2026-06-15]]` — most recent example
  of LLM-prompt-engineered behavior that would need re-validation
  on a new provider
- `[[feedback-eval-with-each-feature]]` — the discipline that makes
  provider swaps trustworthy
- `[[claude-code-hooks-run-under-sh]]` — sibling pattern of
  environment-dependent abstraction (small but same shape)

## What this doc isn't

- Not an ADR. ADR for the investment decision comes when we pick this
  up for real.
- Not an estimate. Effort ranges are illustrative; firmer numbers
  belong in a real plan.
- Not a vendor evaluation. Quality delta numbers should come from
  actual eval runs, not vendor marketing.

## What's needed before executing

1. **A driver signal**: a real tenant requesting privacy/sovereignty,
   OR a strategic decision to lead with privacy as a differentiator,
   OR a vendor risk event (Anthropic pricing shift / API change).
2. **An eval baseline snapshot** at the moment we start Phase 1, so
   regressions are measurable.
3. **A decision on first-non-Anthropic provider**: Mistral cloud or
   Mistral self-hosted. Most code is shared; deployment path differs.
4. **A budget allocation** if self-hosting is on the table (GPU + ops).
