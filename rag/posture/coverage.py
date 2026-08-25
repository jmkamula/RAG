"""
Ship 93'.c — Coverage aggregate (Dashboard "Coverage" tab)

Yellow items (partial + missing MUSTs) across every control are
individually actionable inside the product after Ships 92-94:
  * partial evidence explains "here's what's missing to close it"
  * missing MUST explains "add column X or upload doc Y"
  * external cites carry attestation prompts
  * closure trail links resolvers to the partials they closed
  * auditor Evidence Package export mirrors the same narrative

But the tenant still has to walk control-by-control to see the
total shape. This module builds the aggregate view rendered as
the Dashboard "Coverage" tab (sibling to "Overview" heatmap):

  * bucket 1 — Ready to close (controls with ≥1 partial MUST)
  * bucket 2 — In progress (controls with some direct evidence
                but ≥1 missing MUST)
  * bucket 3 — Not started (controls with zero direct evidence
                and ≥1 missing MUST)

Within each bucket, controls are sorted by (n_partial DESC,
n_direct DESC, control_ref ASC) — most-close-able first. Only
top-K per bucket surface with close-path prose (bounded work);
totals cover the whole picture.

Reads posture_must_verdicts (SSoT). Reuses explain_partial +
explain_missing for close-path narrative — never forks the prose.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

_MUST_LEAF_RE = re.compile(r"^item:([^:]+):(.+)$")


def _humanize_standard_id(standard_id: str) -> str:
    """'ISO27001:2022' -> 'ISO 27001:2022'. Mirrors evidence_package."""
    if standard_id.startswith("ISO27001:"):
        return f"ISO 27001:{standard_id.split(':', 1)[1]}"
    if standard_id.startswith("ISO27701:"):
        return f"ISO 27701:{standard_id.split(':', 1)[1]}"
    if standard_id.startswith("GDPR:"):
        return "GDPR"
    return standard_id


def _strip_html_for_ui(html: str) -> str:
    """Strip inline HTML from explain_* prose for JSON surface."""
    if not html:
        return ""
    t = re.sub(r"</?(?:strong|em|code)>", "", html)
    return re.sub(r"\s+", " ", t).strip()


def _resolve_control_titles(neo4j_driver, keys: list[tuple[str, str]]) -> dict[tuple[str, str], str]:
    """Batch-resolve control titles from Neo4j. Best-effort — silent on failure."""
    out: dict[tuple[str, str], str] = {}
    if neo4j_driver is None or not keys:
        return out
    ids = [f"{sid}:{ref}" for (sid, ref) in keys]
    try:
        with neo4j_driver.session() as s:
            for rec in s.run(
                "MATCH (n) WHERE n.id IN $ids "
                "RETURN n.id AS id, n.title AS title",
                ids=ids,
            ):
                _id = rec["id"] or ""
                _t  = rec["title"] or ""
                if ":" in _id:
                    _std, _ref = _id.split(":", 1)
                    # standard_id may itself contain ':' (e.g. 'GDPR:2016/679')
                    # but the ref is always the last colon-delimited segment
                    _std2, _sep, _ref2 = _id.rpartition(":")
                    if _sep:
                        out[(_std2, _ref2)] = _t
    except Exception as e:
        logger.warning("coverage: title batch resolve failed: %s", e)
    return out


def _fetch_partial_mapping_context(pg_conn, tenant_id: str, must_id: str) -> dict:
    """Look up mapping_id + sheet_name + matched_column for a partial MUST.
    Returns {} if no active partial exists (SSoT + Postgres can drift under
    concurrent writes; degrade gracefully)."""
    out: dict = {}
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s::text, false)",
                (tenant_id,),
            )
            cur.execute(
                """
                SELECT wip.mapping_id, wip.sheet_name, df.excerpt
                  FROM document_findings df
                  JOIN workbook_intake_proposal wip
                    ON wip.id = df.workbook_proposal_id
                 WHERE df.tenant_id = %s::uuid
                   AND df.is_active
                   AND df.checklist_item_id = %s
                   AND df.status = 'partial'
                   AND df.review_status = 'approved'
                 LIMIT 1
                """,
                (tenant_id, must_id),
            )
            row = cur.fetchone()
    except Exception as e:
        logger.warning("coverage: mapping-context fetch failed for %s: %s",
                       must_id, e)
        return out
    if not row:
        return out
    mid, sheet, excerpt = row
    out["mapping_id"] = mid
    out["sheet_name"] = sheet or ""
    # Best-effort column extraction from excerpt (same idiom as EP)
    m = re.search(r"col '([^']*)'", excerpt or "")
    out["matched_column"] = m.group(1) if m else ""
    return out


def _close_path_prose(pg_conn, tenant_id: str, verdict) -> str:
    """Compute the close-path prose for one yellow verdict.

    Reuses explain_partial for 'partial' state + explain_missing for
    'missing' state. Both already emit auditor-safe humanized prose;
    we strip inline HTML for the JSON surface.
    """
    try:
        if verdict.state == "partial":
            ctx = _fetch_partial_mapping_context(pg_conn, tenant_id, verdict.must_id)
            if ctx.get("mapping_id"):
                from rag.posture.partial_explainer import explain_partial
                payload = explain_partial(
                    must_id        = verdict.must_id,
                    mapping_id     = ctx["mapping_id"],
                    sheet_name     = ctx["sheet_name"],
                    matched_column = ctx["matched_column"],
                )
                return _strip_html_for_ui(payload.get("primary_prose", ""))
            # Doc-extractor partial (no workbook mapping): critic-verifier's
            # semantic-fit gate accepted the finding as partial. Reuse
            # explain_missing for the close path (add column / upload doc)
            # but reframe the opening so it acknowledges partial evidence
            # already exists.
            from rag.posture.partial_explainer import explain_missing
            payload = explain_missing(
                must_id = verdict.must_id,
                leaf_id = f"req:{verdict.control_ref}:*",
            )
            prose = _strip_html_for_ui(payload.get("primary_prose", ""))
            # Rewrite "No evidence yet for X" → "Partial evidence on file
            # for X — to move to full coverage": preserves the close path
            # tail intact.
            label = _humanize_must_label(verdict.must_id)
            missing_prefix = f"No evidence yet for {label}."
            if prose.startswith(missing_prefix):
                prose = (
                    f"Partial evidence on file for {label} — to move "
                    f"to full coverage: {prose[len(missing_prefix):].strip()}"
                )
            return prose
        # 'missing' — no workbook proposal to resolve; explain_missing
        # scans the catalog for any pass binding this MUST
        from rag.posture.partial_explainer import explain_missing
        # leaf_id isn't a hard requirement for explain_missing; it uses
        # must_id + the mapping cache. Pass control_ref as a leaf hint.
        payload = explain_missing(
            must_id = verdict.must_id,
            leaf_id = f"req:{verdict.control_ref}:*",
        )
        return _strip_html_for_ui(payload.get("primary_prose", ""))
    except Exception as e:
        logger.warning("coverage: close-path prose failed for %s: %s",
                       verdict.must_id, e)
        return ""


def _humanize_must_label(must_id: str) -> str:
    """Delegate to partial_explainer's canonical humanizer (single source)."""
    try:
        from rag.posture.partial_explainer import _humanize_must_label as _h
        return _h(must_id)
    except Exception:
        return must_id


def build_coverage(
    pg_conn,
    neo4j_driver,
    tenant_id: str,
    k_per_bucket: int = 20,
    max_yellow_per_control: int = 3,
) -> dict:
    """Build the aggregate Fix Workload payload for a tenant.

    Returns:
      {
        "generated_at": ISO-8601 UTC,
        "summary": {
            "controls_ready_to_close": N,
            "controls_in_progress":    N,
            "controls_not_started":    N,
            "total_partial_musts":     N,
            "total_missing_musts":     N,
        },
        "sections": [
          {
            "id":          "ready_to_close" | "in_progress" | "not_started",
            "title":       display title,
            "description": tenant-facing paragraph,
            "n_total":     total controls in this bucket (may exceed shown),
            "n_shown":     controls returned with close-path prose,
            "controls": [
              {
                "control_ref":       "A.5.9",
                "standard_id":       "ISO27001:2022",
                "standard_display":  "ISO 27001:2022",
                "title":             "Inventory of information...",
                "counts": {"partial": N, "missing": N, "direct": N, "total": N},
                "yellow_items": [
                  {"state":"partial","must_id":"...","must_label":"...",
                   "close_path": "..."},
                  ...  # up to max_yellow_per_control
                ],
              },
              ...
            ]
          },
          ...
        ]
      }
    """
    from datetime import datetime, timezone

    # ── Fetch all yellow verdicts for the tenant ────────────────────
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s::text, false)",
            (tenant_id,),
        )
        # We aggregate here at the DB level for the summary counts +
        # bucket assignment. Then a targeted query pulls detail for
        # the top-K per bucket. Stub_rollup rows are excluded — the
        # Ship 59'.e discriminator prevents double-counting canonicals.
        # LEFT JOIN posture_must_bridge_coverage to detect bridge-covered
        # MUSTs — those are covered by xfw evidence, not yellow items.
        # A MUST is a yellow item only if it's partial OR (not-satisfied
        # AND not-bridged). Bridged-only MUSTs surface elsewhere (drill-in
        # attribution panel); they don't belong in the fix workload.
        cur.execute(
            """
            WITH must_state AS (
                SELECT pmv.standard_id,
                       pmv.control_ref,
                       pmv.must_id,
                       pmv.satisfied,
                       pmv.partial,
                       EXISTS(
                           SELECT 1 FROM posture_must_bridge_coverage bc
                            WHERE bc.tenant_id     = pmv.tenant_id
                              AND bc.target_must_id = pmv.must_id
                       ) AS has_bridges
                  FROM posture_must_verdicts pmv
                 WHERE pmv.tenant_id = %s::uuid
                   AND (pmv.reason IS NULL OR pmv.reason NOT LIKE 'stub_rollup:%%')
            )
            SELECT standard_id, control_ref,
                   COUNT(*) FILTER (WHERE partial)                    AS n_partial,
                   COUNT(*) FILTER (WHERE NOT satisfied
                                     AND NOT partial
                                     AND NOT has_bridges)             AS n_missing,
                   COUNT(*) FILTER (WHERE satisfied)                  AS n_direct,
                   COUNT(*)                                           AS n_total
              FROM must_state
             GROUP BY standard_id, control_ref
            HAVING COUNT(*) FILTER (WHERE partial) > 0
                OR COUNT(*) FILTER (WHERE NOT satisfied
                                     AND NOT partial
                                     AND NOT has_bridges) > 0
             ORDER BY control_ref
            """,
            (tenant_id,),
        )
        rows = cur.fetchall()

    # ── Bucket assignment ───────────────────────────────────────────
    ready_to_close: list[dict] = []
    in_progress:    list[dict] = []
    not_started:    list[dict] = []
    total_partial_musts = 0
    total_missing_musts = 0

    for standard_id, control_ref, n_partial, n_missing, n_direct, n_total in rows:
        entry = {
            "standard_id":  standard_id,
            "control_ref":  control_ref,
            "counts": {
                "partial": int(n_partial),
                "missing": int(n_missing),
                "direct":  int(n_direct),
                "total":   int(n_total),
            },
        }
        total_partial_musts += int(n_partial)
        total_missing_musts += int(n_missing)
        if n_partial > 0:
            ready_to_close.append(entry)
        elif n_direct > 0:
            in_progress.append(entry)
        else:
            not_started.append(entry)

    # Sort within each bucket: (n_partial DESC, n_direct DESC, control_ref ASC)
    def _sort_key(e: dict):
        return (
            -e["counts"]["partial"],
            -e["counts"]["direct"],
            e["control_ref"],
        )
    ready_to_close.sort(key=_sort_key)
    in_progress.sort(key=_sort_key)
    not_started.sort(key=_sort_key)

    # ── Enrich top-K per bucket with title + top-N yellow items ─────
    top_ready = ready_to_close[:k_per_bucket]
    top_prog  = in_progress[:k_per_bucket]
    top_ns    = not_started[:k_per_bucket]
    all_top   = top_ready + top_prog + top_ns

    # Batch title resolve
    title_by_key = _resolve_control_titles(
        neo4j_driver,
        [(e["standard_id"], e["control_ref"]) for e in all_top],
    )

    # For each top control, pull yellow verdicts + close-path prose
    from rag.posture.must_verdicts import read_must_verdicts_by_control

    def _enrich(entry: dict) -> dict:
        sid = entry["standard_id"]
        ref = entry["control_ref"]
        entry["standard_display"] = _humanize_standard_id(sid)
        entry["title"] = title_by_key.get((sid, ref), "")
        verdicts = read_must_verdicts_by_control(pg_conn, tenant_id, ref, sid)
        # Prioritize partials first, then missing
        partial_v = [v for v in verdicts.values() if v.state == "partial"]
        missing_v = [
            v for v in verdicts.values()
            if not v.satisfied and not v.partial and not v.bridge_sources
        ]
        # Sort within each by must_id for stable output
        partial_v.sort(key=lambda v: v.must_id)
        missing_v.sort(key=lambda v: v.must_id)
        selected = (partial_v + missing_v)[:max_yellow_per_control]
        items: list[dict] = []
        for v in selected:
            items.append({
                "state":      v.state,
                "must_id":    v.must_id,
                "must_label": _humanize_must_label(v.must_id),
                "close_path": _close_path_prose(pg_conn, tenant_id, v),
            })
        entry["yellow_items"] = items
        return entry

    top_ready_enriched = [_enrich(e) for e in top_ready]
    top_prog_enriched  = [_enrich(e) for e in top_prog]
    top_ns_enriched    = [_enrich(e) for e in top_ns]

    sections = [
        {
            "id":          "ready_to_close",
            "title":       "Ready to close",
            "description": (
                "These controls have partial evidence — the pieces "
                "you already have surfaced a specific gap. Adding "
                "one column or uploading one document typically "
                "moves each to full coverage."
            ),
            "n_total":  len(ready_to_close),
            "n_shown":  len(top_ready_enriched),
            "controls": top_ready_enriched,
        },
        {
            "id":          "in_progress",
            "title":       "In progress",
            "description": (
                "These controls have some direct evidence on file "
                "but still have required elements without coverage. "
                "Each yellow item shows the specific close path."
            ),
            "n_total":  len(in_progress),
            "n_shown":  len(top_prog_enriched),
            "controls": top_prog_enriched,
        },
        {
            "id":          "not_started",
            "title":       "Not started",
            "description": (
                "These controls have no evidence on file yet. "
                "Each yellow item shows how to add the first piece."
            ),
            "n_total":  len(not_started),
            "n_shown":  len(top_ns_enriched),
            "controls": top_ns_enriched,
        },
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "controls_ready_to_close": len(ready_to_close),
            "controls_in_progress":    len(in_progress),
            "controls_not_started":    len(not_started),
            "total_partial_musts":     total_partial_musts,
            "total_missing_musts":     total_missing_musts,
        },
        "sections": sections,
    }
