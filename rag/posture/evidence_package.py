"""
ArionComply — Evidence Package generator

For a satisfied (or partially-satisfied) leaf, produce an auditor-
ready markdown summary showing:

  - Control obligation text (from the standard)
  - Per-MUST coverage:
      ✓ satisfied  → source doc + excerpt (verbatim quote)
      ✗ missing    → remediation hint
  - Coverage stats + generation metadata

Uses existing data:
  * `document_findings` (excerpt, checklist_item_id, review_status)
  * `client_documents` (filename, section_number)
  * catalog `document_requirements.py` for the leaf's MUST/SHOULD text
  * Neo4j RequirementNode for the obligation title + text

The output is auditor-facing. Every claim is grounded in a source
document and its literal excerpt — no synthesis, no summarisation.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def _find_leaf(leaf_id: str):
    """Look up an EvidenceRequirement leaf from the catalog by id.
    Searches both ALL_EVIDENCE_REQUIREMENTS and DerivedSpec.direct_evidence.
    """
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    for er in list(ALL_EVIDENCE_REQUIREMENTS):
        if er.id == leaf_id:
            return er
    for ds in ALL_DERIVED_SPECS:
        for er in ds.direct_evidence:
            if er.id == leaf_id:
                return er
    return None


def _resolve_control_summary(neo4j_driver, standard_id: str, control_ref: str) -> dict:
    """Duplicate of api_server._resolve_control_summary to keep this
    module free of api_server imports."""
    out = {"title": "", "description": ""}
    if neo4j_driver is None:
        return out
    cid = f"{standard_id}:{control_ref}"
    try:
        with neo4j_driver.session() as s:
            row = s.run(
                "MATCH (n) WHERE n.id = $id "
                "RETURN n.title AS title, "
                "       coalesce(n.obligation_text, n.business_description, "
                "                n.description, n.body, '') AS description "
                "LIMIT 1",
                id=cid,
            ).single()
            if row:
                out["title"]       = row["title"] or ""
                out["description"] = row["description"] or ""
    except Exception as e:
        logger.warning("evidence_package: _resolve_control_summary failed: %s", e)
    return out


def build_evidence_package(pg_conn, tenant_id: str, leaf_id: str) -> Optional[str]:
    """Build the markdown evidence package for one leaf.

    Returns the markdown text, or None if the leaf isn't in the catalog.
    """
    leaf = _find_leaf(leaf_id)
    if leaf is None:
        return None

    # ── Gather findings per MUST for this leaf ────────────────────
    must_ids = [ci.id for ci in list(leaf.must_contain)]
    should_ids = [ci.id for ci in list(leaf.should_contain)]
    all_ids = must_ids + should_ids

    findings_by_must: dict[str, list[dict]] = {mid: [] for mid in all_ids}
    if all_ids:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s::text, false)", (tenant_id,),
            )
            cur.execute(
                """
                SELECT df.checklist_item_id, df.excerpt, df.confidence,
                       df.section_number, cd.filename
                  FROM document_findings df
                  JOIN client_documents cd ON cd.id = df.document_id
                 WHERE df.tenant_id = %s::uuid
                   AND df.is_active = TRUE
                   AND df.review_status = 'approved'
                   AND df.checklist_item_id = ANY(%s)
                 ORDER BY df.checklist_item_id, cd.filename
                """,
                (tenant_id, all_ids),
            )
            for mid, excerpt, conf, sec_no, fname in cur.fetchall():
                if mid in findings_by_must:
                    findings_by_must[mid].append({
                        "excerpt":     excerpt or "",
                        "confidence":  conf,
                        "section":     sec_no,
                        "filename":    fname,
                    })

    # ── Resolve the canonical control text ────────────────────────
    from rag.posture_loader import _build_engine_neo4j_driver
    canon = {"title": "", "description": ""}
    neo = _build_engine_neo4j_driver()
    try:
        canon = _resolve_control_summary(neo, leaf.standard_id, leaf.control_ref)
    finally:
        if neo is not None:
            try: neo.close()
            except Exception: pass

    # ── Render ────────────────────────────────────────────────────
    n_must_total     = len(must_ids)
    n_must_satisfied = sum(1 for mid in must_ids if findings_by_must.get(mid))
    n_should_total   = len(should_ids)
    n_should_covered = sum(1 for sid in should_ids if findings_by_must.get(sid))

    coverage_pct = 100 if n_must_total == 0 else round(100 * n_must_satisfied / n_must_total)

    now = datetime.now(timezone.utc)
    lines: list[str] = []
    lines.append(f"# Evidence Package — {leaf.control_ref}: {leaf.title}")
    lines.append("")
    lines.append(f"_Generated {now.strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")
    lines.append(f"- **Standard:** {leaf.standard_id}")
    lines.append(f"- **Control:** {leaf.control_ref}")
    lines.append(f"- **Leaf:** `{leaf.id}`")
    lines.append(f"- **Evidence type:** {leaf.evidence_type}")
    lines.append(f"- **MUST coverage:** {n_must_satisfied}/{n_must_total} ({coverage_pct}%)")
    if n_should_total:
        lines.append(f"- **SHOULD coverage:** {n_should_covered}/{n_should_total}")
    lines.append("")

    if canon.get("title") or canon.get("description"):
        lines.append("## Standard obligation")
        lines.append("")
        if canon["title"]:
            lines.append(f"**{canon['title']}** — {canon['description']}" if canon["description"]
                         else f"**{canon['title']}**")
        else:
            lines.append(canon["description"])
        lines.append("")

    # MUST coverage
    lines.append("## MUST coverage")
    lines.append("")
    for ci in list(leaf.must_contain):
        rows = findings_by_must.get(ci.id, [])
        if rows:
            lines.append(f"### ✓ `{ci.id}` — {ci.text}")
            lines.append("")
            for r in rows:
                loc = f"{r['filename']}"
                if r.get("section"):
                    loc += f", §{r['section']}"
                lines.append(f"> {(r['excerpt'] or '').strip()}")
                lines.append("")
                lines.append(f"*Source: {loc}*"
                             + (f" · confidence: {r['confidence']}" if r.get("confidence") else ""))
                lines.append("")
        else:
            lines.append(f"### ✗ `{ci.id}` — {ci.text}")
            lines.append("")
            rationale = getattr(ci, "rationale", "") or ""
            if rationale:
                lines.append(f"_Rationale:_ {rationale}")
                lines.append("")
            lines.append("_No approved finding yet. Author or upload evidence satisfying this element._")
            lines.append("")

    # SHOULD coverage (optional section, only when there are SHOULDs)
    if should_ids:
        lines.append("## SHOULD coverage")
        lines.append("")
        for ci in list(leaf.should_contain):
            rows = findings_by_must.get(ci.id, [])
            marker = "✓" if rows else "○"  # open circle for uncovered SHOULD
            lines.append(f"### {marker} `{ci.id}` — {ci.text}")
            lines.append("")
            for r in rows:
                loc = f"{r['filename']}"
                if r.get("section"):
                    loc += f", §{r['section']}"
                lines.append(f"> {(r['excerpt'] or '').strip()}")
                lines.append("")
                lines.append(f"*Source: {loc}*")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_This package is auto-generated from ArionComply's document_findings "
                 "table and refreshed on every download. Excerpts are verbatim quotes from "
                 "the tenant's source documents; the standard obligation text is sourced from "
                 "the canonical standard._")

    return "\n".join(lines)
