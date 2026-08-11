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
    # document_inventory intentionally excluded (Ship 51'.a). For broad
    # doc-inventory queries ("what documents do we have"), the LLM
    # enumerates missing controls as a remediation guide; _extract_refs
    # then scans that text and returns 15-20 refs; templates_block used
    # to fire N starter cards for controls that had nothing to do with
    # the user's document question. document_content stays because
    # asking what a specific document should contain (e.g. "what should
    # our access policy include?") is a legitimate template-download
    # surface. Broad remediation-guide UX belongs in the Get Started
    # mode + dashboard drill-in, not stapled to chat doc answers.
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
    from rag.id_types import leaf_control_ref
    by_ref: dict[str, dict] = {}
    for leaf_id, version, source_file in rows:
        ref = leaf_control_ref(leaf_id)
        if not ref:
            continue
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


# ─── Tier-4 structured templates block ────────────────────────────────────
# Structured payload replacing the plain-text footer for the chat UI.
# Renders per-leaf as a compact card: progress-aware line + primary
# download in the right format for the leaf shape + cite-mode
# secondary CTA where applicable + dashboard drill-in link.
# See docs/memory/dejargonize_ux_pass_2026_07_01.md for the design
# arc that led here.

# Mirror of scripts/generate_template_scaffolds._TABULAR_EVIDENCE_*
# Duplicated to keep this module load-cheap; keep in sync.
_TABULAR_EVIDENCE_SUFFIXES = ("_register", "_record", "_matrix", "_log", "_inventory")
_TABULAR_EVIDENCE_EXACT = {
    "register", "statement_of_applicability", "records_of_processing",
    "review_record", "responsibility_matrix", "segregation_matrix",
    "communication_record", "monitoring_record", "test_log",
    "data_flow_inventory", "lawful_basis_register", "revocation_record",
    "approval_record", "audit_record", "configuration_record",
    "publication_record", "change_record", "discovery_record",
    "risk_assessment_record", "risk_treatment_record", "decision_record",
    "contact_register", "asset_register",
}


def _is_tabular(evidence_type: str) -> bool:
    if not evidence_type:
        return False
    if evidence_type in _TABULAR_EVIDENCE_EXACT:
        return True
    return any(evidence_type.endswith(s) for s in _TABULAR_EVIDENCE_SUFFIXES)


def _formats_for(leaf_id: str, evidence_type: str) -> tuple[dict, list[dict]]:
    """Return (primary_download, alt_downloads) for a leaf.

    Tabular leaves (register/record/matrix/log/inventory) get .xlsx
    as primary + .md alt. Narrative leaves get .docx as primary +
    .md alt. .md is always available as an alt because it's the
    canonical round-trip format.
    """
    base = f"/api/v1/templates/{leaf_id}/download"
    if _is_tabular(evidence_type):
        primary = {"format": "xlsx", "label": "Excel starter",
                   "url": f"{base}?format=xlsx"}
        alt     = [{"format": "md", "label": "Markdown",
                    "url": f"{base}?format=md"}]
    else:
        primary = {"format": "docx", "label": "Word starter",
                   "url": f"{base}?format=docx"}
        alt     = [{"format": "md", "label": "Markdown",
                    "url": f"{base}?format=md"}]
    return primary, alt


def _fetch_finding_by_ref(pg_conn, tenant_id: str, refs: list[str]) -> dict[str, str]:
    """Return {control_ref → finding} for the tenant's posture on the
    supplied refs. Only NC/OFI shape rows returned; Comply/N/A/None
    filtered out."""
    if not refs:
        return {}
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
        )
        cur.execute(
            """
            SELECT control_ref, finding
              FROM posture_controls
             WHERE tenant_id   = %s::uuid
               AND is_active   = TRUE
               AND control_ref = ANY(%s)
               AND finding    IN ('NC', 'OFI')
            """,
            (tenant_id, refs),
        )
        return {ref: finding for ref, finding in cur.fetchall()}


def _fetch_leaf_progress(pg_conn, tenant_id: str, leaf_ids: list[str]) -> dict[str, dict]:
    """Return {leaf_id → {bound, total, remaining}} — count of
    per-MUST checklist items that have at least one active+approved
    finding vs total MUST items on that leaf. Sourced from the
    document_findings + catalog union."""
    if not leaf_ids:
        return {}

    # Get total MUST count per leaf from the catalog.
    try:
        from enrichment.documents.document_requirements import (
            ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
        )
    except Exception:
        return {}
    all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
        er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
    ]
    leaf_musts: dict[str, list[str]] = {}
    for er in all_ers:
        if er.id in leaf_ids:
            leaf_musts[er.id] = [ci.id for ci in er.must_contain]

    if not leaf_musts:
        return {}

    # Get bound count per leaf from active+approved findings.
    # Reads posture_must_verdicts (SSoT) via the canonical reader
    # (2026-08-11). Any MUST with a row that isn't strictly 'missing'
    # counts as bound — matches the prior 'present OR partial' semantics.
    from rag.posture.must_verdicts import read_must_verdicts
    all_must_ids = [mid for musts in leaf_musts.values() for mid in musts]
    bound_by_leaf: dict[str, set[str]] = {lid: set() for lid in leaf_musts}
    verdicts = read_must_verdicts(pg_conn, tenant_id, must_ids=all_must_ids)
    bound_item_ids = {mid for mid, v in verdicts.items() if v.state != "missing"}
    for lid, musts in leaf_musts.items():
        bound_by_leaf[lid] = {m for m in musts if m in bound_item_ids}

    out: dict[str, dict] = {}
    for lid, musts in leaf_musts.items():
        total = len(musts)
        bound = len(bound_by_leaf[lid])
        out[lid] = {"bound": bound, "total": total, "remaining": total - bound}
    return out


def _cite_acceptable_types() -> set:
    """Set of evidence_types where cite-mode (external system) is an
    acceptable evidence source — imported lazily from cite_mode."""
    try:
        from rag.posture.cite_mode import _CITE_ACCEPTABLE_TYPES
        return _CITE_ACCEPTABLE_TYPES
    except Exception:
        return set()


def build_templates_block(
    cited_refs:    list[str],
    question_type: Optional[str],
    tenant_id:     str,
    *,
    pg_conn = None,
    db_url:  Optional[str] = None,
) -> Optional[dict]:
    """Structured Tier-4 templates block for the chat answer footer.

    Contextual mode only (starter-kit lives in the dedicated
    "Get Started" mode, not in chat). For each cited ref where the
    tenant's posture is NC or OFI:

      - Primary + alt downloads in the right format for the leaf shape
      - Progress: N of M required elements filled in
      - Cite-mode secondary CTA when the leaf's evidence_type is
        cite-acceptable
      - Drill-in link to the dashboard

    Also emits a `starter_nudge` when the tenant is fresh (Phase 0 /
    Foundation-with-zero-anchors) so the chat gently points at the
    Get Started mode.

    Returns None when nothing to show (query not action-oriented, or
    no NC/OFI cited refs, or no tenant_id / db).
    """
    qt = (question_type or "").lower()
    if qt and qt not in _RELEVANT_QUESTION_TYPES:
        return None

    refs = sorted({r.strip() for r in (cited_refs or []) if r and r.strip()})
    if not refs and not tenant_id:
        return None

    own_conn = False
    if pg_conn is None:
        if not db_url:
            db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return None
        try:
            import psycopg2
            pg_conn = psycopg2.connect(db_url)
            own_conn = True
        except Exception as e:
            logger.warning(f"templates_block: pg connect failed: {e}")
            return None

    try:
        # 1. Filter cited refs to NC/OFI posture only.
        finding_by_ref = _fetch_finding_by_ref(pg_conn, tenant_id, refs) if tenant_id else {}
        gap_refs = [r for r in refs if r in finding_by_ref]

        # 2. Look up primary templates for those refs.
        primaries = _fetch_primary_templates(pg_conn, gap_refs) if gap_refs else []
        primaries_by_ref = {p["control_ref"]: p for p in primaries}

        # 3. Fetch per-leaf progress + evidence_type in one pass.
        leaf_ids = [p["leaf_id"] for p in primaries]
        progress_by_leaf = _fetch_leaf_progress(pg_conn, tenant_id, leaf_ids) if leaf_ids else {}

        cite_ok_set = _cite_acceptable_types()

        # 4. Pull evidence_type per leaf from Neo4j (via catalog lookup).
        try:
            from enrichment.documents.document_requirements import (
                ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
            )
            all_ers = list(ALL_EVIDENCE_REQUIREMENTS) + [
                er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
            ]
            evtype_by_leaf = {er.id: er.evidence_type for er in all_ers if er.id in set(leaf_ids)}
        except Exception:
            evtype_by_leaf = {}

        # 5. Fetch advisory data per control_ref so leaves can carry the
        # per-MUST breakdown (items_missing, upload_hint) that the chat
        # answer used to append as prose. Task #204: unify per-MUST
        # advisory + template download into a single structured payload.
        # Ship 45'.c — batched via build_advisory_data_for_refs (one
        # shared eval_ctx + one shared Neo4j session across all refs).
        # Was N+1: 40 refs × per-call _build_eval_context + fresh session
        # + fresh spec_resolver = ~3.3s on a typical top-NC query.
        advisory_by_leaf: dict[str, dict] = {}
        try:
            from rag.posture.advisory import build_advisory_data_for_refs
            def _std_for(_ref: str) -> str:
                if _ref.startswith("Art."):
                    return "GDPR:2016/679"
                if _ref.startswith("B."):
                    return "ISO27701:2019"
                if _ref.startswith("A.") and _ref.count(".") >= 3:
                    return "ISO27701:2019"
                return "ISO27001:2022"
            _refs_by_std = [(r, _std_for(r)) for r in gap_refs]
            _batched = build_advisory_data_for_refs(
                pg_conn      = pg_conn,
                tenant_id    = tenant_id,
                refs_by_std  = _refs_by_std,
            )
            for _adv in _batched.values():
                if _adv:
                    for _lf in (_adv.get("leaves") or []):
                        _lid = _lf.get("leaf_id")
                        if _lid:
                            advisory_by_leaf[_lid] = _lf
        except Exception as e:
            logger.warning(f"templates_block: advisory data lookup skipped: {e}")

        # 6. Build per-leaf card payload.
        leaves_out: list[dict] = []
        for ref in gap_refs:
            p = primaries_by_ref.get(ref)
            if not p:
                # Cited NC/OFI ref but no template — skip; nothing to offer.
                continue
            leaf_id = p["leaf_id"]
            evidence_type = evtype_by_leaf.get(leaf_id, "")
            primary_dl, alt_dls = _formats_for(leaf_id, evidence_type)
            prog = progress_by_leaf.get(leaf_id, {"bound": 0, "total": 0, "remaining": 0})
            cite_acceptable = evidence_type in cite_ok_set
            # Enrich with per-MUST advisory data — the structured
            # equivalent of what used to be appended as prose after
            # the chat answer. Fields:
            #   items_missing — MUSTs with no active binding
            #   items_have    — MUSTs currently satisfied
            #   upload_hint   — one-line remediation prompt per leaf
            _adv_leaf = advisory_by_leaf.get(leaf_id, {})
            leaves_out.append({
                "control_ref":       ref,
                "leaf_id":           leaf_id,
                "title":             p["title"],
                "finding":           finding_by_ref[ref],
                "evidence_type":     evidence_type,
                "progress":          prog,
                "primary_download":  primary_dl,
                "alt_downloads":     alt_dls,
                "cite_acceptable":   cite_acceptable,
                "dashboard_url":     f"/#dashboard?control={ref}",
                # Task #204: per-MUST advisory data on the card so the
                # SPA renders "still needed" bullets alongside the
                # template download CTA. Prose appendix retired.
                "items_missing":     _adv_leaf.get("items_missing", []),
                "items_have":        _adv_leaf.get("items_have", []),
                "upload_hint":       _adv_leaf.get("upload_hint", ""),
            })

        # 6. Starter nudge — quick check on journey phase.
        starter_nudge = None
        try:
            with pg_conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,)
                )
                cur.execute(
                    "SELECT processes_personal_data FROM client_facts "
                    " WHERE tenant_id = %s::uuid",
                    (tenant_id,),
                )
                row = cur.fetchone()
            profile_row_exists = row is not None
            # A very quick heuristic — proper phase computation lives
            # in rag/journey/state.py; here we just check "did the
            # tenant do the profile step?". If not, they're fresh.
            if not profile_row_exists:
                starter_nudge = {
                    "message": "New to compliance? See where to start →",
                    "url": "/#getstarted",
                }
        except Exception:
            pass

        if not leaves_out and not starter_nudge:
            return None

        return {
            "mode":          "contextual" if leaves_out else "nudge_only",
            "leaves":        leaves_out,
            "starter_nudge": starter_nudge,
        }
    except Exception as e:
        logger.warning(f"templates_block: build failed: {e}")
        return None
    finally:
        if own_conn:
            try:
                pg_conn.close()
            except Exception:
                pass
