"""
Index EDPB Guidelines + WP29 endorsed WP29 documents into Chroma.

Ship 53'.f (2026-08-01) — GDPR consulting-grounding corpus.

Motivation
==========
Before this arc, GDPR remediation queries had no supplementary
implementation-guidance grounding. The LLM cited the article
verbatim and drafted remediation actions from training data.
For DPO-level auditors + EU regulators, that's shallow — real
GDPR practice is grounded in EDPB Guidelines + WP29 predecessor
guidance + case law.

This script indexes the 9 highest-load-bearing EDPB / WP29 PDFs
into a new `edpb_guidelines` Chroma collection so the digest can
fetch topical guidance snippets at build time (Option C per the
Ship 53'.f arc plan — no changes to graph_expander or
ExpandedNode).

Corpus
======
9 documents covering the primary GDPR remediation surfaces.
Each entry maps to the GDPR articles it interprets, which is
what the retrieval layer uses to match cited refs to guidance
snippets.

Pattern
=======
Mirrors scripts/index_27701_to_chroma.py (Ship 53'.d) — uses
EMBED_MODEL_STANDARD from rag/embedding_config.py so this
collection stays consistent with the Ship 5'.b consolidation
onto text-embedding-3-large.

Idempotent — run per corpus refresh. Existing chunks with the
same id are upserted (embedding + metadata refreshed).
"""
from __future__ import annotations

import os
import re
import sys
import json
import hashlib
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv(str(Path(__file__).parent.parent / ".env"))

from vector.indexer import VectorIndexer, COL_ALL
from rag.embedding_config import EMBED_MODEL_STANDARD


COL_EDPB = "edpb_guidelines"

EDPB_DIR = Path(__file__).parent.parent / "private" / "edpb"


# ── Corpus registry ────────────────────────────────────────────────────
# Each entry: filename (in EDPB_DIR) → metadata that describes what
# GDPR articles the document interprets. `interprets_articles` is the
# retrieval-side matching signal — when a chat query cites Art.X, the
# digest fetches guidance chunks from any doc where Art.X is in this
# list.
#
# Kept as data, not YAML, so future contributors can grep for a filename
# and see the full mapping. Extend when a new PDF is added to
# private/edpb/.
CORPUS: dict[str, dict] = {
    "wp29_wp248_dpia.pdf": {
        "source_doc":          "WP29 wp248 rev.01",
        "title":               "Guidelines on Data Protection Impact Assessment (DPIA)",
        "interprets_articles": ["Art.35", "Art.36"],
        "authority":           "WP29",
        "adopted":             "2017-10-04",
    },
    "wp29_wp243_dpo.pdf": {
        "source_doc":          "WP29 wp243 rev.01",
        "title":               "Guidelines on Data Protection Officers",
        "interprets_articles": ["Art.37", "Art.38", "Art.39"],
        "authority":           "WP29",
        "adopted":             "2017-04-05",
    },
    "edpb_072020_controllerprocessor.pdf": {
        "source_doc":          "EDPB 07/2020",
        "title":               "Guidelines on the concepts of controller and processor",
        "interprets_articles": ["Art.4", "Art.24", "Art.26", "Art.28", "Art.29"],
        "authority":           "EDPB",
        "adopted":             "2021-07-07",
    },
    "edpb_052020_consent.pdf": {
        "source_doc":          "EDPB 05/2020",
        "title":               "Guidelines on consent under Regulation 2016/679",
        "interprets_articles": ["Art.6", "Art.7", "Art.8", "Art.9"],
        "authority":           "EDPB",
        "adopted":             "2020-05-04",
    },
    "edpb_092022_breach_notification.pdf": {
        "source_doc":          "EDPB 9/2022",
        "title":               "Guidelines on personal data breach notification under GDPR",
        "interprets_articles": ["Art.33", "Art.34"],
        "authority":           "EDPB",
        "adopted":             "2023-03-28",
    },
    "edpb_rec_012020_supplementary_transfers.pdf": {
        "source_doc":          "EDPB Recommendations 01/2020",
        "title":               "Recommendations on measures that supplement transfer tools",
        "interprets_articles": ["Art.44", "Art.45", "Art.46", "Art.47", "Art.49"],
        "authority":           "EDPB",
        "adopted":             "2021-06-18",
    },
    "edpb_042019_dpbd_art25.pdf": {
        "source_doc":          "EDPB 4/2019",
        "title":               "Guidelines on Article 25 Data Protection by Design and by Default",
        "interprets_articles": ["Art.25"],
        "authority":           "EDPB",
        "adopted":             "2020-10-20",
    },
    "edpb_032018_territorial_scope.pdf": {
        "source_doc":          "EDPB 3/2018",
        "title":               "Guidelines on the territorial scope of the GDPR (Article 3)",
        "interprets_articles": ["Art.3"],
        "authority":           "EDPB",
        "adopted":             "2019-11-12",
    },
    "edpb_012022_right_of_access.pdf": {
        "source_doc":          "EDPB 01/2022",
        "title":               "Guidelines on data subject rights — Right of access",
        "interprets_articles": ["Art.12", "Art.15"],
        "authority":           "EDPB",
        "adopted":             "2023-04-17",
    },
}


# ── Chunking ───────────────────────────────────────────────────────────

# Rough character budget per chunk. Small enough that per-ref retrieval
# stays cheap (a digest might inject 1-2 chunks per cited ref); large
# enough that a chunk carries a complete idea (definition + example).
CHUNK_TARGET_CHARS = 1200
CHUNK_MIN_CHARS    = 300
CHUNK_MAX_CHARS    = 1800

# Section marker patterns. Numeric section headers ("2.", "2.1", "2.1.3")
# are the most reliable EDPB doc structure. Uppercase-word H2 lines
# (e.g., "EXECUTIVE SUMMARY", "INTRODUCTION") are a secondary signal.
_SECTION_HEADER_RE = re.compile(
    r"""^
        (
            \d+(?:\.\d+){0,3}\.?\s+[A-Z]     # e.g. "2.1.3 Definition"
            |
            [A-Z][A-Z\s]{4,}$                # e.g. "EXECUTIVE SUMMARY"
        )
    """,
    re.VERBOSE,
)

# Boilerplate lines to skip — page footers, TOC markers.
_SKIP_LINE_RE = re.compile(
    r"""(
          ^Adopted\s+-\s+After\s+public\s+consultation\s+\d+\s*$
        | ^Version\s+\d+(?:\.\d+)*\s*$
        | ^\d+\s*$                          # bare page number
        | ^Table\s+of\s+contents\s*$
    )""",
    re.VERBOSE | re.IGNORECASE,
)


def _clean_line(line: str) -> str:
    """Trim + collapse internal whitespace."""
    return " ".join(line.split())


def _looks_like_header(line: str) -> bool:
    """True if the line pattern-matches a section header."""
    if not line.strip():
        return False
    if _SECTION_HEADER_RE.match(line.strip()):
        return True
    return False


def _split_into_chunks(text: str) -> list[dict]:
    """Split a PDF's extracted text into semantic chunks.

    Strategy:
      1. Walk lines. Accumulate into a buffer.
      2. On a section header, close the current chunk (if it has
         ≥ CHUNK_MIN_CHARS) and start a new one.
      3. If the buffer exceeds CHUNK_MAX_CHARS without hitting a
         header, flush at the next paragraph break to avoid oversize
         chunks that dilute retrieval.

    Returns list of dicts: {section_title, text, char_count}.
    """
    lines = text.splitlines()
    chunks: list[dict] = []
    buf: list[str] = []
    current_header = ""
    buf_chars = 0

    def flush(header: str):
        nonlocal buf, buf_chars
        if buf_chars < CHUNK_MIN_CHARS:
            return
        text = "\n".join(buf).strip()
        if text:
            chunks.append({
                "section_title": header,
                "text":          text,
                "char_count":    len(text),
            })
        buf = []
        buf_chars = 0

    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            # Paragraph break — flush if buffer is oversized
            if buf_chars > CHUNK_TARGET_CHARS:
                flush(current_header)
            else:
                buf.append("")
                buf_chars += 1
            continue

        if _SKIP_LINE_RE.match(line):
            continue

        if _looks_like_header(line):
            flush(current_header)
            current_header = line[:120]
            # Include the header in the next chunk for context
            buf.append(line)
            buf_chars += len(line) + 1
            continue

        buf.append(line)
        buf_chars += len(line) + 1

        # Hard cap safety
        if buf_chars > CHUNK_MAX_CHARS:
            flush(current_header)

    # Final flush
    flush(current_header)

    return chunks


# ── Indexing ───────────────────────────────────────────────────────────

def _chunk_id(source_doc: str, chunk_index: int) -> str:
    """Deterministic id for idempotent upsert."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", source_doc).strip("_").lower()
    return f"edpb:{normalized}:c{chunk_index:04d}"


def _prepare_records(doc_key: str, meta: dict, chunks: list[dict]) -> tuple[list, list, list]:
    """Convert chunks into (ids, documents, metadatas) tuples for Chroma."""
    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []
    for i, ch in enumerate(chunks):
        cid = _chunk_id(meta["source_doc"], i)
        # Chroma metadata values must be primitives (str/int/float/bool).
        # Serialise interprets_articles as a comma-joined string.
        metadata = {
            "source_doc":          meta["source_doc"],
            "title":                meta["title"],
            "interprets_articles":  ",".join(meta["interprets_articles"]),
            "authority":            meta["authority"],
            "adopted":              meta["adopted"],
            "section_title":        ch["section_title"] or "",
            "chunk_index":          i,
            "standard_id":          "EDPB:guidelines",
            "ref":                  meta["source_doc"],
        }
        ids.append(cid)
        docs.append(ch["text"])
        metas.append(metadata)
    return ids, docs, metas


def main():
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "fallback"

    indexer = VectorIndexer(
        persist_dir     = str(Path(__file__).parent.parent / "chroma_db"),
        provider        = provider,
        embedding_model = EMBED_MODEL_STANDARD if provider == "openai" else None,
    )

    total_chunks = 0
    edpb_collection = indexer._chroma.get_or_create_collection(
        name              = COL_EDPB,
        embedding_function = indexer._embed_fn,
        metadata          = {"hnsw:space": "cosine"},
    )
    all_collection = indexer._chroma.get_or_create_collection(
        name              = COL_ALL,
        embedding_function = indexer._embed_fn,
        metadata          = {"hnsw:space": "cosine"},
    )

    for filename, meta in CORPUS.items():
        txt_path = EDPB_DIR / (filename.rsplit(".", 1)[0] + ".txt")
        if not txt_path.exists():
            print(f"  SKIP {filename} — no .txt file (run pdftotext first)")
            continue

        text = txt_path.read_text(encoding="utf-8", errors="replace")
        chunks = _split_into_chunks(text)
        if not chunks:
            print(f"  SKIP {filename} — no chunks extracted")
            continue

        ids, docs, metas = _prepare_records(filename, meta, chunks)
        # Upsert into edpb_guidelines
        edpb_collection.upsert(ids=ids, documents=docs, metadatas=metas)
        # Upsert into arioncombly_all
        all_collection.upsert(ids=ids, documents=docs, metadatas=metas)

        total_chunks += len(chunks)
        print(f"  {meta['source_doc']:32s} {len(chunks):3d} chunks "
              f"({sum(c['char_count'] for c in chunks) // 1000}KB)")

    print()
    print(f"Total chunks indexed: {total_chunks}")
    print()
    print("Collection counts:")
    for col, count in indexer.collection_stats().items():
        print(f"  {col:25s}: {count:5d} documents")


if __name__ == "__main__":
    main()
