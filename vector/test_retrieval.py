#!/usr/bin/env python3
"""
Test retrieval quality after building the vector index.

Runs a battery of compliance queries and checks that the expected
nodes appear in the top results. With real OpenAI embeddings these
should all pass. With fallback hash embeddings they will not — that's
expected and is why we use real embeddings.

Usage:
    cd ingestion
    python3 vector/test_retrieval.py

    # or with explicit DB path:
    python3 vector/test_retrieval.py --db ./chroma_db
"""

from __future__ import annotations
import sys
import argparse
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vector.retriever import VectorRetriever


# ── Expected results for each test query ──────────────────────────────────────
# Format: (query, expected_refs_in_top_n, n, description)

RETRIEVAL_TESTS = [
    # Cross-standard encryption query
    (
        "pseudonymisation and encryption of personal data at rest and in transit",
        ["Art.32.1.a", "Art.5.1.f", "A.8.24"],
        8,
        "Encryption: should find GDPR Art.32.1.a, Art.5.1.f, and ISO A.8.24"
    ),
    # 72-hour breach notification
    (
        "notify supervisory authority within 72 hours of personal data breach",
        ["Art.33.1", "Art.33"],
        6,
        "Breach notification: should find Art.33.1 (72-hour rule)"
    ),
    # Accountability / controller responsibility
    (
        "controller responsible for demonstrating compliance with data protection principles",
        ["Art.5.2", "Art.24"],
        6,
        "Accountability: should find Art.5.2 and Art.24"
    ),
    # ROPA — records of processing
    (
        "record of processing activities controller processor",
        ["Art.30", "Art.30.1", "Art.30.2"],
        6,
        "ROPA: should find Art.30 and its paragraphs"
    ),
    # Privacy by design
    (
        "data protection by design and by default privacy engineering",
        ["Art.25", "Art.25.1", "Art.25.2"],
        6,
        "Privacy by design: should find Art.25"
    ),
    # Processor agreements
    (
        "data processing agreement processor contract binding obligations",
        ["Art.28", "Art.28.3"],
        6,
        "DPA: should find Art.28"
    ),
    # ISO access control
    (
        "access control identity management user access rights",
        ["A.5.15", "A.5.16", "A.5.17", "A.5.18"],
        8,
        "ISO access control: should find A.5.15-18 cluster"
    ),
    # ISO incident management
    (
        "information security incident response management reporting",
        ["A.5.24", "A.5.25", "A.5.26"],
        8,
        "ISO incident management: should find A.5.24-26"
    ),
    # DPO designation
    (
        "data protection officer designation appointment large scale processing",
        ["Art.37", "Art.37.1"],
        6,
        "DPO: should find Art.37"
    ),
    # Data subject rights
    (
        "right to erasure right to be forgotten delete personal data",
        ["Art.17", "Art.17.1"],
        6,
        "Right to erasure: should find Art.17"
    ),
    # Cross-framework: security measures
    (
        "appropriate technical and organisational measures security risk assessment",
        ["Art.32", "Art.24", "A.8.24"],
        10,
        "TOMs: should find Art.32, Art.24, ISO security controls"
    ),
    # DPIA
    (
        "data protection impact assessment high risk processing systematic monitoring",
        ["Art.35", "Art.35.1", "Art.35.3"],
        6,
        "DPIA: should find Art.35"
    ),
]


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_tests(retriever: VectorRetriever, verbose: bool = False) -> dict:
    passed   = 0
    failed   = 0
    failures = []

    print(f"Running {len(RETRIEVAL_TESTS)} retrieval quality tests...\n")

    for query, expected, n, description in RETRIEVAL_TESTS:
        ctx = retriever.search(query, n=n)
        returned_refs = [r.ref for r in ctx.results]

        # Check how many expected refs appear in results
        found    = [r for r in expected if r in returned_refs]
        missing  = [r for r in expected if r not in returned_refs]
        hit_rate = len(found) / len(expected) if expected else 1.0

        # Pass if at least 1 expected ref in top-n
        # (strict: all expected refs in top-n)
        any_hit  = len(found) >= 1
        all_hit  = len(found) == len(expected)

        if any_hit:
            passed += 1
            status = "✓"
            detail = f"found {found}"
        else:
            failed += 1
            status = "✗"
            detail = f"got {returned_refs[:4]}"
            failures.append((description, query, expected, returned_refs[:5]))

        print(f"  {status} {description}")
        if verbose or not any_hit:
            print(f"    Query:    '{query[:70]}'")
            print(f"    Expected: {expected}")
            print(f"    Got:      {returned_refs[:n]}")
            print(f"    Scores:   {[f'{r.score:.3f}' for r in ctx.results[:5]]}")

        if all_hit and verbose:
            print(f"    ✓✓ All expected refs found ({found})")

    print(f"\n{'='*55}")
    print(f"Results: {passed}/{len(RETRIEVAL_TESTS)} passed, {failed} failed")

    if failures:
        print(f"\nFailed tests:")
        for desc, q, exp, got in failures:
            print(f"  ✗ {desc}")
            print(f"    Expected: {exp}")
            print(f"    Got:      {got}")

    return {
        "passed":  passed,
        "failed":  failed,
        "total":   len(RETRIEVAL_TESTS),
        "pass_pct": round(100 * passed / len(RETRIEVAL_TESTS)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db",
        default=str(Path(__file__).parent.parent / "chroma_db"),
        metavar="PATH",
        help="ChromaDB persist directory (default: ./chroma_db)")
    parser.add_argument("--provider", default="openai",
        choices=["openai", "anthropic", "fallback"])
    parser.add_argument("--model",
        default=None,
        help="Embedding model — MUST match the model used to build the index "
             "(default: text-embedding-3-small). "
             "If you indexed with text-embedding-3-large, pass --model text-embedding-3-large")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # Detect if using fallback
    provider = args.provider
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        print("⚠  OPENAI_API_KEY not set — results will be random (fallback).")
        print("   Set your key and re-run for meaningful quality tests.\n")
        provider = "fallback"
    elif provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠  ANTHROPIC_API_KEY not set — falling back.")
        provider = "fallback"

    if provider == "fallback":
        print("NOTE: Fallback embeddings are hash-based (not semantic).")
        print("      Retrieval quality tests will mostly fail — this is expected.")
        print("      Build the index with real embeddings for meaningful results.\n")

    retriever = VectorRetriever(
        persist_dir    = args.db,
        provider       = provider,
        embedding_model = args.model,
    )

    # Quick collection check
    stats = retriever._indexer.collection_stats()
    print("Collections:")
    for col, count in stats.items():
        print(f"  {col:25s}: {count} documents")
    print()

    if all(c == 0 for c in stats.values()):
        print("✗ Collections are empty.")
        print()
        print("  Build the index first:")
        print("    export OPENAI_API_KEY=sk-...")
        print("    python3 vector/build_index.py \\")
        print("        --iso /path/to/iso_nodes_phase1.json \\")
        print("        --gdpr /path/to/gdpr_nodes_phase2.json")
        sys.exit(1)

    results = run_tests(retriever, verbose=args.verbose)

    print()
    if results["pass_pct"] >= 80:
        print(f"✓ Good retrieval quality ({results['pass_pct']}% pass rate)")
    elif results["pass_pct"] >= 50:
        print(f"⚠  Moderate retrieval quality ({results['pass_pct']}% pass rate)")
        print("   Consider rebuilding the index with text-embedding-3-large")
    else:
        print(f"✗ Poor retrieval quality ({results['pass_pct']}% pass rate)")
        print("   If using fallback embeddings: rebuild with real OpenAI embeddings")
        print("   If using real embeddings: check index was built correctly")


if __name__ == "__main__":
    main()
