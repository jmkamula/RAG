"""
ArionComply — Bulk Document Uploader

Uploads client documents to the platform:
  1. Reads registered documents from client_documents table
  2. Matches uploaded files by filename or DOCxxx pattern
  3. Runs each through the Phase 5 document pipeline (extract → evaluate → store)
  4. Updates client_documents.storage_path and is_metadata_only = FALSE
  5. Outputs a summary of what was processed

Usage:
  # Dry run — show what would be uploaded
  python3 tools/doc_uploader.py --dir ~/Documents/arion_docs/

  # Live upload
  python3 tools/doc_uploader.py --dir ~/Documents/arion_docs/ --live

  # Upload specific files
  python3 tools/doc_uploader.py --files DOC003_Encryption_Policy.pdf DOC007_Risk_Policy.pdf --live

  # Re-process already uploaded documents
  python3 tools/doc_uploader.py --dir ~/Documents/arion_docs/ --reprocess --live
"""
from __future__ import annotations
import os, sys, argparse, re
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

TENANT_ID = "00000000-0000-0000-0000-000000000001"

# Pattern: DOC001_..., DOC001-..., DOC_001_... etc
DOC_PATTERN = re.compile(r'(DOC\d{3})', re.IGNORECASE)


def find_registered_docs(pg) -> list[dict]:
    """Load all registered documents from client_documents."""
    with pg.cursor() as cur:
        cur.execute("""
            SELECT
                id::text, platform_ref, external_ref,
                document_title, document_type, filename,
                storage_path, is_metadata_only
            FROM client_documents
            WHERE tenant_id = %s
            ORDER BY external_ref
        """, (TENANT_ID,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def match_files(docs: list[dict], directory: Path) -> list[dict]:
    """
    Match uploaded files to registered documents.
    Matching logic (in order of preference):
      1. Exact filename match
      2. DOCxxx prefix match
      3. Title keyword match (fuzzy)
    """
    all_files = {f.name: f for f in directory.iterdir()
                 if f.suffix.lower() in ('.pdf', '.docx', '.doc', '.xlsx', '.md', '.txt')}

    results = []
    for doc in docs:
        matched_file = None
        match_method = None

        # 1. Exact filename match
        if doc["filename"] and doc["filename"] in all_files:
            matched_file  = all_files[doc["filename"]]
            match_method  = "exact"

        # 2. DOCxxx prefix match
        if not matched_file:
            ext_ref = doc["external_ref"] or ""
            for fname, fpath in all_files.items():
                m = DOC_PATTERN.search(fname)
                if m and m.group(1).upper() == ext_ref.upper():
                    matched_file = fpath
                    match_method = "prefix"
                    break

        # 3. Title keyword match (last resort)
        if not matched_file and doc["document_title"]:
            title_words = set(
                w.lower() for w in re.split(r'\W+', doc["document_title"])
                if len(w) > 4
            )
            for fname, fpath in all_files.items():
                fname_words = set(w.lower() for w in re.split(r'\W+', fname))
                if len(title_words & fname_words) >= 2:
                    matched_file = fpath
                    match_method = "title_match"
                    break

        results.append({
            **doc,
            "matched_file": matched_file,
            "match_method": match_method,
        })

    return results


def upload_document(pg, doc: dict, live: bool) -> dict:
    """
    Process a single document through the pipeline.
    Returns result dict with status and details.
    """
    file_path = doc["matched_file"]
    if not file_path or not file_path.exists():
        return {"status": "no_file", "doc": doc}

    if not live:
        return {"status": "dry_run", "doc": doc, "file": str(file_path)}

    try:
        # Import pipeline here to avoid loading at module level
        from rag.document_pipeline import DocumentPipeline

        pipeline = DocumentPipeline(pg_conn=pg)

        result = pipeline.ingest(
            tenant_id   = TENANT_ID,
            file_path   = str(file_path),
            external_ref= doc["external_ref"],
            document_id = doc["id"],
        )

        # Update storage_path and is_metadata_only
        storage_path = str(file_path)
        with pg.cursor() as cur:
            cur.execute("""
                UPDATE client_documents SET
                    storage_path    = %s,
                    is_metadata_only = FALSE,
                    updated_at      = NOW()
                WHERE id = %s
            """, (storage_path, doc["id"]))
        pg.commit()

        return {
            "status":   "uploaded",
            "doc":      doc,
            "file":     str(file_path),
            "result":   result,
        }

    except Exception as e:
        pg.rollback()
        return {
            "status":  "error",
            "doc":     doc,
            "file":    str(file_path),
            "error":   str(e),
        }


def print_summary(matched: list[dict], results: list[dict], live: bool):
    total    = len(matched)
    found    = sum(1 for m in matched if m["matched_file"])
    missing  = total - found
    uploaded = sum(1 for r in results if r["status"] == "uploaded")
    errors   = sum(1 for r in results if r["status"] == "error")
    dry_runs = sum(1 for r in results if r["status"] == "dry_run")

    mode = "LIVE UPLOAD" if live else "DRY RUN"
    print(f"\n{'='*60}")
    print(f"  {mode} — Document Upload Summary")
    print(f"{'='*60}")
    print(f"  Registered documents:  {total}")
    print(f"  Files matched:         {found}")
    print(f"  Files not found:       {missing}")
    if live:
        print(f"  Successfully uploaded: {uploaded}")
        print(f"  Errors:                {errors}")
    else:
        print(f"  Would upload:          {dry_runs}")
    print()

    # Show matches
    print("── MATCHED ──────────────────────────────────────────────────")
    for m in matched:
        if m["matched_file"]:
            method = m.get("match_method", "")
            already = " (already uploaded)" if m["storage_path"] else ""
            print(f"  ✓ {m['external_ref']:8s} [{method:12s}] "
                  f"{m['matched_file'].name[:50]}{already}")
    print()

    print("── NOT MATCHED ──────────────────────────────────────────────")
    for m in matched:
        if not m["matched_file"]:
            print(f"  ✗ {m['external_ref']:8s} {(m['document_title'] or '')[:55]}")
    print()

    if errors:
        print("── ERRORS ───────────────────────────────────────────────────")
        for r in results:
            if r["status"] == "error":
                print(f"  ✗ {r['doc']['external_ref']}: {r['error']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Upload Arion Networks documents")
    parser.add_argument("--dir",       type=Path, help="Directory containing documents")
    parser.add_argument("--files",     nargs="+", help="Specific files to upload")
    parser.add_argument("--live",      action="store_true", help="Actually upload (default: dry run)")
    parser.add_argument("--reprocess", action="store_true",
                        help="Re-process already uploaded documents")
    args = parser.parse_args()

    if not args.dir and not args.files:
        parser.error("Provide --dir or --files")

    from rag.posture_loader import build_pg_conn
    pg = build_pg_conn()

    registered = find_registered_docs(pg)
    print(f"Found {len(registered)} registered documents in database")

    if args.dir:
        if not args.dir.exists():
            print(f"✗ Directory not found: {args.dir}")
            sys.exit(1)
        matched = match_files(registered, args.dir)
        # Skip already uploaded unless --reprocess
        if not args.reprocess:
            for m in matched:
                if m["storage_path"] and m["matched_file"]:
                    m["matched_file"] = None
                    m["match_method"] = "already_uploaded"

    elif args.files:
        file_map = {Path(f).name: Path(f) for f in args.files}
        matched = []
        for doc in registered:
            if doc["filename"] in file_map:
                matched.append({**doc, "matched_file": file_map[doc["filename"]],
                                "match_method": "explicit"})
            else:
                matched.append({**doc, "matched_file": None, "match_method": None})

    results = []
    to_upload = [m for m in matched if m["matched_file"]]

    if not to_upload:
        print("No files to upload.")
    else:
        print(f"\n{'Processing' if args.live else 'Would process'} "
              f"{len(to_upload)} documents...\n")
        for i, doc in enumerate(to_upload, 1):
            fname = doc["matched_file"].name
            print(f"  [{i:2d}/{len(to_upload)}] {doc['external_ref']} — {fname[:50]}")
            result = upload_document(pg, doc, live=args.live)
            results.append(result)
            if result["status"] == "error":
                print(f"         ✗ ERROR: {result['error']}")
            elif result["status"] == "uploaded":
                print(f"         ✓ uploaded")

    # Add no_file results
    for m in matched:
        if not m["matched_file"] and m.get("match_method") != "already_uploaded":
            results.append({"status": "no_file", "doc": m})

    pg.close()
    print_summary(matched, results, live=args.live)


if __name__ == "__main__":
    main()
