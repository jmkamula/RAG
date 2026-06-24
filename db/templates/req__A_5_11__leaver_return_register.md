---
leaf_id: req:A.5.11:leaver_return_register
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
---

# Leaver Asset Return Register

> A.5.11 requires every triggered return event to be tracked — invisible leavers are the ones who walk out with assets. The register catalogues every in-flight return: leaver id, trigger type, departure/effective date, asset list (linked to A.5.9 asset register), current status, owner. It is the operational record that proves the return process is actually applied every time, not just on the leavers HR happens to remember to log

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Each leaver/role-changer captured with a unique identifier (employee or contractor id; do not store sensitive PII beyond what HR retains)

<<MUST item:A.5.11:reg_leaver_id>>
_Why: 27002:5.11 — visibility_

<<TEXT>>

## 2. Trigger type per row (termination / role_change / contract_end / secondment_end / agreement_change)

<<MUST item:A.5.11:reg_trigger_type>>
_Why: 27002:5.11 — trigger taxonomy_

<<TEXT>>

## 3. Effective date per row (last working day or role-change date — drives return-deadline calculations)

<<MUST item:A.5.11:reg_effective_date>>
_Why: Timeline anchor_

<<TEXT>>

## 4. Per-leaver asset list (link to A.5.9 asset register entries assigned to this person)

<<MUST item:A.5.11:reg_asset_list>>
_Why: 27002:5.11 + cross-link to [[A.5.9]]_

<<TEXT>>

## 5. Status per row (pending / in_progress / complete / exception / written_off) updated as items are returned

<<MUST item:A.5.11:reg_status>>
_Why: Operational discipline_

<<TEXT>>

## 6. Return owner per row (typically the leaver's line manager + IT custody handler)

<<MUST item:A.5.11:reg_owner>>
_Why: Accountability_

<<TEXT>>

## 7. Access-revocation timestamp per row (when corp accounts/SSO/credentials were disabled — should align with effective date)

<<MUST item:A.5.11:reg_access_revoke>>
_Why: 27002:5.11 — logical asset handling_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Data-preserved flag per row (org information migrated/captured before wipe)

<<SHOULD item:A.5.11:reg_data_preserved>>
_Why: Audit defensibility_

<<TEXT>>

### 2. BYOD flag per row where leaver used personal device (drives different wipe path — selective MDM removal vs full wipe)

<<SHOULD item:A.5.11:reg_byod_flag>>
_Why: Workforce-model coverage_

<<TEXT>>
