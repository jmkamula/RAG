"""Per-control / per-leaf document generation from form-authored evidence.

Reads form-authored document_findings rows (inference_source='form'),
joins with Neo4j MUST descriptions, and renders a canonical document
the tenant can hand to an auditor. Markdown only for MVP — .docx can
ride later.

Document shape (per leaf):

  # Template: A.5.15 :: access_control_policy
  Evidence type: policy
  Updated: 2026-06-15

  ## Section 1: Principle of need-to-know stated
  <tenant's text>

  ## Section 2: Authorisation rules
  <tenant's text>

  ...

  ---
  Source: ISO/IEC 27002:2022 §5.15 implementation guidance.

When `leaf_id` is omitted, generates a combined document with one
section per leaf (each leaf becomes a top-level heading, MUSTs become
subheadings).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_DRIVER = None


def _get_neo_driver():
    global _DRIVER
    if _DRIVER is not None:
        return _DRIVER
    try:
        from neo4j import GraphDatabase
        uri  = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        pw   = os.getenv("NEO4J_PASSWORD")
        if not (uri and user and pw):
            return None
        _DRIVER = GraphDatabase.driver(uri, auth=(user, pw))
        return _DRIVER
    except Exception as e:
        logger.warning("template_document: neo4j driver creation failed: %s", e)
        return None


def _source_label(control_ref: str, standard_id: str) -> str:
    if standard_id.startswith("ISO27001"):
        if control_ref and control_ref.startswith("A."):
            return f"Source: ISO/IEC 27002:2022 §{control_ref[2:]} implementation guidance."
        return f"Source: ISO/IEC 27001:2022 clause {control_ref}."
    if standard_id.startswith("GDPR"):
        return f"Source: GDPR {control_ref} (EU Regulation 2016/679) + EDPB guidance."
    return f"Source: {standard_id} {control_ref}."


def _fetch_leaf_meta(neo, leaf_id: str) -> dict:
    """Fetch evidence_type + leaf label + ordered MUST items for one leaf."""
    with neo.session() as s:
        r = s.run("""
            MATCH (er:EvidenceRequirement {id: $leaf_id})
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(ci:ChecklistItem)
            RETURN er.evidence_type AS et,
                   collect({id: ci.id, text: ci.text}) AS items
        """, leaf_id=leaf_id).single()
        if not r:
            return {"evidence_type": "", "items": []}
        items = [it for it in (r["items"] or []) if it and it.get("id")]
        return {
            "evidence_type": r["et"] or "",
            "items":         items,
        }


def _fetch_leaves_for_control(neo, control_ref: str, standard_id: str) -> list[dict]:
    """All leaves for a control + their MUSTs + evidence_type."""
    full_id_prefix = "req:" + control_ref + ":"
    with neo.session() as s:
        r = s.run("""
            MATCH (er:EvidenceRequirement)
            WHERE er.id STARTS WITH $prefix
            OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(ci:ChecklistItem)
            RETURN er.id AS leaf_id, er.evidence_type AS et,
                   collect({id: ci.id, text: ci.text}) AS items
            ORDER BY er.id
        """, prefix=full_id_prefix).data()
    return [
        {
            "leaf_id":       row["leaf_id"],
            "evidence_type": row["et"] or "",
            "items":         [it for it in (row["items"] or []) if it and it.get("id")],
        }
        for row in r
    ]


def _fetch_form_text(pg_conn, tenant_id: str, control_ref: str,
                    standard_id: str) -> dict[str, str]:
    """Returns {checklist_item_id: text} for all form-authored evidence
    on this control."""
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
        )
        cur.execute("""
            SELECT checklist_item_id, excerpt
              FROM document_findings
             WHERE tenant_id         = %s::uuid
               AND control_ref       = %s
               AND standard_id       = %s
               AND inference_source  = 'form'
               AND is_active         = TRUE
               AND checklist_item_id IS NOT NULL
        """, (tenant_id, control_ref, standard_id))
        rows = cur.fetchall()
    return {r[0]: (r[1] or "") for r in rows}


def _humanize(s: str) -> str:
    return (s or "").replace("_", " ")


def build_template_document(
    pg_conn,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
    leaf_id:     Optional[str] = None,
    neo4j_driver = None,
) -> Optional[dict]:
    """Generate a template document for a control or one leaf.

    Returns dict {filename, mime_type, content} or None if nothing to
    render (no MUSTs found / no neo4j).

    The MUST headings come from Neo4j ChecklistItem.text; the body text
    per MUST comes from form-authored document_findings rows (or
    placeholder "(not yet filled in)" when empty).
    """
    if not control_ref:
        return None

    if neo4j_driver is None:
        neo4j_driver = _get_neo_driver()
        if neo4j_driver is None:
            return None

    form_text = _fetch_form_text(pg_conn, tenant_id, control_ref, standard_id)

    if leaf_id:
        leaves = [_fetch_leaf_meta(neo4j_driver, leaf_id) | {"leaf_id": leaf_id}]
    else:
        leaves = _fetch_leaves_for_control(neo4j_driver, control_ref, standard_id)

    leaves = [l for l in leaves if l.get("items")]
    if not leaves:
        return None

    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    title_suffix = (
        " :: " + leaves[0]["leaf_id"].split(":")[-1] if leaf_id else ""
    )
    out_lines: list[str] = [
        f"# Template: {control_ref}{title_suffix}",
        "",
        f"_Generated {today} from per-MUST tenant input._",
        "",
    ]

    for leaf in leaves:
        leaf_short = leaf["leaf_id"].split(":")[-1]
        et_label   = _humanize(leaf["evidence_type"])
        if not leaf_id:
            # Multi-leaf document: leaf becomes top-level section
            out_lines.append(f"## {_humanize(leaf_short)} ({et_label})")
            out_lines.append("")
        else:
            out_lines.append(f"_Evidence type: {et_label}_")
            out_lines.append("")

        for idx, must in enumerate(leaf["items"], start=1):
            must_id   = must["id"]
            must_text = must["text"] or ""
            body      = form_text.get(must_id, "").strip()

            heading = (
                f"### {idx}. {must_text}"
                if not leaf_id else f"## {idx}. {must_text}"
            )
            out_lines.append(heading)
            out_lines.append("")
            if body:
                out_lines.append(body)
            else:
                out_lines.append("> _(not yet filled in)_")
            out_lines.append("")

    out_lines.append("---")
    out_lines.append(_source_label(control_ref, standard_id))

    body_md = "\n".join(out_lines).rstrip() + "\n"

    leaf_part = (
        "_" + leaves[0]["leaf_id"].split(":")[-1] if leaf_id else ""
    )
    filename = f"template_{control_ref.replace('.', '_')}{leaf_part}.md"

    return {
        "filename":  filename,
        "mime_type": "text/markdown; charset=utf-8",
        "content":   body_md,
    }
