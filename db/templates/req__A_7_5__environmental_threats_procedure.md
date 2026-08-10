---
leaf_id: req:A.7.5:environmental_threats_procedure
control_ref: A.7.5
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Protection Against Physical and Environmental Threats Procedure

<<DOC_CONTROL>>

> A.7.5 requires protection against physical and environmental threats. The procedure documents threat assessment, protection measures per threat, detection systems, response, and recovery. The threat register, applicable-sites scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how your organization protects against physical and environmental threats, including how you assess risks, implement safeguards, detect incidents, and respond or recover from them.

## When to use it

Use this procedure whenever you need to show how your environment is protected from physical and environmental risks. Review and update it whenever there are changes to your threats, locations, or protection measures.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of threats and sites you need to document in your threat register.

## 1. Threat assessment per site (fire, flood, earthquake, civil unrest, power, vandalism, climate-related risk)

<<MUST item:A.7.5:threat_assessment>>
_Why: 27002:7.5 — natural disasters + intentional + unintentional_

<<GUIDANCE>>

<<TEXT>>

## 2. Protection measures stated per identified threat (passive — building design; active — detection + response)

<<MUST item:A.7.5:protection_per_threat>>
_Why: 27002:7.5 — designed and implemented_

<<GUIDANCE>>

<<TEXT>>

## 3. Detection systems (smoke, heat, water leak, temperature, motion, glass-break, seismic where relevant)

<<MUST item:A.7.5:detection>>
_Why: 27002:7.5 — protection_

<<GUIDANCE>>

<<TEXT>>

## 4. Response procedures per threat type (evacuation, suppression, shutdown, BCP activation cross-link A.5.29/A.5.30)

<<MUST item:A.7.5:response>>
_Why: 27002:7.5 — implemented_

<<GUIDANCE>>

<<TEXT>>

## 5. Recovery from environmental incidents (cleanup, salvage, post-incident assessment, lessons → A.5.27)

<<MUST item:A.7.5:recovery>>
_Why: 27002:7.5 — protection_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Insurance considerations and coverage referenced

<<SHOULD item:A.7.5:insurance>>
_Why: Residual risk handling_

<<GUIDANCE>>

<<TEXT>>

### 2. Climate-related risk evolution noted (sea-level, heatwave intensity affecting cooling, wildfire) — periodic re-assessment trigger

<<SHOULD item:A.7.5:climate_risk>>
_Why: Forward-looking_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
