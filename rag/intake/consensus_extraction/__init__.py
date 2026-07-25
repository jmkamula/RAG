"""
Ship 33 — extraction consensus module.

Extension of Ship 1's chat-consensus architecture to intake extraction.
Per-candidate `(leaf_id, must_id)` decisions via weighted signal
aggregation + bounded LLM arbiter.

See docs/memory/ship_33_prime_a_redux_extraction_consensus_design_2026_07_25.md
for the design memo.
"""
from rag.intake.consensus_extraction.types import (
    ExtractionSignalOutput,
    CandidateVerdict,
    CandidateKey,
)
from rag.intake.consensus_extraction.config import (
    ExtractionConsensusConfig,
    default_config,
)

__all__ = [
    "ExtractionSignalOutput",
    "CandidateVerdict",
    "CandidateKey",
    "ExtractionConsensusConfig",
    "default_config",
]
