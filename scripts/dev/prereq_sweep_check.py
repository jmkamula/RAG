"""
Ship 57' MVP-readiness sweep for the per-leaf prerequisites corpus.

Mirrors the Ship 56' deck audit shape: red (blockers) / yellow (curator
flags) / green (informational). Verifies schema, enum validity, ref
resolvability, cardinality, text quality, and LLM-refusal leakage.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/prereq_sweep_check.py
"""
from __future__ import annotations

import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent / "enrichment" / "prerequisites"

REQUIRED_TOP = {"leaf_id", "control_ref", "standard_id", "curation_status",
                "authored_by", "authored_at", "prerequisites"}
REQUIRED_ENTRY = {"ref", "standard_id", "title", "category", "rationale", "good_enough"}
VALID_STDS = {"ISO27001:2022", "ISO27701:2019", "GDPR:2016/679"}
VALID_CATS = {"foundational", "direct", "cross_role"}
VALID_STATUSES = {"draft", "reviewed", "approved"}

# Filler = tacked-on phrase adding no meaning. Restricted to trailing
# position (comma-prefixed OR end-of-string with optional period), because
# mid-sentence uses of these phrases are usually grammatical connectives
# ("essential for accountability") rather than filler. `to ensure that` and
# `in order to ensure` were dropped entirely — almost always structural
# ("must X to ensure Y" = "must X so that Y").
FILLER_PATTERNS = [
    r",\s+for accountability\b",
    r"\bfor accountability\.?\s*$",
    r",\s+for auditability\b",
    r"\bfor auditability\.?\s*$",
    r",\s+for compliance tracking\b",
    r"\bfor compliance tracking\.?\s*$",
    r",\s+for traceability\b",
    r"\bfor traceability\.?\s*$",
]
REFUSAL_PATTERNS = [
    r"^\s*I (cannot|can'?t|am unable|don'?t)",
    r"^\s*As an AI\b",
    r"^\s*I'?m (unable|not able)\b",
    r"^\s*Sorry,? (I|but)\b",
]


def _valid_refs_from_neo4j() -> set[str]:
    """Authoritative valid-ref set — every RequirementNode in the graph."""
    try:
        from neo4j import GraphDatabase
        d = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"),
                  os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")),
        )
        with d.session() as s:
            rows = s.run("MATCH (r:RequirementNode) RETURN r.ref AS ref").data()
        return {r["ref"] for r in rows if r.get("ref")}
    except Exception as e:
        print(f"WARN: Neo4j unavailable ({e}) — ref validity will be skipped.", file=sys.stderr)
        return set()


def main() -> None:
    files = sorted(ROOT.rglob("*.yaml"))
    valid_refs = _valid_refs_from_neo4j()

    parse_errors: list[str] = []
    missing_top: list[tuple[str, list[str]]] = []
    missing_entry: list[tuple[str, int, list[str]]] = []
    bad_std: list[tuple[str, str]] = []
    bad_cat: list[tuple[str, str]] = []
    bad_status: list[tuple[str, str]] = []
    dangling_refs: list[tuple[str, str]] = []
    dup_entries: list[tuple[str, tuple[str, str]]] = []
    empty_rationale: list[str] = []
    empty_good_enough: list[str] = []
    refusals: list[tuple[str, str]] = []
    filler_hits: list[tuple[str, str, str]] = []

    prereq_counts: list[int] = []
    rationale_lens: list[int] = []
    good_enough_lens: list[int] = []
    by_std: Counter = Counter()
    by_cat: Counter = Counter()
    status_counts: Counter = Counter()

    for f in files:
        rel = str(f.relative_to(ROOT))
        try:
            d = yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            parse_errors.append(f"{rel}: {e}")
            continue
        if not isinstance(d, dict):
            parse_errors.append(f"{rel}: not a dict")
            continue

        missing = REQUIRED_TOP - d.keys()
        if missing:
            missing_top.append((rel, sorted(missing)))

        target_std = d.get("standard_id")
        target_ctrl = d.get("control_ref")
        status = d.get("curation_status")

        if target_std and target_std not in VALID_STDS:
            bad_std.append((rel, target_std))
        by_std[target_std] += 1
        if status and status not in VALID_STATUSES:
            bad_status.append((rel, status))
        status_counts[status] += 1

        prereqs = d.get("prerequisites") or []
        if not isinstance(prereqs, list):
            missing_entry.append((rel, -1, ["prerequisites-is-not-a-list"]))
            continue
        prereq_counts.append(len(prereqs))

        seen_keys: set[tuple[str, str]] = set()
        for i, p in enumerate(prereqs):
            if not isinstance(p, dict):
                missing_entry.append((rel, i, ["entry-not-a-dict"]))
                continue
            entry_missing = REQUIRED_ENTRY - p.keys()
            if entry_missing:
                missing_entry.append((rel, i, sorted(entry_missing)))
                continue

            pref = p["ref"]
            pstd = p["standard_id"]
            cat = p["category"]
            rat = (p.get("rationale") or "").strip()
            ge = (p.get("good_enough") or "").strip()

            if pstd not in VALID_STDS:
                bad_std.append((rel, f"prereq {pref}: {pstd}"))
            if cat not in VALID_CATS:
                bad_cat.append((rel, f"prereq {pref}: {cat}"))
            by_cat[cat] += 1

            if valid_refs and pref not in valid_refs:
                dangling_refs.append((rel, pref))
            # NOTE: pref == target_ctrl is legitimate — a leaf under control X
            # can depend on the primary artefact under the same control X (its
            # control-level parent). Not a self-reference.

            key = (pref, pstd)
            if key in seen_keys:
                dup_entries.append((rel, key))
            seen_keys.add(key)

            if not rat:
                empty_rationale.append(f"{rel}[{pref}]")
            else:
                rationale_lens.append(len(rat.split()))
                for pat in REFUSAL_PATTERNS:
                    if re.search(pat, rat, re.IGNORECASE):
                        refusals.append((rel, rat[:80])); break
                for pat in FILLER_PATTERNS:
                    m = re.search(pat, rat, re.IGNORECASE)
                    if m:
                        filler_hits.append((rel, pref, m.group(0)))

            if not ge:
                empty_good_enough.append(f"{rel}[{pref}]")
            else:
                good_enough_lens.append(len(ge.split()))
                for pat in REFUSAL_PATTERNS:
                    if re.search(pat, ge, re.IGNORECASE):
                        refusals.append((rel, ge[:80])); break

    total = len(files)

    def _pct(n): return f"{100.0 * n / total:.1f}%" if total else "-"

    def _stats(nums):
        if not nums: return "n/a"
        return (f"min={min(nums)} med={statistics.median(nums):.0f} "
                f"mean={statistics.mean(nums):.1f} max={max(nums)}  n={len(nums)}")

    def _samples(items, n=5):
        for x in items[:n]:
            print(f"    {x}")
        if len(items) > n:
            print(f"    ... +{len(items)-n} more")

    print("=" * 70)
    print(f"Ship 57' prerequisites corpus sweep — {total} files")
    print("=" * 70)
    print()
    print("── RED (hard blockers) ─────────────────────────────────────────")
    red = 0
    print(f"YAML parse errors:                    {len(parse_errors)}")
    if parse_errors: red += len(parse_errors); _samples(parse_errors)
    print(f"Files missing required top fields:    {len(missing_top)}")
    if missing_top: red += len(missing_top); _samples([f'{r}: {m}' for r,m in missing_top])
    print(f"Entries missing required fields:      {len(missing_entry)}")
    if missing_entry: red += len(missing_entry); _samples([f'{r}[{i}]: {m}' for r,i,m in missing_entry])
    print(f"Bad standard_id values:               {len(bad_std)}")
    if bad_std: red += len(bad_std); _samples([f'{r}: {v}' for r,v in bad_std])
    print(f"Bad category values:                  {len(bad_cat)}")
    if bad_cat: red += len(bad_cat); _samples([f'{r}: {v}' for r,v in bad_cat])
    print(f"Bad curation_status values:           {len(bad_status)}")
    if bad_status: red += len(bad_status); _samples([f'{r}: {v}' for r,v in bad_status])
    print(f"Dangling prereq.ref (not in catalog): {len(dangling_refs)}"
          + ("  (Neo4j-lookup skipped)" if not valid_refs else ""))
    if dangling_refs: red += len(dangling_refs); _samples([f'{r}: {v}' for r,v in dangling_refs])
    print(f"LLM refusals in rationale/good_enough:{len(refusals)}")
    if refusals: red += len(refusals); _samples([f'{r}: {t!r}' for r,t in refusals])

    print()
    print("── YELLOW (curator flags) ──────────────────────────────────────")
    yellow = 0
    zeros = sum(1 for n in prereq_counts if n == 0)
    lows  = sum(1 for n in prereq_counts if 0 < n < 3)
    highs = sum(1 for n in prereq_counts if n > 6)
    print(f"Files with 0 prereqs (may be legit):  {zeros}")
    print(f"Files with 1-2 prereqs (thin):        {lows}")
    if lows: yellow += lows
    print(f"Files with >6 prereqs (verbose):      {highs}")
    if highs: yellow += highs
    print(f"Duplicate (ref,std) entries:          {len(dup_entries)}")
    if dup_entries: yellow += len(dup_entries); _samples([f'{r}: {v}' for r,v in dup_entries])
    print(f"Empty rationale fields:               {len(empty_rationale)}")
    if empty_rationale: yellow += len(empty_rationale); _samples(empty_rationale)
    print(f"Empty good_enough fields:             {len(empty_good_enough)}")
    if empty_good_enough: yellow += len(empty_good_enough); _samples(empty_good_enough)
    print(f"Filler-phrase hits:                   {len(filler_hits)}")
    if filler_hits: yellow += len(filler_hits); _samples([f'{r} [{p}]: {m!r}' for r,p,m in filler_hits])

    print()
    print("── GREEN (informational) ───────────────────────────────────────")
    print(f"Prereqs per file:      {_stats(prereq_counts)}")
    print(f"Rationale words:       {_stats(rationale_lens)}")
    print(f"Good-enough words:     {_stats(good_enough_lens)}")
    print(f"Target std distribution:")
    for s, c in by_std.most_common():
        print(f"  {s or '(missing)':<20} {c}  ({_pct(c)})")
    print(f"Category distribution:")
    for c, n in by_cat.most_common():
        print(f"  {c or '(missing)':<20} {n}")
    print(f"Curation status distribution:")
    for s, c in status_counts.most_common():
        print(f"  {s or '(missing)':<20} {c}  ({_pct(c)})")

    print()
    print("=" * 70)
    verdict = "MVP READY" if red == 0 else "BLOCKERS PRESENT"
    print(f"VERDICT: {verdict}   (red={red}, yellow={yellow})")
    print("=" * 70)


if __name__ == "__main__":
    main()
