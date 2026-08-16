# Mangled-marker re-upload dogfood — internal review notes

_2026-08-16. Testing Task #606's defensive marker validation against a real re-upload scenario. Sample: `req:A.5.15:access_control_policy` docx, mangled `<<MUST item:A.5.15:rbac>>` → `rbaac`._

Goal was to prove Task #606 catches the "officer disables protection + mangles a hidden marker" scenario. It didn't fire. But the walk-through surfaced a **bigger pre-existing bug** that predates Task #606.

---

## Stage-by-stage walk

### Stage 1 — Fresh download

Locked docx has 30 hidden runs + 9 editable placeholders (6 edit-zones + 3 signature cells). All Task #604+#605 expectations met.

### Stage 2 — Officer fills one placeholder

Typed plausible policy text into placeholder #1 (`logical_rules` — SSO + MFA + audit logging). 176 chars.

### Stage 3 — Officer disables Word protection (simulated)

Not required for this simulation — the mangling and re-upload paths work regardless of protection state.

### Stage 4 — Officer accidentally mangles a hidden marker

Simulated: `<<MUST item:A.5.15:rbac>>` → `<<MUST item:A.5.15:rbaac>>` (typo — added an 'a'). This is exactly the scenario Task #606 was designed to catch.

### Stage 5 — Reader + extractor process the file

Reader (`_read_docx`) processed the docx via mammoth-to-markdown. Extracted 21,915 chars.

Zones detected: **10** (7 MUSTs + 3 SHOULDs on A.5.15).
Findings emitted: **10** (all!).
Warnings: **0** (Task #606 didn't fire).
Mangled marker: **not caught**.

### Stage 7 — Verdict

- ✗ Tenant evidence NOT bound (mixed with scaffolding — see below).
- ✗ Mangled marker NOT caught by Task #606.
- ✓ No silent bind to the nonexistent id `rbaac`.

Third bullet is the ONE thing that worked as intended — but only because the reader's reconstruction path uses a DIFFERENT source for the item id than what I thought.

---

## The two bugs surfaced

### Bug A — Task #606 checks the wrong id source

The reader's `_arion_docx_to_edit_zones` (readers.py:590+) reconstructs zone markers from the `◆ Required element — <slug>` VISIBLE labels in the docx, NOT from the hidden `<<MUST item:X>>` markers I stamped with `w:vanish` in Task #604.

Flow:
```
docx contains:
  ◆ Required element — rbac                    ← visible bold text
  Do not edit — system id: <<MUST item:A.5.15:rbaac>>   ← HIDDEN (w:vanish)
  ...

reader sees:
  ◆ Required element — rbac                    ← ✓ visible
  Do not edit — system id: <<MUST item:A.5.15:rbaac>>   ← ✓ mammoth reads hidden text as text
  ...

reader reconstructs:
  <<MUST item:A.5.15:rbac>>                    ← from the ◆ SLUG, not the hidden marker
  <!-- EDIT-ZONE-START item:A.5.15:rbac -->    ← ditto
```

The reader takes the item id from the ◆ label's slug (`rbac`), not from the hidden `<<MUST>>` marker (`rbaac`). Task #606 validates the reader-reconstructed id — which is always valid because the reader derives it from the unmangled slug.

**What Task #606 actually catches**: cases where the tenant mangles the ◆ LABEL itself (`◆ Required element — rbaac`). That's much less likely to happen because the ◆ label is visible prose the officer might read but rarely edit.

**What Task #606 misses**: hidden marker mangling — which was the actual concern from the dogfood friction #6.

### Bug B — Extractor treats ALL scaffolding as tenant evidence

Bigger issue. When a tenant downloads the docx template and re-uploads it **UNEDITED**, the extractor:

- Detects 10 edit zones.
- Emits 10 findings, all `finding='Comply'`, `confidence='high'`, `inference_source='templated'`.
- Auto-approves all 10 at the writer.
- Flips every MUST on A.5.15 to satisfied.
- Control flips to false Comply.

The `_is_pure_scaffolding` check (extractor.py:795) only recognizes:
- Empty/whitespace
- `<<TEXT>>` / `<<NAME>>` placeholders
- `<!-- prefilled from N -->` comments

But the reader's reconstructed zone content contains:
- `*Do not edit — system id*: <<MUST item:X>>` prose
- `*Standard text:*` blockquote
- Italic-style guidance (`_Behavioural principle_`)
- `✓ Good:` example blocks
- `__Best practice ✓ — covered:__` bulleted lists

None of those match `_is_pure_scaffolding`'s patterns. So the extractor treats the whole zone as tenant evidence.

**This is a pre-existing bug that Task #603 (empty edit zones by default) made much worse.** Before #603, zones had prior evidence prefilled which `_is_pure_scaffolding` recognized via the `<!-- prefilled from N -->` comment. Post-#603, zones are empty and the reader-reconstructed scaffolding masquerades as tenant content.

**Impact assessment**: this affects ANY tenant who downloads → uploads-without-editing a docx template. Arion's existing findings (before Task #603) use `inference_source='extracted'` (LLM path), not `templated` — because either the docs pre-date the ArionComply renderer OR they went through the LLM path instead. So the bug hasn't hit production yet. But once tenants start using the docx template loop, it WILL.

---

## What Task #606 still does

Even though it doesn't catch the specific scenario I designed the dogfood around, Task #606 is not useless:

1. **Guards against direct-markdown-upload mangling** — if a tenant uploads a `.md` file (not `.docx`) with a mangled `<<MUST item:X:Y>>` marker inside an `<!-- EDIT-ZONE-START item:X:Y -->` block, the extractor gets the id straight from the EDIT-ZONE-START comment, and Task #606 catches a mangled id there.

2. **Guards against future reader changes** — if the reader is ever refactored to use the hidden marker as the id source (which would actually be the RIGHT design given the docx renderer emits them as the round-trip truth), Task #606's validation is already in place.

3. **Defensive backstop for TABLE-COLUMNS mangling** — the `<!-- TABLE-COLUMNS -->` metadata block still uses raw item ids that a mangled tenant edit could damage.

4. **Metrics** — the `templated_zones_mangled` and `templated_table_cols_mangled` counters now exist in `doc.extraction_metrics`; if the bug ever fires it will show up in `intake_trace_log`.

So Task #606 ships as a defensive backstop with narrower actual coverage than dogfood friction #6 implied.

---

## What we need to do about Bug B

Task #607 recommendation: **extend `_is_pure_scaffolding` to recognize reader-reconstructed patterns.** Two options:

### Option 1 — pattern-based scaffolding stripping

Extend `_is_pure_scaffolding` to sequentially strip known scaffolding shapes:
- `*Do not edit — system id*: <<...>>` line
- `*Standard text:*` blockquote
- `_..._` italic guidance blocks
- `✓ Good:` example blocks
- `Best practice.*:` + bulleted list
- Blank lines and horizontal rules

If nothing substantive remains, treat as pure scaffolding.

Simple, deterministic, no change to reader.

### Option 2 — reader emits sentinels

Modify the reader's `_arion_docx_to_edit_zones` to emit an `<!-- SCAFFOLDING-START -->` / `<!-- SCAFFOLDING-END -->` bracket around the reconstructed scaffolding blocks. Extractor drops those before deciding scaffolding-vs-evidence.

Cleaner but touches two files. Also lets us evolve scaffolding patterns without updating the extractor.

### Option 3 — extractor computes tenant delta

Compute a diff between the reader-extracted body and what our own renderer would produce for the same leaf. Only the delta counts as tenant evidence.

Most robust but requires reproducing the render at extract time (slow, side-effect-y).

Option 2 is the right long-term shape. Option 1 unblocks fastest. Recommend shipping Option 1 as Task #607 and deferring Option 2 to a Phase B intake-quality arc.

---

## Overall verdict

**Task #606 as it stands is a defensive backstop with narrower coverage than the dogfood friction implied.** Ship it — the code is correct and the metrics are useful. Update the retro to reflect what it actually catches (direct-.md marker mangling + table-column mangling) rather than the docx-hidden-marker case that doesn't hit its code path.

**Bug B is a real pre-existing regression that Task #603 exacerbated.** Task #607 needs to fix it. Without Task #607, any docx-upload roundtrip on a template produces false Comply on every MUST it touches. Prioritise before customer ship.

Recommend committing Task #606 with corrected retro + opening Task #607 immediately.
