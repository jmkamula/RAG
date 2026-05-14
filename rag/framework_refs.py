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
