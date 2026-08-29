---
name: ship-101-prime-a-provider-agnostic-prep
description: Ship 101'.a — customer_prep_checklist.html rewritten provider-agnostic. Two paths (cloud VM / on-prem) with per-path tables where mechanics differ; unified Steps 2-6. On-prem replaces Azure for the PoC path per operator's local-PC deployment shift. Azure-specific language swept from CLAUDE_OPERATOR.md + CLAUDE.md.
metadata:
  type: project
---

# Ship 101'.a — Provider-agnostic prep + on-prem support (2026-08-29)

## Framing

Ship 100'.a's `customer_prep_checklist.html` assumed Azure
throughout. Operator reported the actual PoC target is local
on-prem hardware (Intel i5-6500T / 16 GB RAM / Ubuntu 24.04 boxes)
— on-prem replaces Azure for the PoC path, not just supplements
it.

The install itself is provider-agnostic (`install.sh` doesn't
inspect the environment). The checklist needed to catch up.

## Delivered

### `docs/customer_prep_checklist.html` — rewritten

Structure: same 10-step frame, but Step 1 (provisioning) + Step
2 (firewall) each split into **Path A · Cloud VM** and **Path B
· On-prem / bare-metal** sub-sections.

Step 1 unified spec table at the top (OS, arch, CPU/RAM/disk
minimums, network egress). Then per-path detail:

- **Path A Cloud VM** — 3 sub-tables (Azure / AWS / GCP) with
  the provider-specific parameters (image name / SKU / storage
  type / security-group mechanism)
- **Path B On-prem / bare-metal** — network setup (static IP,
  same-LAN vs VPN vs reverse-tunnel), hardware caveats (ARM
  possible-but-untested, older CPUs work slower, low-RAM
  boxes will OOM), and a physical-security warning ("For
  evaluation only. On-prem PoC boxes rarely have the physical
  security posture required for a production install. Move to a
  hardened environment before real compliance-program data
  lives on the box.")

Step 2 firewall split similarly — cloud console table vs `ufw`
commands. Explicit note that a box behind a corporate router
needs the equivalent rule at the boundary too.

Step 6 handoff-package checklist gained a **Deployment path**
item (cloud provider name or "on-prem") so the operator can
anticipate provider-specific vs on-prem-specific gotchas (proxy,
DNS, corporate CA).

Steps 3-5 + ongoing support + uninstall — unchanged. They were
already provider-agnostic (sudo user, `/data/arioncomply` dir,
secret channel, `diagnose.sh` bundle).

### `CLAUDE_OPERATOR.md` — Azure references generalized

Three edits:

- Header line: "customer's Azure VM" → "customer's Ubuntu 24.04
  host" + explicit "provider-agnostic" callout
- Mission §1: "customer has already provisioned an Azure VM" →
  "provisioned an Ubuntu 24.04 host … cloud VM or on-prem"
- Environment §3 host row: SKU-specific list → spec-first with
  examples per provider + on-prem callout ("Older CPUs
  (Haswell/Broadwell) work; expect slower Chroma reindex")
- "NSG rules" row → "Firewall" row (NSG / security group / ufw
  covered)
- Sample host address in handoff table: Azure-specific hostname
  → cloud + on-prem examples

Most other "VM" references left unchanged — the word is
industry-generic for "the target machine"; adding "VM or host"
everywhere clutters without clarifying.

### `CLAUDE.md` — deployment framing updated

- Line 4: "Compliance RAG platform on Azure VM" → "Compliance
  RAG platform. Currently deployed on the arioncomplyVM dev host
  (Azure). Provider-agnostic install — runs identically on any
  Ubuntu 24.04 host (cloud VM or on-prem)."
- Line 386-ish (operator pointer): "customer's Azure VM" →
  "customer's Ubuntu host (cloud VM or on-prem)"

## What NOT changed

- `install.sh` — genuinely provider-agnostic since Ship 47; no
  code change needed
- `arion_status.sh` — same
- `diagnose.sh` — same
- `docs/poc_install_guide.html` — customer DIY path; still valid
  for cloud VM installs (its banner already points at the prep
  checklist for operator-assisted)
- `docs/dry_run_azure_playbook.html` — retained as historical
  (already banner-labelled from Ship 100'.a)
- `docs/history/CLAUDE_DRYRUN.md` — historical, unchanged

## Codified lessons

**Lesson 162: Application-level provider-agnosticism doesn't
guarantee doc-level provider-agnosticism.** `install.sh` works
identically on Azure / AWS / GCP / on-prem because it never
inspects the environment. But the prep checklist was written
Azure-first because that's what the first customer looked like.
Later shifts to other providers (or on-prem) find the code
correct but the docs wrong. Rule: when the code is provider-
agnostic, express that in the docs by leading with the
provider-agnostic spec and using per-provider tabs/sections
for mechanics — not by picking one provider as the default.

**Lesson 163: On-prem PoC boxes carry a physical-security
warning the cloud path doesn't need.** A cloud VM inherits the
provider's data-center controls (audited access, hardware
inventory, tenant isolation). An on-prem box in an unlocked
office doesn't. The docs need to say so explicitly at the
on-prem section — not because ArionComply's installer changes,
but because compliance-program data lands on a box whose
physical posture may be inappropriate for it. Rule: when
documenting deployment targets, call out which controls the
customer inherits vs which they now own — provider changes
shift that boundary.

## Deferred

- Test-drive the on-prem path on the operator's actual local
  box (`arionlabs-dr-01`, i5-6500T, 16 GB RAM). Validates that
  Chroma reindex + Neo4j load complete OK on Haswell/Broadwell-
  era silicon. First real usage will surface any doc gaps.
- Per-provider deep-dives if a customer needs them (AWS
  security-group console screenshots, GCP firewall rules with
  network-tag targeting, etc.). Currently pointed at with a
  short table; expand as demand emerges.

## Related

- [[ship-100-prime-a-operator-runbook]] — the arc this refines
- [[ship-100-prime-c-retire-dryrun]] — Ship 100' arc close
- `CLAUDE_OPERATOR.md` — updated in this arc
- `docs/customer_prep_checklist.html` — rewritten in this arc
- `CLAUDE.md` — deployment framing updated in this arc
