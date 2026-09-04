# Deployments log

Every ArionComply install we operate has a markdown file here recording
what's been shipped, when, and any per-deployment context (test data,
credentials location, known gotchas). The file is the **dev-side view**
of the deployment — updated **before** we run the ssh commands, so that
a fresh Claude session can pick up the arc by reading this directory.

Complements the **PoC-side view** on each customer VM
(`/data/arioncomply/.deployment_log.jsonl`), which is machine-parseable
and appended by `deploy/install.sh` on every run.

**Full step-by-step guide**: see [`PLAYBOOK.md`](PLAYBOOK.md) — the
canonical playbook for fresh install + per-arc updates + golden image
audit + recovery scenarios. The rest of this README is the deployment-
log convention (file naming + row shape + query patterns).

## Naming convention

One file per deployment target: `<hostname-or-nickname>.md`.
Committed to git alongside the code changes they describe.

## File shape

Each file has three sections:

1. **Deployment record** — table of installs / updates in chronological
   order (most recent last). One row per `install.sh` run.
2. **Context** — VM specs, network access, credential-vault location,
   ownership.
3. **Ship history** — brief per-arc note on what shipped + verification
   status, cross-linked to `docs/memory/ship-N-prime-*` retros.

## Use pattern

- **Before running ssh commands**: update the deployment record row with
  planned action + timestamp.
- **After the ssh commands succeed**: mark the row's outcome (`GREEN`)
  and note anything surprising in the Ship history.
- **When something fails**: mark the row `RED`, note the failure in the
  Ship history, and file a follow-up task.

The PoC-side JSONL log is authoritative for _what actually ran_;
this markdown is authoritative for _what we intended + why + what to
watch for_.

## Reading the PoC-side log

`.deployment_log.jsonl` on each customer VM is one JSON object per
`install.sh` run. Query patterns from an operator laptop:

```bash
# Everything, human-readable
ssh arionops@10.0.1.85 'jq . /data/arioncomply/.deployment_log.jsonl'

# Most recent 5 runs, compact table
ssh arionops@10.0.1.85 \
  "jq -r '[.ts,.git_sha,(.migrations_applied|length|tostring)+\" migs\",.outcome] | @tsv' \
   /data/arioncomply/.deployment_log.jsonl | tail -5"

# Any RED outcomes ever
ssh arionops@10.0.1.85 \
  "jq -c 'select(.outcome != \"GREEN\")' /data/arioncomply/.deployment_log.jsonl"

# What SHAs has this box seen?
ssh arionops@10.0.1.85 \
  "jq -r '.git_sha' /data/arioncomply/.deployment_log.jsonl | sort -u"
```

## Future automation (Ship 112'+)

A future automated deploy script will read both logs, compute the delta
between "dev-side intent" and "PoC-side actual", and ship only the
missing pieces with verification between each step.
