"""
LLM-driven per-MUST guidance generator.

Shipped in Ship 56'.b (2026-08-05). Walks the catalog, sends each
ChecklistItem's context to `gpt-4o-mini` via the shared `rag.llm_client`
plumbing, and writes one YAML file per must_id under
`enrichment/guidance/{control_ref}/{slug}.yaml`.

Modes:

    # print the prompt for one or more MUSTs — no LLM call
    python3 -m enrichment.guidance.generate_from_catalog \\
        --sample-print item:5.2:owner,item:A.5.15:least_privilege

    # generate for specific MUSTs (calls LLM, prints YAML output, no file write)
    python3 -m enrichment.guidance.generate_from_catalog \\
        --sample item:5.2:owner,item:A.5.15:least_privilege

    # generate for N random MUSTs (prints, no file write)
    python3 -m enrichment.guidance.generate_from_catalog --sample-random 5

    # bulk-generate for every uncovered MUST + write YAML files
    python3 -m enrichment.guidance.generate_from_catalog --bulk

    # dry-run bulk — cost + counts, no LLM call
    python3 -m enrichment.guidance.generate_from_catalog --bulk --dry-run
"""
from __future__ import annotations

import argparse
import datetime as _dt
import random
import sys
from pathlib import Path
from typing import Optional

import yaml


_DEFAULT_MODEL = "gpt-4o-mini"
_GUIDANCE_ROOT = Path(__file__).resolve().parent

# Module-level state — CLI overrides these
_MODEL = _DEFAULT_MODEL
_MODEL_HANDLE = "llm-4o-mini"       # authored_by field in emitted YAML


def _set_model(model: str) -> None:
    global _MODEL, _MODEL_HANDLE
    _MODEL = model
    # Compact handle for the YAML frontmatter's `authored_by` field
    handle_map = {
        "gpt-4o-mini": "llm-4o-mini",
        "gpt-4o":      "llm-4o",
        "gpt-4.1":     "llm-4.1",
        "gpt-4.1-mini":"llm-4.1-mini",
    }
    _MODEL_HANDLE = handle_map.get(model, f"llm-{model}")


_SYSTEM_PROMPT = """You are a compliance consultant helping a tenant capture evidence for a specific compliance requirement. You will produce 3-5 short, imperative best-practice steps that walk the tenant through what to do — grounded in what an auditor would look for.

Each step must:
- Start with an action verb. Pick the verb that fits — do not begin every step with the same one. Good choices: Name, Document, State, Confirm, Record, Cross-reference, Assign, Publish, Retain, Sign, Approve, Review.
- Use plain English — no jargon, no acronyms without context, no auditor-speak.
- Lead the tenant to a piece of EVIDENCE an auditor could look at (a named person, a dated record, a signed decision, a cross-reference in a register).
- Be specific enough that "done" is checkable — avoid vague verbs at the start (ensure, consider, review as needed).
- Fit in 15-25 words.
- End with a concrete outcome. DO NOT append filler phrases like "for accountability", "for compliance tracking", "for easy access", "for auditor verification", "in a clear and concise manner", "to demonstrate compliance". They add no auditor value.

Where appropriate, include ONE step that names a specific pitfall an auditor would flag (e.g. owner listed as "the team" or "IT"; verbal-only approval; undated policy version; boilerplate that could apply to any organisation). Frame it as a positive action: "Name the owner as a specific individual — not 'the team' or a department."

Return ONLY YAML with a single `guidance` key. No preamble, no code fences, no explanation.

Formatting rules for the YAML output (STRICT — otherwise YAML parsing fails):
- Each step on its own line, prefixed with "- "
- Do NOT include an unquoted colon inside a step. If a step needs a colon (e.g. listing categories), wrap the entire step in double quotes.
- Do NOT include leading whitespace before "- ".
- Escape any double quote inside a quoted step with a backslash."""


def _user_prompt(*, standard_id: str, control_ref: str, leaf_title: str,
                 must_text: str, rationale: str, category: str) -> str:
    return (
        f"Standard: {standard_id}  (control {control_ref})\n"
        f"Artefact: {leaf_title}\n"
        f"Requirement ({category}): {must_text}\n"
        f"Rationale: {rationale}\n\n"
        f"Produce 3-5 imperative best-practice steps for this specific requirement."
    )


def _walk_catalog():
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    for er in ALL_EVIDENCE_REQUIREMENTS:
        yield er
    for ds in ALL_DERIVED_SPECS:
        for er in ds.direct_evidence:
            yield er


def _find_item(must_id: str) -> Optional[tuple]:
    """Locate a ChecklistItem by must_id + return (er, ci, category)."""
    for er in _walk_catalog():
        for ci in er.must_contain:
            if ci.id == must_id:
                return er, ci, "must"
        for ci in er.should_contain:
            if ci.id == must_id:
                return er, ci, "should"
    return None


def _output_path(must_id: str) -> Path:
    """Compute the YAML output path for a must_id.

    item:5.2:owner       -> enrichment/guidance/5.2/owner.yaml
    item:A.5.15:least_privilege -> enrichment/guidance/A.5.15/least_privilege.yaml
    item:Art.30:purposes -> enrichment/guidance/Art.30/purposes.yaml
    """
    parts = must_id.split(":")
    if len(parts) != 3 or parts[0] != "item":
        raise ValueError(f"Unexpected must_id shape: {must_id}")
    _, control_ref, slug = parts
    return _GUIDANCE_ROOT / control_ref / f"{slug}.yaml"


def _parse_yaml_guidance(text: str) -> Optional[list[str]]:
    """Parse an LLM guidance response. Returns the guidance list or None.

    Two-pass:
    1. Try yaml.safe_load (the happy path).
    2. On failure, fall back to line-based extraction — grab lines starting
       with "- " (with any leading spaces). This is robust against the
       most common LLM syntax hazard: unquoted `: ` inside a step value
       (which YAML would parse as a nested key-value pair).
    """
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines)

    # Pass 1: YAML parse
    try:
        data = yaml.safe_load(t)
        if isinstance(data, dict):
            g = data.get("guidance")
            if isinstance(g, list) and all(isinstance(x, str) for x in g) and g:
                return [x.strip() for x in g if x.strip()]
    except yaml.YAMLError:
        pass

    # Pass 2: line-based fallback — grab every "- ..." line
    import re
    steps: list[str] = []
    for line in t.splitlines():
        m = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if m:
            step = m.group(1)
            # Strip surrounding quotes if the LLM did wrap
            if len(step) >= 2 and step[0] == step[-1] and step[0] in ('"', "'"):
                step = step[1:-1]
            steps.append(step)
    return steps if steps else None


def _emit_yaml(must_id: str, er, ci, category: str, guidance: list[str]) -> str:
    """Render the YAML file body for a MUST."""
    payload = {
        "must_id":         must_id,
        "control_ref":     er.control_ref,
        "standard_id":     er.standard_id,
        "must_text":       ci.text,
        "category":        category,
        "curation_status": "draft",
        "authored_by":     _MODEL_HANDLE,
        "authored_at":     _dt.date.today().isoformat(),
        "guidance":        guidance,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=100)


def _print_prompt(must_id: str, verbose: bool = True) -> Optional[tuple]:
    found = _find_item(must_id)
    if not found:
        print(f"  !! {must_id} — not in catalog", file=sys.stderr)
        return None
    er, ci, category = found
    user = _user_prompt(
        standard_id = er.standard_id,
        control_ref = er.control_ref,
        leaf_title  = er.title,
        must_text   = ci.text,
        rationale   = ci.rationale,
        category    = category,
    )
    if verbose:
        print("=" * 78)
        print(f"MUST_ID: {must_id}")
        print("─" * 78)
        print("--- SYSTEM ---")
        print(_SYSTEM_PROMPT)
        print()
        print("--- USER ---")
        print(user)
        print()
    return er, ci, category, user


def _call_llm(must_id: str, er, ci, category, user_prompt: str) -> Optional[list[str]]:
    from rag.llm_client import call as llm_call
    resp = llm_call(
        system      = _SYSTEM_PROMPT,
        user        = user_prompt,
        model       = _MODEL,
        purpose     = "guidance_gen",
        max_tokens  = 500,
        temperature = 0.1,
        timeout_s   = 30.0,
    )
    if resp.error:
        print(f"  ⚠ {must_id} LLM error: {resp.error}: {resp.text}", file=sys.stderr)
        return None
    guidance = _parse_yaml_guidance(resp.text or "")
    if guidance is None:
        print(f"  ⚠ {must_id} unparseable output — raw:", file=sys.stderr)
        print("---BEGIN RAW---", file=sys.stderr)
        print(resp.text[:800], file=sys.stderr)
        print("---END RAW---", file=sys.stderr)
        return None
    return guidance


def cmd_sample_print(must_ids: list[str]):
    for mid in must_ids:
        _print_prompt(mid, verbose=True)


def cmd_sample_generate(must_ids: list[str]):
    for mid in must_ids:
        r = _print_prompt(mid, verbose=True)
        if not r:
            continue
        er, ci, category, user = r
        guidance = _call_llm(mid, er, ci, category, user)
        if not guidance:
            continue
        print("--- LLM OUTPUT ---")
        for g in guidance:
            print(f"  · {g}")
        print()
        print("--- WOULD-WRITE YAML ---")
        print(_emit_yaml(mid, er, ci, category, guidance))


def cmd_sample_random(n: int):
    all_ids: list[str] = []
    for er in _walk_catalog():
        for ci in er.must_contain:
            all_ids.append(ci.id)
        for ci in er.should_contain:
            all_ids.append(ci.id)
    random.shuffle(all_ids)
    cmd_sample_generate(all_ids[:n])


def cmd_bulk(dry_run: bool, skip_confirm: bool = False):
    all_targets: list[tuple[str, object, object, str]] = []
    for er in _walk_catalog():
        for ci in er.must_contain:
            all_targets.append((ci.id, er, ci, "must"))
        for ci in er.should_contain:
            all_targets.append((ci.id, er, ci, "should"))

    total = len(all_targets)
    # Skip already-authored
    remaining: list[tuple[str, object, object, str]] = []
    for mid, er, ci, cat in all_targets:
        if _output_path(mid).exists():
            continue
        remaining.append((mid, er, ci, cat))

    print(f"Total MUSTs in catalog:   {total}")
    print(f"Already authored (skip):  {total - len(remaining)}")
    print(f"To generate:              {len(remaining)}")
    est_cost_usd = len(remaining) * 0.0002 * 3  # ballpark: ~600 tokens per call at $0.0002 per 1k
    print(f"Est. cost (rough):        ${est_cost_usd:.2f}  ({_MODEL})")
    if dry_run:
        print("(dry-run — no LLM calls)")
        return

    if not skip_confirm:
        print()
        print("Confirm bulk generation? Type 'yes' to proceed:")
        answer = input().strip().lower()
        if answer != "yes":
            print("Aborted.")
            return

    ok = 0
    fail = 0
    for i, (mid, er, ci, cat) in enumerate(remaining, 1):
        user = _user_prompt(
            standard_id = er.standard_id,
            control_ref = er.control_ref,
            leaf_title  = er.title,
            must_text   = ci.text,
            rationale   = ci.rationale,
            category    = cat,
        )
        guidance = _call_llm(mid, er, ci, cat, user)
        if not guidance:
            fail += 1
            continue
        path = _output_path(mid)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_emit_yaml(mid, er, ci, cat, guidance))
        ok += 1
        if i % 25 == 0 or i == len(remaining):
            print(f"  [{i}/{len(remaining)}] ok={ok} fail={fail}")

    print(f"\nDone. Written: {ok}   Failed: {fail}")


def main():
    parser = argparse.ArgumentParser(description="LLM-driven per-MUST guidance generator")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--sample-print", metavar="MUST_IDS",
                     help="Comma-separated must_ids — print prompt only, no LLM call")
    grp.add_argument("--sample", metavar="MUST_IDS",
                     help="Comma-separated must_ids — print prompt + LLM output (no file write)")
    grp.add_argument("--sample-random", type=int, metavar="N",
                     help="N random MUSTs — print prompt + LLM output (no file write)")
    grp.add_argument("--bulk", action="store_true",
                     help="Generate for every uncovered MUST + write YAML files")
    parser.add_argument("--dry-run", action="store_true",
                        help="With --bulk, report counts + cost without LLM calls")
    parser.add_argument("--model", default=_DEFAULT_MODEL,
                        help=f"Model name (default {_DEFAULT_MODEL}); try gpt-4o for quality lift")
    parser.add_argument("--yes", action="store_true",
                        help="Skip interactive confirmation on --bulk (for background runs)")
    args = parser.parse_args()
    _set_model(args.model)

    if args.sample_print:
        cmd_sample_print(args.sample_print.split(","))
    elif args.sample:
        cmd_sample_generate(args.sample.split(","))
    elif args.sample_random is not None:
        cmd_sample_random(args.sample_random)
    elif args.bulk:
        cmd_bulk(dry_run=args.dry_run, skip_confirm=args.yes)


if __name__ == "__main__":
    main()
