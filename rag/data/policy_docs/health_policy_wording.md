---
doc_id: POLDOC-HEALTH-001
category: policy_docs
product_line: insurance
policy_type: health
related_policy_ids: [POL-HL-30093]
tags: [health_insurance, hospitalisation, daycare, lapsed, cosmetic]
---

# Meridian Health Insurance — Policy Wording (Product Class: health)

## 1. Scope of Cover

Applies to all Meridian Health Insurance policies (policy numbers prefixed
`HLP`), including policy **POL-HL-30093**.

## 2. Covered Scenarios

- `hospitalisation` — inpatient treatment of 24 hours or more at a network
  or non-network hospital, subject to the sum insured
- `daycare` — listed procedures not requiring a 24-hour admission

## 3. Exclusions

- `cosmetic` — cosmetic or purely elective procedures are never covered

## 4. Lapsed Policies

A policy showing `status = lapsed` on the live record has **no active
cover**. No scenario tag, including `hospitalisation`, is payable while a
policy is lapsed, regardless of the scenario normally being covered under
§2. Reinstatement requires a fresh underwriting review and is outside the
scope of any Nexus tool — a lapsed-policy claim query must be routed to a
human advisor, not answered as if cover were active.

## 5. Claims

Claims are tracked via `insurance_server.get_claim_status`. A claim filed
against a lapsed policy (see claim `CLM-40003` against policy
`POL-HL-30093`) should be expected to resolve as `rejected` for that
reason; this document does not itself decide claim outcomes.
