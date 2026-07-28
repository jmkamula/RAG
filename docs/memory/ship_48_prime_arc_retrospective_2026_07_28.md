---
name: ship-48-prime-arc-retrospective-2026-07-28
description: "Ship 48' arc retrospective — deployment diagnostics + Claude-Code ops playbook. 5 sub-arcs across one session. 4 debug surfaces: scripts/ops/diagnose.sh bundle, docs/error_catalog.html (26 codes), /api/v1/admin/deployment/status endpoint, CLAUDE_DEPLOY_GUIDE.md. Enables AI-assisted troubleshooting of any customer deployment without SSH. Codified: AI-first ops = design artefacts for AI consumption, humans benefit as side effect."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 48' arc retrospective — deployment diagnostics complete.

## What shipped

5 sub-arcs over one session (2026-07-28). Direct follow-on to Ship 47's
POC install path. Motivating question: once we have N customer installs
of Ship 47, how does support (human OR Claude Code) diagnose a broken
one without SSH into each?

| Sub-arc | Delivery | Commit |
|---|---|---|
| 48'.a | Design memo — four debug surfaces + Claude-Code-first support model | 3472316 |
| 48'.b | `scripts/ops/diagnose.sh` (bundle generator) + `docs/error_catalog.html` (26 initial codes) | bc48829 |
| 48'.c | `/api/v1/admin/deployment/status` endpoint + `rag/admin/deployment_status.py` module | 24f9b9e |
| 48'.d | `CLAUDE_DEPLOY_GUIDE.md` + `CLAUDE.md` cross-link | d2d99b9 |
| **48'.e** | **This retro** | pending |

## The four surfaces working together

**Support flow with a broken install** (target user experience):

1. Customer emails: "chat is slow, dashboard shows no evidence"
2. Customer runs `bash scripts/ops/diagnose.sh` — one command
3. Customer uploads the 20KB `arion-diag-*.tar.gz`
4. Support opens Claude Code with:
   - `CLAUDE_DEPLOY_GUIDE.md` in context (system prompt equivalent)
   - Extracted tarball on disk
5. Prompt: "Look at ./arion-diag-*.tar.gz — customer reports chat slow, no evidence."
6. Claude reads `deploy_state.md` first (systemd + ports), spots
   `otel_enabled=0` in `env.redacted.txt`, checks `tenants.txt`
   → posture_controls empty, cross-references
   `docs/error_catalog.html` → `ARION-RUNTIME-002` + `ARION-RUNTIME-005`,
   returns two-line diagnosis + fix commands.

**Total time from tarball to answer: seconds. No SSH needed. Privacy
stays under customer control** (they chose what went in the bundle).

## Delivery velocity

- Session length: ~2.5 hours
- 4 substantive surfaces + retro
- Each sub-arc committed independently; zero mid-arc rollbacks
- Every implementation verified on the demo VM before commit

## Key decisions

### AI-first support model
Everything designed for AI consumption; humans benefit as a side
effect. This inverts the traditional docs model where humans are
primary. Rationale:
- `CLAUDE_DEPLOY_GUIDE.md` structured as a lookup table (Section 3),
  not narrative prose
- Diagnostic bundle files are plain text tables + JSON, not screenshots
  or interactive dashboards
- Error codes are stable identifiers (`ARION-INSTALL-005`) so Claude
  can pattern-match instead of re-parsing symptoms every time
- Every fix instruction is a copy-pasteable command line, not an
  imperative sentence

### Structured over unstructured
Bundle files use consistent formatting:
- Section headers: `=== <name> ===`
- Command echo: `$ <cmd>` above the output
- Machine-friendly counts (`  RequirementNode: 478`)
- Deterministic file ordering across bundles

This makes cross-bundle diff-ing possible ("what changed between the
customer's bundle from Monday and Tuesday?") without custom tooling.

### Privacy by omission, not by filter
Bundle contents are explicitly listed in `diagnose.sh` — no "kitchen
sink" collection with a runtime PII filter. Adding a new file to the
bundle requires editing the script (visible in code review). This
scales safely: we can't accidentally leak content we didn't
explicitly opt in to collect.

### Stable error codes
Once assigned (`ARION-INSTALL-005` — Neo4j warmup race), a code is
never reused. Retired codes carry `[RETIRED]` marker in the catalog.
Rationale: Claude sessions from a year ago should still recognize
`ARION-INSTALL-005` and produce the same diagnosis.

### Non-fatal probes, degraded reporting
Every probe in the diagnostic bundle + status endpoint fails
gracefully. If Chroma is unreachable, `chroma.txt` says `(chroma
probe error: ...)` — the bundle still generates. Same for the
endpoint: services[chroma]="unreachable" instead of a 500.
Rationale: a broken deployment must still be able to produce a
diagnosis of itself.

## Codified 4 lessons

### 1. AI-first ops docs are a real design surface
Historical instinct: "docs are for humans; AI reads what humans read."
Ship 48 inverts that. When your primary support channel is AI-assisted,
you can pack much denser structured data into a Markdown file (Section
5 of the playbook has a 20-row lookup table) without hurting utility
— humans can still scan it, and Claude parses it perfectly.

**Rule**: when writing a doc that will be dropped into AI context,
prefer tables over prose, stable identifiers over descriptive names,
and copy-pasteable commands over imperative language.

### 2. Diagnose runs on the customer's terms
An earlier draft had `diagnose.sh` upload directly to our support
server. Reversed to "bundle to /tmp; customer uploads if they want."
Rationale: customers with strict egress policies still need to be
able to run the diagnostic. Making egress optional broadens the tool's
applicability without giving anything up on our side.

**Rule**: never assume egress. Design diagnostics that work
completely offline; add optional convenience for customers who allow
outbound connections.

### 3. RLS bypass isn't portable — count with proxies
`_tenant_summary()` initially tried `SET LOCAL row_security = off`
to enumerate the `tenants` table. That requires owner privileges the
API pool role doesn't have — degraded to `count=null`. Switched to
`count(DISTINCT tenant_id) FROM posture_controls`, which is (a)
allowed by RLS on this table, (b) a more meaningful metric anyway
("onboarded tenants with evidence" ≥ "rows in tenants table").

**Rule**: when an admin-view aggregate is blocked by RLS, look for
a proxy metric on a less-restrictive table. Often more meaningful
than the "true" count.

### 4. AI ops feedback loop — codify one code per real incident
The 26 initial codes in `error_catalog.html` are entirely
retrospective — every one names a bug we've hit at least once in
Ship 1-47's history. New codes should be added only after
encountering a real symptom. Speculative codes rot.

**Rule**: don't populate the catalog with hypothetical failure
modes. Add codes when a customer (or eval, or measurement run)
surfaces a new failure. The catalog stays honest that way.

## What Ship 48 did NOT do

- **Automated remediation** — every fix in the catalog is a
  prescriptive command the operator runs. No self-healing.
- **Live remote debugging** — no SSH tunnel management, no
  reverse-connect debugger, no shared observability dashboard.
  Bundle-based is the design boundary.
- **PII scanning** — bundle contents are hand-curated to exclude
  PII by design; no runtime scanner.
- **Fleet view across N deployments** — every install is its own
  island. Multi-install fleet management is a much bigger arc
  (control plane, per-install callback, aggregated OTel).
- **Diagnostic-bundle-driven ticketing** — no automatic Zendesk /
  Linear / Slack integration. Operator manually forwards.
- **Chat log capture** — deliberately excluded. May contain
  proprietary tenant context; not appropriate for support bundles.
- **Alert routing** — status endpoint is pull; no push
  notifications on service degradation.

## Deferred / follow-on candidates

### Ship 49 candidates
- **`--upload-to` flag on diagnose.sh** — optional convenience:
  after generating the tarball, POST to a customer-configured
  webhook. Preserves offline default.
- **Bundle diff tool** — `arion-diag-diff.py <old.tar.gz>
  <new.tar.gz>` — highlights what changed between two bundles from
  the same install. Useful for "what regressed since Monday?"
- **Status endpoint in SPA** — `/ui/arioncomply.html` currently has
  no admin-status widget; a small panel showing service health +
  version + tenant count would help operators without needing curl.
- **New error codes as they surface** — as customers hit real issues,
  each becomes a catalog row. Cadence: add 1-2 codes per real support
  incident.

### Longer-term (Ship 50+)
- Aggregated OTel collector we operate — customer sets
  `OTEL_EXPORTER_OTLP_ENDPOINT` at us; we get real-time traces.
  Massive privacy discussion first.
- Bundle vault — customer emails tarball to `support@arion...`;
  auto-decompress + summarize + link into support system.
- Cross-deployment fleet dashboard — one per customer install;
  our team sees aggregate health.
- Container / K8s parallel — `kubectl exec` variant of `diagnose.sh`
  when we support K8s deployments.

## Related

- Ship 47 (POC install path — this arc's motivating context)
- Ship 44 (OTel dual-backend — one observability surface this
  playbook cross-references)
- Ship 46 (demo prep — where "how do we support N deployments?"
  was raised)
- `scripts/ops/diagnose.sh` — the bundle generator
- `docs/error_catalog.html` — the code catalog
- `CLAUDE_DEPLOY_GUIDE.md` — the AI playbook
- `rag/admin/deployment_status.py` — the status endpoint module

## Ship 48' arc closed

**Baseline**: eval + core paths unchanged. All 4 surfaces additive.

Deployment support model established: **AI-first, offline-safe,
customer-controlled**. Every install ships with the tools to
diagnose itself + the AI playbook to interpret those diagnostics.

Scales to N customer installs without N-times the support burden.
