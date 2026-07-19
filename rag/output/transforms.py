"""
Composable output transforms — Ship 7'.b (2026-07-19).

Each function here is a small pure transform: `(text, ...) -> str`.
The gateway (`rag.output.gateway.humanize`) chains a subset per
surface hint. Individual transforms are unit-tested in isolation
so the composition is trivially correct.

Design rules (see [[ship-7-prime-a-output-audit-2026-07-19]]):

- Pure functions — no I/O, no side effects.
- Idempotent — applying twice is the same as once. Callers may
  double-apply during migration; the result must be stable.
- Framework-aware where the transform touches standard/refs;
  pulls conventions from `rag.output.vocab` rather than hard-
  coding.
- Preserve semantic content — never delete a ref, never invent
  a claim. Only transform how existing content is rendered.

New transforms should:
1. Have a docstring stating what they transform, from what shape
   to what shape.
2. Include a "leave unchanged" example in the docstring for the
   idempotence contract.
3. Be added to the default chain in `gateway.py` under the
   appropriate `surface` if broadly useful.
"""
from __future__ import annotations

import re
from typing import Optional

from rag.output import vocab


# ── Standard-id formatting ─────────────────────────────────────────

# All known internal_ids, longest-first so 'ISO27001:2022' matches
# before any bare 'ISO27001' pattern. Populated lazily.
_STANDARD_ID_ALTERNATION: Optional[str] = None


def _build_standard_id_alternation() -> str:
    """Return a regex-alternation string of every enrolled
    internal_id, ordered longest-first (so overlapping prefixes
    don't cause partial matches). Rebuilt on demand — cheap since
    vocab is small and cached."""
    ids = sorted(vocab.all_ids(), key=len, reverse=True)
    return "|".join(re.escape(x) for x in ids)


def format_standard_id(text: str) -> str:
    """Replace every occurrence of a known internal_id substring
    with its `display_name`. Unknown standards pass through
    unchanged (so external refs to future frameworks aren't
    silently dropped).

    Example:
        'Framework: ISO27001:2022 clause 6.1.2' →
        'Framework: ISO 27001:2022 clause 6.1.2'

    Idempotence: since `display_name` values never contain
    `internal_id` substrings (they use spaces), applying twice
    is a no-op.
    """
    if not text:
        return text
    global _STANDARD_ID_ALTERNATION
    if _STANDARD_ID_ALTERNATION is None:
        _STANDARD_ID_ALTERNATION = _build_standard_id_alternation()
    if not _STANDARD_ID_ALTERNATION:
        return text

    def _sub(m: re.Match) -> str:
        return vocab.display_name(m.group(0))

    return re.sub(_STANDARD_ID_ALTERNATION, _sub, text)


def format_standard_id_exact(std_id: str, *, short: bool = False) -> str:
    """Convenience for the exact-string case (e.g. serializing a
    single `standard_id` field). Returns the vocab display_name
    (or short_name if short=True) or the input unchanged when
    the id isn't recognised.

    Example:
        format_standard_id_exact('ISO27001:2022')         → 'ISO 27001:2022'
        format_standard_id_exact('GDPR:2016/679', short=True) → 'GDPR'
    """
    if not std_id:
        return std_id
    return (vocab.short_name(std_id) if short else vocab.display_name(std_id))


# ── Slug humanisation ──────────────────────────────────────────────

# Snake_case (identifier-shape) tokens. Matches sequences of 2+
# lowercased words joined by underscores. We deliberately require
# ≥2 words so we don't rewrite legitimate single tokens like
# 'access' or 'policy'.
_SNAKE_TOKEN_RE = re.compile(
    r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b"
)


def humanize_snake_case(text: str) -> str:
    """Convert snake_case identifiers embedded in prose to space-
    separated words. Only touches ≥2-word tokens; single-word
    identifiers pass through (they're not distinguishable from
    ordinary lowercase words).

    Example:
        'Expected action: access_review_required' →
        'Expected action: access review required'

        'Follow-up: policy_revised was expected before offboarding_complete' →
        'Follow-up: policy revised was expected before offboarding complete'

    Idempotence: output contains no underscore-joined tokens, so
    re-applying is a no-op.
    """
    if not text:
        return text
    return _SNAKE_TOKEN_RE.sub(lambda m: m.group(1).replace("_", " "), text)


# ── Leaf-id / MUST-id scrubbing ────────────────────────────────────

# leaf ids: req:<STANDARD>:<REF>:<SLUG>
_LEAF_ID_RE = re.compile(r"\breq:[A-Za-z0-9._/]+:[a-z0-9_]+\b")

# MUST-item ids: item:<REF>:<SLUG>
_ITEM_ID_RE = re.compile(r"\bitem:[A-Za-z0-9._]+:[a-z0-9_]+\b")


def scrub_leaf_ids(text: str) -> str:
    """Remove `req:X:Y:Z` leaf-id slugs from prose (they exist for
    `data-*` attributes + audit provenance; humans read the
    control ref instead). Also strips `item:X:Y` MUST ids.

    Example:
        'Update the file at req:A.5.15:access_control_policy first' →
        'Update the file at first'   (caller should have used the
                                       humanised leaf title instead;
                                       scrub removes leakage)

    Idempotence: post-scrub text contains no matching patterns.
    """
    if not text:
        return text
    text = _LEAF_ID_RE.sub("", text)
    text = _ITEM_ID_RE.sub("", text)
    # Collapse the double spaces the deletion may have introduced.
    text = re.sub(r" {2,}", " ", text)
    return text.strip() if text.strip() != text else text


# ── UUID scrubbing (context-aware) ─────────────────────────────────

_UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)


def scrub_uuids(text: str, *, keep_suffix: int = 8) -> str:
    """Replace bare UUIDs with a short trailing suffix so the ID
    is still traceable in a support conversation without dumping
    the whole thing into tenant-facing prose.

    Example (keep_suffix=8):
        'Upload not found: 6c6e7102-846c-4aab-87be-91810c4b191b' →
        'Upload not found: …c4b191b'

    Idempotence: the ellipsis form doesn't match _UUID_RE, so
    re-applying is a no-op.
    """
    if not text:
        return text

    def _sub(m: re.Match) -> str:
        raw = m.group(0)
        suffix = raw.replace("-", "")[-keep_suffix:]
        return f"…{suffix}"

    return _UUID_RE.sub(_sub, text)


# ── Composite helpers registered by the gateway ────────────────────

# Registry of all named transforms so the gateway can look them
# up by string name. Add new transforms here + import above.
TRANSFORMS = {
    "format_standard_id":  format_standard_id,
    "humanize_snake_case": humanize_snake_case,
    "scrub_leaf_ids":      scrub_leaf_ids,
    "scrub_uuids":         scrub_uuids,
}
