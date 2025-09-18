"""Lead management schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

from app.models.leads import LeadStatus, LeadSource


class LeadBase(BaseModel):
    """Base lead schema."""
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    role: Optional[str] = None
    purpose: Optional[str] = None
    source: LeadSource = LeadSource.CV_REQUEST


class LeadCreate(LeadBase):
    """Lead creation schema."""
    consent_given: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class LeadUpdate(BaseModel):
    """Lead update schema."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    purpose: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Lead response schema."""
    id: UUID
    status: LeadStatus
    notes: Optional[str] = None
    consent_given: bool
    consent_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class LeadListResponse(BaseModel):
    """Paginated lead list response."""
    leads: list[LeadResponse]
    total: int
    page: int
    size: int
    pages: int