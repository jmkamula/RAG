#!/usr/bin/env python3
"""
Ship 11'.e — re-extraction measurement checkpoint.

Dry-run extractor on the 5 documents Ship 10's HITL review covered
(Data Quality Accuracy, DPIA, RoPA, Consent Management, Processor
Operations). Reports finding counts + counter breakdown per doc.
Does NOT touch the DB — pure measurement.

Compares against Ship 10 baseline:
  DQA:          9 findings (4 approve / 5 reject) →  ?
  DPIA:        13 findings (3 approve / 10 reject) → ?
  RoPA:        17 findings (6 approve / 11 reject) → ?
  Consent:     28 findings (16 approve / 12 reject) → ?
  Processor:   30 findings (19 approve / 11 reject) → ?
  TOTAL:       97 findings (48 approve / 49 reject) → ?

Post-Ship-11'.b/c/d, the extraction pipeline SHOULD produce fewer
noisy candidates. Success signal: total_findings drops well below
97, and the shape of drop counters shows content_shape + bridge
filters firing on real content.

Usage:
  PYTHONPATH=/data/arioncomply python3 scripts/measure_ship11_reextraction.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# Suppress Neo4j notification chatter for readability
logging.basicConfig(level=logging.WARNING)
logging.getLogger("neo4j").setLevel(logging.ERROR)
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)


TENANT   = "00000000-0000-0000-0000-000000000001"
DOC_DIR  = Path("/data/uploads") / TENANT

# Ship 10 baseline for comparison
SHIP10_BASELINE = {
    "Data Quality Accuracy Procedure.docx":                        (9,  4, 5),
    "Data Protection Impact Assessment (DPIA) Procedure.docx":     (13, 3, 10),
    "Records of Processing Activities.docx":                       (17, 6, 11),
    "Consent Management Procedure.docx":                           (28, 16, 12),
    "Processor Operations Procedures.docx":                        (30, 19, 11),
}


def _load_upload_paths():
    """Map filename → upload storage path via document_uploads."""
    import psycopg2
    conn = psycopg2.connect(
        host     = os.getenv("PGHOST",     "127.0.0.1"),
        dbname   = os.getenv("PGDATABASE", "arioncomply_compliance"),
        user     = os.getenv("PGUSER",     "arioncomply"),
        password = os.getenv("PGPASSWORD", ""),
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT filename, storage_path, id::text
                FROM document_uploads
                WHERE tenant_id = %s::uuid
                  AND filename = ANY(%s)
                """,
                (TENANT, list(SHIP10_BASELINE.keys())),
            )
            return {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    finally:
        conn.close()


def _extract_one(filename, storage_path, upload_id):
    """Read → enrich → extract. Returns (findings, metrics)."""
    from rag.intake.readers  import read_document
    from rag.intake.enricher import enrich
    from rag.intake.extractor import extract

    doc = read_document(storage_path, upload_id=upload_id,
                        original_filename=filename)

    # Enricher populates doc_type, standards, topic_tokens etc.
    api_key = os.getenv("OPENAI_API_KEY", "")
    try:
        enrich(doc, api_key)
    except Exception as e:
        print(f"    enrich warning: {e}")

    # Build controls list for the doc's declared standards (or all-standards
    # fallback). Reuse the pipeline's helper via a stub instance.
    from rag.intake.doc_pipeline import DocumentPipeline
    pipeline = DocumentPipeline(
        db_url=f"host={os.getenv('PGHOST', '127.0.0.1')} dbname=arioncomply_compliance user=arioncomply",
        api_key=api_key,
    )
    controls = []
    stds = doc.standard_ids or ["ISO27001:2022"]
    seen = set()
    for std in stds:
        for c in pipeline._load_controls_from_neo4j(std):
            key = (c["ref"], c["standard_id"])
            if key not in seen:
                seen.add(key)
                controls.append(c)

    findings = extract(doc, controls, api_key)

    return findings, doc.extraction_metrics


def main():
    print("─" * 72)
    print(" Ship 11'.e — re-extraction measurement")
    print("─" * 72)

    paths = _load_upload_paths()
    total_new = 0
    total_baseline = sum(v[0] for v in SHIP10_BASELINE.values())
    per_doc_rows = []

    for filename in SHIP10_BASELINE:
        entry = paths.get(filename)
        if not entry:
            print(f"\n  ⚠ {filename}: no upload record — skipped")
            continue
        storage_path, upload_id = entry
        if not Path(storage_path).exists():
            print(f"\n  ⚠ {filename}: file missing at {storage_path} — skipped")
            continue

        print(f"\n  → {filename}")
        try:
            findings, metrics = _extract_one(filename, storage_path, upload_id)
        except Exception as e:
            print(f"    ✗ extract failed: {type(e).__name__}: {e}")
            continue

        baseline_total, baseline_ok, baseline_reject = SHIP10_BASELINE[filename]

        # Extract drop counters
        drops = {
            k: v for k, v in metrics.items()
            if k.startswith("dropped_") or k.startswith("critic_")
        }

        n_findings = len(findings)
        total_new += n_findings

        # Breakdown by inference_source
        by_source = {}
        for f in findings:
            src = getattr(f, "inference_source", None) or "extracted"
            by_source[src] = by_source.get(src, 0) + 1

        # Content-shape drops from the metrics
        cs_drops = metrics.get("dropped_content_shape", 0)

        print(f"    Ship 10 baseline:  {baseline_total} findings "
              f"({baseline_ok} approve / {baseline_reject} reject)")
        print(f"    Ship 11 re-extract: {n_findings} findings")
        print(f"    by source: {by_source}")
        if cs_drops:
            print(f"    content-shape dropped: {cs_drops}")
        interesting = {k: v for k, v in drops.items() if v}
        if interesting:
            print(f"    drop counters: {interesting}")

        per_doc_rows.append((
            filename, baseline_total, baseline_reject, n_findings, cs_drops,
        ))

    # Summary
    print("\n" + "─" * 72)
    print(" SUMMARY")
    print("─" * 72)
    print(f"  {'doc':56s}  {'ship10':>8s}  {'ship11':>8s}  {'delta':>8s}")
    for filename, base_total, base_reject, new_total, _ in per_doc_rows:
        delta = new_total - base_total
        arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "=")
        print(f"  {filename:56s}  {base_total:>8d}  {new_total:>8d}  "
              f"{delta:>+7d} {arrow}")
    print(f"  {'TOTAL':56s}  {total_baseline:>8d}  {total_new:>8d}  "
          f"{(total_new - total_baseline):>+7d}")

    if total_baseline > 0:
        pct = (total_new / total_baseline) * 100
        print(f"\n  Ship 11 produces {pct:.0f}% of Ship 10's finding volume.")
        # Ship 10 had 49/97 = 51% rejection rate. If Ship 11 drops findings
        # that Ship 10 would have rejected, the new-total ≈ baseline_approves.
        approves_10 = sum(v[1] for v in SHIP10_BASELINE.values())
        print(f"  Ship 10 approves: {approves_10} of {total_baseline} "
              f"= {approves_10 * 100 // total_baseline}% approve rate")
        print(f"  If Ship 11 filters preserved approves + dropped rejects,")
        print(f"    ideal new-total = {approves_10} (100% approve rate downstream)")


if __name__ == "__main__":
    sys.exit(main() or 0)
