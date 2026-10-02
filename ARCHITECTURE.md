# Architecture

This document describes the architecture of AI CareerOS.

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    U[User] --> FE[React + TypeScript Frontend]
    FE --> API[Django REST API]
    API --> AUTH[Authentication]
    AUTH --> AUTHZ[Authorization]
    AUTHZ --> ORCH[AI Orchestrator]
    ORCH --> AGENTS[Specialized Agents]
    AGENTS --> TOOLS[Controlled Tools]
    TOOLS --> VERIFY[Verification]
    VERIFY --> RESP[Response]
    RESP --> FE