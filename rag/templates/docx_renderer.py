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
# Ship 54'.d — doc-control + revision-history markers. When a template
# includes <<DOC_CONTROL>>, the renderer emits a document-control
# table (Doc No / Rev / Prepared / Reviewed / Approved / Date + wet-
# sign lines). <<REVISION_HISTORY>> emits an empty audit-defensible
# revision history table. Optional per-template — not every template
# is a controlled document.
DOC_CONTROL_RE       = re.compile(r"^\s*<<DOC_CONTROL>>\s*$")
REVISION_HISTORY_RE  = re.compile(r"^\s*<<REVISION_HISTORY>>\s*$")
# Ship 57' — per-leaf prerequisites marker. Sits once per template
# (typically under "Before you start"); rendered as a grouped callout
# based on the target leaf_id. Empty prereqs ⇒ marker silently dropped.
PREREQUISITES_MARKER_RE = re.compile(r"^\s*<<PREREQUISITES>>\s*$")

# Ship 56'.a — per-MUST guidance marker. Interleaved between the
# MUST/SHOULD marker and the tenant's <<TEXT>> placeholder; resolves to
# the guidance array on the preceding ChecklistItem.
GUIDANCE_MARKER_RE  = re.compile(r"^\s*<<GUIDANCE>>\s*$")
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
    from rag.id_types import item_slug
    slug = item_slug(mid) or mid
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


def _render_guidance_block(doc, guidance: tuple[str, ...] | list[str]) -> None:
    """Render a per-MUST guidance callout: bold 'Best practice:' label
    followed by an indented bullet list of imperative steps. Ship 56'.a."""
    if not guidance:
        return
    label_p = doc.add_paragraph()
    label_p.paragraph_format.space_before = Pt(6)
    label_p.paragraph_format.space_after  = Pt(2)
    lr = label_p.add_run("Best practice:")
    lr.bold = True
    lr.font.size = Pt(10)
    lr.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    for g in guidance:
        bp = doc.add_paragraph(style="List Bullet")
        bp.paragraph_format.left_indent   = Cm(0.8)
        bp.paragraph_format.space_before  = Pt(0)
        bp.paragraph_format.space_after   = Pt(2)
        _add_runs_with_formatting(bp, g)
        for run in bp.runs:
            if run.font.size is None:
                run.font.size = Pt(10)


def _render_prerequisites_block(doc, prereqs) -> None:
    """Render the per-leaf prerequisites callout: bold "Prerequisites:"
    label, then grouped entries (foundational → direct → cross_role)
    each with a ref+title heading, a Why line, and an optional
    Good-enough line. Ship 57'."""
    if not prereqs:
        return
    order = ("foundational", "direct", "cross_role")
    by_cat: dict[str, list] = {}
    for p in prereqs:
        by_cat.setdefault(p.category, []).append(p)

    label_p = doc.add_paragraph()
    label_p.paragraph_format.space_before = Pt(6)
    label_p.paragraph_format.space_after  = Pt(2)
    lr = label_p.add_run("Prerequisites:")
    lr.bold = True
    lr.font.size = Pt(10)
    lr.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    for cat in order:
        for p in by_cat.get(cat, []):
            ref_display = _humanize_std_ref(p.standard_id, p.ref)
            head = doc.add_paragraph(style="List Bullet")
            head.paragraph_format.left_indent  = Cm(0.8)
            head.paragraph_format.space_before = Pt(2)
            head.paragraph_format.space_after  = Pt(0)
            head_run = head.add_run(f"{ref_display} — {p.title}")
            head_run.bold = True
            head_run.font.size = Pt(10)

            why = doc.add_paragraph()
            why.paragraph_format.left_indent  = Cm(1.4)
            why.paragraph_format.space_before = Pt(0)
            why.paragraph_format.space_after  = Pt(0)
            _add_runs_with_formatting(why, f"Why: {p.rationale}")
            for run in why.runs:
                if run.font.size is None:
                    run.font.size = Pt(10)

            if p.good_enough:
                ge = doc.add_paragraph()
                ge.paragraph_format.left_indent  = Cm(1.4)
                ge.paragraph_format.space_before = Pt(0)
                ge.paragraph_format.space_after  = Pt(2)
                _add_runs_with_formatting(ge, f"Good enough: {p.good_enough}")
                for run in ge.runs:
                    if run.font.size is None:
                        run.font.size = Pt(10)


def _humanize_std_ref(standard_id: str, ref: str) -> str:
    """Compact display form for prereq ref+std headers."""
    if standard_id.startswith("GDPR:"):
        return f"GDPR {ref}"
    if standard_id.startswith("ISO27001:"):
        return f"ISO 27001 {ref}"
    if standard_id.startswith("ISO27701:"):
        return f"ISO 27701 {ref}"
    return f"{standard_id} {ref}"


def _render_text_placeholder(doc) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run("[ Click to enter your evidence here ]")
    run.italic         = True
    run.font.size      = Pt(11)
    run.font.color.rgb = RGBColor(0x9C, 0x9A, 0x8E)


# ── Main converter ──────────────────────────────────────────────────────────

# ── Ship 54'.d — doc-control + revision-history block renderers ─────────

def _derive_doc_number(leaf_id: str, template_version: int | None) -> str:
    """Compose a human-readable document number from the leaf_id.

    Examples:
      req:5.2:information_security_policy → ISP-5.2-Rev00
      req:A.5.15:communication_record     → REC-A.5.15-Rev00
      req:Art.30:records_of_processing    → ROPA-Art.30-Rev00

    Convention: {TYPE_PREFIX}-{control_ref}-Rev{template_version:02d}.
    The TYPE_PREFIX is derived from the leaf_type token (e.g. policy →
    POL, procedure → PRC, register → REG, record → REC). Falls back
    to the raw leaf_type slug when unknown so the doc number is always
    populated + curator-overridable in future via template YAML.
    """
    parts = (leaf_id or "").split(":")
    if len(parts) < 3:
        return leaf_id or "DOC"
    ctrl_ref, leaf_type = parts[1], parts[2]
    lt = leaf_type.lower()
    if "policy" in lt:
        prefix = "POL"
    elif "procedure" in lt or "process" in lt:
        prefix = "PRC"
    elif "register" in lt:
        prefix = "REG"
    elif "record" in lt or "log" in lt:
        prefix = "REC"
    elif "review" in lt:
        prefix = "REV"
    elif "framework" in lt:
        prefix = "FRM"
    elif "manual" in lt:
        prefix = "MAN"
    elif "scope" in lt:
        prefix = "SCP"
    else:
        prefix = "DOC"
    rev = f"Rev{(template_version or 1):02d}"
    return f"{prefix}-{ctrl_ref}-{rev}"


def _render_doc_control_block(
    doc, leaf_id: str, template_version: int | None,
) -> None:
    """Insert a document-control table matching consultant-toolkit
    convention (mirrors Share.zip L2-PRC-003 doc-control block).

    Layout (2-column table):
      Document No.       | {derived from leaf_id}
      Revision           | Rev{template_version:02d}
      Revision Date      | {today, DD MMM YYYY}
      Prepared By        | ___________________________ (wet-sign)
      Reviewed By        | ___________________________
      Approved By        | ___________________________

    Deliberate blanks on Prepared/Reviewed/Approved — the tenant fills
    those at document-control review. No auto-fill from tenant_profile
    for the MVP (deferred; tenant_profile doesn't carry
    prepared_by / reviewed_by fields).
    """
    from datetime import date
    doc_no = _derive_doc_number(leaf_id, template_version)
    today  = date.today().strftime("%d %b %Y")
    rev    = f"Rev{(template_version or 1):02d}"

    rows: list[tuple[str, str]] = [
        ("Document No.",   doc_no),
        ("Revision",       rev),
        ("Revision Date",  today),
        ("Prepared By",    "___________________________"),
        ("Reviewed By",    "___________________________"),
        ("Approved By",    "___________________________"),
    ]

    table = doc.add_table(rows=len(rows), cols=2)
    table.style = "Light Grid Accent 1"
    table.autofit = True
    for i, (label, value) in enumerate(rows):
        c0 = table.cell(i, 0)
        c1 = table.cell(i, 1)
        c0.text = ""
        c1.text = ""
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(10)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(value)
        r1.font.size = Pt(10)

    # Small trailing paragraph to separate from body content
    doc.add_paragraph()


def _render_revision_history_block(
    doc, template_version: int | None,
) -> None:
    """Insert a revision-history table. Empty audit-defensible shape:
    curator/tenant adds one row per version. Convention matches Share
    L2-PRC-003 revision-history block.

    Columns: Version | Date | Description of Change | Author

    Seeded with one row for the current template_version + today's
    date. Future edits append rows.
    """
    from datetime import date

    doc.add_heading("Revision History", level=2)

    table = doc.add_table(rows=2, cols=4)
    table.style = "Light Grid Accent 1"
    table.autofit = True

    # Header row
    hdr = ["Version", "Date", "Description of Change", "Author"]
    for i, h in enumerate(hdr):
        c = table.cell(0, i)
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(10)

    # Current-version seed row
    today = date.today().strftime("%d %b %Y")
    rev = f"{(template_version or 1):02d}"
    seed = [rev, today, "Initial issue / current version", ""]
    for i, v in enumerate(seed):
        c = table.cell(1, i)
        c.text = ""
        r = c.paragraphs[0].add_run(v)
        r.font.size = Pt(10)

    doc.add_paragraph()


def render_template_docx(
    pg_conn,
    tenant_id: str,
    leaf_id:   str,
    template_body: str,
    template_version: int | None = None,
) -> bytes:
    """Convert the rendered markdown body to a .docx workbook.

    Walks line-by-line, maps markdown idioms to Word styles, and
    preserves structural markers as visible cues. Returns bytes
    suitable for HTTP response.

    Ship 54'.d — the walk also detects <<DOC_CONTROL>> and
    <<REVISION_HISTORY>> markers and dispatches to the block
    renderers. `template_version` is passed through so those blocks
    can render the current Rev number.
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
    current_item_id: str | None = None   # Ship 56'.a — set on MUST/SHOULD marker;
                                          # consumed by <<GUIDANCE>> marker.

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

        # Ship 54'.d — <<DOC_CONTROL>> marker → document-control table
        if DOC_CONTROL_RE.match(line):
            _render_doc_control_block(doc, leaf_id, template_version)
            continue

        # Ship 54'.d — <<REVISION_HISTORY>> marker → revision history table
        if REVISION_HISTORY_RE.match(line):
            _render_revision_history_block(doc, template_version)
            continue

        # MUST / SHOULD marker as its own line
        marker = MUST_MARKER_RE.match(line.strip())
        if marker:
            current_item_id = marker.group(2)
            _render_marker_line(doc, marker)
            continue

        # Ship 56'.a — <<GUIDANCE>> marker → per-MUST guidance callout
        # for the preceding MUST/SHOULD's ChecklistItem. Empty list ⇒
        # marker silently dropped.
        if GUIDANCE_MARKER_RE.match(line):
            if current_item_id:
                from rag.templates.guidance_lookup import get_guidance_for_item
                _render_guidance_block(doc, get_guidance_for_item(current_item_id))
            continue

        # Ship 57' — <<PREREQUISITES>> marker → per-leaf prereqs callout.
        # Uses the template's target leaf_id (parameter to this function),
        # not a preceding item marker. Empty prereqs ⇒ marker dropped.
        if PREREQUISITES_MARKER_RE.match(line):
            from rag.templates.prerequisites_lookup import get_prerequisites_for_leaf
            _render_prerequisites_block(doc, get_prerequisites_for_leaf(leaf_id))
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
