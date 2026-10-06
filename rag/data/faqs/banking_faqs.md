---
doc_id: FAQ-BANKING-001
category: faqs
product_line: banking
tags: [auto_debit, account_status, restricted, frozen, transactions]
---

# Banking FAQs

## Q: How do I set up auto-debit from my savings or current account?

Auto-debit mandates are set up against a specific account, not a customer
generally. The account must be `active` with `auto_debit_allowed = true`
on its live record. If the account shows a restriction — for example
pending address re-verification — outbound mandates (including new
auto-debit setups for insurance premiums) are suspended until the
restriction is cleared. This is an account-level control and is unrelated
to whether the destination policy itself allows auto-debit as a payment
method.

## Q: Why is my account showing as "restricted"?

Accounts are placed into a `restricted` state for operational reasons such
as pending KYC or address re-verification. A restricted account can still
receive credits in most cases but outbound mandates and certain debit
instructions are suspended until the restriction is lifted. The specific
`restriction_reason` on the account record explains why.

## Q: Why is my account "frozen"?

A `frozen` account most commonly reflects an expired KYC status on the
customer record. Both inbound and outbound activity can be affected. The
customer should complete KYC re-verification to lift a freeze; this is not
something Nexus can resolve automatically.

## Q: Can I see all accounts linked to me?

Yes — `banking_server.get_linked_accounts` returns every account tied to a
customer ID, with the same field minimisation rules as a single account
lookup.
