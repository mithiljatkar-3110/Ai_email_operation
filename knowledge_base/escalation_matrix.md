# FlowStack Escalation Matrix

**Document ID:** POL-ESCALATION-001  
**Version:** 3.0  
**Effective Date:** January 1, 2024  
**Owner:** Customer Operations  
**Classification:** Internal — Support, AI Agent, and CSM Use

---

## 1. Purpose

This matrix defines **who handles what** when inbound communications require escalation beyond standard support. AI agents and support staff must route cases to the correct team within the specified SLA.

**Auto-reply is prohibited** for all Critical-track escalations.

---

## 2. Escalation Tracks

### Track A: Legal

**Route when email contains:**

- Cease and desist, lawsuit, litigation, attorney, legal action
- Trademark, patent, or IP infringement claims
- Regulatory enforcement notices (SEC, FTC, HHS OCR)
- Contract breach allegations with legal counsel CC'd
- Subpoenas, court orders, preservation notices

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | Support / AI Agent | 15 min | Tag `legal-escalation`, do NOT commit to remedies |
| 2 | Legal Ops | 4 hours | Acknowledge receipt, request case summary |
| 3 | General Counsel | 24 hours | Response strategy, approved holding language |
| 4 | CSM / AE | Parallel | Brief account team, pause renewal if applicable |

**Approved holding reply (Legal):**

> We have received your message and take legal matters seriously. Your correspondence has been forwarded to our Legal team, who will review and respond directly within [timeframe per counsel]. We are preserving all relevant records related to this matter.

**Do not:** Admit liability, offer refunds, or discuss settlement terms.

---

### Track B: Security Incidents

**Route when email contains:**

- Suspicious login, unauthorized access, account compromise
- Data breach, data leak, exfiltration
- Ransomware, malware, phishing targeting FlowStack
- Vulnerability disclosure (responsible or otherwise)
- CVE references affecting FlowStack platform

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | Support / AI Agent | **15 min** | Tag `security-p0`, page Security on-call |
| 2 | Security Engineering | 30 min | Triage, contain, preserve logs |
| 3 | CISO (P0 only) | 1 hour | Customer communication approval |
| 4 | Legal + Compliance | Parallel (if PHI/PII) | Breach notification assessment |

**Customer communication (Security P0):**

> We are treating this as a priority security matter. Our Security team is actively investigating and will provide an update within [30 minutes / 1 hour]. If you believe credentials are compromised, please rotate API keys immediately via Admin → API Keys.

**Internal ticket required:** `SEC-INCIDENT-[YYYY]-[NNN]`

---

### Track C: PR Crisis / Reputation

**Route when email contains:**

- Threat to post public review (G2, Trustpilot, Capterra, Google)
- Social media callout (Twitter/X, LinkedIn, Reddit, Hacker News)
- Press inquiry, journalist contact
- Influencer or analyst public criticism
- "I will tell everyone" / viral churn threat

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | Support / AI Agent | 1 hour | Tag `reputation-risk`, escalate to CSM |
| 2 | CSM | 4 hours | Personal outreach, retention playbook (`refund_policy.md`) |
| 3 | Communications / PR | 24 hours | Review any public-facing response |
| 4 | Legal | If defamation or false claims | Review before response |

**Guidance:** Prioritize empathy and concrete remediation. Cross-reference `refund_policy.md` for credit vs. refund options. Do not offer incentives solely to remove reviews.

**Karen W / Retail-Co scenario:** Complaint + refund demand + public review threat → Tracks C + Retention + possible SLA credit review.

---

### Track D: VIP and Enterprise Churn

**Route when:**

- Contact status = VIP in CRM
- Account ACV > $100,000
- Enterprise tier with renewal <90 days
- Executive sponsor sends direct email
- Customer states they are "evaluating alternatives" or "not renewing"

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | CSM | 2 hours | Personal acknowledgment |
| 2 | Account Executive | 4 hours | Join thread or schedule call |
| 3 | VP Customer Success | 24 hours (if unresolved) | Executive alignment |
| 4 | Product (if feature gap) | 48 hours | Roadmap review |

---

### Track E: GDPR and Privacy Requests

**Route when email contains:**

- GDPR Article 15–22 references
- "Data portability", "right to erasure", "right to be forgotten"
- CCPA/CPRA consumer rights requests
- DPA breach notification from customer DPO

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | Support / AI Agent | 48 hours | Acknowledge, create `PRIVACY-[NNN]` ticket |
| 2 | Privacy Team | 30 calendar days | Fulfill request per `compliance_faq.md` |
| 3 | Legal | If formal/legal tone | Review response before sending |

**Approved acknowledgement (GDPR Art. 20 portability):**

> We acknowledge your formal request under GDPR Article 20 for data portability. Your request has been logged as [PRIVACY-NNN] and assigned to our Privacy team. We will provide your data export or confirm completion within 30 calendar days as required by law.

**Do not auto-reply with generic support language.**

---

### Track F: SLA Breach and P0 Production Incidents

**Route when:**

- Customer cites SLA breach, downtime, or production outage
- P0 / URGENT in subject with business impact
- Request for RCA within 24 hours
- Legal team CC'd on incident (e.g., Bob Jones / Enterprise.net escalation chain)

| Step | Owner | SLA | Action |
|------|-------|-----|--------|
| 1 | Support | 15 min (Enterprise P0) | Page on-call, open incident bridge |
| 2 | SRE | Per `sla_policy.md` | Mitigation + status updates |
| 3 | CSM | 1 hour | Customer communication, credit eligibility |
| 4 | Legal | If legal CC'd | Coordinate on RCA and liability language |
| 5 | Post-incident | 24h (P0) | Deliver RCA per `sla_policy.md` |

**SLA credit:** Calculate per `sla_policy.md` Section 4. Do not promise credits beyond formula without Finance.

---

## 3. Priority and Multi-Track Escalation

When multiple tracks apply, use the **highest priority** track for SLA purposes:

| Priority | Track | Examples |
|----------|-------|----------|
| 1 (Highest) | Security (B) | Ransomware, breach |
| 2 | Legal (A) | Cease and desist |
| 3 | SLA / P0 (F) | Production down, SLA breach + legal |
| 4 | GDPR (E) | Formal data portability |
| 5 | PR Crisis (C) | Public review threat |
| 6 | VIP Churn (D) | Enterprise renewal at risk |

**Multi-track example (msg_060 — SLA + Legal):**

1. Open P0 incident bridge (Track F)
2. Notify Legal of customer counsel involvement (Track A)
3. CSM delivers empathetic holding reply citing SLA credit policy
4. Prepare RCA within 24 hours
5. Do NOT auto-reply — human approval required for all outbound messages

---

## 4. AI Agent Routing Rules

The autonomous agent must:

| Condition | Action |
|-----------|--------|
| `urgency = Critical` AND `category = Legal` | `flag_for_legal()` + `escalate_to_human()` |
| `is_security = true` | `escalate_to_human()` immediately, priority 100 |
| `category = Compliance` OR GDPR keywords | `create_internal_ticket()` → Privacy team |
| Public review threat detected | `escalate_to_human()` + retrieve `refund_policy.md` + this matrix |
| `confidence < 0.70` | `escalate_to_human()` with reasoning summary |
| Critical urgency | **Never** `send_auto_reply()` |

---

## 5. Internal Contacts

| Team | Email | Pager |
|------|-------|-------|
| Legal Ops | legal-ops@flowstack.io | Weekdays |
| Security On-Call | security-oncall@flowstack.io | 24/7 PagerDuty |
| Privacy / DPO | privacy@flowstack.io | Weekdays |
| PR / Comms | comms@flowstack.io | On-call for P1+ |
| VP Customer Success | vpcs@flowstack.io | Executive escalations |
| P0 Incident Bridge | incidents@flowstack.io | 24/7 |

---

## 6. Ticket Tagging Convention

```
[TRACK]-[SEVERITY]-[ACCOUNT_ID]
```

Examples:
- `LEGAL-HIGH-ENT-4421`
- `SECURITY-P0-ALL-CUSTOMERS`
- `GDPR-MEDIUM-RETAIL-88271`
- `REPUTATION-HIGH-RETAIL-88271`

---

## 7. Escalation Closure

Every escalated case requires:

1. Resolution summary in CRM
2. Audit log entry (`audit_log` table)
3. Customer confirmation or 48-hour no-response auto-close (except Legal/GDPR — manual close only)
