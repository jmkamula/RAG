"""
ArionComply — Evidence Package generator

For a satisfied (or partially-satisfied) leaf, produce an auditor-
ready markdown summary that reads naturally to a tenant:

  Opening — natural-language "what this is about" from ISO 27002
    business_description (or GDPR-equivalent).
  Artifact framing — EvidenceRequirement.description explaining what
    THIS particular artifact is + how it fits the family.
  Coverage:
      ✓ Required elements — each satisfied element with verbatim
        source excerpt + document reference
      ✗ Required elements missing — element name + hint
      ◐ Recommended additions — same shape, softer language
  Auditor reference — verbatim standard obligation quote at the foot.

Design principles (per 2026-07-01 rewrite):
  * Every claim grounded in a source document; excerpts are verbatim
  * Zero system jargon in the user-facing surface:
    no `item:` ids, no `req:` leaf ids, no `MUST/SHOULD`, no `leaf`,
    no snake_case slugs, standard names spaced ("ISO 27001:2022")
  * Reuse existing curated fields — business_description on
    RequirementNode + description on EvidenceRequirement — rather
    than hand-writing per-node display text (scales to n frameworks)
  * `[leaf-scan back-bind from finding <uuid>]` admin-trace prefix
    scrubbed from excerpts before display
  * confidence tag only surfaced when it's below 'high' (noise
    reduction — the common case is silent)
"""
from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ── De-jargonizer helpers ─────────────────────────────────────────────

_LEAF_SCAN_PREFIX = re.compile(r"^\s*\[leaf-scan back-bind from finding [0-9a-f]{6,}\]\s*")


def _humanize_standard_id(standard_id: str) -> str:
    """'ISO27001:2022' -> 'ISO 27001:2022' / 'GDPR:2016/679' -> 'GDPR'."""
    if standard_id.startswith("ISO27001:"):
        return f"ISO 27001:{standard_id.split(':', 1)[1]}"
    if standard_id.startswith("ISO27701:"):
        return f"ISO 27701:{standard_id.split(':', 1)[1]}"
    if standard_id.startswith("GDPR:"):
        return "GDPR"
    if ":" in standard_id:
        head, rest = standard_id.split(":", 1)
        return f"{head} {rest}"
    return standard_id


def _humanize_evidence_type(evidence_type: str) -> str:
    """snake_case -> Title Case ('communication_record' -> 'Communication Record')."""
    if not evidence_type:
        return ""
    return " ".join(w.capitalize() for w in evidence_type.replace("_", " ").split())


def _clean_excerpt(text: str) -> str:
    """Strip admin-trace prefix + collapse whitespace."""
    if not text:
        return ""
    return _LEAF_SCAN_PREFIX.sub("", text).strip()


def _find_leaf(leaf_id: str):
    """Look up an EvidenceRequirement by id across the canonical catalog."""
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
    """Pull title + obligation_text + business_description for the
    control node. Best-effort — degrades gracefully to empty strings."""
    out = {"title": "", "obligation_text": "", "business_description": ""}
    if neo4j_driver is None:
        return out
    cid = f"{standard_id}:{control_ref}"
    try:
        with neo4j_driver.session() as s:
            row = s.run(
                "MATCH (n) WHERE n.id = $id "
                "RETURN n.title AS title, "
                "       coalesce(n.obligation_text, '') AS obligation_text, "
                "       coalesce(n.business_description, '') AS business_description "
                "LIMIT 1",
                id=cid,
            ).single()
            if row:
                out["title"]                = row["title"] or ""
                out["obligation_text"]      = row["obligation_text"] or ""
                out["business_description"] = row["business_description"] or ""
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

    # ── Gather findings per element ──────────────────────────────
    must_items    = list(leaf.must_contain)
    should_items  = list(leaf.should_contain)
    must_ids      = [ci.id for ci in must_items]
    should_ids    = [ci.id for ci in should_items]
    all_ids       = must_ids + should_ids

    findings_by_element: dict[str, list[dict]] = {mid: [] for mid in all_ids}
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
                if mid in findings_by_element:
                    findings_by_element[mid].append({
                        "excerpt":     _clean_excerpt(excerpt),
                        "confidence":  conf,
                        "section":     sec_no,
                        "filename":    fname,
                    })

    # ── Canonical control fields from Neo4j ───────────────────────
    from rag.posture_loader import _build_engine_neo4j_driver
    neo = _build_engine_neo4j_driver()
    try:
        canon = _resolve_control_summary(neo, leaf.standard_id, leaf.control_ref)
    finally:
        if neo is not None:
            try: neo.close()
            except Exception: pass

    # ── Coverage math ─────────────────────────────────────────────
    n_must_total     = len(must_ids)
    n_must_satisfied = sum(1 for mid in must_ids if findings_by_element.get(mid))
    n_should_total   = len(should_ids)
    n_should_covered = sum(1 for sid in should_ids if findings_by_element.get(sid))
    coverage_pct     = 100 if n_must_total == 0 else round(100 * n_must_satisfied / n_must_total)

    now       = datetime.now(timezone.utc)
    std_human = _humanize_standard_id(leaf.standard_id)

    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────
    header_title = leaf.title or (canon.get("title") or leaf.control_ref)
    lines.append(f"# {header_title} — Coverage Summary")
    lines.append("")
    lines.append(f"_{leaf.control_ref} · {std_human} · "
                 f"Generated {now.strftime('%Y-%m-%d')}_")
    lines.append("")

    # ── Coverage at-a-glance ──────────────────────────────────────
    if n_must_total:
        state = ("Fully covered" if coverage_pct == 100
                 else "Partially covered" if coverage_pct > 0
                 else "Not yet covered")
        lines.append(f"**Status:** {state} — {n_must_satisfied} of "
                     f"{n_must_total} required element"
                     f"{'s' if n_must_total != 1 else ''}"
                     f" covered ({coverage_pct}%).")
        if n_should_total:
            lines.append(f"**Recommended additions:** "
                         f"{n_should_covered} of {n_should_total} covered.")
        lines.append("")

    # ── What this is about — control-level natural language ──────
    if canon.get("business_description"):
        lines.append("## What this is about")
        lines.append("")
        lines.append(canon["business_description"])
        lines.append("")

    # ── This particular artifact — leaf-level natural language ───
    if leaf.description:
        lines.append("## This particular artifact")
        lines.append("")
        lines.append(leaf.description)
        lines.append("")

    # ── Required elements ────────────────────────────────────────
    lines.append(f"## Required elements — {n_must_satisfied} of {n_must_total} covered")
    lines.append("")
    for ci in must_items:
        rows = findings_by_element.get(ci.id, [])
        if rows:
            lines.append(f"- ✓ **{ci.text}**")
            for r in rows:
                loc = r["filename"]
                if r.get("section"):
                    loc += f", §{r['section']}"
                conf_tag = ""
                if r.get("confidence") and r["confidence"].lower() != "high":
                    conf_tag = f" _(confidence: {r['confidence']})_"
                excerpt = (r["excerpt"] or "")
                lines.append(f"  > {excerpt}")
                lines.append(f"  From _{loc}_{conf_tag}")
                lines.append("")
        else:
            lines.append(f"- ✗ **{ci.text}**")
            lines.append(f"  No evidence yet. Add or upload a source that "
                         f"addresses this element.")
            lines.append("")

    # ── Recommended additions ────────────────────────────────────
    if should_ids:
        lines.append(f"## Recommended additions — {n_should_covered} of "
                     f"{n_should_total} covered")
        lines.append("")
        for ci in should_items:
            rows = findings_by_element.get(ci.id, [])
            if rows:
                lines.append(f"- ✓ **{ci.text}**")
                for r in rows:
                    loc = r["filename"]
                    if r.get("section"):
                        loc += f", §{r['section']}"
                    lines.append(f"  > {r['excerpt']}")
                    lines.append(f"  From _{loc}_")
                    lines.append("")
            else:
                lines.append(f"- ○ {ci.text}")

        lines.append("")

    # ── Auditor reference — verbatim standard quote at the foot ──
    if canon.get("obligation_text"):
        lines.append("---")
        lines.append("")
        lines.append("### For auditors — verbatim standard reference")
        lines.append("")
        lines.append(f"_{std_human} §{leaf.control_ref}_ — {canon['obligation_text']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Auto-generated by ArionComply. Excerpts are verbatim "
                 "quotes from your source documents. Refreshed on every "
                 "download._")
    lines.append("")

    return "\n".join(lines)
