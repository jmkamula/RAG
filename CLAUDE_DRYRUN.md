# CLAUDE_DRYRUN.md

**Retired 2026-08-28 (Ship 100'.c).**

This file described a one-time Ship 48 UX validation exercise where
Claude Code ran ON a fresh dry-run VM in Azure and self-drove the
install + break/diagnose scenarios. That exercise was completed;
its guidance no longer applies to forward customer engagements.

## Forward path

Customer engagements now use the **operator model** — customer owns
the Azure infrastructure, Claude runs on the operator's laptop and
drives the install into the customer VM via SSH:

- **`CLAUDE_OPERATOR.md`** (repo root) — the forward runbook.
  Claude-on-operator-laptop mission brief, phases, safety
  guardrails, handback template.
- **`docs/customer_prep_checklist.html`** — customer-side prep
  before handoff (VM, NSG, `arionops` sudo user, secret channel).
- **`CLAUDE_DEPLOY_GUIDE.md §2.6`** — remote-driving patterns
  (SSH + `scp` + bundle extract idiom).
- **`scripts/ops/remote_diagnose.sh`** — one-command wrapper that
  automates the bundle-retrieval pattern.

## Historical content

The original `CLAUDE_DRYRUN.md` is preserved verbatim at
`docs/history/CLAUDE_DRYRUN.md` for reference — if you're
re-running the Ship 48 UX validation itself (e.g., to re-validate
after a diagnostic-bundle change) or auditing what was done at the
time, read it there.

Do NOT use the historical file as guidance for new customer
installs; use `CLAUDE_OPERATOR.md` instead.
