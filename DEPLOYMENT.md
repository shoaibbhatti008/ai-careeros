
---

## 📄 FILE 9: `DEPLOYMENT.md`

```markdown
# Deployment Guide

## Overview

AI CareerOS is deployed as a set of Docker containers behind Nginx.

```mermaid
flowchart TD
    NGINX[Nginx] --> FE[Frontend]
    NGINX --> BE[Backend]
    BE --> PG[(PostgreSQL)]
    BE --> RD[(Redis)]
    BE --> CW[Celery Worker]