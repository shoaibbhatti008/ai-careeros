
---

## 📄 FILE 8: `DEVELOPMENT.md`

```markdown
# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker (optional, recommended)
- Git

## Local Setup (Windows PowerShell)

```powershell
git clone https://github.com/shoaibbhatti008/ai-careeros.git
cd ai-careeros
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend\requirements\development.txt
Copy-Item .env.example .env
# Edit .env with your values
docker compose up -d postgres redis
cd backend
python manage.py migrate
python manage.py runserver