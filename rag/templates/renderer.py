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

# Tabular EDIT-ZONE markers — wrap a markdown table. Captures the leaf_id
# in group 1 and the zone content (header + separator + data rows) in
# group 2. Mirrors extractor._TEMPLATED_TABLE_ZONE_RE.
_TABLE_ZONE_RE = re.compile(
    r"<!--\s*EDIT-ZONE-START\s+leaf:(req:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->"
    r"(.*?)"
    r"<!--\s*EDIT-ZONE-END\s+leaf:\1\s*-->",
    re.DOTALL | re.IGNORECASE,
)

# TABLE-COLUMNS metadata: maps leaf_id → ordered list of item_ids
# (one per table column, left-to-right).
_TABLE_COLUMNS_RE = re.compile(
    r"<!--\s*TABLE-COLUMNS\s+leaf:(req:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->"
    r"(.*?)"
    r"<!--\s*/TABLE-COLUMNS\s*-->",
    re.DOTALL | re.IGNORECASE,
)
_TABLE_COLUMN_RE = re.compile(
    r"<!--\s*column:\s*(item:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->",
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


# Tenant-facing labels for inference_source. The internal slug is a
# useful audit tag but reads as jargon in a rendered template — the
# tenant just wants to know 'where did this text come from'.
_SOURCE_HUMAN: dict[str, str] = {
    "templated":  "prior template edit",
    "form":       "form entry",
    "workbook":   "uploaded workbook",
    "extracted":  "uploaded document",
    "leaf_scan":  "prior finding",
}


def _humanize_source(src: str) -> str:
    return _SOURCE_HUMAN.get(src, (src or "").replace("_", " "))


# Machine control-ref labels like "GDPR:2016/679:Art.32" don't belong in
# tenant-visible text. Reduce to the short human form the rest of the
# product uses.
def _humanize_control_ref(std_ref: str) -> str:
    s = std_ref or ""
    if s.startswith("GDPR:"):
        parts = s.split(":", 2)
        return f"GDPR {parts[-1]}" if len(parts) > 1 else s
    if s.startswith("ISO27001:") or s.startswith("ISO27701:"):
        # 'ISO27001:2022:A.5.15' -> 'ISO 27001:2022 A.5.15'
        parts = s.split(":", 2)
        if len(parts) == 3:
            fam, yr, ref = parts
            fam_h = "ISO 27001" if fam == "ISO27001" else "ISO 27701"
            return f"{fam_h}:{yr} {ref}"
        return s
    return s


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
    profile:    Optional[dict] = None,
) -> tuple[str, int]:
    """Replace placeholders with tenant-specific values.

    Two sources:
      1. `tenants` table — name / short_code / sector / country /
         industry. Fixed schema.
      2. `tenant_profile` (k/v) — open-ended set covering CEO_NAME,
         CISO_NAME, DPO_NAME, ISMS_MANAGER_NAME, ISMS_OWNER_NAME,
         HR_PARTNER_NAME, AWARENESS_LEAD_NAME, REGISTERED_ADDRESS,
         COMPANY_NUMBER, TENANT_DOMAIN, PRODUCT_OR_SERVICE,
         APPROVAL_DATE, NEXT_REVIEW_DATE, etc.

    Placeholder convention: `<<UPPER_SNAKE_NAME>>` ↔
    `profile_key = 'upper_snake_name'.lower()`. Unknown placeholders
    (not in `tenants` and not in `tenant_profile`) stay as literal
    `<<NAME>>` text — tenant can fill them by hand or add a profile
    row.

    Returns (new_body, n_filled).
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
    if profile:
        for k, v in profile.items():
            placeholder = f"<<{k.upper()}>>"
            value = (v or "").strip()
            if value:
                # `tenants` table wins on key collision (e.g.
                # tenant_profile shouldn't override TENANT_NAME).
                fills.setdefault(placeholder, value)
    n_filled = 0
    for marker, value in fills.items():
        if value != marker and marker in body_md:
            body_md = body_md.replace(marker, value)
            n_filled += 1
    return body_md, n_filled


def _extract_leaf_title(body_md: str, leaf_id: str) -> str:
    """Pull the first H1 from the body (the leaf's title). Falls back to
    a slug-derived title from leaf_id if no H1."""
    m = re.search(r"^#\s+(.+?)\s*$", body_md, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Fallback: req:A.5.18:access_revocation_record → "Access Revocation Record"
    from rag.id_types import leaf_evidence_type
    slug = leaf_evidence_type(leaf_id) or leaf_id
    return slug.replace("_", " ").title()


def _extract_control_ref_from_leaf_id(leaf_id: str) -> str:
    """req:A.5.18:access_revocation_record → A.5.18"""
    from rag.id_types import leaf_control_ref
    return leaf_control_ref(leaf_id) or leaf_id


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
            label = _humanize_control_ref(f"{std}:{ref}")
            if src_std and src_ref:
                src = _humanize_control_ref(f"{src_std}:{src_ref}")
            else:
                src = doc
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
                f"**From {d.document_name} "
                f"({_humanize_source(d.inference_source)}, "
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


def _fetch_tabular_rows(
    pg_conn,
    tenant_id: str,
    leaf_id:   str,
) -> list[dict]:
    """Fetch the tenant's most-recent active per-row content for a
    tabular leaf. Returns ordered list of {row_index, column_values}.

    "Most-recent active" = the latest document_id with rows for this leaf.
    Re-extracts supersede the prior document's rows (writer flips
    is_active=FALSE on the older document_id), so the active-row set is
    a single document's worth at any time.
    """
    rows: list[dict] = []
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
        )
        cur.execute(
            """
            SELECT row_index, column_values
              FROM tabular_evidence_rows
             WHERE tenant_id = %s::uuid
               AND leaf_id   = %s
               AND is_active = TRUE
             ORDER BY document_id, row_index
            """,
            (tenant_id, leaf_id),
        )
        for ri, cv in cur.fetchall():
            rows.append({"row_index": ri, "column_values": cv or {}})
    return rows


def _prefill_table_zones(body_md: str, pg_conn, tenant_id: str) -> tuple[str, int]:
    """For each tabular EDIT-ZONE in the body, replace the empty
    template table with one constructed from the tenant's prior
    per-row evidence. Returns (new_body, n_zones_prefilled).

    Header row is preserved verbatim from the template (so column
    titles stay tenant-readable). Separator row preserved. Data rows
    replaced with one row per prior tabular_evidence_rows entry,
    cell-by-cell from column_values keyed by the TABLE-COLUMNS
    metadata's item_id order.
    """
    # Build leaf_id → ordered item_ids map
    leaf_columns: dict[str, list[str]] = {}
    for tc in _TABLE_COLUMNS_RE.finditer(body_md):
        leaf_id = tc.group(1)
        cols    = _TABLE_COLUMN_RE.findall(tc.group(2))
        if cols:
            leaf_columns[leaf_id] = cols
    if not leaf_columns:
        return body_md, 0

    n_prefilled = 0

    def _replace_zone(m: "re.Match[str]") -> str:
        nonlocal n_prefilled
        leaf_id   = m.group(1)
        zone_text = m.group(2)
        columns   = leaf_columns.get(leaf_id)
        if not columns:
            return m.group(0)

        prior = _fetch_tabular_rows(pg_conn, tenant_id, leaf_id)
        if not prior:
            return m.group(0)

        # Extract header + separator lines verbatim from the existing zone
        header_line = ""
        sep_line    = ""
        for raw in zone_text.splitlines():
            line = raw.strip()
            if not line.startswith("|"):
                continue
            if not header_line:
                header_line = raw
                continue
            if re.fullmatch(r"\|[\s\-:|]+\|", line):
                sep_line = raw
                break
        if not header_line:
            return m.group(0)
        if not sep_line:
            sep_line = "|" + "|".join(["---"] * len(columns)) + "|"

        data_lines: list[str] = []
        for r in prior:
            cv = r["column_values"]
            # Sanitise cell text: strip newlines + pipes (markdown table
            # boundary chars). Empty cells render as blank.
            cells = []
            for item_id in columns:
                raw_text = (cv.get(item_id) or "")
                cell = raw_text.replace("\n", " ").replace("|", "\\|").strip()
                cells.append(cell)
            data_lines.append("| " + " | ".join(cells) + " |")

        new_zone = "\n" + header_line + "\n" + sep_line + "\n" + "\n".join(data_lines) + "\n"
        n_prefilled += 1
        return (
            f"<!-- EDIT-ZONE-START leaf:{leaf_id} -->" +
            new_zone +
            f"<!-- EDIT-ZONE-END leaf:{leaf_id} -->"
        )

    new_body = _TABLE_ZONE_RE.sub(_replace_zone, body_md)
    return new_body, n_prefilled


def _apply_prefills_and_wrap_edit_zones(
    body_md:       str,
    prefills:      dict[str, str],
) -> tuple[str, int]:
    """Per-MUST transformation:

      1. Substitute the FIRST <<TEXT>> / <<NAME>> placeholder in the
         section with the composed prefill content (if any)
      2. Wrap the placeholder OR the prefill substitution with edit-zone
         markers `<!-- EDIT-ZONE-START item:X -->` ... `<!-- EDIT-ZONE-END item:X -->`

    Edit-zone markers are what the extractor's fast-path uses to separate
    *tenant authoring* from *template scaffolding* (guidance prose, MUST
    headings, prefilled prior evidence). Without them, the extractor
    would treat the guidance + prefill as tenant evidence on upload —
    "circular counting" where the tenant gets credit for our scaffold
    + their own prior approved findings.

    Returns (new_body, n_musts_prefilled).
    """
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

        # Substitute first placeholder in owned (if prefill available)
        prefill = prefills.get(item_id)
        ph_match = _PLACEHOLDER_RE.search(owned)
        if prefill and ph_match:
            # Replace placeholder with EDIT-ZONE-wrapped prefill
            wrapped = (
                f"<!-- EDIT-ZONE-START {item_id} -->\n"
                f"{prefill}\n"
                f"<!-- EDIT-ZONE-END {item_id} -->"
            )
            owned = owned[:ph_match.start()] + wrapped + owned[ph_match.end():]
            n_prefilled += 1
        elif ph_match:
            # No prefill, but placeholder present — wrap the placeholder
            # itself so the extractor knows where tenant authoring starts.
            wrapped = (
                f"<!-- EDIT-ZONE-START {item_id} -->\n"
                f"{ph_match.group(0)}\n"
                f"<!-- EDIT-ZONE-END {item_id} -->"
            )
            owned = owned[:ph_match.start()] + wrapped + owned[ph_match.end():]

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

        # Tenant profile (key/value) for open-ended placeholders. schema_v49.
        # RLS scopes per tenant; missing rows just leave placeholders intact.
        cur.execute(
            "SELECT set_config('app.tenant_id', %s::text, true)", (tenant_id,),
        )
        cur.execute(
            "SELECT profile_key, profile_value FROM tenant_profile "
            " WHERE tenant_id = %s::uuid",
            (tenant_id,),
        )
        tenant_profile = {k: v for k, v in cur.fetchall()}

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
    # (tenant requested blank template via ?empty=true).
    #
    # EDIT-ZONE wrapping ALWAYS runs (independent of prefill on/off) so
    # the upload-side extractor has stable markers to find tenant
    # authoring vs template scaffolding. Without these markers, the
    # extractor would treat v2 guidance prose + prefilled prior evidence
    # as new tenant evidence on re-upload — "circular counting".
    musts_prefilled       = 0
    prefill_sources_out: list[PrefillSource] = []
    prefills: dict[str, str] = {}
    if prefill:
        surviving_must_ids = list(set(_MUST_MARKER_RE.findall(body)))
        evidence_per_must  = _fetch_prefill_evidence(pg_conn, tenant_id, surviving_must_ids)
        bridge_per_must    = _fetch_bridge_footers(pg_conn, tenant_id, surviving_must_ids)

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

    # ALWAYS wrap edit zones — even when prefill is off, the placeholders
    # need to be flagged for the upload-side extractor.
    body, musts_prefilled = _apply_prefills_and_wrap_edit_zones(body, prefills)

    # Tabular-zone prefill — for templates with a `EDIT-ZONE-START leaf:`
    # block (register/record/matrix/log/inventory shapes), replay the
    # tenant's prior per-row content from tabular_evidence_rows.
    # Schema_v47; gated on prefill=True so ?empty=true still produces a
    # blank table for fresh starts. See [[tabular-evidence-rows-2026-06-26]].
    n_tables_prefilled = 0
    if prefill:
        body, n_tables_prefilled = _prefill_table_zones(body, pg_conn, tenant_id)

    body, n_filled = _substitute_placeholders(body, tenant_row, profile=tenant_profile)

    if include_header:
        # Two-layer header:
        # 1. Tenant-visible CONSULTANT PREAMBLE — disclaimer + tenant
        #    name + generation date + leaf identity. Reads as advisory,
        #    not authoritative. Strips the on-disk H1 + leading
        #    instruction blockquote (replaced by the preamble's own
        #    H1 + disclaimer).
        # 2. Hidden provenance HTML comment — version + MUST counts +
        #    prefill telemetry. Invisible in rendered markdown views.
        tenant_name = tenant_row.get("name") or "(unknown tenant)"
        leaf_title  = _extract_leaf_title(body_md, leaf_id)
        control_ref = _extract_control_ref_from_leaf_id(leaf_id)
        std_label   = "ISO/IEC 27001:2022" if not control_ref.startswith("Art.") else "GDPR 2016/679"
        gen_date    = _dt.date.today().isoformat()

        # Strip the on-disk YAML frontmatter block (--- ... ---) — its
        # leaf_id/version/counts already live in the provenance comment.
        body = re.sub(r"^---\n.*?\n---\n+", "", body, count=1, flags=re.DOTALL)
        # Strip the on-disk H1 line (leaf title) — we replace it with
        # the tenant-personalised preamble H1.
        body = re.sub(r"^#\s+[^\n]+\n+", "", body, count=1, flags=re.MULTILINE)
        # Strip the leading instruction blockquote ("> **Replace each
        # blank fill-in marker...") — redundant with the preamble's
        # disclaimer.
        body = re.sub(
            r"^>\s*\*\*Replace each blank fill-in marker[^\n]+\n+",
            "", body, count=1, flags=re.MULTILINE,
        )

        preamble = (
            f"# {leaf_title} — drafted for {tenant_name}\n\n"
            f"> **Advisory template.** A starting draft to help your "
            f"compliance journey. NOT an authoritative evidence "
            f"guideline — an auditor will examine your *actual* "
            f"artefacts, not this template. Use what's useful, change "
            f"what isn't, delete what doesn't apply.\n\n"
            f"> _Generated {gen_date} · "
            f"{control_ref} · {std_label}_\n\n"
            f"---\n\n"
        )
        provenance = (
            f"<!-- Rendered for {tenant_name} on {gen_date} — "
            f"leaf {leaf_id} v{template_version} — "
            f"{kept}/{must_total} MUSTs in scope"
        )
        if prefill and musts_prefilled:
            provenance += f" — {musts_prefilled} prefilled from prior evidence"
        provenance += " -->\n\n"
        body = provenance + preamble + body

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
