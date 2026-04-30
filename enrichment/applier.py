"""
Tier1EnrichmentApplier

Loads all Tier 1 enrichment files and applies business_description
and query_keywords to RequirementNodes before they are indexed
into ChromaDB.

Design:
  - Enrichment is additive — never overwrites an existing
    business_description if one is already set on the node
  - Applies to both GDPR and ISO nodes
  - Reports coverage and any refs in enrichment with no matching node

Usage:
    from enrichment.applier import Tier1EnrichmentApplier

    applier = Tier1EnrichmentApplier()
    applier.load()
    count = applier.apply(nodes)   # patches in-place
    print(applier.report())
"""

from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.requirement_node import RequirementNode


# ── Enrichment source files ────────────────────────────────────────────────────

ENRICHMENT_FILES = [
    ("tier1_gdpr_security",    "GDPR Security (Art.32)"),
    ("tier1_gdpr_breach",      "GDPR Breach (Art.33-34)"),
    ("tier1_gdpr_controller",  "GDPR Controller (Art.24,25,28,30)"),
    ("tier1_gdpr_principles",  "GDPR Principles + Consent + DPIA/DPO"),
    ("tier1_iso_controls",     "ISO 27001:2022 Controls"),
]


@dataclass
class ApplyReport:
    nodes_enriched:    int = 0
    nodes_skipped:     int = 0   # already had business_description
    refs_not_found:    list = None
    cluster_counts:    dict = None
    warnings:          list = None

    def __post_init__(self):
        self.refs_not_found = self.refs_not_found or []
        self.cluster_counts = self.cluster_counts or {}
        self.warnings       = self.warnings or []

    def summary(self) -> str:
        lines = [
            "Tier 1 Enrichment Apply Report",
            "─" * 40,
            f"Nodes enriched:     {self.nodes_enriched}",
            f"Nodes skipped:      {self.nodes_skipped} (already enriched)",
        ]
        if self.cluster_counts:
            lines.append("By cluster:")
            for cluster, count in self.cluster_counts.items():
                lines.append(f"  {count:3d}  {cluster}")
        if self.refs_not_found:
            lines.append(
                f"Refs not found:     {len(self.refs_not_found)} "
                f"({', '.join(self.refs_not_found[:5])})"
            )
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        return "\n".join(lines)


class Tier1EnrichmentApplier:
    """
    Loads all Tier 1 enrichment data and applies it to RequirementNodes.

    Enrichment data keyed by node ref (e.g. "Art.32.1.a", "A.8.24").
    Applied to nodes matched by ref, regardless of standard.
    """

    def __init__(self, enrichment_dir: str = None):
        self._dir = enrichment_dir or str(Path(__file__).parent)
        self._data: dict[str, dict] = {}   # ref → {business_description, query_keywords}
        self._cluster_map: dict[str, str] = {}  # ref → cluster name
        self._loaded = False

    # ── Public API ─────────────────────────────────────────────────────────

    def load(self) -> "Tier1EnrichmentApplier":
        """Load all enrichment files. Returns self for chaining."""
        enrichment_dir = Path(self._dir)

        for module_name, cluster_label in ENRICHMENT_FILES:
            filepath = enrichment_dir / f"{module_name}.py"
            if not filepath.exists():
                print(f"  ⚠ Enrichment file not found: {filepath}")
                continue

            try:
                mod = self._load_module(module_name, str(filepath))
                data = getattr(mod, "TIER1_ENRICHMENT", {})
                for ref, content in data.items():
                    self._data[ref] = content
                    self._cluster_map[ref] = cluster_label
            except Exception as e:
                print(f"  ⚠ Could not load {module_name}: {e}")

        self._loaded = True
        return self

    def apply(
        self,
        nodes: list[RequirementNode],
        overwrite: bool = False,
    ) -> int:
        """
        Apply Tier 1 enrichment to nodes in-place.

        Args:
            nodes:     List of RequirementNodes to enrich
            overwrite: If True, overwrite existing business_description.
                       Default False — only enrich nodes with empty fields.

        Returns:
            Count of nodes enriched.
        """
        if not self._loaded:
            self.load()
        self._last_report = self._apply_to_nodes(nodes, overwrite)
        return self._last_report.nodes_enriched

    def report(self) -> ApplyReport:
        """Return the report from the last apply() call."""
        if not hasattr(self, "_last_report"):
            return ApplyReport(warnings=["apply() not yet called"])
        return self._last_report

    def coverage(self, nodes: list[RequirementNode]) -> dict:
        """Report what % of nodes would be enriched."""
        if not self._loaded:
            self.load()
        total      = len(nodes)
        enrichable = sum(1 for n in nodes if n.ref in self._data)
        already    = sum(1 for n in nodes if n.business_description)
        return {
            "total_nodes":         total,
            "tier1_entries":       len(self._data),
            "nodes_with_match":    enrichable,
            "already_enriched":    already,
            "coverage_pct":        round(100 * enrichable / total) if total else 0,
        }

    # ── Internal ───────────────────────────────────────────────────────────

    def _apply_to_nodes(
        self,
        nodes:     list[RequirementNode],
        overwrite: bool,
    ) -> ApplyReport:
        report = ApplyReport()

        # Build a lookup by ref
        node_by_ref: dict[str, list[RequirementNode]] = {}
        for node in nodes:
            node_by_ref.setdefault(node.ref, []).append(node)

        for ref, enrichment in self._data.items():
            matched_nodes = node_by_ref.get(ref, [])

            if not matched_nodes:
                report.refs_not_found.append(ref)
                continue

            biz = enrichment.get("business_description", "")
            kw  = enrichment.get("query_keywords", {})

            for node in matched_nodes:
                if node.business_description and not overwrite:
                    report.nodes_skipped += 1
                    continue

                node.business_description = biz
                node.query_keywords       = kw
                report.nodes_enriched += 1

                cluster = self._cluster_map.get(ref, "unknown")
                report.cluster_counts[cluster] = (
                    report.cluster_counts.get(cluster, 0) + 1
                )

        return report

    @staticmethod
    def _load_module(name: str, path: str):
        """Load a Python module from a file path."""
        # Use a unique name to avoid module cache collisions
        unique_name = f"enrichment__{name}_{id(path)}"
        spec = importlib.util.spec_from_file_location(unique_name, path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
