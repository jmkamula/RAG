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
class ControlRef:
    """A reference to another RequirementNode whose verdict composes into the parent.

    Used when the parent control is satisfied by *implementing* another control —
    e.g. GDPR Art.32 (security of processing) is satisfied by the ISO 27001
    Annex A controls that supply the technical/organisational measures.

    Walker resolves the target via the caller-provided spec_resolver and runs
    evaluate_spec on it. Result composes into the parent via the usual op
    (ALL/ANY/AT_LEAST_N), with these propagation rules:
      - target.posture=Comply      → counts toward parent
      - target.posture=OFI         → counts against parent
      - target.posture=NotApplicable → edge-skipped (like applies_when=False)
      - target.posture=UNKNOWN     → parent inherits UNKNOWN (sticky)
      - target.posture=deferred    → counts toward parent iff deferred and Comply

    scope_items optionally narrows what items of the target count: when set,
    only LeafVerdicts whose leaf_id is in scope_items contribute to outcome.
    Lets a deriving framework (e.g. GDPR Art.32) cherry-pick items from the
    source (e.g. ISO A.5.23) without inheriting source-framework-only items
    (e.g. cloud exit strategy) that the deriving framework doesn't care about.
    """
    target_control_id:  str
    title:              str = ""
    scope_items:        Optional[list[str]] = None


@dataclass
class Edge:
    """One :REQUIRES_EVIDENCE or :DERIVES_FROM edge plus its inner target."""
    role:               str
    applies_when:       Optional[str]
    target:             Union["SpecDescriptor", LeafSpec, ControlRef]


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
    # Parallel ID arrays — same order as items_recognised / items_unrecognised.
    # Populated by GenericLeafEvaluator from must_item_ids. Consumed by the
    # per-MUST advisory form (advisory.py + UI) to bind tenant-entered text
    # to specific checklist_item_ids on save.
    item_ids_recognised:   list[str] = field(default_factory=list)
    item_ids_unrecognised: list[str] = field(default_factory=list)
    # Per-MUST staleness (2026-08-10). MUST ids whose latest recognising
    # evidence is older than freshness_days. When the leaf has no
    # freshness_days set, this list is always empty. Additive: leaf-level
    # `fresh: bool` remains for existing consumers.
    item_ids_stale:        list[str] = field(default_factory=list)
    # Per-MUST partial (2026-08-10). MUST ids with document_findings.status
    # ='partial' bound to them. Not counted toward `satisfied` (strict
    # present-only semantics preserved), but surfaced so consumers can
    # render a ◐ half-state instead of a blank.
    item_ids_partial:      list[str] = field(default_factory=list)

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
    # Sub-verdicts from ControlRef edges. tuple of (edge.role, sub-verdict).
    # Used by the chat surface to render attribution: a Comply on Art.32 that
    # rolled up from ISO A.5.23 + A.8.24 should say so, not pretend the
    # evidence was direct.
    derived_from:         list[tuple[str, "ControlVerdict"]] = field(default_factory=list)
    # Polite gap surface (Phase C):
    #   our_gaps    — gaps the tenant cannot close on their own. Curation
    #                 incomplete, dep uncurated, evaluator not implemented.
    #                 Copy is first-person plural — "We're still curating…".
    #   tenant_gaps — gaps the tenant can close by uploading or refreshing
    #                 evidence. Copy is neutral observation — "Your <type>
    #                 doesn't yet include…", never accusatory.
    # gap_list stays as the union (our_gaps + tenant_gaps) for backward
    # compatibility with callers that haven't migrated to the split yet.
    our_gaps:             list[str]           = field(default_factory=list)
    tenant_gaps:          list[str]           = field(default_factory=list)
    gap_list:             list[str]           = field(default_factory=list)
    reason:               str                 = ""


# ── Leaf evaluator callable type ──────────────────────────────────────────────

LeafEvaluatorFn = Callable[[LeafSpec, EvalContext], LeafVerdict]

# Spec resolver: maps a RequirementNode.id to the SpecDescriptor for that
# control's FulfilmentSpec. Required when walking a tree that contains
# ControlRef edges. In-memory tests pass a dict.get; production wires this
# to the Neo4j-driven spec builder.
SpecResolverFn = Callable[[str], "SpecDescriptor"]


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
    spec_resolver:  Optional[SpecResolverFn] = None,
    _stack:         Optional[frozenset[str]] = None,
    _memo:          Optional[dict[str, ControlVerdict]] = None,
) -> ControlVerdict:
    """Walk a single spec subtree and return its verdict.

    The top-level control_id on the returned verdict is taken from
    spec.control_id; nested specs (children of kind=SpecDescriptor) get a
    synthetic verdict that the parent composes via op.

    When a spec's children contain ControlRef edges (cross-control derivation),
    spec_resolver is invoked to look up the target SpecDescriptor by control_id.
    Recursion is cycle-guarded and memoized via the internal _stack/_memo.
    """
    if spec.op not in VALID_OPS:
        raise ValueError(f"invalid spec op {spec.op!r} (expected one of {VALID_OPS})")
    if spec.curation_status not in VALID_CURATION_STATUS:
        raise ValueError(f"invalid curation_status {spec.curation_status!r}")

    _stack = _stack if _stack is not None else frozenset()
    _memo  = _memo  if _memo  is not None else {}

    # Cycle guard (only meaningful when ControlRef edges are walked)
    if spec.control_id and spec.control_id in _stack:
        return ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "UNKNOWN",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = f"derivation cycle detected — {' → '.join([*sorted(_stack), spec.control_id])}",
        )
    if spec.control_id and spec.control_id in _memo:
        return _memo[spec.control_id]

    # Spec-level applies_when gate
    if not _applies(spec.applies_when, eval_ctx):
        verdict = ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "NotApplicable",
            applies         = False,
            curation_status = spec.curation_status,
            reason          = "spec-level applies_when evaluated to False for this tenant",
        )
        if spec.control_id:
            _memo[spec.control_id] = verdict
        return verdict

    # curation_status routing
    if spec.curation_status == "uncurated":
        verdict = ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "UNKNOWN",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "evidence requirements not yet curated for this control",
        )
        if spec.control_id:
            _memo[spec.control_id] = verdict
        return verdict
    if spec.curation_status == "deferred_to_findings":
        verdict = ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "deferred",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "posture for this control is computed from findings, not from the evidence model",
        )
        if spec.control_id:
            _memo[spec.control_id] = verdict
        return verdict
    if spec.curation_status == "explicit_empty":
        verdict = ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "Comply",
            applies         = True,
            curation_status = spec.curation_status,
            reason          = "no evidence is required for this control (explicit decision)",
        )
        if spec.control_id:
            _memo[spec.control_id] = verdict
        return verdict

    # curated: walk children, compose
    inner_stack: frozenset[str] = _stack | ({spec.control_id} if spec.control_id else set())

    leaf_verdicts:           list[LeafVerdict] = []
    derived_verdicts:        list[tuple[str, ControlVerdict]] = []
    child_outcomes:          list[bool] = []
    # child_progress runs parallel to child_outcomes: True iff the child has
    # ANY evidence of implementation (leaf with ≥1 items_recognised, or sub-
    # verdict at Comply/OFI). Used by _compose_posture to distinguish "no
    # evidence anywhere" (→ NC) from "partial evidence, gaps remain" (→ OFI).
    child_progress:          list[bool] = []
    skipped_count:           int  = 0
    had_derivation_NA:       bool = False
    short_circuit_UNKNOWN_for: Optional[str] = None

    for edge in spec.children:
        # Edge-level applies_when gate
        if not _applies(edge.applies_when, eval_ctx):
            skipped_count += 1
            continue

        target = edge.target

        if isinstance(target, LeafSpec):
            v = leaf_evaluator(target, eval_ctx)
            v.role = edge.role
            leaf_verdicts.append(v)
            child_outcomes.append(v.counts_as_comply)
            child_progress.append(bool(v.items_recognised))

        elif isinstance(target, SpecDescriptor):
            sub = evaluate_spec(target, leaf_evaluator, eval_ctx,
                                spec_resolver, inner_stack, _memo)
            child_outcomes.append(sub.posture == "Comply")
            child_progress.append(sub.posture in ("Comply", "OFI"))
            leaf_verdicts.extend(sub.leaves)

        elif isinstance(target, ControlRef):
            if spec_resolver is None:
                raise RuntimeError(
                    f"ControlRef({target.target_control_id!r}) encountered but no spec_resolver provided"
                )
            try:
                target_spec = spec_resolver(target.target_control_id)
            except Exception as e:
                raise RuntimeError(
                    f"spec_resolver failed to resolve {target.target_control_id!r}: {e}"
                ) from e

            sub = evaluate_spec(target_spec, leaf_evaluator, eval_ctx,
                                spec_resolver, inner_stack, _memo)
            derived_verdicts.append((edge.role, sub))

            if sub.posture == "NotApplicable":
                # Source-framework says this control doesn't apply to this
                # tenant. Edge-skipped — but tracked separately from regular
                # applies_when gating so we can promote empty-after-skip to
                # OFI if all the empty came from derivation N/A propagation.
                skipped_count += 1
                had_derivation_NA = True
                continue

            if sub.posture == "UNKNOWN":
                # Sticky propagation. Once one dependency is UNKNOWN, the
                # parent cannot honestly claim Comply or OFI — short-circuit.
                short_circuit_UNKNOWN_for = target.target_control_id
                break

            if sub.posture == "deferred":
                # Engine can't compose from a deferred dependency (its posture
                # lives in posture_controls.finding, not in the spec walker).
                # Treat as edge-skipped with the same accounting as N/A.
                skipped_count += 1
                had_derivation_NA = True
                continue

            # Comply / OFI: compose into outcome
            counts = (sub.posture == "Comply")

            # scope_items refinement: filter the dep's MUST items down to the
            # ones the deriving framework cares about. Operates at item-level
            # granularity, not leaf-level — Art.32 → A.5.23 might pick out
            # just 'item:A.5.23:personal_data' from a leaf whose ISO checklist
            # also contains 'item:A.5.23:exit' (cloud exit strategy — ISO
            # specific, GDPR doesn't care). The dep contributes Comply iff
            # every in-scope item is recognised on a fresh artifact.
            if target.scope_items is not None and sub.leaves:
                scoped = set(target.scope_items)
                filtered_leaves: list[LeafVerdict] = []
                has_in_scope = False
                for lv in sub.leaves:
                    recognised_in_scope   = [i for i in lv.items_recognised   if i in scoped]
                    unrecognised_in_scope = [i for i in lv.items_unrecognised if i in scoped]
                    if not (recognised_in_scope or unrecognised_in_scope):
                        continue
                    has_in_scope = True
                    filtered_leaves.append(LeafVerdict(
                        leaf_id            = lv.leaf_id,
                        role               = lv.role,
                        evidence_type      = lv.evidence_type,
                        satisfied          = not unrecognised_in_scope,
                        fresh              = lv.fresh,
                        reason             = lv.reason,
                        items_recognised   = recognised_in_scope,
                        items_unrecognised = unrecognised_in_scope,
                    ))
                if has_in_scope:
                    counts = all(flv.counts_as_comply for flv in filtered_leaves)
                    sub.leaves   = filtered_leaves
                    sub.gap_list = _build_gap_list(filtered_leaves)
                # If has_in_scope is False — none of the dep's items matched
                # the scope. Fall back to the sub's own posture (counts already
                # holds sub.posture == 'Comply').

            child_outcomes.append(counts)
            child_progress.append(sub.posture in ("Comply", "OFI"))

        else:
            raise TypeError(
                f"edge target must be LeafSpec, SpecDescriptor, or ControlRef, "
                f"got {type(target).__name__}"
            )

    if short_circuit_UNKNOWN_for is not None:
        verdict = ControlVerdict(
            control_id      = spec.control_id,
            spec_id         = spec.spec_id,
            posture         = "UNKNOWN",
            applies         = True,
            curation_status = spec.curation_status,
            leaves          = leaf_verdicts,
            derived_from    = derived_verdicts,
            reason          = f"derives from {short_circuit_UNKNOWN_for} which is UNKNOWN (not yet curated)",
        )
        if spec.control_id:
            _memo[spec.control_id] = verdict
        return verdict

    posture  = _compose_posture(spec.op, spec.n, child_outcomes, had_derivation_NA, child_progress)
    our_g, tenant_g = _build_gaps(leaf_verdicts, derived_verdicts)
    reason   = _build_reason(spec.op, spec.n, child_outcomes, skipped_count, child_progress)

    verdict = ControlVerdict(
        control_id      = spec.control_id,
        spec_id         = spec.spec_id,
        posture         = posture,
        applies         = True,
        curation_status = spec.curation_status,
        leaves          = leaf_verdicts,
        derived_from    = derived_verdicts,
        our_gaps        = our_g,
        tenant_gaps     = tenant_g,
        gap_list        = our_g + tenant_g,
        reason          = reason,
    )
    if spec.control_id:
        _memo[spec.control_id] = verdict
    return verdict


def _compose_posture(
    op:                 str,
    n:                  Optional[int],
    outcomes:           list[bool],
    had_derivation_NA:  bool = False,
    progress:           Optional[list[bool]] = None,
) -> str:
    """Compose child outcomes (True = Comply) into a parent posture.

    Three-tier output: Comply when the op is fully satisfied, OFI when at
    least one child is fully satisfied (but the threshold isn't met yet),
    NC otherwise — including the case where some children show partial
    evidence but none are fully satisfied. The reviewer approves or rejects
    the NC proposal in Stage-2 just like an OFI proposal — the engine
    doesn't get the last word on what's a formal non-conformity, but it
    does flag "nothing fully done yet" as NC so the queue prioritises
    foundational gaps over later-stage partial-completion polishing.

    The `progress` list runs parallel to `outcomes`: True iff the child has
    ANY evidence (leaf with ≥1 items_recognised, or sub-verdict at
    Comply/OFI). It is NOT used to lift NC → OFI — partial evidence alone
    doesn't earn OFI under the current rule. It is retained for the
    reason-string builder (`_build_reason`) which surfaces "(N with
    partial evidence)" so the partial work is still visible to the
    reviewer, just not promoted in the verdict.

    The empty-outcome branches keep their existing meaning (vacuous Comply
    / all-NA OFI) because they're not "0 of N tried"."""
    if not outcomes:
        # Distinguish two empty-outcome cases:
        # (a) All edges gated off by applies_when=False — defensible vacuous
        #     Comply (the tenant has nothing to fulfil right now).
        # (b) All derived dependencies returned NotApplicable / deferred — the
        #     deriving framework has no implementation pathway for this tenant
        #     via the curated dependencies. OFI is the honest signal: the
        #     parent still applies (e.g. GDPR Art.32 if processing PII) but
        #     every listed implementation route is N/A. The curator either
        #     enumerated too narrowly or this tenant needs a control outside
        #     the catalog.
        if had_derivation_NA:
            return "OFI"
        return "Comply"

    n_sat = sum(1 for o in outcomes if o)

    if op == "ALL":
        if all(outcomes):  return "Comply"
        if n_sat == 0:     return "NC"
        return "OFI"
    if op == "ANY":
        if any(outcomes):  return "Comply"
        return "NC"
    if op == "AT_LEAST_N":
        threshold = n if (n is not None and n >= 0) else 1
        if n_sat >= threshold:  return "Comply"
        if n_sat == 0:          return "NC"
        return "OFI"
    raise ValueError(f"unknown op {op!r}")


def _build_gaps(
    verdicts: list[LeafVerdict],
    derived:  Optional[list[tuple[str, ControlVerdict]]] = None,
) -> tuple[list[str], list[str]]:
    """Build (our_gaps, tenant_gaps) per the Phase-C polite-surface contract.

    Tenant-side gaps are things the tenant can close by uploading or
    refreshing evidence — phrased as neutral observation, never accusatory.
    Our-side gaps are curation incompleteness, an uncurated dependency, or
    an evaluator that doesn't yet handle this evidence_type — phrased in
    first-person plural so we own the gap.

    Gaps from derived sub-verdicts are prefixed with '[via <control_id>]' so
    the reader sees where the gap actually lives. The classification (our vs
    tenant) is preserved through derivation: a tenant gap on A.8.24 stays a
    tenant gap when surfaced via Art.32; an uncurated A.5.30 stays an our-gap."""
    our_gaps:    list[str] = []
    tenant_gaps: list[str] = []

    for v in verdicts:
        if v.counts_as_comply:
            continue
        kind = v.role or v.evidence_type or "artifact"
        if not v.fresh and v.satisfied:
            tenant_gaps.append(f"[{kind}] artifact is stale — past its review window, consider refreshing")
            continue
        if v.items_unrecognised:
            for item in v.items_unrecognised:
                tenant_gaps.append(f"[{kind}] your {kind.replace('_', ' ')} doesn't yet include: {item}")
        else:
            tenant_gaps.append(f"[{kind}] we don't have a {kind.replace('_', ' ')} from you yet")

    for role, sub in (derived or []):
        if sub.posture == "Comply":
            continue
        prefix = f"[via {sub.control_id}]" if sub.control_id else "[via derived]"
        if sub.posture == "UNKNOWN":
            our_gaps.append(f"{prefix} we're still curating the evidence model for {sub.control_id or 'this control'}")
            continue
        # OFI / other non-Comply — cascade by the sub's own classification.
        # Backward compat: older sub-verdicts only have gap_list, no split.
        sub_our    = list(sub.our_gaps)    if sub.our_gaps    else []
        sub_tenant = list(sub.tenant_gaps) if sub.tenant_gaps else []
        if not sub_our and not sub_tenant and sub.gap_list:
            sub_tenant = list(sub.gap_list)
        for g in sub_our:
            our_gaps.append(f"{prefix} {g}")
        for g in sub_tenant:
            tenant_gaps.append(f"{prefix} {g}")

    return our_gaps, tenant_gaps


def _build_gap_list(
    verdicts: list[LeafVerdict],
    derived:  Optional[list[tuple[str, ControlVerdict]]] = None,
) -> list[str]:
    """Backward-compat union of our_gaps + tenant_gaps. New code should
    consume ControlVerdict.our_gaps and ControlVerdict.tenant_gaps directly."""
    our_g, tenant_g = _build_gaps(verdicts, derived)
    return our_g + tenant_g


def _build_reason(
    op:        str,
    n:         Optional[int],
    outcomes:  list[bool],
    skipped:   int,
    progress:  Optional[list[bool]] = None,
) -> str:
    total       = len(outcomes)
    satisfied   = sum(1 for o in outcomes if o)
    op_text     = op if op != "AT_LEAST_N" else f"AT_LEAST_{n}"
    skip_text   = f", {skipped} gated off by applies_when" if skipped else ""
    partial_text = ""
    if progress is not None:
        # children with progress (partial evidence) but not satisfied
        partial = sum(1 for o, p in zip(outcomes, progress) if p and not o)
        if partial:
            partial_text = f" ({partial} with partial evidence)"
    return f"{op_text}: {satisfied}/{total} children satisfied{partial_text}{skip_text}"


# ── Public entry point (skeleton — not yet wired) ─────────────────────────────

def evaluate_control(
    spec:           SpecDescriptor,
    leaf_evaluator: LeafEvaluatorFn,
    eval_ctx:       EvalContext,
    spec_resolver:  Optional[SpecResolverFn] = None,
) -> ControlVerdict:
    """Alias of evaluate_spec at the moment; gives callers a name that matches
    the conceptual unit (a control's verdict) rather than the data structure
    (the spec subtree). Once the Neo4j-driven builder lands in commit 4, this
    will take a control_id + the neo4j driver and build the SpecDescriptor
    before walking it.

    spec_resolver is required only when the spec subtree contains ControlRef
    edges (cross-control derivation)."""
    return evaluate_spec(spec, leaf_evaluator, eval_ctx, spec_resolver=spec_resolver)
