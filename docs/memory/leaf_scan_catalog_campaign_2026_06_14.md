---
name: leaf-scan-catalog-campaign-2026-06-14
description: "SHIPPED 2026-06-14 across 10 batches: leaf-scan catalogs from 9 → 246 (1.4% → 38.4% coverage of multi-leaf catalog). A.5 fully closed (37/37); A.6/A.8/ISMS-clause/GDPR subsets covered as Phase-1-retirement recovery. Generator v3 added trigrams + suppressed singletons. End-game: 18 per-MUST back-bindings on Arion across 9 controls; insufficient depth on any leaf to flip a control from NC."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

A one-day campaign to scale leaf-scan catalog coverage from
pilot to broad, driven by the Phase-1 retirement surge.

## Numbers

- Catalogs: 9 → 246 (1.4% → 38.4% of 641 multi-leaf leaves)
- Controls fully scanned: 3 → 65 (A.5.16/A.5.18/A.6.3 → entire A.5 + selected A.6/A.8/ISMS-clause/GDPR)
- MUSTs covered: ~50 → ~1460
- Author rate: ~3-7 min per leaf with v3 generator
- Wall-clock: ~half a day across 10 commits

## Generator v3

`scripts/gen_leaf_scan_catalog.py` upgraded mid-campaign:
- Trigram emission alongside bigrams (stronger anchors)
- `_NEVER_EMIT_SINGLETON` set (50+ generic tokens — user, account,
  identity, status, owner, etc.) — never emitted as standalone
  fingerprint sets
- `_ROLE_PREFIX_HINTS` by item-id prefix (reg_/rev_/scope_/pol_)
- Multi-token evidence-type scaffolds

Result: skeleton output flipped from ~50% noise to ~10% noise.
Reviewer effort cut roughly in half.

## Pattern-by-evidence-type playbook

Validated across 246 catalogs:

- **Register leaves**: column-header anchors (`[X, column]`,
  `[per, row, X]`, `[per, entry]`). Avoid singletons.
- **Record leaves** (revocation/disposal/closure/etc.): active-voice
  past-tense (`[was, revoked]`, `[record, for]`). Cross-reference
  to the lifecycle source (A.5.16 ↔ A.5.18 etc.).
- **Procedure leaves**: domain vocabulary distinct from policy
  prose. Cross-refs to specific controls (`A.5.X`, `Art.Y`) when
  the procedure mandates linkage.
- **Review record leaves**: audit-output vocabulary (findings,
  sample, outliers, root cause).
- **Scope notes**: enumeration markers + sectoral / jurisdictional
  identifiers (DPF / SCCs / MS law).
- **Policy leaves**: cross-references to ISO sub-controls or GDPR
  sub-articles as strong anchors.

## Cross-control anchor convention

Many MUSTs explicitly reference sibling controls (e.g.
`item:A.5.16:authn_link` → A.5.17 credential lifecycle).
Adopting the convention of putting `["A.5.17"]` as a fingerprint
makes those cross-refs **detectable** in policy/procedure text
that cites the related control by number — a strong, low-false-
positive anchor.

## False-positive class learned

`reg_X` keywords like `[user, id]`, `[employee, id]` MATCH POLICY
TEXT, not register rows. The first A.5.16 review uncovered this;
generator v3 NEVER_EMIT_SINGLETON list removed it at source.
Per-row markers required: `[id, column]`, `[per, row, id]`.

## What still didn't recover

On Arion, even with 35 catalogs deployed and leaf-scan run:
- 18 per-MUST back-bindings produced
- BUT zero controls reverted from NC → OFI
- Because Arion's evidence is genuinely thin at the per-MUST
  level (1-2/N per leaf, never N/N)

This validated [[feedback-phase-1-fallback-masks-gaps]] at scale —
Phase-1 was masking real depth gaps, not just labelling gaps.

## Operational gap remaining

Leaf-scan is still CLI-only. To deploy:
1. Wire into the post-Stage-1-approval trigger (currently the
   engine-kick reloads but doesn't auto-back-bind)
2. Cron sweep for tenants with stale findings
3. Admin endpoint for manual back-bind on a specific control

## Related

- [[feedback-phase-1-fallback-masks-gaps]] — the architectural
  finding that drove this campaign
- [[leaf-driven-scan-pilot-2026-06-12]] — the original pilot
  patterns this campaign scaled
- [[curation-phase-b-retrospective]] — sibling arc: multi-leaf
  control curation (118 ISO + 50 GDPR) finished 2026-06-02
- [[feedback-intake-label-unreliability]] — strategic frame:
  per-MUST evidence is the trustworthy signal
