"""
Central embedding-model configuration.

One source of truth for the vector-embedding model used across
all Chroma collections. Anything that indexes or queries vectors
should import from here — never hardcode a model name.

Ship 5'.b (2026-07-18) consolidated all 4 collections onto
`text-embedding-3-large`. The historical split (RequirementNode
collections on -large, musts_arioncomply on -small) was
cost-driven; at ~6,000 total rows across all collections, the
full re-index cost is <$0.25 so the split saved nothing
meaningful but introduced a same-dimension silent-swap risk
(see [[ship-5-prime-a-llm-audit-2026-07-18]]).

Constants:

  EMBED_MODEL_STANDARD  — the openai model name used for all
                          collections (index + query)
  EMBED_DIM             — the vector dimension the model
                          produces; useful for validation
  EMBED_PROVIDER        — "openai" — provider hint for
                          vector/indexer.py's factory paths

Adding a new collection? Just:

    from rag.embedding_config import EMBED_MODEL_STANDARD
    from vector.indexer import VectorIndexer, OpenAIEmbeddingFunction

    idx = VectorIndexer(embedding_model=EMBED_MODEL_STANDARD)

Migrating to a different model? Change the constant here,
run `python3 scripts/reindex_all.py`, done. That's the whole
migration story.
"""
from __future__ import annotations


EMBED_MODEL_STANDARD: str = "text-embedding-3-large"
EMBED_DIM:            int = 3072
EMBED_PROVIDER:       str = "openai"


def embedding_function_name() -> str:
    """Return the canonical `embedding_function_name` value that
    `vector/indexer.py::OpenAIEmbeddingFunction.name()` produces
    for this config. Callers can check stored collection metadata
    against this without re-instantiating the embedding function.
    """
    return f"openai-{EMBED_MODEL_STANDARD}"
