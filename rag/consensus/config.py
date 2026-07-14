"""
Default ConsensusConfig factory + environment overrides.

The defaults in types.ConsensusConfig are the design-time values. This
module lets envs / tenants override without recompiling defaults.
"""
from __future__ import annotations

import os
from typing import Optional

from rag.consensus.types import ConsensusConfig


def _env_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


def default_config() -> ConsensusConfig:
    """Build a ConsensusConfig from module defaults, applying env overrides.

    Env vars honoured (all optional):
      CONSENSUS_REFS_MIN_FLOOR         (float, default 0.20)
      CONSENSUS_REFS_CONFIDENT_FLOOR   (float, default 0.35)
      CONSENSUS_REFS_TIE_BAND          (float, default 0.05)
      CONSENSUS_MIN_CORROBORATORS      (int,   default 2)
      CONSENSUS_MAX_TOP_K              (int,   default 10)
      USE_LEGACY_CLASSIFIER            (bool,  default 1)
                                        false → no LLM fallback on
                                        insufficient; return clarify

    Weight overrides are also available (CONSENSUS_*_WEIGHT) but rarely
    needed for env tuning — those are prime candidates for future
    Postgres pipeline_config once we have log data.
    """
    return ConsensusConfig(
        refs_min_floor        = _env_float("CONSENSUS_REFS_MIN_FLOOR",        0.20),
        refs_confident_floor  = _env_float("CONSENSUS_REFS_CONFIDENT_FLOOR",  0.35),
        refs_tie_band         = _env_float("CONSENSUS_REFS_TIE_BAND",         0.05),
        min_corroborators     = _env_int(  "CONSENSUS_MIN_CORROBORATORS",     2),
        max_top_k_retrieval   = _env_int(  "CONSENSUS_MAX_TOP_K",             10),
        explicit_ref_weight       = _env_float("CONSENSUS_EXPLICIT_REF_WEIGHT",       1.00),
        curated_lexicon_weight    = _env_float("CONSENSUS_CURATED_LEXICON_WEIGHT",    0.30),
        framework_hint_weight     = _env_float("CONSENSUS_FRAMEWORK_HINT_WEIGHT",     0.20),
        session_boost_weight      = _env_float("CONSENSUS_SESSION_BOOST_WEIGHT",      0.10),
        posture_boost_weight      = _env_float("CONSENSUS_POSTURE_BOOST_WEIGHT",      0.15),
        graph_tight_family_boost  = _env_float("CONSENSUS_GRAPH_TIGHT_BOOST",         0.05),
        graph_spread_penalty      = _env_float("CONSENSUS_GRAPH_SPREAD_PENALTY",     -0.10),
        log_full_signals_json = _env_bool("CONSENSUS_LOG_FULL_SIGNALS", True),
        # LLM fallback is always on when consensus is active — it's how
        # we handle queries the deterministic signals can't classify.
        # The FULL kill-switch (skip the whole consensus layer) is a
        # separate env var USE_LEGACY_CLASSIFIER=1 checked at the
        # graph-node wire-up level, not here.
        llm_fallback_enabled  = True,
    )


def consensus_layer_enabled() -> bool:
    """The escape hatch: USE_LEGACY_CLASSIFIER=1 disables the whole
    consensus layer and routes every query through the legacy LLM
    classifier. Default OFF (i.e. consensus IS enabled)."""
    return not _env_bool("USE_LEGACY_CLASSIFIER", False)


def gatekeeper_enabled() -> bool:
    """Ship 1.5 inline gatekeeper toggle. Default ON.

    Set GATEKEEPER_ENABLED=0 to disable the LLM arbiter and let the
    aggregator's tentative decision go straight to the graph node.
    Useful for isolating gatekeeper regressions during tuning."""
    return _env_bool("GATEKEEPER_ENABLED", True)


# Cached process-wide default (env is read once at import; restart to
# pick up new values — matches the rest of the codebase's pattern).
_default: Optional[ConsensusConfig] = None


def get_default_config() -> ConsensusConfig:
    global _default
    if _default is None:
        _default = default_config()
    return _default


def reset_default_config() -> None:
    """Test helper — clears the cached default so env changes take effect."""
    global _default
    _default = None
