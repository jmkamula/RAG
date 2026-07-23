---
name: ship-19-prime-c-frontend-checklist-2026-07-23
description: "Ship 19'.c — frontend leaf checklist render on primary card + intro chip dedupe; closes all 3 user-flagged Ship 18 usability issues"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 19'.c — frontend delivery of the card polish arc. Renders
the `leaves[]` data Ship 19'.b added and closes all three
user-flagged Ship 18 usability issues. Commit `62eb419`.

## Rendering changes (renderStructuredAnswer)

### 1. Intro chip dedupe

Backend keeps emitting `intro.primary_ref` for API/SDK consumers.
Frontend now checks if the ref appears in the first 40 chars of
`intro.text`; if yes, skips the chip. Prevents the
`[A.5.15] ISO 27001 A.5.15 (Access control)...` double-mention.

```javascript
if (intro.primary_ref) {
  const head = (intro.text || '').slice(0, 40);
  if (!head.includes(intro.primary_ref)) {
    introChip = `<span class="ref-tag" ...>${esc(intro.primary_ref)}</span>`;
  }
}
```

### 2. Primary-card leaf checklist

Primary card (`relation === "primary"` with populated `leaves[]`)
renders each leaf as ✓/○ with title + per-MUST count. Related
cards keep the compact `still_needed` chip surface per the
19'.a primary-only decision.

Fallback: primary cards without leaves[] data (single-leaf
controls, Comply/N/A verdicts) render the existing
`still_needed` chip row — no regression.

### CSS additions

- `.sa-primary-card` — purple left border (`#534AB7`) +
  off-white background (`#FBFAF7`) distinguish primary from
  related drill-downs
- `.sa-leaf-checklist` — compact list container, subtle cream
  background matching app design tokens
- `.sa-leaf-yes .sa-leaf-icon` — green ✓ (matches Comply badge
  `#7FB36F`)
- `.sa-leaf-no .sa-leaf-icon` — outlined ○ (`#EEECE2`
  background + gray border)
- `.sa-leaf-count` — right-aligned per-MUST count ("3 of 3
  items"), muted small text

## Verified live on "how do I remediate A.5.15?"

- **Intro chip**: HIDDEN (dedup fired — ref in text head)
- **A.5.15 [PRIMARY] renders 4-leaf checklist**:
  * ✓ Management Approval (3/3)
  * ○ Access Control Policy (5/6)
  * ○ Communication Record (1/5)
  * ○ Periodic Review (1/5)
- **10.1 [related] hides checklist** — keeps compact
  `still_needed` chip surface
- **10.2 [related] hides checklist** — same

## All 3 user-flagged Ship 18 issues closed

| Issue | Fix in Ship 19 |
|---|---|
| Redundant ref chip | 19'.c dedupe logic |
| No enumeration of fulfilled items | 19'.b `leaves[]` + 19'.c ✓/○ checklist |
| Vague "1 of 4 items" in intro | 19'.b prompt rule 1 (+ 19'.d refinement) |

## No backend changes; no restart needed

Ship 19'.c is HTML/CSS/JS only. Users get the new render on
their next page reload.

## Ship 14'.a addendum alignment

1. **Role split?** YES — verdict badge + relation label carry
   the role model into the UI. Primary card highlight
   differentiates from related drill-downs.
2. **Parallel CaseFile view?** YES — UI reflects what the
   digest surfaced.
3. **Deterministic routing?** N/A — UI layer.
4. **Guidance-normative discipline?** YES — guidance-role
   controls typically render empty `leaves[]` correctly.

## Ship 19 progress

| Sub-arc | Status |
|---|---|
| 19'.a Design memo | ✓ (c433d63) |
| 19'.b Backend leaves[] + prompt tweak | ✓ (916519f) |
| **19'.c Frontend checklist + intro dedupe** | **✓ (62eb419, this doc)** |
| 19'.d Rule refinement + eval + retro | next |

## Related

- [[ship-19-prime-a-card-polish-design-2026-07-23]] — design
- [[ship-19-prime-b-backend-leaves-2026-07-23]] — backend
- [[ship-18-prime-c-frontend-cards-prompt-rules-2026-07-23]] —
  precedent for the card render idioms extended here
