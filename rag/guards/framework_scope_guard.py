"""
Framework-version scope guard — 2026-07-13.

Post-answer filter that catches the LLM citing control refs which
aren't in the tenant's declared standard versions, and refs that
weren't surfaced in the LAYER 1/2 nodes provided in the prompt.

Two layers:

  Layer A — namespace validity. The tenant declares which standards
            + versions they operate under (queryable_standards, e.g.
            ["ISO27001:2022", "GDPR:2016/679"]). A ref that isn't in
            the valid RequirementNode.ref set for those standards is
            almost certainly a legacy-standard leak (e.g. ISO 27001
            :2013 A.9.x under a 2022 tenant).

  Layer B — context provenance. Even a syntactically valid ref may
            be off-topic for the specific query (e.g. ISMS clause
            "9.1 Monitoring" cited in an answer about access rights).
            If the ref wasn't in the LAYER 1/2 node set surfaced by
            the resolver, it's an LLM hallucination on top of context.

Applied in llm_answer.rank_and_answer post-processing, next to
posture_claim_guard. On violation:
  - The ref token is removed in-place from the answer.
  - Trailing punctuation / whitespace is tidied.
  - A structured violation record is returned so the caller can log.

Root cause / motivating case: eval case #16 — "what documents do
we need to address the access rights NC?" — where gpt-4o-mini
consistently outputs "required by ISO 27001 9.1 and GDPR Art. 32"
instead of citing A.5.15 / A.5.18 from the provided context.
"""
from __future__ import annotations

import re
from typing import Optional

from rag.framework_refs import (
    _REF_TOKEN_RE,
    extract_ref_candidates,
    get_valid_refs_for_scope,
)


def _family_of(ref: str) -> str:
    """Return a coarse family key for a ref, used by Layer B's
    family-match relaxation. Two refs share a family if they belong
    to the same first-level bucket of the same standard shape.

    Examples:
      A.5.18  → A.5
      A.7.2.4 → A.7
      A.5.15  → A.5   (same family as A.5.18)
      B.8.5.6 → B.8
      Art.32.1.b → Art.32
      Art.5.1.a  → Art.5
      9.1     → 9     (ISMS bare)
      6.1.2   → 6
    """
    if not ref:
        return ""
    if ref.startswith("A.") or ref.startswith("B."):
        parts = ref.split(".")
        return ".".join(parts[:2]) if len(parts) >= 2 else ref
    if ref.startswith("Art."):
        parts = ref.split(".")
        return ".".join(parts[:2]) if len(parts) >= 2 else ref
    return ref.split(".")[0]


def _tidy_punctuation(text: str) -> str:
    """Collapse artefacts left after ref removal:
    - '  ' → ' '
    - ' ,' or ' .' → ',' / '.'
    - stray 'and , ' → 'and ,'
    - leading punctuation on line → strip
    - 'A and B' where A/B collapsed to empty → 'and' orphan cleanup
    """
    if not text:
        return text
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    # ' ,' → ','; ' .' → '.'; ' ;' → ';'
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    # 'ISO 27001 ' followed by punctuation (ref was stripped mid-phrase)
    text = re.sub(r"(ISO ?270\d{2}|GDPR)\s+([,.;])", r"\1\2", text)
    # ',' or 'and' with nothing meaningful in between: 'A , and B' → 'A and B'
    text = re.sub(r",\s*and\b", " and", text)
    text = re.sub(r"\band\s+and\b", "and", text)
    # 'required by  and' → 'required by' (both refs gone)
    text = re.sub(r"\brequired by\s+(?:and\s+)+", "required by ", text)
    text = re.sub(r"\band\s*\.", ".", text)
    return text.strip()


def scan_and_strip_off_scope_refs(
    answer_text:         str,
    queryable_standards: list[str],
    context_refs:        Optional[set[str]] = None,
    neo_driver                             = None,
) -> tuple[str, list[dict]]:
    """
    Scan `answer_text` for ref-shaped tokens and strip those that
    don't pass either Layer A (namespace validity for the tenant's
    standard versions) or Layer B (context provenance from the
    LAYER 1/2 node ref set).

    Args:
        answer_text:         The composed LLM answer.
        queryable_standards: e.g. ["ISO27001:2022", "GDPR:2016/679"].
        context_refs:        Optional set of refs surfaced in the
                             LAYER 1/2 nodes; when provided, Layer B
                             fires. When None, only Layer A applies.
        neo_driver:          Neo4j driver for the Layer A ref set
                             fetch. If None, Layer A no-ops.

    Returns:
        (cleaned_answer, violations)
        violations: list of dicts with keys:
          - ref:      the flagged token
          - layer:    "A" or "B"
          - reason:   short human-readable diagnostic
    """
    if not answer_text or not queryable_standards:
        return answer_text, []

    valid_refs = get_valid_refs_for_scope(queryable_standards, neo_driver)
    # Fail-open when we couldn't determine the valid set — better to
    # let a suspect ref through than to nuke a legitimate answer.
    if not valid_refs and context_refs is None:
        return answer_text, []

    violations: list[dict] = []
    seen_flagged: set[str] = set()

    # Precompute Layer B family whitelist — refs that share a family
    # with a context ref pass Layer B even when not identical. This
    # lets the LLM cite legitimate siblings (e.g. A.5.18 when A.5.15
    # is in context; both belong to the access family) while still
    # stripping unrelated valid-syntax refs (e.g. "9.1 Monitoring"
    # cited for access when only A.5.x was retrieved).
    context_families: set[str] = (
        {_family_of(r) for r in context_refs} if context_refs is not None else set()
    )

    # Iterate matches from right to left so string slicing stays
    # stable as we remove tokens.
    matches = list(_REF_TOKEN_RE.finditer(answer_text))
    for m in reversed(matches):
        ref = m.group(0)

        # Layer A — namespace validity
        layer_a_ok = (not valid_refs) or (ref in valid_refs)

        # Layer B — context provenance (with family-match relaxation)
        if context_refs is None:
            layer_b_ok = True
        else:
            layer_b_ok = (ref in context_refs) or (_family_of(ref) in context_families)

        if layer_a_ok and layer_b_ok:
            continue

        # Determine layer + reason for the diagnostic
        if not layer_a_ok:
            layer  = "A"
            reason = f"ref {ref!r} not in valid namespace for standards={queryable_standards}"
        else:
            layer  = "B"
            reason = f"ref {ref!r} not in LAYER 1/2 provided context"

        # Only log first occurrence per ref to keep the violations
        # list readable, but strip every occurrence.
        if ref not in seen_flagged:
            violations.append({"ref": ref, "layer": layer, "reason": reason})
            seen_flagged.add(ref)

        answer_text = answer_text[:m.start()] + answer_text[m.end():]

    if violations:
        answer_text = _tidy_punctuation(answer_text)

    return answer_text, violations
