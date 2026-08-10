"""
Templates Pass 1b — reposition <<DOC_CONTROL>> marker to top-inline.

Pass 1 defaulted to "## Doc control" footer-with-heading. Convention
change (2026-08-08): place <<DOC_CONTROL>> as a bare marker right
after the H1 title (no heading), matching how compliance documents
typically show version metadata at the top.

Idempotent — templates already in top-inline shape are left alone.
Additive-safe — never touches other markers or existing content.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/dev/templates_pass1b_doc_control_reposition.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent / "db" / "templates"

# Matches "## Doc control" heading + optional blank + <<DOC_CONTROL>> marker
# + optional blank line, anywhere in the file.
_FOOTER_BLOCK = re.compile(
    r"\n##\s+Doc control\s*\n\s*<<DOC_CONTROL>>\s*\n\s*\n?",
    re.IGNORECASE,
)

# Match H1 line (only one per template).
_H1_LINE = re.compile(r"(^#\s+[^\n]+\n)", re.MULTILINE)

# Match a bare <<DOC_CONTROL>> already sitting right after H1 (top-inline).
_ALREADY_TOP_INLINE = re.compile(
    r"^#\s+[^\n]+\n\s*\n\s*<<DOC_CONTROL>>\s*\n",
    re.MULTILINE,
)


def process(path: Path, dry_run: bool) -> str:
    text = path.read_text()

    if _ALREADY_TOP_INLINE.search(text):
        # Already in target shape; only bail if no footer copy also exists
        # (edge case: some template might legitimately have both — remove
        # the footer copy but leave the top one).
        footer_hit = _FOOTER_BLOCK.search(text)
        if not footer_hit:
            return "skip"
        new_text = _FOOTER_BLOCK.sub("\n", text, count=1)
        if not dry_run:
            path.write_text(new_text)
        return "footer_dup_removed"

    footer_hit = _FOOTER_BLOCK.search(text)
    if not footer_hit:
        # No footer block found — nothing to move.
        return "no_marker"

    new_text = _FOOTER_BLOCK.sub("\n", text, count=1)

    h1 = _H1_LINE.search(new_text)
    if not h1:
        return "no_h1"

    insert_pos = h1.end()
    # Preserve one blank line already following H1, add marker + blank.
    # Detect if next chars are already \n or content.
    after_h1 = new_text[insert_pos:]
    if after_h1.startswith("\n"):
        # e.g. "# Title\n\n>Purpose\n..."
        insertion = "\n<<DOC_CONTROL>>\n"
    else:
        insertion = "\n<<DOC_CONTROL>>\n\n"
    new_text = new_text[:insert_pos] + insertion + new_text[insert_pos:]

    if not dry_run:
        path.write_text(new_text)
    return "moved"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(ROOT.glob("req__*.md"))
    from collections import Counter
    counts: Counter = Counter()
    samples: dict[str, list[str]] = {}
    for f in files:
        outcome = process(f, args.dry_run)
        counts[outcome] += 1
        if len(samples.get(outcome, [])) < 3:
            samples.setdefault(outcome, []).append(f.name)

    verb = "would" if args.dry_run else "did"
    print(f"Templates scanned: {len(files)}")
    for outcome, n in counts.most_common():
        print(f"  {outcome:22s} {n}  ({verb} { {'skip':'nothing', 'moved':'move', 'footer_dup_removed':'remove dup footer', 'no_marker':'nothing (no marker)', 'no_h1':'nothing (no H1)' }.get(outcome, '?')})")
    print()
    print("Samples:")
    for outcome, names in samples.items():
        print(f"  {outcome}:")
        for n in names:
            print(f"    {n}")


if __name__ == "__main__":
    main()
