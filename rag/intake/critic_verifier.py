"""
Critic-verifier + discoverer — LLM role redesign for pass-1 extraction.

Phase 2+3 of the critic-verifier arc (2026-07-11). See
docs/critic_verifier_design_2026_07_11.md for the full plan.

This module provides two PURE helpers (no LLM calls yet — those come
in Phase 4):

  _build_priming_set(fingerprint_hits, semantic_top_k, explicit_refs)
    → 5-10 controls the deterministic signals identified, ranked by
    signal strength. Each carries the signal source so the LLM prompt
    can show provenance.

  _build_extend_pool(doc_text, tenant_stds, pool_size=100)
    → top-100 semantically-close controls from the leaf-level Chroma
    collections. The LLM's escape hatch for discovery beyond the
    priming set. Grounded — refs guaranteed to be in the catalog.

Both are pure functions (Chroma is read-only). Testable without any
LLM cost. Wired into `_llm_extract_critic_verifier` in Phase 4.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Signal-strength scoring for the priming set. When a control appears
# via multiple signals, all sources count — but the highest-strength
# source drives ranking.
_SIGNAL_STRENGTH = {
    "explicit_ref":  3,   # author self-cite — strongest
    "fingerprint":   2,   # deterministic keyword hit on curated MUST
    "semantic":      1,   # fuzzy semantic proximity
}


@dataclass
class PrimingControl:
    """One entry in the priming set."""
    control_ref:     str
    control_title:   str
    signal_sources:  list[str]                 # e.g. ["fingerprint", "semantic"]
    strength_score:  int                       # sum of _SIGNAL_STRENGTH per source
    candidate_musts: list[dict] = field(default_factory=list)
        # MUSTs the LLM should verify/confirm
        # each: {"must_id": ..., "text": ..., "source": ...}


@dataclass
class ExtendPoolControl:
    """One entry in the extend pool — the escape hatch."""
    control_ref:  str
    standard_id:  str
    title:        str
    description:  str   # 1-line from curation


def _build_priming_set(
    fingerprint_hits: list[dict],
    semantic_top_k:   Optional[set[str]],
    explicit_refs:    Optional[set[str]],
    control_meta:     dict[str, dict],
    max_size:         int = 10,
) -> list[PrimingControl]:
    """Return the priming set — 5-10 controls the deterministic signals
    identified. Ranked by aggregate signal strength.

    Args:
      fingerprint_hits: list of dicts from _fingerprint_extract_matches,
        each {control_ref, must_id, matched_kw, position, standard_id, ...}
      semantic_top_k: set of control_refs from semantic_controls_in_scope
      explicit_refs:  set of control_refs from doc.explicit_refs
      control_meta:   dict[control_ref → {title, standard_id, musts:[{must_id,text}]}]
      max_size:       cap on set size (default 10)

    Returns:
      List of PrimingControl, ordered by strength_score DESC.

    Signal strengths:
      explicit_ref: 3, fingerprint: 2, semantic: 1

    A control appearing via all 3 signals gets score 6; one via
    semantic only gets 1. Ties broken by control_ref (deterministic).
    """
    # Aggregate by control_ref
    scores: dict[str, list[str]] = {}   # control_ref → list of signal sources
    fp_musts_by_ctrl: dict[str, list[dict]] = {}
    for hit in (fingerprint_hits or []):
        cref = hit.get("control_ref")
        if not cref:
            continue
        scores.setdefault(cref, []).append("fingerprint")
        fp_musts_by_ctrl.setdefault(cref, []).append({
            "must_id":    hit.get("must_id"),
            "matched_kw": hit.get("matched_kw"),
            "source":     "fingerprint",
        })
    for cref in (semantic_top_k or set()):
        scores.setdefault(cref, []).append("semantic")
    for cref in (explicit_refs or set()):
        scores.setdefault(cref, []).append("explicit_ref")

    # Compute strength + build PrimingControls
    entries: list[PrimingControl] = []
    for cref, sources in scores.items():
        meta = control_meta.get(cref, {})
        # Unique sources preserved in order (dedup while preserving)
        seen: set[str] = set()
        unique_sources: list[str] = []
        for s in sources:
            if s not in seen:
                seen.add(s)
                unique_sources.append(s)
        strength = sum(_SIGNAL_STRENGTH.get(s, 0) for s in unique_sources)

        # Assemble candidate MUSTs — start with fingerprint hits, then
        # add other MUSTs from the control_meta catalog (LLM should
        # consider all of them, not just fingerprint-hit ones)
        candidate_musts: list[dict] = list(fp_musts_by_ctrl.get(cref, []))
        seen_must_ids = {m.get("must_id") for m in candidate_musts}
        for m in (meta.get("musts") or []):
            if m.get("must_id") in seen_must_ids:
                continue
            candidate_musts.append({
                "must_id": m.get("must_id"),
                "text":    m.get("text"),
                "source":  "catalog",
            })

        entries.append(PrimingControl(
            control_ref     = cref,
            control_title   = meta.get("title", ""),
            signal_sources  = unique_sources,
            strength_score  = strength,
            candidate_musts = candidate_musts,
        ))

    # Sort: strength DESC, then control_ref ASC for determinism
    entries.sort(key=lambda e: (-e.strength_score, e.control_ref))
    return entries[:max_size]


def _build_extend_pool(
    doc_text:     Optional[str],
    tenant_stds:  Optional[list[str]] = None,
    pool_size:    int = 100,
) -> list[ExtendPoolControl]:
    """Query the leaf-level Chroma collections (iso27001_2022 /
    iso27701_2019 / gdpr_2016_679) with doc content, return the top-K
    controls with 1-line descriptions. This is the LLM's escape hatch
    for extending beyond the priming set.

    Refs are guaranteed to exist in the curated catalog — if the LLM
    picks a ref outside this pool in its extend step, that's a
    "flagged_missing_control" case for catalog feedback.

    Silent fallback on any error returns []. Caller degrades to
    "confirm-only" mode (no LLM discovery step) if pool is empty.
    """
    if not doc_text:
        return []

    try:
        from vector.retriever import VectorRetriever
        retriever = VectorRetriever()
        query_text = doc_text[:6000]   # match MUST embedding lookup cap
        ctx = retriever.search(
            query     = query_text,
            n         = pool_size,
            standards = tenant_stds,
        )
    except Exception as e:
        logger.warning("build_extend_pool: retriever unavailable: %s", e)
        return []

    out: list[ExtendPoolControl] = []
    for r in (ctx.results or []):
        # RequirementNode-level results — ref/title come from the node
        out.append(ExtendPoolControl(
            control_ref = r.ref,
            standard_id = getattr(r, "standard_id", "") or "",
            title       = r.title or "",
            description = (getattr(r, "obligation_text", "") or getattr(r, "business_description", "") or "")[:200],
        ))
    return out


def build_control_meta_from_neo4j(control_refs: list[str], driver) -> dict[str, dict]:
    """Build the {control_ref → {title, standard_id, musts:[...]}} map
    from Neo4j. Used by _build_priming_set to populate control titles
    and candidate MUSTs. Small query — one round-trip per control set."""
    if not control_refs or driver is None:
        return {}
    try:
        with driver.session() as s:
            q = """
            MATCH (rn:RequirementNode)
            WHERE rn.ref IN $refs
            OPTIONAL MATCH (rn)-[:SATISFIED_BY]->(:FulfilmentSpec)
                          -[:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
                          -[:MUST_CONTAIN]->(mi:ChecklistItem)
            RETURN rn.ref  AS control_ref,
                   rn.title AS title,
                   rn.standard_id AS standard_id,
                   collect(DISTINCT {must_id: mi.id, text: mi.text}) AS musts
            """
            out: dict[str, dict] = {}
            for row in s.run(q, refs=list(control_refs)):
                cref = row["control_ref"]
                if not cref:
                    continue
                musts = [m for m in (row["musts"] or []) if m.get("must_id")]
                out[cref] = {
                    "title":       row["title"] or "",
                    "standard_id": row["standard_id"] or "",
                    "musts":       musts,
                }
            return out
    except Exception as e:
        logger.warning("build_control_meta_from_neo4j failed: %s", e)
        return {}
