#!/usr/bin/env python3
"""Ship 51'.d — backfill client_documents metadata fields.

Populates three fields deterministically from data already on the row:

  document_title    ← humanized filename (extension stripped, `_` → ` `,
                      whitespace collapsed). NULL/empty rows only.
  standards_cited   ← derived from control_refs via _control_ref_to_standard
                      (same rules the extractor uses).
  topics_detected   ← filename tokens (via workbook_discovery.tokenize)
                      union DOCUMENT_TOPIC_MAP key hits, minus common
                      stop-tokens.

Idempotent + safe:
  - Only touches rows where the specific target field is NULL / empty array
  - Never overwrites a value someone has manually set
  - Dry-run by default; --apply to write
  - Per-row transactions so a mid-run failure leaves the DB consistent
  - Prints a summary at the end

Usage:
    python3 scripts/backfill_client_documents_metadata.py [--tenant UUID] [--apply] [--limit N]

Related:
  rag/intake/posture_writer.py — the write site to wire this into for
    new uploads (deferred; this script covers historical rows).
  rag/intake/extractor.py::_control_ref_to_standard — reused here.
  rag/intake/workbook_discovery.py::tokenize — reused here.
  rag/classifier.py::DOCUMENT_TOPIC_MAP — reused here.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Iterable

import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, "/data/arioncomply")

from rag.intake.extractor import _control_ref_to_standard
from rag.intake.workbook_discovery import tokenize
from rag.classifier import DOCUMENT_TOPIC_MAP


# ── Derivations ──────────────────────────────────────────────────────

_EXT_RE = re.compile(r"\.\w{1,5}$")
_WS_RE  = re.compile(r"\s+")
_STOP_TOKENS = {
    "docx", "xlsx", "xlsm", "pdf", "txt", "md", "csv",
    "the", "and", "for", "our", "your",
    # Common single-token file words that carry no compliance signal
    "copy", "final", "draft", "version", "backup", "old",
}


def _humanize_filename_to_title(filename: str) -> str:
    """`Information Security & Data Management Policy.docx`
       → `Information Security & Data Management Policy`.

    Deliberately gentle — just strips the extension and normalises
    whitespace. Doesn't try to title-case (many filenames are already
    correctly capitalised; forcing title-case would corrupt initialisms
    like DPIA / GDPR / ISMS).
    """
    if not filename:
        return ""
    stem = _EXT_RE.sub("", filename)
    stem = stem.replace("_", " ")
    stem = _WS_RE.sub(" ", stem).strip()
    return stem


def _standards_from_refs(refs: Iterable[str] | None) -> list[str]:
    """control_refs → deduped list of standard_ids. Cross-cutting docs
    naturally emit multiple entries.

    Handles both shapes stored in `client_documents.control_refs`:
      * Composite: `ISO27001:2022:A.5.1`, `GDPR:2016/679:Art.33`
        (what the intake writer emits — always composite for
        posture_writer >= schema_v27).
      * Bare: `A.5.1`, `Art.33` (older paths / manual seeds).
    """
    if not refs:
        return []
    stds = set()
    for r in refs:
        if not r:
            continue
        parts = r.split(":")
        if len(parts) >= 3:
            # Composite `STANDARD:VERSION:REF` — first two segments.
            stds.add(f"{parts[0]}:{parts[1]}")
        else:
            # Bare ref — delegate to the extractor's classifier.
            try:
                stds.add(_control_ref_to_standard(r))
            except Exception:
                pass
    return sorted(stds)


def _topics_from_filename(filename: str) -> list[str]:
    """Filename tokens ∪ DOCUMENT_TOPIC_MAP key hits, minus stop-tokens
    and short noise. Every value ends up lowercase, underscore-separated
    (matches how topics_detected is consumed elsewhere)."""
    if not filename:
        return []
    stem = _EXT_RE.sub("", filename).replace("_", " ")
    raw_tokens = [t.lower() for t in tokenize(stem)]

    topics: set[str] = set()

    # 1. Multi-word key hits from DOCUMENT_TOPIC_MAP ("data protection",
    #    "access control", etc.) — these are the curator-authored topic
    #    surface. Underscore-join so they round-trip cleanly.
    stem_lower = stem.lower()
    for k in DOCUMENT_TOPIC_MAP:
        if k.lower() in stem_lower:
            topics.add(k.replace(" ", "_"))

    # 2. Single significant tokens from the filename itself.
    for t in raw_tokens:
        if len(t) < 4:
            continue
        if t in _STOP_TOKENS:
            continue
        topics.add(t)

    return sorted(topics)


# ── Backfill runner ──────────────────────────────────────────────────

def backfill(dsn: str, tenant_filter: str | None, apply: bool, limit: int | None) -> None:
    conn = psycopg2.connect(dsn)
    conn.autocommit = False

    where = "is_active = TRUE"
    params: list = []
    if tenant_filter:
        where += " AND tenant_id = %s::uuid"
        params.append(tenant_filter)

    limit_clause = f" LIMIT {int(limit)}" if limit else ""

    n_scanned = 0
    n_title_filled = 0
    n_standards_filled = 0
    n_topics_filled = 0
    n_untouched = 0
    n_errors = 0

    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id::text, tenant_id::text, filename,
                       document_title,
                       standards_cited,
                       topics_detected,
                       control_refs
                  FROM client_documents
                 WHERE {where}
              ORDER BY uploaded_at DESC
                {limit_clause}
                """,
                params,
            )
            rows = cur.fetchall()

        print(f"[scan] {len(rows)} active client_documents "
              f"{'(tenant scoped)' if tenant_filter else '(all tenants)'}")
        print()

        for row in rows:
            (row_id, tenant_id, filename, title, stds, topics, refs) = row
            n_scanned += 1

            updates: dict[str, object] = {}

            # 1. document_title — fill if NULL/empty.
            if not title or not title.strip():
                proposed_title = _humanize_filename_to_title(filename)
                if proposed_title:
                    updates["document_title"] = proposed_title

            # 2. standards_cited — fill if NULL or empty array.
            if not stds:
                proposed_stds = _standards_from_refs(refs or [])
                if proposed_stds:
                    updates["standards_cited"] = proposed_stds

            # 3. topics_detected — fill if NULL or empty array.
            if not topics:
                proposed_topics = _topics_from_filename(filename)
                if proposed_topics:
                    updates["topics_detected"] = proposed_topics

            if not updates:
                n_untouched += 1
                continue

            # Report per-row diff.
            parts = []
            for k, v in updates.items():
                short = v if isinstance(v, str) else v[:4] + (["…"] if len(v) > 4 else [])
                parts.append(f"{k}={short!r}")
            marker = "[dry]" if not apply else "[apply]"
            print(f"{marker} {row_id[:8]} {filename[:50]!r}")
            for p in parts:
                print(f"        {p}")

            if apply:
                try:
                    with conn.cursor() as cur2:
                        set_parts = []
                        set_params: list = []
                        for k, v in updates.items():
                            set_parts.append(f"{k} = %s")
                            set_params.append(v)
                        set_params.append(row_id)
                        cur2.execute(
                            f"""
                            UPDATE client_documents
                               SET {', '.join(set_parts)}
                             WHERE id = %s::uuid
                            """,
                            set_params,
                        )
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    n_errors += 1
                    print(f"        ✗ ERROR: {type(e).__name__}: {e}")
                    continue

            if "document_title" in updates:
                n_title_filled += 1
            if "standards_cited" in updates:
                n_standards_filled += 1
            if "topics_detected" in updates:
                n_topics_filled += 1

    finally:
        conn.close()

    print()
    print("=" * 60)
    print(f"Summary  ({'APPLIED' if apply else 'DRY-RUN'})")
    print(f"  scanned:                {n_scanned}")
    print(f"  document_title filled:  {n_title_filled}")
    print(f"  standards_cited filled: {n_standards_filled}")
    print(f"  topics_detected filled: {n_topics_filled}")
    print(f"  untouched (all set):    {n_untouched}")
    if n_errors:
        print(f"  errors:                 {n_errors}")
    if not apply:
        print()
        print("  Re-run with --apply to write the proposed updates.")


def main():
    load_dotenv("/data/arioncomply/.env")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tenant", help="Scope to a single tenant UUID")
    parser.add_argument("--apply", action="store_true", default=False,
                        help="Actually write updates (default: dry-run)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Optional cap on rows scanned")
    args = parser.parse_args()

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    backfill(dsn, args.tenant, args.apply, args.limit)


if __name__ == "__main__":
    main()
