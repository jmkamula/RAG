---
name: incident-obligations-model
description: "Architecture decision for how incidents, events, classifications, and obligations relate across Postgres and Neo4j. Settled 2026-05-14 with user."
metadata: 
  node_type: memory
  type: project
  originSessionId: f7c33fad-b32e-4557-9944-b406bcbbd8ee
---

**Two-layer model for incident handling**, settled in design conversation 2026-05-14.

- **Neo4j (curated, tenant-agnostic)** holds Event TYPE definitions and their *fully-formed fulfilment requirements*: `:Event -[TRIGGERS_OBLIGATION]-> :RequirementNode` (which control fires, deadline, rationale) and `:Event -[REQUIRES_DOCUMENT]-> :DocumentRequirement` (what evidence proves resolution).
- **Postgres (per-tenant)** holds INSTANCES and resolution STATE: `incidents` (what happened), `incident_classifications` (which Events this incident manifests — 1 incident → N events), `incident_obligations` (one row per (incident, RequirementNode) materialized from the union of all linked Events' triggers; carries `deadline_at`, `is_met`, `met_at`), `incident_documents` (uploaded evidence linked back to incident + `document_role`, satisfies REQUIRES_DOCUMENT items).

**Key cardinality:** an incident is an occurrence of ONE OR MORE events. A ransomware hit on a customer DB simultaneously instantiates `event:personal_data_breach` (GDPR), `event:malicious_code_incident` (ISO 27035), and possibly `event:supervisory_authority_inquiry`. Obligations materialized = union across all linked Events.

**Classification, not enum:** `incidents` should NOT have a single `incident_type` text column. Different standards classify on orthogonal axes (ISO 27035 mechanism category, GDPR CIA dimension, GDPR notifiability, NIST attack vector, NIS2 significance, DORA severity, HIPAA breach presumption, PCI compromise status). One incident carries multiple classifications, each drawn from a *standard-defined* curated vocabulary. Classifications are what bind to Neo4j Events, not the incident directly.

**Vocabulary storage (Option A, chosen 2026-05-14):** classification dimensions and allowed values live in Neo4j alongside Events, since they are definitions: `(:ClassificationDimension {standard_id, dimension}) -[:ALLOWS]-> (:ClassificationValue {value}) -[:MANIFESTS_AS]-> (:Event)`. This keeps the rule "definitions in Neo4j, instances in Postgres" clean and makes the materializer a single Cypher hop from a Postgres classification triple to the bound Event(s) to that Event's `TRIGGERS_OBLIGATION` set. Rejected alternatives: YAML in repo (needs deploy + string lookup, not graph edge); Postgres reference table (splits definitions across two stores).

**Why:** the standards literature doesn't agree on one incident-type taxonomy. Each standard defines its own. Forcing them into one column either loses fidelity (too coarse to trigger the right obligations) or becomes a brittle synthetic concatenation. Curated per-standard vocabularies keep extensibility on the curator side (new standard → new dimensions + Events) rather than user side.

**How to apply:** when working on incident-related code (creation, classification, obligation materialization, fulfillment checking, expander reads), enforce that:
1. Events live only in Neo4j as type defs; never project `:Incident` nodes to Neo4j.
2. Mapping from real incident → Event(s) goes via classification rows, not a single column.
3. Obligation rows are materialized in Postgres at incident-creation time by querying Neo4j for the matched Events' `TRIGGERS_OBLIGATION` set.
4. `is_met` flips by comparing `incident_documents` `document_role` rows against the Event's `REQUIRES_DOCUMENT → DocumentRequirement` set.
5. The reader path (currently `rag/graph_expander.py:930 get_incident_obligations`) should `SELECT FROM incident_obligations` in Postgres, then enrich each row with Neo4j context — not the other way around.

**Current implementation gap** (as of 2026-05-14): table exists with 0 rows; no writer; no classifications table yet; reader queries Neo4j for tenant data which is the wrong direction. Two existing closed incidents need backfill once the writer lands. `incidents.neo4j_synced` / `incidents.neo4j_node_id` columns are dead under this design — were reserved for an abandoned "project Incident to Neo4j" idea.

**Schema decisions locked 2026-05-14:**

1. **Neo4j shape:** `(:ClassificationDimension {id, standard_id, dimension, title, description, clause_ref, is_combinable})` and `(:ClassificationValue {id, standard_id, dimension, value, title, description})` with edges `(:ClassificationDimension)-[:ALLOWS]->(:ClassificationValue)` and `(:ClassificationValue)-[:MANIFESTS_AS]->(:Event)` (0..N). Ids namespaced like Events: `classdim:GDPR:breach_cia`, `classval:GDPR:breach_cia:confidentiality`.

2. **Postgres `incident_classifications`:** PK `(incident_id, standard_id, dimension, value)`; columns for `source` (`workbook|manual|api|derived|llm`), `confidence` (nullable, NULL = curator-certain), `classified_at/_by`, full soft-delete + retention block matching siblings; RLS by `app.tenant_id`; `ON DELETE CASCADE` from `incidents`; lookup index `(standard_id, dimension, value) WHERE is_active=true`.

3. **MANIFESTS_AS cardinality 0..N allowed** — values without bound events act as pure labels for reporting. Materializer treats them as zero-obligation contributions.

4. **`incidents.incident_type` dropped** — replaced entirely by classification rows; importer rewrites to produce N classifications per incident.

5. **`is_combinable` enforced at application layer**, not DB trigger. The writer already calls Neo4j to validate the `(standard_id, dimension, value)` triple and read `MANIFESTS_AS` edges; reading `is_combinable` is one extra property in the same Cypher hit. DB-level enforcement would either need to reach into Neo4j from a trigger or mirror the flag into Postgres — both violate the Postgres=instances/Neo4j=definitions split.

6. **Low-confidence classifications land `is_active=true`**, surfaced in a review queue rather than gated by approval. Reflects the broader [[human-in-the-loop-positioning]] principle.

**Seed (v1) locked 2026-05-14:**
- **2 dimensions only:** GDPR `breach_cia` (combinable, MANIFESTS_AS → `event:personal_data_breach`); ISO 27035 `category` (non-combinable, all values MANIFESTS_AS → new `event:information_security_incident`). Distinct ISO 27035 values are reporting labels at v1; curator can split into mechanism-specific events later if obligations diverge.
- **GDPR `notifiability` deliberately excluded** — it's an outcome (post-risk-assessment state) tracked by `incidents.authority_notified` / `incidents.data_subjects_notified`, not a classification. Art. 33/34 obligations always materialize from `event:personal_data_breach`; the fulfillment check marks them met/N-A based on those columns.
- **New `event:information_security_incident`** to be added to Neo4j with TRIGGERS_OBLIGATION on `ISO27001:2022:A.5.26`, `A.5.27`, `6.1.2` (symmetric to `event:personal_data_breach` minus GDPR articles).
- **Workbook translation:** `InfoSec inc.` → `(ISO_27035, category, unspecified)`; `PII` → `(GDPR, breach_cia, confidentiality)` *derived with confidence=0.5* plus `(ISO_27035, category, unspecified)`; `both` → union of above; `non breach` → zero classifications.
- **`schema_v7.sql` is purely additive** at this step — only adds `incident_classifications`. Dead-column drops on `incidents` (`incident_type`, `neo4j_synced`, `neo4j_node_id`) are deferred to the importer-rewrite migration because (a) `v_incidents_open` view expands `i.*` and would also need refreshing, (b) importer + downstream readers still reference `incident_type`. Bundling all three drops + view refresh + importer rewrite together avoids a broken intermediate state.

Related: [[incident-type-classification-axes]], [[human-in-the-loop-positioning]]
