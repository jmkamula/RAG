---
name: ship-21-prime-arc-retrospective-2026-07-23
description: "Ship 21' arc closer — retired ↳ Compliance facts footer + polished answer_text markdown reconstruction; auditor trail preserved via chat_casefile_log.repair_events + SQL script; 231/232 baseline held"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 21' arc retrospective — 3 sub-arcs across one day
(2026-07-23) retiring the `↳ Compliance facts:` prose footer
and polishing the reconstructed `answer_text` from structured
into clean markdown. Direct follow-on to Ship 20 which made
every chat path emit `answer_structured` — the footer was
structurally redundant with `related[]` cards.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 21'.a | Design memo + auditor query SQL + 30d evidence | d1aceb6 |
| 21'.b | Retirement + `structured_to_prose` helper | 66247f4 |
| **21'.c** | **Eval + retrospective (this doc)** | pending |

## The retirement + polish

### Before (Ship 18/19/20 baseline)

`_casefile_flow` reconstructed prose as:
```
{intro.text}

Title 1: body 1

Title 2: body 2
```

Then `check_and_repair` appended:
```
↳ Compliance facts: 10.1 [NC-DRAFT] — ALL: 0 of 4 required...
```

Two ergonomic problems:
1. Truncated tail ("still needed: operating procedure, sc…")
   was a UX regression Ship 18/19 already fixed on cards.
2. Prose lost related-card detail entirely — SDK consumers
   reading `answer` saw only intro + action titles + the
   awkward footer.

### After (Ship 21'.b)

`structured_to_prose(structured)` emits markdown:
```markdown
{intro.text}

## {action.title}
{action.body}

## Related controls
- **A.5.15** (Access control, ISO 27001:2022) — OFI-DRAFT —
  1 of 4 required items present (3 with partial evidence)
- **10.1** (Continual improvement, ISO 27001:2022) —
  NC-DRAFT — 0 of 4 required items present
```

Every ref, title, standard, verdict, DRAFT tag, and evidence
summary from `related[]` appears in prose. SDK consumers get
complete detail without needing to parse structured JSON.

## Eval outcome

| Baseline | Ship 21'.c run 1 | **Ship 21'.c run 2 (final)** |
|---|---|---|
| PASS | 231/232 | 230/232 | **231/232** |
| WARN | 1 (#200) | 1 (#200) | **1 (#200)** |
| FAIL | 0 | 1 (#5) | **0** |

Ship 21'.c run 1 had a single fail on case #5 (`what should we
do to close the access rights NC?` — MISSING 'register'). Both
"access" and "register" appear in the current answer format
verbatim on 4/4 subsequent manual runs. Case #5 is one of the
pre-catalogued sporadic LLM-phrasing cases in CLAUDE.md
(alongside #3/#6/#14/#26/#31/#33) — the LLM rarely drops
"register" when composing implementation guidance for A.5.18.

Re-eval confirmed baseline: 231/232 PASS + 1 WARN + 0 FAIL,
identical to Ship 15'.e / 18'.c / 19'.d / 20'.e. The retired
footer + polished prose delivered zero systemic impact.

## Auditor-trail guarantee (blowback prevention)

The concern with retiring a visible append: does the auditor
lose provenance of what the LLM originally dropped?

**Answer: no.** Ship 21'.a design memo verified on live data:
- `chat_casefile_log` (schema_v68+) had 2,996 rows in 30d
- 91% had `repair_events` populated
- 61% had at least one `missing_ref` event

Post-retirement:
- Repair events (missing_ref / missing_draft_near_ref /
  missing_verdict_near_ref) still fire above the retired block
  and log identically.
- `footers_added` will only reflect the retained footers
  (bridge + risk), a natural signal that compliance-facts is
  gone.
- Auditors reconstruct the equivalent-of-footer content via
  `scripts/audit_retired_footer.sql` — a parameterised query
  joining `chat_casefile_log ⋈ jsonb_array_elements(
  repair_events)` for single-turn drill or 24h all-tenant sweep.

## Ship 14'.a addendum alignment

| Check | Applied |
|---|---|
| Role split? | YES — related-cards preserve `role` in structured; prose surfaces (Title, standard_display). |
| Parallel CaseFile view? | YES — same digest drives both paths; only OUTPUT shape changes. |
| Deterministic routing? | YES — consensus + classifier + digest_plan unchanged. |
| Guidance-normative discipline? | YES — related section carries standard_display verbatim. |

## Codified properties post-Ship 21

- **The card render is the primary UX; prose is a first-class
  fallback.** Prose reconstruction now includes everything the
  cards show (intro + actions + related). No SDK consumer is
  worse off for not migrating to structured JSON.
- **The `↳ Compliance facts:` footer is retired.** Bridge
  footer + risk footer remain (surface different data classes;
  future arcs may retire them).
- **Retirement discipline: retire visible, keep observability.**
  Every repair event still logs to `chat_casefile_log` — only
  the visible prose append is removed. This pattern (retire
  UX layer, preserve audit log) generalizes: whenever a UX
  element becomes structurally redundant, retire it from the
  visible surface but keep the log path intact + provide an
  auditor-facing query.

## Design decisions locked in

1. **Full retirement over conditional.** The footer was
   structurally redundant on every response since Ship 20.
   Keep-when-fail-open wasn't worth the complexity — fail-open
   already logs `structured_parse_failed` and the tenant still
   sees actionable prose (just without the footer).

2. **Markdown headings for actions.** `## Title\nbody` reads
   as sections in every markdown renderer. Colon-prefixed
   inline was harder to scan.

3. **Related section as bulleted list, not repeat cards.**
   Prose consumers want compact scannable info. Bold ref +
   parenthetical context + verdict-with-DRAFT + evidence
   summary. Matches the pattern in evidence_footer and every
   other Ship 7' gateway prose site.

4. **`_compliance_facts_footer` helper kept in-file.** Removed
   the call, not the function. Any future caller wanting to
   reconstruct the footer string (custom SDK footer, alternate
   surface) can import it. Prevents an accidental capability
   loss.

5. **Bridge + risk footers stay.** They surface data classes
   the current `related[]` doesn't fully mirror (cross-framework
   bridges have their own edge semantics; risk external refs
   are a different vocabulary). Ship 21 scope is narrow;
   future arcs can retire similarly if the equivalent
   structured coverage exists.

## What Ship 21 did NOT do

- **Retire the prose `answer` field itself.** Kept for backward
  compat. Every SDK / API consumer keeps working.
- **Change LLM prompts.** Ship 21 is prose-composition only;
  no classifier / digest / prompt-rule changes.
- **Change short-circuit prose composition.** Short-circuits
  compose their own answer_text via `polish_short_circuit_
  answer`; Ship 21 doesn't touch them. Only the LLM path's
  reconstruction changed.
- **Migrate eval assertions.** Eval still scans `answer_text`
  prose; the new markdown format keeps every prior ref +
  verdict assertion satisfied.
- **Retire bridge footer or risk footer.** Future-arc scope.

## Lessons

1. **Retire-visible + keep-observability is a discipline
   pattern.** Ship 18 established "structured payload +
   backward-compat prose." Ship 21 extended: retire the
   footer's visible-append role while preserving its
   audit-log role. Codified as a general pattern: whenever a
   UX element becomes structurally redundant, retire it from
   the visible surface but keep the log path intact + provide
   an auditor-facing query. The next candidate for this
   treatment: the bridge footer (retire from prose once
   `related[]` includes cross_framework_bridge cards
   uniformly).

2. **Grep the eval before you touch it.** Ship 21'.a's eval
   impact analysis (grep for `↳ Compliance facts` / `↳
   Bridges to` / bracketed verdicts in eval_suite.py) locked
   in "zero regression expected" BEFORE writing code. Ship
   21'.b + 21'.c confirmed. This is cheaper than fixing
   regressions post-hoc — 2 minutes of grep saved possibly
   an hour of prompt-tuning.

3. **Stochastic case #5 is a known pattern.** Documented in
   CLAUDE.md as one of ~7 pre-existing sporadic LLM-phrasing
   cases. When 21'.c run 1 failed on it, my instinct was
   "re-run to distinguish variance from regression" — same
   discipline as [[feedback-eval-state-drift]] locked in
   during Ship 15. Confirmed stochastic via 4/4 manual runs +
   full re-eval. The eval-noise pattern is a real infra
   feature, not a red herring; but so is the discipline of
   re-running.

4. **Auditor SQL scripts are cheap high-value artefacts.**
   `scripts/audit_retired_footer.sql` is 40 lines and gives
   auditors complete provenance of the retired footer's
   information. Cheaper to write than a UX/API deprecation
   notice, and more useful than a design memo alone.

## Ship 21 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 21'.a | Design memo + eval impact grep + auditor SQL + 30d evidence | Locked full-retirement + polish path; audit trail codified |
| 21'.b | Retirement in repair.py + structured_to_prose helper + wiring | Prose polished; footer retired end-to-end |
| **21'.c** | **Eval + retro (this)** | **231/232 PASS + 1 WARN + 0 FAIL — arc closed** |

## Related

- [[ship-2-prime-j-preservation-footer-2026-07-16]] — arc that
  introduced the footer this arc retires
- [[ship-18-prime-arc-retrospective-2026-07-23]] — structured
  payload arc that made the footer redundant
- [[ship-19-prime-arc-retrospective-2026-07-23]] — card polish
  (leaves checklist, intro dedupe)
- [[ship-20-prime-arc-retrospective-2026-07-23]] — universal
  structured coverage across short-circuits
- [[feedback-eval-state-drift]] — the re-run discipline used
  to confirm case #5 was stochasticity not regression
