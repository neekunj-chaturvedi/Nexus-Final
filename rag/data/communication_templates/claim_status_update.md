---
doc_id: TMPL-CLAIM-STATUS-001
category: communication_templates
product_line: insurance
tags: [claims, status_update]
channel: [email, sms, chat]
---

# Template: Claim Status Update

Use when responding to a claim status query. Always insert the masked
claim/policy identifiers only — never the raw claim or policy number.

---

Hello {{customer_name}},

Here's the latest on your claim {{masked_claim_id}} under policy
{{masked_policy_id}}:

**Status:** {{claim_status}}
**Last updated:** {{last_updated_date}}

{{status_specific_note}}

If you have questions about this update, reply here and we'll help
further.

Meridian Financial Group
