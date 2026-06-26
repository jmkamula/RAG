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
# Each hint is a short action sentence pegged to the evidence shape. The
# tenant reading this sees: "produce X to satisfy this leaf". Phrased as
# concrete acts (update / upload / produce / document) rather than
# abstract recommendations.

_UPLOAD_HINTS: dict[str, str] = {
    "policy":
        "Update the policy document to articulate each missing element.",
    "procedure":
        "Document each missing step in the procedure document.",
    "matrix":
        "Update the controls matrix to cover each missing element.",
    "directive":
        "Update the management directive to articulate each missing element.",
    "manual":
        "Update the manual to articulate each missing element.",
    "isms_scope":
        "Update the ISMS scope statement to cover each missing element.",
    "statement_of_applicability":
        "Update the Statement of Applicability to cover each missing element.",

    "register":
        "Add or extend a register (spreadsheet / table) with a column or row per missing element.",
    "asset_register":
        "Add or extend the asset register with a column per missing element.",
    "contact_register":
        "Add or extend the contact register with a column per missing element.",
    "schedule_register":
        "Add or extend the schedule register with a column per missing element.",
    "nonconformity_register":
        "Add or extend the nonconformity register with a column per missing element.",
    "operating_procedures_register":
        "Add or extend the operating procedures register with a column per missing element.",
    "lawful_basis_register":
        "Add or extend the lawful basis register with a column per missing element.",

    "review_record":
        "Conduct a review and produce a review record covering each missing element.",
    "audit_report":
        "Conduct an audit and produce a report covering each missing element.",
    "management_review_minutes":
        "Capture management review minutes covering each missing input.",

    "approval":
        "Produce an approval record with the missing signature / scope details.",
    "approval_record":
        "Produce an approval record with the missing signature / scope details.",

    "revocation_record":
        "Capture per-event revocation records with fields for each missing element.",
    "disposal_record":
        "Capture per-disposal records with fields for each missing element.",
    "closure_record":
        "Capture per-closure records with fields for each missing element.",
    "exercise_record":
        "Capture per-exercise records with fields for each missing element.",
    "activation_record":
        "Capture per-activation records with fields for each missing element.",
    "non_return_record":
        "Capture per-non-return records with fields for each missing element.",
    "return_record":
        "Capture per-return records with fields for each missing element.",
    "application_record":
        "Capture per-application records with fields for each missing element.",
    "discovery_record":
        "Capture per-discovery records with fields for each missing element.",
    "monitoring_record":
        "Capture per-event monitoring records with fields for each missing element.",
    "communication_record":
        "Capture communication records covering each missing element (date, audience, channel).",
    "communication_evidence":
        "Capture communication evidence covering each missing element.",
    "configuration_record":
        "Capture per-system configuration records with fields for each missing element.",
    "risk_assessment_record":
        "Capture risk assessment records covering each missing element.",
    "risk_treatment_record":
        "Capture risk treatment records covering each missing element.",
    "breach_notification":
        "Capture breach notifications covering each missing required content element.",
    "intake_process":
        "Document the intake process covering each missing trigger / path.",

    "scope_note":
        "Add a scope-note section enumerating the missing elements.",
    "agreement_template":
        "Update the agreement template to include clauses for each missing element.",
    "configuration_baseline":
        "Update the configuration baseline to document each missing setting.",
    "classification_scheme":
        "Update the classification scheme to define each missing level / dimension.",
    "responsibility_matrix":
        "Update the responsibility matrix to allocate each missing role.",
    "segregation_matrix":
        "Update the segregation matrix to capture each missing conflict pair.",
    "lawful_basis_register":
        "Add or extend the lawful basis register with a column per missing element.",
    "plan":
        "Update the plan to articulate each missing element.",
    "management_directive":
        "Update the management directive to articulate each missing element.",
}

_DEFAULT_HINT = (
    "Produce evidence (document, record, or register) that articulates "
    "each missing element."
)


def _hint_for(evidence_type: str) -> str:
    return _UPLOAD_HINTS.get(evidence_type, _DEFAULT_HINT)


def _humanize_evidence_type(et: str) -> str:
    """Convert evidence_type to display form (underscores → spaces)."""
    return (et or "").replace("_", " ")


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
) -> Optional[dict]:
    """Return structured advisory data for the given control, or None if no
    advisory is warranted.

    Returns dict with shape:
      {
        "control_ref":    "A.5.15",
        "standard_id":    "ISO27001:2022",
        "posture":        "NC" | "OFI",
        "reason":         "ALL: 0/4 children satisfied (1 with partial evidence)",
        "n_leaves":       4,
        "n_satisfied":    0,
        "n_partial":      1,
        "leaves": [
          {
            "leaf_id":              "req:A.5.15:access_control_policy",
            "leaf_label":           "access control policy",
            "evidence_type":        "policy",
            "evidence_type_label":  "policy document",
            "satisfied":            false,
            "n_have":               2,
            "n_total":              7,
            "items_have":           [<text>, ...],
            "items_missing":        [<text>, ...],
            "upload_hint":          "Update the policy document to ..."
          },
          ...
        ],
        "source":              "Source: ISO/IEC 27002:2022 §5.15 ..."
      }

    Returns None when:
      - No control_ref
      - Neo4j driver unavailable
      - No verdict (control not curated multi-leaf)
      - Posture is Comply or N/A (no advisory needed)
      - All leaves fully satisfied (no MUST gaps)
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
        logger.warning("advisory: evaluate_one_control failed for %s: %s", full_id, e)
        return None
    if verdict is None or not verdict.leaves:
        return None

    posture = (verdict.posture or "").upper()
    if posture not in ("NC", "OFI"):
        return None

    leaves_out: list[dict] = []
    any_unmet = False
    for leaf in verdict.leaves:
        unrec = list(leaf.items_unrecognised or [])
        rec   = list(leaf.items_recognised or [])
        unrec_ids = list(leaf.item_ids_unrecognised or [])
        rec_ids   = list(leaf.item_ids_recognised   or [])
        # Pair (id, text) so the form surface can bind inputs to MUST IDs.
        # `items_*` arrays kept text-only for backwards compat (chat
        # markdown renderer + existing eval cases). `must_items` is the
        # canonical pair list — UI consumes that for the form.
        must_items: list[dict] = []
        for _id, _t in zip(rec_ids, rec):
            must_items.append({"id": _id, "text": _t, "satisfied": True})
        for _id, _t in zip(unrec_ids, unrec):
            must_items.append({"id": _id, "text": _t, "satisfied": False})

        if not unrec:
            # Fully satisfied — include in output so UI shows the ✓ row,
            # but no upload hint needed.
            leaves_out.append({
                "leaf_id":             leaf.leaf_id,
                "leaf_label":          leaf.leaf_id.split(":")[-1].replace("_", " "),
                "evidence_type":       leaf.evidence_type,
                "evidence_type_label": _humanize_evidence_type(leaf.evidence_type),
                "satisfied":           True,
                "n_have":              len(rec),
                "n_total":             len(rec),
                "items_have":          list(rec),
                "items_missing":       [],
                "must_items":          must_items,
                "upload_hint":         "",
            })
            continue
        any_unmet = True
        leaves_out.append({
            "leaf_id":             leaf.leaf_id,
            "leaf_label":          leaf.leaf_id.split(":")[-1].replace("_", " "),
            "evidence_type":       leaf.evidence_type,
            "evidence_type_label": _humanize_evidence_type(leaf.evidence_type),
            "satisfied":           False,
            "n_have":              len(rec),
            "n_total":             len(rec) + len(unrec),
            "items_have":          list(rec),
            "items_missing":       list(unrec),
            "must_items":          must_items,
            "upload_hint":         _hint_for(leaf.evidence_type),
        })

    if not any_unmet:
        # All leaves satisfied — UI doesn't need advisory
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

        leaf_entry = {
            "leaf_id":          leaf.leaf_id,
            "leaf_label":       leaf.leaf_id.split(":")[-1].replace("_", " "),
            "musts_total":      total,
            "musts_bound":      bound,
            "yield_pct":        yield_pct,
            "items_have":       rec_texts,
            "items_missing":    unrec_texts,
            "must_items":       must_items,
            "source_documents": source_docs.get(leaf.leaf_id, []),
            "template_available": template_avail.get(leaf.leaf_id, False),
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
        f"↳ **How to advance {control_ref}** "
        f"(currently {posture}; "
        f"{n_satisfied} of {n_leaves} leaves satisfied, {n_partial} partial)"
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
