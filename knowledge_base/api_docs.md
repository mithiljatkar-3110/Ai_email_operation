# FlowStack API Documentation

**Document ID:** DOC-API-002  
**Version:** 2.0  
**Base URL:** `https://api.flowstack.io`  
**Owner:** Platform Engineering  
**Classification:** Public / Developer Portal

---

## 1. Authentication

All API requests require authentication via API key or OAuth 2.0 bearer token.

### 1.1 API Key Headers

```http
Authorization: Bearer fs_live_xxxxxxxxxxxxxxxx
Content-Type: application/json
X-FlowStack-Version: 2024-01-01
```

### 1.2 Required Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token or API key |
| `Content-Type` | Yes (POST/PUT/PATCH) | Must be `application/json` |
| `X-FlowStack-Version` | Yes | API version date (see versioning) |
| `X-Request-Id` | Recommended | Client-generated UUID for tracing |
| `X-Idempotency-Key` | Recommended (POST) | Prevents duplicate resource creation |

Requests missing `X-FlowStack-Version` receive `400 Bad Request` with error code `missing_version_header`.

---

## 2. API Versioning

### 2.1 Version Header

FlowStack uses date-based versioning via `X-FlowStack-Version`. The current stable version is **`2024-01-01`**.

### 2.2 v1 Deprecation Timeline

| Milestone | Date | Action |
|-----------|------|--------|
| v1 deprecation announced | July 1, 2023 | Documentation updated, customer emails sent |
| v1 frozen (bug fixes only) | January 1, 2024 | No new v1 features |
| v1 end-of-life | **July 1, 2024** | v1 endpoints return `410 Gone` |
| v1 sunset complete | August 1, 2024 | All traffic must use v2 |

**v1 base path:** `/v1/` — **DEPRECATED, DO NOT USE**

### 2.3 v2 Breaking Changes

Customers migrating from v1 to v2 must address:

| Change | v1 Behavior | v2 Behavior |
|--------|-------------|-------------|
| Webhook events endpoint | `POST /v1/hooks` | `POST /v2/events` |
| Authentication scopes | Single API key | Scoped keys (`workflows:read`, `events:write`) |
| Pagination | Offset-based (`?page=2`) | Cursor-based (`?cursor=abc123`) |
| Error format | Plain text | JSON envelope with `error_code`, `message`, `details` |
| Rate limit headers | `X-RateLimit-Remaining` | `RateLimit-Remaining`, `RateLimit-Reset` (RFC 9488) |
| Workflow triggers | Synchronous response | Async with `job_id` polling |

**403 on v2 endpoints** commonly indicates:

1. API key lacks required scope (e.g., missing `events:write` for `POST /v2/events`)
2. Account still on v1 key type (must regenerate in Admin → API Keys)
3. IP allowlist blocking request source

---

## 3. Rate Limits by Tier

Rate limits apply per API key, per minute, unless otherwise noted.

| Tier | Requests/Minute | Burst | Webhook Deliveries/Hour |
|------|---------------|-------|------------------------|
| Starter | 60 | 100 | 1,000 |
| Standard | 300 | 500 | 10,000 |
| Professional | 1,000 | 2,000 | 50,000 |
| Enterprise | 5,000 (custom available) | 10,000 | Unlimited (fair use) |

### 3.1 Rate Limit Response

```http
HTTP/1.1 429 Too Many Requests
RateLimit-Limit: 300
RateLimit-Remaining: 0
RateLimit-Reset: 1704067200
Retry-After: 42

{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Retry after 42 seconds.",
  "details": { "tier": "standard", "limit": 300 }
}
```

### 3.2 Rate Limit Increases

Enterprise customers may request temporary limit increases for launch events (48-hour windows). Submit via CSM ≥5 business days in advance.

---

## 4. Core Endpoints (v2)

### 4.1 Workflows

```
GET    /v2/workflows              List workflows
POST   /v2/workflows              Create workflow
GET    /v2/workflows/{id}         Get workflow
PATCH  /v2/workflows/{id}         Update workflow
DELETE /v2/workflows/{id}         Archive workflow
POST   /v2/workflows/{id}/run     Trigger execution (async)
```

### 4.2 Events (Webhooks)

```
POST   /v2/events                 Ingest external event (triggers workflows)
GET    /v2/events/{id}            Get event status
GET    /v2/events                 List events (paginated)
```

**`POST /v2/events` requirements:**

- Scope: `events:write`
- Payload max size: 1 MB
- Supported content types: `application/json`
- Idempotency: Use `X-Idempotency-Key` header (24-hour deduplication window)

**Common 403 causes:**

```json
{
  "error_code": "INSUFFICIENT_SCOPE",
  "message": "API key requires 'events:write' scope for POST /v2/events",
  "details": { "required_scope": "events:write", "key_scopes": ["workflows:read"] }
}
```

### 4.3 Contacts (CRM Module)

```
GET    /v2/contacts               List contacts
POST   /v2/contacts               Create contact
GET    /v2/contacts/{email}       Get contact by email
PATCH  /v2/contacts/{email}       Update contact
```

---

## 5. Webhook Delivery

- Retry policy: Exponential backoff, 8 attempts over 24 hours
- Timeout: 30 seconds per delivery attempt
- Signature header: `X-FlowStack-Signature` (HMAC-SHA256)
- Failed deliveries visible in Admin → Webhooks → Delivery Log

---

## 6. Sandbox Environment

- Base URL: `https://api.sandbox.flowstack.io`
- Separate API keys (prefix `fs_test_`)
- Rate limits: 50% of production tier
- Data retained 30 days, reset on request

---

## 7. SDKs and Tools

Official SDKs: Python (`flowstack-python`), Node.js (`@flowstack/sdk`), Go (`github.com/flowstack/go-sdk`).

OpenAPI spec: `https://api.flowstack.io/openapi/v2.json`

---

## 8. Support for API Issues

| Issue Type | Channel | SLA |
|------------|---------|-----|
| 403 / scope errors | support@flowstack.io | 24h (Standard) |
| P0 production API down | Enterprise hotline | 15 min |
| v1 migration assistance | developers@flowstack.io | 48h |

Include `X-Request-Id` from failed requests when opening tickets.

---

## 9. Changelog

- **2024-01-01:** v2 GA, cursor pagination, scoped API keys
- **2023-07-01:** v1 deprecation notice
- **2023-03-15:** Webhook signature v2 (HMAC-SHA256 replaces SHA1)
