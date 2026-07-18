"""
Tier 2 Enrichment Generator

Generates business_description and query_keywords for the 259 GDPR nodes
that have obligation_text but no Tier 1 hand-authored enrichment.

Uses gpt-4o-mini — fast, cheap (~$0.013 for full run).

Usage:
    # Sample mode — generate 10 representative nodes for review
    python3 enrichment/tier2_generator.py --sample

    # Full run — generate all remaining nodes
    python3 enrichment/tier2_generator.py --run

    # Resume — skip nodes already in the output file
    python3 enrichment/tier2_generator.py --run --resume

Output:
    enrichment/tier2_generated.json — one entry per node, keyed by ref

The output file is reviewed before being applied to the index.
Apply with: python3 enrichment/tier2_apply.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.requirement_node import RequirementNode
from enrichment.applier       import Tier1EnrichmentApplier


# ── Prompt ────────────────────────────────────────────────────────────────────

GENERATION_PROMPT = """You are enriching a compliance knowledge base used by DPOs, \
compliance managers, and legal counsel.

Article:  {ref} — {title}
Chapter:  {chapter}
Standard: {standard}
{parent_line}
Legal text:
{obligation_text}

Write enrichment for this article. Return JSON only — no preamble, no markdown fences.

Rules for business_description (80-120 words):
- Plain English — explain what this means for a controller or processor in practice
- Say when it is triggered and what it actually requires organisations to do
- Note common misconceptions only if genuinely present in practice
- Do NOT add obligations not in the text above
- Do NOT recommend specific technologies
- Do NOT repeat the legal text verbatim — paraphrase it
- Write as a knowledgeable compliance advisor speaking to a practitioner

Rules for query_keywords:
- exact:        2-5 terms appearing verbatim in the legal text
- practitioner: 4-8 terms DPOs/lawyers actually use for this concept
- scenario:     3-5 real-world situations that trigger this obligation
- confusion:    1-3 adjacent concepts practitioners confuse with this one
                (leave empty list [] if no genuine confusion risk)

{{
  "business_description": "...",
  "query_keywords": {{
    "exact": [...],
    "practitioner": [...],
    "scenario": [...],
    "confusion": [...]
  }}
}}"""


# ── Representative sample selection ───────────────────────────────────────────

SAMPLE_REFS = [
    # General provisions — scope and definitions
    "Art.2",      # Material scope
    "Art.4",      # Definitions (article level)
    "Art.4.1",    # Definition: personal data

    # Rights of data subjects — most queried cluster after Ch.4
    "Art.12",     # Transparent information
    "Art.13",     # Information to be provided
    "Art.17",     # Right to erasure
    "Art.17.1",   # Erasure — paragraph 1
    "Art.20",     # Right to data portability
    "Art.22",     # Automated decision-making

    # Supervisory authorities / enforcement
    "Art.58",     # Powers of supervisory authority
    "Art.83",     # General conditions for fines
    "Art.83.4",   # Lower fine tier
    "Art.83.5",   # Higher fine tier

    # International transfers
    "Art.44",     # General principle for transfers
    "Art.46",     # Transfers subject to safeguards
]


# ── Tier 2 Generator ──────────────────────────────────────────────────────────

class Tier2Generator:

    def __init__(
        self,
        output_path:    str  = "enrichment/tier2_generated.json",
        # Default sourced from rag.llm_models (Ship 5'.d).
        model:          str  = None,
        temperature:    float = 0.2,
        batch_size:     int  = 10,
        delay_between:  float = 0.3,   # seconds between API calls
    ):
        if model is None:
            from rag.llm_models import MODEL_ENRICHMENT_T2
            model = MODEL_ENRICHMENT_T2
        self.output_path   = Path(output_path)
        self.model         = model
        self.temperature   = temperature
        self.batch_size    = batch_size
        self.delay         = delay_between

        # Load existing output for resume support
        self._existing: dict[str, dict] = {}
        if self.output_path.exists():
            with open(self.output_path) as f:
                self._existing = json.load(f)

    # ── Public API ─────────────────────────────────────────────────────────

    def load_nodes(self) -> tuple[list[RequirementNode], dict[str, str]]:
        """
        Load all nodes, apply Tier 1, return nodes needing Tier 2.
        Returns (nodes_to_enrich, parent_title_map).
        """
        here = Path(__file__).parent.parent
        iso_path  = here.parent / "output" / "iso_phase1" / "iso_nodes_phase1.json"
        gdpr_path = here.parent / "output" / "gdpr_phase2" / "gdpr_nodes_phase2.json"

        # Try relative path if absolute not found
        if not iso_path.exists():
            iso_path  = Path("iso_nodes_phase1.json")
            gdpr_path = Path("gdpr_nodes_phase2.json")

        with open(iso_path) as f:
            iso_nodes = [RequirementNode.from_dict(d) for d in json.load(f)]
        with open(gdpr_path) as f:
            gdpr_nodes = [RequirementNode.from_dict(d) for d in json.load(f)]

        all_nodes = iso_nodes + gdpr_nodes

        # Apply Tier 1 enrichment
        applier = Tier1EnrichmentApplier()
        applier.load()
        applier.apply(all_nodes)

        # Build parent title map (ref → title)
        parent_map = {n.ref: n.title for n in all_nodes}

        # Nodes needing Tier 2: has obligation_text, no business_description
        tier2 = [
            n for n in all_nodes
            if not n.business_description
            and n.obligation_text.strip()
        ]

        return tier2, parent_map

    def run_sample(self, refs: list[str] | None = None) -> dict[str, dict]:
        """
        Generate enrichment for a representative sample.
        Returns dict of {ref: enrichment} for review.
        """
        nodes, parent_map = self.load_nodes()
        node_map = {n.ref: n for n in nodes}

        sample_refs = refs or SAMPLE_REFS
        sample_nodes = [
            node_map[ref] for ref in sample_refs
            if ref in node_map
        ]

        missing = [r for r in sample_refs if r not in node_map]
        if missing:
            print(f"  ⚠ Refs not in Tier 2 pool (already Tier 1 or missing): "
                  f"{missing}")

        print(f"Generating sample: {len(sample_nodes)} nodes")
        print(f"Model: {self.model}")
        print()

        results = {}
        for i, node in enumerate(sample_nodes, 1):
            print(f"  [{i:2d}/{len(sample_nodes)}] {node.ref:20s} "
                  f"{node.title[:40]}", end=" ... ", flush=True)
            t0 = time.time()

            enrichment = self._generate_one(node, parent_map)
            elapsed    = round((time.time() - t0) * 1000)

            if enrichment:
                results[node.ref] = enrichment
                biz_words = len(enrichment["business_description"].split())
                kw_count  = sum(
                    len(v) for v in enrichment["query_keywords"].values()
                )
                print(f"✓ {biz_words}w, {kw_count}kw ({elapsed}ms)")
            else:
                print(f"✗ FAILED")

            if i < len(sample_nodes):
                time.sleep(self.delay)

        return results

    def run_full(self, resume: bool = True) -> dict[str, dict]:
        """
        Generate enrichment for all Tier 2 nodes.
        Saves incrementally — safe to interrupt and resume.
        """
        nodes, parent_map = self.load_nodes()

        if resume and self._existing:
            nodes = [n for n in nodes if n.ref not in self._existing]
            print(f"Resuming — {len(self._existing)} already done, "
                  f"{len(nodes)} remaining")
        else:
            print(f"Full run — {len(nodes)} nodes to enrich")

        print(f"Model: {self.model}  Est. cost: ~${len(nodes) * 0.00005:.3f}")
        print()

        results = dict(self._existing)
        failed  = []

        for i, node in enumerate(nodes, 1):
            print(f"  [{i:3d}/{len(nodes)}] {node.ref:20s} "
                  f"{node.title[:35]}", end=" ... ", flush=True)
            t0 = time.time()

            enrichment = self._generate_one(node, parent_map)
            elapsed    = round((time.time() - t0) * 1000)

            if enrichment:
                results[node.ref] = enrichment
                biz_words = len(enrichment["business_description"].split())
                print(f"✓ {biz_words}w ({elapsed}ms)")
            else:
                failed.append(node.ref)
                print(f"✗ FAILED")

            # Save incrementally every 10 nodes
            if i % 10 == 0:
                self._save(results)
                print(f"    [saved {len(results)} entries]")

            if i < len(nodes):
                time.sleep(self.delay)

        # Final save
        self._save(results)

        print(f"\n{'─'*50}")
        print(f"Done: {len(results)} enriched, {len(failed)} failed")
        if failed:
            print(f"Failed: {failed}")

        return results

    # ── Core generation ────────────────────────────────────────────────────

    def _generate_one(
        self,
        node:       RequirementNode,
        parent_map: dict[str, str],
    ) -> dict | None:
        """Generate enrichment for a single node. Returns None on failure."""
        prompt = self._build_prompt(node, parent_map)

        # Ship 5'.c: migrated from direct OpenAI SDK to the central
        # llm_client.call — auto-logs to ai_call_log, provider-neutral
        # wire routing, structured error return. See
        # [[ship-5-prime-a-llm-audit-2026-07-18]] finding 1.
        try:
            from rag.llm_client import call as llm_call

            response = llm_call(
                system      = "",
                user        = prompt,
                model       = self.model,
                purpose     = "enrichment_tier2",
                max_tokens  = 600,
                temperature = self.temperature,
                metadata    = {"ref": node.ref, "attempt": 1},
            )
            if not response.ok:
                print(f"\n    Error: {response.error}", end="")
                return None
            raw    = response.text.strip()
            parsed = self._parse_json(raw)

            if parsed and self._validate(parsed, node.ref):
                return parsed

            # Retry once if parse failed
            print(f"\n    ⚠ Parse failed, retrying...", end="")
            time.sleep(1)
            response = llm_call(
                system      = "",
                user        = prompt,
                model       = self.model,
                purpose     = "enrichment_tier2",
                max_tokens  = 600,
                temperature = 0.0,   # deterministic on retry
                metadata    = {"ref": node.ref, "attempt": 2},
            )
            if not response.ok:
                print(f"\n    Error on retry: {response.error}", end="")
                return None
            raw    = response.text.strip()
            parsed = self._parse_json(raw)
            if parsed and self._validate(parsed, node.ref):
                return parsed

        except Exception as e:
            print(f"\n    Error: {e}", end="")

        return None

    def _build_prompt(
        self,
        node:       RequirementNode,
        parent_map: dict[str, str],
    ) -> str:
        """Build the generation prompt for a node."""
        parent_line = ""
        if node.parent_ref and node.parent_ref in parent_map:
            parent_title = parent_map[node.parent_ref]
            parent_line  = f"Parent:  {node.parent_ref} — {parent_title}\n"

        # Truncate obligation text if very long
        obligation = node.obligation_text[:1200]
        if len(node.obligation_text) > 1200:
            obligation += "..."

        standard = "GDPR 2016/679" if node.is_gdpr else "ISO 27001:2022"

        return GENERATION_PROMPT.format(
            ref            = node.ref,
            title          = node.title,
            chapter        = node.chapter or "General",
            standard       = standard,
            parent_line    = parent_line,
            obligation_text = obligation,
        )

    # ── Validation ─────────────────────────────────────────────────────────

    def _validate(self, parsed: dict, ref: str) -> bool:
        """Basic quality checks on generated enrichment."""
        biz = parsed.get("business_description", "")
        kw  = parsed.get("query_keywords", {})

        checks = {
            "has_description":   len(biz) > 50,
            "reasonable_length": 40 < len(biz.split()) < 250,
            "has_exact":         len(kw.get("exact", [])) >= 1,
            "has_practitioner":  len(kw.get("practitioner", [])) >= 2,
            "has_scenario":      len(kw.get("scenario", [])) >= 1,
        }

        return all(checks.values())

    # ── Helpers ────────────────────────────────────────────────────────────

    def _save(self, results: dict) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def _parse_json(self, raw: str) -> dict | None:
        import re
        clean = re.sub(r'```(?:json)?\s*', '', raw).strip().rstrip('`').strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return None


# ── Pretty printer for sample review ─────────────────────────────────────────

def print_sample_review(results: dict[str, dict]) -> None:
    """Print generated enrichment for human review."""
    print()
    print("=" * 70)
    print("  TIER 2 SAMPLE — REVIEW BEFORE FULL RUN")
    print("=" * 70)

    for ref, enrichment in results.items():
        biz = enrichment.get("business_description", "")
        kw  = enrichment.get("query_keywords", {})

        print(f"\n{'─'*70}")
        print(f"  {ref}")
        print(f"{'─'*70}")
        print(f"\nBusiness description ({len(biz.split())} words):")

        # Word-wrap the description
        import textwrap
        for line in textwrap.wrap(biz, width=68):
            print(f"  {line}")

        print(f"\nKeywords:")
        for category, terms in kw.items():
            if terms:
                print(f"  {category:12s}: {', '.join(str(t) for t in terms[:6])}")

    print(f"\n{'=' * 70}")
    print(f"  {len(results)} nodes sampled")
    print(f"  Review quality above. If satisfied, run:")
    print(f"    python3 enrichment/tier2_generator.py --run")
    print(f"  Then rebuild the index:")
    print(f"    python3 vector/build_index.py --chroma-host localhost ...")
    print(f"{'=' * 70}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Tier 2 enrichment generator for ArionComply"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--sample",
        action="store_true",
        help="Generate representative sample for review",
    )
    group.add_argument(
        "--run",
        action="store_true",
        help="Generate enrichment for all remaining nodes",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Resume from existing output (default: True)",
    )
    parser.add_argument(
        "--refs",
        nargs="+",
        help="Specific refs to sample (overrides default sample list)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="LLM model to use (default: rag.llm_models.MODEL_ENRICHMENT_T2)",
    )
    parser.add_argument(
        "--output",
        default="enrichment/tier2_generated.json",
        help="Output JSON file path",
    )
    args = parser.parse_args()

    generator = Tier2Generator(
        output_path = args.output,
        model       = args.model,
    )

    if args.sample:
        results = generator.run_sample(refs=args.refs)
        print_sample_review(results)

        # Save sample to output for inspection
        sample_path = Path(args.output).with_suffix(".sample.json")
        with open(sample_path, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSample saved to: {sample_path}")

    elif args.run:
        results = generator.run_full(resume=args.resume)
        print(f"\nOutput: {args.output}")
        print("Next step: python3 enrichment/tier2_apply.py")


if __name__ == "__main__":
    main()
