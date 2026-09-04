"""
rag/scoping/applicability.py — Ship 110'.d (2026-09-03).

Applicability derivation: read client_facts + fact_source, apply
deterministic rules, write posture_controls.applicability_status +
applicability_reason for controls that don't apply to the tenant.

Design principles (codified from Ship 110'.a-c discussion):

  · Fact-driven only — no lifecycle_stage coupling. A control is N/A
    because of WHAT the tenant is, not WHERE they are in the journey.
    Ship 107's lifecycle gate stays scoped to notification-producer
    cadence (different concern).

  · Rules fire ONLY when every driving fact is `declared` or `derived`
    in fact_source. `default` facts (never explicitly answered) do NOT
    fire N/A rules — err on showing controls the tenant might need
    until they explicitly declare otherwise. Conservative-in-doubt.

  · Idempotent — safe to re-run at any trigger. Clears previously-
    derived N/A markings, then re-applies rules that currently fire.
    Detects "fact flipped back" cases (control returns to applicable)
    without needing per-rule reversal logic.

  · Human-readable applicability_reason per rule — the sentence a
    tenant or auditor reads when asking "why is this N/A?". Prefixed
    with `[rule_id]` for machine parseability + audit trail.

Triggered by:
  1. Ship 110'.c PUT /api/v1/tenant/facts (per-tenant, sync)
  2. Framework enrolment (per-tenant, sync, post-seed)
  3. Manual admin sweep (per-tenant, on demand)

Not covered here (deferred):
  · Tenant overrides — explicit "no, this DOES apply" that survives
    re-derivation. Needs an applicability_source column ('derived' vs
    'overridden') so this module only clears/re-applies derived rows.
  · Neo4j-based applies_when clauses — rules live in Python for MVP.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


# ── Rule primitives ─────────────────────────────────────────────────

@dataclass(frozen=True)
class TargetScope:
    """A (standard_id, control_ref pattern) filter for posture_controls.

    ref_pattern uses SQL LIKE syntax (`%` wildcard). Rule fires against
    every row matching (tenant_id, standard_id, control_ref LIKE pattern).
    """
    standard_id: str
    ref_pattern: str


@dataclass(frozen=True)
class AppRule:
    """A single applicability rule.

    Fields:
      id             — machine identifier used in applicability_reason
                       prefix + logs. Stable across schema changes.
      driving_facts  — client_facts columns whose value the rule reads.
                       Rule skips if ANY driving fact is at `default`
                       source. This is the conservative-in-doubt guard.
      predicate      — takes a dict of {fact_col: value}, returns True
                       if the rule should fire (mark targets N/A).
      targets        — list of (standard_id, ref pattern) filters.
      reason         — human-readable narrative (prepended with `[id]`
                       so the reader can trace back to this rule).
    """
    id:            str
    driving_facts: tuple[str, ...]
    predicate:     Callable[[dict], bool]
    targets:       tuple[TargetScope, ...]
    reason:        str


# ── Rule registry ───────────────────────────────────────────────────
#
# 11 rules covering the MVP scope-reduction cases most tenants care
# about. Each rule maps a declared/derived fact (or fact combination)
# to a set of (standard_id, control_ref) patterns that should be N/A.
#
# Adding new rules: append here. No schema change required.

RULES: tuple[AppRule, ...] = (

    # ── ISO 27001:2022 physical controls when tenant is cloud-only ──
    AppRule(
        id            = "cloud_only_no_physical",
        driving_facts = ("has_physical_premises",),
        predicate     = lambda f: f["has_physical_premises"] is False,
        targets       = (
            TargetScope("ISO27001:2022", "A.7.%"),
        ),
        reason        = "Cloud-only tenant — physical premises controls do not apply.",
    ),

    # ── ISO 27001:2022 secure-development controls when tenant does
    #    not develop software ─────────────────────────────────────────
    AppRule(
        id            = "no_software_development",
        driving_facts = ("develops_software",),
        predicate     = lambda f: f["develops_software"] is False,
        targets       = (
            TargetScope("ISO27001:2022", "A.8.25"),   # secure dev lifecycle
            TargetScope("ISO27001:2022", "A.8.26"),   # application security
            TargetScope("ISO27001:2022", "A.8.27"),   # secure system arch
            TargetScope("ISO27001:2022", "A.8.28"),   # secure coding
            TargetScope("ISO27001:2022", "A.8.29"),   # security testing
            TargetScope("ISO27001:2022", "A.8.30"),   # outsourced development
            TargetScope("ISO27001:2022", "A.8.31"),   # dev/test/prod separation
            TargetScope("ISO27001:2022", "A.8.33"),   # test information
        ),
        reason        = "Tenant does not develop software — secure-development controls do not apply.",
    ),

    # ── ALL GDPR when tenant does not process personal data ─────────
    AppRule(
        id            = "no_pii_gdpr",
        driving_facts = ("processes_personal_data",),
        predicate     = lambda f: f["processes_personal_data"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.%"),
        ),
        reason        = "Tenant does not process personal data — GDPR does not apply.",
    ),

    # ── ALL ISO 27701 PIMS extensions when tenant does not process
    #    personal data ────────────────────────────────────────────────
    AppRule(
        id            = "no_pii_iso27701",
        driving_facts = ("processes_personal_data",),
        predicate     = lambda f: f["processes_personal_data"] is False,
        targets       = (
            TargetScope("ISO27701:2019", "%"),
        ),
        reason        = "Tenant does not process personal data — ISO 27701 PIMS extensions do not apply.",
    ),

    # ── GDPR territorial scope: no EU AND no UK subjects ────────────
    # Ship 113'.a — kept as (eu, uk) only. The new region columns
    # (us, ca, apac, other) don't affect GDPR — GDPR applies when
    # data subjects are in EU/EEA or UK, regardless of the tenant's
    # own location or other-region subjects.
    AppRule(
        id            = "no_eu_uk_subjects",
        driving_facts = ("eu_data_subjects", "uk_data_subjects"),
        predicate     = lambda f: (
            f["eu_data_subjects"] is False and f["uk_data_subjects"] is False
        ),
        targets       = (
            TargetScope("GDPR:2016/679", "Art.%"),
        ),
        reason        = "Tenant has no EU or UK data subjects — GDPR territorial scope not met.",
    ),

    # ── Controller-specific GDPR articles when tenant is not a
    #    controller. Ship 113'.a dropped the role_joint_controller
    #    guard — the Profile questionnaire no longer surfaces the
    #    joint-controller question (rare + confusing for most
    #    tenants), so the guard would block the rule from ever
    #    firing. Semantically: role_controller=False implies not a
    #    joint controller either (joint is a form of controller).
    AppRule(
        id            = "not_controller",
        driving_facts = ("role_controller",),
        predicate     = lambda f: f["role_controller"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.24"),
            TargetScope("GDPR:2016/679", "Art.24.%"),
            TargetScope("GDPR:2016/679", "Art.25"),
            TargetScope("GDPR:2016/679", "Art.25.%"),
            TargetScope("GDPR:2016/679", "Art.26"),
            TargetScope("GDPR:2016/679", "Art.26.%"),
            TargetScope("ISO27701:2019", "A.7.%"),   # PIMS controller extensions
        ),
        reason        = "Tenant is not a data controller — controller-specific requirements do not apply.",
    ),

    # ── Processor-specific GDPR + ISO 27701 when tenant is not a
    #    processor ───────────────────────────────────────────────────
    AppRule(
        id            = "not_processor",
        driving_facts = ("role_processor",),
        predicate     = lambda f: f["role_processor"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.28"),
            TargetScope("GDPR:2016/679", "Art.28.%"),
            TargetScope("ISO27701:2019", "B.8.%"),   # PIMS processor extensions
        ),
        reason        = "Tenant is not a data processor — processor-specific requirements do not apply.",
    ),

    # ── GDPR Art.9 (special categories) when tenant does not handle
    #    sensitive data ──────────────────────────────────────────────
    AppRule(
        id            = "no_special_category",
        driving_facts = ("special_category_data",),
        predicate     = lambda f: f["special_category_data"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.9"),
            TargetScope("GDPR:2016/679", "Art.9.%"),
        ),
        reason        = "Tenant does not process special category data — Art.9 protections do not apply.",
    ),

    # ── GDPR Art.22 (automated decisions) when tenant doesn't do
    #    automated decision-making ───────────────────────────────────
    AppRule(
        id            = "no_automated_decisions",
        driving_facts = ("automated_decision_making",),
        predicate     = lambda f: f["automated_decision_making"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.22"),
            TargetScope("GDPR:2016/679", "Art.22.%"),
        ),
        reason        = "Tenant does not make automated decisions about individuals — Art.22 does not apply.",
    ),

    # ── GDPR Chapter V (cross-border transfers) when tenant does not
    #    transfer data outside EU/UK ─────────────────────────────────
    AppRule(
        id            = "no_cross_border_transfers",
        driving_facts = ("transfers_data_outside_eu",),
        predicate     = lambda f: f["transfers_data_outside_eu"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.44"),
            TargetScope("GDPR:2016/679", "Art.45"),
            TargetScope("GDPR:2016/679", "Art.45.%"),
            TargetScope("GDPR:2016/679", "Art.46"),
            TargetScope("GDPR:2016/679", "Art.46.%"),
            TargetScope("GDPR:2016/679", "Art.47"),
            TargetScope("GDPR:2016/679", "Art.47.%"),
            TargetScope("GDPR:2016/679", "Art.48"),
            TargetScope("GDPR:2016/679", "Art.49"),
            TargetScope("GDPR:2016/679", "Art.49.%"),
        ),
        reason        = "Tenant does not transfer personal data outside EU/UK — Chapter V does not apply.",
    ),

    # ── GDPR Art.8 (children's consent) when tenant does not process
    #    children's data. Column not exposed in questionnaire yet →
    #    stays at default → rule doesn't fire until curator surfaces
    #    the question. Kept here so a schema addition activates the
    #    rule without a code change. ─────────────────────────────────
    AppRule(
        id            = "no_children_data",
        driving_facts = ("childrens_data",),
        predicate     = lambda f: f["childrens_data"] is False,
        targets       = (
            TargetScope("GDPR:2016/679", "Art.8"),
            TargetScope("GDPR:2016/679", "Art.8.%"),
        ),
        reason        = "Tenant does not process children's personal data — Art.8 does not apply.",
    ),
)


# ── Derivation ──────────────────────────────────────────────────────

@dataclass
class DerivationResult:
    """Outcome of one derivation pass for a tenant."""
    tenant_id:          str
    facts_read:         dict            = field(default_factory=dict)
    rules_evaluated:    int             = 0
    rules_skipped_default: int          = 0   # rule had default-source fact
    rules_fired:        list[str]       = field(default_factory=list)
    controls_cleared:   int             = 0
    controls_na_set:    int             = 0
    per_rule_na_counts: dict            = field(default_factory=dict)


def _fetch_facts(pg_conn, tenant_id: str) -> tuple[dict, dict]:
    """Return (facts_values, fact_source) for the tenant. Facts_values
    is {col: value} for every scoping column; fact_source is the raw
    jsonb dict {col: {source, at, from}}.
    """
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            SELECT processes_personal_data, eu_data_subjects, uk_data_subjects,
                   role_controller, role_processor, role_joint_controller,
                   special_category_data, criminal_conviction_data,
                   childrens_data, automated_decision_making, profiling,
                   large_scale_processing, systematic_monitoring,
                   high_risk_processing, employee_count_250_plus,
                   public_authority, uses_processors, uses_cloud_services,
                   transfers_data_outside_eu, develops_software,
                   has_remote_workers, has_physical_premises,
                   sector, country, employee_count,
                   fact_source
              FROM client_facts
             WHERE tenant_id = %s
             LIMIT 1
        """, (tenant_id,))
        row = cur.fetchone()
        if not row:
            return {}, {}
        cols = [d[0] for d in cur.description]
        facts = dict(zip(cols, row))
        source = facts.pop("fact_source", None) or {}
        return facts, source


def _fact_is_declared_or_derived(fact_source: dict, col: str) -> bool:
    """True when the tenant has explicitly declared (or the system
    derived) a value for `col`. False means the column is at schema
    default and applicability rules must not fire on it.
    """
    marker = fact_source.get(col)
    if not marker:
        return False
    return marker.get("source") in ("declared", "derived", "overridden")


def _clear_derived_na(pg_conn, tenant_id: str) -> int:
    """Clear ALL previously-derived applicability_status='na' rows for
    this tenant. Identified as rows with a non-null applicability_reason
    (our only writer). Manual overrides — when we add them — will use
    a separate applicability_source column so this UPDATE doesn't
    clobber them.
    """
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute("""
            UPDATE posture_controls
               SET applicability_status = 'applicable',
                   applicability_reason = NULL
             WHERE tenant_id = %s::uuid
               AND applicability_status = 'na'
               AND applicability_reason IS NOT NULL
        """, (tenant_id,))
        return cur.rowcount


def _apply_rule(pg_conn, tenant_id: str, rule: AppRule) -> int:
    """Apply one rule — mark matching (standard_id, control_ref) rows
    N/A with reason. Returns number of rows updated (across all target
    scopes for this rule).
    """
    reason_text = f"[{rule.id}] {rule.reason}"
    total = 0
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        for target in rule.targets:
            cur.execute("""
                UPDATE posture_controls
                   SET applicability_status = 'na',
                       applicability_reason = %s
                 WHERE tenant_id  = %s::uuid
                   AND standard_id = %s
                   AND control_ref LIKE %s
                   AND is_active
                   -- Never override a manually-set applicability outcome.
                   -- (Placeholder for future applicability_source column.)
            """, (reason_text, tenant_id, target.standard_id, target.ref_pattern))
            total += cur.rowcount
    return total


def derive_applicability(pg_conn, tenant_id: str) -> DerivationResult:
    """Idempotent per-tenant derivation pass.

    Sequence:
      1. Read client_facts + fact_source.
      2. Clear all previously-derived N/A markings for this tenant.
      3. For each rule, skip if any driving fact is at `default` source;
         else evaluate predicate; if True, apply rule to all target
         scopes.
      4. Commit + return DerivationResult with per-rule counts.

    Caller manages connection lifecycle. Does NOT commit — caller commits.
    """
    result = DerivationResult(tenant_id=tenant_id)

    facts, source = _fetch_facts(pg_conn, tenant_id)
    result.facts_read = facts
    if not facts:
        logger.info("derive_applicability(%s): no client_facts row — no-op", tenant_id)
        return result

    result.controls_cleared = _clear_derived_na(pg_conn, tenant_id)

    for rule in RULES:
        result.rules_evaluated += 1

        # Guard 1: every driving fact must be declared/derived/overridden.
        # If ANY driving fact is at `default`, rule does not fire —
        # tenant hasn't declared enough to safely mark controls N/A.
        if not all(
            _fact_is_declared_or_derived(source, col)
            for col in rule.driving_facts
        ):
            result.rules_skipped_default += 1
            logger.debug(
                "derive_applicability(%s): rule %s SKIPPED (default facts: %s)",
                tenant_id, rule.id,
                [c for c in rule.driving_facts if not _fact_is_declared_or_derived(source, c)],
            )
            continue

        # Guard 2: predicate returns True only when rule should fire
        # (e.g. cloud-only rule fires only when has_physical_premises=False).
        if not rule.predicate(facts):
            continue

        # Fire: mark matching controls N/A with reason
        n = _apply_rule(pg_conn, tenant_id, rule)
        result.rules_fired.append(rule.id)
        result.per_rule_na_counts[rule.id] = n
        result.controls_na_set += n
        logger.info(
            "derive_applicability(%s): rule %s fired → %d controls N/A",
            tenant_id, rule.id, n,
        )

    return result
