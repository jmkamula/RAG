#!/usr/bin/env python3
"""Ship 86'.a — LLM curator for `db/workbook_mappings/*.yaml`.

Extends Ship 80'.b/83'.b's fingerprint YAML curator pattern to
workbook_mappings. Motivation from Ship 85'.b measurement: extract-time
LLM path on multi-sheet workbooks REGRESSED F1 (-4.89pp aggregate)
because LLM can't disambiguate "this table IS the target register" from
"this table is a related register" from markdown alone. Build-time
LLM curator sidesteps this — the curator sees ONE sheet at a time with
full name + column + sample context, and authors a durable YAML that
workbook_persistence (100% precision on templated) then runs
deterministically at extract-time.

Model: gpt-4.1-mini (matches Ship 80'.b/83'.b — no Claude lock).

Flow per unmapped sheet:
  1. Extract sheet_name + column headers + 2 sample rows from
     doc.extraction_metrics["structured_sheets"] (Ship 85'.a output)
  2. Fetch Neo4j MUST catalog for the tenant's enrolled standards
  3. LLM authors `sheet_name_fingerprints` + `passes[].target_control`
     + `passes[].target_evidence_requirement` + column bindings
  4. Write YAML to db/workbook_mappings/ with `# LLM-authored by Ship 86'.a`
     header (preserves audit trail per Ship 83' Lesson 72)

Usage:
    # Single sheet by name (on the ISO workbook fixture)
    PYTHONPATH=. python3 scripts/ship86a_workbook_curator.py \\
        --workbook "ISO 27001 workbook Arion Networks.xlsm" \\
        --sheet "Risk Comms Matrix"

    # Batch — all unmapped sheets on a workbook
    PYTHONPATH=. python3 scripts/ship86a_workbook_curator.py \\
        --workbook "ISO 27001 workbook Arion Networks.xlsm" \\
        --unmapped-only

    # Dry-run (print yaml, don't write)
    ... --dry-run

Cost estimate: ~$0.02 per sheet via gpt-4.1-mini (single call per sheet
with catalog context). 37 sheets on ISO workbook = ~$0.75 total.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv("/data/arioncomply/.env")

REPO = Path("/data/arioncomply")
sys.path.insert(0, str(REPO))

from rag.llm_client import call as llm_call

WORKBOOK_MAPPINGS_DIR = REPO / "db" / "workbook_mappings"
TENANT_ID = "00000000-0000-0000-0000-000000000001"


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _load_structured_sheets(workbook_path: str, workbook_name: str) -> list[dict]:
    """Reuse Ship 85'.a's `_partition_xlsx_via_unstructured` to get
    per-sheet structure."""
    from rag.intake.readers import read_document
    doc = read_document(file_path=workbook_path, original_filename=workbook_name)
    return doc.extraction_metrics.get("structured_sheets") or []


def _identify_mapped_sheets(structured_sheets: list[dict]) -> tuple[set[str], set[str]]:
    """Split sheets into (mapped, unmapped) by checking existing
    workbook_mappings/*.yaml sheet_name_fingerprints."""
    import yaml
    mapped = set()
    unmapped = set()
    # Load all existing sheet fingerprints
    all_fingerprints: list[tuple[str, list[list[str]]]] = []
    for yf in sorted(WORKBOOK_MAPPINGS_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(yf.read_text())
            if not data:
                continue
            fps = []
            for e in data.get("sheet_name_fingerprints", []) or []:
                toks = e.get("tokens") or []
                if toks:
                    fps.append([str(t).lower() for t in toks])
            if fps:
                all_fingerprints.append((yf.stem, fps))
        except Exception:
            continue

    for s in structured_sheets:
        sheet_name = s["sheet_name"]
        tokens_in_name = set(re.findall(r"[a-z]+", sheet_name.lower()))
        matched = False
        for _mapping_id, fps in all_fingerprints:
            for fp_tokens in fps:
                if all(t in tokens_in_name for t in fp_tokens):
                    matched = True
                    break
            if matched:
                break
        if matched:
            mapped.add(sheet_name)
        else:
            unmapped.add(sheet_name)
    return mapped, unmapped


def _fetch_leaf_catalog_summary(standard_prefixes: list[str] = None) -> list[dict]:
    """Get {control_ref, leaf_id, title} for all leaves in enrolled standards.
    Trimmed to just the shape a curator needs to pick a target."""
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    try:
        with driver.session() as s:
            cypher = """
            MATCH (er:EvidenceRequirement)
            WHERE er.standard_id IN ['ISO27001:2022', 'ISO27701:2019', 'GDPR:2016/679']
            RETURN er.id AS leaf_id, er.control_ref AS control_ref,
                   er.standard_id AS standard_id, er.title AS title,
                   er.evidence_type AS evidence_type
            ORDER BY control_ref
            """
            return s.run(cypher).data()
    finally:
        driver.close()


_PASS1_SYSTEM = """You are a compliance auditor identifying which evidence-requirement leaf a workbook sheet represents.

Return strict JSON:
{
  "target_control":  "A.5.9",
  "target_evidence_requirement": "req:A.5.9:asset_inventory",
  "target_evidence_type":        "asset_register",
  "sheet_name_fingerprints": [["asset", "register"], ["asset", "inventory"], ...],
  "confidence": "high|medium|low",
  "rationale":  "one-sentence reason"
}

Rules:
- Choose the SINGLE best-matching leaf from the catalog based on sheet name + columns + sample data
- `sheet_name_fingerprints`: 3-5 token-list variants a user might name this sheet
- Return "not_applicable" as target_control if this sheet is NOT a compliance artefact (TOC, Instructions, Formulas)"""


_PASS2_SYSTEM = """You are a compliance auditor binding columns of a workbook sheet to specific MUSTs of one evidence-requirement leaf.

Return strict JSON:
{
  "column_bindings": [
    {"column_hint": ["employee", "id"], "must_id": "item:7.2:owner", "required": true},
    {"column_hint": ["role"],           "must_id": "item:7.2:required_competence", "required": true},
    ...
  ]
}

Rules:
- Use ONLY must_ids from the provided MUSTs list (verbatim; do not invent)
- column_hint: 1-3 lowercase tokens that would appear in the column header
- required=true if the column MUST be present for the sheet to count as evidence
- Skip columns that don't map to any provided MUST (rather than force a bad binding)"""


def curate_sheet(
    sheet_data:   dict,
    catalog:      list[dict],
    dry_run:      bool = True,
    max_catalog_entries: int = 300,
) -> dict:
    """LLM-author a workbook_mappings YAML for one sheet.

    Returns dict with {stats, yaml_text, output_path}. On dry_run,
    yaml_text is populated but nothing written.
    """
    sheet_name = sheet_data["sheet_name"]
    # Extract column headers from first table's HTML (first row)
    headers = []
    sample_rows = []
    if sheet_data.get("tables_html"):
        html = sheet_data["tables_html"][0].get("html", "")
        # naive parse — grab all <tr>...</tr> segments
        rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
        for i, r in enumerate(rows[:4]):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if i == 0:
                headers = cells
            else:
                sample_rows.append(cells)

    # Format catalog for LLM — cap at max_catalog_entries to fit context
    catalog_lines = []
    for r in catalog[:max_catalog_entries]:
        title = (r.get("title") or "")[:60]
        etype = r.get("evidence_type") or ""
        catalog_lines.append(
            f"  {r['leaf_id']}  |  {r['control_ref']} ({r['standard_id']})  |  "
            f"[{etype}]  {title}"
        )

    # ── Pass 1: pick target leaf + sheet fingerprints ──────────────
    p1_user = (
        f"SHEET NAME: {sheet_name}\n\n"
        f"COLUMN HEADERS: {' | '.join(headers) if headers else '(no headers found)'}\n\n"
        f"SAMPLE ROWS (up to 3):\n" +
        ("\n".join(f"  {' | '.join(r[:15])}" for r in sample_rows) if sample_rows else "  (no data)") +
        f"\n\nCATALOG (subset — {len(catalog_lines)} of {len(catalog)} total):\n" +
        "\n".join(catalog_lines) +
        f"\n\nPick the target leaf. Return JSON only."
    )
    t0 = time.time()
    resp = llm_call(
        system      = _PASS1_SYSTEM,
        user        = p1_user,
        model       = "gpt-4.1-mini",
        purpose     = "other",
        max_tokens  = 1000,
        temperature = 0.2,
        timeout_s   = 60,
        response_format={"type": "json_object"},
    )
    if resp.error:
        return {"error": f"Pass 1: {resp.error}", "sheet_name": sheet_name}
    try:
        p1 = json.loads(resp.text or "{}")
    except json.JSONDecodeError as e:
        return {"error": f"Pass 1 JSON parse: {e}", "sheet_name": sheet_name}
    target_leaf = p1.get("target_evidence_requirement", "")

    # ── Pass 2: bind columns to MUSTs (if leaf is a real compliance target) ─
    column_bindings: list = []
    if target_leaf and target_leaf != "not_applicable":
        # Fetch real MUSTs for the target leaf
        try:
            from neo4j import GraphDatabase
            drv = GraphDatabase.driver(
                os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
            )
            with drv.session() as ns:
                musts_rows = ns.run(
                    "MATCH (:EvidenceRequirement {id: $lid})-[:MUST_CONTAIN]->(ci) "
                    "RETURN ci.id AS id, ci.text AS text ORDER BY id",
                    lid=target_leaf,
                ).data()
            drv.close()
        except Exception as e:
            return {"error": f"Pass 2 Neo4j: {e}", "sheet_name": sheet_name}

        if musts_rows:
            musts_block = "\n".join(
                f"  {r['id']}  |  {(r.get('text') or '')[:120]}"
                for r in musts_rows
            )
            p2_user = (
                f"SHEET NAME: {sheet_name}\n"
                f"TARGET LEAF: {target_leaf}\n\n"
                f"COLUMN HEADERS: {' | '.join(headers) if headers else '(none)'}\n\n"
                f"SAMPLE ROWS:\n" +
                ("\n".join(f"  {' | '.join(r[:15])}" for r in sample_rows) if sample_rows else "  (no data)") +
                f"\n\nMUSTs on this leaf (use these ids VERBATIM):\n{musts_block}"
                f"\n\nBind columns to MUSTs. Return JSON only."
            )
            resp2 = llm_call(
                system      = _PASS2_SYSTEM,
                user        = p2_user,
                model       = "gpt-4.1-mini",
                purpose     = "other",
                max_tokens  = 1500,
                temperature = 0.2,
                timeout_s   = 60,
                response_format={"type": "json_object"},
            )
            if resp2.error:
                return {"error": f"Pass 2: {resp2.error}", "sheet_name": sheet_name}
            try:
                p2 = json.loads(resp2.text or "{}")
            except json.JSONDecodeError as e:
                return {"error": f"Pass 2 JSON parse: {e}", "sheet_name": sheet_name}
            # Validate bindings against real MUST ids
            real_must_ids = {r["id"] for r in musts_rows}
            for cb in (p2.get("column_bindings") or []):
                mid = cb.get("must_id")
                if mid in real_must_ids:
                    column_bindings.append(cb)

    dt = time.time() - t0
    curated = {
        **p1,
        "column_bindings": column_bindings,
    }

    # Render YAML in canonical shape
    slug = _slugify(sheet_name)
    yaml_lines = [
        f"# Workbook mapping: {sheet_name} sheet",
        f"# LLM-authored by Ship 86'.a (curator sweep 2026-08-19).",
        f"# Confidence: {curated.get('confidence', 'medium')}. Rationale: {curated.get('rationale', '')[:150]}",
        "",
        "schema_version: 1",
        f"mapping_id: workbook.llm_curated.{slug}",
        "",
        "# ── Sheet identification ─────────────────────────────────────────────",
        "sheet_name_fingerprints:",
    ]
    for fp in curated.get("sheet_name_fingerprints", []) or []:
        yaml_lines.append(f"  - tokens: [{', '.join(str(t) for t in fp)}]")
    yaml_lines.append("")
    yaml_lines.append("header_row_hints: [1, 2, 3]")
    yaml_lines.append("min_data_rows: 1")
    yaml_lines.append("")
    yaml_lines.append("# ── Extraction passes ─────────────────────────────────────────────────")
    yaml_lines.append("passes:")
    yaml_lines.append("")
    yaml_lines.append("  - pass_name: register")
    yaml_lines.append(f"    target_control: {curated.get('target_control', 'UNKNOWN')}")
    yaml_lines.append(f"    target_evidence_requirement: \"{curated.get('target_evidence_requirement', '')}\"")
    yaml_lines.append(f"    target_evidence_type: {curated.get('target_evidence_type', 'register')}")
    yaml_lines.append("")
    yaml_lines.append("    column_bindings:")
    for cb in curated.get("column_bindings", []) or []:
        hint = cb.get("column_hint") or []
        must_id = cb.get("must_id") or ""
        required = cb.get("required", False)
        yaml_lines.append(f"      - column_fingerprint: [{', '.join(str(t) for t in hint)}]")
        yaml_lines.append(f"        binds_to_must_id: \"{must_id}\"")
        yaml_lines.append(f"        required: {str(required).lower()}")
    yaml_lines.append("")

    yaml_text = "\n".join(yaml_lines)
    stats = {
        "sheet_name":      sheet_name,
        "elapsed_s":       round(dt, 1),
        "confidence":      curated.get("confidence"),
        "target_leaf":     curated.get("target_evidence_requirement"),
        "n_fingerprints":  len(curated.get("sheet_name_fingerprints", []) or []),
        "n_column_bindings": len(curated.get("column_bindings", []) or []),
    }

    output_path = None
    if not dry_run:
        output_path = WORKBOOK_MAPPINGS_DIR / f"ship86_{slug}.yaml"
        output_path.write_text(yaml_text)
        stats["output_path"] = str(output_path.name)

    return {"stats": stats, "yaml_text": yaml_text, "output_path": output_path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True, help="Filename of workbook to curate")
    ap.add_argument("--sheet", help="Single sheet name to curate")
    ap.add_argument("--unmapped-only", action="store_true",
                    help="Curate all sheets on workbook that lack existing mapping")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Resolve workbook path from tenant uploads
    import psycopg2
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (TENANT_ID,))
        cur.execute(
            "SELECT filename, storage_path FROM document_uploads "
            "WHERE tenant_id = %s::uuid AND filename = %s LIMIT 1",
            (TENANT_ID, args.workbook),
        )
        row = cur.fetchone()
    conn.close()
    if not row or not row[1]:
        print(f"Workbook not found on tenant: {args.workbook}", file=sys.stderr)
        sys.exit(2)
    _, storage_path = row

    print(f"Loading structured sheets from {storage_path}...")
    structured = _load_structured_sheets(storage_path, args.workbook)
    print(f"  {len(structured)} sheets detected")

    mapped, unmapped = _identify_mapped_sheets(structured)
    print(f"  {len(mapped)} sheets have existing mappings")
    print(f"  {len(unmapped)} sheets are UNMAPPED")

    # Select which sheets to curate
    to_curate = []
    if args.sheet:
        to_curate = [s for s in structured if s["sheet_name"] == args.sheet]
        if not to_curate:
            print(f"  no such sheet: {args.sheet}", file=sys.stderr)
            sys.exit(2)
    elif args.unmapped_only:
        to_curate = [s for s in structured if s["sheet_name"] in unmapped]
    else:
        # Default: all sheets (mostly for testing)
        to_curate = structured

    print(f"\nCurating {len(to_curate)} sheet(s) — model=gpt-4.1-mini, dry_run={args.dry_run}")
    print()

    catalog = _fetch_leaf_catalog_summary()
    print(f"Loaded catalog: {len(catalog)} leaves\n")

    total_ok = 0
    total_err = 0
    for i, s in enumerate(to_curate, 1):
        print(f"[{i}/{len(to_curate)}] {s['sheet_name']}")
        result = curate_sheet(s, catalog, dry_run=args.dry_run)
        if "error" in result:
            print(f"  ERROR: {result['error']}")
            total_err += 1
            continue
        stats = result["stats"]
        print(f"  target={stats['target_leaf']} conf={stats['confidence']} "
              f"fps={stats['n_fingerprints']} binds={stats['n_column_bindings']} "
              f"elapsed={stats['elapsed_s']}s")
        if stats.get("output_path"):
            print(f"  wrote → {stats['output_path']}")
        total_ok += 1

    print(f"\n=== DONE ===")
    print(f"  Curated: {total_ok}")
    print(f"  Errors:  {total_err}")


if __name__ == "__main__":
    main()
