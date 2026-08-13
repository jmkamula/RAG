#!/usr/bin/env python3
"""Ship 68'.a — scope_items curator tool.

Interactive CLI for authoring per-MUST-pair scope on bridge edges
(IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE). Each pair says
"source's MUST X specifically implements target's MUST Y" — the
per-pair semantics that Ships 60–62 assumed but which the graph
didn't originally carry.

Usage:
    python3 scripts/curation/scope_items_editor.py list
        Show every bridge edge with its edge type, rationale, and
        current scope_items count.

    python3 scripts/curation/scope_items_editor.py list --unscoped
        Only edges without scope_items (curator work queue).

    python3 scripts/curation/scope_items_editor.py edit <src_id> <edge> <dst_id>
        Interactive session:
          - shows source's MUST list (numbered)
          - shows target's MUST list (numbered)
          - shows current scope_items
          - accepts pair adds ("3 → 7"), removes ("del 3 → 7"), or
            done ("save" / "quit").
        Example:
          python3 scripts/curation/scope_items_editor.py edit \
              ISO27001:2022:A.5.18 IMPLEMENTS GDPR:2016/679:Art.32

    python3 scripts/curation/scope_items_editor.py show <src_id> <edge> <dst_id>
        Read-only inspection of one edge.

    python3 scripts/curation/scope_items_editor.py validate
        Assert every scope_items entry references a real MUST id on
        the source + target sides. Exits non-zero on any invalid ref.

Storage
-------
Neo4j property arrays are homogeneously typed. To store list-of-dicts,
each scope_items entry is JSON-encoded as a string:
    {"sr": "item:A.5.18:authorization", "tg": "item:Art.32:reg_owner"}
The reader (rag/posture_loader._parse_scope_items) handles both list-of-
string and (defensively) list-of-dict shapes.

Curator workflow
----------------
1. Read the edge's rationale to understand the mapping intent.
2. Skim source + target MUST lists.
3. For each source MUST that specifically evidences a target MUST,
   author a pair.
4. Save. The next `load_posture` sweep rebuilds bridge_coverage using
   the authored pairs (falls back to cross-product on unauthored edges).

Ship 68'.a Phase 0: schema + tooling. No edges are authored yet —
existing edges continue with cross-product until curator ships pairs.
Ship 68'.b will pilot Art.32's edges. Ship 68'.d bulk-authors the
remaining 450.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass


EDGE_TYPES = ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE")


def _driver():
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pw   = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and pw):
        print("error: NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD not set")
        sys.exit(1)
    return GraphDatabase.driver(uri, auth=(user, pw))


def _fetch_must_ids(session, node_id: str) -> list[tuple[str, str]]:
    """Return [(must_id, text)] for a control node in author order."""
    r = session.run("""
        MATCH (rn:RequirementNode {id: $nid})-[:SATISFIED_BY]->(:FulfilmentSpec)
              -[:REQUIRES_EVIDENCE]->(er:EvidenceRequirement)
              -[:MUST_CONTAIN]->(ci:ChecklistItem)
        RETURN ci.id AS id, ci.text AS text
        ORDER BY id
    """, nid=node_id)
    return [(row["id"], row["text"] or "") for row in r]


def _fetch_scope_items(session, src_id: str, edge: str, dst_id: str) -> list[dict]:
    r = session.run(f"""
        MATCH (s:RequirementNode {{id: $src}})-[e:{edge}]->(t:RequirementNode {{id: $dst}})
        RETURN e.scope_items AS scope_items, e.rationale AS rationale
    """, src=src_id, dst=dst_id).single()
    if not r:
        return []
    raw = r["scope_items"] or []
    out: list[dict] = []
    if isinstance(raw, list):
        for x in raw:
            if isinstance(x, str):
                try:
                    obj = json.loads(x)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    out.append(obj)
            elif isinstance(x, dict):
                out.append(x)
    return out


def _write_scope_items(session, src_id: str, edge: str, dst_id: str,
                       pairs: list[dict]) -> None:
    """Persist scope_items as list of JSON strings (Neo4j homogeneous
    array constraint)."""
    encoded = [json.dumps(p, separators=(",", ":")) for p in pairs]
    session.run(f"""
        MATCH (s:RequirementNode {{id: $src}})-[e:{edge}]->(t:RequirementNode {{id: $dst}})
        SET e.scope_items = $items,
            e.scope_items_updated_at = datetime()
    """, src=src_id, dst=dst_id, items=encoded)


# ── Commands ────────────────────────────────────────────────────────

def cmd_list(args) -> int:
    drv = _driver()
    with drv.session() as s:
        types = " | ".join(f":{e}" for e in EDGE_TYPES)
        q = f"""
            MATCH (src)-[e{'|'.join(':' + e for e in EDGE_TYPES).replace(':', ':', 1)}]->(dst)
            RETURN src.id AS src, dst.id AS dst, type(e) AS et,
                   e.rationale AS rationale, e.scope_items AS si
            ORDER BY et, src, dst
        """
        # Simpler shape — one MATCH per edge type + UNION.
        parts = []
        for et in EDGE_TYPES:
            parts.append(f"""
                MATCH (src:RequirementNode)-[e:{et}]->(dst:RequirementNode)
                RETURN src.id AS src, dst.id AS dst, '{et}' AS et,
                       e.rationale AS rationale, e.scope_items AS si
            """)
        q = " UNION ALL ".join(parts) + " ORDER BY et, src, dst"
        n_total = 0
        n_scoped = 0
        for r in s.run(q):
            n_total += 1
            n_pairs = len(r["si"] or [])
            if n_pairs > 0:
                n_scoped += 1
            if args.unscoped and n_pairs > 0:
                continue
            marker = f"({n_pairs} pairs)" if n_pairs else "(unscoped)"
            print(f"  {r['et']:11s}  {r['src']} → {r['dst']}  {marker}")
            if not args.short and r["rationale"]:
                print(f"      ↳ {r['rationale'][:120]}")
        print()
        print(f"total edges: {n_total}   scoped: {n_scoped}   "
              f"unscoped: {n_total - n_scoped}   "
              f"({100*n_scoped/max(1,n_total):.0f}% scoped)")
    drv.close()
    return 0


def cmd_show(args) -> int:
    drv = _driver()
    with drv.session() as s:
        r = s.run(f"""
            MATCH (src:RequirementNode {{id: $src}})-[e:{args.edge}]->(dst:RequirementNode {{id: $dst}})
            RETURN src.ref AS src_ref, dst.ref AS dst_ref,
                   e.rationale AS rationale, e.scope_items AS si
        """, src=args.src_id, dst=args.dst_id).single()
        if not r:
            print(f"error: no {args.edge} edge {args.src_id} → {args.dst_id}")
            return 1
        print(f"{r['src_ref']} → {r['dst_ref']}   [{args.edge}]")
        print(f"rationale: {r['rationale'] or '(none)'}")
        pairs = _fetch_scope_items(s, args.src_id, args.edge, args.dst_id)
        print(f"scope_items: {len(pairs)} pairs")
        for p in pairs:
            print(f"  - {p.get('sr')} → {p.get('tg')}")
    drv.close()
    return 0


def cmd_edit(args) -> int:
    drv = _driver()
    with drv.session() as s:
        r = s.run(f"""
            MATCH (src:RequirementNode {{id: $src}})-[e:{args.edge}]->(dst:RequirementNode {{id: $dst}})
            RETURN src.ref AS src_ref, dst.ref AS dst_ref, e.rationale AS rationale
        """, src=args.src_id, dst=args.dst_id).single()
        if not r:
            print(f"error: no {args.edge} edge {args.src_id} → {args.dst_id}")
            return 1
        src_musts = _fetch_must_ids(s, args.src_id)
        dst_musts = _fetch_must_ids(s, args.dst_id)
        pairs = _fetch_scope_items(s, args.src_id, args.edge, args.dst_id)

        print(f"\n=== {r['src_ref']} → {r['dst_ref']}   [{args.edge}] ===")
        print(f"rationale: {r['rationale'] or '(none)'}\n")

        print("source MUSTs:")
        for i, (mid, text) in enumerate(src_musts, 1):
            print(f"  s{i:2d}  {mid}")
            print(f"        → {text[:100]}")
        print("\ntarget MUSTs:")
        for i, (mid, text) in enumerate(dst_musts, 1):
            print(f"  t{i:2d}  {mid}")
            print(f"        → {text[:100]}")

        print(f"\ncurrent pairs ({len(pairs)}):")
        for p in pairs:
            print(f"  - {p.get('sr')} → {p.get('tg')}")

        print("\ncommands:  s<N> t<M>   add pair"
              "\n           del s<N> t<M>   remove pair"
              "\n           save            persist to Neo4j"
              "\n           quit            discard changes\n")

        while True:
            try:
                line = input("scope> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nquit")
                return 0
            if not line:
                continue
            if line == "save":
                _write_scope_items(s, args.src_id, args.edge, args.dst_id, pairs)
                print(f"saved {len(pairs)} pairs")
                return 0
            if line == "quit":
                print("discarded")
                return 0
            if line == "list":
                for p in pairs:
                    print(f"  - {p.get('sr')} → {p.get('tg')}")
                continue

            del_mode = False
            if line.startswith("del "):
                del_mode = True
                line = line[4:].strip()
            # Parse "s3 t7" or "s3 → t7" or "s3, t7"
            tokens = [t.strip("→,").strip() for t in line.split() if t.strip("→,").strip()]
            if len(tokens) != 2 or not (tokens[0].startswith("s") and tokens[1].startswith("t")):
                print("  usage: s<N> t<M> (or 'del s<N> t<M>')")
                continue
            try:
                s_idx = int(tokens[0][1:])
                t_idx = int(tokens[1][1:])
            except ValueError:
                print("  usage: s<N> t<M>")
                continue
            if not (1 <= s_idx <= len(src_musts)) or not (1 <= t_idx <= len(dst_musts)):
                print(f"  out of range (source: 1-{len(src_musts)}, target: 1-{len(dst_musts)})")
                continue
            sr = src_musts[s_idx - 1][0]
            tg = dst_musts[t_idx - 1][0]
            if del_mode:
                before = len(pairs)
                pairs = [p for p in pairs if not (p.get("sr") == sr and p.get("tg") == tg)]
                print(f"  removed {before - len(pairs)} pair")
            else:
                if any(p.get("sr") == sr and p.get("tg") == tg for p in pairs):
                    print("  already present")
                    continue
                pairs.append({"sr": sr, "tg": tg})
                print(f"  added: {sr} → {tg}   ({len(pairs)} pairs total)")


def cmd_validate(args) -> int:
    """Assert every scope_items reference is a real MUST id on the
    source + target sides. Exits non-zero on any invalid ref."""
    drv = _driver()
    bad_pairs = 0
    with drv.session() as s:
        for et in EDGE_TYPES:
            for row in s.run(f"""
                MATCH (src:RequirementNode)-[e:{et}]->(dst:RequirementNode)
                WHERE e.scope_items IS NOT NULL AND size(e.scope_items) > 0
                RETURN src.id AS src, dst.id AS dst, e.scope_items AS si
            """):
                pairs = []
                for x in (row["si"] or []):
                    if isinstance(x, str):
                        try:
                            obj = json.loads(x)
                        except Exception:
                            print(f"  malformed JSON on {row['src']} -{et}-> {row['dst']}")
                            bad_pairs += 1
                            continue
                        pairs.append(obj)
                src_musts = {mid for mid, _ in _fetch_must_ids(s, row["src"])}
                dst_musts = {mid for mid, _ in _fetch_must_ids(s, row["dst"])}
                for p in pairs:
                    sr = p.get("sr"); tg = p.get("tg")
                    if sr not in src_musts:
                        print(f"  bad source ref on {row['src']} -{et}-> {row['dst']}: {sr}")
                        bad_pairs += 1
                    if tg not in dst_musts:
                        print(f"  bad target ref on {row['src']} -{et}-> {row['dst']}: {tg}")
                        bad_pairs += 1
    drv.close()
    if bad_pairs:
        print(f"\nFAIL — {bad_pairs} invalid MUST references found")
        return 1
    print("OK — all authored scope_items reference real MUST ids")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list all bridge edges + scope status")
    p_list.add_argument("--unscoped", action="store_true",
                        help="only show edges without scope_items")
    p_list.add_argument("--short", action="store_true",
                        help="omit rationale lines")
    p_list.set_defaults(fn=cmd_list)

    p_show = sub.add_parser("show", help="show one edge's scope_items")
    p_show.add_argument("src_id")
    p_show.add_argument("edge", choices=EDGE_TYPES)
    p_show.add_argument("dst_id")
    p_show.set_defaults(fn=cmd_show)

    p_edit = sub.add_parser("edit", help="interactively author scope_items")
    p_edit.add_argument("src_id")
    p_edit.add_argument("edge", choices=EDGE_TYPES)
    p_edit.add_argument("dst_id")
    p_edit.set_defaults(fn=cmd_edit)

    p_val = sub.add_parser("validate",
                           help="assert scope_items reference real MUSTs")
    p_val.set_defaults(fn=cmd_validate)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
