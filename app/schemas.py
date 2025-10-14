from pydantic import BaseModel, EmailStr, Field
from typing import Any

class LeadIn(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    source: str | None = None
    utm: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None

class LeadOut(BaseModel):
    id: int
    name: str | None
    email: EmailStr | None
    phone: str | None
    source: str | None
    utm: dict | None
    meta: dict | None

    class Config:
        from_attributes = True
