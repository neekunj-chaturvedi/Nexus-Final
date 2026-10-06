---
doc_id: FAQ-INSURANCE-001
category: faqs
product_line: insurance
tags: [claims, premiums, lapsed_policy, auto_debit]
---

# Insurance FAQs

## Q: What happens if my auto-debit premium payment fails?

For home and motor policies, a single failed auto-debit attempt does not
immediately lapse the policy — the `auto_debit_premium_payment` scenario
tag protects continuity of cover for a grace period (see the relevant
policy wording in `policy_docs/`). The customer can pay manually through
any other allowed method within that window.

## Q: My policy shows as "lapsed" — can I still file a claim?

No. A lapsed policy has no active cover for any scenario, including ones
that would normally be listed as covered. This is why policy
`POL-HL-30093` (status: `lapsed`) has a `rejected` claim (`CLM-40003`)
against it — the rejection reflects the lapsed status, not a dispute about
whether hospitalisation is normally covered.

## Q: How long does a claim review take?

Claim status (`filed`, `under_review`, `approved`, `rejected`) is tracked
live via `insurance_server.get_claim_status`. Nexus can report the current
status but has no settlement authority and cannot change a claim's
outcome.

## Q: Is auto-debit available on every policy type?

No. Home and motor policies generally support auto-debit as a payment
method. Travel policies do not — they are card-only. Always check the
specific policy's `payment_methods_allowed` field rather than assuming
auto-debit is universal across products.
