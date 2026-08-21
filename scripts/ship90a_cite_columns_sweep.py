#!/usr/bin/env python3
"""Ship 90'.a — cite_columns sweep across existing workbook mappings.

Ship 89'.b introduced the `cite_columns:` YAML field for cite-mode
integration (workbook hyperlinks → Ship 3' external_evidence_source).
5 mappings were manually backfilled during Ship 89'.b dogfood; the
remaining 235 have no cite_columns block.

This script sweeps the catalog and proposes cite_columns per mapping
via an LLM pass, mirroring Ship 86'.a/89'.a shape:
  - Read each YAML that lacks cite_columns
  - For each pass, fetch real MUSTs from Neo4j
  - Ask LLM: "of these MUSTs, which represent citations to external
    documents? Which columns would carry those cites?"
  - Validate each proposed MUST id against Neo4j
  - Emit cite_columns block via text-based insertion (preserves
    comments + formatting of existing YAML)

Behavior:
  --dry-run    (default): read + LLM propose + write diff to stdout
  --apply              : dry-run + actually write the YAML files
  --only <file>         : sweep only one file (basename or path)
  --limit N             : sweep at most N files (dry-run testing)

Usage:
  # Dry-run whole catalog
  POSTGRES_PASSWORD=... python scripts/ship90a_cite_columns_sweep.py --dry-run

  # Apply proposed cite_columns to one file
  POSTGRES_PASSWORD=... python scripts/ship90a_cite_columns_sweep.py \\
    --only asset_register.yaml --apply

  # Full sweep + apply
  POSTGRES_PASSWORD=... python scripts/ship90a_cite_columns_sweep.py --apply

Cost budget: ~$0.02/file at gpt-4.1-mini. 235 files → ~$5 for full sweep.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "/data/arioncomply")
import yaml
from rag.llm_client import call as llm_call

WORKBOOK_MAPPINGS_DIR = Path("/data/arioncomply/db/workbook_mappings")

_VALID_CITE_KINDS = {"internal_document", "url", "external_system"}

# Ship 91'.h — anti-pattern filter for cite_columns bindings.
# See docs/curation/cite_columns_criterion.md § "Anti-pattern binds".
# Never bind cite_columns to a MUST whose name suffix indicates it's
# data (timestamp/id/owner/status), not evidence.
_CITE_DISALLOWED_SUFFIXES = ("_date", "_at", "_owner")
_CITE_DISALLOWED_EXACT = frozenset({"date", "at", "owner"})


def _cite_bind_disallowed(must_id: str) -> bool:
    """True if this MUST id is a data-shape MUST that shouldn't hold cites.

    Suffixes rejected: `_date`, `_at`, `_owner`. Deliberately allowed:
    `_id` (identity-proving reports) and `_status` (certificate-proves-
    status). See docs/curation/cite_columns_criterion.md.
    """
    tail = (must_id or "").rsplit(":", 1)[-1]
    if tail in _CITE_DISALLOWED_EXACT:
        return True
    return any(tail.endswith(s) for s in _CITE_DISALLOWED_SUFFIXES)

# Skip these evidence_types — no external cite pattern by shape.
_NO_CITE_EVIDENCE_TYPES = {
    "segregation_matrix",
    "responsibility_matrix",
    "classification_scheme",
}


_PROMPT_SYSTEM = """You are a compliance auditor helping curate cite-mode integration for a workbook mapping YAML.

Question: does a real tenant's workbook for THIS register likely
contain a column that HYPERLINKS TO EXTERNAL DOCUMENTS (SharePoint
policies, external system records, regulator URLs, evidence PDFs)?

The MUSTs on this leaf represent stored evidence (data-shaped: IDs,
dates, owners, statuses). NONE of the MUSTs will be *named* like
citations — that's expected. Your job is to identify workbook COLUMN
SHAPES tenants use to cite external docs supporting these MUSTs,
then bind the cite to the semantically-closest existing MUST.

Return strict JSON:
{
  "has_cite_columns": true | false,
  "reasoning": "one sentence explaining the decision",
  "cite_columns": [
    {
      "column_hint":       ["treatment", "plan"],
      "must_id":           "item:6.1.2:reg_treatment_status",
      "cite_kind":         "internal_document",
      "verification_days": 365
    }
  ]
}

CITATION COLUMNS tenants add to registers (common patterns):

  Register type              | Typical cite column headers
  ---------------------------|-------------------------------------------
  Asset register            | (usually none — data in-sheet)
  Risk register             | "Treatment Plan", "Treatment Doc", "SoA Ref"
  DPIA register             | "DPIA Report", "Report Link", "Assessment Doc"
  Incident log              | "Incident Report", "Post-mortem", "Report Ref"
  DSAR register             | "Response Doc", "Fulfillment Evidence"
  Supplier register         | "Contract Ref", "DPA Doc", "SLA Ref"
  Audit register            | "Audit Report", "Finding Reference"
  Legal/regulatory register | "Requirement URL", "Regulator Site"
  Access register           | "Approval Ref", "Ticket", "Change Record"
  Training log              | "Certificate", "Proof of Completion", "Materials"
  Review record             | "Review Report", "Meeting Minutes"
  SoA                       | "Linked Policies", "Reference"
  Change record             | "Change Doc", "Approval Ref"

BINDING LOGIC (bind cite to semantically-closest MUST):

  Column "Treatment Plan"  → bind to reg_treatment_status
                             (the cite corroborates the treatment)
  Column "Incident Report" → bind to reg_incident_id
                             (the cite corroborates the incident itself)
  Column "Audit Report"    → bind to reg_audit_id or reg_finding
  Column "Certificate"     → bind to reg_completion_status
  Column "SoA Reference"   → bind to soa_reference (rare — leaf already
                             has a ref MUST)

The `binds_to` MUST must be from the provided list VERBATIM.

CITE_KIND field values:
  "internal_document" — SharePoint / internal drive / DMS
  "url"               — public web URL (regulator, standard body)
  "external_system"   — Okta, Odoo, ServiceNow, ITSM ticket link

VERIFICATION_DAYS field (freshness cadence, integer):
  Policy references     → 365
  Regulatory URLs       → 180
  Volatile external     → 90
  Long-cycle references → 730

WHEN TO RETURN has_cite_columns=false (no external cite lives in
this register shape):
  - Attestation-only registers (personnel_security_attestation) —
    presence IS the evidence, no external doc to cite
  - Asset register (data-only, no external policy needed)
  - Matrices (segregation of duties, access-to-PII) — pure grid data
  - Single-topic logs where the log IS the evidence
  - Registers whose columns are all data (ID/name/date/owner/status)
    with no natural external doc column

RULES:
- Use ONLY must_ids from the provided MUSTs list (verbatim; do not invent)
- Be CONSERVATIVE. False positives clutter the catalog with cite
  columns tenants never fill. If unsure, return false.
- Do NOT propose more than 3 cite_columns per pass — real registers
  rarely have more than 1-2 cite columns.
- column_hint MUST be 1-3 tokens. Longer fingerprints never match
  because the workbook tokenizer + subset-match require ALL tokens
  to appear in the header. "Treatment Plan" is 2 tokens; "DPIA
  Report Assessment Document Link" is 5 tokens — the latter would
  never match a real column.
- ANTI-PATTERN: NEVER bind cite to a MUST whose name ends in
  `_date`, `_at`, or `_owner`. Timestamps and owner-names are DATA
  — external documents don't corroborate them. A `Response Doc`
  column should bind to `reg_outcome` (what the doc proves), NOT
  `reg_response_date` (when it landed). Skip the proposal if no
  valid non-date/non-owner MUST is available. (Binding cite to a
  MUST ending in `_id` or `_status` IS allowed — reports can prove
  row identity, certificates can prove completion status.)"""


def _fetch_musts_for_leaf(leaf_id: str) -> list[dict]:
    from neo4j import GraphDatabase
    drv = GraphDatabase.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )
    try:
        with drv.session() as ns:
            rows = ns.run(
                "MATCH (:EvidenceRequirement {id: $lid})-[:MUST_CONTAIN]->(ci) "
                "RETURN ci.id AS id, ci.text AS text ORDER BY id",
                lid=leaf_id,
            ).data()
        return rows
    finally:
        drv.close()


def _sweep_pass(pass_block: dict, target_leaf: str) -> dict:
    """Ask the LLM if this pass needs cite_columns. Returns {status, cites}."""
    musts = _fetch_musts_for_leaf(target_leaf)
    if not musts:
        return {"status": "skipped_no_musts", "cites": []}

    # Existing bindings — LLM should see what's already claimed
    existing = []
    for lst_key in ("required_columns", "optional_columns"):
        for col in pass_block.get(lst_key) or []:
            existing.append(
                f"  {lst_key:16s}  {col.get('fingerprint')} → {col.get('binds_to')}"
            )
    existing_block = "\n".join(existing) if existing else "  (none)"

    musts_block = "\n".join(
        f"  {r['id']}  |  {(r.get('text') or '')[:120]}" for r in musts
    )

    p_user = (
        f"CONTROL: {pass_block.get('target_control', '?')}\n"
        f"LEAF: {target_leaf}\n"
        f"EVIDENCE TYPE: {pass_block.get('target_evidence_type', '?')}\n\n"
        f"EXISTING COLUMN BINDINGS ON THIS PASS:\n{existing_block}\n\n"
        f"MUSTs on this leaf (use these ids VERBATIM):\n{musts_block}\n\n"
        f"Are any of these MUSTs citations to external documents? "
        f"If yes, propose cite_columns entries. Return JSON only."
    )
    resp = llm_call(
        system      = _PROMPT_SYSTEM,
        user        = p_user,
        model       = "gpt-4.1-mini",
        purpose     = "other",
        max_tokens  = 800,
        temperature = 0.1,
        timeout_s   = 60,
        response_format={"type": "json_object"},
    )
    if resp.error:
        return {"status": f"llm_error: {resp.error}", "cites": []}
    try:
        p = json.loads(resp.text or "{}")
    except json.JSONDecodeError as e:
        return {"status": f"json_error: {e}", "cites": []}

    if not p.get("has_cite_columns"):
        return {"status": "no_cite_shape", "reasoning": p.get("reasoning", ""), "cites": []}

    # Validate each proposed cite against real MUSTs + fingerprint hygiene
    real_ids = {r["id"] for r in musts}
    validated: list[dict] = []
    for cb in (p.get("cite_columns") or [])[:3]:  # cap 3
        mid = cb.get("must_id")
        if mid not in real_ids:
            continue
        # Ship 91'.h anti-pattern filter — never bind cite to date/id/owner/
        # status MUSTs. See docs/curation/cite_columns_criterion.md.
        if _cite_bind_disallowed(mid):
            continue
        # Fingerprint must be 1-3 tokens (subset match fails on longer)
        hint = cb.get("column_hint") or []
        if not (1 <= len(hint) <= 3):
            continue
        ck = (cb.get("cite_kind") or "internal_document").strip()
        if ck not in _VALID_CITE_KINDS:
            ck = "internal_document"
        vd = cb.get("verification_days")
        if not isinstance(vd, int) or vd < 30 or vd > 3650:
            vd = 365
        validated.append({
            "column_hint":       hint,
            "must_id":           mid,
            "cite_kind":         ck,
            "verification_days": vd,
        })
    return {
        "status":    "ok" if validated else "no_valid_cites",
        "reasoning": p.get("reasoning", ""),
        "cites":     validated,
    }


def _render_cite_block(cites: list[dict], indent: str = "    ") -> str:
    """Render a cite_columns block with the same indentation as existing lists."""
    lines = [f"{indent}# Ship 90'.a — LLM-proposed cite_columns (curator sweep).",
             f"{indent}cite_columns:"]
    for cb in cites:
        hint = ", ".join(str(t) for t in (cb.get("column_hint") or []))
        lines.append(f"{indent}  - fingerprint: [{hint}]")
        lines.append(f"{indent}    binds_to: \"{cb['must_id']}\"")
        lines.append(f"{indent}    cite_kind: {cb['cite_kind']}")
        lines.append(f"{indent}    verification_days: {cb['verification_days']}")
    return "\n".join(lines)


def _insert_cite_block_in_yaml(yaml_text: str, cites: list[dict]) -> str | None:
    """Text-based insert of a cite_columns block into an existing YAML.

    Preserves comments + formatting. Inserts after the last optional_columns
    entry (or last required_columns entry if no optional). Returns None if
    the structure can't be safely located.
    """
    lines = yaml_text.splitlines()
    # Find the last line that belongs to optional_columns or required_columns
    # by scanning from the top and tracking the last non-blank indented line
    # after we've seen one of those anchors.
    anchor_re = re.compile(r"^(\s+)(optional_columns|required_columns):\s*$")
    last_col_line_idx = -1
    last_col_indent = None
    inside_cols = False
    for i, line in enumerate(lines):
        m = anchor_re.match(line)
        if m:
            inside_cols = True
            last_col_indent = m.group(1) + "  "  # entries indent under the key
            last_col_line_idx = i
            continue
        if inside_cols:
            # Blank line, or a top-level key that's a sibling → end of the block
            stripped = line.rstrip()
            if not stripped:
                # End of block — remember the line before this blank
                inside_cols = False
                continue
            # Determine indent of this line
            m_indent = re.match(r"^(\s*)", line)
            cur_indent = m_indent.group(1) if m_indent else ""
            # If line is indented deeper than the block header → still inside
            if last_col_indent and len(cur_indent) >= len(last_col_indent) - 2:
                last_col_line_idx = i
            else:
                inside_cols = False
    if last_col_line_idx < 0:
        return None
    # Insert cite block after the last column-list line
    block = _render_cite_block(cites, indent="    ")
    new_lines = lines[:last_col_line_idx + 1] + ["", block] + lines[last_col_line_idx + 1:]
    return "\n".join(new_lines) + ("\n" if yaml_text.endswith("\n") else "")


def _pass_has_cite_columns(pass_block: dict) -> bool:
    return bool(pass_block.get("cite_columns"))


def sweep_file(path: Path, dry_run: bool = True) -> dict:
    """Sweep one YAML — returns stats + optional diff."""
    yaml_text = path.read_text()
    try:
        y = yaml.safe_load(yaml_text)
    except Exception as e:
        return {"path": path.name, "status": f"yaml_parse_error: {e}"}
    passes = y.get("passes") or []
    if not passes:
        return {"path": path.name, "status": "no_passes"}
    # Skip if any pass already has cite_columns — idempotent
    if any(_pass_has_cite_columns(p) for p in passes):
        return {"path": path.name, "status": "already_has_cite"}
    # Skip by evidence_type shape
    tets = {p.get("target_evidence_type", "") for p in passes}
    if any(t in _NO_CITE_EVIDENCE_TYPES for t in tets):
        return {"path": path.name, "status": "skipped_by_shape", "evidence_types": list(tets)}

    # For now, only sweep the FIRST pass — most files have a single pass, and
    # multi-pass files (personnel_security_attestation_register, policy_ack) are
    # rare + special-cased.
    p0 = passes[0]
    target_leaf = p0.get("target_evidence_requirement")
    if not target_leaf:
        return {"path": path.name, "status": "no_target_leaf"}

    t0 = time.time()
    result = _sweep_pass(p0, target_leaf)
    dt = round(time.time() - t0, 1)

    out = {
        "path":       path.name,
        "status":     result.get("status"),
        "reasoning":  result.get("reasoning", ""),
        "cites":      result.get("cites", []),
        "elapsed_s":  dt,
        "n_cites":    len(result.get("cites", [])),
        "target":     target_leaf,
    }

    if result.get("cites"):
        new_yaml = _insert_cite_block_in_yaml(yaml_text, result["cites"])
        if new_yaml is None:
            out["status"] = "insert_failed"
            return out
        if not dry_run:
            path.write_text(new_yaml)
            out["applied"] = True
        else:
            # Show a compact diff — just the block we'd add
            out["proposed_block"] = _render_cite_block(result["cites"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", dest="dry_run", action="store_false")
    ap.add_argument("--only", help="Basename (or path) of a single YAML")
    ap.add_argument("--limit", type=int, default=0,
                    help="Sweep at most N files (0 = no limit)")
    args = ap.parse_args()

    mode = "APPLY" if not args.dry_run else "DRY-RUN"
    print(f"─── Ship 90'.a cite_columns sweep — mode={mode} ───\n")

    files: list[Path]
    if args.only:
        p = Path(args.only)
        if not p.is_absolute():
            p = WORKBOOK_MAPPINGS_DIR / p.name
        if not p.exists():
            print(f"File not found: {p}", file=sys.stderr)
            return 2
        files = [p]
    else:
        files = sorted(WORKBOOK_MAPPINGS_DIR.glob("*.yaml"))
    if args.limit:
        files = files[: args.limit]

    print(f"Files to sweep: {len(files)}\n")
    tallies = {"ok": 0, "no_cite_shape": 0, "already_has_cite": 0,
               "skipped_by_shape": 0, "no_target_leaf": 0, "no_passes": 0,
               "no_valid_cites": 0, "insert_failed": 0, "yaml_parse_error": 0,
               "llm_error": 0, "json_error": 0, "skipped_no_musts": 0}
    applied = 0
    for i, path in enumerate(files, 1):
        result = sweep_file(path, dry_run=args.dry_run)
        status = result.get("status", "unknown")
        # Bucket unknown status prefixes into tallies
        for k in tallies:
            if status == k or status.startswith(k):
                tallies[k] += 1
                break
        if result.get("applied"):
            applied += 1
        # Print interesting rows
        if status == "ok":
            marker = "APPLY" if result.get("applied") else "propose"
            print(f"[{i}/{len(files)}] {path.name}")
            print(f"  {marker} n_cites={result['n_cites']} elapsed={result['elapsed_s']}s "
                  f"target={result['target']}")
            if result.get("reasoning"):
                print(f"  reason: {result['reasoning'][:120]}")
            for c in result["cites"]:
                print(f"    - fp={c['column_hint']} → {c['must_id']} "
                      f"[{c['cite_kind']}, {c['verification_days']}d]")
            if args.dry_run and result.get("proposed_block"):
                # Show the block only in dry-run + verbose
                pass
        elif status in ("no_cite_shape",):
            print(f"[{i}/{len(files)}] {path.name}  no_cite_shape  ({result.get('reasoning','')[:70]})")
        else:
            print(f"[{i}/{len(files)}] {path.name}  {status}")

    print("\n─── SUMMARY ───")
    for k, v in tallies.items():
        if v > 0:
            print(f"  {k:20s}  {v}")
    if not args.dry_run:
        print(f"  applied              {applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
