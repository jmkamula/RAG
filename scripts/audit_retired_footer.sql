-- Ship 21 — Auditor query for the retired `↳ Compliance facts:` footer
--
-- Post-Ship-21 the visible prose footer is gone from chat responses.
-- Every dropped-ref event that WOULD have rendered as a footer is
-- still captured in chat_casefile_log.repair_events (schema_v68+).
--
-- This query reconstructs the equivalent-of-footer content for any
-- chat turn, so auditors have a complete provenance trail without
-- the UX cost of a truncated inline footer.
--
-- Prereq: psql -U arioncomply_app -h 127.0.0.1 -d arioncomply_compliance
--
-- Usage — one turn:
--   \set turn '<request_id or session_id>'
--   \i scripts/audit_retired_footer.sql
--
-- Usage — recent 24h all-tenant sweep:
--   Change WHERE clause below to `AND created_at > now() - interval '24 hours'`.

-- Every repair event on every turn since the Ship 21/22 rollout:
--   * kind        — missing_ref | missing_draft_near_ref |
--                   missing_verdict_near_ref | missing_bridge_footer |
--                   missing_risk_ref | missing_ref_structured |
--                   structured_parse_failed
--   * ref         — control ref the LLM dropped from prose (or
--                   NULL for footer-level misses like bridge)
--   * detail      — human-readable note the repair layer generated
-- All of these were previously appended to the visible prose as
-- `↳ Compliance facts: ...` (Ship 21'.b retirement), `↳ Bridges to
-- ISO 27001 ...` (Ship 22'.b retirement), or `↳ Risk register: ...`
-- (Ship 22'.c retirement). Now they live here exclusively; the
-- card render + `## Related controls` / `## Risks` prose sections
-- carry the equivalent auditor-visible content.

SELECT c.created_at::timestamp(0)                         AS ts,
       c.tenant_id,
       c.session_id,
       c.request_id,
       c.query,
       ev->>'kind'                                         AS repair_kind,
       ev->>'ref'                                          AS ref,
       ev->>'detail'                                       AS detail
  FROM chat_casefile_log c,
       LATERAL jsonb_array_elements(c.repair_events) AS ev
 WHERE c.repair_events_count > 0
   -- and c.request_id = :'turn'    -- uncomment for single-turn drill
   -- and c.created_at > now() - interval '24 hours'
 ORDER BY c.created_at DESC
 LIMIT 100;

-- Per-kind aggregate — how often each repair type fires per tenant.
-- Useful to prove "retirement did not silence auditor-relevant signals";
-- expect the counts to STAY roughly stable across the Ship 21 rollout
-- (repair events log identically; only the visible append is removed).

-- SELECT c.tenant_id,
--        ev->>'kind' AS repair_kind,
--        count(*)    AS n
--   FROM chat_casefile_log c,
--        LATERAL jsonb_array_elements(c.repair_events) AS ev
--  WHERE c.created_at > now() - interval '7 days'
--  GROUP BY 1, 2
--  ORDER BY 1, 3 desc;
