---
doc_id: TMPL-GENERAL-001
category: communication_templates
product_line: cross_product
tags: [general, routine, drafting_agent_default]
channel: [email, sms, chat]
---

# Template: General Routine Response

Default shape for the Drafting Agent's answer to a routine, non-escalated
request. The agent fills each placeholder only from the grounded context
assembled by the retrieval layer — never from unsupported inference.

---

Hello {{customer_name}},

{{direct_answer_to_request}}

{{supporting_detail_grounded_in_retrieved_context}}

{{next_step_or_none}}

Meridian Financial Group
