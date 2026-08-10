"""
Templates Pass 1 — architecture normalization.

Adds a canonical section skeleton to db/templates/*.md.  Additive-only —
never modifies existing content.  Idempotent — re-running skips sections
that already exist.

Canonical section order (inserted between the title/purpose blockquotes
and the first body section):

    ## What this template gives you    (LLM prose, ~1-2 sentences)
    ## When to use it                  (LLM prose)
    ## Before you start                (with <<PREREQUISITES>> marker)
    ## Cross-references                (with <<CROSS_REFERENCES>> marker)
    ## Estimated effort                (LLM prose)

Appended at end (in that order) unless present:

    ## Doc control                     (with <<DOC_CONTROL>> marker)
    ## Revision history                (with <<REVISION_HISTORY>> marker)

Per-section additivity: a missing canonical section is filled in.  An
existing canonical section (e.g. hand-authored "Before you start" on a
tier-A anchor template) is left entirely untouched — no marker injection,
no content modification.  Marker verification is Pass 2/3/4/5's scope.

LLM prose is generated in a single gpt-4.1 call per template returning
JSON with 3 keys.  Line-based fallback parser copied from Ship 56'/57'.

Modes:
    # dry-run + diff for one template (no write, no LLM call cost)
    python3 -m scripts.dev.templates_pass1_architecture --sample req:A.7.9:off_premises_assets_policy

    # generate + diff for one template (LLM call, no write)
    python3 -m scripts.dev.templates_pass1_architecture --sample req:A.7.9:off_premises_assets_policy --with-llm

    # bulk
    python3 -m scripts.dev.templates_pass1_architecture --bulk --yes
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATES = _ROOT / "db" / "templates"

_MODEL = "gpt-4.1"

# ── Canonical section metadata ─────────────────────────────────────────────
# key → (heading_line, section_body_generator_key_or_marker)
_CANON: list[tuple[str, str]] = [
    ("what_it_gives_you", "## What this template gives you"),
    ("when_to_use",       "## When to use it"),
    ("prerequisites",     "## Prerequisites"),
    ("cross_references",  "## Cross-references"),
    ("estimated_effort",  "## Estimated effort"),
]
_FOOTER: list[tuple[str, str]] = [
    # Ship convention 2026-08-08: <<DOC_CONTROL>> is placed TOP-INLINE
    # (bare marker right after H1, no heading) — see _ensure_doc_control_top_inline.
    ("revision_history", "## Revision history"),
]

_DOC_CONTROL_MARKER = "<<DOC_CONTROL>>"

_CANON_HEADINGS_LC = {h.lower() for _, h in _CANON}
_FOOTER_HEADINGS_LC = {h.lower() for _, h in _FOOTER}
_STRUCTURAL_HEADINGS_LC = _CANON_HEADINGS_LC | _FOOTER_HEADINGS_LC

_LLM_PROSE_KEYS = {"what_it_gives_you", "when_to_use", "estimated_effort"}


# ── Parsing ────────────────────────────────────────────────────────────────
@dataclass
class ParsedTemplate:
    path:              Path
    frontmatter_text:  str          # raw block including the --- lines, or ""
    frontmatter:       dict         # parsed
    pre_canonical:     str          # everything from after frontmatter up to first H2
    sections:          list[tuple[str, str]]  # (heading_line, section_content) in order
    trailing_ws:       str

    def canonical_headings_present(self) -> set[str]:
        return {h.lower().strip() for h, _ in self.sections
                if h.lower().strip() in _CANON_HEADINGS_LC}

    def footer_headings_present(self) -> set[str]:
        return {h.lower().strip() for h, _ in self.sections
                if h.lower().strip() in _FOOTER_HEADINGS_LC}


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H2_LINE_RE = re.compile(r"^(##[ \t]+.+)$", re.MULTILINE)


def _parse(path: Path) -> ParsedTemplate:
    text = path.read_text()

    fm_text = ""
    fm: dict = {}
    fm_match = _FRONTMATTER_RE.match(text)
    if fm_match:
        fm_text = fm_match.group(0)
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError:
            fm = {}
        body = text[fm_match.end():]
    else:
        body = text

    # Find all H2 line offsets to split into (pre-canonical, sections).
    h2_matches = list(_H2_LINE_RE.finditer(body))
    if not h2_matches:
        pre = body.rstrip("\n") + "\n"
        return ParsedTemplate(path, fm_text, fm, pre, [], "")

    pre = body[:h2_matches[0].start()]

    # Sections span from each H2 line to the next H2 (or end).
    sections: list[tuple[str, str]] = []
    for i, m in enumerate(h2_matches):
        start = m.start()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        chunk = body[start:end]
        # Split heading line from content
        nl = chunk.find("\n")
        if nl == -1:
            heading, content = chunk, ""
        else:
            heading, content = chunk[:nl], chunk[nl + 1:]
        sections.append((heading, content))

    return ParsedTemplate(path, fm_text, fm, pre, sections, "")


# ── Section generators ─────────────────────────────────────────────────────
def _section_with_marker(heading: str, marker: str) -> tuple[str, str]:
    content = f"\n{marker}\n\n"
    return (heading, content)


def _section_with_prose(heading: str, prose: str) -> tuple[str, str]:
    content = f"\n{prose.strip()}\n\n"
    return (heading, content)


def _build_missing_section(key: str, heading: str, prose: dict) -> tuple[str, str]:
    if key == "prerequisites":
        return _section_with_marker(heading, "<<PREREQUISITES>>")
    if key == "cross_references":
        return _section_with_marker(heading, "<<CROSS_REFERENCES>>")
    if key == "doc_control":
        return _section_with_marker(heading, "<<DOC_CONTROL>>")
    if key == "revision_history":
        return _section_with_marker(heading, "<<REVISION_HISTORY>>")
    # LLM-prose sections
    return _section_with_prose(heading, prose.get(key, "").strip())


# ── LLM prose ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = (
    "You are a compliance documentation writer. Produce three short, "
    "tenant-facing prose blocks about a compliance document template. "
    "Plain English, no system-slug jargon (do not say 'MUST', "
    "'evidence_type', 'trigger_type', etc.). "
    "Return JSON only with exactly three keys: "
    "gives_you, when_to_use, estimated_effort. "
    "Each value is a single-paragraph string, 1-2 sentences (max ~35 words)."
)


def _humanize_evidence_type(et: str) -> str:
    return (et or "").replace("_", " ").strip() or "document"


def _humanize_trigger(trigger: str) -> str:
    m = {
        "universal":     "always applies to your environment",
        "profile_fact":  "applies when your profile matches specific triggers",
        "lifecycle_end": "produced at the close of a lifecycle event",
        "annual_cycle":  "part of the annual compliance cycle",
    }
    return m.get(trigger or "", (trigger or "").replace("_", " "))


def _fresh_desc(days: Optional[int]) -> str:
    if not days:
        return "as needed"
    if days >= 365:
        return f"about once a year (every {days} days)"
    if days >= 180:
        return f"about twice a year (every {days} days)"
    if days >= 90:
        return f"quarterly (every {days} days)"
    return f"every {days} days"


def _framework_role(std_id: str) -> str:
    if std_id == "ISO27001:2022": return "ISO 27001 (Program)"
    if std_id == "ISO27701:2019": return "ISO 27701 (Privacy Extension)"
    if std_id == "GDPR:2016/679": return "GDPR (Obligation)"
    return std_id or "?"


def _prompt_user(fm: dict, title: str, purpose: str) -> str:
    parts = [
        f"TEMPLATE:",
        f"  title: {title}",
        f"  purpose: {purpose}",
        f"  standard: {_framework_role(fm.get('standard_id', ''))}",
        f"  control: {fm.get('control_ref', '?')}",
        f"  document type: {_humanize_evidence_type(fm.get('evidence_type', ''))}",
        f"  trigger cadence: {_humanize_trigger(fm.get('trigger_type', ''))}",
        f"  refresh: {_fresh_desc(fm.get('freshness_days'))}",
        f"  required elements: {fm.get('must_count', 0)}",
        f"  recommended elements: {fm.get('should_count', 0)}",
        f"  shape: {'tabular register' if fm.get('table_shape') else 'prose document'}",
        "",
        "For each of gives_you / when_to_use / estimated_effort, produce 1-2 sentences.",
        "- gives_you: what this template provides. The tenant reads this to decide 'is this for me?'",
        "- when_to_use: when to use it. Include the trigger + refresh cadence in natural language.",
        "- estimated_effort: realistic time estimate for filling it in from scratch.",
        "  Factor: each required element ≈10-15 minutes to author; registers scale per row.",
        "",
        "Return JSON only.",
    ]
    return "\n".join(parts)


def _parse_llm_json(text: str) -> Optional[dict]:
    t = (text or "").strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        t = "\n".join(lines)
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            return d
    except json.JSONDecodeError:
        pass
    # Line-based fallback: match `"key": "..."` per line
    out: dict = {}
    for line in t.splitlines():
        m = re.match(r'^\s*"?(\w+)"?\s*[:=]\s*"?(.+?)"?\s*,?\s*$', line)
        if m:
            k, v = m.group(1), m.group(2)
            if k in {"gives_you", "when_to_use", "estimated_effort"}:
                out[k] = v.strip('"').strip()
    return out or None


def _call_llm(fm: dict, title: str, purpose: str) -> Optional[dict]:
    from rag.llm_client import call as llm_call
    resp = llm_call(
        system=_SYSTEM_PROMPT,
        user=_prompt_user(fm, title, purpose),
        model=_MODEL,
        purpose="guidance_gen",   # reuse allowlisted purpose
        max_tokens=600,
        temperature=0.2,
        timeout_s=45.0,
    )
    if resp.error:
        print(f"  ⚠ LLM error: {resp.error}", file=sys.stderr)
        return None
    parsed = _parse_llm_json(resp.text or "")
    if not parsed:
        print(f"  ⚠ unparseable LLM response:\n{resp.text[:500]}", file=sys.stderr)
        return None
    # Normalize keys → generator key mapping
    return {
        "what_it_gives_you": parsed.get("gives_you", "").strip(),
        "when_to_use":        parsed.get("when_to_use", "").strip(),
        "estimated_effort":   parsed.get("estimated_effort", "").strip(),
    }


# ── Rebuild ────────────────────────────────────────────────────────────────
def _rebuild(parsed: ParsedTemplate, prose: dict) -> tuple[str, list[str]]:
    """Assemble a new template body. Returns (new_text, sections_added).

    Additive: existing sections retained in place. Missing canonical
    sections inserted at their canonical position (before the first body
    section). Missing footer sections appended at the end.
    """
    sections_added: list[str] = []

    canonical_present  = parsed.canonical_headings_present()
    footer_present     = parsed.footer_headings_present()

    # Split existing sections into (leading_canonical_or_footer, body).
    # We treat the FIRST non-canonical, non-footer H2 as the start of body.
    body_start_idx = None
    for i, (heading, _) in enumerate(parsed.sections):
        if heading.lower().strip() not in _STRUCTURAL_HEADINGS_LC:
            body_start_idx = i
            break

    leading  = parsed.sections if body_start_idx is None else parsed.sections[:body_start_idx]
    body     = [] if body_start_idx is None else parsed.sections[body_start_idx:]

    # Now build the canonical block: all 5 in canonical order.
    # For each canonical key, use existing (from leading) if present,
    # else build a new one.
    def _find(existing: list[tuple[str, str]], heading_lc: str) -> Optional[tuple[str, str]]:
        for h, c in existing:
            if h.lower().strip() == heading_lc:
                return (h, c)
        return None

    new_canonical: list[tuple[str, str]] = []
    for key, heading in _CANON:
        found = _find(leading, heading.lower())
        if found:
            new_canonical.append(found)
        else:
            new_canonical.append(_build_missing_section(key, heading, prose))
            sections_added.append(heading)

    # Footer block: doc_control + revision_history at the end.
    # Existing footer sections may be interspersed anywhere — collect from
    # both leading + body positions and keep at end.
    footer_sections: list[tuple[str, str]] = []
    for src in (leading, body):
        for h, c in src:
            if h.lower().strip() in _FOOTER_HEADINGS_LC:
                footer_sections.append((h, c))

    # Body without footer sections
    body_filtered = [(h, c) for h, c in body if h.lower().strip() not in _FOOTER_HEADINGS_LC]

    new_footer: list[tuple[str, str]] = []
    for key, heading in _FOOTER:
        found = _find(footer_sections, heading.lower())
        if found:
            new_footer.append(found)
        else:
            new_footer.append(_build_missing_section(key, heading, prose))
            sections_added.append(heading)

    # Ensure <<DOC_CONTROL>> top-inline: right after H1 in pre_canonical.
    pre = parsed.pre_canonical
    if not _has_doc_control_marker(parsed):
        m = re.search(r"(^#\s+[^\n]+\n)", pre, re.MULTILINE)
        if m:
            insert_pos = m.end()
            pre = pre[:insert_pos] + "\n" + _DOC_CONTROL_MARKER + "\n" + pre[insert_pos:]
            sections_added.append(_DOC_CONTROL_MARKER + " (top-inline)")

    # Serialize
    parts = [parsed.frontmatter_text]
    if pre:
        parts.append(pre.rstrip("\n") + "\n\n")
    for h, c in new_canonical + body_filtered + new_footer:
        parts.append(f"{h}\n{c}".rstrip("\n") + "\n\n")
    return "".join(parts).rstrip("\n") + "\n", sections_added


def _extract_title_and_purpose(pre: str) -> tuple[str, str]:
    title = ""
    purpose = ""
    for line in pre.splitlines():
        s = line.strip()
        if not title and s.startswith("# ") and not s.startswith("## "):
            title = s[2:].strip()
            continue
        if not purpose and s.startswith("> "):
            purpose = s[2:].strip()
            break
    return title, purpose


# ── Commands ───────────────────────────────────────────────────────────────
def _template_path_for_leaf(leaf_id: str) -> Path:
    slug = leaf_id.replace(":", "__").replace(".", "_")
    return _TEMPLATES / f"{slug}.md"


def _has_doc_control_marker(parsed: ParsedTemplate) -> bool:
    """True if <<DOC_CONTROL>> marker exists anywhere in the file (pre-canonical,
    canonical, body, or footer sections)."""
    if _DOC_CONTROL_MARKER in parsed.pre_canonical:
        return True
    for _, content in parsed.sections:
        if _DOC_CONTROL_MARKER in content:
            return True
    return False


def _needs_work(parsed: ParsedTemplate) -> bool:
    if _CANON_HEADINGS_LC - parsed.canonical_headings_present():
        return True
    if _FOOTER_HEADINGS_LC - parsed.footer_headings_present():
        return True
    if not _has_doc_control_marker(parsed):
        return True
    return False


def cmd_sample(leaf_id: str, with_llm: bool) -> None:
    p = _template_path_for_leaf(leaf_id)
    if not p.exists():
        print(f"!! not found: {p}", file=sys.stderr); return

    parsed = _parse(p)
    if not _needs_work(parsed):
        print(f"template already normalized — nothing to add: {p.name}")
        return

    title, purpose = _extract_title_and_purpose(parsed.pre_canonical)
    prose: dict = {}
    llm_needed = _CANON_HEADINGS_LC - parsed.canonical_headings_present()
    llm_needed = {h for h in llm_needed if any(
        k for k, hd in _CANON if hd.lower() == h and k in _LLM_PROSE_KEYS
    )}

    if with_llm and llm_needed:
        print(f"[LLM] generating prose for {p.name}...")
        prose = _call_llm(parsed.frontmatter, title, purpose) or {}
    elif llm_needed:
        prose = {k: f"[LLM prose placeholder for {k}]"
                 for k in ("what_it_gives_you", "when_to_use", "estimated_effort")}

    new_text, added = _rebuild(parsed, prose)
    print(f"=== {p.name} ===")
    print(f"sections that would be added ({len(added)}):")
    for a in added:
        print(f"  + {a}")
    print()
    print("--- FIRST 60 LINES OF PROPOSED OUTPUT ---")
    for line in new_text.splitlines()[:60]:
        print(line)


def cmd_bulk(dry_run: bool, skip_confirm: bool) -> None:
    files = sorted(_TEMPLATES.glob("req__*.md"))
    needs: list[Path] = []
    for p in files:
        if _needs_work(_parse(p)):
            needs.append(p)
    print(f"Total templates:    {len(files)}")
    print(f"Already normalized: {len(files) - len(needs)}")
    print(f"To update:          {len(needs)}")
    est = len(needs) * 0.003
    print(f"Est. cost (rough):  ${est:.2f}  ({_MODEL})")
    if dry_run:
        print("(dry-run — no LLM calls, no writes)")
        return
    if not skip_confirm:
        print("\nConfirm bulk? Type 'yes' to proceed:")
        if input().strip().lower() != "yes":
            print("Aborted."); return

    ok = fail = 0
    for i, p in enumerate(needs, 1):
        parsed = _parse(p)
        title, purpose = _extract_title_and_purpose(parsed.pre_canonical)
        prose = _call_llm(parsed.frontmatter, title, purpose) or {}
        if not prose:
            fail += 1; continue
        new_text, _added = _rebuild(parsed, prose)
        p.write_text(new_text)
        ok += 1
        if i % 25 == 0 or i == len(needs):
            print(f"  [{i}/{len(needs)}] ok={ok} fail={fail}")
    print(f"\nDone. Updated: {ok}   Failed: {fail}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Templates Pass 1 — architecture normalization")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sample", metavar="LEAF_ID")
    g.add_argument("--bulk", action="store_true")
    ap.add_argument("--with-llm", action="store_true",
                    help="Call the LLM in --sample mode (default: placeholders)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    if args.sample:
        cmd_sample(args.sample, args.with_llm)
    elif args.bulk:
        cmd_bulk(args.dry_run, args.yes)


if __name__ == "__main__":
    main()
