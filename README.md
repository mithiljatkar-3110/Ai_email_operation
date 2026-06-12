# AI CRM System

AI-powered CRM platform for intelligent email triage, autonomous workflow execution, retrieval-augmented reasoning (RAG), and operational analytics.

## Overview

This system processes inbound customer emails and automatically:

* Performs heuristic triage
* Classifies emails using an LLM
* Retrieves relevant company policies using RAG
* Executes autonomous workflows through a ReAct-style agent
* Escalates critical issues
* Generates draft responses
* Produces analytics and operational dashboards

The project was developed as part of an AI CRM assessment focused on agentic workflows and enterprise customer support automation.

---

# Architecture

```text
Email
  ↓
Ingestion API
  ↓
Heuristic Triage Layer
  ↓
PostgreSQL
  ↓
RAG Retrieval
  ↓
Gemini Classification
  ↓
ReAct Agent
  ↓
Action / Escalation / Draft Reply
  ↓
Analytics Dashboard
```

Core Components:

* FastAPI Backend
* PostgreSQL
* FAISS Vector Store
* Sentence Transformers Embeddings
* Gemini 2.5 Flash
* ReAct Agent Framework

---

# Tech Stack

| Layer        | Technology              |
| ------------ | ----------------------- |
| Backend      | FastAPI                 |
| Database     | PostgreSQL              |
| ORM          | SQLAlchemy              |
| Migrations   | Alembic                 |
| LLM          | Gemini 2.5 Flash        |
| Embeddings   | all-MiniLM-L6-v2        |
| Vector Store | FAISS                   |
| Frontend     | React + Vite + Tailwind |
| Analytics    | Recharts                |

---

# Setup Guide

## 1. Clone Repository

```bash
git clone <repo-url>
cd Ai_crm_system
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure PostgreSQL

Create database:

```sql
CREATE DATABASE crm_agent;
```

Apply migrations:

```bash
alembic upgrade head
```

---

## 5. Configure Environment Variables

Create:

```text
.env
```

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=crm_agent

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---

# Knowledge Base Setup

Build the vector index:

```bash
python scripts/seed_kb.py
```

This:

1. Loads markdown documents
2. Chunks content
3. Generates embeddings
4. Creates a FAISS index

Generated files:

```text
storage/faiss_index.bin
storage/faiss_metadata.json
```

---

# Running the Application

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://localhost:8000/docs
```

Health Check:

```text
GET /health
```

---

# SQL Schema 

```sql
-- CONTACTS

CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50),
    priority_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- THREADS

CREATE TABLE threads (
    id UUID PRIMARY KEY,
    thread_id VARCHAR(255) UNIQUE NOT NULL,
    sender_email VARCHAR(255),
    status VARCHAR(50),
    last_updated_at TIMESTAMP
);

-- EMAILS

CREATE TABLE emails (
    id UUID PRIMARY KEY,
    thread_id UUID REFERENCES threads(id),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    sender VARCHAR(255),
    subject TEXT,
    body TEXT,
    timestamp TIMESTAMP,
    category VARCHAR(50),
    urgency VARCHAR(50),
    confidence FLOAT,
    sentiment_score FLOAT,
    requires_human BOOLEAN,
    priority_score INTEGER,
    status VARCHAR(50)
);

-- ACTIONS

CREATE TABLE actions (
    id UUID PRIMARY KEY,
    email_id UUID REFERENCES emails(id),
    action_type VARCHAR(100),
    proposed_content TEXT,
    agent_reasoning_log JSONB,
    executed_at TIMESTAMP DEFAULT NOW()
);



```


# Running Email Simulation

Replay the assessment dataset:

```bash
python scripts/replay.py
```

Custom speed:

```bash
python scripts/replay.py --speed 1
```

The simulator:

* Replays all emails
* Preserves thread structure
* Triggers ingestion and classification

---

# Implemented Features

## Email Ingestion

* Validation
* Deduplication
* Thread linking
* Priority scoring

## Heuristic Layer

Detects:

* Spam
* Security incidents
* Internal emails
* Urgent messages

## RAG Pipeline

Knowledge retrieval from:

* Pricing policy
* SLA policy
* Refund policy
* Compliance documents
* Escalation matrix

## LLM Classification

Classifies:

* Category
* Urgency
* Sentiment
* Confidence
* Human-review requirement

## Autonomous Agent

Supports:

* Draft replies
* Ticket creation
* Legal escalation
* Retention workflows
* SLA breach handling

## Analytics

* Category distribution
* Sentiment trends
* Escalation rate
* Agent action distribution

---

# Example Workflows

## Bob Jones SLA Escalation

Trigger:

* SLA breach
* Legal review
* Attorney involvement

Agent Actions:

1. Retrieve thread history
2. Search SLA policy
3. Check account status
4. Flag legal review
5. Create ticket
6. Draft holding response
7. Escalate to human

---

## Karen Churn-Risk Workflow

Trigger:

* Refund demand
* Cancellation request
* Public review threat

Agent Actions:

1. Retrieve history
2. Search retention policy
3. Create retention ticket
4. Escalate to account manager
5. Generate retention response

---

# Design Decisions and Trade-offs

## PostgreSQL over MongoDB

Chosen because:

* Strong relational model
* Thread and action relationships
* Better analytics queries
* Easier reporting

Trade-off:

* Slightly more schema management

---

## FAISS instead of pgvector

Chosen because:

* No PostgreSQL extension required
* Easy local setup
* Fast retrieval for small datasets

Trade-off:

* Separate vector storage layer

---

## Rule-Based Planner

Chosen because:

* Deterministic behavior
* Reliable demonstrations
* Easier debugging

Trade-off:

* Less adaptive than fully LLM-driven planning

---

## Local Embeddings

Chosen because:

* No API cost
* Fast execution
* Offline capability

Trade-off:

* Lower semantic quality than premium embedding APIs

---

# Known Limitations

* Agent planner is rule-based rather than fully LLM-driven.
* Contact profiles are not automatically populated.
* Web intelligence and reputation monitoring are not implemented.
* Vector embeddings are stored in FAISS rather than the database.
* Some classifications may require retry due to LLM output formatting issues.

---

# Future Improvements

* Contact enrichment
* Web reputation intelligence
* Human approval workflows
* Audit logging
* Background workers
* LLM-based planning
* pgvector integration
* Multi-agent orchestration

---

# API Summary

| Endpoint                           | Purpose             |
| ---------------------------------- | ------------------- |
| GET /health                        | Health check        |
| POST /api/ingest                   | Email ingestion     |
| POST /api/classify/{email_id}      | Classification      |
| GET /rag/search                    | Knowledge retrieval |
| POST /agent/dry-run/{email_id}     | Agent simulation    |
| GET /analytics/*                   | Analytics           |
| GET /dashboard/*                   | Dashboard data      |
| GET /threads/{thread_id}/workspace | Thread workspace    |

---

# Author

AI CRM System – Assessment Submission

Built using FastAPI, PostgreSQL, FAISS, Gemini, and React.
