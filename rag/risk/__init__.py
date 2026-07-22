"""
Risk-register query + display module.

Ship 14'.c (2026-07-22) — shared between internal
`/api/v1/tenant/risks/*` and external
`/api/external/v1/risks/*` endpoints.

Discipline (from Ship 14'.a addendum):
- Framework role model: `control_refs` renders as a flat list
  spanning program/extension/obligation with role/subject
  metadata attached client-side via `linked_controls_view()`;
  no primary/xfw hierarchy.
- Guidance-normative: response objects are pure data views;
  they never influence engine verdicts.
"""
from rag.risk.queries import (
    RiskRow,
    RiskDetail,
    RiskSummary,
    LinkedControl,
    fetch_risks,
    fetch_risk_detail,
    fetch_risk_summary,
    linked_controls_view,
)

__all__ = [
    "RiskRow",
    "RiskDetail",
    "RiskSummary",
    "LinkedControl",
    "fetch_risks",
    "fetch_risk_detail",
    "fetch_risk_summary",
    "linked_controls_view",
]
