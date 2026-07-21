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
import math
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Ship 11'.d/redesign — post-critic semantic-fit gate ────────────
#
# The critic-verifier grounds quotes verbatim + binds to MUSTs. That
# doesn't catch cross-anchor keyword drift: "Technical safeguards
# (encryption, access controls, data minimization)" verbatim in the
# doc + confirmed for A.7.4.1 (Limit collection) because "data
# minimization" matched. The quote is a safeguards bullet, not
# collection-limit prose.
#
# Ship 11'.d shipped a prompt-enrichment fix (business_description +
# MUST-prefix taxonomy in the system prompt) that violated case-file
# discipline: it grew the prompt 2.3x and destabilized JSON output.
# Ship 11'.d/redesign replaces that with a DETERMINISTIC POST-CRITIC
# GATE:
#
#   For each critic-confirmed finding, compute cosine similarity
#   between the quote embedding + the anchor's business_description
#   embedding. If similarity < threshold, reject.
#
# This preserves the case-file principle: LLM composes/confirms;
# deterministic gates verify semantics AFTER.

_SEMANTIC_FIT_THRESHOLD  = 0.30    # cosine sim below this → reject
_ANCHOR_EMBED_CACHE: dict[str, list[float]] = {}


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors, 0 when either is zero-norm."""
    dot = 0.0
    na  = 0.0
    nb  = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na  += x * x
        nb  += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def _get_embed_fn():
    """Return the shared OpenAI embedding function used across the
    codebase (Ship 5'.b: text-embedding-3-large). Cached at module
    scope. Returns None if embedding infrastructure unavailable —
    caller degrades to passing all findings through (fail-open)."""
    global _EMBED_FN
    try:
        return _EMBED_FN
    except NameError:
        pass
    try:
        from vector.indexer import OpenAIEmbeddingFunction
        from rag.embedding_config import EMBED_MODEL_STANDARD
        _EMBED_FN = OpenAIEmbeddingFunction(model=EMBED_MODEL_STANDARD)
        return _EMBED_FN
    except Exception as e:
        logger.warning("semantic_fit gate: embedding fn unavailable: %s", e)
        _EMBED_FN = None
        return None


def _embed_anchor_description(desc: str, embed_fn) -> Optional[list[float]]:
    """Return cached or freshly-embedded vector for an anchor
    business_description. Cache is process-scoped."""
    if not desc:
        return None
    if desc in _ANCHOR_EMBED_CACHE:
        return _ANCHOR_EMBED_CACHE[desc]
    try:
        out = embed_fn([desc])
        vec = list(out[0]) if len(out) else None
    except Exception as e:
        logger.warning("anchor embed failed: %s", e)
        vec = None
    if vec is not None:
        _ANCHOR_EMBED_CACHE[desc] = vec
    return vec


def _semantic_fit_ok(
    quote: str,
    anchor_description: str,
    embed_fn,
    threshold: float = _SEMANTIC_FIT_THRESHOLD,
) -> tuple[bool, str, float]:
    """Ship 11'.d/redesign gate. Returns (ok, reason, similarity).

    Fail-open policy: if embedding infrastructure is unavailable OR
    the anchor lacks a business_description, PASS the finding through.
    The gate is a signal-add, not a signal-required check — the
    critic + Ship 11'.c filters remain the primary defence.
    """
    if embed_fn is None:
        return (True, "embed_unavailable", 0.0)
    if not anchor_description or not quote:
        return (True, "no_description_baseline", 0.0)

    anchor_vec = _embed_anchor_description(anchor_description, embed_fn)
    if anchor_vec is None:
        return (True, "anchor_embed_failed", 0.0)

    try:
        quote_vec = list(embed_fn([quote])[0])
    except Exception as e:
        logger.warning("quote embed failed: %s", e)
        return (True, "quote_embed_failed", 0.0)

    sim = _cosine(anchor_vec, quote_vec)
    if sim < threshold:
        return (False, f"semantic_fit_low:{sim:.2f}", sim)
    return (True, f"semantic_fit_ok:{sim:.2f}", sim)

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
    business_description: str = ""             # Ship 11'.d: curator-authored
                                                # anchor CORE OBLIGATION summary.
                                                # Feeds the prompt so the LLM
                                                # can check quote-to-anchor
                                                # SEMANTIC fit, not just topic.


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
            control_ref          = cref,
            control_title        = meta.get("title", ""),
            signal_sources       = unique_sources,
            strength_score       = strength,
            candidate_musts      = candidate_musts,
            business_description = meta.get("business_description", ""),
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
        from rag.embedding_config import EMBED_MODEL_STANDARD
        # Explicit embedding model (Ship 5'.b) — see extractor.py:2415.
        retriever = VectorRetriever(embedding_model=EMBED_MODEL_STANDARD)
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


_CRITIC_SYSTEM_PROMPT = """You are a compliance evidence critic reviewing a document.

Deterministic signals (keyword fingerprints, semantic embeddings, ref
regex) have proposed which controls this document covers. Your job:

1. CONFIRM each priming-set proposal by finding a VERBATIM quote from
   the document that grounds the control's requirement. When the
   priming control lists candidate MUSTs, you MUST pick the ONE that
   the quote best evidences (this binds the finding at the MUST level,
   which is how the engine measures leaf satisfaction). If you can't
   ground the control at all, REJECT with a short reason.

2. EXTEND: independently identify OTHER controls this document covers
   that the signals missed. For each, provide a verbatim quote. You
   MUST only pick refs from the EXTEND POOL provided below. If you
   believe the doc covers a control NOT in the pool, use
   `flagged_missing_control` — do NOT invent refs.

RULES:
- Every quote must appear VERBATIM in the document body. Rejecting a
  wrong signal is better than fabricating a confirmation.
- Being cautious is better than being wrong.
- Do NOT reference control refs outside the priming set or extend pool.
- Confidence: "high" if the quote is unambiguous and specific; "medium"
  if broadly relevant; "low" if only weakly implied (rare — prefer to
  reject).

Respond ONLY with valid JSON matching this schema (no prose before/after):

{
  "confirmed": [
    {"control_ref": "A.7.2.3",
     "checklist_item_id": "item:A.7.2.3:...",   // REQUIRED when candidate MUSTs are listed; pick the id whose text best matches your quote
     "quote": "<verbatim from document>",
     "confidence": "high|medium|low"}
  ],
  "rejected": [
    {"control_ref": "A.7.5.2",
     "reason": "<why the signal was wrong for this doc>"}
  ],
  "extended": [
    {"control_ref": "A.7.4.5",
     "checklist_item_id": "item:...",   // optional
     "quote": "<verbatim from document>",
     "confidence": "high|medium|low"}
  ],
  "flagged_missing_control": [
    {"guess_ref": "A.5.19",
     "reason": "<what evidence in the doc suggests a control not in the pool>"}
  ]
}
"""


def _format_priming_block(priming: list[PrimingControl]) -> str:
    """Human-readable priming section for the prompt. Keep it lean —
    Ship 11'.d/redesign codified that anchor-semantic verification
    belongs in a POST-CRITIC deterministic gate, not in the LLM prompt.
    business_description is fetched onto PrimingControl but consumed
    downstream by the semantic-fit gate, not by the LLM."""
    if not priming:
        return "(no signals proposed anything — extend from the pool below)"
    lines: list[str] = []
    for p in priming:
        sources = " + ".join(p.signal_sources)
        lines.append(
            f'  - control_ref: "{p.control_ref}"  title: "{p.control_title}"  '
            f'signals: {sources}  strength: {p.strength_score}'
        )
        # Include up to 5 candidate MUSTs so the LLM can bind to the right one
        for m in p.candidate_musts[:5]:
            mid  = m.get("must_id") or ""
            text = m.get("text") or ""
            src  = m.get("source", "catalog")
            lines.append(f'      * {mid}  [{src}]  {text[:180]}')
    return "\n".join(lines)


def _format_extend_pool_block(pool: list[ExtendPoolControl]) -> str:
    """Compact extend-pool listing — one line per control."""
    if not pool:
        return "(extend pool unavailable — confirm/reject only)"
    lines: list[str] = []
    for e in pool:
        title = (e.title or "").replace('"', "'")
        desc  = (e.description or "").replace("\n", " ")[:80]
        lines.append(f'  - {e.control_ref} ({e.standard_id}): {title}  — {desc}')
    return "\n".join(lines)


def _build_critic_prompt(
    doc_text:    str,
    doc_name:    str,
    priming:     list[PrimingControl],
    extend_pool: list[ExtendPoolControl],
) -> str:
    """Assemble the full user prompt from priming + extend pool + doc text."""
    priming_block   = _format_priming_block(priming)
    extend_block    = _format_extend_pool_block(extend_pool)

    return f"""DOCUMENT: {doc_name}
────────────────────────────────────────────────────────────────────
{doc_text[:60000]}
────────────────────────────────────────────────────────────────────

DETERMINISTIC SIGNALS SAY THIS DOC PROBABLY COVERS THESE CONTROLS
(priming set — confirm or reject each):

{priming_block}

EXTEND POOL — additional controls that MAY apply if you find evidence
(refs listed here are the ONLY valid refs for the "extended" step):

{extend_block}

Now respond with the JSON structure specified in the system prompt."""


def _parse_critic_response(
    raw:          str,
    valid_refs:   set[str],
    valid_musts:  dict[str, set[str]],   # control_ref → set of valid must_ids
) -> dict:
    """Parse the critic-verifier JSON response. Returns
    {confirmed, rejected, extended, flagged_missing_control} with
    stripped/validated entries. Refs outside `valid_refs` are dropped
    from confirmed/extended (LLM tried to reference something not in
    priming+pool). checklist_item_id is dropped if it's not in the
    control's valid_musts (defensive against hallucinated ids)."""
    import json as _json
    import re as _re

    raw = _re.sub(r'```json\s*|\s*```', '', raw).strip()
    if not raw or raw == "{}":
        return {"confirmed": [], "rejected": [], "extended": [], "flagged_missing_control": []}
    try:
        data = _json.loads(raw)
    except _json.JSONDecodeError as e:
        # Salvage the leading JSON object if the model appended prose
        last_brace = raw.rfind("}")
        if last_brace > 0:
            try:
                data = _json.loads(raw[: last_brace + 1])
            except Exception:
                logger.warning("critic_verifier parse error: %s", e)
                return {"confirmed": [], "rejected": [], "extended": [], "flagged_missing_control": []}
        else:
            logger.warning("critic_verifier parse error: %s", e)
            return {"confirmed": [], "rejected": [], "extended": [], "flagged_missing_control": []}

    def _clean_entry(e: dict, allow_musts: bool = True) -> Optional[dict]:
        cref = (e.get("control_ref") or "").strip()
        if not cref or cref not in valid_refs:
            return None
        item_id = (e.get("checklist_item_id") or "").strip() or None
        if item_id and allow_musts:
            allowed = valid_musts.get(cref) or set()
            if item_id not in allowed:
                item_id = None  # hallucinated — drop silently
        quote = (e.get("quote") or "").strip()
        conf  = (e.get("confidence") or "medium").strip().lower()
        if conf not in ("high", "medium", "low"):
            conf = "medium"
        if not quote or len(quote) < 20:
            return None
        return {
            "control_ref":       cref,
            "checklist_item_id": item_id,
            "quote":             quote,
            "confidence":        conf,
        }

    out = {
        "confirmed": [],
        "rejected":  [],
        "extended":  [],
        "flagged_missing_control": [],
    }
    for e in (data.get("confirmed") or []):
        c = _clean_entry(e)
        if c: out["confirmed"].append(c)
    for e in (data.get("rejected") or []):
        cref = (e.get("control_ref") or "").strip()
        reason = (e.get("reason") or "").strip()[:400]
        if cref:
            out["rejected"].append({"control_ref": cref, "reason": reason})
    for e in (data.get("extended") or []):
        c = _clean_entry(e)
        if c: out["extended"].append(c)
    for e in (data.get("flagged_missing_control") or []):
        gref   = (e.get("guess_ref") or "").strip()
        reason = (e.get("reason") or "").strip()[:400]
        if gref:
            out["flagged_missing_control"].append({"guess_ref": gref, "reason": reason})
    return out


def _extract_critic_verifier(
    doc,                        # ParsedDocument
    priming:      list[PrimingControl],
    extend_pool:  list[ExtendPoolControl],
    # Default sourced from rag.llm_models (Ship 5'.d).
    model:        str = None,
    max_tokens:   int = 4000,
    timeout_s:    float = 90.0,
) -> tuple[dict, Optional[str]]:
    """Run the critic-verifier LLM pass. Returns (parsed_response, error).

    The parsed dict has {confirmed, rejected, extended, flagged_missing_control}.
    Error is None on success, else the LlmResponse.error string. Never
    raises — silent-fail contract of the whole intake stage.

    IMPORTANT: this function does NOT convert to DocumentFinding — that's
    done by the caller so grounding + posture-writer integration stays
    in one place (extractor.py). This function only handles the LLM
    interaction + response validation.
    """
    from rag.llm_client import call as llm_call
    from rag.llm_models import MODEL_EXTRACTOR
    if model is None:
        model = MODEL_EXTRACTOR

    doc_text = doc.markdown or doc.full_text or ""
    if not doc_text.strip():
        return ({"confirmed": [], "rejected": [], "extended": [], "flagged_missing_control": []},
                "empty doc text")

    prompt = _build_critic_prompt(
        doc_text    = doc_text,
        doc_name    = getattr(doc, "original_name", "") or "unnamed",
        priming     = priming,
        extend_pool = extend_pool,
    )

    metadata = {
        "step":          "critic_verifier",
        "doc_name":      getattr(doc, "original_name", ""),
        "priming_size":  len(priming),
        "pool_size":     len(extend_pool),
    }

    # Try up to twice — LLM structured-JSON output is stochastic; a
    # malformed response on attempt 1 usually parses cleanly on retry
    # (same prompt, same temperature=0.0, different token sample).
    response = None
    for attempt in (1, 2):
        response = llm_call(
            system      = _CRITIC_SYSTEM_PROMPT,
            user        = prompt,
            model       = model,
            purpose     = "extractor",
            max_tokens  = max_tokens,
            temperature = 0.0,
            timeout_s   = timeout_s,
            metadata    = {**metadata, "attempt": attempt},
        )
        if not response.ok:
            break
        # Quick parse check — if it parses, use this attempt
        import json as _json_probe
        import re as _re_probe
        _probe_raw = _re_probe.sub(r'```json\s*|\s*```', '', response.text).strip()
        try:
            _json_probe.loads(_probe_raw)
            break   # parsed — done
        except _json_probe.JSONDecodeError:
            if attempt == 2:
                logger.warning("critic_verifier: both attempts returned malformed JSON")

    if not response.ok:
        return ({"confirmed": [], "rejected": [], "extended": [], "flagged_missing_control": []},
                response.error)

    # Build the valid ref/must sets from priming + extend pool so the
    # parser can drop anything the LLM invented.
    valid_refs: set[str] = set()
    valid_musts: dict[str, set[str]] = {}
    for p in priming:
        valid_refs.add(p.control_ref)
        valid_musts.setdefault(p.control_ref, set()).update(
            m.get("must_id") for m in p.candidate_musts if m.get("must_id")
        )
    for e in extend_pool:
        valid_refs.add(e.control_ref)
        # Extend pool doesn't carry MUSTs — LLM can propose any MUST
        # for extend controls; caller validates against Neo4j downstream

    parsed = _parse_critic_response(response.text, valid_refs, valid_musts)
    return parsed, None


def build_control_meta_from_neo4j(control_refs: list[str], driver) -> dict[str, dict]:
    """Build the {control_ref → {title, standard_id, business_description,
    musts:[...]}} map from Neo4j. Used by _build_priming_set to populate
    control titles + curated business_description (Ship 11'.d) and
    candidate MUSTs. Small query — one round-trip per control set.

    `business_description` is the curator-authored one-line summary of
    the anchor's CORE OBLIGATION (e.g. A.7.2.6 = "Contracts with PII
    processors: identify, document + agree the additional obligations
    on the customer per Art.28"). The critic prompt uses this so the
    LLM can verify quote-to-anchor semantic fit rather than just
    keyword-topic overlap. Falls back to obligation_text when
    business_description is empty.
    """
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
                   coalesce(rn.business_description, rn.obligation_text, '')
                       AS business_description,
                   collect(DISTINCT {must_id: mi.id, text: mi.text}) AS musts
            """
            out: dict[str, dict] = {}
            for row in s.run(q, refs=list(control_refs)):
                cref = row["control_ref"]
                if not cref:
                    continue
                musts = [m for m in (row["musts"] or []) if m.get("must_id")]
                out[cref] = {
                    "title":                row["title"] or "",
                    "standard_id":          row["standard_id"] or "",
                    "business_description": row["business_description"] or "",
                    "musts":                musts,
                }
            return out
    except Exception as e:
        logger.warning("build_control_meta_from_neo4j failed: %s", e)
        return {}
