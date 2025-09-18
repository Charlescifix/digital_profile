"""CV request schemas for validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class CVRequest(BaseModel):
    """CV request input schema."""
    
    name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    role: Optional[str] = None
    purpose: Optional[str] = None
    consent: bool
    website: str = ""  # Honeypot field
    
    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.strip()
    
    @validator("phone")
    def validate_phone(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Phone number must be at least 10 characters long")
        return v.strip()
    
    @validator("purpose")
    def validate_purpose(cls, v):
        if v and len(v) > 500:
            raise ValueError("Purpose must be less than 500 characters")
        return v
    
    @validator("consent")
    def validate_consent(cls, v):
        if not v:
            raise ValueError("Consent is required")
        return v
    
    @validator("website")
    def validate_honeypot(cls, v):
        # Honeypot should be empty
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "John Smith",
                "email": "john.smith@company.com",
                "phone": "+1-555-0123",
                "company": "Tech Corp",
                "role": "CTO",
                "purpose": "Interested in AI consulting for our fintech platform",
                "consent": True,
                "website": ""
            }
        }


class CVResponse(BaseModel):
    """CV request response schema."""
    
    success: bool
    message: str
    request_id: str
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "CV request processed successfully",
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }