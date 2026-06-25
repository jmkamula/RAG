---
leaf_id: req:A.5.11:leaver_return_register
control_ref: A.5.11
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Leaver Asset Return Register

> A.5.11 requires every triggered return event to be tracked — invisible leavers are the ones who walk out with assets. The register catalogues every in-flight return: leaver id, trigger type, departure/effective date, asset list (linked to A.5.9 asset register), current status, owner. It is the operational record that proves the return process is actually applied every time, not just on the leavers HR happens to remember to log

<!-- TABLE-COLUMNS leaf:req:A.5.11:leaver_return_register -->
<!-- column: item:A.5.11:reg_leaver_id -->
<!-- column: item:A.5.11:reg_trigger_type -->
<!-- column: item:A.5.11:reg_effective_date -->
<!-- column: item:A.5.11:reg_asset_list -->
<!-- column: item:A.5.11:reg_status -->
<!-- column: item:A.5.11:reg_owner -->
<!-- column: item:A.5.11:reg_access_revoke -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.11:leaver_return_register -->
| Reg Leaver Id | Reg Trigger Type | Reg Effective Date | Reg Asset List | Reg Status | Reg Owner | Reg Access Revoke |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.11:leaver_return_register -->

## Column guidance — what to fill in

### Reg Leaver Id

<<MUST item:A.5.11:reg_leaver_id>>
_Why: 27002:5.11 — visibility_

> _Standard text:_ Each leaver/role-changer captured with a unique identifier (employee or contractor id; do not store sensitive PII beyond what HR retains)

### Reg Trigger Type

<<MUST item:A.5.11:reg_trigger_type>>
_Why: 27002:5.11 — trigger taxonomy_

> _Standard text:_ Trigger type per row (termination / role_change / contract_end / secondment_end / agreement_change)

### Reg Effective Date

<<MUST item:A.5.11:reg_effective_date>>
_Why: Timeline anchor_

> _Standard text:_ Effective date per row (last working day or role-change date — drives return-deadline calculations)

### Reg Asset List

<<MUST item:A.5.11:reg_asset_list>>
_Why: 27002:5.11 + cross-link to [[A.5.9]]_

> _Standard text:_ Per-leaver asset list (link to A.5.9 asset register entries assigned to this person)

### Reg Status

<<MUST item:A.5.11:reg_status>>
_Why: Operational discipline_

> _Standard text:_ Status per row (pending / in_progress / complete / exception / written_off) updated as items are returned

### Reg Owner

<<MUST item:A.5.11:reg_owner>>
_Why: Accountability_

> _Standard text:_ Return owner per row (typically the leaver's line manager + IT custody handler)

### Reg Access Revoke

<<MUST item:A.5.11:reg_access_revoke>>
_Why: 27002:5.11 — logical asset handling_

> _Standard text:_ Access-revocation timestamp per row (when corp accounts/SSO/credentials were disabled — should align with effective date)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Data Preserved

<<SHOULD item:A.5.11:reg_data_preserved>>
_Why: Audit defensibility_

> _Standard text:_ Data-preserved flag per row (org information migrated/captured before wipe)

### Reg Byod Flag

<<SHOULD item:A.5.11:reg_byod_flag>>
_Why: Workforce-model coverage_

> _Standard text:_ BYOD flag per row where leaver used personal device (drives different wipe path — selective MDM removal vs full wipe)
