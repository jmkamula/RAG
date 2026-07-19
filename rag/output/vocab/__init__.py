"""
Per-framework display vocabulary — Ship 7'.b (2026-07-19).

Each JSON file in this directory defines the display conventions
for one enrolled standard: `internal_id` (canonical DB slug),
`display_name` (what tenants see), plus per-family
`ref_conventions` for future refinements. Loaded once at module
init and cached.

Adding a framework (e.g. SOC 2, NIS2, DORA) is a one-file edit
— drop `soc2_2017.json` in this directory. No code change to the
gateway required.

See [[ship-7-prime-a-output-audit-2026-07-19]] for the design
rationale (why per-framework JSON beats a monolithic humanize()
switch statement).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_VOCAB_DIR = Path(__file__).parent
_CACHE: dict[str, dict[str, Any]] = {}


def _load_all() -> dict[str, dict[str, Any]]:
    """Read every *.json in this directory, keyed by `internal_id`.
    Called on first access; result is cached in `_CACHE`.
    Malformed / missing `internal_id` files are logged + skipped
    rather than raised — the gateway must survive a partial vocab
    at boot."""
    if _CACHE:
        return _CACHE
    import logging
    _log = logging.getLogger("rag.output.vocab")
    for path in sorted(_VOCAB_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            key = data.get("internal_id")
            if not key:
                _log.warning("vocab: %s missing 'internal_id' — skipped", path.name)
                continue
            _CACHE[key] = data
        except Exception as e:
            _log.warning("vocab: failed to load %s: %s", path.name, e)
    return _CACHE


def get(internal_id: str) -> dict[str, Any] | None:
    """Return the vocab dict for a given canonical id, or None
    if the standard isn't enrolled / defined."""
    return _load_all().get(internal_id)


def all_ids() -> list[str]:
    """List of canonical ids that have a vocab file defined."""
    return list(_load_all().keys())


def display_name(internal_id: str, fallback: str | None = None) -> str:
    """Convenience: get `display_name` or the fallback (defaults
    to the internal_id itself so unknown standards render as their
    raw slug rather than 'None')."""
    v = get(internal_id)
    if v and v.get("display_name"):
        return v["display_name"]
    return fallback if fallback is not None else internal_id


def short_name(internal_id: str, fallback: str | None = None) -> str:
    """Convenience: get `short_name` (headline-friendly) or fallback."""
    v = get(internal_id)
    if v and v.get("short_name"):
        return v["short_name"]
    return fallback if fallback is not None else internal_id
