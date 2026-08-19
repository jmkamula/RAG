#!/usr/bin/env python3
"""Ship 82'.a — 2-pass structured GT authoring via Claude Opus.

Problem framed by Ship 81'.d retro: every extractor path plateaus at
15-17% strict precision on the 5-doc measurement corpus. Root cause is
NOT extractor limits — it's GT authoring bias. My hand-authored GT
enumerates ~100 satisfies MUSTs across 5 docs; the extractors surface
~400 findings; the delta (~300) becomes "unknown FPs" that may include
legitimate attributions I didn't enumerate.

Solution: independent LLM-authored GT via Claude Opus (different model
family than the extractor's gpt-4.1 — breaks self-reference bias).

Flow per doc:
  Pass 1 (scope enumeration):
    Prompt Claude Opus with:
      - Doc text (or excerpt if >30K)
      - Full leaf catalog for the tenant's enrolled standards, one
        line per leaf (control_ref + title + short description)
    Ask: "which leaves are IN SCOPE for this document?"
    Expected output: JSON list of leaf_ids
    Cost per doc: ~$0.30 with claude-opus-4-7

  Pass 2 (verdict per in-scope MUST):
    For each in-scope leaf's MUSTs (~5-8 per leaf, batched 10 per LLM call):
      Prompt: "For each MUST, verdict:
        satisfies | partial | not_satisfies | not_applicable  + quote"
    Expected output: JSON verdicts + quotes
    Cost per doc: ~$1-2 depending on in-scope breadth

Output: `docs/ground_truth/llm_authored/{doc_slug}_expected.yaml`
in the same shape as hand-authored GT (must_id / verdict / confidence /
quote / rationale).

Model: claude-opus-4-7 via rag.llm_client (Anthropic wire protocol).
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
load_dotenv("/data/arioncomply/.env")

REPO = Path("/data/arioncomply")
sys.path.insert(0, str(REPO))

from rag.llm_client import call as llm_call

# 5-doc baseline (same as ship77/78/80 measurements)
DOCS = {
    "dpia":     ("5f59f505-45a2-4e7d-ba76-c4c6f4b2e08a",
                 "Data Protection Impact Assessment (DPIA) Procedure.docx"),
    "ropa":     ("28d9086c-37a1-4dce-b129-a3afd4e5bb18",
                 "Records of Processing Activities.docx"),
    "consent":  ("10287fa5-f757-420b-98a4-ee9e34d02d25",
                 "Consent Management Procedure.docx"),
    "proc_ops": ("453c55b3-1863-4461-90cb-f7ad058029f2",
                 "Processor Operations Procedures.docx"),
    "dqa":      ("fbb179a2-f565-4947-9d95-d9b3d6375691",
                 "Data Quality Accuracy Procedure.docx"),
}

TENANT_ID = "00000000-0000-0000-0000-000000000001"
GT_OUT_DIR = REPO / "docs" / "ground_truth" / "llm_authored"
GT_OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "claude-opus-4-7"


def _fetch_doc_text(upload_id: str) -> str:
    """Load the doc's parsed text via the intake reader (same shape the
    extractor sees). Reads storage_path from document_uploads then parses
    the file with rag.intake.readers.read_document.
    """
    import psycopg2
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (TENANT_ID,))
            cur.execute(
                "SELECT filename, storage_path FROM document_uploads "
                "WHERE id = %s::uuid LIMIT 1",
                (upload_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise RuntimeError(f"upload_id {upload_id} not found")
    filename, storage_path = row
    if not storage_path or not Path(storage_path).exists():
        raise RuntimeError(f"storage_path missing for {upload_id}: {storage_path}")
    from rag.intake.readers import read_document
    parsed = read_document(file_path=storage_path, original_filename=filename)
    # Prefer markdown (structure preserved); fall back to full_text
    return parsed.markdown or parsed.full_text or ""


def _fetch_leaf_catalog() -> list[dict]:
    """Return all leaves in enrolled standards with title + brief."""
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (er:EvidenceRequirement)
                WHERE er.standard_id IN ['ISO27001:2022', 'ISO27701:2019', 'GDPR:2016/679']
                RETURN er.id AS leaf_id, er.control_ref AS control_ref,
                       er.standard_id AS standard_id, er.title AS title
                ORDER BY standard_id, control_ref, leaf_id
                """
            ).data()
    finally:
        driver.close()
    return rows


def _fetch_musts_for_leaves(leaf_ids: list[str]) -> dict[str, list[dict]]:
    """{leaf_id: [{must_id, text}]} for the given leaves."""
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    try:
        with driver.session() as s:
            rows = s.run(
                """
                MATCH (er:EvidenceRequirement)-[:MUST_CONTAIN]->(ci:ChecklistItem)
                WHERE er.id IN $leaf_ids
                RETURN er.id AS leaf_id, ci.id AS must_id, ci.text AS text
                ORDER BY leaf_id, must_id
                """, leaf_ids=leaf_ids
            ).data()
    finally:
        driver.close()
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r["leaf_id"], []).append({
            "must_id": r["must_id"], "text": r["text"] or "",
        })
    return out


_PASS1_SYSTEM = """You are a compliance auditor.

Given a document and a catalog of compliance leaves (control + title), decide which leaves are IN SCOPE for the document — meaning the document is the kind of artifact that could carry evidence for those leaves.

Return strict JSON: {"in_scope_leaves": ["req:X:Y", "req:A:B", ...]}

Rules:
- Be inclusive but principled. A DPIA procedure is in-scope for the DPIA leaf (Art.35:dpia_procedure) AND arguably for privacy-program leaves it touches (Art.5, Art.24, Art.25). But it is NOT in-scope for physical security leaves (A.7.1-A.7.14) even if it mentions premises briefly.
- Include leaves the document could evidence, even if unsatisfied.
- Do NOT include leaves that are simply mentioned in passing.
- Return leaf IDs verbatim from the catalog.
- Return JSON only."""


_PASS2_SYSTEM = """You are a compliance auditor.

For each MUST item in the batch, judge whether the document contains evidence satisfying it.

Return strict JSON:
{"verdicts": [
  {"must_id": "item:X:Y",
   "verdict": "satisfies" | "partial" | "not_satisfies" | "not_applicable",
   "confidence": "high" | "medium" | "low",
   "quote": "<verbatim quote from doc, or empty>",
   "rationale": "<one-sentence reason>"},
  ...
]}

Verdict definitions:
- "satisfies": the document has language a strict auditor would accept as complete evidence for this MUST
- "partial": the document addresses the MUST's intent but lacks specificity, completeness, or required attributes
- "not_satisfies": the MUST is in the doc's scope but the doc lacks evidence
- "not_applicable": the MUST is not in scope for this document type

Rules:
- Quote must be verbatim substring from the doc (≤ 250 chars).
- Empty quote when verdict is "not_satisfies" or "not_applicable".
- Do not fabricate evidence — only cite text that actually appears.
- Return one verdict per input must_id, preserving order.
- Return JSON only."""


def _pass1_scope(doc_text: str, catalog: list[dict], doc_name: str) -> list[str]:
    """Ask Claude which leaves are in-scope for this doc."""
    doc_excerpt = doc_text[:28000]  # cap so total prompt < 60K
    catalog_lines = [
        f"  {r['leaf_id']}  |  {r['control_ref']} ({r['standard_id']})  |  {r['title'] or '(no title)'}"
        for r in catalog
    ]
    user = (
        f"DOCUMENT ({doc_name}):\n{doc_excerpt}\n\n"
        f"CATALOG ({len(catalog)} leaves):\n" + "\n".join(catalog_lines) +
        "\n\nReturn JSON with in_scope_leaves."
    )
    t0 = time.time()
    resp = llm_call(
        system      = _PASS1_SYSTEM,
        user        = user,
        model       = MODEL,
        purpose     = "extractor",
        max_tokens  = 4000,
        temperature = 0.1,
        timeout_s   = 240,
    )
    dt = time.time() - t0
    if resp.error:
        raise RuntimeError(f"Pass 1 LLM error: {resp.error}")
    text = resp.text or ""
    # Claude may wrap JSON in ```json ... ```
    if "```" in text:
        text = text.split("```json")[-1].split("```")[0] if "```json" in text \
               else text.split("```")[1] if text.count("```") >= 2 else text
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  Pass 1 JSON parse error: {e}", file=sys.stderr)
        print(f"  Raw: {text[:300]!r}", file=sys.stderr)
        return []
    print(f"  Pass 1 ({dt:.1f}s, {len(data.get('in_scope_leaves', []))} leaves)")
    return data.get("in_scope_leaves", [])


def _pass2_verdicts(
    doc_text: str,
    doc_name: str,
    musts_by_leaf: dict[str, list[dict]],
) -> list[dict]:
    """Ask Claude for a verdict per in-scope MUST (batched)."""
    all_musts = []
    for leaf_id, musts in musts_by_leaf.items():
        for m in musts:
            all_musts.append({"leaf_id": leaf_id, **m})
    if not all_musts:
        return []
    print(f"  Pass 2: {len(all_musts)} MUSTs to verdict")

    doc_excerpt = doc_text[:20000]  # keep prompt lean; Pass 1 already saw full doc
    BATCH_SIZE = 10
    verdicts = []
    for i in range(0, len(all_musts), BATCH_SIZE):
        batch = all_musts[i : i + BATCH_SIZE]
        must_lines = []
        for m in batch:
            slug = m["must_id"].split(":")[-1]
            text = (m.get("text") or "").strip()[:200]
            must_lines.append(f"  - {m['must_id']}  |  {slug}  |  {text}")
        user = (
            f"DOCUMENT ({doc_name}):\n{doc_excerpt}\n\n"
            f"BATCH OF MUSTs (id | slug | description):\n" +
            "\n".join(must_lines) +
            "\n\nReturn JSON with per-MUST verdicts."
        )
        t0 = time.time()
        try:
            resp = llm_call(
                system      = _PASS2_SYSTEM,
                user        = user,
                model       = MODEL,
                purpose     = "extractor",
                max_tokens  = 3000,
                temperature = 0.1,
                timeout_s   = 240,
            )
        except Exception as e:
            print(f"    batch {i//BATCH_SIZE}: LLM call raised {e}", file=sys.stderr)
            continue
        dt = time.time() - t0
        if resp.error:
            print(f"    batch {i//BATCH_SIZE}: LLM error {resp.error}", file=sys.stderr)
            continue
        text = resp.text or ""
        if "```json" in text:
            text = text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in text and text.count("```") >= 2:
            text = text.split("```", 1)[1].split("```", 1)[0]
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"    batch {i//BATCH_SIZE}: JSON parse error {e}", file=sys.stderr)
            continue
        batch_verdicts = data.get("verdicts", [])
        verdicts.extend(batch_verdicts)
        print(f"    batch {i//BATCH_SIZE} ({dt:.1f}s): {len(batch_verdicts)} verdicts")
    return verdicts


def _write_gt_yaml(doc_key: str, doc_name: str, verdicts: list[dict]) -> Path:
    """Emit YAML matching the shape ship77e_compare.py parses."""
    out_path = GT_OUT_DIR / f"{doc_key}_expected.yaml"
    lines = [
        f"# LLM-authored ground truth for {doc_name}",
        f"# Model: {MODEL} — 2-pass structured (Ship 82'.a).",
        f"# Total verdicts: {len(verdicts)}",
        "",
        f"doc: {doc_name}",
        f"annotator: {MODEL}",
        f"generated_at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        "",
        "musts:",
    ]
    for v in verdicts:
        mid = v.get("must_id") or ""
        verdict = v.get("verdict") or "not_applicable"
        conf = v.get("confidence") or "medium"
        quote = (v.get("quote") or "").replace('"', "'").strip()
        rationale = (v.get("rationale") or "").replace('"', "'").strip()
        lines.append(f"  - must_id: {mid}")
        lines.append(f"    verdict: {verdict}")
        lines.append(f"    confidence: {conf}")
        if quote:
            lines.append(f"    quote: \"{quote[:250]}\"")
        else:
            lines.append(f"    quote: \"\"")
        if rationale:
            lines.append(f"    rationale: \"{rationale[:200]}\"")
        lines.append("")
    out_path.write_text("\n".join(lines) + "\n")
    return out_path


def author_gt_for_doc(doc_key: str, upload_id: str, doc_name: str,
                     catalog: list[dict]) -> dict:
    """Full 2-pass authoring for one doc. Returns stats dict."""
    stats = {"doc_key": doc_key, "in_scope_leaves": 0,
             "verdicts_total": 0, "verdicts_by_verdict": {}, "path": None}

    print(f"\n=== {doc_key}: {doc_name} ===")
    doc_text = _fetch_doc_text(upload_id)
    print(f"  Doc text: {len(doc_text)} chars")

    # Pass 1: scope
    in_scope_leaves = _pass1_scope(doc_text, catalog, doc_name)
    stats["in_scope_leaves"] = len(in_scope_leaves)
    if not in_scope_leaves:
        print(f"  Pass 1 returned no leaves — skipping doc")
        return stats

    # Pass 2: verdicts per MUST on in-scope leaves
    musts_by_leaf = _fetch_musts_for_leaves(in_scope_leaves)
    verdicts = _pass2_verdicts(doc_text, doc_name, musts_by_leaf)
    stats["verdicts_total"] = len(verdicts)
    from collections import Counter
    stats["verdicts_by_verdict"] = dict(Counter(v.get("verdict", "?") for v in verdicts))

    # Write YAML
    out_path = _write_gt_yaml(doc_key, doc_name, verdicts)
    stats["path"] = str(out_path.name)
    print(f"  wrote {out_path} — {stats['verdicts_total']} verdicts "
          f"({stats['verdicts_by_verdict']})")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="Only run for this doc_key (e.g. 'dqa')")
    args = ap.parse_args()

    catalog = _fetch_leaf_catalog()
    print(f"Loaded leaf catalog: {len(catalog)} leaves")

    docs_to_run = DOCS
    if args.only:
        if args.only not in DOCS:
            print(f"Unknown doc_key: {args.only}", file=sys.stderr)
            sys.exit(2)
        docs_to_run = {args.only: DOCS[args.only]}

    total_stats = []
    t_start = time.time()
    for doc_key, (upload_id, doc_name) in docs_to_run.items():
        stats = author_gt_for_doc(doc_key, upload_id, doc_name, catalog)
        total_stats.append(stats)

    print(f"\n=== TOTALS (elapsed {int(time.time()-t_start)}s) ===")
    for s in total_stats:
        print(f"  {s['doc_key']:<10} in_scope={s['in_scope_leaves']:>3} "
              f"verdicts={s['verdicts_total']:>3}  {s.get('verdicts_by_verdict', {})}")


if __name__ == "__main__":
    main()
