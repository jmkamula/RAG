---
name: human-in-the-loop-positioning
description: "ArionComply positions itself as a compliance assistant, not an authority. Client remains responsible and answerable; humans commit final posture."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7c33fad-b32e-4557-9944-b406bcbbd8ee
---

**Rule:** ArionComply helps clients on their compliance journey but does not present itself as an authority. The client remains responsible and answerable for compliance posture. All document imports (and by extension, all auto-derived data: classifications, obligations, postures, control determinations) must support a human-in-the-loop step before they become committed posture.

**Why:** stated explicitly by user 2026-05-14 in the context of designing the confidence-threshold behavior for incident classifications. Auto-derived/LLM-suggested classifications should land visible and active (not gated by approval workflow), but always surface to a review queue so the human can confirm or override. This positions ArionComply as a helper, not a decider — important for liability framing, audit defensibility, and trust.

**How to apply:**
- When designing flows that involve auto-derivation, ML inference, LLM suggestions, or rule-based defaults: never auto-commit as authoritative. Always provide a review surface.
- Avoid UI/answer copy that frames the platform as the authority ("ArionComply has determined…", "Your control X is non-compliant"). Instead: "Based on the documents imported, control X appears non-compliant — please confirm".
- When the user is asked about thresholds or approval gates: default to "land active + surface for review" rather than "block until approved". Friction-light, but always traceable.
- This applies to: document imports, classification derivation, obligation materialization, posture inference, evidence linking.
