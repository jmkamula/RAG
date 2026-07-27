-- Curator seed data — Ship 47'.b
-- Generated: 2026-07-27T15:11:52+00:00
-- Apply after schema_baseline.sql on a fresh install.
-- All tables here are portable across tenants and non-runtime.

BEGIN;

-- ── standards ──
--
-- PostgreSQL database dump
--

\restrict tZQWvfvffRLSQuYj0hAf9gNzgciC8SJgsyTu9URL15kYk0STvE2VV4ZM9pRNSrZ

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: standards; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.standards DISABLE TRIGGER ALL;

INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27001:2022', 'ISO27001', '2022', 'ISO/IEC 27001:2022', 'ISO 27001', 'management_system', true, 'global', 'Information Security Management Systems — Requirements', NULL, true, NULL, '2026-04-29 07:59:41.240042+00', 'program', '{information_security}', 'org_wide', 'voluntary');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27701:2019', 'ISO27701', '2019', 'ISO/IEC 27701:2019', 'ISO 27701', 'management_system', true, 'global', 'Privacy Information Management System — Extension to ISO 27001/27002', 'Annex D', true, NULL, '2026-04-29 07:59:41.240042+00', 'extension', '{privacy}', 'org_wide', 'voluntary');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('GDPR:2016/679', 'GDPR', '2016/679', 'General Data Protection Regulation (EU) 2016/679', 'GDPR', 'regulation', false, 'EU', 'EU regulation on protection of natural persons with regard to processing of personal data', NULL, true, NULL, '2026-04-29 07:59:41.240042+00', 'obligation', '{privacy}', 'data_type_scoped', 'legal');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27002:2022', 'ISO27002', '2022', 'ISO/IEC 27002:2022', 'ISO 27002', 'code_of_practice', false, 'global', 'Information Security Controls — guidance for ISO 27001 Annex A', NULL, true, NULL, '2026-04-29 07:59:41.240042+00', 'guidance', '{information_security}', 'org_wide', 'voluntary');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27018:2019', 'ISO27018', '2019', 'ISO/IEC 27018:2019', 'ISO 27018', 'code_of_practice', false, 'global', 'Protection of PII in public clouds — extends ISO 27001/27701', NULL, false, NULL, '2026-04-29 07:59:41.240042+00', 'extension', '{cloud,privacy}', 'org_wide', 'voluntary');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('NIST-CSF:2.0', 'NIST-CSF', '2.0', 'NIST Cybersecurity Framework 2.0', 'NIST CSF', 'framework', false, 'US', 'Framework for improving critical infrastructure cybersecurity', NULL, false, NULL, '2026-04-29 07:59:41.240042+00', 'program', '{information_security}', 'org_wide', 'voluntary');
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27003:2017', 'ISO27003', '2017', 'ISO/IEC 27003:2017 — Information security management systems — Guidance', 'ISO 27003', 'code_of_practice', false, 'global', 'Implementation guidance for ISO 27001 management-system clauses (context, leadership, planning, support, operation, evaluation, improvement).', NULL, false, NULL, '2026-07-21 17:21:20.874437+00', 'guidance', '{information_security_management_system}', 'org_wide', NULL);
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27005:2022', 'ISO27005', '2022', 'ISO/IEC 27005:2022 — Guidance on managing information security risks', 'ISO 27005', 'code_of_practice', false, 'global', 'Guidance on the information-security risk management process supporting ISO 27001 6.1 / 8.2 / 8.3 (risk assessment methodology, treatment options, acceptance criteria, register schema).', NULL, false, NULL, '2026-07-21 17:21:20.874437+00', 'guidance', '{risk_management}', 'org_wide', NULL);
INSERT INTO public.standards (id, family, version, full_name, short_name, standard_type, certifiable, jurisdiction, description, annex_mapping, loaded_in_graph, node_count, created_at, role, subject, scope_type, mandate_source) VALUES ('ISO27004:2016', 'ISO27004', '2016', 'ISO/IEC 27004:2016 — Information security management — Monitoring, measurement, analysis and evaluation', 'ISO 27004', 'code_of_practice', false, 'global', 'Guidance on selecting, defining, presenting and using information-security performance and effectiveness metrics; supports ISO 27001 clause 9.1 and monitoring-adjacent Annex A controls.', NULL, false, NULL, '2026-07-22 08:59:56.216538+00', 'guidance', '{monitoring_and_measurement}', 'org_wide', NULL);


ALTER TABLE public.standards ENABLE TRIGGER ALL;

--
-- PostgreSQL database dump complete
--

\unrestrict tZQWvfvffRLSQuYj0hAf9gNzgciC8SJgsyTu9URL15kYk0STvE2VV4ZM9pRNSrZ


-- ── standard_relationships ──
--
-- PostgreSQL database dump
--

\restrict lPnIqgz4aFN76OhCsi1UBPByvUpmxgarcYZQQKFh6iTezbmtpklhKobAhiyB2Wx

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: standard_relationships; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.standard_relationships DISABLE TRIGGER ALL;

INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('0feb9a6f-4c2c-48f1-8e44-26f0735b096f', 'ISO27701:2019', 'ISO27001:2022', 'extends', 'ISO 27701:2019 Introduction', 'full', 'ISO 27701 adds PIMS requirements to ISO 27001 ISMS', '2026-04-29 07:59:41.243692+00');
INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('b9d6cbfd-00a3-4836-9832-db2b52fd46e5', 'ISO27701:2019', 'GDPR:2016/679', 'maps_to', 'ISO 27701:2019 Annex D', 'partial', 'Annex D maps ISO 27701 controls to GDPR articles. Coverage is partial — not every GDPR article has a direct 27701 control.', '2026-04-29 07:59:41.243692+00');
INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('394da0e3-ad33-4531-b145-4a46f54124d2', 'ISO27701:2019', 'GDPR:2016/679', 'satisfies', 'ISO 27701:2019 Introduction', 'partial', 'ISO 27701 certification provides evidence of GDPR compliance measures but does not guarantee full legal compliance', '2026-04-29 07:59:41.243692+00');
INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('8d2d609f-52ef-4769-b7cc-d5f8d6cad164', 'ISO27001:2022', 'ISO27002:2022', 'references', 'ISO 27001:2022 Annex A', 'full', 'ISO 27001 Annex A controls are defined in ISO 27002', '2026-04-29 07:59:41.243692+00');
INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('8e9be6ed-6a70-4be4-ba79-deb0cb53d764', 'ISO27701:2019', 'ISO27018:2019', 'references', 'ISO 27701:2019', 'partial', 'ISO 27018 provides additional guidance for cloud PII processing', '2026-04-29 07:59:41.243692+00');
INSERT INTO public.standard_relationships (id, source_id, target_id, relationship, mapping_source, coverage, notes, created_at) VALUES ('e5f0ce4c-7a67-436b-b14a-b818a9ee27ac', 'ISO27001:2022', 'GDPR:2016/679', 'implements', 'ISO 27001:2022 Annex A controls (Neo4j IMPLEMENTS edges)', 'partial', 'ISO 27001 Annex A controls implement parts of GDPR (Art.32 security of processing, Art.28 processor obligations, etc). Control-level mapping lives in Neo4j; this row marks the standards-level relationship so GDPR appears in scope for tenants enrolled only in ISO 27001.', '2026-05-15 19:50:51.080816+00');


ALTER TABLE public.standard_relationships ENABLE TRIGGER ALL;

--
-- PostgreSQL database dump complete
--

\unrestrict lPnIqgz4aFN76OhCsi1UBPByvUpmxgarcYZQQKFh6iTezbmtpklhKobAhiyB2Wx


-- ── retention_policies ──
--
-- PostgreSQL database dump
--

\restrict 57X3Y4UYlYhToleKkPRrc9CbVnqaKOyQzVXGy05RV1JMibCsZxRdcLZAhQjoXLA

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: retention_policies; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.retention_policies DISABLE TRIGGER ALL;

INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('34614983-6b67-4163-a75d-7fcf1cef3faa', NULL, 'compliance', NULL, 7, 0, NULL, false, 'ISO 27001 A.5.33, GDPR Art.5(1)(e)', 'Compliance records retained 7 years, manual review before purge', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('0f957a12-7fba-4b7d-b3a6-4e655f33cd8b', NULL, 'compliance', 'posture_controls', 7, 0, NULL, false, 'ISO 27001 A.5.33', 'Posture history required for audit trail', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('1af379c1-320e-4329-a499-c0e5cc690182', NULL, 'compliance', 'isms_audits', 7, 0, NULL, false, 'ISO 27001 A.5.33', 'Audit records required for surveillance audits', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('6c0ae18f-762d-49f3-9e39-6ddbc7719946', NULL, 'compliance', 'incidents', 7, 0, 5, false, 'ISO 27001 A.5.26, GDPR Art.33', 'Anonymise personal data after 5 years, retain incident record for 7', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('ed1c7a2d-2b48-4405-9d7a-330929132c30', NULL, 'compliance', 'document_findings', 7, 0, NULL, false, 'ISO 27001 A.5.33', 'Evidence of document evaluation retained', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('f03550a5-2b50-4330-b026-3bfd703bc252', NULL, 'operational', NULL, 5, 0, 3, true, 'ISO 27001 A.5.33, GDPR Art.5(1)(e)', 'Operational records 5 years, PII anonymised after 3', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('64f4966a-d276-476b-a0e5-285a5d2e0c86', NULL, 'operational', 'risks', 5, 0, 3, true, 'ISO 27001 A.5.33', 'Risk register retained 5 years', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('f1620c21-f464-47ae-b7b0-42555b86fd96', NULL, 'operational', 'vendors', 5, 0, 3, true, 'ISO 27001 A.5.33, GDPR Art.28', 'Processor agreements 5 years, contact data anonymised at 3', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('6a59aa68-3f15-49a1-ab2f-38fcba0b117f', NULL, 'operational', 'remediation_plans', 5, 0, NULL, true, 'ISO 27001 A.5.33', 'Remediation evidence retained 5 years', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('e10ddf41-d4e0-47f6-b79c-1e43960b7cb5', NULL, 'personal_data', NULL, 0, 0, NULL, false, 'GDPR Art.17', 'Erasure on data subject request within 30 days', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('29748336-20a7-41a4-afcc-8021e570ce0b', NULL, 'personal_data', 'users', 0, 0, NULL, false, 'GDPR Art.17', 'User accounts anonymised on erasure request', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('97d781ee-c2a0-43aa-98b2-94938eeebb78', NULL, 'platform', NULL, 0, 30, NULL, true, 'Contractual', 'Soft deleted on tenant offboarding, purged after 30 days', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('ee217216-dcc5-48de-b7fa-eccabdfa47ab', NULL, 'session', NULL, 0, 90, NULL, true, 'GDPR Art.5(1)(e)', 'Conversation history auto-purged after 90 days', '2026-04-29 15:20:51.415792+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('9661c041-a9de-4046-883d-8f01884e7524', NULL, 'compliance', 'confirmation_log', 7, 0, NULL, false, 'ISO 27001 A.5.33, GDPR Art.5(1)(d) accuracy principle', 'Confirmation audit trail — who confirmed what and when. Required to demonstrate competent human review of compliance posture.', '2026-05-02 07:58:56.295289+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('334cec5f-cbc8-4e78-ae6b-c99eec00d570', NULL, 'operational', 'request_trace_log', 5, 0, NULL, true, 'ISO 27001 A.5.33, GDPR Art.5(1)(e)', 'Request traces retained 5 years for audit and performance analysis. Auto-purge permitted after retention period.', '2026-05-02 08:04:10.701454+00');
INSERT INTO public.retention_policies (id, tenant_id, retention_class, table_name, retain_years, retain_days, anonymise_after_years, auto_purge, legal_basis, notes, created_at) VALUES ('d19d9216-e1ae-4e36-9abb-a1c44208839d', NULL, 'platform', 'tenant_source_registry', 0, 30, NULL, true, 'Contractual', 'Source registrations soft-deleted on disconnection, purged 30 days after soft delete.', '2026-05-02 08:04:10.701454+00');


ALTER TABLE public.retention_policies ENABLE TRIGGER ALL;

--
-- PostgreSQL database dump complete
--

\unrestrict 57X3Y4UYlYhToleKkPRrc9CbVnqaKOyQzVXGy05RV1JMibCsZxRdcLZAhQjoXLA


-- ── ref_prefixes ──
--
-- PostgreSQL database dump
--

\restrict xe9pSf6E7VHjdBXLQ6zOSOuTIajU1bC6uvWcDWIPfhNyfHT2WV0szZraCnM9Z5I

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ref_prefixes; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.ref_prefixes DISABLE TRIGGER ALL;

INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('PC', 'posture_control', 'posture_controls', 'Posture Control');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('CD', 'document', 'client_documents', 'Client Document');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('INC', 'incident', 'incidents', 'Incident');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('AST', 'asset', 'assets', 'Asset');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('RSK', 'risk', 'risks', 'Risk');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('VND', 'vendor', 'vendors', 'Vendor / Supplier');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('AUD', 'audit', 'isms_audits', 'ISMS Audit');
INSERT INTO public.ref_prefixes (prefix, entity_type, table_name, description) VALUES ('FND', 'finding', 'document_findings', 'Document Finding');


ALTER TABLE public.ref_prefixes ENABLE TRIGGER ALL;

--
-- PostgreSQL database dump complete
--

\unrestrict xe9pSf6E7VHjdBXLQ6zOSOuTIajU1bC6uvWcDWIPfhNyfHT2WV0szZraCnM9Z5I


-- ── ref_sequences ──
--
-- PostgreSQL database dump
--

\restrict dQFXp5OyPpEH3DccLNkXnwYK1Se0KTs6Ksug6yvYCxVGDJrEtQjKc3IpvJNkXd3

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ref_sequences; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.ref_sequences DISABLE TRIGGER ALL;

INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'AST', 21);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'INC', 3);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'RSK', 36);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'AUD', 3);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'PC', 109);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'VND', 8);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('00000000-0000-0000-0000-000000000001', 'CD', 66);
INSERT INTO public.ref_sequences (tenant_id, prefix, next_seq) VALUES ('77777777-7777-7777-7777-777777777777', 'CD', 13);


ALTER TABLE public.ref_sequences ENABLE TRIGGER ALL;

--
-- PostgreSQL database dump complete
--

\unrestrict dQFXp5OyPpEH3DccLNkXnwYK1Se0KTs6Ksug6yvYCxVGDJrEtQjKc3IpvJNkXd3


-- ── roles ──
--
-- PostgreSQL database dump
--

\restrict F9YHK1CbLKmFOa3Sc4wOee3tokEQ0U19Vs7gV4NfjMPeHbjlbzPpuM4YdVdyugc

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: -
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.roles DISABLE TRIGGER ALL;

INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (1, 'admin', 'Tenant administrator — full access, manages users', true, true, true, true, true, false);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (2, 'compliance_manager', 'Owns the ISMS — manages posture, documents, incidents', true, true, true, false, true, false);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (3, 'dpo', 'Data Protection Officer — full GDPR scope, breach authority', true, true, true, false, true, false);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (4, 'ciso', 'CISO — reads all, writes technical controls only', true, false, true, false, true, false);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (5, 'staff', 'Can submit evidence and view own area only', false, false, true, false, false, false);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (6, 'arion_advisor', 'ArionComply support — reads all, annotates, cannot alter posture', false, false, false, false, true, true);
INSERT INTO public.roles (id, name, description, can_write_posture, can_write_incidents, can_write_documents, can_manage_users, can_view_all, is_arion_staff) VALUES (7, 'auditor', 'External auditor — time-limited read-only access', false, false, false, false, true, false);


ALTER TABLE public.roles ENABLE TRIGGER ALL;

--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.roles_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

\unrestrict F9YHK1CbLKmFOa3Sc4wOee3tokEQ0U19Vs7gV4NfjMPeHbjlbzPpuM4YdVdyugc


COMMIT;
