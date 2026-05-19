"""ArionComply — Fulfilment Engine (skeleton).

Walks the RequirementNode → SATISFIED_BY → FulfilmentSpec → REQUIRES_EVIDENCE
→ EvidenceRequirement tree and composes a posture verdict per control.

Phase 1 (this commit): the walker, operators, and types are implemented;
the engine is driven by in-memory SpecDescriptor fixtures and is NOT yet
called from anywhere. The actual Neo4j query that builds a SpecDescriptor
from a control id, and the per-evidence-type leaf evaluators, land in
commits 3-4.

Posture vocabulary produced by this engine:
  Comply         — all required (MUST) leaves satisfied and fresh
  OFI            — applies, curated, but at least one MUST gap (or stale)
  UNKNOWN        — curation_status='uncurated' (no spec content yet);
                   honest signal that we don't know — never auto-Comply
  NotApplicable  — spec-level applies_when returned False for this tenant
  Comply (intentional empty)  — curation_status='explicit_empty'
  deferred       — curation_status='deferred_to_findings' (caller reads
                   posture_controls instead)

NC is NOT produced by this engine. NC requires an explicit finding of
failure (a contradiction surfaced by the extractor or a user-logged
issue) — that path is separate from the completeness composition done
here, per [[human_in_the_loop_positioning]]: we encourage completeness,
we do not judge accuracy.

The leaf evaluator is an injected callable. Its returned LeafVerdict
carries 'satisfied' (all MUST items recognised) and 'fresh' (within the
leaf's freshness_days, if any). The composer treats !satisfied OR !fresh
as a gap.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Union

from rag.posture.applies_when import (
    EvalContext, ValidationContext,
    parse as applies_when_parse,
    evaluate as applies_when_evaluate,
)


# ── Spec data model (in-memory mirror of the Neo4j shape) ─────────────────────

@dataclass
class LeafSpec:
    """Mirror of one :EvidenceRequirement node."""
    leaf_id:        str          # e.g. 'req:5.2:information_security_policy'
    evidence_type:  str          # e.g. 'policy', 'procedure', 'register_entry'
    must_items:     list[str]    = field(default_factory=list)
    should_items:   list[str]    = field(default_factory=list)
    freshness_days: Optional[int] = None
    title:          str          = ""
    # control_ref + standard_id let the leaf evaluator do coarse Phase-1
    # matching against (control_ref, status, evidence_type) findings when
    # the extractor hasn't tagged findings by checklist_item_id yet.
    control_ref:    str          = ""
    standard_id:    str          = ""


@dataclass
class Edge:
    """One :REQUIRES_EVIDENCE edge plus its inner target."""
    role:               str
    applies_when:       Optional[str]
    target:             Union["SpecDescriptor", LeafSpec]


@dataclass
class SpecDescriptor:
    """Mirror of one :FulfilmentSpec node and its outgoing children."""
    spec_id:         str
    op:              str          # 'ALL' | 'ANY' | 'AT_LEAST_N'
    n:               Optional[int] = None    # used by AT_LEAST_N
    applies_when:    Optional[str] = None
    curation_status: str          = "uncurated"   # 'curated' | 'uncurated' | 'explicit_empty' | 'deferred_to_findings'
    children:        list[Edge]   = field(default_factory=list)
    control_id:      str          = ""   # the RequirementNode id (for verdict trace)


VALID_OPS              = {"ALL", "ANY", "AT_LEAST_N"}
VALID_CURATION_STATUS  = {"curated", "uncurated", "explicit_empty", "deferred_to_findings"}


# ── Verdict types ──────────────────────────────────────────────────────────────

@dataclass
class LeafVerdict:
    leaf_id:            str
    role:               str
    evidence_type:      str
    satisfied:          bool                  # all MUST items recognised
    fresh:              bool                  # within freshness_days (True if no freshness req)
    reason:             str                   # one-line rationale for display
    items_recognised:   list[str] = field(default_factory=list)
    items_unrecognised: list[str] = field(default_factory=list)

    @property
    def counts_as_comply(self) -> bool:
        return self.satisfied and self.fresh


@dataclass
class ControlVerdict:
    control_id:           str
    spec_id:              Optional[str]
    posture:              str                 # see header for vocabulary
    applies:              bool                # False ⇒ applies_when at spec level was False
    curation_status:      str
    leaves:               list[LeafVerdict]   = field(default_factory=list)
    gap_list:             list[str]           = field(default_factory=list)
    reason:               str                 = ""


# ── Leaf evaluator callable type ──────────────────────────────────────────────

LeafEvaluatorFn = Callable[[LeafSpec, EvalContext], LeafVerdict]


def not_yet_implemented_leaf_evaluator(leaf: LeafSpec, ctx: EvalContext) -> LeafVerdict:
    """Default placeholder — wiring at commit 3-4 will inject the real one,
    which dispatches on leaf.evidence_type. Returns 'not implemented' verdict."""
    return LeafVerdict(
        leaf_id            = leaf.leaf_id,
        role               = "",
        evidence_type      = leaf.evidence_type,
        satisfied          = False,
        fresh              = False,
        reason             = f"leaf evaluator for evidence_type={leaf.evidence_type!r} not yet wired",
        items_recognised   = [],
        items_unrecognised = list(leaf.must_items),
    )


# ── applies_when wrapper that tolerates NULL/empty as 'always applies' ────────

def _applies(expr: Optional[str], eval_ctx: EvalContext) -> bool:
    """NULL ⇒ True. Empty string is a curator error caught at parse time."""
    if expr is None:
        return True
    ast = applies_when_parse(expr)
    return bool(applies_when_evaluate(ast, eval_ctx))


# ── Walker / composer ─────────────────────────────────────────────────────────

def evaluate_spec(
    spec:           SpecDescriptor,
    leaf_evaluator: LeafEvaluatorFn,
    eval_ctx:       EvalContext,
) -> ControlVerdict:
    """Walk a single spec subtree and return its verdict.

    The top-level control_id on the returned verdict is taken from
    spec.control_id; nested specs (children of kind=SpecDescriptor) get a
    synthetic verdict that the parent composes via op.
    """
    if spec.op not in VALID_OPS:
        raise ValueError(f"invalid spec op {spec.op!r} (expected one of {VALID_OPS})")
    if spec.curation_status not in VALID_CURATION_STATUS:
        raise ValueError(f"invalid curation_status {spec.curation_status!r}")

    # Spec-level applies_when gate
    if not _applies(spec.applies_when, eval_ctx):
        return ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "NotApplicable",
            applies         = False,
            curation_status = spec.curation_status,
            reason          = "spec-level applies_when evaluated to False for this tenant",
        )

    # curation_status routing
    if spec.curation_status == "uncurated":
        return ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "UNKNOWN",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "evidence requirements not yet curated for this control",
        )
    if spec.curation_status == "deferred_to_findings":
        return ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "deferred",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "posture for this control is computed from findings, not from the evidence model",
        )
    if spec.curation_status == "explicit_empty":
        return ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "Comply",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "no evidence is required for this control (explicit decision)",
        )

    # curated: walk children, compose
    leaf_verdicts: list[LeafVerdict] = []
    child_outcomes: list[bool] = []     # True ⇒ counts as Comply for compose
    skipped_count = 0

    for edge in spec.children:
        # Edge-level applies_when gate — skipped edges are neither comply nor gap
        if not _applies(edge.applies_when, eval_ctx):
            skipped_count += 1
            continue

        target = edge.target
        if isinstance(target, LeafSpec):
            v = leaf_evaluator(target, eval_ctx)
            v.role = edge.role  # the edge owns the display role
            leaf_verdicts.append(v)
            child_outcomes.append(v.counts_as_comply)
        elif isinstance(target, SpecDescriptor):
            sub = evaluate_spec(target, leaf_evaluator, eval_ctx)
            # Treat nested sub-spec as Comply iff its rolled-up posture is Comply.
            child_outcomes.append(sub.posture == "Comply")
            # Surface the sub's leaves so the parent's verdict has the full picture
            leaf_verdicts.extend(sub.leaves)
        else:
            raise TypeError(f"edge target must be LeafSpec or SpecDescriptor, got {type(target).__name__}")

    posture = _compose_posture(spec.op, spec.n, child_outcomes)
    gap_list = _build_gap_list(leaf_verdicts)
    reason = _build_reason(spec.op, spec.n, child_outcomes, skipped_count)

    return ControlVerdict(
        control_id      = spec.control_id,
        spec_id         = spec.spec_id,
        posture         = posture,
        applies         = True,
        curation_status = spec.curation_status,
        leaves          = leaf_verdicts,
        gap_list        = gap_list,
        reason          = reason,
    )


def _compose_posture(op: str, n: Optional[int], outcomes: list[bool]) -> str:
    """Compose child outcomes (True = Comply) into a parent posture."""
    if not outcomes:
        # All children were skipped (applies_when False on every edge) OR no
        # children at all under a 'curated' spec. Empty-after-applicability
        # is a defensible Comply: the tenant doesn't have anything to fulfil
        # right now. The curator's intent is captured by 'explicit_empty'
        # which routes earlier; this branch handles the dynamic case.
        return "Comply"
    if op == "ALL":
        return "Comply" if all(outcomes) else "OFI"
    if op == "ANY":
        return "Comply" if any(outcomes) else "OFI"
    if op == "AT_LEAST_N":
        threshold = n if (n is not None and n >= 0) else 1
        return "Comply" if sum(1 for o in outcomes if o) >= threshold else "OFI"
    raise ValueError(f"unknown op {op!r}")


def _build_gap_list(verdicts: list[LeafVerdict]) -> list[str]:
    """Auditor-facing list of what's missing. Per [[the completeness principle]]
    items are 'unrecognised' (we couldn't find them in the supply) rather than
    'missing' (a judgement we don't make)."""
    gaps: list[str] = []
    for v in verdicts:
        if v.counts_as_comply:
            continue
        if not v.fresh and v.satisfied:
            gaps.append(f"[{v.role or v.evidence_type}] artifact is stale — consider refreshing")
            continue
        if v.items_unrecognised:
            for item in v.items_unrecognised:
                gaps.append(f"[{v.role or v.evidence_type}] auditors expect: {item} — we couldn't find it")
        else:
            gaps.append(f"[{v.role or v.evidence_type}] no matching artifact uploaded")
    return gaps


def _build_reason(op: str, n: Optional[int], outcomes: list[bool], skipped: int) -> str:
    total       = len(outcomes)
    satisfied   = sum(1 for o in outcomes if o)
    op_text     = op if op != "AT_LEAST_N" else f"AT_LEAST_{n}"
    skip_text   = f", {skipped} gated off by applies_when" if skipped else ""
    return f"{op_text}: {satisfied}/{total} children satisfied{skip_text}"


# ── Public entry point (skeleton — not yet wired) ─────────────────────────────

def evaluate_control(
    spec:           SpecDescriptor,
    leaf_evaluator: LeafEvaluatorFn,
    eval_ctx:       EvalContext,
) -> ControlVerdict:
    """Alias of evaluate_spec at the moment; gives callers a name that matches
    the conceptual unit (a control's verdict) rather than the data structure
    (the spec subtree). Once the Neo4j-driven builder lands in commit 4, this
    will take a control_id + the neo4j driver and build the SpecDescriptor
    before walking it."""
    return evaluate_spec(spec, leaf_evaluator, eval_ctx)
