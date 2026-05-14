"""
ArionComply — Document Readers
Stage 1: Extract raw text and structure from uploaded files.
No LLM, no interpretation — pure extraction.

Supported formats:
  PDF   → pdfplumber (text + page markers)
  DOCX  → python-docx (text + heading structure)
  XLSX  → openpyxl (sheets + rows)
  TXT   → direct read
  CSV   → csv module

Dependencies:
  pip install pdfplumber python-docx openpyxl
"""
from __future__ import annotations

import csv
import io
import logging
import os
from pathlib import Path
from typing import Optional

from .models import ParsedDocument, RawSection

logger = logging.getLogger(__name__)

# Token estimate: 1 token ≈ 4 characters (conservative for compliance text)
CHARS_PER_TOKEN = 4


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def read_document(
    file_path: str,
    upload_id: Optional[str] = None,
) -> ParsedDocument:
    """
    Read a document and return a ParsedDocument with raw sections.
    Dispatches to the appropriate reader based on file extension.
    """
    path      = Path(file_path)
    ext       = path.suffix.lower().lstrip(".")
    file_name = path.name

    readers = {
        "pdf":  _read_pdf,
        "docx": _read_docx,
        "doc":  _read_docx,
        "xlsx": _read_xlsx,
        "xls":  _read_xlsx,
        "txt":  _read_txt,
        "csv":  _read_csv,
        "md":   _read_txt,
    }

    reader = readers.get(ext)
    if reader is None:
        logger.warning(f"Unsupported file type: {ext} — treating as plain text")
        reader = _read_txt

    logger.info(f"Reading {file_name} ({ext})")
    doc = reader(file_path, file_name)
    doc.upload_id = upload_id

    # Compute token estimate from full text
    doc.full_text     = "\n\n".join(s.text for s in doc.raw_sections if s.text.strip())
    doc.token_estimate = len(doc.full_text) // CHARS_PER_TOKEN

    logger.info(
        f"Read {file_name}: {len(doc.raw_sections)} sections, "
        f"~{doc.token_estimate:,} tokens, {doc.page_count} pages"
    )
    return doc


# =============================================================================
# PDF READER
# =============================================================================

def _read_pdf(file_path: str, file_name: str) -> ParsedDocument:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber required: pip install pdfplumber")

    sections = []
    page_count = 0

    with pdfplumber.open(file_path) as pdf:
        page_count = len(pdf.pages)
        current_heading = None
        current_text    = []
        section_start   = 1

        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            if not text.strip():
                continue

            lines = text.splitlines()
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Detect headings: short lines, possible numbering
                is_heading = (
                    len(stripped) < 80
                    and (
                        # Numbered heading: "1.", "1.1", "4.2 Access Control"
                        bool(__import__('re').match(r'^\d+\.?\d*\s+\w', stripped))
                        # All caps short line
                        or (stripped.isupper() and len(stripped) > 3)
                    )
                )

                if is_heading and current_text:
                    # Save current section
                    sections.append(RawSection(
                        section_id  = f"page_{section_start}_{page_num}",
                        heading     = current_heading,
                        text        = "\n".join(current_text),
                        page_start  = section_start,
                        page_end    = page_num,
                        level       = _detect_heading_level(current_heading or ""),
                    ))
                    current_heading = stripped
                    current_text    = []
                    section_start   = page_num
                elif is_heading:
                    current_heading = stripped
                else:
                    current_text.append(line)

        # Final section
        if current_text:
            sections.append(RawSection(
                section_id  = f"page_{section_start}_{page_count}",
                heading     = current_heading,
                text        = "\n".join(current_text),
                page_start  = section_start,
                page_end    = page_count,
                level       = _detect_heading_level(current_heading or ""),
            ))

    # If no sections detected (flat PDF), treat each page as a section
    if not sections:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    sections.append(RawSection(
                        section_id = f"page_{i}",
                        heading    = f"Page {i}",
                        text       = text,
                        page_start = i,
                        page_end   = i,
                        level      = 0,
                    ))

    return ParsedDocument(
        source_file  = file_path,
        file_type    = "pdf",
        original_name = file_name,
        raw_sections = sections,
        page_count   = page_count,
    )


# =============================================================================
# DOCX READER
# =============================================================================

def _read_docx(file_path: str, file_name: str) -> ParsedDocument:
    try:
        import docx
    except ImportError:
        raise ImportError("python-docx required: pip install python-docx")

    doc      = docx.Document(file_path)
    sections = []

    current_heading  = None
    current_level    = 0
    current_paras    = []
    section_idx      = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name if para.style else ""
        is_heading = "Heading" in style_name

        if is_heading:
            if current_paras:
                sections.append(RawSection(
                    section_id = f"section_{section_idx}",
                    heading    = current_heading,
                    text       = "\n".join(current_paras),
                    page_start = None,
                    page_end   = None,
                    level      = current_level,
                ))
                section_idx += 1

            # Extract heading level from style name (Heading 1, Heading 2, ...)
            import re
            m = re.search(r'(\d+)', style_name)
            current_level   = int(m.group(1)) if m else 1
            current_heading = text
            current_paras   = []
        else:
            current_paras.append(text)

    # Final section
    if current_paras:
        sections.append(RawSection(
            section_id = f"section_{section_idx}",
            heading    = current_heading,
            text       = "\n".join(current_paras),
            page_start = None,
            page_end   = None,
            level      = current_level,
        ))

    return ParsedDocument(
        source_file   = file_path,
        file_type     = "docx",
        original_name = file_name,
        raw_sections  = sections,
        page_count    = 0,  # DOCX doesn't easily expose page count
    )


# =============================================================================
# XLSX READER
# =============================================================================

# Fuzzy column name matching for compliance workbooks
_CONTROL_REF_ALIASES = [
    "control", "control_ref", "control ref", "iso ref", "clause",
    "control id", "controlid", "ref", "control number", "annex",
]
_FINDING_ALIASES = [
    "finding", "status", "compliance", "result", "assessment",
    "compliant", "gap status", "implementation",
]
_GAP_ALIASES = [
    "gap", "gap_description", "gap description", "comment", "notes",
    "evidence", "description", "observation", "detail",
]
_EVIDENCE_ALIASES = [
    "evidence", "evidence_text", "evidence text", "justification",
    "supporting evidence", "rationale",
]


def _fuzzy_col(headers: list[str], aliases: list[str]) -> Optional[int]:
    """Find column index by fuzzy name matching."""
    headers_lower = [h.lower().strip() for h in headers]
    for alias in aliases:
        for i, h in enumerate(headers_lower):
            if alias in h or h in alias:
                return i
    return None


def _is_compliance_workbook(headers: list[str]) -> bool:
    """Return True if the sheet looks like a compliance assessment workbook."""
    has_control = _fuzzy_col(headers, _CONTROL_REF_ALIASES) is not None
    has_finding = _fuzzy_col(headers, _FINDING_ALIASES) is not None
    return has_control and has_finding


def _normalise_finding_value(val: str) -> str:
    """Map workbook finding values to canonical NC/OFI/Comply/N/A."""
    if not val:
        return "not_addressed"
    v = str(val).strip().lower()

    comply_terms  = ["comply", "compliant", "yes", "implemented", "done",
                     "complete", "full", "met", "pass", "✓", "green", "high"]
    ofi_terms     = ["ofi", "partial", "partly", "in progress", "improving",
                     "medium", "amber", "yellow", "opportunity"]
    nc_terms      = ["nc", "non-conform", "no", "not implemented", "fail",
                     "missing", "not met", "red", "critical", "not done"]
    na_terms      = ["n/a", "na", "not applicable", "out of scope", "excluded"]

    for term in comply_terms:
        if term in v:
            return "Comply"
    for term in ofi_terms:
        if term in v:
            return "OFI"
    for term in nc_terms:
        if term in v:
            return "NC"
    for term in na_terms:
        if term in v:
            return "N/A"
    return "not_addressed"


def _read_xlsx(file_path: str, file_name: str) -> ParsedDocument:
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl required: pip install openpyxl")

    wb       = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sections = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue

        # Find header row (first non-empty row)
        header_row = None
        header_idx = 0
        for i, row in enumerate(rows):
            if any(cell for cell in row if cell is not None):
                header_row = [str(c).strip() if c is not None else "" for c in row]
                header_idx = i
                break

        if header_row is None:
            continue

        if _is_compliance_workbook(header_row):
            # Structured compliance workbook — parse as data
            col_ctrl  = _fuzzy_col(header_row, _CONTROL_REF_ALIASES)
            col_find  = _fuzzy_col(header_row, _FINDING_ALIASES)
            col_gap   = _fuzzy_col(header_row, _GAP_ALIASES)
            col_evid  = _fuzzy_col(header_row, _EVIDENCE_ALIASES)

            structured_rows = []
            for row in rows[header_idx + 1:]:
                ctrl = row[col_ctrl] if col_ctrl is not None else None
                find = row[col_find] if col_find is not None else None
                if not ctrl or not find:
                    continue
                structured_rows.append({
                    "control_ref":    str(ctrl).strip(),
                    "finding_raw":    str(find).strip(),
                    "finding":        _normalise_finding_value(str(find)),
                    "gap_description": str(row[col_gap]).strip() if col_gap is not None and row[col_gap] else "",
                    "evidence_text":   str(row[col_evid]).strip() if col_evid is not None and row[col_evid] else "",
                })

            # Represent as a single section with structured metadata
            text = f"COMPLIANCE WORKBOOK SHEET: {sheet_name}\n"
            text += "\n".join(
                f"{r['control_ref']} | {r['finding']} | {r['gap_description']}"
                for r in structured_rows
            )
            sections.append(RawSection(
                section_id = f"sheet_{sheet_name}",
                heading    = sheet_name,
                text       = text,
                page_start = None,
                page_end   = None,
                level      = 0,
                metadata   = {
                    "structured":    True,
                    "sheet_name":    sheet_name,
                    "column_map": {
                        "control_ref": header_row[col_ctrl] if col_ctrl is not None else None,
                        "finding":     header_row[col_find] if col_find is not None else None,
                        "gap":         header_row[col_gap]  if col_gap  is not None else None,
                    },
                    "rows": structured_rows,
                },
            ))
        else:
            # Narrative sheet — extract as text
            text_lines = []
            for row in rows:
                line = " | ".join(
                    str(c).strip() for c in row if c is not None and str(c).strip()
                )
                if line:
                    text_lines.append(line)
            if text_lines:
                sections.append(RawSection(
                    section_id = f"sheet_{sheet_name}",
                    heading    = sheet_name,
                    text       = "\n".join(text_lines),
                    page_start = None,
                    page_end   = None,
                    level      = 0,
                    metadata   = {"structured": False, "sheet_name": sheet_name},
                ))

    wb.close()

    return ParsedDocument(
        source_file   = file_path,
        file_type     = "xlsx",
        original_name = file_name,
        raw_sections  = sections,
        page_count    = 0,
    )


# =============================================================================
# TXT / CSV READERS
# =============================================================================

def _read_txt(file_path: str, file_name: str) -> ParsedDocument:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Split at double newlines (paragraph boundaries)
    import re
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    sections = []
    for i, para in enumerate(paragraphs):
        sections.append(RawSection(
            section_id = f"para_{i}",
            heading    = None,
            text       = para,
            page_start = None,
            page_end   = None,
            level      = 0,
        ))

    return ParsedDocument(
        source_file   = file_path,
        file_type     = "txt",
        original_name = file_name,
        raw_sections  = sections,
        page_count    = 0,
    )


def _read_csv(file_path: str, file_name: str) -> ParsedDocument:
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows    = list(reader)

    if _is_compliance_workbook(headers):
        # Treat like a structured XLSX sheet
        col_ctrl = _fuzzy_col(headers, _CONTROL_REF_ALIASES)
        col_find = _fuzzy_col(headers, _FINDING_ALIASES)
        col_gap  = _fuzzy_col(headers, _GAP_ALIASES)

        structured_rows = []
        for row in rows:
            ctrl = row.get(headers[col_ctrl], "") if col_ctrl is not None else ""
            find = row.get(headers[col_find], "") if col_find is not None else ""
            if not ctrl or not find:
                continue
            structured_rows.append({
                "control_ref":     ctrl.strip(),
                "finding":         _normalise_finding_value(find),
                "gap_description": row.get(headers[col_gap], "").strip() if col_gap is not None else "",
            })

        text = "COMPLIANCE CSV\n" + "\n".join(
            f"{r['control_ref']} | {r['finding']} | {r['gap_description']}"
            for r in structured_rows
        )
        section = RawSection(
            section_id = "csv_data",
            heading    = "CSV Data",
            text       = text,
            page_start = None,
            page_end   = None,
            level      = 0,
            metadata   = {"structured": True, "rows": structured_rows},
        )
    else:
        text = "\n".join(
            " | ".join(str(v) for v in row.values() if v)
            for row in rows
        )
        section = RawSection(
            section_id = "csv_data",
            heading    = "CSV Data",
            text       = text,
            page_start = None,
            page_end   = None,
            level      = 0,
            metadata   = {"structured": False},
        )

    return ParsedDocument(
        source_file   = file_path,
        file_type     = "csv",
        original_name = file_name,
        raw_sections  = [section],
        page_count    = 0,
    )


# =============================================================================
# HELPERS
# =============================================================================

def _detect_heading_level(heading: str) -> int:
    """Detect heading level from numbering pattern."""
    import re
    if not heading:
        return 0
    m = re.match(r'^(\d+)(\.\d+)*', heading)
    if m:
        dots = heading[:m.end()].count(".")
        return dots + 1
    if heading.isupper():
        return 1
    return 0
