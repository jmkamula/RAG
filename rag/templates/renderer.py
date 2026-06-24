"""
rag/templates/renderer.py — render a stored template body_md for a tenant.

Tenant-scoped transformations applied in order:
  1. Lookup template body from `templates` table (Postgres mirror of
     db/templates/*.md filesystem source-of-truth)
  2. Strip MUST sections where tenant_must_overrides.applies = FALSE
     for that must_id (Arion cloud-only: drops A.5.15:physical_rules etc.)
  3. Per-MUST PREFILL — for each <<MUST item:X>> in the body, look up
     active+approved+present rows in document_findings, dedup across
     sources, compose with attribution into the section's <<TEXT>> /
     <<NAME>> placeholder. xfw_bridge bridges sourcing FROM the leaf
     get a "Related cross-framework evidence" footer per section.
  4. Substitute identity placeholders (<<TENANT_NAME>>, <<TENANT_SECTOR>>,
     <<TENANT_COUNTRY>>, <<GENERATED_DATE>>) from the `tenants` table
  5. Optionally prepend a generation header (off by default — caller
     decides via include_header param)

The <<MUST item:X>> / <<SHOULD item:X>> markers stay intact — they bind
the upload-side extractor when the tenant uploads back. The placeholder
content between them is what tenants edit; when prefill is on, those
zones come back populated with the tenant's prior approved evidence.

Section stripping is structural: removes the lines from the section
heading through the next heading or the next horizontal-rule marker
(`---` on its own line).
"""

from __future__ import annotations

import datetime as _dt
import logging
import re
from dataclasses import dataclass, field
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

_MUST_MARKER_RE = re.compile(
    r"<<MUST\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>",
)

_PLACEHOLDER_RE = re.compile(
    r"<<(?:TEXT|NAME)>>",
)

_LEAFSCAN_PREFIX_RE = re.compile(
    r"^\[leaf-scan back-bind from finding [a-z0-9]+\]\s*",
    re.IGNORECASE,
)

# Source trust hierarchy — lower number = higher trust. xfw_bridge
# intentionally absent (bridges are surfaced as section footers, not
# treated as prefill content).
_SOURCE_RANK: dict[str, int] = {
    "templated":  1,   # tenant authored directly into our template
    "form":       2,   # tenant authored directly into our form
    "workbook":   3,   # YAML-parsed tenant Excel
    "extracted":  4,   # LLM-extracted from tenant doc
    "leaf_scan":  5,   # back-bind from existing finding
}


@dataclass
class EvidenceRow:
    must_id:         str
    inference_source: str
    excerpt:         str            # cleaned (leaf-scan prefix stripped)
    document_name:   str
    extracted_at:    _dt.datetime

    @property
    def source_rank(self) -> int:
        return _SOURCE_RANK.get(self.inference_source, 99)


@dataclass
class PrefillSource:
    must_id:         str
    inference_source: str
    document_name:   str
    extracted_at_iso: str


@dataclass
class RenderedTemplate:
    leaf_id:          str
    template_version: int
    body_md:          str            # post-render markdown
    must_total:       int            # MUSTs in the source template
    must_rendered:    int            # MUSTs surviving after N/A strip
    must_dropped:     int            # MUSTs stripped as N/A for this tenant
    placeholders_filled: int         # identity placeholders substituted
    musts_prefilled:  int            # MUSTs with prefill content composed
    prefill_sources:  list[PrefillSource] = field(default_factory=list)


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


def _clean_excerpt(text: str) -> str:
    """Strip the leaf-scan back-bind marker prefix that's an internal
    annotation, not tenant content. Leaves the rest untouched."""
    return _LEAFSCAN_PREFIX_RE.sub("", text or "").strip()


def _fetch_prefill_evidence(
    pg_conn,
    tenant_id: str,
    must_ids:  list[str],
) -> dict[str, list[EvidenceRow]]:
    """For each must_id, fetch active+approved+present document_findings
    grouped by checklist_item_id. Excludes xfw_bridge (handled separately
    as a section footer)."""
    if not must_ids:
        return {}
    out: dict[str, list[EvidenceRow]] = {mid: [] for mid in must_ids}
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
        )
        cur.execute(
            """
            SELECT df.checklist_item_id,
                   df.inference_source,
                   df.excerpt,
                   COALESCE(cd.filename, '(unknown source)') AS document_name,
                   df.extracted_at
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE cd.tenant_id      = %s::uuid
               AND cd.is_active      = TRUE
               AND cd.is_current     = TRUE
               AND df.is_active      = TRUE
               AND df.review_status  = 'approved'
               AND df.status         = 'present'
               AND df.inference_source <> 'xfw_bridge'
               AND df.checklist_item_id = ANY(%s)
             ORDER BY df.extracted_at DESC
            """,
            (tenant_id, must_ids),
        )
        for row in cur.fetchall():
            mid, src, excerpt, doc_name, extracted_at = row
            out[mid].append(EvidenceRow(
                must_id          = mid,
                inference_source = src,
                excerpt          = _clean_excerpt(excerpt or ""),
                document_name    = doc_name,
                extracted_at     = extracted_at,
            ))
    return out


def _fetch_bridge_footers(
    pg_conn,
    tenant_id: str,
    must_ids:  list[str],
) -> dict[str, list[str]]:
    """For each must_id, fetch xfw_bridge rows where this must_id is the
    BOUND target (`checklist_item_id`) — those are cross-framework
    inheritances surfaced as section footers. Returns {must_id: [
    "GDPR:2016/679:Art.32 (from Access Control Policy.docx)", ...]}.
    """
    if not must_ids:
        return {}
    out: dict[str, list[str]] = {mid: [] for mid in must_ids}
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
        )
        cur.execute(
            """
            SELECT df.checklist_item_id,
                   df.standard_id,
                   df.control_ref,
                   COALESCE(cd.filename, '(unknown)') AS doc_name,
                   df.inferred_from_standard_id,
                   df.inferred_from_control_ref
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE cd.tenant_id      = %s::uuid
               AND df.is_active      = TRUE
               AND df.inference_source = 'xfw_bridge'
               AND df.checklist_item_id = ANY(%s)
            """,
            (tenant_id, must_ids),
        )
        for row in cur.fetchall():
            mid, std, ref, doc, src_std, src_ref = row
            label = f"{std}:{ref}"
            src   = f"{src_std}:{src_ref}" if src_std and src_ref else doc
            out[mid].append(f"{label} (from {src})")
    return out


def _dedup_evidence(rows: list[EvidenceRow]) -> list[EvidenceRow]:
    """Source-rank sort then dedup: exact (after whitespace+case
    normalisation) + substring containment. Highest-trust source wins
    when texts are equivalent."""
    rows_sorted = sorted(rows, key=lambda r: (r.source_rank, -r.extracted_at.timestamp()))
    seen_norm: list[str] = []
    distinct:  list[EvidenceRow] = []
    for r in rows_sorted:
        norm = re.sub(r"\s+", " ", r.excerpt.lower()).strip()
        if not norm:
            continue
        # Substring or exact-match dedup
        if any(norm == s or norm in s or s in norm for s in seen_norm):
            continue
        seen_norm.append(norm)
        distinct.append(r)
    return distinct


def _compose_prefill_block(
    must_id:       str,
    distinct_rows: list[EvidenceRow],
    bridge_labels: list[str],
) -> Optional[str]:
    """Build the substitution content for ONE MUST's <<TEXT>>/<<NAME>>
    placeholder. Returns None when no prefill exists (placeholder stays).
    Single source: just the excerpt + attribution comment. Multiple
    sources: concatenated with **From <doc>:** headers. Bridges are
    appended as a footer line regardless."""
    if not distinct_rows and not bridge_labels:
        return None

    parts: list[str] = []
    if len(distinct_rows) == 1:
        d = distinct_rows[0]
        parts.append(d.excerpt)
        parts.append(
            f"<!-- prefilled from {d.document_name} via "
            f"{d.inference_source} on {d.extracted_at.date().isoformat()} -->"
        )
    elif len(distinct_rows) > 1:
        for d in distinct_rows:
            parts.append(
                f"**From {d.document_name} ({d.inference_source}, "
                f"{d.extracted_at.date().isoformat()}):**"
            )
            parts.append(d.excerpt)
        parts.append(f"<!-- prefilled from {len(distinct_rows)} sources -->")

    if bridge_labels:
        if parts:
            parts.append("")  # blank-line separator before footer
        bridge_lines = [f"↳ Related cross-framework evidence: {b}" for b in bridge_labels]
        parts.extend(bridge_lines)

    return "\n\n".join(parts)


def _apply_prefills(
    body_md:       str,
    prefills:      dict[str, str],
) -> tuple[str, int]:
    """For each <<MUST item:X>> marker in body_md, if a prefill exists
    for that item_id, replace the FIRST <<TEXT>> or <<NAME>> placeholder
    that appears in the marker's section (between this marker and the
    next heading/marker/rule).

    Returns (new_body, n_musts_prefilled).
    """
    if not prefills:
        return body_md, 0

    # Find all MUST markers + their positions
    markers = list(_MUST_MARKER_RE.finditer(body_md))
    if not markers:
        return body_md, 0

    out_parts: list[str] = []
    cursor = 0
    n_prefilled = 0

    for i, m in enumerate(markers):
        item_id = m.group(1)
        # Pre-marker text + the marker itself stay verbatim
        out_parts.append(body_md[cursor:m.end()])
        # Determine section bounds: from marker end to next marker start
        # OR end of doc; further truncate at the next heading or `---`
        section_end_outer = markers[i + 1].start() if i + 1 < len(markers) else len(body_md)
        section_body = body_md[m.end():section_end_outer]
        boundary = re.search(r"^(?:#{2,}\s|---\s*$)", section_body, re.MULTILINE)
        section_split = boundary.start() if boundary else len(section_body)
        owned     = section_body[:section_split]
        afterward = section_body[section_split:]

        # Substitute first placeholder in owned
        prefill = prefills.get(item_id)
        if prefill and _PLACEHOLDER_RE.search(owned):
            owned = _PLACEHOLDER_RE.sub(prefill, owned, count=1)
            n_prefilled += 1

        out_parts.append(owned)
        out_parts.append(afterward)
        cursor = section_end_outer

    if cursor < len(body_md):
        out_parts.append(body_md[cursor:])

    return "".join(out_parts), n_prefilled


def render_template(
    pg_conn,
    tenant_id:           str,
    leaf_id:             str,
    *,
    include_header:      bool = False,
    prefill:             bool = True,
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

    # PREFILL — for each MUST surviving the N/A strip, look up the
    # tenant's prior approved+active evidence and compose it into the
    # section's <<TEXT>>/<<NAME>> placeholder. Skipped when prefill=False
    # (tenant requested blank template via ?empty=true) or when there's
    # no evidence on any MUST.
    musts_prefilled       = 0
    prefill_sources_out: list[PrefillSource] = []
    if prefill:
        surviving_must_ids = list(set(_MUST_MARKER_RE.findall(body)))
        evidence_per_must  = _fetch_prefill_evidence(pg_conn, tenant_id, surviving_must_ids)
        bridge_per_must    = _fetch_bridge_footers(pg_conn, tenant_id, surviving_must_ids)

        prefills: dict[str, str] = {}
        for must_id in surviving_must_ids:
            distinct = _dedup_evidence(evidence_per_must.get(must_id, []))
            bridges  = bridge_per_must.get(must_id, [])
            block = _compose_prefill_block(must_id, distinct, bridges)
            if block is not None:
                prefills[must_id] = block
            for d in distinct:
                prefill_sources_out.append(PrefillSource(
                    must_id          = must_id,
                    inference_source = d.inference_source,
                    document_name    = d.document_name,
                    extracted_at_iso = d.extracted_at.date().isoformat(),
                ))

        body, musts_prefilled = _apply_prefills(body, prefills)

    body, n_filled = _substitute_placeholders(body, tenant_row)

    if include_header:
        header = (
            f"<!-- Rendered for {tenant_row.get('name','(unknown tenant)')} "
            f"on {_dt.date.today().isoformat()} — "
            f"leaf {leaf_id} v{template_version} — "
            f"{kept}/{must_total} MUSTs in scope"
        )
        if prefill and musts_prefilled:
            header += f" — {musts_prefilled} prefilled from prior evidence"
        header += " -->\n\n"
        body = header + body

    return RenderedTemplate(
        leaf_id             = leaf_id,
        template_version    = template_version,
        body_md             = body,
        must_total          = must_total,
        must_rendered       = kept,
        must_dropped        = dropped,
        placeholders_filled = n_filled,
        musts_prefilled     = musts_prefilled,
        prefill_sources     = prefill_sources_out,
    )
