---
doc_id: POLDOC-MOTOR-001
category: policy_docs
product_line: insurance
policy_type: general_motor
related_policy_ids: [POL-IN-30092]
tags: [motor_insurance, payment_terms, auto_debit, coverage, collision, theft]
---

# Meridian General Motor Insurance — Policy Wording (Product Class: general_motor)

## 1. Scope of Cover

Applies to all Meridian General Motor Insurance policies (policy numbers
prefixed `GIP`), including policy **POL-IN-30092**. As with every Meridian
policy wording, customer-specific details must be read live from
`insurance_server.get_policy_details`, not inferred from this document.

## 2. Covered Scenarios

- `collision` — accidental damage from collision with another vehicle or
  object
- `theft` — theft of the insured vehicle
- `auto_debit_premium_payment` — premium continuity protection identical to
  the General Home product (see §4 of this document)

## 3. Exclusions

- `racing` — any damage sustained while the vehicle is used in a race,
  rally, or speed trial is excluded in full

## 4. Premium Payment Terms

**Auto-debit is available as a payment method for all Meridian Motor
policies with a linked bank account in good standing.** This is a
product-level rule and applies across the General Motor book by default.

> As with every Meridian product, this clause describes product-level
> eligibility only. It is **not** a guarantee that auto-debit will succeed
> for a specific customer: if the linked account carries a restriction
> (for example, a hold pending address or KYC re-verification), outbound
> auto-debit mandates on that account are suspended by the bank regardless
> of what this policy wording says is generally allowed. In that
> situation the structured, live account status from `banking_server`
> overrides this document, and the conflict must be surfaced rather than
> resolved by assuming either source is correct.

## 5. Claims

Claims are tracked via `insurance_server.get_claim_status` under the
relevant scenario tag. This wording does not grant settlement authority.
