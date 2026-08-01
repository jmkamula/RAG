"""
ArionComply — Framework-aware reference helpers.

Shared utilities for working with fully-qualified compliance references
in the form STANDARD:VERSION:REF (e.g. "ISO27001:2022:A.5.18",
"GDPR:2016/679:Art.32"). Used by any code that needs to:

  - parse a list of mixed-framework refs into framework groups, OR
  - render those groups as human-readable prose for an answer.

Lives in its own module so both rag/arion_graph.py and
rag/context_assembler.py (which arion_graph imports) can use it
without a circular import.
"""
from __future__ import annotations

# Friendly display labels for known frameworks.
# Tuple: (display_name, noun_for_refs).
# When a new framework is added, drop a row here — the rest of the system
# picks it up automatically.
_FRAMEWORK_DISPLAY: dict[str, tuple[str, str]] = {
    "ISO27001": ("ISO 27001", "controls"),
    "ISO27701": ("ISO 27701", "controls"),
    "GDPR":     ("GDPR",      "articles"),
    "NIST":     ("NIST",      "controls"),
    "SOC2":     ("SOC 2",     "criteria"),
    "HIPAA":    ("HIPAA",     "safeguards"),
}

# Stable priority for display order — keeps cross-framework answers
# consistent run-to-run.
_FRAMEWORK_PRIORITY = ["ISO27001", "ISO27701", "GDPR", "NIST", "SOC2", "HIPAA"]


def group_refs_by_framework(
    refs: list | None,
) -> list[tuple[str, str, list[str]]]:
    """
    Parse fully-qualified refs (STANDARD:VERSION:REF, e.g. "ISO27001:2022:A.5.1")
    and group by standard.

    Returns a list of (display_name, noun, sorted_refs) tuples ordered by
    a stable framework priority (ISO 27001 → ISO 27701 → GDPR → others
    alphabetically). Bare refs without a STANDARD: prefix are bucketed
    as "Other".
    """
    if not refs:
        return []

    groups: dict[str, list[str]] = {}
    for raw in refs:
        if not raw:
            continue
        parts = raw.split(":", 2)
        if len(parts) == 3:
            standard, _version, control = parts
        elif len(parts) == 2:
            standard, control = parts
        else:
            standard, control = "OTHER", parts[0]
        groups.setdefault(standard, []).append(control)

    ordered_keys  = [k for k in _FRAMEWORK_PRIORITY if k in groups]
    ordered_keys += sorted(k for k in groups if k not in _FRAMEWORK_PRIORITY)

    out: list[tuple[str, str, list[str]]] = []
    for k in ordered_keys:
        display, noun = _FRAMEWORK_DISPLAY.get(k, (k, "controls"))
        out.append((display, noun, sorted(set(groups[k]))))
    return out


def normalize_control_ref(ref: str | None, standard_id: str | None) -> str | None:
    """
    Return the canonical control_ref for the given standard.

    ISMS clauses (4-10) collide with Annex A categories (A.5-A.8) at
    the 2-dot level (e.g. ISMS clause 8.2 vs Annex A.8.2). The
    normalizer cannot tell from format alone, so it favours
    preservation over heuristic prefixing — callers must pass the
    canonical form (curated specs use bare for ISMS clauses,
    A.-prefixed for Annex A).

    Rules (ISO 27001:2022):
      - 3-dot pattern (e.g. "6.1.1") → ISMS clause, never Annex A.
        Strip any A. prefix.
      - "A.5.18" → leave alone (canonical Annex A).
      - "5.18" / "6.1" → leave alone (caller's choice).
      - "9.2", "10.1" → leave alone (unambiguous ISMS body).

    Other standards pass through unchanged.

    Previously this auto-added 'A.' to any [5-8].N or [5-8].N.N ref,
    which corrupted ISMS clauses 5.x/6.x/7.x/8.x by re-filing them
    under Annex A storage. See [[normalizer-annex-a-isms-collision]].
    """
    if not ref:
        return ref
    if standard_id != "ISO27001:2022":
        return ref
    import re
    # 3-dot pattern is ALWAYS ISMS clause — strip A. prefix if present.
    m3 = re.match(r"^([Aa]\.?\s*)?(\d+\.\d+\.\d+)$", ref)
    if m3:
        return m3.group(2)
    # Anything starting with 'A.' is canonical Annex A.
    if ref.startswith("A."):
        return ref
    # Bare 2-dot / 3-dot / single-num → leave alone. Callers must
    # pass the canonical form.
    return ref


# ── Framework-version scope guard (2026-07-13) ────────────────────────────────
#
# The LLM can hallucinate control refs from its training data — most
# commonly ISO 27001:2013 Annex A (A.9.x, A.10.x, A.11.x, A.12.x, A.14.x)
# leaking into answers about ISO 27001:2022, where those refs were
# renumbered into A.5.x-A.8.x. Case #16 (root-caused 2026-07-13)
# surfaced this: "Access Rights Policy → required by ISO 27001 9.1"
# where 9.1 is the 2013 legacy for what's now A.5.15/A.5.18.
#
# The guard has two layers:
#   Layer A — namespace validity for the tenant's queryable_standards
#             (an ISO 27001:2022 tenant must not see A.9.x etc.)
#   Layer B — context-provenance: any ref emitted by the LLM must
#             actually exist in the LAYER 1/2 nodes provided in the
#             prompt (catches valid-syntax off-topic refs like "9.1
#             ISMS clause" cited for access-rights questions).
#
# Ground truth for Layer A = the Neo4j RequirementNode set for the
# tenant's standards. Cached at module scope by frozenset(standards).
# The cache is invalidated by process restart — safe because standards
# metadata is static.

import re as _re
import logging as _logging

_scope_logger = _logging.getLogger("rag.framework_refs")

_VALID_REFS_BY_SCOPE: dict[frozenset, set[str]] = {}

# Loose ref-shape pattern used to extract candidate control refs from
# prose. Captures ISO Annex A (A.5.18), ISMS clauses (9.2, 6.1.2),
# GDPR articles (Art.32, Art.5.1.a), and ISO 27701 (A.7.2.4, B.8.5.6).
# Anchored to word boundaries so it doesn't fragment identifiers.
_REF_TOKEN_RE = _re.compile(
    r"""
    (?:                                                 # one of:
        A\.\d+\.\d+(?:\.\d+)?                            #   Annex A: A.5.18, A.7.2.4
      | B\.\d+\.\d+(?:\.\d+)?                            #   ISO 27701 processor: B.8.5.6
      | Art\.\d+(?:\.\d+(?:\.[a-z])?)?                   #   GDPR: Art.32, Art.5.1.a
      | (?<![\w.])(?:[4-9]|10)\.[1-9](?:\.\d+)?(?!\w)    #   Bare ISMS clause 4.1-10.9 only
                                                         #   (avoids matching "32.1" from Art.32.1)
    )
    """,
    _re.VERBOSE,
)


def extract_ref_candidates(text: str) -> list[str]:
    """Return the ordered list of ref-shaped tokens found in prose."""
    if not text:
        return []
    return _REF_TOKEN_RE.findall(text)


# Ship 52 addendum — ref-form canonicalizer.
# Refs live in two conventions across the codebase:
#   Machine form  — `Art.32`, `Art.32.1.b`     (primary_ref, id_types)
#   Display form  — `GDPR Art. 32`, `Art. 32.1.b` (LLM prose, prompts)
# The variance is the space after "Art.". ISO 27001 refs (`A.5.15`)
# have no interior spacing so the two forms accidentally coincide,
# which is why the mismatch stayed latent until GDPR queries surfaced.
# Any comparison / dedup / extract site that mixed the two forms
# would silently miss its target — see the intro-chip dedup case
# ("Art.32.1GDPR Art. 32.1.b requires...") reported during Ship 52's
# GDPR spot-check.
#
# Canonicalize toward MACHINE form (no space) so `primary_ref` and
# prose match byte-for-byte. Call this at every polish exit + on the
# final repaired case-file answer. Belt-and-braces normalization also
# applied at SPA dedup sites so future short-circuits skipping polish
# are still safe.
import re as _re_canon
_ART_SPACE_RE = _re_canon.compile(r"\bArt\.\s+(\d)")


def canonicalize_ref_whitespace(text: str) -> str:
    """Rewrite ref-form variance to canonical machine form.
      "GDPR Art. 32"      → "GDPR Art.32"
      "Art. 32.1.b"       → "Art.32.1.b"
      "A.5.15"            → "A.5.15"       (unchanged; no variance)
    Idempotent — running it twice is a no-op. Safe on empty / None."""
    if not text:
        return text
    return _ART_SPACE_RE.sub(r"Art.\1", text)


def _populate_valid_refs(standards: frozenset, neo_driver) -> set[str]:
    """Fetch the full set of RequirementNode.ref values for these
    standards from Neo4j. Called once per unique standards frozenset.
    Silent-fail: returns empty set if Neo4j is unreachable (guard
    then no-ops rather than false-positive-strip valid refs)."""
    if not neo_driver:
        return set()
    try:
        with neo_driver.session() as s:
            r = s.run(
                """
                MATCH (n:RequirementNode)
                WHERE n.standard_id IN $standards
                RETURN DISTINCT n.ref AS ref
                """,
                standards=list(standards),
            )
            refs = {row["ref"] for row in r if row["ref"]}
            return refs
    except Exception as e:
        _scope_logger.warning(
            "framework_refs: valid-refs Neo4j fetch failed (%s) — "
            "guard will no-op for standards=%s",
            e, list(standards),
        )
        return set()


def get_valid_refs_for_scope(
    standards: list[str] | None,
    neo_driver=None,
) -> set[str]:
    """Return the set of RequirementNode.ref values for these standards,
    cached across calls. Empty set = fail-open (guard skips validation)."""
    if not standards:
        return set()
    key = frozenset(standards)
    cached = _VALID_REFS_BY_SCOPE.get(key)
    if cached is not None:
        return cached
    refs = _populate_valid_refs(key, neo_driver)
    if refs:
        _VALID_REFS_BY_SCOPE[key] = refs
    return refs


def clear_valid_refs_cache() -> None:
    """Test helper — reset the module-level cache."""
    _VALID_REFS_BY_SCOPE.clear()


def render_framework_refs(refs: list | None) -> str:
    """
    Render grouped framework refs as a single inline clause for prose.

    Examples:
        one framework  → "ISO 27001 controls A.5.1, A.5.12"
        two+           → "ISO 27001 controls A.5.1, A.5.12; GDPR articles Art.32"
        none           → ""
    """
    groups = group_refs_by_framework(refs)
    if not groups:
        return ""
    return "; ".join(
        f"{display} {noun} {', '.join(items)}"
        for display, noun, items in groups
    )
