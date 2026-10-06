---
doc_id: TMPL-AUTODEBIT-001
category: communication_templates
product_line: cross_product
tags: [auto_debit, confirmation, cross_product]
channel: [email]
---

# Template: Auto-Debit Setup Outcome

Use for both successful and blocked auto-debit setup outcomes arising from
a cross-product request (bank account + insurance policy). Select the
block matching `setup_outcome`.

---

Hello {{customer_name}},

You asked about setting up auto-debit for your policy
{{masked_policy_id}} from your account {{masked_account_id}}.

**If {{setup_outcome}} == confirmed:**
Good news — auto-debit is confirmed. Your policy allows this payment
method and your account is in good standing, so premiums will now be
collected automatically each {{premium_frequency}}.

**If {{setup_outcome}} == blocked_account_restricted:**
We're unable to set this up right now. While your policy allows auto-debit
as a payment method, your linked account currently has a restriction
({{restriction_reason}}) that suspends new outbound mandates. Once that's
resolved, we can set this up — no action needed from you to retry, we'll
confirm once it's lifted.

**If {{setup_outcome}} == not_offered_for_product:**
Auto-debit isn't offered for this product type. Please use one of the
allowed payment methods listed on your policy instead.

Meridian Financial Group
