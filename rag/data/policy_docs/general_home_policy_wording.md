---
doc_id: POLDOC-HOME-001
category: policy_docs
product_line: insurance
policy_type: general_home
related_policy_ids: [POL-IN-30091]
tags: [home_insurance, payment_terms, auto_debit, coverage, fire, flood, theft]
---

# Meridian General Home Insurance — Policy Wording (Product Class: general_home)

## 1. Scope of Cover

This policy wording applies to all Meridian General Home Insurance policies
(policy numbers prefixed `GIP`), including policy **POL-IN-30091**. It
describes the standard terms shared by every policy in this product class.
Customer-specific figures (premium amount, renewal date, status) are not
repeated here — those must always be read from the live policy record via
`insurance_server.get_policy_details`, never assumed from this document.

## 2. Covered Scenarios

Unless specifically excluded (see §3), the following scenario tags are
covered under a General Home policy in good standing:

- `fire` — structural and contents damage caused by fire
- `flood` — water damage from external flooding events
- `theft` — burglary and forced-entry theft of insured contents
- `auto_debit_premium_payment` — premium continuity protection: a missed
  premium due solely to a failed auto-debit attempt does not, by itself,
  lapse the policy within the grace period described in §4

## 3. Exclusions

- `wear_and_tear` — gradual deterioration is never covered
- `war` — damage arising from war or war-like operations is excluded

## 4. Premium Payment Terms

Premiums on a General Home policy may be paid through any of the payment
methods marked as allowed on the individual policy record (see
`get_policy_details.payment_methods_allowed`). In general, Meridian permits
home insurance premiums to be collected by **auto-debit from a linked
savings or current account**, provided the policy itself lists `auto_debit`
as an allowed method.

> **Important — this clause describes the general product rule, not any
> single customer's eligibility.** Auto-debit from a specific account can
> still fail or be blocked for reasons that live on the *account*, not the
> policy — for example an account that is restricted, frozen, or pending
> KYC re-verification. The customer's live account status, retrieved from
> `banking_server`, is always authoritative over this general policy
> wording when the two disagree. If a customer's account is restricted,
   auto-debit must not be presented as available even though this clause
   describes it as generally permitted for the product.

A missed auto-debit attempt triggers a 15-day grace period before the
policy lapses. Within that window, the customer may pay manually through
any other allowed method without losing continuous-coverage status.

## 5. Claims

Claims against a General Home policy are filed under the relevant scenario
tag (see §2) and tracked via `insurance_server.get_claim_status`. This
document does not grant settlement authority; claim outcomes are decided
through Meridian's claims operations process, not by this wording alone.
