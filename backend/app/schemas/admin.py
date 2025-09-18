"""Admin user schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class AdminBase(BaseModel):
    """Base admin schema."""
    email: EmailStr
    username: str
    full_name: str


class AdminCreate(AdminBase):
    """Admin creation schema."""
    password: str


class AdminUpdate(BaseModel):
    """Admin update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class AdminResponse(AdminBase):
    """Admin response schema."""
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str