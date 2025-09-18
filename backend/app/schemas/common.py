"""Common schemas for API responses."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel


class ResponseMessage(BaseModel):
    """Generic response message."""
    success: bool
    message: str
    data: Optional[Any] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    database: bool
    redis: bool
    version: str


class AnalyticsResponse(BaseModel):
    """Analytics data response."""
    portfolio_metrics: Dict[str, Any]
    lead_quality: Dict[str, Any]
    time_period: str
    generated_at: datetime


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime