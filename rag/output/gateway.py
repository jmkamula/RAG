"""
Output gateway — Ship 7'.b (2026-07-19).

The single entry point that tenant-facing serialisation code
calls to render text as natural, factual, jargon-free prose.

Design (see [[ship-7-prime-a-output-audit-2026-07-19]]):

- Opt-in per site — sites call `humanize(text, surface=...)`
  explicitly. Never middleware.
- Surface hints tune behaviour without a switch statement in
  the gateway (default chains per surface listed below).
- Framework-aware — pulls display conventions from
  `rag.output.vocab`. Adding SOC 2 / NIS2 later is one JSON
  file, not a code edit.
- Composable — the actual work lives in
  `rag.output.transforms`; the gateway just picks + chains.

Two entry points:

  humanize(text, *, surface, transforms=None)
    → apply the default chain for `surface`, or the caller's
      explicit subset. Returns the transformed text.

  gateway_guard(text, *, surface=None)
    → return a list of JargonEvent dicts describing jargon
      patterns still present. Warn-only linter — never mutates.

## Surfaces

Named contexts. Each maps to a chain of transform names.

  external_api_json     — serialised REST responses
  notification_title    — short strings shown in inbox / email
                          subject / Slack heading
  notification_body     — longer strings in email body / Slack
                          block / inbox drill-in
  stage2_reason         — engine-proposed gap reason text
  error_detail          — HTTPException / SDK error message text
  cascade_rationale     — SOAR-facing cascade explanation

Callers may bypass the default chain with an explicit
`transforms=['scrub_uuids', 'humanize_snake_case']` list — useful
when the input has known shape and doesn't need the full pass.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

from rag.output.transforms import TRANSFORMS


# ── Default transform chains per surface ───────────────────────────
#
# Ordering matters — later transforms see the output of earlier
# ones. Rule of thumb: scrubbers (destructive) before humanisers
# (cosmetic), so cosmetic passes see clean text.

_SURFACE_DEFAULTS: dict[str, tuple[str, ...]] = {
    "external_api_json": (
        # Wire-format JSON. Rare in-string standard-ids should render
        # as display names. Slug identifiers stay verbatim in
        # structured fields (ref, standard_id) — callers control that
        # via explicit field-level humanize() calls.
        "format_standard_id",
    ),
    "notification_title": (
        # Short strings. Humanise snake_case action verbs, format
        # standards. No UUID scrubbing — titles rarely contain them
        # and the trailing '…c4b191b' looks worse than a truncated
        # UUID for short strings.
        "humanize_snake_case",
        "format_standard_id",
    ),
    "notification_body": (
        # Longer strings. All cosmetic transforms; scrub UUIDs since
        # bodies may quote error paths.
        "humanize_snake_case",
        "format_standard_id",
        "scrub_uuids",
    ),
    "stage2_reason": (
        # Engine-composed gap reasons. Slugs sneak in from legacy
        # gap_description prose. Full clean.
        "scrub_leaf_ids",
        "humanize_snake_case",
        "format_standard_id",
    ),
    "error_detail": (
        # Tenant-facing HTTPException detail. Scrub UUIDs to a
        # traceable suffix; humanise anything else.
        "scrub_uuids",
        "humanize_snake_case",
        "format_standard_id",
    ),
    "cascade_rationale": (
        # SOAR-facing. Keep it minimal — SIEM consumers may parse.
        "humanize_snake_case",
        "format_standard_id",
    ),
    "evidence_prose": (
        # Auditor-facing prose in the Evidence Package + obligation
        # text. Scrub leaf-id leakage that curator authoring may have
        # embedded, humanise snake_case action verbs, and format
        # standard-id slugs.
        "scrub_leaf_ids",
        "humanize_snake_case",
        "format_standard_id",
    ),
}


class UnknownSurface(ValueError):
    """Raised when a caller passes a `surface=` value with no
    default chain registered. Fail loud rather than silently
    passing text through — a typo in the surface name would
    otherwise ship jargon."""


def humanize(
    text: str,
    *,
    surface: str,
    transforms: Optional[Iterable[str]] = None,
) -> str:
    """Apply the humanisation chain for `surface` (or the
    caller's explicit `transforms` subset) to `text`.

    Never mutates the input. Returns the transformed string.
    Empty / None input returns unchanged.

    Raises UnknownSurface if `surface` isn't a registered name
    AND `transforms` isn't provided. Callers who need a truly
    custom pipeline should pass `transforms=[...]` explicitly
    and provide any string as `surface` (it's a label at that
    point, not a lookup key)."""
    if not text:
        return text

    if transforms is None:
        chain = _SURFACE_DEFAULTS.get(surface)
        if chain is None:
            raise UnknownSurface(
                f"Unknown surface {surface!r}; either register it "
                f"in _SURFACE_DEFAULTS or pass explicit transforms=[...]"
            )
    else:
        chain = tuple(transforms)

    out = text
    for name in chain:
        fn = TRANSFORMS.get(name)
        if fn is None:
            # Unknown transform name — skip silently rather than
            # raising, so a typo in a caller doesn't break a
            # production response. Log at DEBUG so it's visible in
            # dev but doesn't spam prod.
            import logging
            logging.getLogger("rag.output.gateway").debug(
                "gateway: unknown transform %r in surface %r — skipped",
                name, surface,
            )
            continue
        out = fn(out)
    return out


# ── gateway_guard: warn-only linter ────────────────────────────────
#
# Detects known jargon patterns in a string. Returns a list of
# events — never mutates. Used in unit tests to assert that
# producer functions emit clean output, and available to CI as a
# warn-only signal.

# Patterns treated as jargon in tenant-facing surfaces.

_JARGON_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "raw_standard_id",
        re.compile(r"\b(?:ISO27001:20\d{2}|ISO27701:20\d{2}|GDPR:20\d{2}/\d+)\b"),
    ),
    (
        "leaf_id",
        re.compile(r"\breq:[A-Za-z0-9._/]+:[a-z0-9_]+\b"),
    ),
    (
        "item_id",
        re.compile(r"\bitem:[A-Za-z0-9._]+:[a-z0-9_]+\b"),
    ),
    (
        "bare_uuid",
        re.compile(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
        ),
    ),
    (
        "snake_case_slug",
        # Two-or-more-word snake_case identifiers. Skips single
        # words (indistinguishable from ordinary lowercase words)
        # and CamelCase / kebab-case.
        re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+){1,}\b"),
    ),
)


def gateway_guard(
    text: str,
    *,
    surface: Optional[str] = None,
) -> list[dict]:
    """Scan `text` for known jargon patterns; return a list of
    events. Each event: `{kind, snippet, start, end}`. Empty
    list means the text is clean.

    `surface` is currently informational (attached to events) —
    future work may suppress specific kinds per surface (e.g.
    `external_api_json` legitimately carries `standard_id` slugs
    in structured fields, so callers targeting that surface may
    filter kind='raw_standard_id' out).
    """
    if not text:
        return []
    events: list[dict] = []
    for kind, pattern in _JARGON_PATTERNS:
        for m in pattern.finditer(text):
            events.append({
                "kind":    kind,
                "snippet": m.group(0),
                "start":   m.start(),
                "end":     m.end(),
                "surface": surface,
            })
    return events


# ── Public surface ─────────────────────────────────────────────────

__all__ = [
    "humanize",
    "gateway_guard",
    "UnknownSurface",
]
