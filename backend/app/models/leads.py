"""Lead model for CV requests and contact management."""

from sqlalchemy import Column, String, Text, Boolean, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadSource(str, enum.Enum):
    """Lead source enumeration."""
    CV_REQUEST = "cv_request"
    CALENDLY = "calendly"
    LINKEDIN = "linkedin"
    REFERRAL = "referral"
    DIRECT = "direct"
    OTHER = "other"


class Lead(Base):
    """Lead model for storing contact information and CV requests."""
    
    __tablename__ = "leads"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Contact information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    company = Column(String(255), nullable=True)
    role = Column(String(255), nullable=True)
    
    # Request details
    purpose = Column(Text, nullable=True)
    source = Column(Enum(LeadSource), default=LeadSource.CV_REQUEST, nullable=False)
    
    # Technical tracking
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Consent and compliance
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Lead management
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', email='{self.email}', status='{self.status}')>"