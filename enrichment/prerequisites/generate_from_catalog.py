"""
LLM-driven per-leaf prerequisites generator.

Ship 57' (2026-08-07). Mirrors the Ship 56' guidance generator
(enrichment/guidance/generate_from_catalog.py). Walks the catalog,
sends per-leaf context to gpt-4.1, writes one YAML per leaf under
enrichment/prerequisites/{control_ref}/{evidence_type_slug}.yaml.

Context inputs per leaf:
- Target leaf metadata (control_ref, standard_id, evidence_type, title, description)
- Framework role of the leaf: PROGRAM (ISO27001) | EXTENSION (ISO27701) | OBLIGATION (GDPR)
- Existing Neo4j PREREQUISITE_OF edges INBOUND to the leaf's control (with rationale)
- Existing template "Before you start" prose if a template exists
- Framework-role-appropriate foundational prereq HINTS

Modes:
    # print prompt only for one MUST — no LLM call
    python3 -m enrichment.prerequisites.generate_from_catalog \\
        --sample-print req:A.5.15:access_control_policy

    # generate for a comma-separated list (LLM call, no file write)
    python3 -m enrichment.prerequisites.generate_from_catalog \\
        --sample req:A.5.15:access_control_policy,req:A.7.2.7:consent_capture

    # bulk (writes YAMLs, skips already-authored)
    python3 -m enrichment.prerequisites.generate_from_catalog --bulk --yes
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path
from typing import Optional

import yaml


_DEFAULT_MODEL = "gpt-4.1"
_GUIDANCE_ROOT = Path(__file__).resolve().parent
_TEMPLATES_ROOT = Path(__file__).resolve().parent.parent.parent / "db" / "templates"

_MODEL = _DEFAULT_MODEL
_MODEL_HANDLE = "llm-4.1"


def _set_model(model: str) -> None:
    global _MODEL, _MODEL_HANDLE
    _MODEL = model
    handles = {
        "gpt-4o-mini": "llm-4o-mini",
        "gpt-4o":      "llm-4o",
        "gpt-4.1":     "llm-4.1",
        "gpt-4.1-mini":"llm-4.1-mini",
    }
    _MODEL_HANDLE = handles.get(model, f"llm-{model}")


# ── Framework role helpers ────────────────────────────────────────────────
def _framework_role(standard_id: str) -> str:
    if standard_id == "ISO27001:2022": return "PROGRAM"
    if standard_id == "ISO27701:2019": return "EXTENSION"
    if standard_id == "GDPR:2016/679": return "OBLIGATION"
    return "UNKNOWN"


# Cross-cutting foundational hints the LLM should consider per role.
# Not exhaustive — a starting list to prime candidate prereqs.
_FOUNDATIONAL_HINTS_PROGRAM = [
    ("4.3",    "ISO27001:2022", "ISMS Scope Statement"),
    ("5.2",    "ISO27001:2022", "Information Security Policy"),
    ("6.1.2",  "ISO27001:2022", "Risk Assessment"),
    ("A.5.9",  "ISO27001:2022", "Asset Register"),
    ("A.5.12", "ISO27001:2022", "Classification Scheme"),
    ("A.5.2",  "ISO27001:2022", "Roles & Responsibilities"),
    ("A.5.3",  "ISO27001:2022", "Segregation of Duties"),
]
_FOUNDATIONAL_HINTS_EXTENSION = _FOUNDATIONAL_HINTS_PROGRAM + [
    ("A.7.2.1", "ISO27701:2019", "Identify and Document Purpose"),
    ("A.7.2.2", "ISO27701:2019", "Identify Lawful Basis"),
]
_FOUNDATIONAL_HINTS_OBLIGATION = [
    ("Art.30", "GDPR:2016/679", "Records of Processing Activities"),
    ("Art.6",  "GDPR:2016/679", "Lawful Basis"),
    ("Art.37", "GDPR:2016/679", "DPO Designation"),
    ("4.3",    "ISO27001:2022", "ISMS Scope Statement"),  # if a Program is in place
]


def _foundational_hints_for(role: str) -> list[tuple[str, str, str]]:
    if role == "PROGRAM":     return _FOUNDATIONAL_HINTS_PROGRAM
    if role == "EXTENSION":   return _FOUNDATIONAL_HINTS_EXTENSION
    if role == "OBLIGATION":  return _FOUNDATIONAL_HINTS_OBLIGATION
    return []


# ── Neo4j edge seed ───────────────────────────────────────────────────────
_NEO_DRIVER = None
def _neo():
    global _NEO_DRIVER
    if _NEO_DRIVER is None:
        from neo4j import GraphDatabase
        _NEO_DRIVER = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"),
                  os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")),
        )
    return _NEO_DRIVER


def _existing_prereqs_from_graph(control_ref: str) -> list[dict]:
    """Fetch INBOUND PREREQUISITE_OF edges to the control (i.e. controls
    that ARE prereqs of the target). Includes rationale text."""
    with _neo().session() as s:
        rows = s.run("""
            MATCH (prereq:RequirementNode)-[r:PREREQUISITE_OF]->(target:RequirementNode)
            WHERE target.ref = $ref
            RETURN prereq.ref AS ref,
                   prereq.standard_id AS standard_id,
                   coalesce(prereq.title, prereq.ref) AS title,
                   r.rationale AS rationale
            ORDER BY prereq.ref
        """, ref=control_ref).data()
    return rows


# ── Template Before-you-start prose seed ──────────────────────────────────
def _find_template_path(leaf_id: str) -> Optional[Path]:
    """leaf_id = req:CTRL:SLUG → db/templates/req__CTRL__SLUG.md (colons/dots → underscores)"""
    slug = leaf_id.replace(":", "__").replace(".", "_")
    p = _TEMPLATES_ROOT / f"{slug}.md"
    return p if p.exists() else None


def _template_before_you_start(leaf_id: str) -> str:
    p = _find_template_path(leaf_id)
    if not p:
        return ""
    text = p.read_text()
    # Extract the "## Before you start" section (up to next H2)
    m = re.search(r"^## Before you start\s*\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


# ── Prompt ────────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a compliance consultant identifying prerequisites for a specific compliance artefact. You will produce a structured YAML list of PREREQUISITES — the artefacts that must exist BEFORE the target leaf can be meaningfully drafted.

VOCABULARY:
- PROGRAM = ISO 27001 (the operational compliance program a tenant runs)
- EXTENSION = ISO 27701 (privacy extension to a program)
- OBLIGATION = GDPR (regulatory obligation demonstrated by the program)

Every prerequisite has:
- ref: the control_ref or article number (e.g. "4.3", "A.5.9", "Art.30")
- standard_id: one of "ISO27001:2022" | "ISO27701:2019" | "GDPR:2016/679"
- title: display title
- category: exactly one of
    * "foundational" — cross-cutting baseline (scope, roles, RoPA, etc.)
    * "direct" — specific upstream artefact in the SAME framework role as the target
    * "cross_role" — prereq lives in a DIFFERENT framework role than the target (e.g. Extension leaf's Program base clause; Obligation article as legal yardstick)
- rationale: 1-3 sentences explaining WHY this prereq matters for the SPECIFIC target artefact. Tenant-facing, plain English.
- good_enough: 1-2 sentences on what "done enough" means — the pragmatic threshold to unblock the current task (not full compliance).

Emit 3-6 prerequisites per target. Prioritise the ones that would BLOCK a tenant from drafting the current artefact if missing. Skip vanity prereqs. If the target is itself foundational (like 4.3 ISMS Scope), it may have very few or zero prereqs — return an empty list is acceptable.

Return ONLY YAML with a single `prerequisites` key. No preamble, no code fences, no explanation. Formatting: if a step needs a colon, wrap the entire scalar in double quotes to keep YAML happy."""


def _user_prompt(er, role: str, foundational_hints: list[tuple], graph_prereqs: list[dict], template_bys: str) -> str:
    parts = [
        f"TARGET LEAF:",
        f"  leaf_id: {er.id}",
        f"  control_ref: {er.control_ref}",
        f"  standard_id: {er.standard_id}  (role: {role})",
        f"  evidence_type: {er.evidence_type}",
        f"  title: {er.title}",
        f"  description: {er.description}",
        "",
        "FOUNDATIONAL HINTS for this framework role (candidate prereqs — decide which apply):",
    ]
    for ref, std, title in foundational_hints:
        if ref == er.control_ref: continue  # don't self-prereq
        parts.append(f"  - {ref} ({std}) — {title}")
    if graph_prereqs:
        parts.append("")
        parts.append("EXISTING CURATOR-VETTED PREREQ EDGES (from the knowledge graph — validate + use rationale as a starting point):")
        for gp in graph_prereqs:
            rat = (gp.get("rationale") or "").strip()
            parts.append(f"  - {gp['ref']} ({gp['standard_id']}) — {gp['title']}")
            if rat:
                parts.append(f"      graph rationale: {rat}")
    if template_bys:
        parts.append("")
        parts.append("EXISTING TEMPLATE 'Before you start' PROSE (curator's tenant-facing intuition — validate + structure):")
        parts.append("  ---")
        for line in template_bys.splitlines()[:20]:  # cap size
            parts.append(f"  {line}")
        parts.append("  ---")
    parts.append("")
    parts.append("Produce the prerequisites YAML now.")
    return "\n".join(parts)


# ── Parser (with line-based fallback for colon edge case) ────────────────
def _parse_yaml_prereqs(text: str) -> Optional[list[dict]]:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines and lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].startswith("```"): lines = lines[:-1]
        t = "\n".join(lines)
    try:
        data = yaml.safe_load(t)
        if isinstance(data, dict):
            p = data.get("prerequisites")
            if isinstance(p, list):
                return p
    except yaml.YAMLError:
        pass
    return None


def _emit_yaml(er, role: str, prereqs: list[dict]) -> str:
    payload = {
        "leaf_id":         er.id,
        "control_ref":     er.control_ref,
        "standard_id":     er.standard_id,
        "curation_status": "draft",
        "authored_by":     _MODEL_HANDLE,
        "authored_at":     _dt.date.today().isoformat(),
        "prerequisites":   prereqs,
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True,
                          default_flow_style=False, width=100)


def _output_path(er) -> Path:
    slug = er.id.split(":", 2)[-1]  # everything after "req:CTRL:"
    return _GUIDANCE_ROOT / er.control_ref / f"{slug}.yaml"


# ── LLM call ──────────────────────────────────────────────────────────────
def _call_llm(er, prompt: str) -> Optional[list[dict]]:
    from rag.llm_client import call as llm_call
    resp = llm_call(
        system=_SYSTEM_PROMPT,
        user=prompt,
        model=_MODEL,
        purpose="guidance_gen",   # reuse — CHECK constraint already allows it
        max_tokens=1500,
        temperature=0.2,
        timeout_s=45.0,
    )
    if resp.error:
        print(f"  ⚠ {er.id} LLM error: {resp.error}", file=sys.stderr)
        return None
    parsed = _parse_yaml_prereqs(resp.text or "")
    if parsed is None:
        print(f"  ⚠ {er.id} unparseable output — raw:", file=sys.stderr)
        print(resp.text[:600], file=sys.stderr)
        return None
    return parsed


# ── Commands ──────────────────────────────────────────────────────────────
def _find_leaf(leaf_id: str):
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    for er in ALL_EVIDENCE_REQUIREMENTS:
        if er.id == leaf_id:
            return er
    for ds in ALL_DERIVED_SPECS:
        for er in ds.direct_evidence:
            if er.id == leaf_id:
                return er
    return None


def _print_context(er):
    role = _framework_role(er.standard_id)
    hints = _foundational_hints_for(role)
    graph_prereqs = _existing_prereqs_from_graph(er.control_ref)
    template_bys = _template_before_you_start(er.id)
    prompt = _user_prompt(er, role, hints, graph_prereqs, template_bys)

    print("=" * 78)
    print(f"LEAF: {er.id}  (role: {role})")
    print("─" * 78)
    print("--- USER PROMPT ---")
    print(prompt)
    print()
    return prompt


def cmd_sample_print(leaf_ids: list[str]):
    for lid in leaf_ids:
        er = _find_leaf(lid)
        if not er:
            print(f"!! {lid} not in catalog", file=sys.stderr); continue
        _print_context(er)


def cmd_sample_generate(leaf_ids: list[str]):
    for lid in leaf_ids:
        er = _find_leaf(lid)
        if not er:
            print(f"!! {lid} not in catalog", file=sys.stderr); continue
        prompt = _print_context(er)
        prereqs = _call_llm(er, prompt)
        if not prereqs:
            continue
        print(f"--- LLM RETURNED {len(prereqs)} PREREQ(S) ---")
        for p in prereqs:
            print(f"  · {p.get('ref')} ({p.get('standard_id')}) [{p.get('category')}] {p.get('title')}")
            print(f"      rationale: {(p.get('rationale') or '').strip()}")
            ge = (p.get('good_enough') or '').strip()
            if ge:
                print(f"      good_enough: {ge}")
        print()
        print("--- WOULD-WRITE YAML ---")
        print(_emit_yaml(er, _framework_role(er.standard_id), prereqs))


def cmd_bulk(dry_run: bool, skip_confirm: bool = False):
    from enrichment.documents.document_requirements import (
        ALL_EVIDENCE_REQUIREMENTS, ALL_DERIVED_SPECS,
    )
    all_targets = list(ALL_EVIDENCE_REQUIREMENTS) + [
        er for ds in ALL_DERIVED_SPECS for er in ds.direct_evidence
    ]
    remaining = [er for er in all_targets if not _output_path(er).exists()]
    print(f"Total leaves in catalog:  {len(all_targets)}")
    print(f"Already authored (skip):  {len(all_targets) - len(remaining)}")
    print(f"To generate:              {len(remaining)}")
    est = len(remaining) * 0.003
    print(f"Est. cost (rough):        ${est:.2f}  ({_MODEL})")
    if dry_run:
        print("(dry-run — no LLM calls)")
        return
    if not skip_confirm:
        print("\nConfirm bulk? Type 'yes' to proceed:")
        if input().strip().lower() != "yes":
            print("Aborted."); return

    ok = fail = 0
    for i, er in enumerate(remaining, 1):
        role = _framework_role(er.standard_id)
        hints = _foundational_hints_for(role)
        graph_prereqs = _existing_prereqs_from_graph(er.control_ref)
        template_bys = _template_before_you_start(er.id)
        prompt = _user_prompt(er, role, hints, graph_prereqs, template_bys)
        prereqs = _call_llm(er, prompt)
        if not prereqs:
            fail += 1; continue
        path = _output_path(er)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_emit_yaml(er, role, prereqs))
        ok += 1
        if i % 25 == 0 or i == len(remaining):
            print(f"  [{i}/{len(remaining)}] ok={ok} fail={fail}")
    print(f"\nDone. Written: {ok}   Failed: {fail}")


def main():
    parser = argparse.ArgumentParser(description="LLM-driven per-leaf prerequisites generator")
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--sample-print", metavar="LEAF_IDS")
    grp.add_argument("--sample", metavar="LEAF_IDS")
    grp.add_argument("--bulk", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--model", default=_DEFAULT_MODEL)
    args = parser.parse_args()
    _set_model(args.model)

    if args.sample_print:
        cmd_sample_print(args.sample_print.split(","))
    elif args.sample:
        cmd_sample_generate(args.sample.split(","))
    elif args.bulk:
        cmd_bulk(dry_run=args.dry_run, skip_confirm=args.yes)


if __name__ == "__main__":
    main()
