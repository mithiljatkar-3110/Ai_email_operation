# FlowStack Pricing Policy

**Document ID:** POL-PRICING-001  
**Version:** 3.2  
**Effective Date:** January 1, 2024  
**Owner:** Revenue Operations  
**Classification:** Internal / Customer-Facing

---

## 1. Overview

FlowStack is an enterprise workflow automation and customer operations platform sold on a per-seat, annual subscription basis. This policy governs list pricing, discounts, billing mechanics, and contractual pricing exceptions for all commercial accounts.

All quotes, order forms, and self-serve checkout flows must comply with this policy unless explicitly approved by the VP of Sales or Finance.

---

## 2. Subscription Tiers

### 2.1 Starter

- **Price:** $29 per seat / month (billed annually at $348/seat/year)
- **Included:** Up to 5 seats, 10,000 workflow executions/month, email support (48h SLA)
- **Target customer:** Small teams, pilots, and proof-of-concept deployments
- **Minimum contract:** 12 months
- **Overage:** $0.002 per additional workflow execution

### 2.2 Standard

- **Price:** $79 per seat / month (billed annually at $948/seat/year)
- **Included:** Unlimited seats, 100,000 workflow executions/month, priority email support (24h SLA), SSO (SAML), audit logs (90 days)
- **Target customer:** Mid-market companies with 20–200 seats
- **Minimum contract:** 12 months
- **Overage:** $0.0015 per additional workflow execution

### 2.3 Professional

- **Price:** $149 per seat / month (billed annually at $1,788/seat/year)
- **Included:** Everything in Standard plus dedicated CSM (accounts >100 seats), 500,000 workflow executions/month, advanced RBAC, audit logs (1 year), sandbox environment
- **Target customer:** Scaling organizations with compliance requirements
- **Minimum contract:** 12 months

### 2.4 Enterprise

- **Price:** Custom — typically $120–$220 per seat / month depending on volume, term, and modules
- **Included:** Everything in Professional plus custom SLA, HIPAA BAA, dedicated infrastructure options, 24/7 phone support, unlimited executions (fair use), custom integrations
- **Minimum contract:** 24 months for net-new Enterprise deals >200 seats
- **Procurement:** Requires signed Order Form, MSA, and DPA where applicable

---

## 3. Nonprofit and Education Discounts

### 3.1 Eligibility

Registered 501(c)(3) nonprofit organizations, registered charities (UK/EU), and accredited educational institutions (K-12 and higher education) are eligible for nonprofit pricing on **Standard** and **Professional** tiers only.

Enterprise tier nonprofit pricing requires VP Sales approval.

### 3.2 Discount Structure

| Tier | Standard Discount | Maximum Approved Discount |
|------|-------------------|---------------------------|
| Standard | **30% off list price** | 40% (VP Sales approval) |
| Professional | 20% off list price | 30% (VP Sales approval) |
| Enterprise | Case-by-case | 15% baseline |

**Example:** A 12-seat nonprofit on Standard pays:
- List: 12 × $948 = $11,376/year
- With 30% discount: **$7,963.20/year** ($663.60/month equivalent)

### 3.3 Verification Requirements

Customers must provide one of the following before discount activation:

1. IRS Determination Letter (US 501(c)(3))
2. Charity Commission registration (UK)
3. `.edu` email domain + institutional verification for education
4. NGO registry documentation (international)

Discounts are applied at renewal only if documentation remains valid. Sales may grant a 30-day provisional discount while verification is pending.

### 3.4 Prohibited Use

Nonprofit pricing may not be resold, transferred to for-profit subsidiaries, or applied to government agencies (see Section 6 for government pricing).

---

## 4. Pro-Rata Billing Rules

### 4.1 Mid-Cycle Seat Additions

When seats are added mid-billing cycle, charges are calculated pro-rata for the remaining days in the current term.

**Formula:**

```
Pro-rata charge = (Annual seat price ÷ 365) × Remaining days × New seats added
```

**Example:** Customer on Standard ($948/seat/year) adds 5 seats with 180 days remaining:

```
($948 ÷ 365) × 180 × 5 = $2,338.36
```

### 4.2 Mid-Cycle Seat Removals

Seat reductions take effect at the **next renewal**. FlowStack does not provide pro-rata refunds for removed seats mid-term unless required by local consumer law or explicitly negotiated in the MSA.

### 4.3 Tier Upgrades

Upgrading tiers (e.g., Standard → Professional) triggers immediate pro-rata charge for the price difference on all active seats for the remainder of the term. Downgrades take effect at renewal.

### 4.4 Annual to Monthly Conversion

Annual contracts may not be converted to monthly billing mid-term. Customers requesting early termination of annual contracts are subject to the cancellation terms in the MSA (typically 50% of remaining contract value or full remaining value for Enterprise).

---

## 5. Enterprise Custom Pricing

### 5.1 Approval Thresholds

| Deal Size (ACV) | Approver |
|-----------------|----------|
| < $50,000 | Sales Manager |
| $50,000 – $250,000 | Regional VP Sales |
| $250,000 – $1,000,000 | VP Sales + Finance |
| > $1,000,000 | CFO + CRO |

### 5.2 Common Enterprise Concessions

- Multi-year prepay discounts: 10% (2-year), 15% (3-year)
- Volume seat discounts: tiered at 200, 500, 1,000+ seats
- Bundled professional services: implementation, training, custom workflow design
- SLA uplift packages (see `sla_policy.md`)

### 5.3 Price Protection

Enterprise MSAs may include renewal price caps (typically 5–8% annual increase maximum). All caps must be documented in the Order Form.

---

## 6. Government and Regulated Industry Pricing

Government agencies (federal, state, local) and healthcare systems requiring BAA/HIPAA are quoted on Enterprise tier minimum. Nonprofit healthcare clinics may qualify for nonprofit Standard pricing if they meet 501(c)(3) criteria and do not require PHI processing in production.

---

## 7. Payment Terms

- **Self-serve / SMB:** Credit card or ACH, charged annually in advance
- **Mid-market:** Net-30 on annual invoice (credit approval required)
- **Enterprise:** Net-30 to Net-60 per MSA; multi-year prepay encouraged
- **Late payment:** 1.5% monthly interest after 30 days past due; service suspension at 60 days

---

## 8. Renewal and Auto-Renewal

All subscriptions auto-renew for the same term unless cancelled 30 days before renewal date. Renewal pricing is list price minus any contracted discount cap. Customer Success must initiate renewal conversations 90 days before expiry for accounts >$25K ACV.

---

## 9. Competitive and Retention Discounts

Discounts offered for competitive displacement or churn save scenarios require:

1. Documented competitor quote or churn risk assessment
2. Approval per Section 5.1 thresholds
3. Entry in CRM with reason code

Maximum retention discount without executive approval: 25% for one renewal term.

---

## 10. Contact

- **Sales quoting questions:** sales-ops@flowstack.io
- **Billing disputes:** billing@flowstack.io
- **Nonprofit verification:** nonprofit@flowstack.io
