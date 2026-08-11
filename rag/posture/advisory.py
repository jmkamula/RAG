"""Per-MUST advisory generation.

Translates the engine's per-leaf verdicts into actionable guidance for the
tenant: which fulfilment criteria (MUSTs) are covered, which are missing,
and what to upload/produce to close the gap.

Deterministic compose (no LLM). The data path:
  evaluate_one_control() → ControlVerdict with leaves[].items_recognised/unrecognised
  + Neo4j ChecklistItem.text per MUST (already in the verdict's leaf metadata
    via items_recognised/unrecognised, which are TEXTS not ids)
  + evidence_type per leaf → upload-hint template

Returns markdown.

Conditions for advisory to render:
  - Control's engine verdict is NC or OFI (Comply/N/A → no advisory)
  - At least one MUST is unmet across the control's leaves

Hook point: appended deterministically to chat answers for posture_check
queries that identify exactly one control.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from .engine_runner import evaluate_one_control

logger = logging.getLogger(__name__)


# Lazy neo4j driver — created once per process the first time the advisory
# hook fires (chat doesn't already carry the driver in state). Cached on
# the module so subsequent calls reuse the connection.
_DRIVER = None


def _get_neo_driver():
    """Lazy neo4j driver creation. Returns None on any failure so the
    advisory hook silently no-ops rather than blocking the chat answer."""
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
        logger.warning("advisory: neo4j driver creation failed: %s", e)
        return None


# ── Upload-hint templates per evidence_type ──────────────────────────────────
#
# Compact verb + noun directive per evidence shape. The specificity of
# WHAT to add lives in the "Still needed" list above these hints — the
# hint gives the shape of the action, nothing more. Earlier versions
# ended every hint with "each missing element" or "with a column per
# missing element" — templated tail that was redundant with the Still
# needed list. Trimmed to the actionable verb + object 2026-07-04
# (loose end #6).

_UPLOAD_HINTS: dict[str, str] = {
    # Documents — narrative artefacts to update
    "policy":                       "Update your policy document.",
    "procedure":                    "Update your procedure document.",
    "plan":                         "Update your plan document.",
    "matrix":                       "Update your controls matrix.",
    "directive":                    "Update your management directive.",
    "management_directive":         "Update your management directive.",
    "manual":                       "Update your manual.",
    "isms_scope":                   "Update your ISMS scope statement.",
    "statement_of_applicability":   "Update your Statement of Applicability.",
    "scope_note":                   "Add a scope-note section.",
    "agreement_template":           "Update your agreement template.",
    "configuration_baseline":       "Update your configuration baseline.",
    "classification_scheme":        "Update your classification scheme.",
    "responsibility_matrix":        "Update your responsibility matrix.",
    "segregation_matrix":           "Update your segregation matrix.",
    "intake_process":               "Document your intake process.",

    # Registers — spreadsheet-shaped inventories to add rows / columns to
    "register":                     "Add or extend a register (spreadsheet or table).",
    "asset_register":               "Add or extend the asset register.",
    "contact_register":             "Add or extend the contact register.",
    "schedule_register":            "Add or extend the schedule register.",
    "nonconformity_register":       "Add or extend the nonconformity register.",
    "operating_procedures_register":"Add or extend the operating procedures register.",
    "lawful_basis_register":        "Add or extend the lawful basis register.",

    # Reviews + audits — periodic evidence of executed activity
    "review_record":                "Add a review record.",
    "audit_report":                 "Add an audit report.",
    "management_review_minutes":    "Capture management review minutes.",

    # Approvals — signed decision records
    "approval":                     "Produce an approval record.",
    "approval_record":              "Produce an approval record.",

    # Per-event records — one row per lifecycle event
    "revocation_record":            "Capture per-event revocation records.",
    "disposal_record":              "Capture per-disposal records.",
    "closure_record":               "Capture per-closure records.",
    "exercise_record":              "Capture per-exercise records.",
    "activation_record":            "Capture per-activation records.",
    "non_return_record":            "Capture per-non-return records.",
    "return_record":                "Capture per-return records.",
    "application_record":           "Capture per-application records.",
    "discovery_record":             "Capture per-discovery records.",
    "monitoring_record":            "Capture per-event monitoring records.",
    "communication_record":         "Capture communication records (date, audience, channel).",
    "communication_evidence":       "Capture communication evidence.",
    "configuration_record":         "Capture per-system configuration records.",
    "risk_assessment_record":       "Capture risk assessment records.",
    "risk_treatment_record":        "Capture risk treatment records.",
    "breach_notification":          "Capture breach notifications.",
}

_DEFAULT_HINT = "Produce evidence (document, record, or register)."


def _hint_for(evidence_type: str) -> str:
    return _UPLOAD_HINTS.get(evidence_type, _DEFAULT_HINT)


def _humanize_evidence_type(et: str) -> str:
    """Convert evidence_type slug to display form. Snake_case → Title
    Case. e.g. 'communication_record' → 'Communication Record',
    'policy' → 'Policy'. Special-cased acronyms preserved."""
    if not et:
        return ""
    # Common acronyms + already-uppercased words to preserve
    preserve = {"iso", "gdpr", "dpia", "roi", "sla", "kpi", "cia"}
    parts = et.replace("_", " ").split()
    out = []
    for w in parts:
        if w.lower() in preserve:
            out.append(w.upper())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def _humanize_leaf_label(leaf) -> str:
    """Prefer the catalog's authored title; fall back to snake_case-to-title.

    leaf.title is human-friendly ('Information Security Policy (Annex A.5.1)').
    The fallback strips the parent control_ref suffix when it's tacked on,
    so we don't render 'Information Security Policy (Annex A.5.1) — Coverage'
    in a per-leaf row where the control ref already appears in the parent.
    """
    if getattr(leaf, "title", None):
        # Drop trailing " (Annex A.X)" style parenthetical if present
        t = leaf.title
        # Common patterns to strip: "(Annex A.5.1)", "(A.5.1)"
        import re as _re
        t = _re.sub(r"\s*\((?:Annex\s+)?[A-Z]?\.?[\d.]+\)\s*$", "", t).strip()
        return t
    # Fallback: leaf_id evidence-type slug → Title Case
    from rag.id_types import leaf_evidence_type
    slug = leaf_evidence_type(getattr(leaf, "leaf_id", "") or "")
    return _humanize_evidence_type(slug)


# ── Source-of-truth label per standard ───────────────────────────────────────

def _source_label(control_ref: str, standard_id: str) -> str:
    """Best-effort 'see X' citation for the standard the MUSTs derive from."""
    if standard_id.startswith("ISO27001"):
        # ISO 27001 controls draw implementation guidance from ISO 27002.
        # ISMS clauses (4-10) are in ISO 27001 directly.
        if control_ref and control_ref.startswith("A."):
            # Strip "A.": A.5.15 → 5.15
            sub = control_ref[2:]
            return f"Source: ISO/IEC 27002:2022 §{sub} implementation guidance."
        return f"Source: ISO/IEC 27001:2022 clause {control_ref}."
    if standard_id.startswith("GDPR"):
        return f"Source: GDPR {control_ref} (EU Regulation 2016/679) + EDPB guidance."
    return f"Source: {standard_id} {control_ref}."


# ── Data builder (UI surfaces consume this) ──────────────────────────────────

def build_per_must_advisory_data(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    standard_id:  str = "ISO27001:2022",
    neo4j_driver = None,
    *,
    pre_built_ctx = None,
    shared_session = None,
    shared_resolver = None,
) -> Optional[dict]:
    """Return structured advisory data for the given control, or None if no
    advisory is warranted.

    Returns dict with shape:
      {
        "control_ref":    "A.5.15",
        "standard_id":    "ISO27001:2022",
        "posture":        "NC" | "OFI",
        "reason":         "0/4 leaves satisfied (1 with partial evidence)",
        "n_leaves":       4,
        "n_satisfied":    0,
        "n_partial":      1,
        "leaves": [
          {
            "leaf_id":              "req:A.5.15:access_control_policy",
            "leaf_label":           "Access Control Policy",
            "evidence_type":        "policy",
            "evidence_type_label":  "Policy Document",
            "satisfied":            false,
            "n_have":               2,
            "n_total":              7,
            "items_have":           [<text>, ...],
            "items_missing":        [<text>, ...],
            "must_items":           [{"id":..., "text":..., "satisfied":bool,
                                     "guidance":[...],
                                     "bridge_sources":[{...}]}...],
            "n_bridged":            0,   # count of MUSTs unmet-direct but
                                         # covered via xfw bridges
            "prerequisites":        [...],
            "upload_hint":          "Update your policy document."
          },
          ...
        ],
        "source":              "Source: ISO/IEC 27002:2022 §5.15 ..."
      }

    Returns None when:
      - No control_ref
      - No SSoT rows for this tenant+control (fallback path also finds
        no verdict → treated as "not curated" or "N/A everywhere")
      - Live posture is Comply or N/A (no advisory needed)
      - All leaves fully satisfied (no MUST gaps)

    Ship 60'.b (2026-08-11) — sources from Ship 58'/59' SSoT
    (`posture_must_verdicts` + `posture_must_bridge_coverage`) instead
    of re-running `evaluate_one_control` per request. Falls back to the
    legacy engine path if SSoT is unpopulated or the leaf structure
    fetch fails — no big-bang cutover.
    """
    if not control_ref:
        return None

    # Ship 60'.b — SSoT + leaf-structure path. Skip the engine round-trip
    # when we have per-MUST truth already computed.
    data = _build_advisory_from_ssot(
        pg_conn, tenant_id, control_ref, standard_id,
    )
    if data is not None:
        return data

    # Legacy fallback — SSoT unpopulated OR leaf structure fetch failed.
    # Kept for defence-in-depth during the transition window. Ship 60'.d
    # retro will assess whether this path can retire.
    if neo4j_driver is None:
        neo4j_driver = _get_neo_driver()
        if neo4j_driver is None:
            return None

    full_id = f"{standard_id}:{control_ref}"
    try:
        verdict = evaluate_one_control(
            pg_conn, neo4j_driver, tenant_id, full_id,
            pre_built_ctx   = pre_built_ctx,
            shared_session  = shared_session,
            shared_resolver = shared_resolver,
        )
    except Exception as e:
        logger.warning("advisory: evaluate_one_control failed for %s: %s", full_id, e)
        return None
    if verdict is None or not verdict.leaves:
        return None

    posture = (verdict.posture or "").upper()
    if posture not in ("NC", "OFI"):
        return None

    from rag.templates.guidance_lookup import get_guidance_for_item
    from rag.templates.prerequisites_lookup import get_prerequisites_for_leaf
    from dataclasses import asdict as _asdict

    leaves_out: list[dict] = []
    any_unmet = False
    for leaf in verdict.leaves:
        unrec = list(leaf.items_unrecognised or [])
        rec   = list(leaf.items_recognised or [])
        unrec_ids = list(leaf.item_ids_unrecognised or [])
        rec_ids   = list(leaf.item_ids_recognised   or [])
        must_items: list[dict] = []
        for _id, _t in zip(rec_ids, rec):
            must_items.append({
                "id":         _id,
                "text":       _t,
                "satisfied":  True,
                "guidance":   list(get_guidance_for_item(_id)),
                "bridge_sources": [],
            })
        for _id, _t in zip(unrec_ids, unrec):
            must_items.append({
                "id":         _id,
                "text":       _t,
                "satisfied":  False,
                "guidance":   list(get_guidance_for_item(_id)),
                "bridge_sources": [],
            })

        prerequisites = [_asdict(p) for p in get_prerequisites_for_leaf(leaf.leaf_id)]
        leaf_satisfied = not unrec
        leaves_out.append({
            "leaf_id":             leaf.leaf_id,
            "leaf_label":          _humanize_leaf_label(leaf),
            "evidence_type":       leaf.evidence_type,
            "evidence_type_label": _humanize_evidence_type(leaf.evidence_type),
            "satisfied":           leaf_satisfied,
            "n_have":              len(rec),
            "n_total":             len(rec) + len(unrec),
            "items_have":          list(rec),
            "items_missing":       list(unrec),
            "must_items":          must_items,
            "n_bridged":           0,
            "prerequisites":       prerequisites,
            "upload_hint":         "" if leaf_satisfied else _hint_for(leaf.evidence_type),
        })
        if not leaf_satisfied:
            any_unmet = True

    if not any_unmet:
        return None

    return {
        "control_ref": control_ref,
        "standard_id": standard_id,
        "posture":     posture,
        "reason":      verdict.reason or "",
        "n_leaves":    len(verdict.leaves),
        "n_satisfied": sum(1 for l in leaves_out if l["satisfied"]),
        "n_partial":   sum(1 for l in leaves_out
                            if (not l["satisfied"]) and l["n_have"] > 0),
        "leaves":      leaves_out,
        "source":      _source_label(control_ref, standard_id),
    }


def _build_advisory_from_ssot(
    pg_conn,
    tenant_id:   str,
    control_ref: str,
    standard_id: str,
) -> Optional[dict]:
    """Ship 60'.b — SSoT-sourced advisory build.

    Reads three pieces:
      1. Leaf structure from Neo4j (cached, tenant-agnostic) —
         which MUSTs belong to which leaf + human text per MUST.
      2. Per-MUST fulfillment from `posture_must_verdicts` (SSoT).
         MUST-ids absent from SSoT are N/A-excluded for this tenant
         (writer drops them per `_fetch_na_must_ids` upstream).
      3. Live control-level `finding` from `posture_controls`
         (authoritative for top-level NC/OFI/Comply/N/A).

    Skips advisory when:
      - Leaf structure unavailable (uncurated / stub / no MUSTs).
      - SSoT unpopulated for this control (tenant never triggered
        load_posture yet — fallback path will).
      - Live posture Comply / N/A.
      - Every leaf fully satisfied.

    Returns None on any of those (advisory not warranted); returns the
    dict on success.
    """
    from rag.posture.leaf_structure import get_control_leaves
    from rag.posture.must_verdicts import read_must_verdicts_by_control
    from rag.templates.guidance_lookup import get_guidance_for_item
    from rag.templates.prerequisites_lookup import get_prerequisites_for_leaf
    from dataclasses import asdict as _asdict

    cl = get_control_leaves(control_ref, standard_id)
    if cl is None or not cl.leaves:
        return None

    verdicts = read_must_verdicts_by_control(
        pg_conn, tenant_id, control_ref, standard_id,
    )
    if not verdicts:
        return None  # SSoT unpopulated — fallback path will try engine

    # Top-level posture: consult posture_controls for the live finding.
    # SSoT stores per-MUST truth; posture_controls stores the tenant-
    # facing verdict which incorporates cascade overlays + tenant
    # overrides + confirmation state. Advisory renders only when this
    # composite says NC or OFI.
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute("""
                SELECT finding
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid
                   AND control_ref = %s
                   AND standard_id = %s
                 LIMIT 1
            """, (tenant_id, control_ref, standard_id))
            row = cur.fetchone()
    except Exception as e:
        logger.warning("advisory: posture_controls lookup failed for %s/%s: %s",
                       standard_id, control_ref, e)
        return None
    live_posture = (row[0] if row else "") or ""
    posture = live_posture.upper()
    if posture not in ("NC", "OFI"):
        return None

    leaves_out: list[dict] = []
    any_unmet = False
    for leaf in cl.leaves:
        # Join CATALOG MUSTs with SSoT rows. MUSTs absent from SSoT are
        # N/A-excluded for this tenant → drop.
        applicable_ids: list[str] = [
            mid for mid in leaf.must_ids if mid in verdicts
        ]
        if not applicable_ids:
            # Entire leaf N/A-excluded for this tenant — skip; the leaf
            # isn't part of the tenant's obligation surface.
            continue

        items_have:    list[str] = []
        items_missing: list[str] = []
        must_items:    list[dict] = []
        n_bridged_leaf = 0

        for mid in applicable_ids:
            mv    = verdicts[mid]
            text  = leaf.must_texts.get(mid, "")
            is_satisfied = mv.satisfied  # strict direct fulfillment
            # A MUST is 'bridged' when NOT direct-satisfied but has
            # bridge attribution. Tenant-facing UX may choose to soften
            # the "missing" framing when bridged; for now we surface
            # both `satisfied` (strict) + `bridge_sources` + let the
            # consumer decide.
            bridge_sources = [
                {
                    "source_must_id":     b.source_must_id,
                    "source_control_ref": b.source_control_ref,
                    "source_standard_id": b.source_standard_id,
                    "source_role":        b.source_role,
                    "edge_type":          b.edge_type,
                }
                for b in mv.bridge_sources
            ]
            if is_satisfied:
                items_have.append(text)
            else:
                items_missing.append(text)
                if bridge_sources:
                    n_bridged_leaf += 1
            must_items.append({
                "id":             mid,
                "text":           text,
                "satisfied":      is_satisfied,
                "guidance":       list(get_guidance_for_item(mid)),
                "bridge_sources": bridge_sources,
            })

        n_have  = len(items_have)
        n_total = len(applicable_ids)
        leaf_satisfied = (n_have == n_total)

        prerequisites = [_asdict(p) for p in get_prerequisites_for_leaf(leaf.leaf_id)]

        # Build a minimal leaf shim so _humanize_leaf_label can reuse
        # the existing logic (it reads `.title` + `.leaf_id`).
        class _LeafShim:
            pass
        _shim = _LeafShim()
        _shim.title   = leaf.title
        _shim.leaf_id = leaf.leaf_id

        leaves_out.append({
            "leaf_id":             leaf.leaf_id,
            "leaf_label":          _humanize_leaf_label(_shim),
            "evidence_type":       leaf.evidence_type,
            "evidence_type_label": _humanize_evidence_type(leaf.evidence_type),
            "satisfied":           leaf_satisfied,
            "n_have":              n_have,
            "n_total":             n_total,
            "items_have":          items_have,
            "items_missing":       items_missing,
            "must_items":          must_items,
            "n_bridged":           n_bridged_leaf,
            "prerequisites":       prerequisites,
            "upload_hint":         "" if leaf_satisfied else _hint_for(leaf.evidence_type),
        })
        if not leaf_satisfied:
            any_unmet = True

    if not leaves_out or not any_unmet:
        return None

    n_leaves_out = len(leaves_out)
    n_leaves_satisfied = sum(1 for l in leaves_out if l["satisfied"])
    n_leaves_partial   = sum(1 for l in leaves_out
                              if (not l["satisfied"]) and l["n_have"] > 0)
    reason = f"{n_leaves_satisfied}/{n_leaves_out} leaves satisfied"
    if n_leaves_partial:
        reason += f" ({n_leaves_partial} with partial evidence)"

    return {
        "control_ref": control_ref,
        "standard_id": standard_id,
        "posture":     posture,
        "reason":      reason,
        "n_leaves":    n_leaves_out,
        "n_satisfied": n_leaves_satisfied,
        "n_partial":   n_leaves_partial,
        "leaves":      leaves_out,
        "source":      _source_label(control_ref, standard_id),
    }


def build_advisory_data_for_refs(
    pg_conn,
    tenant_id: str,
    refs_by_std: list[tuple[str, str]],
    neo4j_driver = None,
) -> dict[str, Optional[dict]]:
    """Ship 45'.c — batched advisory build for many (control_ref, standard_id).

    Was N+1 in `build_templates_block`: 40 refs × per-call
    `_build_eval_context` (Postgres + Neo4j) + fresh Neo4j session +
    fresh `build_spec_resolver`. Now shared once, reused across all refs.

    Returns a dict {control_ref: advisory_data_or_None}.

    On any setup failure (Neo4j driver / eval_ctx), falls back to
    per-ref uncached calls so partial results still land.
    """
    if not refs_by_std:
        return {}

    if neo4j_driver is None:
        neo4j_driver = _get_neo_driver()

    from .engine_runner import _build_eval_context
    from rag.posture.spec_builder import build_spec_resolver as _bsr

    out: dict[str, Optional[dict]] = {}
    shared_ctx = None
    session_cm = None
    session = None
    resolver = None

    try:
        if neo4j_driver is not None:
            try:
                shared_ctx = _build_eval_context(pg_conn, neo4j_driver, tenant_id)
            except Exception as e:
                logger.warning("build_advisory_data_for_refs: eval_ctx failed: %s", e)
            try:
                session_cm = neo4j_driver.session()
                session = session_cm.__enter__()
                resolver = _bsr(session)
            except Exception as e:
                logger.warning("build_advisory_data_for_refs: session/resolver failed: %s", e)
                session = None
                resolver = None

        for control_ref, standard_id in refs_by_std:
            try:
                out[control_ref] = build_per_must_advisory_data(
                    pg_conn         = pg_conn,
                    tenant_id       = tenant_id,
                    control_ref     = control_ref,
                    standard_id     = standard_id,
                    neo4j_driver    = neo4j_driver,
                    pre_built_ctx   = shared_ctx,
                    shared_session  = session,
                    shared_resolver = resolver,
                )
            except Exception as e:
                logger.warning("build_advisory_data_for_refs(%s): %s", control_ref, e)
                out[control_ref] = None
    finally:
        if session_cm is not None:
            try:
                session_cm.__exit__(None, None, None)
            except Exception:
                pass

    return out


# ── Evidence-class breakdown (dashboard drill-in) ───────────────────────────


def _fetch_source_documents_per_leaf(
    pg_conn,
    tenant_id:    str,
    leaf_to_must_ids: dict[str, list[str]],
) -> dict[str, list[str]]:
    """For each leaf, return the distinct filenames that backed the bound
    MUSTs. Empty list when no bindings for that leaf.

    Uses the catalog's leaf → must_ids mapping (not Neo4j) so we don't
    miss a binding if its checklist_item_id is present in document_findings
    but the parent leaf relationship hasn't been recomputed yet.
    """
    all_must_ids = [mid for ids in leaf_to_must_ids.values() for mid in ids]
    if not all_must_ids:
        return {}
    out: dict[str, list[str]] = {leaf: [] for leaf in leaf_to_must_ids}
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s::text, false)", (tenant_id,),
        )
        cur.execute(
            """
            SELECT df.checklist_item_id, cd.filename
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE df.tenant_id   = %s::uuid
               AND df.is_active   = TRUE
               AND df.review_status = 'approved'
               AND df.checklist_item_id = ANY(%s)
            """,
            (tenant_id, all_must_ids),
        )
        # Build inverse map: must_id → leaf_id
        must_to_leaf: dict[str, str] = {}
        for leaf, ids in leaf_to_must_ids.items():
            for mid in ids:
                must_to_leaf[mid] = leaf
        per_leaf_filenames: dict[str, set[str]] = {leaf: set() for leaf in leaf_to_must_ids}
        for must_id, fn in cur.fetchall():
            leaf = must_to_leaf.get(must_id)
            if leaf and fn:
                per_leaf_filenames[leaf].add(fn)
        for leaf, fns in per_leaf_filenames.items():
            out[leaf] = sorted(fns)
    return out


def _fetch_cites_per_leaf(
    pg_conn,
    tenant_id: str,
    leaf_ids:  list[str],
) -> dict[str, list[dict]]:
    """For each leaf, fetch external_evidence_source rows grouped by
    system_id. Returns {leaf_id: [{system_id, system_name, system_url,
    musts: [{must_id, last_verified_at, next_review_due, is_fresh,
    per_must_note}]}, ...]}.

    Empty list when schema_v50 not applied (silent fallback).
    """
    if not leaf_ids:
        return {}
    out: dict[str, list[dict]] = {lid: [] for lid in leaf_ids}
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(
                """
                SELECT ees.leaf_id, s.id::text, s.system_name, s.system_url,
                       ees.must_id, ees.cadence_days, ees.per_must_note,
                       ees.last_verified_at, ees.next_review_due
                  FROM external_evidence_source ees
                  JOIN tenant_external_system s ON s.id = ees.system_id
                 WHERE ees.tenant_id = %s::uuid
                   AND ees.leaf_id   = ANY(%s)
                   AND ees.is_active = TRUE
                   AND s.is_active   = TRUE
                 ORDER BY ees.leaf_id, s.system_name, ees.must_id
                """,
                (tenant_id, leaf_ids),
            )
            from rag.posture.cite_mode import is_cite_fresh
            grouped: dict[tuple[str, str], dict] = {}
            for row in cur.fetchall():
                leaf_id, sys_id, sys_name, sys_url, must_id, cadence, note, lv, ndd = row
                key = (leaf_id, sys_id)
                if key not in grouped:
                    grouped[key] = {
                        "system_id":   sys_id,
                        "system_name": sys_name,
                        "system_url":  sys_url or "",
                        "musts":       [],
                    }
                grouped[key]["musts"].append({
                    "must_id":          must_id,
                    "cadence_days":     cadence,
                    "per_must_note":    note or "",
                    "last_verified_at": lv.isoformat() if lv else None,
                    "next_review_due":  ndd.isoformat() if ndd else None,
                    "is_fresh":         is_cite_fresh(lv, cadence),
                })
            for (leaf_id, _sys_id), group in grouped.items():
                out[leaf_id].append(group)
    except Exception:
        return out  # schema_v50 not applied — silent
    return out


def _fetch_template_availability(
    pg_conn,
    leaf_ids: list[str],
) -> dict[str, bool]:
    """Look up which leaves have a template in the templates table."""
    if not leaf_ids:
        return {}
    out: dict[str, bool] = {lid: False for lid in leaf_ids}
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT leaf_id FROM templates WHERE leaf_id = ANY(%s)",
            (leaf_ids,),
        )
        for (lid,) in cur.fetchall():
            out[lid] = True
    return out


def build_evidence_class_breakdown(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    standard_id:  str = "ISO27001:2022",
    neo4j_driver = None,
) -> Optional[dict]:
    """Per-control evidence-class breakdown for the dashboard drill-in.

    Groups the control's leaves by evidence_type. For each class group:
      - which leaves belong to that class
      - per-leaf MUSTs total + bound + missing
      - source documents that backed the bound MUSTs
      - template availability per leaf
      - class-level rollup + upload_hint

    Returns the rollup regardless of posture (Comply controls show
    "100% covered" cells; this is a *coverage* surface, not just
    advisory). Returns None only when the control is uncurated.

    Shape:
      {
        "control_ref": "A.5.18",
        "standard_id": "ISO27001:2022",
        "posture": "NC",
        "n_leaves": 5,
        "musts_total": 31,
        "musts_bound": 5,
        "overall_yield_pct": 16,
        "evidence_classes": [
          {
            "evidence_type": "procedure",
            "evidence_type_label": "procedure",
            "class_musts_total": 8,
            "class_musts_bound": 1,
            "class_yield_pct":   12,
            "upload_hint": "Document each missing step ...",
            "leaves": [
              {
                "leaf_id":          "req:A.5.18:access_rights_procedure",
                "leaf_label":       "access rights procedure",
                "musts_total":      8,
                "musts_bound":      1,
                "yield_pct":        12,
                "items_have":       [<text>...],
                "items_missing":    [<text>...],
                "must_items":       [{"id":..., "text":..., "satisfied":bool}],
                "source_documents": ["Access Control Policy.docx"],
                "template_available": true,
              },
              ...
            ]
          },
          ...
        ]
      }
    """
    if not control_ref:
        return None
    if neo4j_driver is None:
        neo4j_driver = _get_neo_driver()
        if neo4j_driver is None:
            return None

    full_id = f"{standard_id}:{control_ref}"
    try:
        verdict = evaluate_one_control(pg_conn, neo4j_driver, tenant_id, full_id)
    except Exception as e:
        logger.warning("evidence_class_breakdown: evaluate failed for %s: %s", full_id, e)
        return None
    if verdict is None or not verdict.leaves:
        return None

    # Build the leaf → bound must_ids map from verdict, plus full must_ids
    # set per leaf.
    leaf_to_bound_ids: dict[str, list[str]] = {
        leaf.leaf_id: list(leaf.item_ids_recognised or [])
        for leaf in verdict.leaves
    }
    leaf_to_all_ids: dict[str, list[str]] = {
        leaf.leaf_id: list(leaf.item_ids_recognised or []) + list(leaf.item_ids_unrecognised or [])
        for leaf in verdict.leaves
    }

    leaf_ids = list(leaf_to_all_ids.keys())
    source_docs    = _fetch_source_documents_per_leaf(pg_conn, tenant_id, leaf_to_bound_ids)
    template_avail = _fetch_template_availability(pg_conn, leaf_ids)
    cites_per_leaf = _fetch_cites_per_leaf(pg_conn, tenant_id, leaf_ids)

    # Group leaves by evidence_type
    by_class: dict[str, list[dict]] = {}
    musts_total_all = 0
    musts_bound_all = 0
    for leaf in verdict.leaves:
        rec_ids   = list(leaf.item_ids_recognised   or [])
        unrec_ids = list(leaf.item_ids_unrecognised or [])
        rec_texts   = list(leaf.items_recognised   or [])
        unrec_texts = list(leaf.items_unrecognised or [])
        total = len(rec_ids) + len(unrec_ids)
        bound = len(rec_ids)
        musts_total_all += total
        musts_bound_all += bound
        yield_pct = int(round(bound / total * 100)) if total else 0

        must_items: list[dict] = []
        for _id, _t in zip(rec_ids, rec_texts):
            must_items.append({"id": _id, "text": _t, "satisfied": True})
        for _id, _t in zip(unrec_ids, unrec_texts):
            must_items.append({"id": _id, "text": _t, "satisfied": False})

        # Cite-acceptable: surface the cite lane on this leaf's UI card.
        # Engine has already counted fresh cites toward `bound` above
        # (leaf_evaluators._fetch_recognised_cites); the flag drives the
        # frontend's render — whether to show "+ Cite source" + grouped
        # cites + verify buttons for this leaf.
        from rag.posture.cite_mode import is_cite_acceptable
        cite_acceptable = is_cite_acceptable(leaf.evidence_type)

        leaf_entry = {
            "leaf_id":          leaf.leaf_id,
            "leaf_label":       _humanize_leaf_label(leaf),
            "musts_total":      total,
            "musts_bound":      bound,
            "yield_pct":        yield_pct,
            "items_have":       rec_texts,
            "items_missing":    unrec_texts,
            "must_items":       must_items,
            "source_documents": source_docs.get(leaf.leaf_id, []),
            "template_available": template_avail.get(leaf.leaf_id, False),
            "cite_acceptable":  cite_acceptable,
            "cites":            cites_per_leaf.get(leaf.leaf_id, []),
        }
        by_class.setdefault(leaf.evidence_type or "evidence", []).append(leaf_entry)

    # Emit class rollups, ordered by class-total descending (most-MUSTs first)
    classes_out: list[dict] = []
    for et, leaves in by_class.items():
        class_total = sum(l["musts_total"] for l in leaves)
        class_bound = sum(l["musts_bound"] for l in leaves)
        classes_out.append({
            "evidence_type":       et,
            "evidence_type_label": _humanize_evidence_type(et),
            "class_musts_total":   class_total,
            "class_musts_bound":   class_bound,
            "class_yield_pct":     int(round(class_bound / class_total * 100))
                                   if class_total else 0,
            "upload_hint":         _hint_for(et),
            "leaves":              leaves,
        })
    classes_out.sort(key=lambda c: -c["class_musts_total"])

    overall_yield = int(round(musts_bound_all / musts_total_all * 100)) \
                    if musts_total_all else 0
    return {
        "control_ref":      control_ref,
        "standard_id":      standard_id,
        "posture":          (verdict.posture or "").upper(),
        "n_leaves":         len(verdict.leaves),
        "musts_total":      musts_total_all,
        "musts_bound":      musts_bound_all,
        "overall_yield_pct": overall_yield,
        "evidence_classes":  classes_out,
        "source":           _source_label(control_ref, standard_id),
    }


# ── Markdown renderer (chat surface) ─────────────────────────────────────────

def _render_advisory_markdown(data: dict) -> str:
    """Render the data dict as markdown. Same shape as before — chat
    surfaces use this. Returns "" if data is None."""
    if not data:
        return ""
    posture     = data["posture"]
    control_ref = data["control_ref"]
    n_leaves    = data["n_leaves"]
    n_satisfied = data["n_satisfied"]
    n_partial   = data["n_partial"]

    header_line = (
        f"↳ **How to strengthen {control_ref}** "
        f"(currently {posture}; "
        f"{n_satisfied} of {n_leaves} required artifacts in place, "
        f"{n_partial} in progress)"
    )

    leaf_sections: list[str] = []
    for leaf in data["leaves"]:
        if leaf["satisfied"]:
            continue  # advisory is only for unmet leaves
        leaf_label = leaf["leaf_label"]
        et_label   = leaf["evidence_type_label"]
        n_have, n_total = leaf["n_have"], leaf["n_total"]

        lines = [f"  - **{leaf_label}** ({et_label}) — {n_have}/{n_total} elements covered."]
        rec = leaf["items_have"]
        if rec:
            have_str = "; ".join(t[:80] for t in rec[:6])
            if len(rec) > 6:
                have_str += f"; (+{len(rec) - 6} more)"
            lines.append(f"    Have: {have_str}.")

        miss = leaf["items_missing"]
        miss_show = miss[:10]
        miss_tail = f" (+{len(miss) - 10} more)" if len(miss) > 10 else ""

        lines.append("    Still needed:")
        for it in miss_show:
            lines.append(f"      - {it}")
        if miss_tail:
            lines.append(f"      - …{miss_tail}")
        lines.append(f"    To address: {leaf['upload_hint']}")
        leaf_sections.append("\n".join(lines))

    if not leaf_sections:
        return ""

    return (
        "\n\n"
        + header_line
        + "\n\n"
        + "\n\n".join(leaf_sections)
        + "\n\n"
        + data["source"]
    )


# ── Main entry point (chat path) ─────────────────────────────────────────────

def build_per_must_advisory(
    pg_conn,
    tenant_id:    str,
    control_ref:  str,
    standard_id:  str = "ISO27001:2022",
    neo4j_driver = None,
) -> str:
    """Return markdown advisory for the given control, or "" if no advisory
    is warranted (Comply, N/A, no curated multi-leaf, or all MUSTs satisfied).

    Cost: one evaluate_one_control() call (Neo4j + Postgres). Acceptable on
    the chat path for posture_check queries that identify a single control.

    If neo4j_driver is None, lazily creates one from env vars. Returns ""
    on any failure (chat path must never break on advisory issues).
    """
    data = build_per_must_advisory_data(
        pg_conn      = pg_conn,
        tenant_id    = tenant_id,
        control_ref  = control_ref,
        standard_id  = standard_id,
        neo4j_driver = neo4j_driver,
    )
    return _render_advisory_markdown(data) if data else ""
