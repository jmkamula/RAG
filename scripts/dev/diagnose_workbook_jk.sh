#!/usr/bin/env bash
#
# scripts/dev/diagnose_workbook_jk.sh
#
# 2026-09-08 diagnostic for the "jk" workbook returning 0 findings.
#
# Prints:
#   1. findings_count on both recent workbook uploads (jk vs pre-jk
#      shows whether earlier one also produced 0 or if only jk is broken)
#   2. sheet-by-sheet inventory of the jk file: name, row count, first
#      6 header cells (so we can see if column names differ from what
#      the mapping YAMLs expect)
#   3. discover_workbook proposals against those sheets (0 = header
#      mismatch OR meta missing; N>0 with 0 findings written = write-
#      path issue)
#
# Runs read-only against local Postgres + reads uploaded xlsm files.
# No mutations. Safe to re-run.

set -u
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

# ── 1. Both workbook uploads' status ──────────────────────────────
echo "=== 1. Both workbook uploads: extraction result ==="
sudo -u postgres psql -d arioncomply_compliance -c "
SELECT LEFT(filename, 55) AS filename,
       LEFT(id::text, 8) AS id_prefix,
       extraction_path,
       extraction_status,
       findings_count,
       uploaded_at::date AS uploaded
  FROM document_uploads
 WHERE filename ILIKE '%workbook%'
 ORDER BY uploaded_at DESC LIMIT 5;"

# ── 2 + 3. Discover against the jk file directly ──────────────────
echo
echo "=== 2+3. Discovery diagnostic against jk file ==="
PYTHONPATH=. python3 <<'PY'
import openpyxl
import sys
import psycopg2
import os
from pathlib import Path

# Ship 118'.d pattern — load .env via python-dotenv (the operator's
# arionops shell doesn't have ARION_OWNER_PW unless the .env is
# sourced, and bash `source .env` chokes on values with unsafe chars).
try:
    from dotenv import load_dotenv
    load_dotenv('/data/arioncomply/.env')
except ImportError:
    pass

# Look up the jk upload id + storage path from Postgres
conn = psycopg2.connect(
    host="127.0.0.1", dbname="arioncomply_compliance",
    user="arioncomply", password=os.environ.get("ARION_OWNER_PW", ""),
)
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, tenant_id, filename, storage_path
              FROM document_uploads
             WHERE filename ILIKE %s
             ORDER BY uploaded_at DESC LIMIT 1
        """, ('%jk%',))
        row = cur.fetchone()
finally:
    conn.close()

if not row:
    print("No 'jk' upload row found in document_uploads.")
    sys.exit(0)

upload_id, tenant_id, filename, storage_path = row
print(f"Upload: {filename}")
print(f"  id:           {upload_id}")
print(f"  tenant_id:    {tenant_id}")
print(f"  storage_path: {storage_path}")

# The storage_path column may be NULL if the app derives the path;
# use the observed pattern uploads/<tenant>/<upload_id>.xlsm
candidates = []
if storage_path:
    candidates.append(Path(storage_path))
candidates.extend([
    Path(f"/data/arioncomply/uploads/{tenant_id}/{upload_id}.xlsm"),
    Path(f"/data/arioncomply/uploads/{tenant_id}/{upload_id}.xlsx"),
])

xlsm = next((p for p in candidates if p.exists()), None)
if not xlsm:
    print(f"\nERROR: file not found. Tried:")
    for c in candidates:
        print(f"  {c}")
    sys.exit(1)
print(f"  resolved:     {xlsm} ({xlsm.stat().st_size} bytes)")

# ── Sheet inventory ──
wb = openpyxl.load_workbook(xlsm, keep_vba=True, data_only=True, read_only=True)
print(f"\nSheets ({len(wb.sheetnames)}):")
rows_per_sheet = {}
for name in wb.sheetnames:
    ws = wb[name]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    rows_per_sheet[name] = rows
    header = rows[0] if rows else []
    header_preview = [(str(h)[:40] if h is not None else "None") for h in header[:8]]
    print(f"  {name!r:35}: {len(rows):5d} rows; headers[:8] = {header_preview}")
wb.close()

# ── Discovery ──
# discover_workbook returns list[SheetProposal], each with:
#   sheet, mapping_id, confidence, header_row, headers[], row_count,
#   passes=list[PassProposal], warnings, anchor_decisions
# PassProposal has: pass_name, target_control, matched_columns={must_id: col_header},
#   satisfied/partial/missing (MUST ids), freshness_column, cite_bindings
from rag.intake.workbook_discovery import discover_workbook
try:
    proposals = discover_workbook(rows_per_sheet)
    print(f"\ndiscover_workbook returned {len(proposals)} SheetProposal(s)")
    empty_sheets = 0
    for i, sp in enumerate(proposals):
        total_matched = sum(len(p.matched_columns) for p in sp.passes)
        total_satisfied = sum(len(p.satisfied) for p in sp.passes)
        if total_matched == 0 and total_satisfied == 0:
            empty_sheets += 1
            continue
        # Only print non-empty proposals
        print(f"\n[{i}] sheet={sp.sheet!r} mapping={sp.mapping_id}")
        print(f"     confidence={sp.confidence:.2f} row_count={sp.row_count} passes={len(sp.passes)}")
        for j, p in enumerate(sp.passes[:3]):
            print(f"     pass[{j}] name={p.pass_name}")
            print(f"       matched_columns ({len(p.matched_columns)}): {dict(list(p.matched_columns.items())[:5])}")
            print(f"       satisfied ({len(p.satisfied)}): {p.satisfied[:5]}")
            print(f"       partial ({len(p.partial)}): {p.partial[:5]}")
            print(f"       warnings: {p.warnings[:3]}")
    print(f"\nSummary: {len(proposals)} proposals total, {empty_sheets} with 0 matched_columns + 0 satisfied")

    # Now run persist_proposals in a rollback-only session to see what it would write
    print(f"\n=== persist_proposals dry-run (rollback after) ===")
    from rag.intake.workbook_persistence import persist_proposals
    from uuid import UUID
    conn2 = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.environ.get("ARION_OWNER_PW", ""),
    )
    try:
        pass_count, findings_count = persist_proposals(
            conn2,
            UUID(str(tenant_id)),
            str(xlsm),
            UUID(str(upload_id)),
            proposals,
        )
        print(f"  persist_proposals would write: {pass_count} passes, {findings_count} findings")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        conn2.rollback()
        conn2.close()
except Exception as e:
    import traceback
    traceback.print_exc()
PY
