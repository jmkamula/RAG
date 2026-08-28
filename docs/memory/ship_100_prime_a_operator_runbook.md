---
name: ship-100-prime-a-operator-runbook
description: Ship 100'.a — new CLAUDE_OPERATOR.md replaces CLAUDE_DRYRUN.md forward. Codifies the Claude-on-operator-laptop / customer-owns-Azure model. New customer_prep_checklist.html carries the customer-side prep (VM, NSG, arionops user, secret channel). Existing HTML playbooks get header notes redirecting to the new path.
metadata:
  type: project
---

# Ship 100'.a — Claude operator runbook + customer prep checklist (2026-08-28)

## Framing

The Ship 48 dry-run codified a "Claude runs ON the fresh VM,
self-drives Phase 1/2, writes a report" model in
`CLAUDE_DRYRUN.md`. That was a one-time validation.

For real customer engagements the boundary is different:

- **Customer owns Azure infra** — VM provisioning, NSG,
  operator SSH user, /data/arioncomply directory
- **Claude operator on their laptop** — SSH into customer VM,
  drive `install.sh --yes`, provision tenant, smoke test,
  deliver handback + credentials via customer's secret vault

Nothing about the ArionComply install itself changed. What
changed is the **actor model** around it.

## Delivered

### `CLAUDE_OPERATOR.md` (new, replaces DRYRUN forward)

Structured for Claude Code sessions running on an operator
laptop. Nine sections:

1. Mission — Claude on laptop, customer VM as target
2. Handoff acceptance — 7-item minimum before touching the VM
3. Environment — laptop scratch layout + expected VM state
4. Phases — Connect+install / Tenant+smoke / Troubleshoot /
   Handback
5. State + report files — `state.md` (private) +
   `handback.md` (customer-facing)
6. Handback template — copy-paste artifact structure
7. Safety guardrails — dry-run rules PLUS "customer's live
   system" additions (never share creds via email/chat, confirm
   before restart, etc.)
8. Escalation criteria — two-attempt rule, credential-at-risk
   trip, time budgets
9. Handback finalize — encrypted archive OR wipe of local
   scratch

Key differences from `CLAUDE_DRYRUN.md`:

- All command patterns are `ssh arionops@<vm-ip> ...` +
  `scp` for bundle retrieval — never local execution
- Credentials pattern: `credentials.private` scratch file,
  then customer's secret-vault, then delete
- Handback doc is customer-facing (redacted, no raw keys)

### `docs/customer_prep_checklist.html` (new)

Customer-side prep BEFORE handoff to the operator. 10-step
table + detailed sections:

1. Provision Azure VM (Ubuntu 24.04, D4s v3, admin user)
2. NSG rules (SSH from operator IP only; no public 8080)
3. Create `arionops` sudo user with operator's SSH pubkey
4. Prep `/data/arioncomply` directory
5. Choose secret-delivery channel (vault, NOT email/chat)
6. Send handoff to operator (connection info + creds via vault)

Plus "what happens next" summary of the operator's work, and
uninstall + user-rotation snippets.

Written for a customer security or IT team member — not a
compliance specialist. Assumes Azure portal familiarity, no
ArionComply-specific knowledge.

### Existing HTML playbooks — redirect banners

Two edits — hero-section header note in each:

- `docs/poc_install_guide.html` — banner: "This is the DIY
  path. For operator-assisted, see Customer Prep Checklist"
- `docs/dry_run_azure_playbook.html` — banner: "Historical.
  Forward engagements use Customer Prep Checklist +
  CLAUDE_OPERATOR.md"

No content edited; both remain valid for their original
audience. The banners route new readers to the right doc.

## What NOT changed

- `deploy/install.sh` — already has `--yes` mode + env-var
  contract, works for remote-driving as-is
- `scripts/ops/diagnose.sh` — already portable, bundle path
  is stable
- `CLAUDE_DEPLOY_GUIDE.md` — troubleshooting playbook unchanged
  in scope; Ship 100'.b will add a remote-diagnose pattern
- `CLAUDE_DRYRUN.md` — kept as historical reference; not
  deleted, marked as such via CLAUDE_OPERATOR.md §Related

## Codified lessons

**Lesson 156: When the actor model changes, docs need
splitting, not editing.** DRYRUN.md was a coherent doc for
ONE actor (Claude on VM). Trying to squeeze in a second
actor (Claude on laptop) would have muddled it. Fresh
document per actor pattern is clearer + tolerates future
model shifts. Rule: when you find yourself hedging with
"if you're X do Y, if you're Z do W" across a doc, split
into two docs each written for a single-actor mental model.

**Lesson 157: Customer-facing checklists want checkbox
semantics + explicit NOT-acceptable lists.** The customer
prep checklist uses `☐` boxes for the handoff items and
explicit "NOT acceptable" lists (email/chat/SMS) for
secret-delivery. This is because customer readers are
compliance-conscious and want to verify each item. Rule:
customer-facing docs that gate handoff should render as
a checklist a reader can walk down + physically check,
not as prose the reader has to interpret.

## Deferred (Ship 100'.b / .c)

- **Remote-diagnose pattern in `CLAUDE_DEPLOY_GUIDE.md`** —
  add a §2.3 showing SSH → run diagnose.sh → scp → read
  locally. Small.
- **`scripts/ops/remote_diagnose.sh` wrapper** — optional
  helper that automates the SSH+scp+extract, callable as
  `bash scripts/ops/remote_diagnose.sh <vm-ip>`. Nice to
  have, not required.
- **Handback template refinement** — after first real
  customer engagement, iterate on what fields the customer
  actually cares about vs what's ceremony.
- **Retire `CLAUDE_DRYRUN.md`** — after 100'.b + 100'.c
  land, DRYRUN's forward guidance is fully subsumed. Move
  to `docs/history/` or delete.

## Related

- [[ship-48-prime-a-deployment-diagnostics-design-2026-07-28]]
  — Ship 48'.a foundational deployment diagnostic UX this
  runbook coordinates
- `CLAUDE_OPERATOR.md` — the runbook itself (this arc)
- `docs/customer_prep_checklist.html` — customer-side prep
  (this arc)
- `docs/poc_install_guide.html` — customer DIY install
  (banner updated this arc)
- `docs/dry_run_azure_playbook.html` — historical Ship 48
  validation (banner updated this arc)
- `CLAUDE_DEPLOY_GUIDE.md` — troubleshooting playbook
  (unchanged in this arc; 100'.b will add remote-diagnose)
- `CLAUDE_DRYRUN.md` — retired forward, kept as history
