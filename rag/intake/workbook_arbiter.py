"""Ship 91'.a — Workbook LLM row-arbiter.

Runs AFTER workbook_persistence structural extraction. For each
fingerprint-matched sheet the structural pass produced, this module
scaffolds an LLM prompt with the catalog's three-way discipline
(required / optional / cite) as frame + all data rows, and asks the
LLM to judge per row per MUST.

Design (Ship 91'.a — scope: propose only, no writes):
  - LLM sees the full MUST set for the target leaf
  - Full row scan (user-selected in Ship 91' design)
  - Output: list[ArbitratedFinding] — pure function, no DB
  - Verifier: substring-match evidence_text against actual cell
    content at LLM-claimed (row, column). Catches fabrication.
  - MUST id validation: verbatim match against real_must_ids.

Writes happen in Ship 91'.b (workbook_persistence extension).

Model: gpt-4.1-mini (~$0.02/sheet, consistent with Ship 89/90 curators).

Precision safeguards mirror the LLM extractor path
(rag/intake/extractor.py::_evidence_grounded / Ship 6'.b):
  * Substring match after punctuation-strip + case-fold
  * MUST id must exist on the target leaf (dropped otherwise)
  * (row, column) must resolve to a real data cell
  * grounding_method='workbook_llm_arbiter' surfaces in
    document_findings for auditor telemetry
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from rag.intake.workbook_discovery import (
    SheetProposal,
    tokenize,
)
from rag.llm_client import call as llm_call
from rag.llm_models import MODEL_WORKBOOK_ARBITER

logger = logging.getLogger(__name__)


# ── Public dataclass ─────────────────────────────────────────────────

@dataclass
class ArbitratedFinding:
    """One LLM-arbitrated finding, validated + ready for write."""
    control_ref:       str
    standard_id:       str
    checklist_item_id: str            # MUST id
    status:            str            # 'present' or 'partial'
    confidence:        str            # 'high' or 'medium'
    evidence_text:     str            # verbatim from the source cell
    sheet_name:        str
    source_row:        int            # 1-based row number in sheet
    source_column:     str            # header text
    source_cell:       str            # A1-notation ("D5")


# ── Constants ────────────────────────────────────────────────────────

_MAX_ROWS_PER_PROMPT = 200   # cap rows to prevent runaway prompts on large registers
_MIN_EVIDENCE_LEN    = 3     # short enough for register cells (IDs, dates), long
                             # enough to reject "-" / "?" fabrication
_MAX_FINDINGS_PER_SHEET = 400  # sanity cap on LLM output


# ── Prompt ───────────────────────────────────────────────────────────

_ARBITER_SYSTEM = """You are a compliance auditor extracting evidence from a workbook register sheet.

You will see:
  1. The sheet's fingerprint-matched target: a specific compliance
     leaf with its MUST items (unit requirements).
  2. The catalog's three-way column discipline for this leaf:
       required_columns  — anchor columns proving the row IS this artefact
       optional_columns  — corroboration (owner, dates, status, notes)
       cite_columns      — cells that hyperlink to external evidence
  3. The sheet's actual header row + data rows.

Task: for each DATA ROW × each MUST on the leaf, judge whether the
row contains evidence satisfying that MUST. Emit only rows where
evidence exists (skip not_addressed to keep the response compact).

Return strict JSON:
{
  "findings": [
    {
      "row_number":    3,
      "must_id":       "item:A.5.9:asset_records",
      "status":        "present" | "partial",
      "evidence_text": "verbatim substring from the row's cell",
      "source_column": "Asset ID",
      "confidence":    "high" | "medium"
    },
    ...
  ]
}

RULES:
- Use ONLY must_ids from the provided MUSTs list (verbatim; do not invent)
- evidence_text MUST be a verbatim substring from the source cell.
  If a cell says "MFA enforced via Okta since 2024-03", you may quote
  the whole thing or any contiguous span — but do NOT paraphrase.
- source_column MUST be one of the sheet's actual header names.
- Skip rows with no evidence for a MUST (do not emit not_addressed).
- Confidence: 'high' if the cell explicitly names the MUST subject;
  'medium' if the cell implies it or requires interpretation.
- Status: 'present' if the MUST is fully evidenced in this row's
  cell; 'partial' if the evidence is directional but incomplete
  (e.g. cell says "planned" without proof of implementation).
- Look at ALL columns — including Notes, Comments, and free-text
  columns. Structural extraction already handled the fingerprinted
  columns; you're adding value on cells the fingerprints missed.

Return JSON only."""


# ── Row utilities ────────────────────────────────────────────────────

def _idx_to_column_letter(idx: int) -> str:
    """0 → 'A', 25 → 'Z', 26 → 'AA'."""
    result = ""
    n = idx + 1
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = chr(ord("A") + r) + result
    return result


def _cell_ref(row_number_1based: int, col_idx: int) -> str:
    return f"{_idx_to_column_letter(col_idx)}{row_number_1based}"


def _row_to_dict(headers: list[str], row: list[Any]) -> dict[str, str]:
    """Zip headers with row cells, empty cells omitted."""
    out: dict[str, str] = {}
    for i, h in enumerate(headers):
        if not h:
            continue
        val = row[i] if i < len(row) else None
        if val is None:
            continue
        s = str(val).strip()
        if not s:
            continue
        out[h] = s
    return out


def _find_header_col(headers: list[str], target_header: str) -> int:
    """Case-insensitive exact-match on header text; -1 if not found."""
    if not target_header:
        return -1
    target = target_header.strip().lower()
    for i, h in enumerate(headers):
        if h and h.strip().lower() == target:
            return i
    return -1


# ── Verifier ─────────────────────────────────────────────────────────

_PUNCT_RE = re.compile(r"[^\w\s]")

def _normalize_for_match(s: str) -> str:
    """Strip punctuation + collapse whitespace + lowercase."""
    if not s:
        return ""
    s = _PUNCT_RE.sub(" ", s)
    return " ".join(s.split()).lower()


def _evidence_grounded_in_cell(evidence: str, cell_value: str) -> bool:
    """Ship 6'.b pattern: verbatim substring after normalization.

    Lenient enough that punctuation drift ("MFA," vs "MFA") passes,
    strict enough to reject full fabrication ("Okta configured" when
    the cell just says "MFA")."""
    if not evidence or len(evidence) < _MIN_EVIDENCE_LEN:
        return False
    if not cell_value:
        return False
    needle = _normalize_for_match(evidence)[:80]
    haystack = _normalize_for_match(cell_value)
    return bool(needle) and needle in haystack


# ── Prompt builder ───────────────────────────────────────────────────

def _build_pass_block_summary(pass_yaml: dict) -> str:
    """Format the pass's required / optional / cite lists for the LLM."""
    lines = []
    def _list(key: str, label: str):
        cols = pass_yaml.get(key) or []
        if not cols:
            return
        lines.append(f"{label}:")
        for c in cols:
            fp = c.get("fingerprint") or []
            mid = c.get("binds_to") or "?"
            lines.append(f"  - {', '.join(str(t) for t in fp):30s} → {mid}")
    _list("required_columns", "  ANCHOR MUSTs (required)")
    _list("optional_columns", "  CORROBORATION MUSTs (optional)")
    _list("cite_columns",     "  CITED MUSTs (cite_columns)")
    return "\n".join(lines) if lines else "  (no column discipline declared)"


def _build_prompt(
    proposal:   SheetProposal,
    pass_yaml:  dict,
    musts:      list[dict],
    headers:    list[str],
    header_row: int,
    data_rows:  list[list[Any]],
) -> str:
    """Assemble the user prompt for one pass."""
    target_leaf   = pass_yaml.get("target_evidence_requirement", "?")
    target_ctrl   = pass_yaml.get("target_control", "?")
    evidence_type = pass_yaml.get("target_evidence_type", "?")

    musts_block = "\n".join(
        f"  {r['id']}  |  {(r.get('text') or '')[:150]}" for r in musts
    )
    header_line = " | ".join(h for h in headers if h)

    # Row lines — cap at _MAX_ROWS_PER_PROMPT to prevent runaway prompts
    row_lines: list[str] = []
    for offset, row in enumerate(data_rows[:_MAX_ROWS_PER_PROMPT]):
        row_num_1based = header_row + 2 + offset  # header is 0-indexed; data starts row+1 (1-based header+2)
        cells = _row_to_dict(headers, row)
        if not cells:
            continue
        # Render as "Row N: col=val, col=val, ..."
        parts = [f"{k}={v[:120]}" for k, v in cells.items()]
        row_lines.append(f"Row {row_num_1based}: " + " | ".join(parts))
    if len(data_rows) > _MAX_ROWS_PER_PROMPT:
        row_lines.append(f"... ({len(data_rows) - _MAX_ROWS_PER_PROMPT} more rows truncated)")

    return (
        f"SHEET: {proposal.sheet}\n"
        f"DETECTED AS: {target_leaf} (via {proposal.mapping_id}, "
        f"confidence {proposal.confidence})\n"
        f"CONTROL: {target_ctrl}  |  EVIDENCE TYPE: {evidence_type}\n\n"
        f"CATALOG COLUMN DISCIPLINE (from YAML):\n"
        f"{_build_pass_block_summary(pass_yaml)}\n\n"
        f"MUSTs on this leaf (bind ONLY to these ids VERBATIM):\n"
        f"{musts_block}\n\n"
        f"HEADER ROW ({header_row + 1}): {header_line}\n\n"
        f"DATA ROWS ({len(row_lines)} shown of {len(data_rows)} total):\n"
        + "\n".join(row_lines)
        + "\n\nReturn JSON only per the schema in the system prompt."
    )


# ── Main entry ───────────────────────────────────────────────────────

def _fetch_musts_for_leaf(leaf_id: str) -> list[dict]:
    """Query Neo4j for the MUST list of a specific leaf."""
    import os
    from neo4j import GraphDatabase
    drv = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )
    try:
        with drv.session() as s:
            rows = s.run(
                "MATCH (:EvidenceRequirement {id: $lid})-[:MUST_CONTAIN]->(ci) "
                "RETURN ci.id AS id, ci.text AS text ORDER BY id",
                lid=leaf_id,
            ).data()
        return rows
    finally:
        drv.close()


def arbitrate_sheet(
    proposal:  SheetProposal,
    pass_yaml: dict,
    rows:      list[list[Any]],
    api_key:   Optional[str] = None,
    *,
    max_tokens: int = 12000,
) -> list[ArbitratedFinding]:
    """Ship 91'.a entry point — arbitrate one fingerprint-matched sheet.

    Args:
      proposal:  SheetProposal (from workbook_discovery, includes
                 sheet + mapping_id + confidence + header_row + headers)
      pass_yaml: the pass_block dict from the mapping YAML (the pass
                 that produced this proposal — needed for MUST/column
                 discipline scaffolding)
      rows:      the sheet's raw row data (all rows including header)
      api_key:   ignored; LLM path uses rag.llm_client which reads env
      max_tokens: LLM response cap (default 4000; scales with row count)

    Returns:
      list[ArbitratedFinding] — validated proposals ready for write.
      Empty list on any failure (log + return, do not raise).
    """
    target_leaf = pass_yaml.get("target_evidence_requirement", "")
    target_ctrl = pass_yaml.get("target_control", "")
    if not target_leaf or target_leaf == "?":
        logger.debug("workbook_arbiter: skip %r — no target_leaf", proposal.sheet)
        return []

    # Fetch MUSTs — same discipline as ship86 curator
    try:
        musts = _fetch_musts_for_leaf(target_leaf)
    except Exception as e:
        logger.warning("workbook_arbiter: MUST fetch failed for %s: %s",
                       target_leaf, e)
        return []
    if not musts:
        logger.debug("workbook_arbiter: no MUSTs on leaf %s", target_leaf)
        return []

    real_must_ids = {r["id"] for r in musts}
    headers = proposal.headers or []
    header_row = proposal.header_row
    if header_row is None or not headers:
        logger.debug("workbook_arbiter: no header row on %r", proposal.sheet)
        return []

    # Data rows = everything after header
    data_rows = [r for r in rows[header_row + 1:] if any(cell for cell in r)]
    if not data_rows:
        return []

    prompt = _build_prompt(proposal, pass_yaml, musts, headers, header_row, data_rows)

    resp = llm_call(
        system      = _ARBITER_SYSTEM,
        user        = prompt,
        model       = MODEL_WORKBOOK_ARBITER,   # gpt-4.1-mini per Ship 91' choice
        purpose     = "extractor",
        max_tokens  = max_tokens,
        temperature = 0.1,
        timeout_s   = 120,
        response_format={"type": "json_object"},
    )
    if resp.error:
        logger.warning("workbook_arbiter: LLM error on %r: %s",
                       proposal.sheet, resp.error)
        return []
    # Some models wrap JSON in markdown fences (Claude does; gpt-4.1-mini
    # usually doesn't but strip defensively).
    raw = (resp.text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError as e:
        logger.warning("workbook_arbiter: JSON parse error on %r: %s (raw=%r)",
                       proposal.sheet, e, raw[:200])
        return []

    standard_id = _standard_from_leaf(target_leaf)
    findings: list[ArbitratedFinding] = []
    for f in (parsed.get("findings") or [])[:_MAX_FINDINGS_PER_SHEET]:
        must_id = f.get("must_id")
        if must_id not in real_must_ids:
            continue
        row_num = f.get("row_number")
        if not isinstance(row_num, int) or row_num <= header_row + 1:
            continue
        # Locate the source cell for verification
        src_col_name = f.get("source_column", "")
        col_idx = _find_header_col(headers, src_col_name)
        if col_idx < 0:
            continue
        # Convert LLM's row_num (1-based) to rows[] index (0-based)
        row_idx_in_rows = row_num - 1
        if row_idx_in_rows >= len(rows):
            continue
        cell_value = str(rows[row_idx_in_rows][col_idx] or "").strip() \
            if col_idx < len(rows[row_idx_in_rows]) else ""
        evidence_text = str(f.get("evidence_text", "")).strip()
        if not _evidence_grounded_in_cell(evidence_text, cell_value):
            continue
        status = f.get("status", "").strip().lower()
        if status not in ("present", "partial"):
            continue
        confidence = f.get("confidence", "medium").strip().lower()
        if confidence not in ("high", "medium"):
            confidence = "medium"
        findings.append(ArbitratedFinding(
            control_ref       = target_ctrl,
            standard_id       = standard_id,
            checklist_item_id = must_id,
            status            = status,
            confidence        = confidence,
            evidence_text     = evidence_text[:500],
            sheet_name        = proposal.sheet,
            source_row        = row_num,
            source_column     = src_col_name,
            source_cell       = _cell_ref(row_num, col_idx),
        ))
    return findings


def _standard_from_leaf(leaf_id: str) -> str:
    """Resolve target_evidence_requirement → standard_id (same as workbook_persistence)."""
    from enrichment.documents import document_requirements as DR
    for r in DR.ALL_EVIDENCE_REQUIREMENTS:
        if r.id == leaf_id:
            return r.standard_id
    for name in dir(DR):
        obj = getattr(DR, name, None)
        if isinstance(obj, DR.DerivedSpec):
            for r in obj.direct_evidence or []:
                if r.id == leaf_id:
                    return r.standard_id
    return ""


def arbitrate_workbook(
    proposals:           list[SheetProposal],
    workbook_rows:       dict[str, list[list[Any]]],
    mapping_pass_lookup: dict[tuple[str, str], dict],
    *,
    api_key: Optional[str] = None,
) -> list[ArbitratedFinding]:
    """Batch-arbitrate all fingerprint-matched sheets in a workbook.

    Args:
      proposals:  from discover_workbook — one per fingerprint-matched sheet
      workbook_rows: sheet_name → raw rows
      mapping_pass_lookup: (mapping_id, pass_name) → pass_yaml dict
                            (caller extracts from loaded YAML mappings)

    Returns flat list of all arbitrated findings across all sheets.
    """
    all_findings: list[ArbitratedFinding] = []
    for prop in proposals:
        rows = workbook_rows.get(prop.sheet) or []
        if not rows:
            continue
        for pass_prop in prop.passes:
            pass_yaml = mapping_pass_lookup.get(
                (prop.mapping_id, pass_prop.pass_name)
            )
            if not pass_yaml:
                continue
            findings = arbitrate_sheet(prop, pass_yaml, rows, api_key)
            all_findings.extend(findings)
    return all_findings


# ── Ship 91'.b — write path ──────────────────────────────────────────


def persist_arbitrated_findings(
    pg,
    tenant_id:          Any,
    client_document_id: Any,
    findings:           list[ArbitratedFinding],
    *,
    dedup_existing: bool = True,
) -> int:
    """Write arbitrated findings to document_findings.

    Dedup rule (Ship 91'.b):
      If a workbook-emitted structural finding already exists for the
      SAME (tenant, document, control_ref, checklist_item_id) with
      status='present' — SKIP. The structural pass wins by construction.
      Otherwise, emit the LLM finding.

    Returns count of findings actually written.
    """
    if not findings:
        return 0
    tenant_str = str(tenant_id)
    doc_str    = str(client_document_id)
    written    = 0

    # Load existing (control_ref, must_id, status) triples emitted by
    # workbook_persistence for this document — used to skip duplicates.
    existing: set[tuple[str, str]] = set()
    if dedup_existing:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            cur.execute(
                """
                SELECT control_ref, checklist_item_id
                  FROM document_findings
                 WHERE document_id = %s::uuid
                   AND is_active   = TRUE
                   AND inference_source IN ('workbook', 'workbook_llm_arbiter')
                   AND status = 'present'
                """,
                (doc_str,),
            )
            existing = {(row[0], row[1]) for row in cur.fetchall()}

    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )
            for f in findings:
                key = (f.control_ref, f.checklist_item_id)
                if key in existing:
                    continue
                excerpt = (
                    f"sheet {f.sheet_name!r} row {f.source_row} "
                    f"col {f.source_column!r}: {f.evidence_text}"
                )[:500]
                cur.execute(
                    """
                    INSERT INTO document_findings (
                        tenant_id, document_id,
                        control_ref, standard_id, checklist_item_id,
                        status, confidence, excerpt,
                        inference_source, grounding_method,
                        corroborating_signals,
                        is_active, retention_class
                    ) VALUES (
                        %s::uuid, %s::uuid,
                        %s, %s, %s,
                        %s, %s, %s,
                        'workbook_llm_arbiter', 'workbook_llm_arbiter',
                        ARRAY['llm_arbiter']::text[],
                        TRUE, 'compliance'
                    )
                    """,
                    (
                        tenant_str, doc_str,
                        f.control_ref, f.standard_id, f.checklist_item_id,
                        f.status, f.confidence, excerpt,
                    ),
                )
                written += 1
        pg.commit()
    except Exception:
        pg.rollback()
        raise
    return written
