---
name: ship-47-prime-e-vm-appliance-design-2026-07-27
description: "Ship 47'.e appendix — VM appliance deployment options. Four paths from lightest-touch to most polished: (1) cloud-init user-data wrapping install.sh, (2) baked disk image (VHD/AMI/OVA) via Packer, (3) Terraform module, (4) cloud-marketplace listing. Recommend #1 for POC-scale; #2 becomes worthwhile once we have >5 customer installs."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 47'.e appendix — VM appliance deployment. Complements
Ship 47'.a's install.sh strategy with the "click deploy" path.

## The question

install.sh works, but it still asks the operator to <em>choose an image,
provision a VM, SSH in, git clone, run the script</em>. Can we ship
something more appliance-shaped where the operator just gets a
running ArionComply from a single "deploy" action?

## Four paths

### 1. cloud-init user-data — wrapping install.sh
Any cloud vendor supports <code>user-data</code>: a script that runs on first
boot. Ours becomes a small bootstrap:

```bash
#!/bin/bash
apt-get update && apt-get install -y git
git clone https://github.com/jmkamula/RAG.git /data/arioncomply
cd /data/arioncomply
ARION_OWNER_PW='${arion_owner_pw}' \
  ARION_APP_PW='${arion_app_pw}' \
  NEO4J_PW='${neo4j_pw}' \
  OPENAI_KEY='${openai_key}' \
  bash deploy/install.sh --yes
```

Customer copies this into their cloud console (Azure "Custom data",
AWS "User data", GCP "Startup script"), fills in the four variables,
provisions any Ubuntu 22.04+ VM, and gets a running ArionComply
~15 minutes later.

**Pros**: zero new infrastructure on our side. Works everywhere.
Portable across clouds. No image maintenance burden.
**Cons**: first-boot install is slow (~15 min). Customer sees "not
ready" state for that window. `apt install` dependent on their
network policy.
**Effort**: 1 day. Mostly Terraform/CloudFormation snippet templates
for each cloud + docs.
**Recommended for**: POC installs, single-customer pilots.

### 2. Baked disk image (VHD / AMI / OVA) via Packer
[Packer](https://www.packer.io) runs the installer on a base Ubuntu
image, snapshots the result, and outputs a cloud-specific image
format. Customer's VM boots straight into a ready ArionComply — no
apt install on first boot.

**Pros**: fast first boot (~1 min from VM start to API ready).
Deterministic image content. Signed image gives supply-chain assurance.
**Cons**: per-cloud image maintenance (Azure VHD, AWS AMI, GCP image,
VMware OVA). Image staleness — need to rebuild on every codebase
change or apt security update. Storage costs for image hosting.
**Effort**: 1 week for the first cloud (Azure). +2-3 days per
additional cloud. +ongoing rebuild cadence.
**Recommended when**: >5 customer installs OR customers require
"golden image" audit trail.

### 3. Terraform module
A `terraform-arioncomply-vm` module that provisions the VM +
attaches the cloud-init from option 1 or references the image from
option 2. Customer's IaC treats ArionComply as a managed resource.

**Pros**: integrates with customer's existing IaC discipline.
Idempotent — running `terraform apply` again is a no-op if unchanged.
**Cons**: only helps customers who already do Terraform. Doesn't
address the install path itself — it's a wrapper.
**Effort**: 2-3 days. Best done alongside option 1.
**Recommended alongside**: option 1 for Terraform-native customers.

### 4. Cloud-marketplace listing
Azure Marketplace, AWS Marketplace, GCP Marketplace. Customer
searches "ArionComply", clicks Deploy, fills in a form, gets a
running instance. Billing can pass through the cloud vendor.

**Pros**: sales channel + discoverability + billing integration.
Perceived-trust boost (vetted by the vendor).
**Cons**: substantial application + review process per vendor
(weeks). Requires option 2 (baked images) as a prerequisite.
Ongoing vendor compliance work.
**Effort**: 2-4 weeks per vendor.
**Recommended when**: mature product with >20 customers + a proper
GTM motion.

## Recommendation

Right now (Ship 47 target: POC installs for known customers):
**start with option 1 — cloud-init user-data.**

- Wraps `install.sh` in a template any cloud console accepts
- No new infrastructure on our side
- Same code path as manual install, so bug reports translate directly
- Upgrades to option 2 later without breaking existing installs

Ship 48 or later could add a Packer pipeline (option 2) once we
have enough installs to feel the pain of first-boot install time.

## Sketched artefacts (would go in Ship 47'.g if we do this)

```
deploy/
├── install.sh                        # existing (Ship 47'.c)
├── postgres_preamble.sql             # existing
├── requirements.txt                  # existing
├── .env.example                      # existing
└── cloud-init/
    ├── user-data.tpl                 # template with ${arion_owner_pw} etc
    ├── azure-vm.tf                   # Terraform provisioning Ubuntu + our user-data
    ├── aws-ec2.tf
    └── gcp-vm.tf
```

Each cloud-specific `.tf` is ~30 lines. The `user-data.tpl` is ~25 lines.

## What we'd deliberately skip for POC-scale

- **Multi-region orchestration** — one VM per install, single region
- **HA / clustering** — single VM handles POC load fine
- **Autoscaling** — same
- **Signed / attested images** — option 2's job later
- **Marketplace listings** — option 4's job later
- **Kubernetes packaging** (Helm chart) — different shape entirely,
  not appropriate for single-VM POC

## Related

- Ship 47'.a (POC install baseline design) — the design memo
  install.sh implements
- Ship 47'.c (install.sh) — the script this appliance work wraps
- Ship 46 deployment discussion — the shape trade-off analysis
