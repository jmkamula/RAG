"""
Templates Pass 2 — guidance marker activation.

For every <<MUST item:X>> / <<SHOULD item:X>> block in every template,
insert a <<GUIDANCE>> marker at the natural end of the block if not
already present. Idempotent — templates with guidance already in place
are left alone.

Block boundary = whichever of the following comes first after the
MUST/SHOULD marker:
  - <<TEXT>> or <<NAME>> placeholder     → insert right before it
  - Next H2/H3 heading                    → insert right before it
  - Next MUST/SHOULD marker               → insert right before it
  - EOF                                   → append at end

Insertion position keeps <<GUIDANCE>> at the end of each MUST section's
prose, right before the tenant-edit zone (matching the Ship 56'
convention shown on A.5.15).

Usage:
    # print diff for one template
    python3 -m scripts.dev.templates_pass2_guidance_markers --sample req:10.1:applicable_triggers_scope

    # bulk
    python3 -m scripts.dev.templates_pass2_guidance_markers --bulk [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent / "db" / "templates"

_MARKER_RE = re.compile(
    r"^<<(?:MUST|SHOULD)\s+item:[A-Za-z0-9.]+:[a-z0-9_]+>>\s*$",
    re.MULTILINE,
)

# What ends a MUST/SHOULD block — checked strictly after the marker line.
_BOUNDARY_RE = re.compile(
    r"^(?:"
    r"<<(?:TEXT|NAME)>>\s*"                                 # tenant edit-zone
    r"|<<(?:MUST|SHOULD)\s+item:[A-Za-z0-9.]+:[a-z0-9_]+>>\s*"   # next MUST/SHOULD
    r"|##\s+.+"                                              # next H2
    r"|###\s+.+"                                             # next H3
    r")$",
    re.MULTILINE,
)

_GUIDANCE_RE = re.compile(r"^<<GUIDANCE>>\s*$", re.MULTILINE)


def _insert_guidance(text: str) -> tuple[str, int]:
    """Return (new_text, num_insertions)."""
    markers = list(_MARKER_RE.finditer(text))
    if not markers:
        return text, 0

    insertions: list[tuple[int, str]] = []
    for m in markers:
        block_start = m.end()
        b_match = _BOUNDARY_RE.search(text, pos=block_start)
        block_end = b_match.start() if b_match else len(text)
        block = text[block_start:block_end]
        if _GUIDANCE_RE.search(block):
            continue  # already has guidance
        insertions.append((block_end, "<<GUIDANCE>>\n\n"))

    if not insertions:
        return text, 0

    # Apply from end to start so earlier positions stay valid.
    result = text
    for pos, ins in reversed(insertions):
        prefix = result[:pos]
        # If the prefix doesn't end with a blank line already, add one so
        # the marker sits on its own line separated by an empty line.
        trailing_nl = 0
        i = len(prefix) - 1
        while i >= 0 and prefix[i] == "\n":
            trailing_nl += 1
            i -= 1
        # Ensure exactly 2 trailing newlines before the marker (blank line +
        # marker's own line-start).
        if trailing_nl == 0:
            leading = "\n\n"
        elif trailing_nl == 1:
            leading = "\n"
        else:
            leading = ""
        result = prefix + leading + ins + result[pos:]
    return result, len(insertions)


def _process(path: Path, dry_run: bool) -> tuple[int, str]:
    text = path.read_text()
    new_text, n = _insert_guidance(text)
    if n and not dry_run:
        path.write_text(new_text)
    return n, new_text


def cmd_sample(leaf_id: str) -> None:
    slug = leaf_id.replace(":", "__").replace(".", "_")
    p = ROOT / f"{slug}.md"
    if not p.exists():
        print(f"!! not found: {p}", file=sys.stderr); return
    n, new_text = _process(p, dry_run=True)
    print(f"{p.name}: {n} guidance marker(s) would be inserted.")
    if n == 0:
        return
    # Show a couple of preview windows around each MUST/SHOULD marker
    markers = list(_MARKER_RE.finditer(new_text))
    for m in markers[:3]:
        start = max(0, m.start() - 60)
        end = min(len(new_text), m.end() + 300)
        print("─" * 60)
        print(new_text[start:end])


def cmd_bulk(dry_run: bool) -> None:
    files = sorted(ROOT.glob("req__*.md"))
    total_insertions = 0
    touched = 0
    zero = 0
    for i, p in enumerate(files, 1):
        n, _ = _process(p, dry_run)
        if n:
            touched += 1
            total_insertions += n
        else:
            zero += 1
    verb = "would insert" if dry_run else "inserted"
    print(f"Templates scanned:  {len(files)}")
    print(f"Templates touched:  {touched}")
    print(f"Templates untouched:{zero}")
    print(f"Total markers {verb}: {total_insertions}")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", metavar="LEAF_ID")
    g.add_argument("--bulk", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.sample:
        cmd_sample(args.sample)
    elif args.bulk:
        cmd_bulk(args.dry_run)


if __name__ == "__main__":
    main()
