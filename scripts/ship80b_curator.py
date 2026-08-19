#!/usr/bin/env python3
"""Ship 80'.b — LLM-only fingerprint YAML curator.

Explicitly does NOT reuse the deterministic heuristics from
`gen_leaf_scan_catalog.py` — those produced the current broken
skeletons that cause the 66% recall floor. Instead, each MUST gets
a fresh LLM authoring pass with rich context (leaf title, artefact
shape, control ref, standard, MUST description) and the LLM returns
verb-noun doc-prose keyword tuples in the Ship 38'.b idiom
([corrected, inaccurate] + [validation, forms] style).

The output YAML CONTAINS ONLY LLM-authored keywords. Skeleton
keywords from prior gen_leaf_scan_catalog runs are DISCARDED
(replaced, not merged). This is by design — mixing skeleton noise
back in dilutes the LLM's precision and re-introduces the
[processor, records] failure mode.

Hand-curated additions from prior arcs (Ship 38'.b marker comments)
are preserved by looking for the `# Ship 38'.b curator additions`
comment marker and rescuing tuples underneath.

Usage:
    # Single leaf (by leaf-id — will create YAML if missing)
    python scripts/ship80b_curator.py --leaf req:Art.7:consent_register

    # Batch from file (one leaf-id per line, blank lines OK)
    python scripts/ship80b_curator.py --leaves-from-file targets.txt

    # Dry-run — print what would be written, don't touch disk
    python scripts/ship80b_curator.py --leaf X --dry-run

    # Verbose — show LLM per-MUST timing + tuple count
    python scripts/ship80b_curator.py --leaf X --verbose

Model + cost: gpt-4.1-mini. ~$0.02 per leaf (5 MUSTs avg). Pilot on
49 leaves ≈ $1.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv("/data/arioncomply/.env")

REPO = Path("/data/arioncomply")
sys.path.insert(0, str(REPO))

CATALOG_DIR = REPO / "db" / "must_fingerprints"


# ---------------------------------------------------------------------------
# Catalog lookup (Neo4j is authoritative for MUST descriptions + leaf titles)
# ---------------------------------------------------------------------------

def _fetch_leaf_from_catalog(leaf_id: str):
    """Return (leaf_title, control_ref, standard_id, [(must_id, description), ...])
    from Neo4j. None if not found."""
    import os
    from neo4j import GraphDatabase
    uri, user, pw = os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        print("ERROR: NEO4J_URI/USER/PASSWORD not set", file=sys.stderr)
        sys.exit(2)
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    try:
        cypher = """
        MATCH (er:EvidenceRequirement {id: $leaf_id})
        OPTIONAL MATCH (rn:RequirementNode {ref: er.control_ref, standard_id: er.standard_id})
        OPTIONAL MATCH (er)-[:MUST_CONTAIN]->(item:ChecklistItem)
        RETURN
          er.title       AS leaf_title,
          er.control_ref AS control_ref,
          er.standard_id AS standard_id,
          rn.title       AS control_title,
          collect({id: item.id, text: item.text}) AS items
        """
        with driver.session() as s:
            row = s.run(cypher, leaf_id=leaf_id).single()
    finally:
        driver.close()
    if not row or not row["control_ref"]:
        return None
    items = [(it["id"], it.get("text") or "")
             for it in (row["items"] or []) if it.get("id")]
    return {
        "leaf_id":       leaf_id,
        "leaf_title":    row["leaf_title"] or "",
        "control_ref":   row["control_ref"],
        "standard_id":   row["standard_id"],
        "control_title": row.get("control_title") or "",
        "musts":         items,
    }


def _yaml_path_for(leaf_id: str) -> Path:
    slug = leaf_id.replace(":", "_").replace(".", "_") + ".yaml"
    return CATALOG_DIR / slug


# ---------------------------------------------------------------------------
# Rescue Ship 38'.b hand-curated additions (preserved across regeneration)
# ---------------------------------------------------------------------------

_CURATOR_MARKER = "# Ship 38'.b curator additions"


def _rescue_curator_tuples(path: Path) -> dict[str, list[list[str]]]:
    """Read an existing YAML and extract tuples that appear under a
    '# Ship 38'.b curator additions' marker, indexed by must_id.
    Returns {} if the file doesn't exist or no marker present."""
    if not path.exists():
        return {}
    rescued: dict[str, list[list[str]]] = {}
    current_must: Optional[str] = None
    in_rescue_block = False
    kw_line_re = re.compile(r"^\s*-\s*\[([^\]]+)\]\s*$")
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        m = re.match(r'\s*-\s*must_id:\s*"([^"]+)"', line)
        if m:
            current_must = m.group(1)
            in_rescue_block = False
            continue
        if _CURATOR_MARKER in line:
            in_rescue_block = True
            continue
        # New comment or new section terminates the rescue window
        if in_rescue_block:
            if line.startswith("  - must_id:") or (line.strip().startswith("#") and _CURATOR_MARKER not in line):
                in_rescue_block = False
            else:
                mm = kw_line_re.match(line)
                if mm and current_must:
                    toks = [t.strip().lower() for t in mm.group(1).split(",") if t.strip()]
                    if toks:
                        rescued.setdefault(current_must, []).append(toks)
    return rescued


# ---------------------------------------------------------------------------
# LLM authoring — one call per MUST
# ---------------------------------------------------------------------------

_LLM_SYSTEM = """You are a compliance vocabulary curator authoring fingerprint keyword tuples for a MUST item.

WHAT YOU RETURN
Strict JSON: {"keywords": [["tok1","tok2"], ["tok1","tok2","tok3"], ...]}

HOW THE TUPLES ARE USED
- Each tuple is an AND across substrings: ALL tokens must appear as substrings in a document excerpt for the tuple to fire.
- Multiple tuples are OR'd: ANY tuple firing satisfies the fingerprint.
- Excerpt is normalised (lowercase, punctuation stripped, whitespace collapsed) before matching, so tokens should be lowercase and unpunctuated.

WHAT MAKES A GOOD TUPLE
- 2 or 3 tokens. 4 only when strictly needed.
- Natural doc-prose vocabulary a real compliance document uses when this MUST is satisfied.
- Match the SHAPE of the MUST (prefix in the slug):
  * reg_*   -> REGISTER field: expect column headings, per-row phrasing
              Good: [subject, id, column]  [captured, timestamp]  [logged, source]  [per, record]
  * rev_*   -> REVIEW artefact: cadence + date + reviewer vocab
              Good: [next, review]  [reviewed, annually]  [review, date]  [review, cadence]
  * proc_*  -> PROCEDURE step: action verbs + roles + triggers
              Good: [shall, process]  [triggered, by]  [responsible, for]  [must, notify]
  * scope_* -> SCOPE statement: applicability phrasing
              Good: [applies, to]  [in, scope]  [covers, activities]  [excluded, from]
  * (other) -> policy / plan / other: reason from the MUST description
- Prefer specific short tuples over padded long ones. [correction, tracked] beats [any, correction, procedure, tracked].
- Do NOT copy the MUST slug verbatim: for `reg_subject_id`, do NOT emit [reg, subject]; use [subject, reference] or [data, subject, id].
- Avoid stopwords as standalone tokens. Stopwords: the, of, and, a, an, to, from, for, with, or, is, are, be.
- Avoid single-word tuples unless the word is highly specific and appears only in the target artefact context.

DOMAIN-AWARE VOCABULARY EXAMPLES
- GDPR Art.7 (Consent) doc-prose: consent given, consent captured, opt in, opt out, withdrawal request, unambiguous, freely given, granular, marketing consent, cookie consent, consent banner.
- GDPR Art.30 (RoPA) doc-prose: records of processing, controller record, processor record, retention period, purpose of processing, categories of data, categories of recipients, transfers to third countries.
- GDPR Art.35 (DPIA) doc-prose: data protection impact assessment, DPIA reference, systematic description, necessity assessment, risk assessment, residual risk, prior consultation, art 36.
- ISO 27701 A.7.3 (Subject rights) doc-prose: data subject request, right to erasure, rectification, response within, one month, subject request log.
- ISO 27701 B.8.5 (Transfers/subcontractors) doc-prose: subprocessor, transfer basis, standard contractual clauses, adequacy decision, prior notification, customer authorisation.

QUALITY BAR
- Every tuple must be something an auditor could plausibly grep for in a real document. Ask yourself "would I actually find this phrase in a policy/procedure/register?" — if no, drop it.
- Return 4-6 tuples. Do not pad. Fewer high-quality tuples beats more noisy ones.
- Return JSON only. No prose, no comments."""


def _llm_generate_for_must(
    leaf_title:    str,
    control_ref:   str,
    standard_id:   str,
    control_title: str,
    must_id:       str,
    description:   str,
    verbose:       bool = False,
) -> list[list[str]]:
    from rag.llm_client import call as llm_call
    tail   = must_id.rsplit(":", 1)[-1]
    shape  = tail.split("_", 1)[0] if "_" in tail else ""
    user = (
        f"CONTROL: {control_ref} ({standard_id})\n"
        f"CONTROL TITLE: {control_title}\n"
        f"LEAF ARTEFACT: {leaf_title}\n"
        f"MUST ID: {must_id}\n"
        f"SHAPE PREFIX: {shape or '(none — reason from description)'}\n"
        f"MUST DESCRIPTION:\n{description}\n\n"
        f"Return 4-6 keyword tuples for this MUST. JSON only."
    )
    t0 = time.time()
    resp = llm_call(
        system      = _LLM_SYSTEM,
        user        = user,
        model       = "gpt-4.1-mini",
        purpose     = "other",
        max_tokens  = 500,
        temperature = 0.2,
        timeout_s   = 45,
        response_format = {"type": "json_object"},
    )
    dt = time.time() - t0
    if resp.error:
        print(f"      LLM error on {must_id}: {resp.error}", file=sys.stderr)
        return []
    try:
        data = json.loads(resp.text or "{}")
    except json.JSONDecodeError as e:
        print(f"      JSON parse error on {must_id}: {e}", file=sys.stderr)
        return []
    out: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for kw in data.get("keywords", []) or []:
        if not isinstance(kw, list) or not kw:
            continue
        cleaned = [str(t).strip().lower() for t in kw if str(t).strip()]
        # Drop tuples that are all-stopwords or too long/short
        _STOPWORDS = {"the","of","and","a","an","to","from","for","with","or","is","are","be","in","on","at","by","as"}
        cleaned = [t for t in cleaned if t not in _STOPWORDS]
        if not cleaned or len(cleaned) > 4:
            continue
        key = tuple(sorted(cleaned))
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
    if verbose:
        print(f"      LLM ({dt:.1f}s) -> {len(out)} tuples")
    return out


# ---------------------------------------------------------------------------
# YAML rendering — pure LLM output + rescued hand-curator tuples
# ---------------------------------------------------------------------------

def _render_yaml(
    leaf:          dict,
    must_keywords: dict[str, list[list[str]]],
    rescued:       dict[str, list[list[str]]],
) -> str:
    lines: list[str] = []
    lines.append(f"# Per-MUST fingerprint catalog for {leaf['leaf_id']}")
    lines.append(f"# LLM-authored by Ship 80'.b (curator sweep 2026-08-18).")
    lines.append(f"# Pure LLM-authored keywords + rescued Ship 38'.b curator")
    lines.append(f"# additions if present. Skeleton heuristics from")
    lines.append(f"# gen_leaf_scan_catalog were intentionally discarded.")
    lines.append("")
    lines.append(f"schema_version: 1")
    lines.append(f'target_evidence_requirement: "{leaf["leaf_id"]}"')
    lines.append(f'target_control: "{leaf["control_ref"]}"')
    lines.append(f'target_standard: "{leaf["standard_id"]}"')
    lines.append("")
    lines.append("must_fingerprints:")
    for (must_id, description) in leaf["musts"]:
        # Description: first sentence, cap 140
        desc = (description or must_id.split(":")[-1].replace("_", " ")).split(". ")[0]
        desc_clean = desc.replace('"', "'").strip()
        lines.append(f'  - must_id: "{must_id}"')
        lines.append(f'    description: "{desc_clean[:200]}"')
        lines.append(f"    excerpt_keywords:")
        llm_kws = must_keywords.get(must_id, [])
        for kw in llm_kws:
            lines.append(f"      - [{', '.join(kw)}]")
        rescued_kws = rescued.get(must_id, [])
        if rescued_kws:
            lines.append(f"      {_CURATOR_MARKER}")
            for kw in rescued_kws:
                # Skip if already covered by LLM output
                key = tuple(sorted(kw))
                llm_keys = {tuple(sorted(x)) for x in llm_kws}
                if key in llm_keys:
                    continue
                lines.append(f"      - [{', '.join(kw)}]")
        if not llm_kws and not rescued_kws:
            lines.append("      # (LLM returned no tuples — needs manual review)")
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def curate_one(leaf_id: str, *, dry_run: bool = False, verbose: bool = False) -> dict:
    stats = {"leaf_id": leaf_id, "n_musts": 0, "n_tuples": 0,
             "n_rescued": 0, "created_new": False, "error": None}
    leaf = _fetch_leaf_from_catalog(leaf_id)
    if not leaf:
        stats["error"] = "leaf not in Neo4j catalog"
        return stats
    stats["n_musts"] = len(leaf["musts"])
    path = _yaml_path_for(leaf_id)
    stats["created_new"] = not path.exists()
    rescued = _rescue_curator_tuples(path) if not stats["created_new"] else {}
    stats["n_rescued"] = sum(len(v) for v in rescued.values())

    must_keywords: dict[str, list[list[str]]] = {}
    for (must_id, description) in leaf["musts"]:
        if verbose:
            print(f"    -> {must_id}", flush=True)
        kws = _llm_generate_for_must(
            leaf_title    = leaf["leaf_title"],
            control_ref   = leaf["control_ref"],
            standard_id   = leaf["standard_id"],
            control_title = leaf["control_title"],
            must_id       = must_id,
            description   = description,
            verbose       = verbose,
        )
        must_keywords[must_id] = kws
        stats["n_tuples"] += len(kws)

    yaml_text = _render_yaml(leaf, must_keywords, rescued)

    if dry_run:
        print(yaml_text)
        print("---")
    else:
        path.write_text(yaml_text)
    return stats


def main():
    ap = argparse.ArgumentParser(description="Ship 80'.b LLM-only fingerprint curator")
    ap.add_argument("--leaf", help="Leaf id (req:X:Y)")
    ap.add_argument("--leaves-from-file", help="File with one leaf-id per line")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    targets: list[str] = []
    if args.leaf:
        targets.append(args.leaf)
    if args.leaves_from_file:
        with open(args.leaves_from_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    targets.append(line)
    if not targets:
        ap.error("Must specify --leaf or --leaves-from-file")

    print(f"Curating {len(targets)} leaf(s) — model=gpt-4.1-mini, dry-run={args.dry_run}")
    print()

    totals = {"leaves": 0, "created": 0, "musts": 0,
              "tuples": 0, "rescued": 0, "errors": 0}
    for i, lid in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {lid}")
        stats = curate_one(lid, dry_run=args.dry_run, verbose=args.verbose)
        if stats["error"]:
            print(f"  ERROR: {stats['error']}")
            totals["errors"] += 1
            continue
        totals["leaves"] += 1
        totals["created"] += 1 if stats["created_new"] else 0
        totals["musts"] += stats["n_musts"]
        totals["tuples"] += stats["n_tuples"]
        totals["rescued"] += stats["n_rescued"]
        tag = "CREATED" if stats["created_new"] else "UPDATED"
        rescued_note = f" (+{stats['n_rescued']} rescued Ship 38'.b)" if stats["n_rescued"] else ""
        print(f"  {tag} {_yaml_path_for(lid).name} — {stats['n_musts']} MUSTs, "
              f"{stats['n_tuples']} LLM tuples{rescued_note}")

    print()
    print(f"=== TOTALS ===")
    print(f"  Leaves processed: {totals['leaves']}")
    print(f"  New YAMLs created: {totals['created']}")
    print(f"  MUSTs touched: {totals['musts']}")
    print(f"  LLM tuples emitted: {totals['tuples']}")
    print(f"  Ship 38'.b curator tuples preserved: {totals['rescued']}")
    print(f"  Errors: {totals['errors']}")


if __name__ == "__main__":
    main()
