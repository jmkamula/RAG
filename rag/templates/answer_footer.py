"""
rag/templates/answer_footer.py — append a deterministic
"Templates available" footer to chat answers.

Mirrors the cross-framework bridge footer pattern (see
[[cross-framework-bridge-footer-2026-06-14]]): when the LLM has
freedom over structural data it's stochastic; surface deterministically.

A template footer is appended when:
  - The query intent is action-oriented (implementation /
    gap_analysis / posture_check / document_inventory /
    document_content)
  - The answer cites at least one control_ref that has a template
    in the templates table

Footer shape (one line per cited control):

    ↳ Templates available:
      - A.5.15 Access Control Policy → /api/v1/templates/req:A.5.15:access_control_policy/download
      - A.5.18 Access Rights Procedure → /api/v1/templates/req:A.5.18:access_rights_procedure/download

Per-control "primary" template: prefer hand-refined v2 anchor;
fall back to the first v1 leaf alphabetically. Tenants can find
sibling-leaf templates via the wizard or by exploring the URL
prefix.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Optional


logger = logging.getLogger(__name__)


# Question types where a template footer makes sense. Definitional
# answers ("what is X") and pure cross-framework lookups don't need
# one (CROSS_FRAMEWORK already has the bridge footer).
_RELEVANT_QUESTION_TYPES = {
    "implementation",
    "gap_analysis",
    "posture_check",
    "document_inventory",
    "document_content",
}


def build_template_footer(
    cited_refs:    list[str],
    question_type: Optional[str],
    *,
    pg_conn = None,
    db_url:  Optional[str] = None,
) -> str:
    """Return a "↳ Templates available: ..." footer, or empty string.

    Either `pg_conn` (open connection — caller manages lifecycle) or
    `db_url` (helper opens + closes ephemerally) must be supplied.
    Returns "" silently on any DB failure so the answer is never
    broken by a templates lookup error.
    """
    if not cited_refs:
        return ""
    qt = (question_type or "").lower()
    if qt and qt not in _RELEVANT_QUESTION_TYPES:
        return ""

    # Dedup + canonicalise the refs
    refs = sorted({r.strip() for r in cited_refs if r and r.strip()})
    if not refs:
        return ""

    own_conn = False
    if pg_conn is None:
        if not db_url:
            db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return ""
        try:
            import psycopg2
            pg_conn = psycopg2.connect(db_url)
            own_conn = True
        except Exception as e:
            logger.warning(f"template footer: pg connect failed: {e}")
            return ""

    try:
        primaries = _fetch_primary_templates(pg_conn, refs)
    except Exception as e:
        logger.warning(f"template footer: lookup failed: {e}")
        return ""
    finally:
        if own_conn:
            try:
                pg_conn.close()
            except Exception:
                pass

    if not primaries:
        return ""

    lines = ["", "↳ Templates available:"]
    for p in primaries:
        lines.append(
            f"  - {p['control_ref']} {p['title']} → {p['download_url']}"
        )
    return "\n".join(lines)


def _fetch_primary_templates(pg_conn, refs: list[str]) -> list[dict]:
    """For each control_ref in refs, return the primary template.

    Primary = highest template_version (v2 anchor preferred over v1).
    When multiple v2 anchors share a control_ref (rare), the first
    alphabetically wins. Pure auto-scaffolds (v1) tie-break the same way.
    """
    if not refs:
        return []

    # Build a regex matching any of: 'req:<ref>:...' where <ref> is one
    # of the cited refs. Escape regex specials in each ref.
    pattern = "^req:(" + "|".join(re.escape(r) for r in refs) + "):"

    with pg_conn.cursor() as cur:
        cur.execute(
            """
            SELECT leaf_id, template_version, source_file
              FROM templates
             WHERE leaf_id ~ %s
             ORDER BY template_version DESC, leaf_id ASC
            """,
            (pattern,),
        )
        rows = cur.fetchall()

    # Group by control_ref, pick the first (highest version due to ORDER BY)
    by_ref: dict[str, dict] = {}
    for leaf_id, version, source_file in rows:
        parts = leaf_id.split(":", 2)
        if len(parts) < 3:
            continue
        ref = parts[1]
        if ref in by_ref:
            continue  # already have the primary for this ref
        by_ref[ref] = {
            "control_ref":  ref,
            "leaf_id":      leaf_id,
            "template_version": version,
            "title":        _title_from_source_file(source_file),
            "download_url": f"/api/v1/templates/{leaf_id}/download",
        }

    return sorted(by_ref.values(), key=lambda d: d["control_ref"])


def _title_from_source_file(source_file: str) -> str:
    """req__A_5_15__access_control_policy.md → Access Control Policy.

    Source filenames follow the convention from
    scripts/generate_template_scaffolds.py: leaf_id with colons →
    double-underscore + dots → single-underscore + .md extension.
    Reverses for a human-readable title.
    """
    name = (source_file or "").rsplit(".", 1)[0]
    parts = name.split("__", 2)
    if len(parts) < 3:
        return name
    slug = parts[2]
    return slug.replace("_", " ").title()
