---
name: feedback-poc-context-low-security-friction
description: "For self-owned PoC deployments on private hardware where user is both operator and tenant, don't repeatedly warn about leaked credentials / API keys / passwords when the practical blast radius is zero. Security theater is friction they don't need."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Don't repeatedly warn about credential leaks (API keys, passwords in ps output, plaintext in transcripts) when the user's context makes them functionally moot: self-owned box, private LAN, single-tenant PoC, user is both operator and tenant. First mention is fine so they're aware; further repetition when they've moved on is friction.

**Why:** During Ship 101'.a on-prem PoC deployment, user was running install commands via SSH from their Mac into their own on-prem box (arionlabs-dr-01, 10.0.1.85, private LAN). They were the tenant. I flagged three separate credential leaks (two OpenAI keys via ps -ef, an API key pasted into chat) with warnings about rotation. On the third one they interrupted: "im not concerned about the API key, i need to run the PoC through." My paranoia was misaligned with their actual risk model.

**How to apply:** For self-owned PoC / evaluation / on-prem / dev-box contexts where the user IS the security boundary: mention the leak once matter-of-factly if you notice, then drop it. Don't re-raise or offer redaction techniques unless the user asks. For genuine multi-user or production contexts, the paranoia is still appropriate — this is context-specific, not a blanket "don't warn about credentials."

Related: [[human-in-the-loop-positioning]] — ArionComply's default posture is "assist, not decide"; that extends to how much friction to add around user judgment calls on their own systems.
