"""
ArionComply — Extract cross-framework edges from source JSONs (S4)

One-shot script that re-emits the XFW_EDGES Python block from
iso_nodes_phase1.json + gdpr_nodes_phase2.json's cross_framework_
summary fields. Output is the literal code block that goes into
enrichment/relationships/relationship_catalog.py.

Usage:
  python3 scripts/extract_xfw_to_catalog.py > /tmp/xfw_block.py

The script is idempotent — re-run when the source JSONs change to
get a fresh edge block. Manual edits to relationship_catalog.py
will be lost on re-extract; prefer editing the source JSON for
durable changes.
"""
from __future__ import annotations
import json
import sys
from collections import Counter

ISO_PATH  = "/data/arioncomply/iso_nodes_phase1.json"
GDPR_PATH = "/data/arioncomply/gdpr_nodes_phase2.json"

# Same canonicalisation as load_graph_relationships.py
REL_MAP = {
    "IMPLEMENTS_GDPR": "IMPLEMENTS",
    "SUPPORTS_GDPR":   "SUPPORTS",
    "MAPS_TO":         "RELATED_TO",
    "REFERENCES":      "RELATED_TO",
}
KEEP_TYPES = ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE")


def _esc(s: str) -> str:
    """Escape for a Python single-quoted string literal."""
    return (s or "").replace("\\", "\\\\").replace("'", "\\'")


def _split(nid: str) -> tuple[str, str]:
    """'STANDARD:WITH:COLONS:ref' -> ('STANDARD:WITH:COLONS', 'ref')."""
    if ":" not in nid:
        return ("", nid)
    idx = nid.rfind(":")
    return (nid[:idx], nid[idx + 1:])


def main():
    edges = []
    seen: set[tuple[str, str, str]] = set()
    for path in (ISO_PATH, GDPR_PATH):
        with open(path) as f:
            nodes = json.load(f)
        for n in nodes:
            src_id = n.get("id", "")
            if not src_id:
                continue
            cfw = n.get("cross_framework_summary", {}) or {}
            for k, mapping in cfw.items():
                tgt_id = mapping.get("related_req_id", k)
                if not tgt_id:
                    continue
                rel = mapping.get("relationship_type", "RELATED_TO")
                rel = REL_MAP.get(rel.upper().strip(), rel.upper().strip())
                if rel not in KEEP_TYPES:
                    continue
                key = (src_id, tgt_id, rel)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({
                    "src": src_id, "tgt": tgt_id, "rel": rel,
                    "rationale": (mapping.get("rationale") or
                                  mapping.get("relationship_description") or "").strip(),
                    "confidence": (mapping.get("confidence") or "").strip(),
                })

    # Stable order: type then src then tgt
    rel_order = {t: i for i, t in enumerate(KEEP_TYPES)}
    edges.sort(key=lambda e: (rel_order[e["rel"]], e["src"], e["tgt"]))

    out = sys.stdout
    out.write("# S4: cross-framework edges migrated from "
              "iso_nodes_phase1.json + gdpr_nodes_phase2.json\n"
              "# (cross_framework_summary fields).\n"
              "# Edge types: IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE.\n"
              "# Re-generate via scripts/extract_xfw_to_catalog.py — do not\n"
              "# edit by hand; the next regeneration overwrites local edits.\n\n")
    out.write("XFW_EDGES: list[RelationshipEdge] = [\n")
    for e in edges:
        src_std, src_ref = _split(e["src"])
        tgt_std, tgt_ref = _split(e["tgt"])
        rationale = _esc(e["rationale"])[:300]
        citation  = "iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)"
        role      = e["confidence"].lower() if e["confidence"] else None
        rationale_arg = f"\n        rationale='{rationale}',"  if rationale else ""
        role_arg      = f"\n        role='{_esc(role)}',"      if role      else ""
        out.write(
            "    RelationshipEdge(\n"
            f"        source_ref='{src_ref}', source_standard_id='{src_std}',\n"
            f"        target_ref='{tgt_ref}', target_standard_id='{tgt_std}',\n"
            f"        edge_type='{e['rel']}',"
            f"{rationale_arg}\n"
            f"        citation='{citation}',"
            f"{role_arg}\n"
            "    ),\n"
        )
    out.write("]\n")

    # Stats to stderr
    print(f"# Total edges: {len(edges)}", file=sys.stderr)
    for k, v in Counter(e["rel"] for e in edges).most_common():
        print(f"#   {k:12s} {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
