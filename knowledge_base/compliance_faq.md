# FlowStack Compliance FAQ

**Document ID:** DOC-COMPLIANCE-001  
**Version:** 1.8  
**Effective Date:** January 1, 2024  
**Owner:** Security & Compliance  
**Classification:** Customer-Facing / Sales Enablement

---

## 1. Overview

FlowStack serves regulated industries including healthcare, financial services, and enterprise SaaS. This FAQ answers common compliance questions from prospects, customers, and support agents.

For binding commitments, refer to executed BAAs, DPAs, and Order Forms.

---

## 2. SOC 2 Type II

### Q: Is FlowStack SOC 2 certified?

**A:** Yes. FlowStack maintains **SOC 2 Type II** certification covering Security, Availability, and Confidentiality trust service criteria. Our most recent audit period ended September 30, 2023 with **no qualified opinions**.

- Report available under NDA to Enterprise and Professional customers
- Request via: compliance@flowstack.io (typically fulfilled within 2 business days)
- Bridge letters provided between audit cycles

### Q: What controls are covered?

Encryption at rest (AES-256), encryption in transit (TLS 1.2+), access controls, vulnerability management, incident response, change management, and employee background checks.

---

## 3. HIPAA and BAA

### Q: Can FlowStack sign a Business Associate Agreement (BAA)?

**A:** Yes. FlowStack offers a **HIPAA BAA** for customers on **Enterprise tier** who process Protected Health Information (PHI) in the platform.

**Requirements:**

1. Signed Enterprise Order Form
2. Execution of FlowStack Standard BAA (or customer paper via Legal review, 4–6 week lead time)
3. Use of HIPAA-eligible regions (US-only data residency)
4. Configuration of audit logging and access controls per implementation guide

**BAA is NOT available on:** Starter, Standard, or Professional self-serve tiers.

### Q: What PHI can be processed?

Workflow metadata, contact records, and integration payloads may contain PHI if customer configures accordingly. FlowStack does **not** provide clinical decision support and is not a covered entity.

### Q: HIPAA incident notification timeline?

Suspected PHI breaches are notified to the customer **within 24 hours** of FlowStack confirmation, per BAA terms. Customer is responsible for notifying individuals and HHS as required.

---

## 4. GDPR and Data Protection

### Q: Does FlowStack support GDPR compliance?

**A:** Yes. FlowStack acts as a **Data Processor** under GDPR. Customers are Data Controllers.

**Available artifacts:**

- Standard Data Processing Agreement (DPA) — Schedule to MSA
- EU Standard Contractual Clauses (SCCs) Module 2 (Controller to Processor)
- Sub-processor list (updated quarterly at `flowstack.io/legal/subprocessors`)
- Data Processing Impact Assessment (DPIA) template for customers

### Q: How does a customer execute a DPA?

1. Customer signs MSA / Order Form
2. DPA is incorporated by reference OR signed separately
3. For EU customers: SCCs automatically apply
4. Enterprise customers may request custom DPA terms via Legal (6–8 week review)

### Q: How do we handle GDPR data subject requests?

| Request Type | FlowStack Role | Process |
|--------------|----------------|---------|
| **Access (Art. 15)** | Assist Controller | Customer submits via Admin → Privacy → Data Export; FlowStack provides within 30 days |
| **Erasure (Art. 17)** | Assist Controller | Customer initiates deletion; FlowStack purges within 30 days |
| **Portability (Art. 20)** | Assist Controller | JSON/CSV export via API or Admin console |
| **Rectification (Art. 16)** | Assist Controller | Customer updates records directly or via API |

**Formal GDPR requests** (e.g., email from data subject or their attorney) must be escalated per `escalation_matrix.md` → Legal / Compliance track. Acknowledge within **48 hours**; complete within **30 calendar days** (extendable by 60 days with notice).

### Q: Where is EU customer data stored?

| Region | Location | Available Tiers |
|--------|----------|-----------------|
| US (default) | AWS us-east-1, us-west-2 | All tiers |
| EU | AWS eu-west-1 (Ireland) | Professional, Enterprise |
| UK | AWS eu-west-2 (London) | Enterprise |
| APAC | AWS ap-southeast-1 | Enterprise |

EU data residency must be selected at account provisioning. Migration between regions requires Professional Services engagement.

---

## 5. Data Residency and Sovereignty

### Q: Can we require all data stays in a specific country?

**A:** Enterprise customers may select region at provisioning. FlowStack does not transfer customer data outside the selected region except:

- Encrypted backups to paired DR region (disclosed in DPA)
- Support access from approved personnel (subject to background checks and access logging)

### Q: Do you support data localization for Australia, Canada, Brazil?

Australia (ap-southeast-2) and Canada (ca-central-1) available for Enterprise with 8-week provisioning lead time. Brazil: evaluate case-by-case.

---

## 6. PCI DSS

FlowStack is **not** a payment card processor. We do not store, process, or transmit cardholder data. Payment processing is handled by Stripe (PCI DSS Level 1). Customers must not send PAN/CVV through FlowStack workflows.

---

## 7. ISO 27001

FlowStack is ISO 27001:2013 certified. Certificate available on request alongside SOC 2 report.

---

## 8. Penetration Testing and Security

- Annual third-party penetration test (summary available under NDA)
- Continuous vulnerability scanning
- Bug bounty program: `security.flowstack.io`
- Customer right to audit (Enterprise): once annually with 30 days notice, subject to confidentiality

---

## 9. Encryption Standards

| Layer | Standard |
|-------|----------|
| At rest | AES-256 (AWS KMS, customer-managed keys available Enterprise) |
| In transit | TLS 1.2 minimum, TLS 1.3 preferred |
| API keys | Hashed at rest, shown once at creation |
| Backups | Encrypted, separate KMS keys |

---

## 10. Sub-Processors

Key sub-processors: AWS (infrastructure), Stripe (billing), SendGrid (transactional email), Datadog (monitoring), OpenAI (optional AI features — **disabled by default for HIPAA accounts**).

Customers may object to new sub-processors within 30 days of notification per DPA terms.

---

## 11. AI and Data Usage

FlowStack does **not** use customer workflow data to train foundation models without explicit opt-in. Enterprise and HIPAA accounts: AI features disabled by default; enablement requires BAA amendment.

---

## 12. Compliance Contact

- **General compliance:** compliance@flowstack.io
- **BAA / HIPAA:** hipaa@flowstack.io
- **GDPR / DPA:** privacy@flowstack.io
- **Security incidents:** security@flowstack.io (P0 — see `escalation_matrix.md`)
