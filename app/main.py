from fastapi import FastAPI, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Any
from app.config import settings
from app.db.database import Base, engine, get_db
from app.db import crud
from app.schemas import LeadIn, LeadOut
from app.tasks.jobs import enqueue, enrich_lead_job, notify_slack_job, notify_telegram_job

app = FastAPI(title="API Automation Hub", version="0.1.0")

# Создаем таблицы
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

@app.post("/webhooks/form", response_model=LeadOut)
async def ingest_form(lead: LeadIn, db: Session = Depends(get_db)):
    data = lead.model_dump()
    data["source"] = data.get("source") or "form"
    try:
        created = crud.upsert_lead(db, data)
        enqueue(enrich_lead_job, created.id)
        enqueue(notify_slack_job, f"New lead #{created.id} from {created.source}: {created.email or created.phone}")
        enqueue(notify_telegram_job, f"New lead #{created.id} from {created.source}: {created.email or created.phone}")
        crud.log_event(db, provider="form", event_type="lead", payload=data, status="processed")
        return created
    except Exception as e:
        crud.log_event(db, provider="form", event_type="lead", payload=data, status="error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    event_type = payload.get("type", "unknown")
    crud.log_event(db, provider="stripe", event_type=event_type, payload=payload, status="received")
    # Пример извлечения лида из checkout.session.completed
    try:
        session = payload.get("data", {}).get("object", {})
        email = session.get("customer_details", {}).get("email")
        name = session.get("customer_details", {}).get("name")
        lead = crud.upsert_lead(db, {"name": name, "email": email, "source": "stripe", "meta": {"stripe_id": session.get("id")}})
        enqueue(enrich_lead_job, lead.id)
    except Exception:
        pass
    return {"ok": True}

@app.post("/webhooks/calendly")
async def calendly_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    event_type = payload.get("event", "unknown")
    crud.log_event(db, provider="calendly", event_type=event_type, payload=payload, status="received")
    # Пример: извлечь email/имя участника
    try:
        invitee = payload.get("payload", {}).get("invitee", {})
        email = invitee.get("email")
        name = invitee.get("name")
        lead = crud.upsert_lead(db, {"name": name, "email": email, "source": "calendly", "meta": {"invitee": invitee}})
        enqueue(enrich_lead_job, lead.id)
    except Exception:
        pass
    return {"ok": True}

@app.get("/leads")
def list_leads(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.db import models
    q = select(models.Lead).order_by(models.Lead.id.desc()).limit(limit).offset(offset)
    items = db.execute(q).scalars().all()
    return {"items": [{
        "id": i.id, "name": i.name, "email": i.email, "phone": i.phone, "source": i.source, "utm": i.utm, "meta": i.meta,
        "created_at": str(i.created_at)
    } for i in items]}

@app.get("/events")
def list_events(limit: int = 50, offset: int = 0, provider: str | None = None, db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.db import models
    q = select(models.EventLog).order_by(models.EventLog.id.desc()).limit(limit).offset(offset)
    if provider:
        q = q.where(models.EventLog.provider == provider)
    items = db.execute(q).scalars().all()
    return {"items": [{
        "id": i.id, "provider": i.provider, "event_type": i.event_type, "status": i.status, "error": i.error, "created_at": str(i.created_at)
    } for i in items]}

@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    from sqlalchemy import select, func
    from app.db import models
    total_leads = db.scalar(select(func.count(models.Lead.id))) or 0
    by_source = db.execute(select(models.Lead.source, func.count()).group_by(models.Lead.source)).all()
    return {"total_leads": total_leads, "by_source": dict(by_source)}
