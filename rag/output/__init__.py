"""
rag.output — framework-aware output gateway (Ship 7'.b, 2026-07-19).

Public entry points:

  from rag.output import humanize, gateway_guard, format_standard_id_exact

The gateway consolidates every tenant-facing string transform in
one module so multi-framework enrolment doesn't fan out into
scattered `_humanize_*` helpers.

See [[ship-7-prime-a-output-audit-2026-07-19]] for the design
rationale and the list of MIXED sites that Ship 7'.c+ will
migrate.
"""
from rag.output.gateway import UnknownSurface, gateway_guard, humanize
from rag.output.transforms import (
    format_standard_id,
    format_standard_id_exact,
    humanize_snake_case,
    scrub_leaf_ids,
    scrub_uuids,
    strip_markdown_escapes,
)

__all__ = [
    "humanize",
    "gateway_guard",
    "UnknownSurface",
    "format_standard_id",
    "format_standard_id_exact",
    "humanize_snake_case",
    "scrub_leaf_ids",
    "scrub_uuids",
    "strip_markdown_escapes",
]
