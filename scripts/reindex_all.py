"""
scripts/reindex_all.py — one-shot rebuild of every vector collection.

Ship 5'.b (2026-07-18) — added when we consolidated onto a single
embedding model (`text-embedding-3-large`). Enables future model
migrations to be a two-step operation:

    1. Edit `rag/embedding_config.py::EMBED_MODEL_STANDARD`
    2. `python3 scripts/reindex_all.py --reset`

Collections rebuilt:

  RequirementNode graph (index_all_from_json):
    * iso27001_2022    — from iso_nodes_phase1.json
    * gdpr_2016_679    — from gdpr_nodes_phase2.json
    * arioncombly_all  — combined
    (ISO 27701 is a separate seed — see index_27701_to_chroma.py)

  MUST checklist (build_must_index.py):
    * musts_arioncomply — from document_requirements.py

Options:

  --reset           Drop and rebuild the RequirementNode collections
                    instead of upserting. Necessary when the embed
                    model changes (dimensions differ between models).
  --musts-only      Skip the RequirementNode collections; rebuild
                    only the MUST checklist collection.
  --nodes-only      Rebuild only the RequirementNode collections.
  --iso27701        Also run the ISO 27701 seed + indexer.

Idempotent: safe to re-run. Prints a summary of upserted counts +
elapsed time per collection.

Cost: ~$0.25 for a full rebuild across all 4 collections at
`text-embedding-3-large` pricing (2026 rates). Cheap enough that
running this on every deploy is fine if you want.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(str(Path(__file__).parent.parent / ".env"))

from rag.embedding_config import EMBED_MODEL_STANDARD, EMBED_PROVIDER


ROOT       = Path(__file__).parent.parent
CHROMA_DIR = str(ROOT / "chroma_db")
ISO_JSON   = str(ROOT / "iso_nodes_phase1.json")
GDPR_JSON  = str(ROOT / "gdpr_nodes_phase2.json")


def _index_requirement_nodes(reset: bool) -> dict:
    """Rebuild the RequirementNode collections (iso/gdpr/all).
    Uses vector/indexer.py::VectorIndexer configured with the
    shared embedding model constant."""
    from vector.indexer import VectorIndexer
    print(f"[nodes]  indexing RequirementNode collections "
          f"(model={EMBED_MODEL_STANDARD}, reset={reset})")
    idx = VectorIndexer(
        persist_dir     = CHROMA_DIR,
        provider        = EMBED_PROVIDER,
        embedding_model = EMBED_MODEL_STANDARD,
    )
    t0 = time.time()
    result = idx.index_all_from_json(
        iso_json  = ISO_JSON,
        gdpr_json = GDPR_JSON,
        reset     = reset,
    )
    elapsed = time.time() - t0
    print(f"[nodes]  done in {elapsed:.1f}s — {result}")
    return {"nodes": {"elapsed_s": round(elapsed, 1), **(result or {})}}


def _index_musts() -> dict:
    """Rebuild the musts_arioncomply collection via the existing
    build script (which itself uses the shared constant now)."""
    print(f"[musts]  indexing musts_arioncomply "
          f"(model={EMBED_MODEL_STANDARD})")
    from scripts.build_must_index import build_index
    t0 = time.time()
    summary = build_index()
    elapsed = time.time() - t0
    print(f"[musts]  done in {elapsed:.1f}s — {summary}")
    return {"musts": {"elapsed_s": round(elapsed, 1), **(summary or {})}}


def _index_iso27701() -> dict:
    """Rebuild the iso27701 collection via its dedicated script."""
    print(f"[27701]  indexing iso27701_2019 "
          f"(model={EMBED_MODEL_STANDARD})")
    from scripts.index_27701_to_chroma import main as _27701_main
    t0 = time.time()
    _27701_main()
    elapsed = time.time() - t0
    print(f"[27701]  done in {elapsed:.1f}s")
    return {"iso27701": {"elapsed_s": round(elapsed, 1)}}


def main():
    ap = argparse.ArgumentParser(description="Reindex all Chroma collections.")
    ap.add_argument("--reset",       action="store_true",
                    help="Drop + rebuild (required for model changes).")
    ap.add_argument("--musts-only",  action="store_true",
                    help="Rebuild only the MUST checklist collection.")
    ap.add_argument("--nodes-only",  action="store_true",
                    help="Rebuild only the RequirementNode collections.")
    ap.add_argument("--iso27701",    action="store_true",
                    help="Also run the ISO 27701 indexer.")
    args = ap.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    print(f"reindex_all.py — model={EMBED_MODEL_STANDARD}, dir={CHROMA_DIR}")
    print()

    summary: dict = {}

    if not args.musts_only:
        summary.update(_index_requirement_nodes(reset=args.reset))

    if not args.nodes_only:
        summary.update(_index_musts())

    if args.iso27701:
        summary.update(_index_iso27701())

    print()
    print("=" * 60)
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
