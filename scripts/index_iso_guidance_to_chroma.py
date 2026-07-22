"""
Ship 13'.d (2026-07-22) — index ISO 27003:2017 + ISO 27005:2022
guidance standards into dedicated Chroma collections.

Ship 13'.b/'.c authored per-leaf enrichment paragraphs on 40
27001 leaves. This script makes the FULL guidance texts
retrievable, so future queries about implementation methodology
can surface guidance sections the enrichment paragraphs
condensed or omitted.

Chunking strategy:
  - Split each extracted text at top-level §X.Y anchors
  - Each § becomes one Chroma doc (title header + body)
  - Boilerplate lines (copyright, license notices, page numbers)
    are stripped
  - Only sections in chapters 4-10 (real content) are indexed;
    front matter (scope, definitions, foreword) skipped

Collections:
  iso27003_2017  — created if absent
  iso27005_2022  — created if absent
  (iso27004_* was deferred; edition mismatch — see 13'.a memo)

Embedding: text-embedding-3-large (rag/embedding_config.py).

Idempotent: uses `col.upsert()`, so re-running refreshes without
duplicates. Sample retrieval query is printed at end for
verification.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/index_iso_guidance_to_chroma.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from dotenv import load_dotenv

from rag.embedding_config import EMBED_MODEL_STANDARD
from vector.indexer import OpenAIEmbeddingFunction

load_dotenv(str(Path(__file__).parent.parent / ".env"))


COL_27003 = "iso27003_2017"
COL_27004 = "iso27004_2016"
COL_27005 = "iso27005_2022"

_TEXT_27003 = Path("/data/arioncomply/private/iso27003_2017.txt")
_TEXT_27004 = Path("/data/arioncomply/private/iso27004_2016.txt")
_TEXT_27005 = Path("/data/arioncomply/private/iso27005_2022.txt")


# ── Section anchor regex ───────────────────────────────────────
# Matches lines like:
#   `4.1 Understanding the organization and its context`
#   `6.1.2\tInformation security risk assessment`
#   `7.5.1    General`
# but not:
#   `4.1.2 Sub-item text …`  when the line ends with a period /
#     continues (heuristic — we allow only short heading titles)
_SEC_HDR = re.compile(
    r"^([0-9]+(?:\.[0-9]+){0,3})[\s ​]+(.{2,120})$"
)

# ── Lines to strip from chunk bodies ───────────────────────────
_STRIP_PATTERNS = [
    re.compile(r"©\s*ISO/IEC.*"),                    # copyright lines
    re.compile(r"^ISO/IEC 27[0-9]{3}:[0-9]{4}\(E\)"),  # header/footer
    re.compile(r"Licensed to.*"),                     # license watermark
    re.compile(r"DGN Store Order.*"),
    re.compile(r"Single user licence only.*"),
    re.compile(r"^\s*\d+\s*﻿?\s*$"),                  # bare page numbers
    re.compile(r"^\s*[a-z]\)?\s*$"),                  # dangling list markers
    re.compile(r"^\s*﻿\s*$"),                         # BOM-only lines
]


def _is_content_section(section_ref: str) -> bool:
    """Skip front-matter — chapters 1-3 are scope/refs/definitions."""
    try:
        top = int(section_ref.split(".", 1)[0])
    except ValueError:
        return False
    return top >= 4


def _clean_line(line: str) -> str:
    stripped = line.rstrip("\n\r")
    for pat in _STRIP_PATTERNS:
        if pat.match(stripped) or pat.search(stripped):
            return ""
    return stripped


def _looks_like_header(line: str) -> bool:
    """Filter out false positive '§X.Y' matches that are actually
    body sentences beginning with a number. Real headers are
    short, don't end in punctuation, and don't contain mid-
    sentence punctuation (period+space+letter, comma+space+letter)."""
    stripped = line.strip()
    if stripped.endswith((".", ",", ";", ":", "—", "-")):
        return False
    if len(stripped) > 130:
        return False
    # Reject body lines like "6.1.1 (general). Risks that fall …"
    if re.search(r"[.,]\s+[A-Za-z]", stripped):
        return False
    return True


def chunk_standard(text_path: Path, standard_id: str) -> list[dict]:
    """Read `text_path`, split at top-level § headers, return a
    list of chunks with metadata."""
    if not text_path.exists():
        raise FileNotFoundError(f"Text file missing: {text_path}")

    raw_lines = text_path.read_text(encoding="utf-8").splitlines()

    chunks: list[dict] = []
    current_ref: str | None = None
    current_title: str = ""
    current_body: list[str] = []

    def _emit_current():
        if current_ref and _is_content_section(current_ref):
            body = "\n".join(l for l in current_body if l.strip()).strip()
            if body:
                doc_text = f"{standard_id} §{current_ref} {current_title}\n\n{body}"
                chunks.append({
                    "id":       f"{standard_id}:§{current_ref}",
                    "ref":      current_ref,
                    "title":    current_title,
                    "document": doc_text,
                    "metadata": {
                        "standard_id": standard_id,
                        "ref":         current_ref,
                        "title":       current_title[:200],
                        "chapter":     current_ref.split(".", 1)[0],
                        "kind":        "guidance",
                    },
                })

    for line in raw_lines:
        cleaned = _clean_line(line)
        if not cleaned:
            continue

        m = _SEC_HDR.match(cleaned)
        if m and _looks_like_header(cleaned):
            _emit_current()
            current_ref = m.group(1)
            current_title = m.group(2).strip()
            current_body = []
        elif current_ref is not None:
            current_body.append(cleaned)

    _emit_current()
    return chunks


def index_collection(
    client,
    col_name: str,
    chunks: list[dict],
    embed_fn,
    dry_run: bool = False,
) -> None:
    """Upsert the chunks into the named collection."""
    if dry_run:
        print(f"  [dry-run] {col_name}: would upsert {len(chunks)} chunks")
        for c in chunks[:5]:
            print(f"    • §{c['ref']:8} '{c['title'][:60]}'  {len(c['document'])}c")
        return

    col = client.get_or_create_collection(
        name=col_name,
        embedding_function=embed_fn,
        metadata={
            "hnsw:space": "cosine",
            "embedding_function_name": embed_fn.name(),
        },
    )

    t0 = time.time()
    BATCH = 50
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        col.upsert(
            ids       = [c["id"]        for c in batch],
            documents = [c["document"]  for c in batch],
            metadatas = [c["metadata"]  for c in batch],
        )
    elapsed = time.time() - t0
    print(f"  {col_name:25s}: {len(chunks):3d} chunks upserted ({elapsed:.1f}s)")


def sample_query(client, col_name: str, embed_fn, query_text: str) -> None:
    """Run a sample query and print the top-3 hits."""
    try:
        col = client.get_collection(name=col_name, embedding_function=embed_fn)
    except Exception as e:
        print(f"  [!] cannot query {col_name}: {e}")
        return

    result = col.query(query_texts=[query_text], n_results=3)
    print(f"\nSample query on {col_name}: {query_text!r}")
    for i, (doc, meta, dist) in enumerate(zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ), 1):
        ref = meta.get("ref", "?")
        title = meta.get("title", "")
        preview = doc.split("\n\n", 1)[1][:140] if "\n\n" in doc else doc[:140]
        preview = preview.replace("\n", " ")
        print(f"  {i}. §{ref} {title[:50]}  dist={dist:.3f}")
        print(f"     …{preview!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sample", action="store_true",
                    help="Run sample queries after indexing")
    args = ap.parse_args()

    print(f"Ship 13'.d — index ISO 27003 + 27005 guidance to Chroma")
    print(f"Model: {EMBED_MODEL_STANDARD}")
    print()

    # Chunk
    print("Chunking ISO 27003:2017…")
    chunks_27003 = chunk_standard(_TEXT_27003, "ISO27003:2017")
    print(f"  {len(chunks_27003)} sections extracted")
    print("Chunking ISO 27004:2016…")
    chunks_27004 = chunk_standard(_TEXT_27004, "ISO27004:2016")
    print(f"  {len(chunks_27004)} sections extracted")
    print("Chunking ISO 27005:2022…")
    chunks_27005 = chunk_standard(_TEXT_27005, "ISO27005:2022")
    print(f"  {len(chunks_27005)} sections extracted")
    print()

    # Index
    print("Indexing to Chroma…")
    embed_fn = OpenAIEmbeddingFunction(model=EMBED_MODEL_STANDARD)
    client = chromadb.PersistentClient(
        path=str(Path(__file__).parent.parent / "chroma_db")
    )

    index_collection(client, COL_27003, chunks_27003, embed_fn, dry_run=args.dry_run)
    index_collection(client, COL_27004, chunks_27004, embed_fn, dry_run=args.dry_run)
    index_collection(client, COL_27005, chunks_27005, embed_fn, dry_run=args.dry_run)

    if args.sample and not args.dry_run:
        sample_query(client, COL_27005, embed_fn,
                     "how do I structure a risk assessment process")
        sample_query(client, COL_27005, embed_fn,
                     "what are risk acceptance criteria and who approves them")
        sample_query(client, COL_27003, embed_fn,
                     "how to define ISMS scope")
        sample_query(client, COL_27003, embed_fn,
                     "management review agenda items")
        sample_query(client, COL_27004, embed_fn,
                     "what performance and effectiveness measures to use")
        sample_query(client, COL_27004, embed_fn,
                     "who are the roles in a measurement programme")

    return 0


if __name__ == "__main__":
    sys.exit(main())
