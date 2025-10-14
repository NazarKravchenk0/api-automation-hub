from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import models
from app.utils.normalize import normalize_email, normalize_phone

def upsert_lead(db: Session, lead_in: dict) -> models.Lead:
    email = normalize_email(lead_in.get("email"))
    phone = normalize_phone(lead_in.get("phone"))
    source = lead_in.get("source")

    if email:
        stmt = select(models.Lead).where(models.Lead.email == email)
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            # обновляем поля с учетом приоритета источников
            existing.name = lead_in.get("name") or existing.name
            existing.phone = phone or existing.phone
            existing.source = source or existing.source
            existing.utm = lead_in.get("utm") or existing.utm
            existing.meta = lead_in.get("meta") or existing.meta
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

    lead = models.Lead(
        name=lead_in.get("name"),
        email=email,
        phone=phone,
        source=source,
        utm=lead_in.get("utm"),
        meta=lead_in.get("meta"),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

def log_event(db: Session, provider: str, event_type: str, payload: dict, status: str = "received", error: str | None = None):
    ev = models.EventLog(provider=provider, event_type=event_type, payload=payload, status=status, error=error)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev
