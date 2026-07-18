"""
Central LLM-model configuration.

One source of truth for every LLM model choice across the
codebase. Anything that picks a model should import from here —
never hardcode a string like "gpt-4o-mini" in a call site.

Ship 5'.a audit found model names scattered across ~10 files as
default arguments. Ship 5'.d consolidates them here so future
model migrations are one edit per role instead of a global grep.

Roles + rationale (from Ship 5'.a audit):

  MODEL_CHAT_ANSWER    — long-form compliance answer prose.
                          Heavy reasoning + citations. Currently
                          gpt-4o. Used by rag/llm_answer.py compose.

  MODEL_CHAT_VERIFY    — small JSON verdict on an answer's
                          groundedness. gpt-4o-mini. Used by
                          rag/llm_answer.py verify+correct.

  MODEL_CLASSIFIER     — small structured intent decision.
                          gpt-4o-mini. Used by rag/classifier.py.

  MODEL_CONSENSUS_GK   — bounded arbiter in the Ship 1 consensus
                          layer. gpt-4o-mini. Used by
                          rag/consensus/gatekeeper.py. Overridable
                          via GATEKEEPER_MODEL env for A/B tests.

  MODEL_EXTRACTOR      — long-form structured extraction from
                          documents (JSON out). claude-sonnet-4-6.
                          Used by rag/intake/extractor.py pass1+
                          pass2 and rag/intake/critic_verifier.py.

  MODEL_ENRICHER       — small structured JSON enrichment
                          (doc_type / topic_tokens / scope).
                          claude-haiku-4-5-20251001. Used by
                          rag/intake/enricher.py.

  MODEL_ENRICHMENT_T2  — offline enrichment JSON generation for
                          RequirementNode metadata (business_
                          description, query_keywords). Currently
                          gpt-4o-mini. Used by
                          enrichment/tier2_generator.py.

## Env overrides

Any of these can be overridden without a code change via env
var, using the constant name uppercased. Example:

    export MODEL_CHAT_ANSWER="gpt-4o-2025"
    export MODEL_EXTRACTOR="claude-opus-4-7"

Useful for A/B tests + partner-specific pinning. Callers should
prefer the constant over `os.getenv` scattered across the tree.

## Migrating a role

To swap a role's model:
  1. Edit the constant here
  2. Re-run affected evals (chat models → tests/eval_suite.py;
     extractor → run a doc through the intake pipeline)
  3. Update the pricing entry in `rag/ai_trace.py::_MODEL_PRICING`
     if the new model has different pricing
"""
from __future__ import annotations
import os


def _model(role: str, default: str) -> str:
    return os.getenv(role, default)


# ── Chat pipeline ─────────────────────────────────────────────────────
MODEL_CHAT_ANSWER    = _model("MODEL_CHAT_ANSWER",    "gpt-4o")
MODEL_CHAT_VERIFY    = _model("MODEL_CHAT_VERIFY",    "gpt-4o-mini")
MODEL_CLASSIFIER     = _model("MODEL_CLASSIFIER",     "gpt-4o-mini")
MODEL_CONSENSUS_GK   = _model("GATEKEEPER_MODEL",     "gpt-4o-mini")  # existing env name for A/B

# ── Intake pipeline ───────────────────────────────────────────────────
MODEL_EXTRACTOR      = _model("MODEL_EXTRACTOR",      "claude-sonnet-4-6")
MODEL_ENRICHER       = _model("MODEL_ENRICHER",       "claude-haiku-4-5-20251001")

# ── Offline enrichment ────────────────────────────────────────────────
MODEL_ENRICHMENT_T2  = _model("MODEL_ENRICHMENT_T2",  "gpt-4o-mini")


def all_models() -> dict:
    """Return a snapshot of every model constant + its current value.
    Useful for diagnostics + smoke tests."""
    return {
        "MODEL_CHAT_ANSWER":    MODEL_CHAT_ANSWER,
        "MODEL_CHAT_VERIFY":    MODEL_CHAT_VERIFY,
        "MODEL_CLASSIFIER":     MODEL_CLASSIFIER,
        "MODEL_CONSENSUS_GK":   MODEL_CONSENSUS_GK,
        "MODEL_EXTRACTOR":      MODEL_EXTRACTOR,
        "MODEL_ENRICHER":       MODEL_ENRICHER,
        "MODEL_ENRICHMENT_T2":  MODEL_ENRICHMENT_T2,
    }
