"""
Templates Pass 3 — close the section-vs-marker gap.

Pass 1's additive rule preserved existing "## Before you start" and
"## Cross-references" sections (from hand-authored tier-A anchors)
without injecting the corresponding markers. This pass fixes that:

  - "## Before you start" without <<PREREQUISITES>> → append marker
  - "## Cross-references" without <<CROSS_REFERENCES>> → append marker

Marker placement: at the END of the existing section (after any
hand-authored content), before the next H2 heading. Preserves the
curator's checklist/bullet content unchanged.

Idempotent — templates where both markers are already present are
skipped.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/templates_pass3_marker_gap_fix.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent / "db" / "templates"

# Sections and their markers. Each entry: (heading_text, marker_string).
_SECTIONS = [
    ("## Prerequisites",   "<<PREREQUISITES>>"),
    ("## Cross-references", "<<CROSS_REFERENCES>>"),
]

_NEXT_H2_RE = re.compile(r"^##\s+", re.MULTILINE)


def _section_range(text: str, heading: str) -> tuple[int, int] | None:
    """Return (start_of_content, end_of_section) for the given H2 heading.
    Start = char index right after the heading + newline.
    End = index of the next H2, or len(text)."""
    i = text.find(heading)
    if i < 0:
        return None
    # advance past heading line (include newline)
    line_end = text.find("\n", i)
    if line_end < 0:
        return None
    content_start = line_end + 1
    m = _NEXT_H2_RE.search(text, pos=content_start)
    content_end = m.start() if m else len(text)
    return content_start, content_end


def process(path: Path, dry_run: bool) -> list[str]:
    """Return list of markers inserted (empty = no change)."""
    text = path.read_text()
    inserted: list[str] = []
    new_text = text

    # Apply from bottom to top to keep indices valid on multi-marker fixes.
    ranges: list[tuple[int, int, str, str]] = []
    for heading, marker in _SECTIONS:
        rng = _section_range(new_text, heading)
        if not rng:
            continue
        cs, ce = rng
        section_body = new_text[cs:ce]
        if marker in section_body:
            continue
        ranges.append((cs, ce, heading, marker))

    for cs, ce, heading, marker in reversed(ranges):
        # Insert marker right before ce, on its own line, with a blank line
        # separator from any existing content above.
        section_body = new_text[cs:ce]
        # Trim trailing blank lines from body for clean append.
        trimmed = section_body.rstrip("\n") + "\n"
        appended = trimmed + "\n" + marker + "\n\n"
        new_text = new_text[:cs] + appended + new_text[ce:]
        inserted.append(marker)

    if inserted and not dry_run:
        path.write_text(new_text)
    return list(reversed(inserted))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(ROOT.glob("req__*.md"))
    touched = 0
    total_inserts = 0
    per_marker: dict[str, int] = {}
    samples: list[str] = []
    for f in files:
        inserted = process(f, args.dry_run)
        if inserted:
            touched += 1
            total_inserts += len(inserted)
            for m in inserted:
                per_marker[m] = per_marker.get(m, 0) + 1
            if len(samples) < 8:
                samples.append(f"  {f.name}  ← inserted: {', '.join(inserted)}")

    verb = "would insert" if args.dry_run else "inserted"
    print(f"Templates scanned:   {len(files)}")
    print(f"Templates touched:   {touched}")
    print(f"Total markers {verb}: {total_inserts}")
    print(f"  by marker:")
    for m, n in sorted(per_marker.items()):
        print(f"    {m}  {n}")
    if samples:
        print()
        print("Samples:")
        for s in samples:
            print(s)


if __name__ == "__main__":
    main()
