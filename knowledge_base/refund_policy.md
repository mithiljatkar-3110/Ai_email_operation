# FlowStack Refund and Retention Policy

**Document ID:** POL-REFUND-001  
**Version:** 2.4  
**Effective Date:** January 1, 2024  
**Owner:** Customer Success & Finance  
**Classification:** Internal / Customer-Facing

---

## 1. Purpose

This policy defines when FlowStack issues refunds vs. service credits, the 14-day refund window, exception approval paths, and the churn retention playbook for at-risk accounts.

Support agents must **not** promise refunds outside this policy without Finance approval.

---

## 2. Standard Refund Policy

### 2.1 14-Day Money-Back Guarantee (Self-Serve Only)

New customers on **Starter** and **Standard** tiers who purchase via credit card may request a **full refund within 14 calendar days** of initial purchase if:

- They have used fewer than 1,000 workflow executions
- No custom implementation services were delivered
- Account is not under investigation for abuse

Refund requests after 14 days are **not eligible** for automatic refund on self-serve plans.

### 2.2 Annual Contract Refunds (Mid-Market and Enterprise)

**No refunds after 14 days** from contract start date or invoice payment date, whichever is later, unless:

1. FlowStack fails to deliver the service (material breach of SLA sustained >30 days)
2. Mutual termination is negotiated in writing
3. Executive exception is approved (see Section 4)

Remaining contract value is **not** refunded for:

- Customer business changes (layoffs, budget cuts, project cancellation)
- Dissatisfaction with features on roadmap
- Failure to adopt the platform internally
- Competitor selection after contract signature

### 2.3 Professional Services

Implementation, training, and custom development fees are **non-refundable** once work has commenced. If work has not started, up to 100% may be refunded minus 10% administrative fee.

---

## 3. Credits vs. Refunds

| Situation | Default Remedy |
|-----------|----------------|
| SLA breach (uptime) | Service credit on next invoice |
| Billing error (overcharge) | Refund or credit (customer choice) |
| Duplicate charge | Full refund within 5 business days |
| Feature outage <24 hours | Service credit per `sla_policy.md` |
| P0 incident with business impact | Service credit; refund only if credit insufficient per negotiation |
| Goodwill gesture (minor issue) | Service credit up to 1 month (CSM approval) |
| Goodwill gesture (major issue) | Up to 3 months credit (Director CS approval) |

**Guidance:** Always offer credits before refunds. Credits preserve revenue and keep the customer on platform.

---

## 4. Refund Exception Process

### 4.1 Approval Matrix

| Refund Amount | Approver |
|---------------|----------|
| < $500 | Support Lead |
| $500 – $5,000 | Customer Success Manager |
| $5,000 – $25,000 | Director of Customer Success |
| $25,000 – $100,000 | VP Customer Success + Finance |
| > $100,000 | CFO |

### 4.2 Required Documentation

Every exception refund requires:

1. CRM case with full thread history
2. Reason code (billing error, SLA breach, executive escalation, legal settlement)
3. Approval email or ticket comment from authorized approver
4. Finance ticket for payment processing (5–10 business days)

---

## 5. Churn Retention Playbook

### 5.1 Trigger Conditions

Activate retention protocol when a customer:

- Requests cancellation or refund
- Mentions switching to a competitor
- Threatens public review (G2, Trustpilot, social media)
- Shows deteriorating sentiment across 3+ support interactions
- Is flagged VIP or Enterprise tier

### 5.2 Retention Steps (In Order)

1. **Acknowledge and empathize** — Do not argue. Confirm you understand the impact.
2. **Diagnose root cause** — Product gap, support failure, billing surprise, champion departure?
3. **Offer appropriate remedy:**
   - Technical issue → Escalate to engineering, provide incident timeline
   - Billing issue → Review invoice, apply credit if warranted
   - Feature gap → Roadmap discussion, beta access, workaround
   - Price sensitivity → Renewal discount (max 25% one-time per `pricing_policy.md`)
4. **Executive outreach** — Accounts >$50K ACV: offer call with CSM + Account Executive within 48 hours
5. **Document outcome** — Win, save-with-credit, or churn with exit interview

### 5.3 Public Review Threats

If a customer threatens a public negative review:

- **Do not** offer refunds beyond policy limits to suppress reviews (legal risk)
- Escalate to `escalation_matrix.md` → PR Crisis / Reputation track
- CSM drafts response citing specific remediation steps taken
- Legal review if threat includes defamation, false claims, or regulatory action

### 5.4 Refund + Review Scenario (e.g., Retail Customer Complaint)

When a customer demands a refund due to service quality AND threatens public escalation:

1. Retrieve full thread history and account status
2. Check SLA eligibility for credits (not automatic refund)
3. Apply retention playbook Section 5.2
4. If refund requested past 14-day window: explain policy, offer credit + priority support
5. Escalate to human agent with pre-filled brief per `escalation_matrix.md`
6. **Never auto-reply** with generic "we'll look into it" — cite specific policies and next steps

---

## 6. Chargebacks

All chargebacks are handled by Finance + Legal. Support must not issue duplicate refunds for chargebacked amounts. Account is suspended pending resolution.

---

## 7. Tax and Currency

Refunds are issued in the original payment currency. Tax refunded only where legally required. International wire refunds may incur banking fees borne by customer unless billing error.

---

## 8. Prohibited Refund Commitments

Support and AI agents **must not**:

- Promise refunds outside the 14-day self-serve window without approval
- Offer cash refunds in lieu of credits without Finance approval
- Refund annual contracts pro-rata for seat reductions
- Commit to refunds in response to legal threats (route to Legal)

---

## 9. Contact

- **Refund requests:** billing@flowstack.io
- **Retention escalations:** retention@flowstack.io
- **Finance processing:** finance-refunds@flowstack.io
