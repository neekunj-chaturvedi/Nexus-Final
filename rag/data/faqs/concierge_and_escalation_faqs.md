---
doc_id: FAQ-CONCIERGE-001
category: faqs
product_line: cross_product
tags: [escalation, kyc, complaint, hardship, safeguarding]
---

# Concierge & Escalation FAQs

## Q: When does Nexus escalate a request to a human?

Two independent triggers can send a request to a human reviewer:

1. **Confidence-based** — the Validation Agent's confidence in the drafted
   response falls below the configured threshold.
2. **Hard, category-based** — the request was classified at intake with
   one of three categories that always escalate, no matter how confident
   the draft is: `financial_hardship`, `safeguarding_concern`, or
   `compliance_override_request`.

The hard-category trigger exists specifically so that a customer
disclosing hardship (or a bad-faith attempt to talk an agent out of
escalating) cannot be smoothed over by a confident-sounding draft. It is
enforced by a deterministic tool call
(`concierge_ops_server.run_escalation_check`), not by any agent's own
judgement, and does not change based on how the request is phrased.

## Q: What does a KYC status of "pending" or "expired" mean for service?

`pending` KYC means verification is incomplete and certain actions may be
limited until it's done. `expired` KYC means a previously verified
customer now needs re-verification; this is frequently the underlying
cause of an account or portfolio showing as restricted or frozen
elsewhere in the system.

## Q: How are customer notifications sent?

`concierge_ops_server.send_customer_notification` sanitises the outbound
message, checks the customer's KYC status before sending to certain
channels, and writes a record of the send. Every notification send and
every escalation decision is also recorded via
`concierge_ops_server.write_audit_log` for compliance review.
