"""
ContextAssembler — ArionComply RAG Orchestration

Takes the ExpandedContext from GraphExpander and structures it
into a precise, tiered prompt context for the LLM answer step.

Design principles:
  - Primary nodes get full content (obligation text + enrichment)
  - Secondary nodes get compressed (ref + title + one-line summary)
  - Posture is injected next to each relevant control
  - Cross-framework relationships are made explicit
  - Token budget enforced per question type
  - Structure varies by QuestionType — a definition answer looks
    different from a gap analysis

Output: AssembledContext — a structured string ready for the LLM,
plus metadata the LLM call needs (question type, tenant, intent).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from rag.classifier     import QueryIntent, QuestionType, TenantProfile
from rag.graph_expander import ExpandedContext, ExpandedNode, CrossFrameworkEdge


# ── Token budgets per question type ───────────────────────────────────────────
# Approximate token counts for context assembly.
# Primary nodes use ~150-250 tokens each (full content).
# Secondary nodes use ~40-60 tokens each (compressed).

CONTEXT_BUDGET_TOKENS: dict[QuestionType, int] = {
    QuestionType.DEFINITION:      2000,
    QuestionType.IMPLEMENTATION:  3000,
    QuestionType.GAP_ANALYSIS:    4000,
    QuestionType.POSTURE_CHECK:   3500,
    QuestionType.CROSS_FRAMEWORK: 3000,
    QuestionType.FREE_ASSESSMENT: 4500,
    QuestionType.UNKNOWN:         2500,
}

# Max primary nodes to render at full content
MAX_PRIMARY_FULL: dict[QuestionType, int] = {
    QuestionType.DEFINITION:      4,
    QuestionType.IMPLEMENTATION:  6,
    QuestionType.GAP_ANALYSIS:    8,
    QuestionType.POSTURE_CHECK:   7,
    QuestionType.CROSS_FRAMEWORK: 6,
    QuestionType.FREE_ASSESSMENT: 8,
    QuestionType.UNKNOWN:         4,
}


# ── Output dataclass ───────────────────────────────────────────────────────────

@dataclass
class AssembledContext:
    """
    The fully assembled prompt context ready for the LLM.

    Passed directly to LLMAnswer.generate().
    """
    # The structured context string for the LLM
    context_text:    str

    # Metadata — not in the context string but used by LLM call
    intent:          QueryIntent
    tenant_name:     str
    question_type:   QuestionType

    # For verification pass — which nodes/posture were used
    node_ids_used:   list[str]
    has_posture:     bool
    posture_summary: dict        # ref → finding for nodes used

    # Document alerts — missing files that should be surfaced
    document_alerts: list = field(default_factory=list)

    # Stats
    primary_count:   int = 0
    secondary_count: int = 0
    approx_tokens:   int = 0


# ── ContextAssembler ──────────────────────────────────────────────────────────

class ContextAssembler:
    """
    Assembles ExpandedContext + PostureRecords into a structured
    LLM prompt context.

    Usage:
        assembler = ContextAssembler(tenant_profile)
        context   = assembler.assemble(
            expanded = graph_expander_result,
            intent   = query_intent,
            posture  = posture_lookup_result,   # dict: node_id → PostureRecord
        )
    """

    def __init__(self, tenant_profile: TenantProfile):
        self.tenant = tenant_profile

    # ── Public API ─────────────────────────────────────────────────────────

    def assemble(
        self,
        expanded:          ExpandedContext,
        intent:            QueryIntent,
        posture:           dict | None = None,
        doc_contexts:      dict | None = None,      # node_id → DocumentContext
        incident_contexts: list | None = None,      # list[IncidentObligationContext]
        document_alerts:   list | None = None,      # from load_document_alerts()
    ) -> AssembledContext:
        """
        Assemble the full prompt context.

        Args:
            expanded:          ExpandedContext from GraphExpander
            intent:            QueryIntent from QueryClassifier
            posture:           node_id → {finding, gap, evidence}
            doc_contexts:      node_id → DocumentContext (when needs_documentation)
            incident_contexts: open incidents with triggered obligations
        """
        posture           = posture or {}
        doc_contexts      = doc_contexts or {}
        incident_contexts = incident_contexts or []
        qtype   = intent.question_type
        budget  = CONTEXT_BUDGET_TOKENS.get(qtype, 2500)
        max_full = MAX_PRIMARY_FULL.get(qtype, 5)

        sections = []

        # ── Section 1: Query frame ─────────────────────────────────────
        sections.append(self._render_query_frame(intent))

        # ── Section 2: Primary obligations (full content) ─────────────
        primary = self._select_primary(expanded, intent, max_full)
        if primary:
            sections.append(
                self._render_primary_section(primary, posture, intent)
            )

        # ── Section 3: Cross-framework implementing controls ──────────
        xfw_nodes = self._select_xfw_nodes(expanded, intent)
        if xfw_nodes:
            sections.append(
                self._render_xfw_section(
                    xfw_nodes, expanded.xfw_edges, posture, intent
                )
            )

        # ── Section 4: Supporting context (compressed) ────────────────
        secondary = [
            n for n in expanded.secondary_nodes
            if n not in primary and n not in xfw_nodes
        ]
        if secondary:
            sections.append(
                self._render_secondary_section(secondary[:8])
            )

        # ── Section 5: Posture summary (if available) ─────────────────
        if posture and intent.needs_posture:
            sections.append(self._render_posture_summary(posture))

        # ── Section 6: Document requirements (when needs_documentation) ─
        if doc_contexts and intent.dimensions.needs_documentation:
            doc_section = self._render_document_section(
                doc_contexts = doc_contexts,
                primary_ids  = {n.node_id for n in primary},
            )
            if doc_section:
                sections.append(doc_section)

        # ── Section 7: Open incidents with deadlines ────────────────────
        if incident_contexts:
            inc_section = self._render_incident_section(incident_contexts)
            if inc_section:
                sections.insert(1, inc_section)  # after query frame — urgent first

        context_text   = "\n\n".join(s for s in sections if s.strip())
        approx_tokens  = len(context_text) // 4   # rough estimate

        # Trim if over budget — remove secondary section first
        if approx_tokens > budget and secondary:
            sections_no_secondary = [
                s for s in sections
                if "SUPPORTING CONTEXT" not in s[:30]
            ]
            context_text  = "\n\n".join(s for s in sections_no_secondary if s.strip())
            approx_tokens = len(context_text) // 4

        all_used     = primary + xfw_nodes
        posture_used = {
            nid: rec for nid, rec in posture.items()
            if nid in {n.node_id for n in all_used}
        }

        return AssembledContext(
            context_text    = context_text,
            intent          = intent,
            tenant_name     = self.tenant.name,
            question_type   = qtype,
            node_ids_used   = [n.node_id for n in all_used],
            has_posture     = bool(posture),
            posture_summary = posture_used,
            document_alerts = document_alerts or [],
            primary_count   = len(primary),
            secondary_count = len(secondary),
            approx_tokens   = approx_tokens,
        )

    # ── Section renderers ──────────────────────────────────────────────

    def _render_query_frame(self, intent: QueryIntent) -> str:
        """Header section: query type, scope, tenant context."""
        qtype_labels = {
            QuestionType.DEFINITION:      "Definition / Explanation",
            QuestionType.IMPLEMENTATION:  "Implementation Guidance",
            QuestionType.GAP_ANALYSIS:    "Gap Analysis",
            QuestionType.POSTURE_CHECK:   "Compliance Posture Check",
            QuestionType.CROSS_FRAMEWORK: "Cross-Framework Mapping",
            QuestionType.FREE_ASSESSMENT: "Overall Compliance Assessment",
            QuestionType.UNKNOWN:         "General Query",
        }
        standards = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in intent.standards_scope
        )
        role = intent.role_filter or "controller/processor"
        refs = ", ".join(intent.resolved_refs[:5]) if intent.resolved_refs else "general"

        lines = [
            "[QUERY CONTEXT]",
            f"Type:       {qtype_labels.get(intent.question_type, 'Query')}",
            f"Standard:   {standards}",
            f"Role:       {role}",
            f"Focus:      {refs}",
            f"Tenant:     {self.tenant.name}",
            f"Posture:    {'available' if self.tenant.has_posture_data else 'not yet loaded'}",
        ]
        return "\n".join(lines)

    def _render_primary_section(
        self,
        nodes:   list[ExpandedNode],
        posture: dict,
        intent:  QueryIntent,
    ) -> str:
        """Primary obligations — full content.
        
        Ordering: NC first (most critical), then OFI, then unassessed,
        then Comply. Ensures the LLM sees the most important findings
        at the top of the context where attention is highest.
        """
        def _posture_priority(node: ExpandedNode) -> int:
            rec = posture.get(node.node_id, {}) if posture else {}
            finding = rec.get("finding", "")
            return {"NC": 0, "OFI": 1, "": 2, "N/A": 3, "Comply": 4}.get(finding, 2)

        sorted_nodes = sorted(nodes, key=_posture_priority)
        lines = ["[PRIMARY OBLIGATIONS]"]
        for node in sorted_nodes:
            lines.append(self._render_node_full(node, posture, intent))
            lines.append("")
        return "\n".join(lines)

    def _render_xfw_section(
        self,
        nodes:     list[ExpandedNode],
        xfw_edges: list[CrossFrameworkEdge],
        posture:   dict,
        intent:    QueryIntent,
    ) -> str:
        """Cross-framework implementing controls."""
        if not nodes:
            return ""

        # Separate ISO and GDPR cross-framework nodes
        iso_nodes  = [n for n in nodes if n.is_iso]
        gdpr_nodes = [n for n in nodes if n.is_gdpr]

        lines = ["[CROSS-FRAMEWORK CONTROLS]"]

        if iso_nodes and intent.standards_scope and "ISO27001:2022" in intent.standards_scope:
            lines.append("ISO 27001:2022 implementing controls:")
            for node in iso_nodes:
                # Find the relationship type for this node
                rel = self._find_rel_type(node.node_id, xfw_edges)
                lines.append(self._render_node_with_posture(
                    node, posture, rel_label=rel
                ))
                lines.append("")

        if gdpr_nodes and intent.standards_scope and "GDPR:2016/679" in intent.standards_scope:
            lines.append("GDPR obligations satisfied by these controls:")
            for node in gdpr_nodes:
                rel = self._find_rel_type(node.node_id, xfw_edges)
                lines.append(self._render_node_with_posture(
                    node, posture, rel_label=rel
                ))
                lines.append("")

        return "\n".join(lines)

    def _render_secondary_section(
        self,
        nodes: list[ExpandedNode],
    ) -> str:
        """Supporting context — compressed one-liners."""
        if not nodes:
            return ""
        lines = ["[SUPPORTING CONTEXT]"]
        for node in nodes:
            summary = self._one_line_summary(node)
            lines.append(f"  {node.ref:20s} {node.standard_id.split(':')[0]:10s} {summary}")
        return "\n".join(lines)

    def _render_document_section(
        self,
        doc_contexts: dict,         # node_id → DocumentContext
        primary_ids:  set[str],     # node_ids already in primary section
    ) -> str:
        """
        Render document requirements for selected controls.
        Shows checklist items with ✓/✗ status when document is uploaded,
        or shows requirements list when no document uploaded yet.
        Only renders for controls that are in the primary section.
        """
        lines = ["[DOCUMENT REQUIREMENTS]"]
        rendered = 0

        for node_id, ctx in doc_contexts.items():
            # Only render for controls already in primary context
            if node_id not in primary_ids:
                continue

            lines.append(f"\n── {ctx.control_ref}: {ctx.document_title}")
            lines.append(f"   Type: {ctx.document_type}  |  Trigger: {ctx.trigger_type}")

            if ctx.has_document_uploaded:
                # Show evaluation results
                pct = ctx.completeness_pct
                lines.append(f"   Completeness: {pct}%")
                present = ctx.present_must
                missing = ctx.missing_must
                gdpr_gaps = ctx.gdpr_gaps

                if present:
                    for item in present[:3]:
                        lines.append(f"   ✓ {item.text}")
                if missing:
                    for item in missing:
                        gdpr_tag = " [GDPR required]" if item.gdpr_required else ""
                        lines.append(f"   ✗ {item.text}{gdpr_tag}")
                if gdpr_gaps:
                    lines.append(
                        f"   ⚠ {len(gdpr_gaps)} GDPR-required items missing"
                    )
            else:
                # No document uploaded — show what's needed
                lines.append("   Status: not yet uploaded")
                lines.append("   Must contain:")
                for item in ctx.must_contain[:5]:
                    gdpr_tag = " [GDPR]" if item.gdpr_required else ""
                    lines.append(f"     - {item.text}{gdpr_tag}")
                if len(ctx.must_contain) > 5:
                    lines.append(f"     ... +{len(ctx.must_contain)-5} more items")

            rendered += 1

        if rendered == 0:
            return ""

        return "\n".join(lines)

    def _render_incident_section(
        self,
        incident_contexts: list,    # list[IncidentObligationContext]
    ) -> str:
        """
        Render open incidents prominently — above primary obligations.
        Shows deadline urgency and triggered controls.
        Critical incidents get ⚠ WARNING header.
        """
        if not incident_contexts:
            return ""

        lines = []
        critical = [i for i in incident_contexts
                    if i.urgency in ("overdue", "critical")]
        others   = [i for i in incident_contexts
                    if i.urgency not in ("overdue", "critical")]

        if critical:
            lines.append("[⚠ ACTIVE INCIDENTS — DEADLINES APPROACHING]")
            for inc in critical:
                urgency_label = "OVERDUE" if inc.urgency == "overdue" else "< 12 HOURS"
                lines.append(
                    f"\n!! {inc.incident_type.replace('_',' ').upper()} "
                    f"[{inc.severity.upper()}] — Deadline: {urgency_label}"
                )
                if inc.deadline_at:
                    lines.append(f"   Deadline: {inc.deadline_at}")
                lines.append(
                    f"   Obligations triggered: "
                    f"{', '.join(nid.split(':')[-1] for nid in inc.triggered_node_ids)}"
                )

        if others:
            lines.append("\n[OPEN INCIDENTS]")
            for inc in others:
                lines.append(
                    f"  {inc.incident_type.replace('_',' ').title()} "
                    f"[{inc.severity}] — {inc.urgency.replace('_',' ')}"
                )

        return "\n".join(lines) if lines else ""

    def _render_posture_summary(self, posture: dict) -> str:
        """Tenant posture summary — includes gap descriptions for verifier."""
        if not posture:
            return ""
        lines = ["[COMPLIANCE POSTURE SUMMARY — these are factual assessment findings]"]
        for node_id, rec in posture.items():
            ref     = node_id.split(":")[-1]
            finding = rec.get("finding", "?")
            gap     = rec.get("gap_description", "")
            evidence = rec.get("evidence_note", "")
            action  = rec.get("remedial_action", "")

            icons = {"Comply": "✓", "OFI": "△", "NC": "✗", "N/A": "—"}
            icon  = icons.get(finding, "?")
            line  = f"  {icon} {finding:7s} {ref}"
            if gap:
                line += f"\n    Gap: {gap}"
            if evidence and finding == "Comply":
                line += f"\n    Evidence: {evidence}"
            if action and finding in ("OFI", "NC"):
                line += f"\n    Action: {action}"
            lines.append(line)
        return "\n".join(lines)

    # ── Node renderers ─────────────────────────────────────────────────

    def _render_node_full(
        self,
        node:    ExpandedNode,
        posture: dict,
        intent:  QueryIntent,
    ) -> str:
        """Full node content for primary obligations."""
        lines = [f"── {node.ref}: {node.title}"]

        # Extract layers from the vector document
        doc_layers = self._parse_document_layers(node.document)

        # Business description — the plain-English explanation
        if doc_layers.get("business_description"):
            lines.append(doc_layers["business_description"])

        # Obligation text — the canonical legal text
        if doc_layers.get("obligation_text"):
            lines.append(f"Text: {doc_layers['obligation_text']}")

        # Posture (if available and relevant)
        rec = posture.get(node.node_id)
        if rec:
            lines.append(self._render_posture_record(rec))
        elif posture:
            # Posture data is loaded but this control has not been assessed
            # Explicit marker prevents LLM from inferring compliance status
            lines.append("Posture: ? Not yet assessed — do not infer compliance status")

        # Evidence requirements — what compliance looks like
        if (doc_layers.get("evidence") and
                intent.question_type in (
                    QuestionType.GAP_ANALYSIS,
                    QuestionType.POSTURE_CHECK,
                    QuestionType.IMPLEMENTATION,
                )):
            lines.append(f"Evidence required:\n  {doc_layers['evidence']}")

        # Gap indicators — what non-compliance looks like
        if (doc_layers.get("gaps") and
                intent.question_type in (
                    QuestionType.GAP_ANALYSIS,
                    QuestionType.POSTURE_CHECK,
                )):
            lines.append(f"Common gaps:\n  {doc_layers['gaps']}")

        return "\n".join(lines)

    def _render_node_with_posture(
        self,
        node:      ExpandedNode,
        posture:   dict,
        rel_label: str = "",
    ) -> str:
        """Node with inline posture — for cross-framework section."""
        rec      = posture.get(node.node_id)
        posture_str = ""
        if rec:
            finding = rec.get("finding", "?")
            gap     = rec.get("gap_description", "")
            posture_str = f" [{finding}]"
            if gap and finding in ("OFI", "NC"):
                posture_str += f" — {gap[:80]}"
        elif posture:
            # Posture loaded but control not assessed — mark explicitly
            posture_str = " [Not assessed]"

        rel_str = f" ({rel_label})" if rel_label else ""
        line    = f"  {node.ref:20s}{rel_str}{posture_str}"

        # Add first sentence of business description
        doc_layers = self._parse_document_layers(node.document)
        if doc_layers.get("business_description"):
            first_sent = self._first_sentence(
                doc_layers["business_description"]
            )
            line += f"\n    {first_sent}"

        return line

    # ── Node selection ─────────────────────────────────────────────────

    def _select_primary(
        self,
        expanded: ExpandedContext,
        intent:   QueryIntent,
        max_full: int,
    ) -> list[ExpandedNode]:
        """
        Select primary nodes for full rendering.
        Priority: cited > parents > others.
        """
        cited   = [n for n in expanded.primary_nodes
                   if n.source == "cited"]
        parents = [n for n in expanded.primary_nodes
                   if n.source == "parent"]
        others  = [n for n in expanded.secondary_nodes
                   if n.source in ("cited", "parent")]

        result = cited + parents + others
        # Remove informational nodes
        result = [n for n in result if not n.is_informational]
        return result[:max_full]

    def _select_xfw_nodes(
        self,
        expanded: ExpandedContext,
        intent:   QueryIntent,
    ) -> list[ExpandedNode]:
        """
        Select cross-framework nodes.
        For GAP/POSTURE: include all, ISO first.
        For DEFINITION: skip cross-framework.
        """
        if intent.question_type == QuestionType.DEFINITION:
            return []

        xfw = [n for n in expanded.secondary_nodes
               if n.source == "xfw" and not n.is_informational]

        # Sort: ISO first for GDPR-primary queries, GDPR first for ISO-primary
        primary_std = (
            "GDPR:2016/679"
            if any("GDPR" in s for s in intent.standards_scope)
            else "ISO27001:2022"
        )
        xfw.sort(key=lambda n: (0 if n.standard_id != primary_std else 1))
        return xfw[:6]   # cap at 6 cross-framework nodes

    # ── Document parsing ───────────────────────────────────────────────

    def _parse_document_layers(self, document: str) -> dict[str, str]:
        """
        Parse the layered vector document back into structured fields.

        Layer order in to_vector_document():
          Line 0: header (standard + ref + title)
          Line 1: business_description (if enriched)
          ...
          "Text: ..." or raw obligation text
          "Evidence: ..."
          "Gaps: ..."
          "Keywords: ..."
          "Related ...: ..."
        """
        lines   = [l.strip() for l in document.split('\n') if l.strip()]
        result  = {}

        if not lines:
            return result

        # Skip header line (line 0: "GDPR:2016/679 Art.32: ...")
        body_lines = lines[1:]

        current_key   = "business_description"
        current_lines = []

        for line in body_lines:
            if line.startswith("Evidence: "):
                if current_lines:
                    result[current_key] = " ".join(current_lines)
                current_key   = "evidence"
                current_lines = [line[len("Evidence: "):]]
            elif line.startswith("Gaps: "):
                if current_lines:
                    result[current_key] = " ".join(current_lines)
                current_key   = "gaps"
                current_lines = [line[len("Gaps: "):]]
            elif line.startswith("Keywords: "):
                if current_lines:
                    result[current_key] = " ".join(current_lines)
                current_key   = "keywords"
                current_lines = [line[len("Keywords: "):]]
            elif line.startswith("Related "):
                if current_lines:
                    result[current_key] = " ".join(current_lines)
                current_key   = "related"
                current_lines = []   # skip related lines
            else:
                # Continuation of current section
                # Detect if this looks like obligation text vs description
                # Obligation text tends to start with lowercase or a legal phrase
                if (current_key == "business_description" and
                        current_lines and
                        not result.get("obligation_text")):
                    # Check if this line looks like canonical text
                    # (short, starts with known legal phrases)
                    legal_starts = (
                        "the ", "where ", "each ", "any ", "when ", "in ",
                        "processing", "personal data", "the controller",
                        "a controller", "the processor"
                    )
                    if (len(line) < 150 and
                            line.lower().startswith(legal_starts)):
                        # Looks like obligation text — promote
                        result["business_description"] = " ".join(current_lines)
                        current_key   = "obligation_text"
                        current_lines = [line]
                        continue
                current_lines.append(line)

        if current_lines and current_key not in ("related", "keywords"):
            result[current_key] = " ".join(current_lines)

        return result

    def _render_posture_record(self, rec: dict) -> str:
        """Render a posture record inline."""
        finding  = rec.get("finding", "Unknown")
        evidence = rec.get("evidence_note", "")
        gap      = rec.get("gap_description", "")
        action   = rec.get("remedial_action", "")

        finding_icons = {
            "Comply": "✓", "OFI": "△", "NC": "✗", "N/A": "—"
        }
        icon   = finding_icons.get(finding, "?")
        lines  = [f"Posture: {icon} {finding}"]
        if evidence and finding == "Comply":
            lines.append(f"  Evidence: {evidence[:100]}")
        if gap and finding in ("OFI", "NC"):
            lines.append(f"  Gap: {gap[:100]}")
        if action and finding in ("OFI", "NC"):
            lines.append(f"  Action: {action[:100]}")
        return "\n".join(lines)

    # ── Helpers ────────────────────────────────────────────────────────

    def _find_rel_type(
        self,
        node_id:   str,
        xfw_edges: list[CrossFrameworkEdge],
    ) -> str:
        """Find the relationship type for a node from the XFW edges."""
        for e in xfw_edges:
            if e.source_id == node_id or e.target_id == node_id:
                return e.rel_type
        return ""

    def _one_line_summary(self, node: ExpandedNode) -> str:
        """Extract first sentence of business description for compression."""
        doc_layers = self._parse_document_layers(node.document)
        biz = doc_layers.get("business_description", "")
        if biz:
            return self._first_sentence(biz)[:90]
        return node.title[:90]

    def _first_sentence(self, text: str) -> str:
        """Extract first sentence from text."""
        m = re.search(r'^[^.!?]+[.!?]', text)
        return m.group(0).strip() if m else text[:100]
