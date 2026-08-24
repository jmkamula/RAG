"""Ship 93'.a — partial evidence explainability.

For each partial finding emitted by workbook_persistence, derive:
  1. WHAT'S MISSING — the specific mechanism that would move this
     MUST from partial to present.
  2. HOW TO MAKE IT RIGHT — actionable prose the tenant reads.

Two clean branches, derived from the source YAML pass:

  Branch A: MUST X is bound in the pass's `required_columns` BUT
            the tenant's workbook doesn't have that column populated
            (only the optional/corroboration column matched).
            → "Populate a column matching [fingerprint tokens] to
               anchor this evidence."

  Branch B: MUST X is bound ONLY in the pass's `optional_columns`
            (coverage:partial by design — corroboration-only).
            → "This is corroboration-only by design. Upload a
               document that explicitly demonstrates [MUST label]
               to move it to present."

The system NEVER writes a resolution. Explainer generates guidance
prose only; the tenant acts.

Server-side derivation — same pattern as Ship 92'.d cite
attestation humanization. Client renders as-is.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

_WORKBOOK_MAPPINGS_DIR = Path("/data/arioncomply/db/workbook_mappings")


# ── Module-level YAML cache (loaded once) ────────────────────────────

_MAPPING_CACHE: dict[str, dict] | None = None


def _load_mapping_cache() -> dict[str, dict]:
    """Load all workbook_mappings YAML files, indexed by mapping_id.
    Cached at module level — the catalog is stable per process.
    """
    global _MAPPING_CACHE
    if _MAPPING_CACHE is not None:
        return _MAPPING_CACHE
    cache: dict[str, dict] = {}
    for path in sorted(_WORKBOOK_MAPPINGS_DIR.glob("*.yaml")):
        try:
            y = yaml.safe_load(path.read_text())
        except Exception as e:
            logger.warning("partial_explainer: skip malformed %s: %s", path.name, e)
            continue
        mid = y.get("mapping_id")
        if mid:
            cache[mid] = y
    _MAPPING_CACHE = cache
    return cache


def _humanize_must_label(must_id: str) -> str:
    """Slug tail → readable label. Reuses the Ship 92'.d discipline.

    'item:10.1:reg_target_date' → 'Target date'
    'item:6.1.3:soa_reference' → 'SoA reference'
    'item:A.5.9:owner_per_asset' → 'Owner per asset'
    """
    if not must_id or ":" not in must_id:
        return must_id or ""
    tail = must_id.rsplit(":", 1)[-1]
    parts = tail.split("_")
    preserve = {"iso": "ISO", "gdpr": "GDPR", "dpia": "DPIA", "sla": "SLA",
                "kpi": "KPI", "cia": "CIA", "roi": "ROI", "soa": "SoA",
                "sig": "SIG", "isms": "ISMS", "id": "ID", "pii": "PII",
                "bcp": "BCP", "ict": "ICT", "eol": "EOL"}
    expand = {"reg": "", "rev": "review", "rec": "record",
              "proc": "procedure", "off": "offboarding",
              "disc": "discovery", "recon": "reconciliation",
              "idmgmt": "identity management",
              "url": "URL", "ref": "reference"}
    out: list[str] = []
    for p in parts:
        low = p.lower()
        if low in preserve:
            out.append(preserve[low])
        elif low in expand:
            e = expand[low]
            if e:
                out.append(e)
        else:
            out.append(p.replace("-", " "))
    label = " ".join(t for t in out if t).strip()
    if not label:
        return tail.replace("_", " ")
    return label[0].upper() + label[1:]


def _humanize_fingerprint(fp: list[str]) -> str:
    """['due', 'date'] → 'Due Date' — for column-header display."""
    if not fp:
        return ""
    return " ".join(t.title() for t in fp)


def _fingerprint_variants(col: dict) -> list[str]:
    """Return all fingerprint variants for a column binding — the
    tenant can name their column any of these and it'd match.
    """
    variants: list[str] = []
    fp = col.get("fingerprint") or []
    if fp:
        variants.append(_humanize_fingerprint(fp))
    for alt in col.get("alternative_fingerprints") or []:
        if alt:
            variants.append(_humanize_fingerprint(alt))
    return variants


def _find_pass_for_finding(
    mapping_id: str,
    finding_must_id: str,
) -> Optional[dict]:
    """Find the pass_yaml inside a mapping that binds the given MUST.

    A mapping can have multiple passes (e.g. attestation register +
    review record). The one that binds this finding's MUST is the
    source of truth for explainability.
    """
    if not mapping_id or not finding_must_id:
        return None
    cache = _load_mapping_cache()
    mapping = cache.get(mapping_id)
    if not mapping:
        return None
    for p in mapping.get("passes") or []:
        for key in ("required_columns", "optional_columns"):
            for col in p.get(key) or []:
                if col.get("binds_to") == finding_must_id:
                    return p
    return None


def _find_required_binding(pass_yaml: dict, must_id: str) -> Optional[dict]:
    """Look up the required_columns entry binding a specific MUST.
    Returns the entry dict or None."""
    for col in pass_yaml.get("required_columns") or []:
        if col.get("binds_to") == must_id:
            return col
    return None


def _find_cite_binding(pass_yaml: dict, must_id: str) -> Optional[dict]:
    """Look up the cite_columns entry binding a MUST. Returns dict or None."""
    for col in pass_yaml.get("cite_columns") or []:
        if col.get("binds_to") == must_id:
            return col
    return None


def _target_evidence_type(pass_yaml: dict) -> str:
    """Human label for the evidence type — 'register' / 'record' / etc."""
    et = (pass_yaml.get("target_evidence_type") or "").replace("_", " ")
    return et.strip() or "workbook"


# ── Public entry ─────────────────────────────────────────────────────


def explain_partial(
    must_id:             str,
    mapping_id:          str,
    sheet_name:          str,
    matched_column:      str,
) -> dict:
    """Explain why a workbook finding is partial + how to move it to present.

    Args:
      must_id:        e.g. 'item:10.1:reg_target_date'
      mapping_id:     e.g. 'workbook.iso.10_1.isms_schedule_improvement_register'
      sheet_name:     e.g. 'ISMS Schedule' (for tenant context)
      matched_column: e.g. 'DUE DATE' (the column that DID match)

    Returns:
      {
        "must_label":      humanized MUST label
        "matched_column":  as-passed-in
        "sheet_name":      as-passed-in
        "branch":          'anchor_missing' | 'corroboration_only' | 'unknown'
        "why_partial":     one-sentence explanation
        "how_to_close":    list of actionable steps
        "primary_prose":   tenant-facing paragraph (may contain <strong>)
      }
    """
    result = {
        "must_id":        must_id,
        "must_label":     _humanize_must_label(must_id),
        "matched_column": matched_column,
        "sheet_name":     sheet_name,
        "branch":         "unknown",
        "why_partial":    "",
        "how_to_close":   [],
        "primary_prose":  "",
    }

    pass_yaml = _find_pass_for_finding(mapping_id, must_id)
    if not pass_yaml:
        result["primary_prose"] = (
            f"This is <strong>{result['must_label']}</strong>. Partial evidence "
            f"is on record from your workbook (sheet '{sheet_name}' col "
            f"'{matched_column}'), but we don't have the source YAML to "
            f"suggest a specific next step. Upload a document that explicitly "
            f"demonstrates {result['must_label'].lower()}."
        )
        result["how_to_close"] = [
            f"Upload a document that explicitly demonstrates {result['must_label'].lower()}.",
        ]
        return result

    required_bind = _find_required_binding(pass_yaml, must_id)
    cite_bind     = _find_cite_binding(pass_yaml, must_id)
    evidence_type = _target_evidence_type(pass_yaml)

    if required_bind:
        # Branch A: MUST X IS declared as an anchor (required_columns),
        # but the tenant's workbook doesn't have that column populated.
        # Only the optional/corroboration column matched.
        variants = _fingerprint_variants(required_bind)
        primary_variant = variants[0] if variants else result["must_label"]

        steps = []
        if variants:
            var_list = ", ".join(f"<code>{v}</code>" for v in variants[:3])
            steps.append(
                f"Add a column named like {var_list} to your "
                f"<strong>{sheet_name}</strong> {evidence_type} "
                f"and populate it per row."
            )
        else:
            steps.append(
                f"Add an anchor column for <strong>{result['must_label']}</strong> "
                f"to your <strong>{sheet_name}</strong> {evidence_type}."
            )

        if cite_bind:
            cite_kind = (cite_bind.get("cite_kind") or "internal_document").replace("_", " ")
            steps.append(
                f"Or add a hyperlink to the {cite_kind} in the "
                f"<strong>{cite_bind.get('fingerprint', ['reference'])[0].title()}</strong> "
                f"column of a data row."
            )

        steps.append(
            f"Or upload a supporting document that names "
            f"<strong>{result['must_label']}</strong> explicitly."
        )

        result["branch"] = "anchor_missing"
        result["why_partial"] = (
            f"Your workbook has the corroborating value in the "
            f"<strong>{matched_column}</strong> column but not the anchor "
            f"column that this evidence type expects."
        )
        result["how_to_close"] = steps
        result["primary_prose"] = (
            f"{result['why_partial']} "
            f"To move <strong>{result['must_label']}</strong> to <strong>present</strong>, "
            f"do one of: " + " ".join(f"({i+1}) {s.strip('.')}." for i, s in enumerate(steps))
        )
        return result

    # Branch B: MUST is only in optional_columns (coverage:partial) —
    # corroboration-only by design. Upload path is the only way.
    steps = []
    if cite_bind:
        cite_kind = (cite_bind.get("cite_kind") or "internal_document").replace("_", " ")
        steps.append(
            f"Add a hyperlink to the {cite_kind} in the "
            f"<strong>{cite_bind.get('fingerprint', ['reference'])[0].title()}</strong> "
            f"column of a data row (and confirm the attestation prompt)."
        )
    steps.append(
        f"Upload a document that explicitly demonstrates "
        f"<strong>{result['must_label']}</strong>."
    )

    result["branch"] = "corroboration_only"
    result["why_partial"] = (
        f"This is <em>corroboration-only</em> evidence by design. Your "
        f"workbook shows <strong>{matched_column}</strong>, which supports "
        f"but doesn't fully evidence <strong>{result['must_label']}</strong>."
    )
    result["how_to_close"] = steps
    result["primary_prose"] = (
        f"{result['why_partial']} "
        f"To move it to <strong>present</strong>: "
        + " ".join(f"({i+1}) {s.strip('.')}." for i, s in enumerate(steps))
    )
    return result


def explain_missing(
    must_id:   str,
    leaf_id:   str,
) -> dict:
    """Ship 93'.f — explain a MUST that has no active evidence anywhere.

    Unlike explain_partial (which traces to a specific workbook proposal),
    explain_missing looks across ALL workbook_mappings to find any pass
    that binds this MUST — that becomes the "here's how to add it"
    guidance. If no mapping binds it, the only path is doc upload.

    Args:
      must_id:  e.g. 'item:A.5.9:owner_per_asset'
      leaf_id:  e.g. 'req:A.5.9:asset_inventory'

    Returns:
      {
        "must_id":        as-passed
        "must_label":     humanized MUST label
        "branch":         'workbook_or_doc' | 'doc_only' | 'unknown'
        "workbook_hint":  optional dict with column-add suggestion
        "how_to_close":   list of actionable steps
        "primary_prose":  tenant-facing paragraph (may contain <strong>)
      }
    """
    result = {
        "must_id":       must_id,
        "must_label":    _humanize_must_label(must_id),
        "branch":        "unknown",
        "workbook_hint": None,
        "how_to_close":  [],
        "primary_prose": "",
    }

    # Search all mappings for a pass that binds this MUST
    cache = _load_mapping_cache()
    workbook_hits: list[dict] = []
    for mid, mapping in cache.items():
        for p in mapping.get("passes") or []:
            required = _find_required_binding(p, must_id)
            optional = None
            for col in p.get("optional_columns") or []:
                if col.get("binds_to") == must_id:
                    optional = col
                    break
            if required or optional:
                workbook_hits.append({
                    "mapping_id":         mid,
                    "target_evidence_type": _target_evidence_type(p),
                    "required":           required,
                    "optional":           optional,
                    "cite":               _find_cite_binding(p, must_id),
                })

    steps: list[str] = []

    if workbook_hits:
        # Prefer required_columns hits (the definitive "add this column"
        # answer); fall back to optional_columns hints.
        preferred = next(
            (h for h in workbook_hits if h.get("required")), None
        ) or workbook_hits[0]

        col_spec  = preferred["required"] or preferred["optional"]
        evidence_type = preferred["target_evidence_type"]
        variants = _fingerprint_variants(col_spec)

        if variants:
            var_list = ", ".join(f"<code>{v}</code>" for v in variants[:3])
            steps.append(
                f"Add a column named like {var_list} to a "
                f"<strong>{evidence_type}</strong> in your workbook."
            )

        cite = preferred.get("cite")
        if cite:
            cite_kind = (cite.get("cite_kind") or "internal_document").replace("_", " ")
            cite_fp = _humanize_fingerprint(cite.get("fingerprint") or [])
            if cite_fp:
                steps.append(
                    f"Or add a hyperlink to the {cite_kind} in a "
                    f"<strong>{cite_fp}</strong> column of a data row."
                )

        steps.append(
            f"Or upload a document that explicitly demonstrates "
            f"<strong>{result['must_label']}</strong>."
        )

        result["branch"] = "workbook_or_doc"
        result["workbook_hint"] = {
            "evidence_type": evidence_type,
            "column_variants": variants,
        }
        result["primary_prose"] = (
            f"No evidence yet for <strong>{result['must_label']}</strong>. "
            f"To add it: " + " ".join(f"({i+1}) {s.strip('.')}." for i, s in enumerate(steps))
        )
    else:
        # No mapping binds this MUST — doc upload is the only path.
        steps.append(
            f"Upload a document that explicitly demonstrates "
            f"<strong>{result['must_label']}</strong>."
        )
        result["branch"] = "doc_only"
        result["primary_prose"] = (
            f"No evidence yet for <strong>{result['must_label']}</strong>. "
            f"No workbook mapping in the catalog binds this — the only "
            f"way to close it is to upload a document that explicitly "
            f"demonstrates it."
        )

    result["how_to_close"] = steps
    return result


def explain_arbiter_partial(
    must_id:       str,
    evidence_text: str,
    sheet_name:    str,
    source_column: str,
) -> dict:
    """Ship 93'.z.ii — explain a partial emitted by the Ship 91' LLM
    row-arbiter.

    Arbiter partials are semantically different from workbook partials:
    they're the LLM's judgment that the cell contains corroborating
    text but not full evidence. The `evidence_text` was the LLM's
    verbatim quote from the cell that supports (but doesn't fully
    prove) the MUST.

    Branch: `arbiter_incomplete` — the LLM found supporting text but
    judged it insufficient. Close path: tenant reviews and either
    accepts as partial (Path A in the Stage-1 flow) OR uploads a
    document that explicitly demonstrates the MUST.

    Args:
      must_id:       the MUST id the arbiter judged partial
      evidence_text: LLM's verbatim quote from the cell
      sheet_name:    workbook sheet the cell was on
      source_column: header of the cell

    Returns the same shape as explain_partial for consistency.
    """
    result = {
        "must_id":        must_id,
        "must_label":     _humanize_must_label(must_id),
        "matched_column": source_column,
        "sheet_name":     sheet_name,
        "branch":         "arbiter_incomplete",
        "why_partial":    "",
        "how_to_close":   [],
        "primary_prose":  "",
    }
    quote = (evidence_text or "").strip()
    quote_display = quote[:100] + ("…" if len(quote) > 100 else "")

    steps = [
        f"Upload a document that explicitly demonstrates "
        f"<strong>{result['must_label']}</strong>.",
    ]
    if source_column:
        steps.append(
            f"Or amend the <strong>{source_column}</strong> column of your "
            f"workbook so it explicitly asserts <strong>{result['must_label']}</strong> "
            f"(re-upload triggers extraction)."
        )

    result["why_partial"] = (
        f"The arbiter found corroborating text in your workbook — "
        f"<em>“{quote_display}”</em> — but judged it insufficient as "
        f"full evidence of <strong>{result['must_label']}</strong>."
    )
    result["how_to_close"] = steps
    result["primary_prose"] = (
        f"{result['why_partial']} "
        f"To move it to <strong>present</strong>: "
        + " ".join(f"({i+1}) {s.strip('.')}." for i, s in enumerate(steps))
    )
    return result


def explain_finding(pg, tenant_id: str, finding_id: str) -> dict | None:
    """Fetch the finding + trace to its source YAML + explain.

    Handles workbook-sourced partials (via explain_partial) AND
    Ship 91' LLM-arbiter-sourced partials (via explain_arbiter_partial).
    Returns None for other cases.
    """
    with pg.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)",
            (str(tenant_id),),
        )
        cur.execute(
            """
            SELECT df.checklist_item_id, df.status, df.inference_source,
                   df.excerpt, wip.mapping_id, wip.sheet_name
              FROM document_findings df
              LEFT JOIN workbook_intake_proposal wip
                     ON wip.id = df.workbook_proposal_id
             WHERE df.tenant_id = %s::uuid
               AND df.id        = %s::uuid
               AND df.is_active
            """,
            (str(tenant_id), str(finding_id)),
        )
        row = cur.fetchone()
    if not row:
        return None
    must_id, status, inf_src, excerpt, mapping_id, sheet_name = row
    if status != "partial":
        return None
    # Excerpt shape from workbook + arbiter both start with
    # "sheet 'X' row N col 'Y'..." — parse the pieces we need.
    matched_column = ""
    evidence_text  = ""
    if excerpt:
        try:
            import re as _re
            m = _re.search(r"sheet '([^']*)'\s*(?:row\s*\d+)?\s*col '([^']*)'\s*(?::\s*(.*))?", excerpt)
            if m:
                sheet_name    = sheet_name or m.group(1)
                matched_column = m.group(2)
                evidence_text  = (m.group(3) or "").strip()
        except Exception:
            pass
    if inf_src == "workbook":
        return explain_partial(
            must_id        = must_id,
            mapping_id     = mapping_id or "",
            sheet_name     = sheet_name or "",
            matched_column = matched_column,
        )
    if inf_src == "workbook_llm_arbiter":
        return explain_arbiter_partial(
            must_id       = must_id,
            evidence_text = evidence_text or excerpt or "",
            sheet_name    = sheet_name or "",
            source_column = matched_column,
        )
    return None
