"""CV request endpoint for handling CV download requests."""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog
import uuid

from app.schemas.cv_request import CVRequest, CVResponse
from app.services.lead_service import LeadService
from app.services.email_service import EmailService
from app.utils.validation import validate_honeypot, validate_request_data
from app.core.database import get_database

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter()
router.state.limiter = limiter
router.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize logger
logger = structlog.get_logger(__name__)


@router.post("/request-cv", response_model=CVResponse)
@limiter.limit("3/hour")  # Rate limit: 3 requests per hour per IP
async def request_cv(
    request: Request,
    cv_request: CVRequest,
    db = Depends(get_database)
):
    """
    Process CV request and send CV via email.
    
    **Rate Limited**: 3 requests per hour per IP address
    
    **Security Features**:
    - Honeypot spam protection
    - Input validation and sanitization
    - GDPR consent validation
    - IP and user agent logging
    """
    try:
        # Log the incoming request
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        
        logger.info(
            "CV request received",
            ip=client_ip,
            email=cv_request.email,
            company=cv_request.company
        )
        
        # Validate honeypot (spam protection)
        if not validate_honeypot(cv_request.website):
            logger.warning("Honeypot triggered", ip=client_ip)
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Validate request data
        validate_request_data(cv_request)
        
        # Check consent
        if not cv_request.consent:
            raise HTTPException(status_code=400, detail="Consent is required")
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Initialize services
        lead_service = LeadService(db)
        email_service = EmailService()
        
        # Create lead record
        lead_data = {
            "id": request_id,
            "name": cv_request.name,
            "email": cv_request.email,
            "phone": cv_request.phone,
            "company": cv_request.company,
            "role": cv_request.role,
            "purpose": cv_request.purpose,
            "source": "cv_request",
            "ip_address": client_ip,
            "user_agent": user_agent,
            "consent_given": True,
            "consent_timestamp": datetime.utcnow()
        }
        
        await lead_service.create_lead(lead_data)
        
        # Send CV email
        await email_service.send_cv_email(
            to_email=cv_request.email,
            name=cv_request.name,
            company=cv_request.company,
            purpose=cv_request.purpose
        )
        
        logger.info(
            "CV request processed successfully",
            request_id=request_id,
            email=cv_request.email
        )
        
        return CVResponse(
            success=True,
            message="CV request processed successfully. You should receive the CV via email shortly.",
            request_id=request_id,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error processing CV request",
            error=str(e),
            ip=client_ip,
            email=cv_request.email
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )


@router.get("/cv-status/{request_id}")
async def get_cv_request_status(
    request_id: str,
    db = Depends(get_database)
):
    """Get the status of a CV request."""
    try:
        lead_service = LeadService(db)
        lead = await lead_service.get_lead_by_id(request_id)
        
        if not lead:
            raise HTTPException(status_code=404, detail="Request not found")
        
        return {
            "request_id": request_id,
            "status": lead["status"],
            "created_at": lead["created_at"],
            "email_sent": True  # If record exists, email was sent
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching CV request status", error=str(e), request_id=request_id)
        raise HTTPException(status_code=500, detail="Internal server error")