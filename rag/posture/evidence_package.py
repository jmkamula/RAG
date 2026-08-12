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

    Ship 61'.a (2026-08-12) — hybrid SSoT + raw-findings design:
      * Coverage counts + per-element state come from
        `posture_must_verdicts` (Ship 58'/59' SSoT). This respects the
        engine's discipline: N/A-excluded MUSTs are filtered out of
        totals, stale evidence is categorised, freshness rules apply.
      * Verbatim excerpts still come from `document_findings` — the
        auditor needs the text as it appears in the tenant's source.
      * Cross-framework bridge attribution surfaces per element when
        the tenant's related-framework evidence covers the MUST
        (matches the SPA nudge / chat markdown / digest suffix from
        Ship 60'.g/h/i/j).
      * SSoT-empty fallback: if no verdicts exist for the control
        (fresh tenant / sweep lag), degrade to the pre-Ship-61'.a
        "count elements with ≥1 approved finding" heuristic.
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

    # ── SSoT read for per-MUST verdicts + bridge attribution ─────
    # Ship 61'.a — same reader the advisory + breakdown surfaces use.
    # Silent on empty (schema not applied, fresh tenant, etc.) — the
    # fallback path below uses the legacy findings-only counting.
    from rag.posture.must_verdicts import read_must_verdicts_by_control
    ssot_verdicts = read_must_verdicts_by_control(
        pg_conn, tenant_id, leaf.control_ref, leaf.standard_id,
    )

    # ── Canonical control fields from Neo4j ───────────────────────
    from rag.posture_loader import _build_engine_neo4j_driver
    neo = _build_engine_neo4j_driver()
    try:
        canon = _resolve_control_summary(neo, leaf.standard_id, leaf.control_ref)
    finally:
        if neo is not None:
            try: neo.close()
            except Exception: pass

    # ── Coverage math (hybrid SSoT + findings fallback) ───────────
    # Two counting modes, chosen per-MUST:
    #   SSoT mode  — MUST id is in ssot_verdicts. Categorise as
    #     "direct" (verdict.satisfied), "bridged" (not-satisfied but
    #     bridge_sources non-empty), or "missing".
    #   fallback   — MUST id is NOT in SSoT (either N/A-excluded OR
    #     SSoT unpopulated). If ssot_verdicts is empty overall,
    #     that's the unpopulated case: count via presence of ≥1
    #     approved finding. If ssot_verdicts is non-empty but this
    #     specific MUST is absent, that's N/A-excluded and the MUST
    #     drops from the total (respects tenant scope).
    #
    # `applicable_must_ids` is the effective per-leaf MUST set for
    # this tenant. Empty ssot ⇒ all catalog MUSTs applicable (fallback).
    ssot_empty = not ssot_verdicts
    if ssot_empty:
        applicable_must_ids = list(must_ids)
    else:
        applicable_must_ids = [mid for mid in must_ids if mid in ssot_verdicts]

    n_must_total     = len(applicable_must_ids)
    n_must_satisfied = 0   # direct-satisfied per SSoT (or findings fallback)
    n_must_bridged   = 0   # unmet-direct but cross-framework attribution present

    def _must_state(mid: str) -> str:
        """Return one of 'direct' / 'bridged' / 'missing' for this MUST."""
        if ssot_empty:
            return "direct" if findings_by_element.get(mid) else "missing"
        v = ssot_verdicts.get(mid)
        if v is None:
            return "missing"  # shouldn't hit due to applicable_must_ids filter
        if v.satisfied:
            return "direct"
        if v.bridge_sources:
            return "bridged"
        return "missing"

    for mid in applicable_must_ids:
        st = _must_state(mid)
        if st == "direct":
            n_must_satisfied += 1
        elif st == "bridged":
            n_must_bridged += 1

    n_should_total   = len(should_ids)
    n_should_covered = sum(1 for sid in should_ids if findings_by_element.get(sid))
    # Coverage % uses direct satisfaction (auditor-strict); bridged
    # elements are surfaced separately in the header so the tenant
    # sees the honest split.
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
        # Ship 61'.a — cross-framework attribution surfaced at the
        # top so auditors see the picture before scanning per-element
        # detail. Silent when zero.
        if n_must_bridged:
            noun = "element is" if n_must_bridged == 1 else "elements are"
            # Roll up unique source standards across all unmet-bridged
            # MUSTs — same shape as the SPA/chat/digest nudge.
            _bridge_stds: set[str] = set()
            for mid in applicable_must_ids:
                v = ssot_verdicts.get(mid) if not ssot_empty else None
                if v is None or v.satisfied or not v.bridge_sources:
                    continue
                for b in v.bridge_sources:
                    if b.source_standard_id:
                        _bridge_stds.add(_humanize_standard_id(b.source_standard_id))
            if _bridge_stds:
                std_list = ", ".join(sorted(_bridge_stds))
                lines.append(
                    f"**Cross-framework coverage:** {n_must_bridged} "
                    f"{noun} covered by evidence for related "
                    f"{std_list} controls (see below)."
                )
        if n_should_total:
            lines.append(f"**Recommended additions:** "
                         f"{n_should_covered} of {n_should_total} covered.")
        lines.append("")

    # Ship 7'.c — Evidence Package prose is auditor-facing. Route
    # curator-authored fields through the output gateway so any
    # leaf-id / snake_case / raw standard-id leakage in
    # `business_description` / leaf `.description` is scrubbed
    # before it reaches the auditor.
    from rag.output import humanize as _humanize

    # ── What this is about — control-level natural language ──────
    if canon.get("business_description"):
        lines.append("## What this is about")
        lines.append("")
        lines.append(_humanize(canon["business_description"], surface="evidence_prose"))
        lines.append("")

    # ── This particular artifact — leaf-level natural language ───
    if leaf.description:
        lines.append("## This particular artifact")
        lines.append("")
        lines.append(_humanize(leaf.description, surface="evidence_prose"))
        lines.append("")

    # ── Required elements ────────────────────────────────────────
    lines.append(f"## Required elements — {n_must_satisfied} of {n_must_total} covered")
    lines.append("")
    for ci in must_items:
        # Ship 61'.a — filter N/A-excluded MUSTs from the rendered
        # list. SSoT drops them; Evidence Package shouldn't ask the
        # auditor to check something outside the tenant's scope.
        if not ssot_empty and ci.id not in ssot_verdicts:
            continue

        rows = findings_by_element.get(ci.id, [])
        st   = _must_state(ci.id)

        if st == "direct":
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
            if not rows:
                # SSoT says satisfied but no excerpts in doc_findings
                # (e.g. cite-mode leaf, or a source that hasn't been
                # excerpted). Note the coverage without a quote block.
                lines.append(f"  Coverage recorded — no verbatim excerpt available.")
                lines.append("")
        elif st == "bridged":
            # Ship 61'.a — unmet-direct but covered via cross-framework
            # bridge attribution. Auditor gets the deterministic
            # source-control ref + edge type without prose invention.
            v = ssot_verdicts[ci.id]
            lines.append(f"- ↗ **{ci.text}** (cross-framework coverage)")
            # Group source refs by (standard_id, control_ref, edge_type)
            # to avoid repeating identical bridges — e.g. many source
            # MUSTs on the same source control produce one "via A.5.15"
            # line, not one line per source MUST.
            grouped: dict[tuple[str, str, str], int] = {}
            for b in v.bridge_sources:
                key = (b.source_standard_id, b.source_control_ref, b.edge_type)
                grouped[key] = grouped.get(key, 0) + 1
            # Cap the display to the top 3 groups — auditors can
            # drill in from the SPA if they need the full attribution
            # graph; the package shouldn't sprawl.
            top_groups = sorted(
                grouped.items(), key=lambda kv: -kv[1],
            )[:3]
            for (std_id, src_ref, edge), n in top_groups:
                std_disp = _humanize_standard_id(std_id)
                lines.append(
                    f"  ↳ Covered via _{std_disp} {src_ref}_ ({edge})"
                )
            more = len(grouped) - len(top_groups)
            if more > 0:
                lines.append(f"  ↳ …and {more} more related control{'s' if more != 1 else ''}.")
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
