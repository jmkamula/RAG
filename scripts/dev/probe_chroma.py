"""
scripts/dev/probe_chroma.py — quick Chroma data-parity check.

Connects to the local Chroma HTTP service (default port 8000).
Lists all collections + doc counts so you can compare against a
known-good source.

Expected on a fresh install from the Ship 102' + 103' golden tar:
    arioncombly_all               1668
    edpb_guidelines               1190
    gdpr_2016_679                  303
    iso27001_2022                  126
    iso27003_2017                   25
    iso27004_2016                   23
    iso27005_2022                   42
    iso27701_2019                   49
    musts_arioncomply             5385
    --------------------------------
    total                         8811
    9 collections

Usage:
    python3 scripts/dev/probe_chroma.py
"""
from __future__ import annotations
import os
import sys

import chromadb


HOST = os.getenv("CHROMA_HOST", "127.0.0.1")
PORT = int(os.getenv("CHROMA_PORT", "8000"))

EXPECTED = {
    "arioncombly_all":    1668,
    "edpb_guidelines":    1190,
    "gdpr_2016_679":       303,
    "iso27001_2022":       126,
    "iso27003_2017":        25,
    "iso27004_2016":        23,
    "iso27005_2022":        42,
    "iso27701_2019":        49,
    "musts_arioncomply":  5385,
}


def main() -> None:
    try:
        c = chromadb.HttpClient(host=HOST, port=PORT)
        collections = c.list_collections()
    except Exception as e:
        sys.exit(f"failed to connect to Chroma at {HOST}:{PORT} — {e}")

    print(f"Chroma at {HOST}:{PORT}")
    print(f"{len(collections)} collections found:")
    print()

    total = 0
    mismatches = []
    seen = set()
    for coll_sum in sorted(collections, key=lambda x: x.name):
        coll = c.get_collection(coll_sum.name)
        cnt  = coll.count()
        exp  = EXPECTED.get(coll.name)
        marker = "  " if exp == cnt else "✗ "
        if exp is not None and exp != cnt:
            mismatches.append((coll.name, exp, cnt))
        print(f"  {marker}{coll.name:25s}  {cnt:>6}  (expected {exp if exp is not None else '?'})")
        total += cnt
        seen.add(coll.name)

    missing = set(EXPECTED.keys()) - seen
    if missing:
        print()
        print("--- missing collections ---")
        for m in sorted(missing):
            print(f"  ✗ {m:25s}  MISSING (expected {EXPECTED[m]})")

    print()
    print(f"total docs: {total}")

    if not mismatches and not missing and len(collections) == len(EXPECTED):
        print("PARITY — all 9 collections present with expected counts")
        sys.exit(0)
    else:
        print("MISMATCHES — see ✗ markers above")
        sys.exit(1)


if __name__ == "__main__":
    main()
