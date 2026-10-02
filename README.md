<div align="center">

# AI CareerOS

### Open-Source Multi-Agent AI Career Intelligence Platform

**Analyze resumes. Discover career opportunities. Identify skill gaps. Practice interviews.  
Search personal documents with RAG. Coordinate specialized AI agents safely.**

[![CI](https://github.com/shoaibbhatti008/ai-careeros/actions/workflows/ci.yml/badge.svg)](https://github.com/shoaibbhatti008/ai-careeros/actions/workflows/ci.yml)
[![Security](https://github.com/shoaibbhatti008/ai-careeros/actions/workflows/security.yml/badge.svg)](https://github.com/shoaibbhatti008/ai-careeros/actions/workflows/security.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.x-092E20.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-18.x-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/typescript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/redis-7-DC382D.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Security](#security-model) • [Agent Docs](docs/AGENTS.md) • [API](API.md)

</div>

---

## Overview

**AI CareerOS** is a production-oriented, security-first, open-source platform
that coordinates multiple specialized AI agents to help developers, students,
job seekers, and researchers make better career decisions.

Unlike a basic chatbot, AI CareerOS is built as a **multi-agent orchestration platform** with:

- Explicit **agent responsibilities** and permission boundaries
- A **controlled tool system** — agents can only use registered, validated tools
- **Human approval workflows** for sensitive actions
- **Retrieval-Augmented Generation (RAG)** over user-owned documents
- **Prompt-injection defenses** for all untrusted external content
- **Full audit logging**, observability, and security testing

> AI CareerOS never executes AI output directly. Every sensitive action passes through validation, authorization, and (where required) explicit user approval.

---

## Demo

> A live demo link will be published once the first stable release is available.

The repository is being built **phase-by-phase** with real, tested code. No fake screenshots, no fake metrics, no fake stars.

Screenshots will appear in [`docs/screenshots/`](docs/screenshots/) once real functionality is implemented.

---

## Features

### Multi-Agent AI

- **Orchestrator** — plans and coordinates multi-agent workflows
- **ResumeAgent** — analyzes resumes and extracts skills
- **ResumeAgentLLM** — LLM-powered resume analysis
- **JobAgent** — parses job descriptions and computes match scores
- **SkillGapAgent** — identifies and prioritizes skill gaps
- **InterviewAgent** — generates mock interview questions and analyzes answers
- **RAGAgent** — answers questions grounded in user-owned documents
- **VerificationAgent** — validates outputs before use
- **ApprovalAgent** — human-in-the-loop approval for sensitive actions

### Career Intelligence

- Resume analysis with structured feedback
- Job matching against user profiles and preferences
- Skill gap analysis with prioritized recommendations
- Interview preparation with feedback
- Document Q&A via RAG

### Security-First Design

- Registered tools only — no arbitrary code execution
- Per-agent permission boundaries and schemas
- Prompt-injection detection and safe handling
- Human approval for sensitive actions
- IDOR / XSS / CSRF / SQLi / upload protection
- Rate limiting, timeouts, and execution budgets
- Full audit logging with trace IDs

### RAG & Document AI

- Secure document ingestion (PDF, DOCX, TXT, MD)
- Chunking, embedding, and vector storage
- Ownership-filtered retrieval — no cross-user leakage
- Source-attributed answers

### Observability

- Structured JSON logs
- Trace IDs across agents and tools
- Counters, histograms (p50/p95/p99)
- Agent execution and tool execution records
- Rate limiting and cost tracking

### Cost Control

- Per-user, per-agent, per-model cost tracking
- Curated pricing table (GPT-4o, Claude, mock)
- Hard budgets: steps, tools, tokens, cost, duration
- Fail-closed on budget violations

---

## Why AI CareerOS?

Most "AI career tools" are thin wrappers around a single LLM prompt. AI CareerOS is different:

| Concern | Typical Chatbot | AI CareerOS |
|---|---|---|
| Architecture | Single prompt | Multi-agent orchestration |
| Tool use | Unrestricted | Registered, permissioned tools |
| Security | Ad-hoc | Security-first by design |
| Sensitive actions | Auto-executed | Human approval workflow |
| External content | Trusted | Treated as untrusted |
| Observability | Minimal | Structured, traced |
| Testing | None | Security + agent safety tests |
| License | Closed | Apache 2.0 |

---

## Architecture

```mermaid
flowchart TD
    U[User] --> FE[React + TypeScript Frontend]
    FE --> API[Django REST API]
    API --> AUTH[Authentication]
    AUTH --> AUTHZ[Authorization]
    AUTHZ --> ORCH[AI Orchestrator]
    ORCH --> A1[Resume Agent]
    ORCH --> A2[Job Agent]
    ORCH --> A3[Skill Gap Agent]
    ORCH --> A4[Interview Agent]
    ORCH --> A5[RAG Agent]
    ORCH --> A6[Verification Agent]
    ORCH --> A7[Approval Agent]
    A1 & A2 & A3 & A4 & A5 --> TOOLS[Controlled Tools]
    TOOLS --> PERM[4-Layer Permission Check]
    PERM --> EXEC[Tool Execution]
    EXEC --> OBS[Observability]
    A6 --> VERIFY[Output Verification]
    A7 --> APPROVE[Human Approval]
    VERIFY & APPROVE --> RESP[Response]
    RESP --> FE