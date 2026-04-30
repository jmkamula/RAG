"""
Tier 2 Enrichment Apply

Loads tier2_generated.json, runs quality checks, patches all nodes,
updates ChromaDB metadata fields, and rebuilds the vector index.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    export CHROMA_HOST=localhost

    # Step 1 — quality check only (no changes)
    python3 enrichment/tier2_apply.py --check

    # Step 2 — apply and rebuild index
    python3 enrichment/tier2_apply.py --apply
"""
from __future__ import annotations

import json
import sys
import os
import argparse
import textwrap
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.requirement_node import RequirementNode
from enrichment.applier       import Tier1EnrichmentApplier


# ── Paths ──────────────────────────────────────────────────────────────────────

HERE            = Path(__file__).parent
GENERATED_PATH  = HERE / "tier2_generated.json"
SAMPLE_PATH     = HERE / "tier2_generated.sample.json"
ISO_JSON        = HERE.parent.parent / "output" / "iso_phase1" / "iso_nodes_phase1.json"
GDPR_JSON       = HERE.parent.parent / "output" / "gdpr_phase2" / "gdpr_nodes_phase2.json"


# ── Quality checks ─────────────────────────────────────────────────────────────

def check_quality(generated: dict) -> tuple[list, list]:
    """
    Run quality checks on generated enrichment.
    Returns (warnings, errors).
    Errors block apply. Warnings are printed but do not block.
    """
    warnings = []
    errors   = []

    for ref, data in generated.items():
        biz = data.get("business_description", "")
        kw  = data.get("query_keywords", {})
        wc  = len(biz.split())

        # Errors — block apply
        if wc < 30:
            errors.append(f"{ref}: description too short ({wc}w — minimum 30)")
        if not biz.strip():
            errors.append(f"{ref}: empty business_description")
        if not isinstance(kw, dict):
            errors.append(f"{ref}: query_keywords is not a dict")
            continue

        # Warnings — logged but do not block
        if wc < 60:
            warnings.append(f"{ref}: short description ({wc}w)")
        if wc > 220:
            warnings.append(f"{ref}: very long description ({wc}w)")
        if not kw.get("exact"):
            warnings.append(f"{ref}: no exact keywords")
        if len(kw.get("practitioner", [])) < 2:
            warnings.append(f"{ref}: fewer than 2 practitioner keywords")
        if not kw.get("scenario"):
            warnings.append(f"{ref}: no scenario keywords")

        # Check for generic starts (sign of low-quality output)
        first_words = biz[:40].lower()
        generic_starts = [
            "this article requires",
            "this provision",
            "this section",
            "the gdpr requires",
        ]
        if any(first_words.startswith(g) for g in generic_starts) and wc < 70:
            warnings.append(
                f"{ref}: starts generically and is short — consider reviewing"
            )

    return warnings, errors


def print_quality_report(
    generated:  dict,
    node_map:   dict,
    warnings:   list,
    errors:     list,
) -> None:
    """Print a formatted quality report."""
    word_counts = [len(d["business_description"].split())
                   for d in generated.values()]
    kw_counts   = [sum(len(v) for v in d.get("query_keywords", {}).values()
                       if isinstance(v, list))
                   for d in generated.values()]

    print(f"\n{'─' * 60}")
    print(f"  TIER 2 QUALITY REPORT")
    print(f"{'─' * 60}")
    print(f"  Entries:       {len(generated)}")
    print(f"  Word count:    min={min(word_counts)}  "
          f"max={max(word_counts)}  "
          f"avg={sum(word_counts)//len(word_counts)}")
    print(f"  Keyword count: avg={sum(kw_counts)//len(kw_counts)}")
    print(f"  Warnings:      {len(warnings)}")
    print(f"  Errors:        {len(errors)}")

    # Coverage by chapter
    chapter_counts: dict[str, int] = defaultdict(int)
    for ref in generated:
        node    = node_map.get(ref)
        chapter = node.chapter if node and node.chapter else "Unknown"
        chapter_counts[chapter] += 1

    print(f"\n  Coverage by chapter:")
    for chapter, count in sorted(
        chapter_counts.items(), key=lambda x: -x[1]
    ):
        print(f"    {count:3d}  {chapter}")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings[:15]:
            print(f"    ⚠ {w}")
        if len(warnings) > 15:
            print(f"    ... and {len(warnings) - 15} more")

    if errors:
        print(f"\n  Errors ({len(errors)}) — BLOCKING:")
        for e in errors:
            print(f"    ✗ {e}")

    print(f"{'─' * 60}")


def print_spot_check(generated: dict, refs: list[str]) -> None:
    """Print full enrichment for a spot-check sample."""
    print(f"\n{'=' * 60}")
    print(f"  SPOT CHECK SAMPLE")
    print(f"{'=' * 60}")

    for ref in refs:
        if ref not in generated:
            print(f"\n  {ref}: not in generated file")
            continue
        data = generated[ref]
        biz  = data.get("business_description", "")
        kw   = data.get("query_keywords", {})

        print(f"\n{'─' * 60}")
        print(f"  {ref}  ({len(biz.split())} words)")
        print(f"{'─' * 60}")
        for line in textwrap.wrap(biz, width=58):
            print(f"  {line}")
        print()
        for cat, terms in kw.items():
            if terms:
                terms_str = ", ".join(str(t) for t in terms[:5])
                print(f"  {cat:12s}: {terms_str}")


# ── Apply enrichment ───────────────────────────────────────────────────────────

def apply_enrichment(
    generated:  dict,
    nodes:      list[RequirementNode],
) -> tuple[int, int]:
    """
    Patch nodes in-place with generated enrichment.
    Returns (enriched_count, skipped_count).
    """
    node_map   = {n.ref: n for n in nodes}
    enriched   = 0
    skipped    = 0
    not_found  = []

    for ref, data in generated.items():
        node = node_map.get(ref)
        if not node:
            not_found.append(ref)
            continue

        # Skip if already has Tier 1 enrichment — never overwrite hand-authored
        if node.business_description:
            skipped += 1
            continue

        node.business_description = data.get("business_description", "")
        node.query_keywords        = data.get("query_keywords", {})
        enriched += 1

    if not_found:
        print(f"  ⚠ {len(not_found)} refs not found in node set: "
              f"{not_found[:5]}")

    return enriched, skipped


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Apply Tier 2 enrichment to ArionComply knowledge base"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="Quality check only — no changes made",
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="Apply enrichment and rebuild ChromaDB index",
    )
    parser.add_argument(
        "--generated",
        default=str(GENERATED_PATH),
        help=f"Path to generated JSON (default: {GENERATED_PATH})",
    )
    parser.add_argument(
        "--spot-check",
        nargs="*",
        metavar="REF",
        help="Print full enrichment for specific refs (e.g. Art.17 Art.83.4)",
    )
    parser.add_argument(
        "--chroma-host",
        default=None,
        help="ChromaDB HTTP server host",
    )
    parser.add_argument(
        "--chroma-port",
        default=8000,
        type=int,
    )
    parser.add_argument(
        "--model",
        default="text-embedding-3-large",
        help="Embedding model for index rebuild",
    )
    args = parser.parse_args()

    # ── Load generated enrichment ──────────────────────────────────────────
    gen_path = Path(args.generated)
    if not gen_path.exists():
        print(f"✗ Generated file not found: {gen_path}")
        print(f"  Run: python3 enrichment/tier2_generator.py --run")
        sys.exit(1)

    with open(gen_path) as f:
        generated = json.load(f)
    print(f"✓ Loaded {len(generated)} generated entries from {gen_path.name}")

    # ── Load nodes ──────────────────────────────────────────────────────────
    iso_path  = Path(args.__dict__.get("iso", str(ISO_JSON)))
    gdpr_path = Path(args.__dict__.get("gdpr", str(GDPR_JSON)))

    # Try local paths if absolute not found
    if not iso_path.exists():
        iso_path  = Path("iso_nodes_phase1.json")
        gdpr_path = Path("gdpr_nodes_phase2.json")

    with open(iso_path) as f:
        iso_nodes = [RequirementNode.from_dict(d) for d in json.load(f)]
    with open(gdpr_path) as f:
        gdpr_nodes = [RequirementNode.from_dict(d) for d in json.load(f)]

    all_nodes = iso_nodes + gdpr_nodes
    node_map  = {n.ref: n for n in all_nodes}
    print(f"✓ Loaded {len(all_nodes)} nodes ({len(iso_nodes)} ISO, "
          f"{len(gdpr_nodes)} GDPR)")

    # Apply Tier 1 first (preserves hand-authored enrichment)
    applier = Tier1EnrichmentApplier()
    applier.load()
    applier.apply(all_nodes)
    t1_count = sum(1 for n in all_nodes if n.business_description)
    print(f"✓ Tier 1 applied: {t1_count} nodes already enriched")

    # ── Quality check ──────────────────────────────────────────────────────
    warnings, errors = check_quality(generated)
    print_quality_report(generated, node_map, warnings, errors)

    # ── Spot check ─────────────────────────────────────────────────────────
    spot_refs = args.spot_check
    if spot_refs is not None:
        if not spot_refs:
            # Default spot check — a varied sample
            spot_refs = [
                "Art.4.1", "Art.13", "Art.83.4",   # our corrected entries
                "Art.17",  "Art.20", "Art.22",       # rights cluster
                "Art.44",  "Art.46",                 # transfers
                "Art.9",   "Art.9.1",                # special categories
            ]
        print_spot_check(generated, spot_refs)

    # Block on errors
    if errors:
        print(f"\n✗ {len(errors)} errors found — fix before applying")
        sys.exit(1)

    if args.check:
        print(f"\n✓ Quality check complete — no errors found")
        print(f"  Ready to apply: python3 enrichment/tier2_apply.py --apply")
        return

    # ── Apply ──────────────────────────────────────────────────────────────
    print(f"\nApplying Tier 2 enrichment...")
    enriched, skipped = apply_enrichment(generated, all_nodes)
    print(f"  Enriched:  {enriched} nodes")
    print(f"  Skipped:   {skipped} (Tier 1 — not overwritten)")

    total_enriched = sum(1 for n in all_nodes if n.business_description)
    print(f"  Total now: {total_enriched} / {len(all_nodes)} nodes enriched "
          f"({100*total_enriched//len(all_nodes)}%)")

    # ── Rebuild index ──────────────────────────────────────────────────────
    print(f"\nRebuilding ChromaDB index...")
    chroma_host = args.chroma_host or os.getenv("CHROMA_HOST")

    from vector.indexer import VectorIndexer
    from enrichment.applier import Tier1EnrichmentApplier as _T1

    indexer = VectorIndexer(
        provider        = "openai",
        embedding_model = args.model,
        chroma_host     = chroma_host,
        chroma_port     = args.chroma_port,
    )

    # Split back into iso/gdpr for the indexer
    iso_enriched  = [n for n in all_nodes if n.is_iso]
    gdpr_enriched = [n for n in all_nodes if n.is_gdpr]

    stats = indexer.index_all(iso_enriched, gdpr_enriched, reset=True)

    print(f"\n{'─' * 60}")
    print(f"  INDEX REBUILD COMPLETE")
    print(f"{'─' * 60}")
    for coll, info in stats.items():
        print(f"  {coll:25s}: {info.get('upserted', 0)} docs")
    print(f"\n✓ Tier 2 enrichment applied and index rebuilt")
    print(f"  Run retrieval test: python3 vector/test_retrieval.py")


if __name__ == "__main__":
    main()
