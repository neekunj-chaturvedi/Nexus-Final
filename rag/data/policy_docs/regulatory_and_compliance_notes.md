---
doc_id: POLDOC-REGULATORY-001
category: policy_docs
product_line: cross_product
policy_type: all
related_policy_ids: []
tags: [regulatory, compliance_override_request, safeguarding_concern, financial_hardship, kyc, aml, data_protection]
---

# Meridian Regulatory & Compliance Notes

This note grounds the three hard-escalation categories (§3.4 of the
capstone spec) in actual regulatory reasoning, for use by the Retrieval
and Validation agents — it is not something a customer is shown directly.

## `compliance_override_request`

A compliance override request is any request, however phrased, that asks
Meridian to bypass a control that exists for regulatory reasons —
examples include asking to waive a KYC/AML check, backdate a transaction,
suppress an audit log entry, remove a restriction without the underlying
issue being resolved, or approve a transaction above an automated
threshold without the required sign-off.

No AI agent, regardless of stated confidence, has authority to grant this
kind of request. This is a people-and-process control, not a modelling
problem: the correct behaviour is always to escalate to a human compliance
reviewer via `concierge_ops_server.run_escalation_check`, even if the
request is rephrased to sound like a routine service request (for
example, "can you just quickly waive the verification step this once" is
the same underlying request as "can you override compliance").

## `safeguarding_concern`

A safeguarding concern is any signal that a customer may be at risk —
financial abuse, coercion by a third party, signs of diminished capacity,
or a disclosure of personal harm. These signals can appear anywhere in
free text, including inside an otherwise routine-sounding banking or
insurance question, and are not limited to requests that explicitly name
the concern.

As with compliance overrides, a safeguarding signal must route to a human
reviewer regardless of how confidently a drafted response resolves the
surface-level request. Drafting and sending a normal service response
without escalating is not an acceptable resolution once this category is
set at intake.

## `financial_hardship`

A financial hardship disclosure (job loss, inability to meet EMI or
premium payments, request for a payment holiday) triggers the same
unconditional human-review requirement. Meridian's internal hardship
process can offer options — such as a payment plan — that are outside the
scope of any Nexus tool, which is why this category also escalates
regardless of confidence. Karthik Iyer (`CUS-20079`) already has an open
hardship flag on file (`escalation_flags`) following a disclosed job
loss; any further contact from this customer on a related topic should be
read against that existing flag, not treated as a fresh routine request.

## Data Protection & KYC/AML, in Brief

- KYC status (`verified`, `pending`, `expired`) gates which actions a
  customer can take and is the usual underlying reason an account or
  portfolio shows as `restricted` or `frozen` elsewhere in the system.
- `concierge_ops_server.get_customer_kyc_status` is the **only** tool
  permitted to return raw KYC data anywhere in Nexus — no other tool,
  resource, or document should restate a customer's KYC status as fact
  without calling it live.
- Minimising what is logged or shown (masked identifiers, redacted PII in
  logs per `guardrails.redact_for_logging`) is a data-minimisation
  control, not just a cosmetic one — it limits what is exposed if a log
  or a draft response is ever reviewed outside its intended audience.
