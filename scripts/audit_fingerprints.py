"""
Ship 16'.a (2026-07-22) — audit the fingerprint catalog in
`db/must_fingerprints/` for over-broad token sets that cause
extractor over-attribution.

Root cause from Ship 11'.f: 4 specific bridge-fanout patterns
reappeared in the Ship 11'.e re-extract because their MUSTs
fire on very-loose token pairs (e.g. `[subprocessor, audit]`
matches any doc mentioning both words in any context). The
Ship 11'.b bridge gate + 11'.c/'.d filters catch downstream
noise but can't repair upstream over-firing.

This audit walks every `.yaml` catalog file and flags:

1. **Short token groups** — any `excerpt_keywords` entry with
   < 3 tokens (loose pairs). These are the primary suspects.

2. **Common-noise tokens** — token groups containing only
   generic words like `[review, date]`, `[program, evidence]`,
   `[coverage, check]`. These fire on almost any procedural doc.

3. **Token overlap with other leaves** — the same token set
   defined across multiple leaves means any matching doc gets
   over-attributed to N leaves.

4. **Duplicate MUST-id occurrences** across files — leaves
   that share MUST ids (should be rare).

Reports per-leaf + per-fingerprint counts. Writes results to
stdout by default; `--out` writes to a JSON report for
downstream tooling.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/audit_fingerprints.py [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml


_CATALOG_DIR = Path("/data/arioncomply/db/must_fingerprints")


# Generic "noise" tokens that appear across procedural documents
# — a fingerprint using ONLY these is almost certainly over-broad.
_NOISE_TOKENS = {
    "review", "record", "check", "program", "documented", "date",
    "coverage", "audit", "procedure", "process", "activity", "log",
    "register", "document", "documentation", "policy", "list",
    "sample", "sampled", "identity", "identifier", "row", "rows",
    "content", "reviewer", "flag", "table", "sheet", "annex",
    "section", "reference", "sweep", "planned", "interval",
    "meta", "meta_review", "annual", "quarterly", "monthly",
}


def _load_all_fingerprints() -> list[dict]:
    """Load every YAML in the catalog dir. Returns a list of
    {file, leaf_id, control, standard, must_id, tokens_groups}
    entries — one per MUST-fingerprint pair."""
    out: list[dict] = []
    for path in sorted(_CATALOG_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
        except Exception as e:
            print(f"WARN: failed to load {path.name}: {e}", file=sys.stderr)
            continue
        leaf_id  = data.get("target_evidence_requirement", "")
        control  = data.get("target_control", "")
        standard = data.get("target_standard", "")
        for fp in data.get("must_fingerprints", []):
            must_id = fp.get("must_id", "")
            token_groups = fp.get("excerpt_keywords", []) or []
            out.append({
                "file":         path.name,
                "leaf_id":      leaf_id,
                "control":      control,
                "standard":     standard,
                "must_id":      must_id,
                "token_groups": token_groups,
                "description":  fp.get("description", ""),
            })
    return out


def _classify_group(tokens: list) -> str:
    """Return a classification tag for the token group.

    Defensive str-coercion: YAML auto-parses `yes`/`no`/`true`/
    `false`/numbers into non-str types; treat those as edge-case
    tokens with lower-cased string values.
    """
    if not tokens:
        return "empty"
    n = len(tokens)
    tokens_str = [str(t).lower() for t in tokens]
    non_noise = [t for t in tokens_str if t not in _NOISE_TOKENS]
    if n < 2:
        return "single_token"
    if n == 2 and not non_noise:
        return "loose_pair_noise_only"
    if n == 2 and len(non_noise) == 1:
        return "loose_pair_one_signal"
    if n == 2:
        return "loose_pair_ok"
    if not non_noise:
        return "multi_noise_only"
    if len(non_noise) == 1:
        return "one_signal_padded"
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None,
                    help="Write JSON report to this path.")
    ap.add_argument("--limit-per-class", type=int, default=15,
                    help="Print at most this many examples per class.")
    args = ap.parse_args()

    entries = _load_all_fingerprints()
    n_files = len({e["file"] for e in entries})
    n_musts = len(entries)
    print(f"Loaded {n_musts} MUST-fingerprints across {n_files} leaves\n")

    # Classify every token group per MUST.
    problematic: dict[str, list[dict]] = defaultdict(list)
    token_group_leaves: dict[tuple, set[str]] = defaultdict(set)

    for e in entries:
        worst_class = "ok"
        for group in e["token_groups"]:
            klass = _classify_group(group)
            # Str-coerce for sorting + collision-key hygiene (YAML
            # auto-parses `yes`/`no`/`true`/numbers into non-strs).
            group_key = tuple(sorted(str(t).lower() for t in group))
            token_group_leaves[group_key].add(e["leaf_id"])
            # Rank worst → best for the entry summary.
            rank = {"empty": 0, "single_token": 1, "multi_noise_only": 2,
                    "loose_pair_noise_only": 3, "loose_pair_one_signal": 4,
                    "one_signal_padded": 5, "loose_pair_ok": 6, "ok": 7}
            if rank.get(klass, 9) < rank.get(worst_class, 9):
                worst_class = klass
        if worst_class != "ok":
            problematic[worst_class].append(e)

    # Report per-class counts.
    print("=" * 62)
    print("Per-class MUST-fingerprint counts (worst-group classification)")
    print("=" * 62)
    class_totals = {c: len(problematic[c]) for c in problematic}
    for c in ("empty", "single_token", "multi_noise_only",
              "loose_pair_noise_only", "loose_pair_one_signal",
              "one_signal_padded", "loose_pair_ok"):
        if c not in class_totals:
            continue
        print(f"  {c:28} {class_totals[c]:5d}")

    # Cross-leaf token-set collisions.
    collisions = {
        tokens: leaves for tokens, leaves in token_group_leaves.items()
        if len(leaves) > 1 and len(tokens) >= 2
    }
    print()
    print(f"Cross-leaf token-set collisions: {len(collisions)} "
          f"(same tokens matching multiple leaves)")

    # Show top-N collisions by leaf count.
    if collisions:
        top = sorted(collisions.items(), key=lambda kv: -len(kv[1]))[:12]
        print("  Worst offenders:")
        for tokens, leaves in top:
            print(f"    tokens={list(tokens)} → {len(leaves)} leaves")
            for l in sorted(leaves)[:5]:
                print(f"      • {l}")
            if len(leaves) > 5:
                print(f"      • … +{len(leaves) - 5} more")

    # Show examples per problematic class.
    print()
    print("=" * 62)
    print("Sample entries per class (Ship 11'.f targets flagged)")
    print("=" * 62)
    target_musts = {
        "item:A.7.2.6:rev_subprocessor_audit",
        "item:A.7.4.7:rev_expiry_sweep",
        "item:A.7.2.8:ropa_activity_id",
        "item:A.7.4.8:proc_disposal",
    }
    for klass, items in problematic.items():
        if klass in ("ok", "loose_pair_ok"):
            continue
        # Sort: known targets first, then by control ref
        items_sorted = sorted(
            items,
            key=lambda e: (
                0 if e["must_id"] in target_musts else 1,
                e["control"], e["must_id"],
            ),
        )
        print(f"\n[{klass}]  showing up to {args.limit_per_class}:")
        for e in items_sorted[:args.limit_per_class]:
            marker = " ← Ship 11'.f target" if e["must_id"] in target_musts else ""
            print(f"  {e['must_id']}{marker}")
            for g in e["token_groups"]:
                if _classify_group(g) == klass:
                    print(f"    tokens={g}")

    # JSON report
    if args.out:
        report = {
            "n_files":              n_files,
            "n_musts":              n_musts,
            "class_totals":         class_totals,
            "top_collisions": [
                {"tokens": list(tokens), "leaves": sorted(leaves)}
                for tokens, leaves in sorted(
                    collisions.items(), key=lambda kv: -len(kv[1]),
                )[:50]
            ],
            "problematic": {
                k: [
                    {"must_id": e["must_id"], "leaf_id": e["leaf_id"],
                     "control": e["control"],
                     "problem_groups": [
                         g for g in e["token_groups"]
                         if _classify_group(g) == k
                     ]}
                    for e in problematic[k]
                ]
                for k in problematic
            },
        }
        args.out.write_text(json.dumps(report, indent=2))
        print(f"\nWrote report → {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
