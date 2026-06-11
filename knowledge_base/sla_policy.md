# FlowStack Service Level Agreement (SLA) Policy

**Document ID:** POL-SLA-001  
**Version:** 4.1  
**Effective Date:** January 1, 2024  
**Owner:** Site Reliability Engineering  
**Classification:** Customer-Facing (Enterprise Order Form Attachment)

---

## 1. Scope

This SLA applies to the FlowStack cloud platform (`app.flowstack.io`, API endpoints `api.flowstack.io`) for paying customers on Standard, Professional, and Enterprise tiers. Free trials and sandbox environments are excluded.

Enterprise customers may negotiate enhanced SLAs via Order Form amendments.

---

## 2. Uptime Commitment

### 2.1 Monthly Uptime SLA

FlowStack commits to **99.9% monthly uptime** for the production platform.

**Uptime calculation:**

```
Uptime % = ((Total minutes in month − Downtime minutes) ÷ Total minutes in month) × 100
```

**Excluded from downtime (planned maintenance):**

- Scheduled maintenance windows (Saturdays 02:00–06:00 UTC, announced ≥72 hours in advance)
- Customer-caused outages (misconfigured webhooks, expired API keys, rate limit exhaustion)
- Force majeure events
- Third-party DNS or CDN failures outside FlowStack control

### 2.2 Uptime by Tier

| Tier | Uptime SLA | Measurement Window |
|------|------------|-------------------|
| Standard | 99.5% | Calendar month |
| Professional | 99.9% | Calendar month |
| Enterprise | 99.9% (up to 99.95% negotiated) | Calendar month |

---

## 3. Incident Severity and Response Times

### 3.1 Severity Definitions

| Severity | Definition | Examples |
|----------|------------|----------|
| **P0 – Critical** | Complete platform outage or data loss risk affecting multiple customers | API unavailable, authentication down, data corruption |
| **P1 – High** | Major feature unavailable for a single enterprise customer or degraded performance >50% | Workflow engine stalled, webhook delivery failure >1 hour |
| **P2 – Medium** | Partial feature degradation, workaround available | Dashboard slow load, single integration failure |
| **P3 – Low** | Minor issue, cosmetic, or documentation error | UI alignment, non-blocking bug |

### 3.2 Response Time SLAs (Enterprise Tier)

| Severity | Initial Response | Status Update Frequency | Resolution Target |
|----------|-----------------|------------------------|-------------------|
| **P0** | **15 minutes** | Every 30 minutes | 4 hours (mitigation), 24 hours (RCA) |
| **P1** | 1 hour | Every 2 hours | 8 hours (mitigation), 72 hours (RCA) |
| **P2** | 4 hours | Daily | 5 business days |
| **P3** | 1 business day | As needed | Next release cycle |

**Standard/Professional tiers:** P0 initial response within 1 hour; P1 within 4 hours.

### 3.3 RCA Delivery SLA

A **Root Cause Analysis (RCA) report** is required for all P0 and P1 incidents affecting Enterprise customers.

| Severity | RCA Delivery Deadline | Report Contents |
|----------|----------------------|-----------------|
| **P0** | **24 hours** from incident resolution | Timeline, root cause, customer impact, corrective actions, prevention plan |
| **P1** | 5 business days | Same as P0 |
| **P2** | Optional upon request | Summary post-mortem |

RCA reports are delivered to the customer's designated technical contact and CSM. Legal or compliance incidents may require redacted public versions.

---

## 4. Service Credit Calculation

### 4.1 Credit Eligibility

Customers on Professional and Enterprise tiers are eligible for service credits when monthly uptime falls below the committed SLA **and** the customer submits a credit request within 30 days of the incident month.

### 4.2 Credit Formula

```
Service Credit = (Monthly subscription fee × Credit percentage)
```

| Monthly Uptime Achieved | Credit Percentage |
|------------------------|-------------------|
| 99.0% – 99.89% | 10% of monthly fee |
| 95.0% – 98.99% | 25% of monthly fee |
| < 95.0% | 50% of monthly fee |

**Example:** Enterprise customer pays $20,000/month. Uptime was 98.5% (below 99.9% SLA):

```
Service Credit = $20,000 × 25% = $5,000
```

Credits are applied to the **next invoice** unless the customer requests a refund (refund requests require Finance approval and are governed by `refund_policy.md`).

### 4.3 Credit Caps and Exclusions

- Maximum credit per month: **50% of monthly subscription fee**
- Credits are the **sole and exclusive remedy** for SLA breaches unless otherwise stated in the MSA
- Credits do not apply to professional services, overage charges, or third-party marketplace fees
- Multiple P0 incidents in one month do not stack credits beyond the cap

### 4.4 Credit Request Process

1. Customer submits ticket referencing incident ID(s) within 30 days
2. Support validates downtime against internal monitoring (Datadog, PagerDuty logs)
3. CSM confirms credit calculation with Finance
4. Credit applied within one billing cycle

---

## 5. Support Channels by Tier

| Channel | Standard | Professional | Enterprise |
|---------|----------|--------------|------------|
| Email | ✓ (48h) | ✓ (24h) | ✓ (4h business) |
| Chat | — | ✓ | ✓ |
| Phone / P0 Hotline | — | — | ✓ (24/7) |
| Dedicated CSM | — | >100 seats | ✓ |
| Slack Connect | — | — | Optional add-on |

**Enterprise P0 Hotline:** +1-800-FLOW-P0 (available on Order Form)

---

## 6. Maintenance Windows

- **Standard maintenance:** Saturdays 02:00–06:00 UTC
- **Emergency maintenance:** Announced ≥4 hours in advance when possible
- Customers may subscribe to status updates at `status.flowstack.io`

---

## 7. Data Durability and Backup SLA

- **RPO (Recovery Point Objective):** 1 hour for Enterprise, 4 hours for Professional
- **RTO (Recovery Time Objective):** 4 hours for Enterprise, 8 hours for Professional
- Daily encrypted backups retained 30 days; Enterprise may purchase extended retention

---

## 8. Escalation During Active Incidents

If a customer reports production impact and the ticket is not acknowledged within the response SLA:

1. Customer replies "ESCALATE" on the ticket
2. Automatic PagerDuty page to on-call engineering manager
3. CSM notified for accounts >$50K ACV
4. If legal or SLA breach language appears in customer communication, route per `escalation_matrix.md`

---

## 9. SLA Disputes

Customers disputing uptime calculations must provide:

- Timestamped error logs or monitoring evidence
- Affected endpoints and regions
- Business impact summary

FlowStack will reconcile against internal telemetry within 5 business days.

---

## 10. Contact

- **P0 Incidents:** support@flowstack.io (subject: P0) or Enterprise hotline
- **SLA credit requests:** sla-credits@flowstack.io
- **RCA requests:** postmortem@flowstack.io
