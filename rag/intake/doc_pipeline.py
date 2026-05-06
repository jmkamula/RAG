"""
ArionComply — Document Injection Pipeline Orchestrator
Entry point for Path B document intake.

Usage:
  # Process a single file
  python3 tools/doc_pipeline.py --file /path/to/policy.pdf --tenant-id <UUID>

  # Process a directory
  python3 tools/doc_pipeline.py --dir /path/to/docs/ --tenant-id <UUID>

  # Dry run (no DB writes)
  python3 tools/doc_pipeline.py --file policy.pdf --tenant-id <UUID> --dry-run

  # Reprocess a specific upload_id
  python3 tools/doc_pipeline.py --upload-id <UUID> --tenant-id <UUID>
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from rag.intake.models import ExtractionPath, PipelineResult
from rag.intake.readers import read_document
from rag.intake.enricher import enrich
from rag.intake.extractor import extract
from rag.intake.posture_writer import write_findings, update_upload_status

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".txt", ".csv", ".md"}


# =============================================================================
# MAIN PIPELINE
# =============================================================================

class DocumentPipeline:
    """
    Orchestrates all stages of the document injection pipeline.

    Stages:
      1. Read    — extract text and structure from file
      2. Enrich  — classify, detect standard, scan for refs, decide path
      3. Extract — LLM extraction (or structured parse for XLSX/CSV)
      4. Write   — document_findings + posture_controls aggregation
    """

    def __init__(
        self,
        db_url:   str,
        api_key:  str,
        dry_run:  bool = False,
        verbose:  bool = False,
    ):
        self.db_url  = db_url
        self.api_key = api_key
        self.dry_run = dry_run

        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            format  = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt = "%H:%M:%S",
            level   = level,
        )

        self._controls_cache: dict[str, list[dict]] = {}   # standard_id → controls

    def run(
        self,
        file_path: str,
        tenant_id: str,
        upload_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        Process one document.
        Returns PipelineResult with status and counts.
        """
        t_start   = time.time()
        file_path = str(Path(file_path).resolve())
        file_name = Path(file_path).name

        if not Path(file_path).exists():
            return PipelineResult(
                upload_id     = upload_id or "",
                tenant_id     = tenant_id,
                document_name = file_name,
                doc_type      = None,
                standard_ids  = [],
                extraction_path = "failed",
                findings_count  = 0,
                controls_assessed = [],
                controls_updated  = [],
                status = "failed",
                error  = f"File not found: {file_path}",
            )

        upload_id = upload_id or str(uuid.uuid4())
        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Processing: {file_name}")

        try:
            # ── Stage 1: Read ─────────────────────────────────────────────
            logger.info(f"Stage 1: Reading {file_name}")
            doc = read_document(file_path, upload_id=upload_id)

            # ── Stage 2: Enrich ───────────────────────────────────────────
            logger.info(f"Stage 2: Enriching — ~{doc.token_estimate:,} tokens")
            doc = enrich(doc, api_key=self.api_key)

            # ── Manual review branch ──────────────────────────────────────
            if doc.extraction_path == ExtractionPath.MANUAL_REVIEW:
                msg = (
                    f"Document too large ({doc.token_estimate:,} tokens). "
                    f"Split into individual policies before re-uploading."
                )
                logger.warning(f"Manual review required: {file_name} — {msg}")
                if not self.dry_run:
                    self._update_status(upload_id, "requires_manual_review", 0, msg)
                return PipelineResult(
                    upload_id     = upload_id,
                    tenant_id     = tenant_id,
                    document_name = file_name,
                    doc_type      = doc.doc_type,
                    standard_ids  = doc.standard_ids,
                    extraction_path = "manual",
                    findings_count  = 0,
                    controls_assessed = [],
                    controls_updated  = [],
                    status = "manual_review",
                    error  = msg,
                    duration_ms = int((time.time() - t_start) * 1000),
                )

            # ── Stage 3: Get control list from Neo4j ──────────────────────
            logger.info(f"Stage 3: Loading controls for {doc.standard_ids}")
            controls = self._get_controls(doc.standard_ids)

            # ── Stage 3: Extract ──────────────────────────────────────────
            logger.info(
                f"Stage 3: Extracting via {doc.extraction_path.value} path "
                f"({len(controls)} controls available)"
            )
            if not self.dry_run:
                self._update_status(upload_id, "extracting", 0)

            findings = extract(doc, controls, self.api_key)

            logger.info(f"Extracted {len(findings)} findings from {file_name}")

            if self.dry_run:
                self._print_dry_run(findings, doc)
                return PipelineResult(
                    upload_id     = upload_id,
                    tenant_id     = tenant_id,
                    document_name = file_name,
                    doc_type      = doc.doc_type,
                    standard_ids  = doc.standard_ids,
                    extraction_path = doc.extraction_path.value,
                    findings_count  = len(findings),
                    controls_assessed = list({f.control_ref for f in findings}),
                    controls_updated  = [],
                    status      = "dry_run",
                    duration_ms = int((time.time() - t_start) * 1000),
                )

            # ── Stage 4: Write ────────────────────────────────────────────
            logger.info(f"Stage 4: Writing {len(findings)} findings to DB")
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            try:
                summary = write_findings(findings, tenant_id, upload_id, conn)
                conn.commit()   # commit findings - safe even if status update fails
            except Exception as e:
                conn.rollback()
                raise
            finally:
                # Update status in a clean connection - never blocked by prior errors
                try:
                    update_upload_status(
                        upload_id      = upload_id,
                        status         = "extracted",
                        findings_count = len(findings),
                        conn           = conn,
                    )
                    conn.commit()
                except Exception:
                    pass
                conn.close()

            duration_ms = int((time.time() - t_start) * 1000)
            logger.info(
                f"Complete: {file_name} | "
                f"{len(findings)} findings | "
                f"{summary['posture_updated']} updated | "
                f"{summary['posture_created']} created | "
                f"{duration_ms}ms"
            )

            return PipelineResult(
                upload_id     = upload_id,
                tenant_id     = tenant_id,
                document_name = file_name,
                doc_type      = doc.doc_type,
                standard_ids  = doc.standard_ids,
                extraction_path = doc.extraction_path.value,
                findings_count  = len(findings),
                controls_assessed = list({f.control_ref for f in findings}),
                controls_updated  = summary.get("controls_assessed", []),
                status      = "extracted",
                duration_ms = duration_ms,
            )

        except Exception as e:
            logger.error(f"Pipeline failed for {file_name}: {e}", exc_info=True)
            if not self.dry_run:
                try:
                    self._update_status(upload_id, "failed", 0, str(e))
                except Exception:
                    pass
            return PipelineResult(
                upload_id     = upload_id,
                tenant_id     = tenant_id,
                document_name = file_name,
                doc_type      = None,
                standard_ids  = [],
                extraction_path = "failed",
                findings_count  = 0,
                controls_assessed = [],
                controls_updated  = [],
                status  = "failed",
                error   = str(e),
                duration_ms = int((time.time() - t_start) * 1000),
            )

    def run_directory(
        self,
        directory: str,
        tenant_id: str,
    ) -> list[PipelineResult]:
        """Process all supported files in a directory."""
        results = []
        files   = sorted(
            p for p in Path(directory).iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )

        if not files:
            logger.warning(f"No supported files found in {directory}")
            return []

        logger.info(f"Processing {len(files)} files from {directory}")
        for i, file_path in enumerate(files, 1):
            logger.info(f"[{i}/{len(files)}] {file_path.name}")
            result = self.run(str(file_path), tenant_id)
            results.append(result)
            self._print_result(result)

        self._print_summary(results)
        return results

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_controls(self, standard_ids: list[str]) -> list[dict]:
        """
        Load control list from Neo4j for the given standards.
        Results cached per standard_id.
        """
        all_controls = []
        for std in standard_ids:
            if std in self._controls_cache:
                all_controls.extend(self._controls_cache[std])
                continue
            try:
                controls = self._load_controls_from_neo4j(std)
                self._controls_cache[std] = controls
                all_controls.extend(controls)
                logger.info(f"Loaded {len(controls)} controls for {std}")
            except Exception as e:
                logger.warning(f"Could not load controls for {std}: {e}")

        return all_controls

    def _load_controls_from_neo4j(self, standard_id: str) -> list[dict]:
        """Load RequirementNode refs from Neo4j."""
        neo4j_uri  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_pass = os.getenv("NEO4J_PASSWORD", "")

        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
            with driver.session() as s:
                result = s.run("""
                    MATCH (n:RequirementNode)
                    WHERE n.standard_id = $std
                    RETURN n.ref AS ref,
                           n.title AS title,
                           n.standard_id AS standard_id
                    ORDER BY n.ref
                """, std=standard_id)
                controls = [
                    {
                        "ref":         row["ref"],
                        "title":       row["title"] or row["ref"],
                        "standard_id": row["standard_id"],
                    }
                    for row in result
                    if row["ref"]
                ]
            driver.close()
            return controls
        except Exception as e:
            logger.warning(f"Neo4j unavailable: {e} — using empty control list")
            return []

    def _update_status(
        self,
        upload_id: str,
        status:    str,
        count:     int,
        error:     Optional[str] = None,
    ) -> None:
        """Update document_uploads status — best effort."""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_url)
            update_upload_status(upload_id, status, count, conn, error)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Status update failed: {e}")

    def _update_upload_doc_meta(self, upload_id: str, doc, conn) -> None:
        """Update doc_type and standard_id on document_uploads row."""
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE document_uploads
                    SET doc_type    = %s,
                        standard_id = %s,
                        doc_type_confidence = %s
                    WHERE id = %s
                """, (
                    doc.doc_type,
                    doc.standard_ids[0] if doc.standard_ids else None,
                    doc.doc_type_confidence,
                    upload_id,
                ))
        except Exception as e:
            logger.debug(f"Doc meta update failed: {e}")

    def _print_dry_run(self, findings, doc) -> None:
        print(f"\n{'='*60}")
        print(f"DRY RUN — {doc.original_name}")
        print(f"  doc_type:    {doc.doc_type}")
        print(f"  standards:   {doc.standard_ids}")
        print(f"  path:        {doc.extraction_path.value}")
        print(f"  tokens:      ~{doc.token_estimate:,}")
        print(f"  findings:    {len(findings)}")
        print()
        if findings:
            print("  Findings:")
            for f in sorted(findings, key=lambda x: x.control_ref):
                conf = f"[{f.confidence}]"
                evid = f.evidence_text[:60] + "..." if len(f.evidence_text) > 60 else f.evidence_text
                print(f"    {f.control_ref:12s} {f.finding:8s} {conf:8s} {evid}")
        print(f"{'='*60}\n")

    def _print_result(self, r: PipelineResult) -> None:
        status_icon = {"extracted": "✓", "failed": "✗", "manual_review": "△", "dry_run": "○"}.get(r.status, "?")
        print(
            f"  {status_icon} {r.document_name[:45]:45s} "
            f"{r.status:15s} "
            f"{r.findings_count:3d} findings  "
            f"{r.duration_ms:5d}ms"
        )
        if r.error:
            print(f"    ✗ {r.error[:80]}")

    def _print_summary(self, results: list[PipelineResult]) -> None:
        total    = len(results)
        ok       = sum(1 for r in results if r.status == "extracted")
        failed   = sum(1 for r in results if r.status == "failed")
        manual   = sum(1 for r in results if r.status == "manual_review")
        findings = sum(r.findings_count for r in results)

        print(f"\n{'='*60}")
        print(f"PIPELINE SUMMARY")
        print(f"  Documents: {total}  ✓ {ok}  ✗ {failed}  △ manual_review {manual}")
        print(f"  Findings:  {findings}")
        print(f"{'='*60}\n")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ArionComply Document Injection Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/doc_pipeline.py --file policy.pdf --tenant-id <UUID>
  python3 tools/doc_pipeline.py --dir ./docs/ --tenant-id <UUID> --dry-run
  python3 tools/doc_pipeline.py --file report.xlsx --tenant-id <UUID> --verbose
        """,
    )
    parser.add_argument("--file",      help="Path to a single document")
    parser.add_argument("--dir",       help="Directory of documents to process")
    parser.add_argument("--upload-id", help="Existing document_uploads.id to reprocess")
    parser.add_argument("--tenant-id", required=True, help="Tenant UUID")
    parser.add_argument("--dry-run",   action="store_true", help="Parse and extract without writing to DB")
    parser.add_argument("--verbose",   action="store_true", help="Debug logging")
    parser.add_argument("--output",    help="Write results to JSON file")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.error("Provide --file or --dir")

    db_url  = os.getenv("DATABASE_URL")
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not db_url:
        parser.error("DATABASE_URL not set in environment")
    if not api_key:
        parser.error("ANTHROPIC_API_KEY not set in environment")

    pipeline = DocumentPipeline(
        db_url  = db_url,
        api_key = api_key,
        dry_run = args.dry_run,
        verbose = args.verbose,
    )

    if args.file:
        result  = pipeline.run(args.file, args.tenant_id, args.upload_id)
        results = [result]
        pipeline._print_result(result)
    else:
        results = pipeline.run_directory(args.dir, args.tenant_id)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(
                [
                    {
                        "upload_id":    r.upload_id,
                        "document":     r.document_name,
                        "status":       r.status,
                        "doc_type":     r.doc_type,
                        "standards":    r.standard_ids,
                        "path":         r.extraction_path,
                        "findings":     r.findings_count,
                        "duration_ms":  r.duration_ms,
                        "error":        r.error,
                    }
                    for r in results
                ],
                f, indent=2,
            )
        print(f"Results written to {args.output}")

    failed = [r for r in results if r.status == "failed"]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
