"""
Apply keyword patches and rebuild ChromaDB index.

Usage:
  # Preview what will change
  python3 enrichment/apply_keyword_patches.py --dry-run

  # Apply patches and rebuild index
  python3 enrichment/apply_keyword_patches.py --chroma-host localhost

  # Apply without rebuilding (manual rebuild later)
  python3 enrichment/apply_keyword_patches.py --no-rebuild
"""
import json, sys, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.requirement_node   import RequirementNode
from enrichment.applier        import Tier1EnrichmentApplier
from enrichment.keyword_patches import KEYWORD_PATCHES, apply_patches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--no-rebuild",  action="store_true")
    parser.add_argument("--chroma-host", default=None)
    parser.add_argument("--chroma-port", default=8000, type=int)
    parser.add_argument("--iso-file",    default="iso_nodes_phase1.json")
    parser.add_argument("--gdpr-file",   default="gdpr_nodes_phase2.json")
    args = parser.parse_args()

    # ── Load nodes ────────────────────────────────────────────────────────
    print("Loading nodes...")
    with open(args.iso_file) as f:
        iso_raw = json.load(f)
    with open(args.gdpr_file) as f:
        gdpr_raw = json.load(f)

    iso_nodes  = [RequirementNode.from_dict(n) for n in iso_raw]
    gdpr_nodes = [RequirementNode.from_dict(n) for n in gdpr_raw]
    all_nodes  = iso_nodes + gdpr_nodes

    print(f"  ISO: {len(iso_nodes)}  GDPR: {len(gdpr_nodes)}")

    # ── Apply Tier 1 ──────────────────────────────────────────────────────
    applier = Tier1EnrichmentApplier()
    applier.load()
    applier.apply(iso_nodes)

    # ── Apply tier2 if available ──────────────────────────────────────────
    # tier2 can be at multiple locations depending on cwd
    tier2_path = Path("enrichment/tier2_generated.json")
    if not tier2_path.exists():
        tier2_path = Path(__file__).parent / "tier2_generated.json"
    if tier2_path.exists():
        with open(tier2_path) as f:
            tier2 = json.load(f)
        t2_applied = 0
        no_bd_count = sum(1 for n in all_nodes if not n.business_description)
        for n in all_nodes:
            if not n.business_description and n.ref in tier2:
                n.business_description = tier2[n.ref].get("business_description","")
                n.query_keywords = tier2[n.ref].get("query_keywords",{})
                t2_applied += 1
        print(f"  Tier2 loaded: {len(tier2)} entries, {no_bd_count} nodes need BD")
        print(f"  Tier2 applied: {t2_applied} nodes")
    else:
        print(f"  Tier2 not found at: {tier2_path} — GDPR nodes will have no BD")

    # ── Preview or apply patches ──────────────────────────────────────────
    if args.dry_run:
        print("\n[DRY RUN] Patch preview:\n")
        for ref, patch in KEYWORD_PATCHES.items():
            node = next((n for n in all_nodes if n.ref == ref), None)
            if not node:
                print(f"  {ref}: NOT FOUND in nodes")
                continue
            existing = node.query_keywords or {}
            new_pract = [k for k in patch.get("practitioner",[])
                         if k not in existing.get("practitioner",[])]
            new_scen  = [k for k in patch.get("scenario",[])
                         if k not in existing.get("scenario",[])]
            if new_pract or new_scen:
                print(f"  {ref} — {(node.title or '')[:50]}")
                if new_pract:
                    print(f"    +practitioner ({len(new_pract)}): {new_pract[:3]}...")
                if new_scen:
                    print(f"    +scenario ({len(new_scen)}): {new_scen[:2]}...")
        print(f"\nTotal nodes to patch: {len(KEYWORD_PATCHES)}")
        return

    # ── Apply patches ─────────────────────────────────────────────────────
    count, patched_refs = apply_patches(all_nodes, KEYWORD_PATCHES)
    print(f"\nPatches applied: {count} nodes")
    for ref in patched_refs:
        node = next(n for n in all_nodes if n.ref == ref)
        kw = node.query_keywords or {}
        pract_count = len(kw.get("practitioner",[]))
        scen_count  = len(kw.get("scenario",[]))
        print(f"  {ref:12s}: {pract_count} practitioner, {scen_count} scenario keywords")

    # ── Save updated nodes ────────────────────────────────────────────────
    if not args.dry_run:
        iso_out = [n.to_dict() if hasattr(n,"to_dict") else vars(n)
                   for n in iso_nodes]
        gdpr_out = [n.to_dict() if hasattr(n,"to_dict") else vars(n)
                    for n in gdpr_nodes]

        with open(args.iso_file, "w") as f:
            json.dump(iso_out, f, indent=2, ensure_ascii=False)
        with open(args.gdpr_file, "w") as f:
            json.dump(gdpr_out, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved updated node files")

    # ── Rebuild ChromaDB index ────────────────────────────────────────────
    if not args.no_rebuild and not args.dry_run:
        print("\nRebuilding ChromaDB index...")
        from vector.indexer import VectorIndexer

        indexer = VectorIndexer(
            chroma_host     = args.chroma_host,
            chroma_port     = args.chroma_port,
            embedding_model = "text-embedding-3-large",
        )
        indexer.index_all(iso_nodes, gdpr_nodes, reset=True)
        print("✓ Index rebuilt")

    print("\nDone. Run tests:")
    print("  python3 test_keyword_patches.py --chroma-host localhost")


if __name__ == "__main__":
    main()
