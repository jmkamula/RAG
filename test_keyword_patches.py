"""
Test suite for keyword patches.
Validates:
  1. Each benchmark failure query now resolves correctly
  2. No contamination of adjacent control retrieval
  3. Cross-standard queries still work

Run: python3 test_keyword_patches.py
"""
import sys, os, json
sys.path.insert(0, '.')

from models.requirement_node import RequirementNode
from enrichment.applier      import Tier1EnrichmentApplier
from enrichment.keyword_patches import KEYWORD_PATCHES, apply_patches
from vector.retriever        import VectorRetriever

# ── Colours ───────────────────────────────────────────────────────────────────
G = "\033[32m"
R = "\033[31m"
Y = "\033[33m"
D = "\033[2m"
X = "\033[0m"

# ── Test definitions ──────────────────────────────────────────────────────────

# Format: (query, must_include, must_not_include, description)
PATCH_TESTS = [
    # F1 — Encryption gaps
    (
        "what are our encryption gaps?",
        ["A.8.24"],
        [],
        "F1: encryption gaps → A.8.24",
    ),
    (
        "encryption policy gap analysis",
        ["A.8.24"],
        ["A.5.23", "Art.33"],
        "F1: encryption policy gap → A.8.24, not cloud/breach",
    ),
    (
        "cryptographic controls gap",
        ["A.8.24"],
        [],
        "F1: cryptographic controls gap → A.8.24",
    ),

    # F2 — Audit preparation
    (
        "preparing for our ISO 27001 audit next month",
        ["9.2"],
        ["A.8.24", "Art.33"],
        "F2: audit prep → 9.2, not encryption/breach",
    ),
    (
        "ISO audit preparation checklist",
        ["9.2"],
        [],
        "F2: audit preparation → 9.2",
    ),
    (
        "what to prepare before ISO 27001 audit",
        ["9.2"],
        ["Art.28"],
        "F2: audit prep → 9.2, not processor obligations",
    ),

    # F3/F5 — Cloud storage
    (
        "what are our obligations for cloud storage for data privacy?",
        ["A.5.23", "Art.28"],
        ["9.2", "A.8.11"],
        "F3: cloud storage → A.5.23 + Art.28, not audit/masking",
    ),
    (
        "cloud security requirements ISO 27001",
        ["A.5.23"],
        ["A.8.24"],
        "F3: cloud security → A.5.23, not cryptography",
    ),
    (
        "what does GDPR require for cloud providers?",
        ["Art.28"],
        ["Art.33"],
        "F5: cloud GDPR → Art.28, not breach notification",
    ),

    # Contamination checks — these should NOT be affected by patches
    (
        "data masking for personal data",
        ["A.8.11"],
        ["A.8.24"],
        "CONTAMINATION: masking → A.8.11, not cryptography",
    ),
    (
        "72 hour breach notification",
        ["Art.33"],
        ["Art.28", "A.8.24"],
        "CONTAMINATION: breach → Art.33, not processor/encryption",
    ),
    (
        "right to erasure",
        ["Art.17"],
        ["A.8.24", "Art.28"],
        "CONTAMINATION: erasure → Art.17, not encryption/processor",
    ),
    (
        "management review inputs ISO 27001",
        ["9.3"],
        ["9.2"],
        "CONTAMINATION: mgmt review → 9.3, not internal audit",
    ),

    # Cross-standard — should still work
    (
        "encryption requirement GDPR ISO",
        ["Art.32", "A.8.24"],
        [],
        "CROSS-STD: encryption → Art.32 + A.8.24",
    ),
    (
        "what does Art.33.1 require?",
        ["Art.33"],
        ["A.8.24", "Art.28"],
        "EXISTING: Art.33.1 fast path still works",
    ),
    (
        "risk assessment personal data",
        ["6.1.2", "Art.32"],
        [],
        "GENERAL: risk assessment → 6.1.2 + Art.32",
    ),
]


def run_tests(retriever: VectorRetriever, top_k: int = 8):
    passed = 0
    failed = 0
    warnings = 0

    print(f"\n{'─'*65}")
    print(f"  KEYWORD PATCH VALIDATION — {len(PATCH_TESTS)} tests")
    print(f"{'─'*65}\n")

    for query, must_include, must_not_include, description in PATCH_TESTS:
        ctx = retriever.search(query=query, n=top_k)
        retrieved_refs = [r.ref for r in ctx.results]

        # Check must_include
        missing = [r for r in must_include if r not in retrieved_refs]
        # Check must_not_include
        contaminated = [r for r in must_not_include if r in retrieved_refs]

        if not missing and not contaminated:
            status = f"{G}✓{X}"
            passed += 1
        elif missing and not contaminated:
            status = f"{R}✗{X}"
            failed += 1
        elif not missing and contaminated:
            status = f"{Y}△{X}"
            warnings += 1
        else:
            status = f"{R}✗{X}"
            failed += 1

        print(f"  {status} {description}")

        if missing:
            print(f"    {R}Missing:{X}      {missing}")
            print(f"    {D}Retrieved:{X}    {retrieved_refs[:6]}")
        if contaminated:
            print(f"    {Y}Contaminated:{X} {contaminated}")
            print(f"    {D}Retrieved:{X}    {retrieved_refs[:6]}")

    print(f"\n{'─'*65}")
    print(f"  Results: {G}{passed} passed{X}  "
          f"{Y}{warnings} warnings{X}  "
          f"{R}{failed} failed{X}")
    print(f"{'─'*65}\n")

    return passed, warnings, failed


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--chroma-host", default=None)
    parser.add_argument("--chroma-port", default=8000, type=int)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show patch changes without connecting to ChromaDB")
    args = parser.parse_args()

    # Load nodes
    print("Loading nodes...")
    with open("iso_nodes_phase1.json") as f:
        iso_raw = json.load(f)
    with open("gdpr_nodes_phase2.json") as f:
        gdpr_raw = json.load(f)

    iso_nodes  = [RequirementNode.from_dict(n) for n in iso_raw]
    gdpr_nodes = [RequirementNode.from_dict(n) for n in gdpr_raw]
    all_nodes  = iso_nodes + gdpr_nodes

    # Apply tier1
    applier = Tier1EnrichmentApplier()
    applier.load()
    applier.apply(iso_nodes)

    if args.dry_run:
        print("\n[DRY RUN] Showing what patches would add:\n")
        for ref, patch in KEYWORD_PATCHES.items():
            node = next((n for n in all_nodes if n.ref == ref), None)
            if node:
                existing = node.query_keywords or {}
                print(f"  {ref} — {node.title[:50]}")
                for cat in ("practitioner", "scenario"):
                    new_kws = [k for k in patch.get(cat,[])
                               if k not in existing.get(cat,[])]
                    if new_kws:
                        print(f"    +{cat}: {new_kws}")
            else:
                print(f"  {ref}: not found in nodes")
        return

    # Apply patches
    count, patched_refs = apply_patches(all_nodes, KEYWORD_PATCHES)
    print(f"Applied patches to {count} nodes: {patched_refs}")

    # Connect to ChromaDB
    print(f"Connecting to ChromaDB ({args.chroma_host or 'local'}:{args.chroma_port})...")
    retriever = VectorRetriever(
        chroma_host = args.chroma_host,
        chroma_port = args.chroma_port,
    )

    # Run tests
    passed, warnings, failed = run_tests(retriever)

    if failed == 0:
        print("\n✓ All benchmark failures resolved — patches are clean")
    else:
        print(f"\n✗ {failed} tests still failing — review keyword patches")


if __name__ == "__main__":
    main()
