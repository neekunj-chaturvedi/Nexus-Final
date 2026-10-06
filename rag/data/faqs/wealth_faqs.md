---
doc_id: FAQ-WEALTH-001
category: faqs
product_line: wealth
tags: [portfolio, suitability, risk_profile]
---

# Wealth FAQs

## Q: How is fund suitability decided?

Every investment product declares which risk profiles it suits
(`conservative`, `moderate`, `aggressive`) in its fund fact sheet.
`wealth_server.check_product_suitability` compares a customer's stated
risk profile against that list — it does not consider portfolio size,
goals, or anything else outside the risk-profile match. A product
suggestion outside the customer's risk profile should fail this check.

## Q: Why does my portfolio summary hide some figures?

Portfolio data is minimised according to `caller_scope`, the same pattern
used for bank accounts. A basic scope sees status and top-level value; a
fuller scope is required to see individual holdings. Portfolio numbers are
always masked to their last four digits regardless of scope.

## Q: What does a "restricted" portfolio mean?

A restricted portfolio (see `PORT-20080`) typically reflects an open
compliance or KYC issue on the linked customer record, similar to a
restricted bank account. Trading or rebalancing instructions against a
restricted portfolio should not be actioned without that issue being
resolved first.
