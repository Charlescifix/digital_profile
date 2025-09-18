# Charles Nwankpa Portfolio Backend Specification

## Overview

Backend API system to support the Charles Nwankpa AI Product Engineer portfolio, handling CV requests, contact management, chat interactions, and analytics. Built for production deployment with enterprise-grade security and performance.

## Core Requirements

### 1. CV Request Management System

**Endpoint**: `POST /api/request-cv`

**Purpose**: Handle gated CV requests with lead qualification and email delivery

**Request Schema**:
```json
{
  "name": "string (required)",
  "email": "string (required, email format)",
  "phone": "string (required)",
  "company": "string (optional)",
  "role": "string (optional)",
  "purpose": "string (optional, max 500 chars)",
  "consent": "boolean (required, must be true)",
  "website": "string (honeypot, must be empty)"
}
```

**Response Schema**:
```json
{
  "success": true,
  "message": "CV request processed successfully",
  "requestId": "uuid",
  "timestamp": "ISO 8601"
}
```

**Business Logic**:
- Validate required fields and email format
- Check honeypot field (reject if filled)
- Store lead data with timestamp
- Trigger email delivery with CV attachment
- Log request for analytics
- Rate limiting: 3 requests per IP per hour
- GDPR compliance logging

### 2. Contact & Lead Management

**Database Schema - Leads Table**:
```sql
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  company VARCHAR(255),
  role VARCHAR(255),
  purpose TEXT,
  source VARCHAR(50) DEFAULT 'cv_request',
  ip_address INET,
  user_agent TEXT,
  consent_given BOOLEAN NOT NULL DEFAULT false,
  consent_timestamp TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) DEFAULT 'new',
  notes TEXT
);

CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_leads_status ON leads(status);
```

### 3. Email Delivery System

**Service**: Automated CV delivery via email

**Requirements**:
- Professional email template with branding
- CV attachment (PDF, max 2MB)
- Delivery confirmation tracking
- Bounce handling and retry logic
- Email template personalization

**Email Template Structure**:
```
Subject: Charles Nwankpa - AI Product Engineer CV

Dear [Name],

Thank you for your interest in my AI/ML engineering services.

As requested, please find my CV attached. This document outlines my experience in:
- Production ML/AI systems
- RAG architecture and LLM implementation  
- Enterprise-grade solution development
- Strategic AI consulting

Next Steps:
- Book a discovery call: https://calendly.com/charles-nwankpa/intro-call
- Connect on LinkedIn: https://linkedin.com/in/charles-nwankpa
- Explore my projects: https://charles-ai.up.railway.app

Best regards,
Charles Nwankpa
AI Product Engineer
```

### 4. Analytics & Metrics

**Endpoint**: `GET /api/admin/analytics`

**Metrics to Track**:
```json
{
  "portfolio_metrics": {
    "cv_requests": {
      "total": 150,
      "this_month": 23,
      "conversion_rate": 0.12
    },
    "page_views": {
      "total": 1250,
      "unique_visitors": 890,
      "bounce_rate": 0.34
    },
    "contact_sources": {
      "cv_request": 120,
      "calendly_direct": 45,
      "linkedin": 30
    }
  },
  "lead_quality": {
    "by_company_type": {
      "startup": 45,
      "enterprise": 32,
      "consulting": 28
    },
    "by_role": {
      "founder": 35,
      "cto": 28,
      "recruiter": 22,
      "other": 25
    }
  }
}
```

### 5. Admin Dashboard APIs

**Authentication**: JWT-based admin authentication

**Endpoints**:
- `GET /api/admin/leads` - Paginated lead list with filters
- `GET /api/admin/leads/{id}` - Individual lead details
- `PUT /api/admin/leads/{id}` - Update lead status/notes
- `GET /api/admin/analytics` - Portfolio performance metrics
- `GET /api/admin/email-logs` - Email delivery tracking

### 6. Chat Integration (Future Enhancement)

**Endpoint**: `POST /api/chat`

**Purpose**: Intelligent chat responses and lead capture

**Features**:
- RAG-powered responses about Charles's experience
- Context-aware conversation handling
- Automatic lead capture during conversations
- Integration with OpenAI GPT-4 or Claude

## Technical Architecture

### Recommended Stack

**Backend Framework**: FastAPI (Python)
- High performance async/await
- Automatic API documentation
- Excellent validation with Pydantic
- Perfect fit for AI/ML integration

**Database**: PostgreSQL
- ACID compliance for lead data
- JSON columns for flexible analytics
- Strong ecosystem and tooling

**Email Service**: AWS SES or SendGrid
- Professional deliverability
- Tracking and analytics
- Template management

**File Storage**: AWS S3
- CV storage and versioning
- CDN distribution
- Secure access controls

**Deployment**: Docker + AWS ECS/Railway
- Container-based deployment
- Auto-scaling capabilities
- Easy CI/CD integration

### Security Implementation

**Data Protection**:
```python
# Environment variables
DATABASE_URL = "postgresql://..."
JWT_SECRET = "cryptographically-secure-key"
EMAIL_API_KEY = "email-service-key"
CORS_ORIGINS = ["https://charles-ai.up.railway.app"]

# Security headers
security_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000"
}
```

**Rate Limiting**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/request-cv")
@limiter.limit("3/hour")
async def request_cv(request: Request, cv_request: CVRequest):
    # Implementation
```

### GDPR Compliance

**Data Handling**:
- Explicit consent logging with timestamps
- Right to erasure implementation
- Data portability (export functionality)
- Privacy policy integration
- Retention policy (auto-delete after 2 years)

**Compliance Endpoints**:
- `DELETE /api/privacy/delete-data` - Data erasure request
- `GET /api/privacy/export-data` - Data export request
- `POST /api/privacy/consent-withdraw` - Withdraw consent

## API Documentation

### Example FastAPI Implementation Structure

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import asyncpg
import smtplib
from datetime import datetime
import uuid

app = FastAPI(title="Charles Nwankpa Portfolio API")

# Models
class CVRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    company: str = None
    role: str = None
    purpose: str = None
    consent: bool
    website: str = ""  # Honeypot

class CVResponse(BaseModel):
    success: bool
    message: str
    requestId: str
    timestamp: datetime

# Database connection
async def get_db():
    return await asyncpg.connect(DATABASE_URL)

# Core endpoint
@app.post("/api/request-cv", response_model=CVResponse)
async def request_cv(cv_request: CVRequest):
    # Validation
    if not cv_request.consent:
        raise HTTPException(400, "Consent required")
    
    if cv_request.website:  # Honeypot check
        raise HTTPException(400, "Invalid request")
    
    # Store lead
    lead_id = str(uuid.uuid4())
    db = await get_db()
    
    await db.execute("""
        INSERT INTO leads (id, name, email, phone, company, role, purpose, consent_given)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """, lead_id, cv_request.name, cv_request.email, cv_request.phone,
        cv_request.company, cv_request.role, cv_request.purpose, True)
    
    # Send email with CV
    await send_cv_email(cv_request.email, cv_request.name)
    
    return CVResponse(
        success=True,
        message="CV request processed successfully",
        requestId=lead_id,
        timestamp=datetime.utcnow()
    )

async def send_cv_email(email: str, name: str):
    # Email implementation with CV attachment
    pass
```

### Deployment Configuration

**Docker Configuration** (`Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables**:
```env
DATABASE_URL=postgresql://user:password@localhost/portfolio
EMAIL_API_KEY=your_email_service_key
JWT_SECRET=your_jwt_secret
CORS_ORIGINS=https://charles-ai.up.railway.app
CV_FILE_PATH=/app/static/charles_nwankpa_cv.pdf
```

## Integration Points

### Frontend Integration

**CV Request Form Handler**:
```javascript
// Update existing frontend code
const REQUEST_CV_ENDPOINT = 'https://api.charles-ai.up.railway.app/api/request-cv';

async function submitCv(e) {
    e.preventDefault();
    const form = e.target;
    const data = Object.fromEntries(new FormData(form));
    
    try {
        const res = await fetch(REQUEST_CV_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!res.ok) throw new Error('Failed to submit request');
        
        const result = await res.json();
        showSuccessMessage(result.message);
        
    } catch (err) {
        showErrorMessage('Failed to process request. Please try again.');
    }
}
```

### Analytics Integration

**Google Analytics 4 Events**:
```javascript
// Track CV requests
gtag('event', 'cv_request_submitted', {
    'event_category': 'lead_generation',
    'event_label': 'cv_download',
    'value': 1
});

// Track successful submissions
gtag('event', 'cv_request_success', {
    'event_category': 'conversion',
    'event_label': 'qualified_lead'
});
```

## Performance Requirements

- **Response Time**: < 200ms for CV requests
- **Availability**: 99.9% uptime
- **Scalability**: Handle 1000+ requests/hour
- **Email Delivery**: < 30 seconds average
- **Database**: Connection pooling for concurrent requests

## Monitoring & Observability

**Health Checks**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "database": await check_db_connection(),
        "email_service": await check_email_service()
    }
```

**Logging Strategy**:
- Structured JSON logging
- Request/response correlation IDs  
- Error tracking with Sentry
- Performance monitoring with DataDog/New Relic

## Future Enhancements

1. **AI Chat Integration**: RAG-powered chatbot with Charles's knowledge base
2. **Calendar Integration**: Direct Calendly booking API integration
3. **CRM Integration**: Sync leads with HubSpot/Salesforce
4. **A/B Testing**: Form variants and conversion optimization
5. **Multi-language Support**: Internationalization for global reach
6. **Advanced Analytics**: Funnel analysis and lead scoring

---

**Estimated Development Timeline**: 2-3 weeks for MVP, 4-6 weeks for full implementation

**Estimated Cost**: $50-100/month for hosting and services (Railway + AWS SES + database)