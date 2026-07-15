"""
CaseFile — single source of truth for one chat turn's ground truth.

The CaseFile wraps the ResolvedContext + SessionContext + intent as a
read-only record that both the LLM digest builder and the preservation
check consult. The LLM sees a compact digest (~1-2k tokens) rendered
from this file; the preservation check reads the full file to verify
the LLM's answer didn't drop mandatory refs / verdicts / bridges.

Design principles:
  1. No data reshaping — the CaseFile holds references, not copies.
     Downstream code should not need to re-fetch from ResolvedContext.
  2. Accessors materialise on demand — `posture_by_ref()`,
     `xfw_bridges()`, etc. compute views but don't cache; small
     surface, cheap to call.
  3. Minimal deps — this module should be importable without pulling
     most of the codebase, so tests can construct fixtures easily.
"""
from rag.casefile.types import CaseFile

__all__ = ["CaseFile"]
