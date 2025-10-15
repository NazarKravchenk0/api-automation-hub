# API Automation Hub (FastAPI + Postgres + Redis RQ)

A unified service for receiving and processing events and leads from multiple sources (Stripe, Calendly, website forms), 
with deduplication, business logic, task queue, and a minimal dashboard.

## Quick Start (Docker Compose)
1) Copy `.env.example` to `.env` and update values if necessary.
2) Run:
```bash
docker compose up --build
```
3) API documentation: http://localhost:8000/docs  
4) Database admin (Adminer): http://localhost:8080  (System: PostgreSQL; Server: db; User/Pass: from .env; DB: from .env)

## What's Inside
- **FastAPI** — REST API and mini-dashboard
- **PostgreSQL** — lead and event storage
- **Redis + RQ** — background task queue (enrichment, notifications, retries)
- **Business rules:** normalization, deduplication by email/phone, source priorities
- **Webhooks:** Stripe, Calendly, Generic Form
- **Monitoring:** healthcheck endpoint, structured logs
- **OpenAPI/Swagger:** auto-generated docs at /docs

## Environment Variables (.env)
See `.env.example` (database connection, Redis, integration API keys).

## Main Endpoints
- `POST /webhooks/stripe` — Stripe events (invoice.payment_succeeded, checkout.session.completed, etc.)
- `POST /webhooks/calendly` — Calendly events (invitation.created, etc.)
- `POST /webhooks/form` — universal form intake (name/email/phone/source/utm)
- `GET  /leads` — list of leads with pagination and filters
- `GET  /events` — list of events
- `GET  /metrics` — metrics (lead count by source, CR where applicable)
- `GET  /health` — service health status

## Local Development (without Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env.example | xargs)  # example setup
uvicorn app.main:app --reload
rq worker --url $REDIS_URL hub-queue
```
> For Windows, use `set` or `$Env:` instead of `export`.

## Tests
```bash
pytest -q
```

## Compliance Notes
Scripting and webhooks must comply with each service's ToS. 
Notifications or messages may be sent only with user consent and in accordance with GDPR and local laws.
