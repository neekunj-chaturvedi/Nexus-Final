---
doc_id: POLDOC-PAYMENTS-001
category: policy_docs
product_line: cross_product
policy_type: all
related_policy_ids: [POL-IN-30091, POL-IN-30092, POL-HL-30093, POL-TR-30094]
tags: [payment_terms, auto_debit, cross_product, reconciliation]
---

# Meridian Insurance — Cross-Product Payment Terms

This note summarises premium payment terms that apply *across* Meridian's
general insurance and health products, for use when a customer's request
touches both their bank account and their policy (a `cross_product`
request).

## Auto-Debit, Generally

Auto-debit is Meridian's preferred premium collection method and is
described, product by product, as broadly available wherever a policy
lists `auto_debit` in its `payment_methods_allowed` (see the individual
policy wordings in this folder). As a product matter, Meridian actively
encourages customers to move to auto-debit for continuity of cover.

## Why This Document Is Not Enough on Its Own

This document, and the individual policy wordings alongside it, describe
what Meridian's insurance *product* allows. They say nothing about whether
a specific customer's *bank account* can currently support an outbound
auto-debit mandate. That depends on the account's live status — `active`,
`restricted`, or `frozen` — which only `banking_server` can answer, and
which can change independently of anything written here (for example, a
restriction placed for KYC re-verification).

**Whenever this document's general description of auto-debit availability
conflicts with a customer's live account status, the live account status
from `banking_server` is authoritative.** The correct behaviour is not to
silently prefer one source — it is to surface the disagreement to the
validation step so a human can see both facts side by side.
