"""
scripts/prototype_semantic_extract.py — Phase 2 semantic-search recall.

Layered on top of the current single-shot LLM extractor. Operates in
**recall-gap-filling mode**: for each MUST that the current extractor left
unbound on a doc whose parent leaf IS bound (≥1 finding elsewhere in the
leaf), run semantic search for the MUST against this doc's passages, LLM-
verify candidates, emit net-new bindings.

Rationale (see [[llm-narrative-under-discovery-audit-2026-06-26]]):
  - Current extractor's failure mode = misses specific MUSTs in details-dense
    passages where it has full-doc attention but limited budget per item.
  - Semantic search's failure mode (v1 attempt) = strict per-passage verify
    rejects implicit coverage; loses cross-passage reasoning.
  - Inverse failure modes → use semantic search ONLY for the gap, not as a
    replacement. Precision on known-unfilled MUSTs > recall on fresh docs.

Pipeline:
  1. Load current document_findings for the doc; compute (leaf_id → bound_ids)
  2. For each leaf with ≥1 binding, identify UNFILLED MUSTs (catalog - bound)
  3. Fetch the unfilled MUSTs' embeddings from musts_arioncomply
  4. Load + embed this doc's passages (paragraph-chunked)
  5. For each unfilled MUST: cosine-rank passages, take top-K above threshold
  6. LLM-verify each (MUST, passage) candidate
  7. Emit one net-new finding per yes

NOT wired into production extract() path. Pure measurement tool until A/B
results stabilise. Output is a JSON report on stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.config import Settings
from vector.indexer import OpenAIEmbeddingFunction


# ── Config ──────────────────────────────────────────────────────────────────

EMBED_MODEL    = "text-embedding-3-small"
VERIFY_MODEL   = "claude-sonnet-4-6"
COLLECTION     = "musts_arioncomply"

# Phase 2 retrieval
TOP_K_PASSAGES_PER_MUST    = 3       # passages per unfilled MUST
SIM_DISTANCE_THRESHOLD     = 1.05    # cosine distance; lower = more similar
MIN_PASSAGE_CHARS          = 80
MAX_PASSAGE_CHARS          = 1500

VERIFY_TIMEOUT_S           = 30
MIN_EVIDENCE_QUOTE_CHARS   = 40

TENANT_ID = "00000000-0000-0000-0000-000000000001"


# ── Catalog access ──────────────────────────────────────────────────────────

def _load_catalog_leaves() -> dict[str, dict]:
    """Return {leaf_id: {must_ids: set, must_texts: dict[must_id, text],
                         leaf_title: str, control_ref: str,
                         standard_id: str, evidence_type: str}}."""
    from enrichment.documents import document_requirements as drm
    out: dict[str, dict] = {}
    for attr in dir(drm):
        obj = getattr(drm, attr)
        if not isinstance(obj, drm.EvidenceRequirement):
            continue
        must_ids:    set[str]      = set()
        must_texts:  dict[str, str] = {}
        for ci in list(obj.must_contain):
            must_ids.add(ci.id)
            must_texts[ci.id] = ci.text
        out[obj.id] = {
            "must_ids":      must_ids,
            "must_texts":    must_texts,
            "leaf_title":    obj.title,
            "control_ref":   obj.control_ref,
            "standard_id":   obj.standard_id,
            "evidence_type": obj.evidence_type,
        }
    return out


def _must_to_leaf_index(catalog: dict[str, dict]) -> dict[str, str]:
    """Reverse map: must_id → leaf_id (for findings → leaves resolution)."""
    out: dict[str, str] = {}
    for leaf_id, info in catalog.items():
        for mid in info["must_ids"]:
            out[mid] = leaf_id
    return out


# ── DB access ───────────────────────────────────────────────────────────────

def _build_pg_conn():
    import psycopg2
    url = os.getenv("DATABASE_URL")
    if not url:
        env = Path(__file__).resolve().parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("DATABASE_URL="):
                    url = line.split("=", 1)[1].strip()
                    break
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(url)


def _load_doc(conn, filename: str) -> tuple[str, str]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s::text, false)", (TENANT_ID,),
        )
        cur.execute(
            """
            SELECT du.id::text, dt.markdown
              FROM document_uploads du
              LEFT JOIN document_text dt ON dt.upload_id = du.id
             WHERE du.tenant_id = %s::uuid
               AND du.filename  = %s
               AND du.extraction_status = 'completed'
             ORDER BY du.uploaded_at DESC
             LIMIT 1
            """,
            (TENANT_ID, filename),
        )
        row = cur.fetchone()
        return (row[0], row[1] or "") if row else ("", "")


def _load_current_findings(conn, filename: str) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s::text, false)", (TENANT_ID,),
        )
        cur.execute(
            """
            SELECT df.checklist_item_id, df.control_ref, df.standard_id,
                   df.status, LEFT(df.excerpt, 200), df.inference_source
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE cd.tenant_id = %s::uuid
               AND cd.filename  = %s
               AND df.is_active = TRUE
               AND df.inference_source IN ('extracted', 'leaf_scan')
            """,
            (TENANT_ID, filename),
        )
        return [
            {
                "must_id":     r[0],
                "control_ref": r[1],
                "standard_id": r[2],
                "status":      r[3],
                "excerpt":     r[4],
                "source":      r[5],
            }
            for r in cur.fetchall()
        ]


# ── Doc passages ────────────────────────────────────────────────────────────

def _chunk_passages(markdown: str) -> list[str]:
    raw = [p.strip() for p in markdown.split("\n\n")]
    out: list[str] = []
    seen: set[str] = set()
    for p in raw:
        lines = [l.lstrip("#").lstrip(">").lstrip("-").lstrip("*").strip()
                 for l in p.splitlines()]
        text = " ".join(l for l in lines if l).strip()
        if len(text) < MIN_PASSAGE_CHARS:
            continue
        if text in seen:
            continue
        seen.add(text)
        if len(text) > MAX_PASSAGE_CHARS:
            cursor = 0
            while cursor < len(text):
                end = min(cursor + MAX_PASSAGE_CHARS, len(text))
                if end < len(text):
                    sb = text.rfind(". ", cursor, end)
                    if sb > cursor + MIN_PASSAGE_CHARS:
                        end = sb + 1
                chunk = text[cursor:end].strip()
                if len(chunk) >= MIN_PASSAGE_CHARS:
                    out.append(chunk)
                cursor = end
        else:
            out.append(text)
    return out


# ── Semantic similarity helpers ─────────────────────────────────────────────

def _cosine(a, b) -> float:
    """Cosine similarity between two 1-D vectors (lists or numpy arrays)."""
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ── LLM verify ──────────────────────────────────────────────────────────────

def _verify_must(api_key: str, must_id: str, must_text: str, leaf_title: str,
                 passage: str) -> dict:
    user_prompt = f"""You are verifying whether a passage from a tenant's compliance document evidences a specific MUST item that the previous extraction pass missed.

MUST id: {must_id}
Parent leaf: {leaf_title}
MUST text: {must_text}

Passage from the document:
\"\"\"
{passage}
\"\"\"

Does this passage ground the MUST? Reply with ONLY this exact JSON:

{{"grounded": true,  "quote": "verbatim quote from the passage, ≥{MIN_EVIDENCE_QUOTE_CHARS} characters"}}

or

{{"grounded": false, "reason": "one short sentence on why not"}}

Rules:
- grounded=true ONLY when the passage contains specific evidence for THIS MUST.
- Quote MUST be verbatim text from the passage.
- General statements that don't satisfy THIS MUST → grounded=false.
- No prose outside the JSON."""

    body = json.dumps({
        "model":      VERIFY_MODEL,
        "max_tokens": 400,
        "system":     "You are a careful compliance auditor. Output ONLY valid JSON.",
        "messages":   [{"role": "user", "content": user_prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data    = body,
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=VERIFY_TIMEOUT_S) as resp:
            data = json.loads(resp.read())
        text = data["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.strip("`").lstrip("json").strip()
        return json.loads(text)
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        return {"grounded": False, "reason": f"verify_error: {type(e).__name__}"}
    except Exception as e:
        return {"grounded": False, "reason": f"unexpected: {type(e).__name__}: {e}"}


# ── Phase 2 driver ──────────────────────────────────────────────────────────

def run(filename: str, api_key: str, *, verbose: bool = False) -> dict:
    pg = _build_pg_conn()
    upload_id, markdown = _load_doc(pg, filename)
    current = _load_current_findings(pg, filename)
    if not markdown:
        return {"filename": filename, "upload_id": upload_id,
                "error": "no markdown found in document_text"}

    catalog       = _load_catalog_leaves()
    must_to_leaf  = _must_to_leaf_index(catalog)

    # ── Resolve target_leaves from current findings ─────────────────────────
    leaves_touched: dict[str, set[str]] = {}  # leaf_id → bound must_ids
    for f in current:
        mid = f["must_id"]
        if not mid:
            continue
        leaf_id = must_to_leaf.get(mid)
        if not leaf_id:
            continue
        leaves_touched.setdefault(leaf_id, set()).add(mid)

    if not leaves_touched:
        return {"filename": filename, "upload_id": upload_id,
                "error": "no leaves touched by current findings — Phase 2 has no scope"}

    # Compute unfilled MUSTs per touched leaf
    unfilled_by_leaf: dict[str, list[str]] = {}
    for leaf_id, bound in leaves_touched.items():
        all_musts = catalog[leaf_id]["must_ids"]
        unfilled  = sorted(all_musts - bound)
        if unfilled:
            unfilled_by_leaf[leaf_id] = unfilled

    n_leaves_touched  = len(leaves_touched)
    n_unfilled_total  = sum(len(v) for v in unfilled_by_leaf.values())
    if verbose:
        print(f"  leaves touched: {n_leaves_touched}", file=sys.stderr)
        print(f"  unfilled MUSTs in those leaves: {n_unfilled_total}", file=sys.stderr)

    if n_unfilled_total == 0:
        return {"filename": filename, "upload_id": upload_id,
                "leaves_touched": n_leaves_touched,
                "unfilled_musts": 0,
                "semantic_findings": 0,
                "note": "every MUST in touched leaves already bound — no Phase 2 gap"}

    # ── Embed doc passages ──────────────────────────────────────────────────
    passages = _chunk_passages(markdown)
    if not passages:
        return {"filename": filename, "upload_id": upload_id,
                "error": "no usable passages"}

    embed_fn = OpenAIEmbeddingFunction(model=EMBED_MODEL)
    t_embed  = time.time()
    passage_vecs_arr = embed_fn(passages)
    # OpenAIEmbeddingFunction wraps in numpy array — normalize to list-of-lists
    passage_vecs = [list(v) for v in passage_vecs_arr]
    t_embed = time.time() - t_embed
    if verbose:
        print(f"  passages: {len(passages)}  ({t_embed:.1f}s embed)", file=sys.stderr)

    # ── Fetch MUST embeddings from existing collection ──────────────────────
    client = chromadb.PersistentClient(
        path     = str(Path(__file__).resolve().parent.parent / "chroma_db"),
        settings = Settings(anonymized_telemetry=False),
    )
    collection = client.get_collection(COLLECTION, embedding_function=embed_fn)

    unfilled_must_ids = [mid for ids in unfilled_by_leaf.values() for mid in ids]
    must_records = collection.get(
        ids     = unfilled_must_ids,
        include = ["embeddings", "metadatas"],
    )

    # Build a map: must_id → (vector, metadata)
    must_vec: dict[str, list[float]] = {}
    must_meta: dict[str, dict]       = {}
    for ix in range(len(must_records["ids"])):
        mid = must_records["ids"][ix]
        must_vec[mid]  = list(must_records["embeddings"][ix])
        must_meta[mid] = must_records["metadatas"][ix] or {}

    # ── For each unfilled MUST: rank passages by cosine, verify top-K ───────
    semantic_findings: list[dict] = []
    skipped_by_threshold = 0
    verify_calls = 0
    t_verify = time.time()
    for ix, mid in enumerate(unfilled_must_ids):
        if mid not in must_vec:
            continue
        mvec = must_vec[mid]
        # Score all passages
        scored = []
        for pix, pvec in enumerate(passage_vecs):
            sim = _cosine(mvec, pvec)
            # ChromaDB-style: distance = 1 - sim (lower = better)
            scored.append((1.0 - sim, pix))
        scored.sort(key=lambda x: x[0])
        top = scored[:TOP_K_PASSAGES_PER_MUST]

        # Verify top-K passages above threshold
        best_finding = None
        for dist, pix in top:
            if dist > SIM_DISTANCE_THRESHOLD:
                skipped_by_threshold += 1
                continue
            passage = passages[pix]
            meta    = must_meta[mid]
            must_text = catalog.get(must_to_leaf[mid], {}).get("must_texts", {}).get(mid, "")
            result = _verify_must(
                api_key   = api_key,
                must_id   = mid,
                must_text = must_text,
                leaf_title= meta.get("leaf_title", ""),
                passage   = passage,
            )
            verify_calls += 1
            if result.get("grounded") and result.get("quote") \
                    and len(result["quote"]) >= MIN_EVIDENCE_QUOTE_CHARS:
                best_finding = {
                    "must_id":     mid,
                    "control_ref": meta.get("control_ref"),
                    "standard_id": meta.get("standard_id"),
                    "evidence_type": meta.get("evidence_type"),
                    "leaf_id":     must_to_leaf[mid],
                    "quote":       result["quote"][:400],
                    "distance":    round(dist, 3),
                    "passage_ix":  pix,
                }
                break  # first grounded passage wins; don't burn more verify calls
        if best_finding:
            semantic_findings.append(best_finding)
        if verbose and (ix + 1) % 20 == 0:
            print(f"  processed {ix + 1}/{len(unfilled_must_ids)} MUSTs "
                  f"(grounded so far: {len(semantic_findings)}, "
                  f"verify calls: {verify_calls})", file=sys.stderr)
    t_verify = time.time() - t_verify

    # ── Per-leaf yield improvement ──────────────────────────────────────────
    yield_by_leaf = {}
    for leaf_id, bound in leaves_touched.items():
        catalog_count = len(catalog[leaf_id]["must_ids"])
        before_pct    = int(round(len(bound) / catalog_count * 100)) if catalog_count else 0
        new_in_leaf   = sum(1 for f in semantic_findings if f["leaf_id"] == leaf_id)
        after         = len(bound) + new_in_leaf
        after_pct     = int(round(after / catalog_count * 100)) if catalog_count else 0
        yield_by_leaf[leaf_id] = {
            "leaf_title":     catalog[leaf_id]["leaf_title"],
            "control_ref":    catalog[leaf_id]["control_ref"],
            "catalog_musts":  catalog_count,
            "before_bound":   len(bound),
            "new_bindings":   new_in_leaf,
            "after_bound":    after,
            "before_pct":     before_pct,
            "after_pct":      after_pct,
        }

    return {
        "filename":            filename,
        "upload_id":           upload_id,
        "passages":            len(passages),
        "leaves_touched":      n_leaves_touched,
        "unfilled_musts":      n_unfilled_total,
        "verify_calls":        verify_calls,
        "skipped_by_threshold":skipped_by_threshold,
        "embed_seconds":       round(t_embed, 1),
        "verify_seconds":      round(t_verify, 1),
        "current_with_must_id":sum(1 for f in current if f["must_id"]),
        "semantic_findings":   len(semantic_findings),
        "yield_by_leaf":       yield_by_leaf,
        "semantic_findings_detail": semantic_findings,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("filename", help="Document filename (e.g. 'HR Security Policy.docx')")
    p.add_argument("--verbose", action="store_true", help="Progress to stderr")
    args = p.parse_args(argv)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        env = Path(__file__).resolve().parent.parent / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    report = run(args.filename, api_key, verbose=args.verbose)
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
