#!/usr/bin/env python3
"""
Build the ArionComply vector index using OpenAI embeddings.

Usage:
    export OPENAI_API_KEY=sk-...
    cd ingestion
    python3 vector/build_index.py

Options:
    --model    text-embedding-3-small (default) | text-embedding-3-large
    --reset    Drop and rebuild collections from scratch (default: True)
    --iso      Path to iso_nodes_phase1.json
    --gdpr     Path to gdpr_nodes_phase2.json
    --db       ChromaDB persist directory (default: ./chroma_db)
    --dry-run  Print stats without embedding (uses fallback)

After running:
    - ./chroma_db/ contains the persistent vector store
    - Run vector/test_retrieval.py to verify semantic quality
"""

from __future__ import annotations
import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Build ArionComply vector index with OpenAI embeddings"
    )
    parser.add_argument("--model",
        default="text-embedding-3-small",
        choices=["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        help="OpenAI embedding model")
    parser.add_argument("--provider",
        default="openai",
        choices=["openai", "anthropic", "fallback"],
        help="Embedding provider")
    parser.add_argument("--reset",
        action="store_true", default=True,
        help="Drop and recreate collections (default: True)")
    parser.add_argument("--no-reset",
        action="store_false", dest="reset",
        help="Upsert only — don't drop existing collections")
    # Search for node files in several likely locations
    def _find_file(candidates):
        for c in candidates:
            if Path(c).exists():
                return str(c)
        return candidates[0]   # return first candidate so error message is helpful

    here = Path(__file__).parent   # vector/

    parser.add_argument("--iso",
        default=_find_file([
            here / "iso_nodes_phase1.json",                          # same dir
            here.parent / "output/iso_phase1/iso_nodes_phase1.json", # ingestion/output
            here.parent.parent / "output/iso_phase1/iso_nodes_phase1.json",
        ]),
        metavar="PATH",
        help="Path to iso_nodes_phase1.json (default: auto-detected)")
    parser.add_argument("--gdpr",
        default=_find_file([
            here / "gdpr_nodes_phase2.json",
            here.parent / "output/gdpr_phase2/gdpr_nodes_phase2.json",
            here.parent.parent / "output/gdpr_phase2/gdpr_nodes_phase2.json",
        ]),
        metavar="PATH",
        help="Path to gdpr_nodes_phase2.json (default: auto-detected)")
    parser.add_argument("--db",
        default=str(here.parent / "chroma_db"),
        metavar="PATH",
        help="ChromaDB persist directory (default: ./chroma_db)")
    parser.add_argument("--chroma-host", default=None,
        help="ChromaDB HTTP server host (e.g. localhost). "
             "Overrides --db when set.")
    parser.add_argument("--chroma-port", default=8000, type=int,
        help="ChromaDB HTTP server port (default: 8000)")
    parser.add_argument("--dry-run", action="store_true",
        help="Use fallback embeddings (no API call) — for structure testing only")

    args = parser.parse_args()

    # Check API key
    provider = args.provider
    if args.dry_run:
        provider = "fallback"
        print("⚠  Dry run — using fallback embeddings (not semantic)")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print("✗ OPENAI_API_KEY not set.")
            print("  Set it with: export OPENAI_API_KEY=sk-...")
            sys.exit(1)
        print(f"✓ OPENAI_API_KEY set ({api_key[:8]}...)")
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("✗ ANTHROPIC_API_KEY not set.")
            sys.exit(1)
        print(f"✓ ANTHROPIC_API_KEY set ({api_key[:8]}...)")

    # Check input files
    for label, path in [("ISO nodes", args.iso), ("GDPR nodes", args.gdpr)]:
        if not Path(path).exists():
            print(f"✗ {label} not found: {path}")
            print()
            print("  Pass the paths explicitly:")
            print("    python3 vector/build_index.py \\")
            print("        --iso /path/to/iso_nodes_phase1.json \\")
            print("        --gdpr /path/to/gdpr_nodes_phase2.json")
            print()
            print("  The JSON files are in the outputs from the bootstrap runs.")
            print("  Download them from the Claude session or copy from wherever")
            print("  you saved ingestion_pipeline_v4.tar.gz outputs.")
            sys.exit(1)
        print(f"✓ {label}: {path}")

    # Print model info
    if provider == "openai":
        model_dims = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        dims = model_dims.get(args.model, "?")
        model_cost = {
            "text-embedding-3-small": "$0.02/M tokens (~$0.006 for full index)",
            "text-embedding-3-large": "$0.13/M tokens (~$0.039 for full index)",
            "text-embedding-ada-002": "$0.10/M tokens (legacy)",
        }
        cost = model_cost.get(args.model, "")
        print(f"\nModel:       {args.model}")
        print(f"Dimensions:  {dims}")
        print(f"Est. cost:   {cost}")

    print(f"DB path:     {args.db}")
    print(f"Reset:       {args.reset}")
    print()

    # Build index
    from vector.indexer import VectorIndexer
    from enrichment.applier import Tier1EnrichmentApplier

    chroma_host = args.chroma_host or os.getenv("CHROMA_HOST")
    chroma_port = args.chroma_port or int(os.getenv("CHROMA_PORT", "8000"))

    indexer = VectorIndexer(
        persist_dir     = args.db,
        provider        = provider,
        embedding_model = args.model if provider != "fallback" else None,
        chroma_host     = chroma_host,
        chroma_port     = chroma_port,
    )

    # Load nodes
    iso_nodes  = indexer._load_nodes(args.iso)
    gdpr_nodes = indexer._load_nodes(args.gdpr)

    # Apply Tier 1 enrichment before indexing
    print("\nApplying Tier 1 enrichment...")
    applier = Tier1EnrichmentApplier()
    applier.load()
    count = applier.apply(iso_nodes + gdpr_nodes)
    report = applier.report()
    print(f"  Enriched {count} nodes across {len(report.cluster_counts)} clusters")
    if report.refs_not_found:
        print(f"  ⚠ {len(report.refs_not_found)} refs not found: "
              f"{report.refs_not_found[:5]}")
    print()

    stats = indexer.index_all(iso_nodes, gdpr_nodes, reset=args.reset)

    print()
    print("Final collection counts:")
    for col, count in indexer.collection_stats().items():
        print(f"  {col:25s}: {count:4d} documents")

    print()
    print("✓ Index build complete.")
    if not args.dry_run:
        print("  Next: python3 vector/test_retrieval.py")


if __name__ == "__main__":
    main()
