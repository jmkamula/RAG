"""
scripts/build_must_index.py — index every MUST/SHOULD in the catalog into
ChromaDB for semantic-search-based extraction.

Background:
    Leaf-level collections (iso27001_2022, gdpr_2016_679, arioncombly_all) are
    already indexed by vector.indexer for chat retrieval. This script adds a
    FINER-GRAINED collection at the per-MUST level (~3271 vectors) so the
    extractor can pose targeted queries:

        "for MUST item:A.5.18:rev_sla_met, find doc passages that ground it"

    instead of the current single-shot "extract everything from this doc against
    these N controls" prompt that the audit on 2026-06-26 measured at 17%
    median yield.

Vector document composition (per MUST):
    - Standard + control_ref + MUST id (header)
    - Parent leaf title + evidence_type
    - Parent leaf description (practitioner-language enrichment)
    - The MUST text itself (primary signal)
    - Rationale citation (e.g. "27002:5.18 — provisioning")

Embedding model:
    text-embedding-3-small (same as the existing leaf collections — keeps the
    catalog/MUST vector spaces compatible for future hybrid retrieval).

Idempotent — re-running upserts by `must_id` key.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Make repo root importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from enrichment.documents import document_requirements as drm
from vector.indexer import OpenAIEmbeddingFunction


COLLECTION_NAME = "musts_arioncomply"


def _build_must_document(req: "drm.EvidenceRequirement", item: "drm.ChecklistItem") -> str:
    """
    Compose the embedded text for one MUST/SHOULD.

    Layer order (most → least semantically central):
      1. Header — standard, control_ref, MUST id
      2. Parent leaf identity — title + evidence_type
      3. Parent leaf description — practitioner-language context (Tier-1
         enrichment lives here)
      4. The MUST/SHOULD text itself
      5. Rationale citation (27002:X.Y pointer, sometimes with a few words)

    Layer 3 carries the 27002-flavor practitioner language without shipping
    27002 verbatim (copyright-safe; curation has paraphrased).
    """
    parts = [
        f"{req.standard_id} {req.control_ref} :: {item.id}",
        f"Leaf: {req.title} (evidence_type={req.evidence_type})",
    ]
    if req.description:
        parts.append(f"Context: {req.description}")
    parts.append(f"{item.category.upper()}: {item.text}")
    if item.rationale:
        parts.append(f"Rationale: {item.rationale}")
    return "\n".join(p for p in parts if p and p.strip())


def _build_must_metadata(req: "drm.EvidenceRequirement", item: "drm.ChecklistItem") -> dict:
    """
    ChromaDB metadata — must be str/int/float/bool, no lists.

    Filterable axes that the extractor / future advisory will query on:
      - must_id (primary)
      - leaf_id (req:control_ref:slug)
      - control_ref, standard_id, evidence_type
      - category (must / should)
      - gdpr_aligned (some MUSTs are GDPR-required even on ISO leaves)
    """
    return {
        "must_id":         item.id,
        "leaf_id":         req.id,
        "control_ref":     req.control_ref,
        "standard_id":     req.standard_id,
        "evidence_type":   req.evidence_type,
        "category":        item.category,
        "gdpr_aligned":    bool(item.gdpr_aligned),
        "trigger_type":    req.trigger_type,
        "leaf_title":      (req.title or "")[:200],
    }


def _collect_items() -> list[tuple]:
    """
    Walk document_requirements.py and yield (req, item) pairs for every
    ChecklistItem in must_contain + should_contain across every
    EvidenceRequirement.
    """
    pairs = []
    seen_ids: set[str] = set()
    for attr in dir(drm):
        obj = getattr(drm, attr)
        if not isinstance(obj, drm.EvidenceRequirement):
            continue
        for item in list(obj.must_contain) + list(obj.should_contain):
            if item.id in seen_ids:
                # Defensive: a misconfiguration could repeat ids across leaves.
                # Keep the first occurrence so the index stays deterministic.
                continue
            seen_ids.add(item.id)
            pairs.append((obj, item))
    return pairs


def build_index(
    chroma_path: str,
    model:       str = "text-embedding-3-small",
    reset:       bool = False,
    dry_run:     bool = False,
) -> dict:
    import chromadb
    from chromadb.config import Settings

    pairs = _collect_items()
    n_must   = sum(1 for _, it in pairs if it.category == "must")
    n_should = sum(1 for _, it in pairs if it.category == "should")
    print(f"Catalog walk: {len(pairs)} items ({n_must} MUSTs + {n_should} SHOULDs)")
    if dry_run:
        # Show 3 sample documents so the user can sanity-check composition
        for req, item in pairs[:3]:
            print()
            print("─" * 70)
            print(_build_must_document(req, item))
        print()
        print("(dry-run — no Chroma writes)")
        return {"items": len(pairs), "dry_run": True}

    client = chromadb.PersistentClient(
        path     = chroma_path,
        settings = Settings(anonymized_telemetry=False),
    )

    embed_fn = OpenAIEmbeddingFunction(model=model)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Dropped existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name              = COLLECTION_NAME,
        embedding_function = embed_fn,
    )

    # Build batches keyed by must_id (ChecklistItem.id) — idempotent upsert.
    BATCH = 100
    t0 = time.time()
    total = 0
    for batch_start in range(0, len(pairs), BATCH):
        batch = pairs[batch_start:batch_start + BATCH]
        ids   = [item.id for _, item in batch]
        docs  = [_build_must_document(req, item) for req, item in batch]
        metas = [_build_must_metadata(req, item) for req, item in batch]

        collection.upsert(ids=ids, documents=docs, metadatas=metas)
        total += len(batch)
        elapsed = time.time() - t0
        rate    = total / elapsed if elapsed > 0 else 0
        eta     = (len(pairs) - total) / rate if rate > 0 else 0
        print(f"  upserted {total}/{len(pairs)}  ({rate:.0f}/s  eta {eta:.0f}s)")

    elapsed = time.time() - t0
    print()
    print(f"Done: {total} MUSTs indexed in {elapsed:.1f}s")
    print(f"Collection: {COLLECTION_NAME}  count={collection.count()}")
    return {"items": total, "elapsed_s": round(elapsed, 1),
            "collection": COLLECTION_NAME, "count": collection.count()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--chroma-path", default=str(Path(__file__).resolve().parent.parent / "chroma_db"),
                   help="Path to Chroma persist dir (default: <repo>/chroma_db)")
    p.add_argument("--model", default="text-embedding-3-small",
                   help="OpenAI embedding model (default: text-embedding-3-small)")
    p.add_argument("--reset", action="store_true",
                   help="Drop the collection before rebuilding")
    p.add_argument("--dry-run", action="store_true",
                   help="Show sample documents, no Chroma writes")
    args = p.parse_args(argv)

    build_index(
        chroma_path = args.chroma_path,
        model       = args.model,
        reset       = args.reset,
        dry_run     = args.dry_run,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
