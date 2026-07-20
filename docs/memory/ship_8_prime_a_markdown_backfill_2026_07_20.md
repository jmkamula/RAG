---
name: ship-8-prime-a-markdown-backfill-2026-07-20
description: "Ship 8'.a — one-shot backfill for markdown-escape artifacts in stored posture + document_findings prose"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 8'.a (2026-07-20) — closes the DB-side counterpart of the
Ship 7'.d markdown-escape fix.

## Motivation

Ship 7'.d added `strip_markdown_escapes` to the output gateway's
`stage2_reason`, `evidence_prose`, and `cascade_rationale`
surface chains. That fixed the extractor-artifact leak at
serialization — every external API + Evidence Package + Stage-2
response now renders cleanly.

But the DB rows themselves still contained `\-`, `\(`, `\.`
artifacts. Any code path NOT routed through the gateway (admin
psql queries, support tooling, log lines, older internal
surfaces) still saw them.

## What shipped

- **`scripts/backfill_markdown_escapes.py`** — one-shot script.
  Reads rows matching a Postgres regex mirroring
  `_MD_ESCAPE_RE`, applies `strip_markdown_escapes` in Python
  (guaranteeing identical semantics with the gateway
  transform), UPDATEs. Idempotent — safe to re-run; post-scrub
  rows match no more.
- **`--dry-run`** flag for pre-application verification.
- **`--tenant`** flag for per-tenant scoping.

Tables backfilled:
- `posture_controls.gap_description` + `.action_required`
- `document_findings.excerpt`

Uses the `arioncomply` superuser to bypass RLS (script runs
under ops/admin credentials, not tenant-scoped app user).

## Run outcome

    posture_controls:  scanned=   18  updated=   18
    document_findings: scanned= 1110  updated= 1110

Total: 1128 rows scrubbed across the demo tenant. Idempotence
verified by re-running dry-run — 0 rows matched post-fix.

## Sample verification

Before:

    B.8.5.1 | OFI | Verpex processes: \- Server log data
        \(IP addresses, browser information, timestamps\) \- ...

After:

    B.8.5.1 | OFI | Verpex processes: - Server log data
        (IP addresses, browser information, timestamps) - ...

Reads naturally in psql + admin panels + any code path.

## Design note — same regex, two forms

The Postgres regex `\\[-().*+_\[\]!|<>#{}\`~]` is used only as
a WHERE filter to find candidate rows cheaply. The actual scrub
uses the Python `strip_markdown_escapes` transform to guarantee
identical semantics with the runtime gateway. If the regex is
too permissive (false positive rows), the Python pass is a
no-op and the row is skipped — safe. If it's too restrictive
(false negatives), those rows survive to a future re-run.

## Baseline

Full eval running with the 27701 expansion (Ship 8'.b) — this
backfill is data-only, no eval impact.

## Related

- [[ship-7-prime-d-evaluation-checkpoint-2026-07-19]] — the
  transform this backfill applies
- [[ship-7-prime-a-output-audit-2026-07-19]] — parent output-
  gateway arc
