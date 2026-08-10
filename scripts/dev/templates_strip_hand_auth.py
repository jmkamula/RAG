"""
Strip hand-authored content from Prerequisites + Cross-references sections.

The generated content (Ship 57' prereqs + Ship 1.7 xfw bridges) now
covers what these sections need to say, so the curator-authored
checklists/bullets that lived above the markers are redundant. This
script removes everything between the section heading and its marker,
leaving the marker in place.

Idempotent — templates without hand-auth content are unchanged.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/templates_strip_hand_auth.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent / "db" / "templates"

# (heading, marker) pairs — content between heading-line-end and marker
# gets replaced with a single blank line.
_SECTIONS = [
    ("## Prerequisites",   "<<PREREQUISITES>>"),
    ("## Cross-references", "<<CROSS_REFERENCES>>"),
]


def _strip_between(text: str, heading: str, marker: str) -> tuple[str, int]:
    """Return (new_text, chars_stripped). No-op if heading or marker not
    found, or if the space between is already empty."""
    heading_idx = text.find(heading)
    if heading_idx < 0:
        return text, 0
    heading_line_end = text.find("\n", heading_idx)
    if heading_line_end < 0:
        return text, 0
    # Search for marker after heading only
    marker_idx = text.find(marker, heading_line_end)
    if marker_idx < 0:
        return text, 0
    # Ensure marker sits within this section (before next H2)
    next_h2 = re.search(r"^##\s+", text[heading_line_end + 1:], re.MULTILINE)
    if next_h2 and heading_line_end + 1 + next_h2.start() < marker_idx:
        return text, 0

    between = text[heading_line_end + 1:marker_idx]
    if not between.strip():
        return text, 0  # already stripped

    new_text = text[:heading_line_end + 1] + "\n" + text[marker_idx:]
    return new_text, len(between)


def process(path: Path, dry_run: bool) -> dict[str, int]:
    text = path.read_text()
    stripped: dict[str, int] = {}
    for heading, marker in _SECTIONS:
        new_text, n = _strip_between(text, heading, marker)
        if n:
            stripped[heading] = n
            text = new_text
    if stripped and not dry_run:
        path.write_text(text)
    return stripped


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--preview", metavar="LEAF_ID",
                    help="Show before/after for one template (implies --dry-run)")
    args = ap.parse_args()

    if args.preview:
        slug = args.preview.replace(":", "__").replace(".", "_")
        p = ROOT / f"{slug}.md"
        if not p.exists():
            print(f"!! not found: {p}"); return
        before = p.read_text()
        # simulate
        after = before
        for heading, marker in _SECTIONS:
            after, _ = _strip_between(after, heading, marker)
        for heading, marker in _SECTIONS:
            print(f"=== {heading} ===")
            # Show BEFORE section
            i0 = before.find(heading); e0 = before.find("\n## ", i0 + 5)
            print("--- BEFORE ---")
            print(before[i0:e0 if e0 > 0 else i0 + 800][:800])
            i1 = after.find(heading); e1 = after.find("\n## ", i1 + 5)
            print("--- AFTER ---")
            print(after[i1:e1 if e1 > 0 else i1 + 400][:400])
            print()
        return

    files = sorted(ROOT.glob("req__*.md"))
    total_touched = 0
    per_heading: dict[str, int] = {}
    total_chars = 0
    samples: list[str] = []
    for f in files:
        stripped = process(f, args.dry_run)
        if stripped:
            total_touched += 1
            for h, n in stripped.items():
                per_heading[h] = per_heading.get(h, 0) + 1
                total_chars += n
            if len(samples) < 10:
                samples.append(f"  {f.name}: {list(stripped.keys())}")

    verb = "would strip" if args.dry_run else "stripped"
    print(f"Templates scanned:  {len(files)}")
    print(f"Templates touched:  {total_touched}")
    print(f"Total chars {verb}: {total_chars}")
    print(f"  by section:")
    for h, n in sorted(per_heading.items()):
        print(f"    {h}  {n} files")
    if samples:
        print("Samples:")
        for s in samples:
            print(s)


if __name__ == "__main__":
    main()
