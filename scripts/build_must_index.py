"""
Build the musts_arioncomply Chroma collection — MUST-level embeddings
across ISO 27001, ISO 27701, and GDPR.

Wave 2 of signal-fusion arc (2026-07-09). The retired 2026-06-26 version
was used as a REPLACEMENT for the pattern path (fingerprint + doc_mappings)
and lost the A/B comparison, so was deleted on 2026-07-03. This rebuild
is used as an ENSEMBLE CONTRIBUTOR — one input signal alongside doc_mappings
and fingerprints in the writer's auto-approve corroboration gate. See
[[27701-intake-arc-2026-07-08]] and [[must-embedding-index-2026-06-26]].

Walks `enrichment/documents/document_requirements.py` — the canonical
catalog union — and upserts every ChecklistItem (must + should) into the
`musts_arioncomply` Chroma collection. Idempotent: rerun on curation
refresh; the upsert keys on `must_id` so stale rows update in place.

Model: `text-embedding-3-small` (matches the leaf-level collections;
same vector space enables future hybrid retrieval).

Cost: ~4300 vectors × 3-small pricing ~= $0.05, ~40s runtime.

Vector document composition — five layers:
  1. Header:      {standard_id} {control_ref} :: {must_id}
  2. Leaf ident:  Leaf: {title} (evidence_type={et})
  3. Leaf desc:   {leaf.description}  (curation practitioner-language)
  4. MUST text:   {item.text}  (primary signal)
  5. Rationale:   Rationale: {item.rationale}

Metadata stored (filterable in Chroma queries):
  must_id, leaf_id, control_ref, standard_id, evidence_type,
  category (must/should), gdpr_aligned, trigger_type, leaf_title
"""
from __future__ import annotations
import os
import sys
import time
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from dotenv import load_dotenv

load_dotenv(str(Path(__file__).parent.parent / ".env"))

from enrichment.documents.document_requirements import (
    ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS, EvidenceRequirement, ChecklistItem,
)


COLLECTION_NAME = "musts_arioncomply"
CHROMA_DIR      = str(Path(__file__).parent.parent / "chroma_db")
EMBED_MODEL     = "text-embedding-3-small"


def _iter_leaves() -> Iterable[EvidenceRequirement]:
    """Union: top-level EvidenceRequirements + DerivedSpec.direct_evidence.

    The loader's canonical membership predicate — matches how
    load_to_neo4j and the extractor read the catalog. Any hand-rolled
    dir(drm) scan misses the DerivedSpec direct_evidence path (2026-06-27
    incident that soft-deleted 96 valid findings).
    """
    for er in ALL_EVIDENCE_REQUIREMENTS:
        yield er
    for ds in ALL_DERIVED_SPECS:
        for er in ds.direct_evidence:
            yield er


def _compose_document(item: ChecklistItem, leaf: EvidenceRequirement) -> str:
    """Five-layer document composition. Header + leaf identity + leaf
    description + MUST text + rationale. Empty layers collapsed."""
    parts: list[str] = []
    parts.append(f"{leaf.standard_id} {leaf.control_ref} :: {item.id}")
    parts.append(f"Leaf: {leaf.title} (evidence_type={leaf.evidence_type})")
    if leaf.description:
        parts.append(leaf.description)
    parts.append(item.text)
    if item.rationale:
        parts.append(f"Rationale: {item.rationale}")
    return "\n".join(parts)


def _compose_metadata(item: ChecklistItem, leaf: EvidenceRequirement) -> dict:
    """Chroma metadata — filterable in queries. Booleans allowed; nested
    dicts / lists NOT allowed (Chroma limitation)."""
    return {
        "must_id":       item.id,
        "leaf_id":       leaf.id,
        "control_ref":   leaf.control_ref,
        "standard_id":   leaf.standard_id,
        "evidence_type": leaf.evidence_type,
        "category":      item.category,          # "must" | "should"
        "gdpr_aligned":  bool(item.gdpr_aligned),
        "trigger_type":  leaf.trigger_type,
        "leaf_title":    leaf.title,
    }


def build_index() -> dict:
    """Idempotent build. Returns a summary dict."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY missing — embeddings collection cannot be built. "
            "Set the key in .env before running."
        )

    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
    embed_fn = OpenAIEmbeddingFunction(
        api_key    = os.getenv("OPENAI_API_KEY"),
        model_name = EMBED_MODEL,
    )

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection(
        name              = COLLECTION_NAME,
        embedding_function= embed_fn,
        metadata          = {"model": EMBED_MODEL, "source": "document_requirements.py"},
    )

    ids:  list[str] = []
    docs: list[str] = []
    mds:  list[dict] = []

    seen_ids: set[str] = set()   # dedup — DerivedSpec.direct_evidence can share MUSTs across specs

    for leaf in _iter_leaves():
        for item in list(leaf.must_contain) + list(leaf.should_contain):
            if item.id in seen_ids:
                continue
            seen_ids.add(item.id)
            ids.append(item.id)
            docs.append(_compose_document(item, leaf))
            mds.append(_compose_metadata(item, leaf))

    if not ids:
        return {"upserted": 0, "collection": COLLECTION_NAME}

    t0 = time.time()
    # Chroma upserts in batches to avoid single-call token limits
    batch_size = 200
    upserted   = 0
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        col.upsert(
            ids       = ids[start:end],
            documents = docs[start:end],
            metadatas = mds[start:end],
        )
        upserted += (end - start) if end <= len(ids) else (len(ids) - start)
        print(f"  upserted {upserted}/{len(ids)}", flush=True)
    elapsed = time.time() - t0

    return {
        "upserted":   upserted,
        "collection": COLLECTION_NAME,
        "elapsed_s":  round(elapsed, 1),
        "final_count": col.count(),
    }


if __name__ == "__main__":
    print(f"Building {COLLECTION_NAME} at {CHROMA_DIR}")
    summary = build_index()
    print()
    print(f"Done. {summary}")
