"""
rag/templates/renderer.py — render a stored template body_md for a tenant.

Tenant-scoped transformations:
  1. Lookup template body from `templates` table
  2. Strip MUST sections where tenant_must_overrides.applies = FALSE
     for that must_id (Arion cloud-only: drops A.5.15:physical_rules etc.)
  3. Substitute identity placeholders (<<TENANT_NAME>>, <<TENANT_SECTOR>>,
     <<TENANT_COUNTRY>>, <<GENERATED_DATE>>) from the `tenants` table
  4. Optionally prepend a generation header (off by default — caller
     decides via include_header param)

The <<TEXT>> per-MUST blanks stay intact — they're tenant fill-in zones.
The <<MUST item:X>> / <<SHOULD item:X>> markers stay intact — they bind
the upload-side extractor when the tenant uploads back.

Section stripping is structural: removes the lines from the section
heading through the next heading or the next horizontal-rule marker
(`---` on its own line). Tested with the scaffold generator's output
shape.
"""

from __future__ import annotations

import datetime as _dt
import logging
import re
from dataclasses import dataclass
from typing import Optional


logger = logging.getLogger(__name__)


_MUST_BLOCK_RE = re.compile(
    # A whole MUST section: starts at "## N. Header" line, captures up
    # to (but not including) the next "## " heading at the same level
    # or a horizontal rule ("---") on its own line. The MUST marker
    # appears inside.
    r"(^##\s+\d+\.[^\n]*\n(?:(?!^##\s|^---\s*$).*\n?)*)",
    re.MULTILINE,
)


@dataclass
class RenderedTemplate:
    leaf_id:          str
    template_version: int
    body_md:          str            # post-render markdown
    must_total:       int            # MUSTs in the source template
    must_rendered:    int            # MUSTs surviving after N/A strip
    must_dropped:     int            # MUSTs stripped as N/A for this tenant
    placeholders_filled: int         # identity placeholders substituted


def _strip_na_sections(
    body_md:       str,
    na_must_ids:   set[str],
) -> tuple[str, int, int]:
    """Drop section blocks that contain a <<MUST item:X>> marker for any
    must_id in na_must_ids. Returns (new_body, dropped_count, kept_count).

    A "section" is the run of lines from a `## N. Heading` line up to
    (but not including) the next `## ` heading or a `---` rule.

    The instruction blockquote at the top of the doc is untouched —
    only `## N.` numbered sections are candidates for stripping.
    """
    if not na_must_ids:
        # Fast path — also count for telemetry
        kept = body_md.count("<<MUST item:")
        return body_md, 0, kept

    sections = _MUST_BLOCK_RE.findall(body_md)
    dropped = 0
    kept    = 0
    for section in sections:
        # Find the MUST marker in this section
        m = re.search(r"<<MUST\s+(item:[^>\s]+)>>", section)
        if not m:
            continue
        must_id = m.group(1)
        if must_id in na_must_ids:
            body_md = body_md.replace(section, "", 1)
            dropped += 1
        else:
            kept += 1
    return body_md, dropped, kept


def _substitute_placeholders(
    body_md:    str,
    tenant_row: dict,
) -> tuple[str, int]:
    """Replace <<TENANT_NAME>>, <<TENANT_SECTOR>>, <<TENANT_COUNTRY>>,
    <<TENANT_SHORT>>, <<GENERATED_DATE>> with values from the tenants
    table. Returns (new_body, n_filled).
    """
    today = _dt.date.today().isoformat()
    fills = {
        "<<TENANT_NAME>>":    (tenant_row.get("name") or "").strip()       or "<<TENANT_NAME>>",
        "<<TENANT_SHORT>>":   (tenant_row.get("short_code") or "").strip() or "<<TENANT_SHORT>>",
        "<<TENANT_SECTOR>>":  (tenant_row.get("sector") or "").strip()     or "<<TENANT_SECTOR>>",
        "<<TENANT_COUNTRY>>": (tenant_row.get("country") or "").strip()    or "<<TENANT_COUNTRY>>",
        "<<TENANT_INDUSTRY>>":(tenant_row.get("industry") or "").strip()   or "<<TENANT_INDUSTRY>>",
        "<<GENERATED_DATE>>": today,
    }
    n_filled = 0
    for marker, value in fills.items():
        if value != marker and marker in body_md:
            body_md = body_md.replace(marker, value)
            n_filled += 1
    return body_md, n_filled


def render_template(
    pg_conn,
    tenant_id:      str,
    leaf_id:        str,
    *,
    include_header: bool = False,
) -> Optional[RenderedTemplate]:
    """Look up template by leaf_id, apply tenant scope + placeholder
    substitution, return RenderedTemplate. Returns None when leaf_id
    not in templates table.

    Caller is responsible for `SET app.tenant_id` (RLS) — the
    tenant_must_overrides query relies on it.
    """
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT template_version, body_md, must_count "
            "  FROM templates WHERE leaf_id = %s",
            (leaf_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        template_version, body_md, must_total = row

        # Tenant identity
        cur.execute(
            "SELECT name, slug, short_code, sector, country, industry "
            "  FROM tenants WHERE id = %s::uuid",
            (tenant_id,),
        )
        t_row = cur.fetchone()
        tenant_row = (
            dict(zip(
                ["name", "slug", "short_code", "sector", "country", "industry"],
                t_row,
            )) if t_row else {}
        )

        # N/A MUSTs from tenant_must_overrides (applies = FALSE)
        cur.execute(
            "SELECT must_id FROM tenant_must_overrides "
            " WHERE tenant_id = %s::uuid AND applies = FALSE",
            (tenant_id,),
        )
        na_must_ids = {r[0] for r in cur.fetchall()}

    body, dropped, kept = _strip_na_sections(body_md, na_must_ids)
    body, n_filled      = _substitute_placeholders(body, tenant_row)

    if include_header:
        header = (
            f"<!-- Rendered for {tenant_row.get('name','(unknown tenant)')} "
            f"on {_dt.date.today().isoformat()} — "
            f"leaf {leaf_id} v{template_version} — "
            f"{kept}/{must_total} MUSTs in scope -->\n\n"
        )
        body = header + body

    return RenderedTemplate(
        leaf_id             = leaf_id,
        template_version    = template_version,
        body_md             = body,
        must_total          = must_total,
        must_rendered       = kept,
        must_dropped        = dropped,
        placeholders_filled = n_filled,
    )
