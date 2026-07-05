-- schema_v60_standards_role_model.sql — Framework role model (Phase 1)
--
-- Adds explicit role / subject / scope / mandate_source metadata to the
-- standards registry. This is the first phase of the multi-framework
-- architecture refactor (design conversation 2026-07-05):
--
--   PROGRAM     — a management-system / attestation framework that can
--                 carry certification. Standalone. (ISO 27001, SOC 2,
--                 HITRUST, TISAX, NIST CSF)
--   EXTENSION   — extends a PROGRAM for a specific subject; requires
--                 ≥1 PROGRAM. (ISO 27701, 27017, 27018)
--   OBLIGATION  — legal / regulatory / contractual mandate; not a
--                 management system itself; demonstrated-by
--                 PROGRAM + EXTENSION. (GDPR, CCPA, NIS2, DORA, EU AI
--                 Act, HIPAA Privacy Rule, PCI DSS-as-obligation)
--
-- The existing `standard_type` column (management_system / regulation
-- / framework / code_of_practice) describes the STANDARD'S FORM.
-- `role` describes the STANDARD'S POSITION in a compliance stack.
-- They are orthogonal — ISO 27701 is form=management_system AND
-- role=extension, because it's an ISMS extension that can only exist
-- on top of another ISMS. `standard_type` is kept unchanged.
--
-- No behavior change in this migration. Read-only metadata additions
-- + backfill for the current 6 rows in `standards`. Downstream code
-- (scope_loader, posture_loader, extractor) picks up the new columns
-- in Phase 2 and beyond.

BEGIN;

-- ── New columns on standards ──────────────────────────────────────────

ALTER TABLE standards
    ADD COLUMN IF NOT EXISTS role           TEXT,
    ADD COLUMN IF NOT EXISTS subject        TEXT[]  NOT NULL DEFAULT ARRAY[]::TEXT[],
    ADD COLUMN IF NOT EXISTS scope_type     TEXT    NOT NULL DEFAULT 'org_wide',
    ADD COLUMN IF NOT EXISTS mandate_source TEXT;

-- Role check (nullable until backfilled below, then constrained):
--   'program'    — can stand alone (ISO 27001, SOC 2, NIST CSF, TISAX)
--   'extension'  — requires a program (ISO 27701, ISO 27017, ISO 27018)
--   'obligation' — legal/contractual mandate (GDPR, NIS2, DORA, CCPA)
--   'guidance'   — companion / code-of-practice; not a compliance surface
--                  on its own (ISO 27002 relative to 27001)
ALTER TABLE standards
    DROP CONSTRAINT IF EXISTS standards_role_chk;

-- Scope_type check:
--   'org_wide'         — applies to the whole organisation (ISO 27001,
--                        SOC 2, NIST CSF)
--   'data_type_scoped' — applies to a specific data class (PCI CDE,
--                        HIPAA PHI, GDPR EU personal data)
--   'sector_scoped'    — applies to a specific sector (DORA financial,
--                        NIS2 essential entities, TISAX automotive)
--   'system_scoped'    — applies to specific systems (EU AI Act
--                        high-risk AI systems)
ALTER TABLE standards
    DROP CONSTRAINT IF EXISTS standards_scope_type_chk;
ALTER TABLE standards
    ADD CONSTRAINT standards_scope_type_chk
    CHECK (scope_type IN ('org_wide', 'data_type_scoped',
                          'sector_scoped', 'system_scoped'));

-- Mandate_source check (nullable):
--   'voluntary'   — chosen by the org (ISO 27001, NIST CSF)
--   'attestation' — third-party attestation regime (SOC 2, TISAX)
--   'legal'       — imposed by law (GDPR, NIS2, DORA, EU AI Act, HIPAA)
--   'contractual' — imposed by contract / trade body (PCI DSS,
--                   customer requirements)
ALTER TABLE standards
    DROP CONSTRAINT IF EXISTS standards_mandate_source_chk;
ALTER TABLE standards
    ADD CONSTRAINT standards_mandate_source_chk
    CHECK (mandate_source IS NULL OR mandate_source IN
           ('voluntary', 'attestation', 'legal', 'contractual'));

-- ── Backfill for the current 6 rows ──────────────────────────────────

-- ISO 27001:2022 — the baseline ISMS. Voluntary, org-wide, information
-- security. Standalone PROGRAM.
UPDATE standards SET
    role           = 'program',
    subject        = ARRAY['information_security'],
    scope_type     = 'org_wide',
    mandate_source = 'voluntary'
WHERE id = 'ISO27001:2022';

-- ISO 27701:2019 — PIMS extension. Cannot exist without a 27001 ISMS
-- (per §4.1). Privacy subject. Standalone certifiable but structurally
-- an EXTENSION.
UPDATE standards SET
    role           = 'extension',
    subject        = ARRAY['privacy'],
    scope_type     = 'org_wide',
    mandate_source = 'voluntary'
WHERE id = 'ISO27701:2019';

-- GDPR:2016/679 — EU law. Data-type-scoped (EU personal data). Legal
-- mandate demonstrated-by PROGRAM + EXTENSION in privacy subject.
UPDATE standards SET
    role           = 'obligation',
    subject        = ARRAY['privacy'],
    scope_type     = 'data_type_scoped',
    mandate_source = 'legal'
WHERE id = 'GDPR:2016/679';

-- ISO 27002:2022 — code of practice / guidance for 27001 Annex A. Not
-- a compliance surface itself; explains what the 27001 controls mean.
UPDATE standards SET
    role           = 'guidance',
    subject        = ARRAY['information_security'],
    scope_type     = 'org_wide',
    mandate_source = 'voluntary'
WHERE id = 'ISO27002:2022';

-- ISO 27018:2019 — cloud PII processor code. Extension for cloud +
-- privacy subject.
UPDATE standards SET
    role           = 'extension',
    subject        = ARRAY['cloud', 'privacy'],
    scope_type     = 'org_wide',
    mandate_source = 'voluntary'
WHERE id = 'ISO27018:2019';

-- NIST CSF 2.0 — voluntary framework. Non-certifiable but usable as a
-- reference PROGRAM.
UPDATE standards SET
    role           = 'program',
    subject        = ARRAY['information_security'],
    scope_type     = 'org_wide',
    mandate_source = 'voluntary'
WHERE id = 'NIST-CSF:2.0';

-- ── Add role CHECK now that all rows are populated ────────────────────

ALTER TABLE standards
    ADD CONSTRAINT standards_role_chk
    CHECK (role IN ('program', 'extension', 'obligation', 'guidance'));

-- Enforce NOT NULL after backfill.
ALTER TABLE standards
    ALTER COLUMN role SET NOT NULL;

-- ── Indexes for the new lookup patterns ───────────────────────────────

-- Subject-scoped lookup (Phase 3: extractor routes by subject).
CREATE INDEX IF NOT EXISTS idx_standards_subject
    ON standards USING GIN (subject);

-- Role-scoped lookup (Phase 4: dashboard three-lens view).
CREATE INDEX IF NOT EXISTS idx_standards_role
    ON standards (role);

COMMIT;

-- Verification query (run manually after migration):
--   SELECT id, short_name, role, subject, scope_type, mandate_source
--   FROM standards ORDER BY role, id;
