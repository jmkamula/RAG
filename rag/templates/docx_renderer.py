"""
rag/templates/docx_renderer.py — render a narrative template as .docx.

For the 14 narrative v2 anchors (and any future narrative leaves),
Word is the native format: compliance officers edit prose, track
changes, leave comments. This module converts the rendered markdown
body into a python-docx Document with reasonable Word styling.

Phase A scope (download-only):
  - Convert common markdown idioms to Word-native paragraph styles
    (headings, blockquotes, bullets, bold/italic runs, code spans).
  - Preserve <<MUST item:X>> markers + EDIT-ZONE comments as visible
    plain text so the tenant sees the structural anchors and can
    edit between them. Phase B (round-trip) will move these to
    Word-native comments/bookmarks.
  - <<TEXT>> placeholders render as a styled "Click to enter text"
    cue so the editable region is visually obvious.

Not full markdown — focused on the 80% of constructs the v2 templates
actually use. Tables, footnotes, link references, etc. are
unhandled; narrative templates don't use them.
"""
from __future__ import annotations

import io
import re

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, Cm, RGBColor


# ── Constants ───────────────────────────────────────────────────────────────

MUST_MARKER_RE   = re.compile(r"<<(MUST|SHOULD)\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)>>")
EDIT_ZONE_START  = re.compile(r"<!--\s*EDIT-ZONE-START\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->")
EDIT_ZONE_END    = re.compile(r"<!--\s*EDIT-ZONE-END\s+(item:[A-Za-z0-9.]+:[a-z0-9_]+)\s*-->")
HTML_COMMENT_RE  = re.compile(r"^<!--.*?-->\s*$", re.DOTALL)
PROV_COMMENT_RE  = re.compile(r"^<!--.+?-->\n*", re.DOTALL)
INLINE_RUN_RE    = re.compile(
    r"(\*\*[^*\n]+\*\*"     # **bold**
    r"|__[^_\n]+__"          # __bold__
    r"|\*[^*\n]+\*"          # *italic*
    r"|_[^_\n]+_"            # _italic_
    r"|`[^`\n]+`"            # `code`
    r")"
)


# ── Inline run helpers ──────────────────────────────────────────────────────

def _add_runs_with_formatting(paragraph, text: str, base_color: RGBColor | None = None) -> None:
    """Split text on inline-markdown boundaries and add runs with bold /
    italic / monospace styling per fragment."""
    if not text:
        return
    parts = INLINE_RUN_RE.split(text)
    for part in parts:
        if not part:
            continue
        bold = italic = code = False
        content = part
        if (part.startswith("**") and part.endswith("**")) or \
           (part.startswith("__") and part.endswith("__")):
            bold = True
            content = part[2:-2]
        elif (part.startswith("*") and part.endswith("*") and len(part) > 2):
            italic = True
            content = part[1:-1]
        elif (part.startswith("_") and part.endswith("_") and len(part) > 2):
            italic = True
            content = part[1:-1]
        elif part.startswith("`") and part.endswith("`"):
            code = True
            content = part[1:-1]
        run = paragraph.add_run(content)
        run.bold   = bold
        run.italic = italic
        if code:
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        if base_color:
            run.font.color.rgb = base_color


def _add_paragraph(doc, text: str, style: str | None = None,
                   alignment=None, indent_cm: float | None = None,
                   color: RGBColor | None = None) -> None:
    """Add a styled paragraph; inline markdown handled."""
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    if alignment is not None:
        p.alignment = alignment
    if indent_cm is not None:
        p.paragraph_format.left_indent = Cm(indent_cm)
    _add_runs_with_formatting(p, text, base_color=color)


# ── Marker-aware line processing ────────────────────────────────────────────

def _humanize_item_slug(mid: str) -> str:
    """`item:4.3:boundaries` → 'boundaries'.

    Drops the internal `item:CTRL:` prefix so the tenant-visible marker
    reads as a natural label ('boundaries', 'exclusions', 'owner')
    rather than a debug-log tag. The full id remains encoded in the
    round-trip `<<MUST item:X>>` marker preserved in the source .md,
    just not visually loud in the rendered doc."""
    if not mid:
        return ""
    parts = mid.split(":")
    slug = parts[-1] if parts else mid
    return slug.replace("_", " ")


def _render_marker_line(doc, marker_match: re.Match) -> None:
    """Render a <<MUST item:X>> or <<SHOULD item:X>> marker as a small
    label paragraph — visible structural anchor."""
    kind, mid = marker_match.group(1), marker_match.group(2)
    kind_label = "Required element" if kind == "MUST" else "Recommended addition"
    slug = _humanize_item_slug(mid)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(f"◆ {kind_label} — {slug}")
    run.font.name  = "Calibri"
    run.font.size  = Pt(10)
    run.bold = True
    run.font.color.rgb = RGBColor(0x9C, 0x6F, 0x1B)


def _render_edit_zone_marker(doc, label: str, mid: str) -> None:
    """Render an EDIT-ZONE-START / EDIT-ZONE-END line as a subtle
    guidance cue. The internal `item:X:Y` id is dropped from the
    visible text — the surrounding structural markers keep round-trip
    binding when we ship Phase B upload extraction."""
    slug = _humanize_item_slug(mid)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    text = (f"▽ Enter your evidence for “{slug}” below ▽"
            if label == "EDIT START"
            else f"△ End of “{slug}” △")
    run = p.add_run(text)
    run.font.name  = "Calibri"
    run.font.size  = Pt(9)
    run.italic = True
    run.font.color.rgb = RGBColor(0xBA, 0xB8, 0xAB)


def _render_text_placeholder(doc) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run("[ Click to enter your evidence here ]")
    run.italic         = True
    run.font.size      = Pt(11)
    run.font.color.rgb = RGBColor(0x9C, 0x9A, 0x8E)


# ── Main converter ──────────────────────────────────────────────────────────

def render_template_docx(
    pg_conn,
    tenant_id: str,
    leaf_id:   str,
    template_body: str,
) -> bytes:
    """Convert the rendered markdown body to a .docx workbook.

    Walks line-by-line, maps markdown idioms to Word styles, and
    preserves structural markers as visible cues. Returns bytes
    suitable for HTTP response.
    """
    doc = Document()

    # Set base style — Word's default Calibri 11pt is fine; tighten margins
    # slightly so compliance officers don't waste a page on whitespace.
    sec = doc.sections[0]
    sec.left_margin   = Cm(2.0)
    sec.right_margin  = Cm(2.0)
    sec.top_margin    = Cm(1.8)
    sec.bottom_margin = Cm(1.8)

    # Strip the leading provenance HTML comment (the render_template
    # `include_header=True` provenance line — it's metadata, not content).
    body = PROV_COMMENT_RE.sub("", template_body, count=1)

    in_code_block = False
    in_list_block = False

    for raw_line in body.splitlines():
        line = raw_line.rstrip()

        # Code fences — flip state, render a horizontal-rule-ish separator
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.8)
            run = p.add_run(line)
            run.font.name = "Consolas"
            run.font.size = Pt(9)
            continue

        # Empty line — paragraph break
        if not line.strip():
            in_list_block = False
            continue

        # MUST / SHOULD marker as its own line
        marker = MUST_MARKER_RE.match(line.strip())
        if marker:
            _render_marker_line(doc, marker)
            continue

        # EDIT-ZONE markers
        ez_start = EDIT_ZONE_START.match(line.strip())
        if ez_start:
            _render_edit_zone_marker(doc, "EDIT START", ez_start.group(1))
            continue
        ez_end = EDIT_ZONE_END.match(line.strip())
        if ez_end:
            _render_edit_zone_marker(doc, "EDIT END",   ez_end.group(1))
            continue

        # <<TEXT>> placeholder
        if line.strip() == "<<TEXT>>":
            _render_text_placeholder(doc)
            continue

        # Other HTML comments — strip silently (provenance, leftover markers)
        if HTML_COMMENT_RE.match(line.strip()):
            continue

        # Headings
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
            continue
        if line.startswith("#### "):
            doc.add_heading(line[5:].strip(), level=4)
            continue

        # Horizontal rule
        if re.fullmatch(r"-{3,}\s*", line.strip()):
            p = doc.add_paragraph()
            run = p.add_run("─" * 40)   # box-drawing horizontal
            run.font.color.rgb = RGBColor(0xC8, 0xC5, 0xB8)
            continue

        # Blockquote (standard-text + advisory blocks)
        if line.startswith("> "):
            content = line[2:].strip()
            p = doc.add_paragraph(style="Intense Quote") if "_Standard text:_" in content \
                else doc.add_paragraph(style="Quote")
            _add_runs_with_formatting(p, content)
            continue
        if line.strip() == ">":
            doc.add_paragraph()
            continue

        # Checklist line (- [ ] or - [x]) — MUST match before generic list
        # else the leading "- " gets eaten by the unordered-list rule and
        # the "[ ]" leaks into the bullet text.
        m = re.match(r"^(\s*)-\s+\[([ xX])\]\s+(.*)$", line)
        if m:
            checked = m.group(2).lower() == "x"
            p = doc.add_paragraph()
            indent_level = len(m.group(1)) // 2
            if indent_level:
                p.paragraph_format.left_indent = Cm(0.6 * (indent_level + 1))
            cb = p.add_run("☒ " if checked else "☐ ")
            cb.font.size = Pt(11)
            _add_runs_with_formatting(p, m.group(3))
            continue

        # Unordered list
        m = re.match(r"^(\s*)[-*]\s+(.*)$", line)
        if m:
            indent_level = len(m.group(1)) // 2
            p = doc.add_paragraph(style="List Bullet")
            if indent_level:
                p.paragraph_format.left_indent = Cm(0.6 * (indent_level + 1))
            _add_runs_with_formatting(p, m.group(2))
            in_list_block = True
            continue

        # Ordered list
        m = re.match(r"^(\s*)\d+\.\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Number")
            _add_runs_with_formatting(p, m.group(2))
            in_list_block = True
            continue

        # Default — regular paragraph with inline formatting
        _add_paragraph(doc, line)

    # Serialize
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
