# Charles Nwankpa Portfolio Backend API

> **Production-ready FastAPI backend** for managing CV requests, lead generation, and portfolio analytics.

## 🚀 Quick Start

### Development Setup

1. **Clone and setup environment:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup database:**
   ```bash
   # Create PostgreSQL database
   createdb portfolio_db
   
   # Run migrations
   psql -d portfolio_db -f migrations/001_initial_schema.sql
   ```

3. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Core Features

### ✅ CV Request Management
- **Gated CV delivery** with lead qualification
- **Spam protection** via honeypot and rate limiting
- **GDPR-compliant** data collection with consent tracking
- **Professional email delivery** with branded templates

### ✅ Lead Management System
- **Lead lifecycle tracking** (new → qualified → converted)
- **Source attribution** (CV request, Calendly, LinkedIn)
- **Admin dashboard** with full CRUD operations
- **Advanced filtering** and search capabilities

### ✅ Email Delivery
- **Automated CV delivery** via SMTP/SES
- **Professional email templates** with personalization
- **Delivery tracking** and error handling
- **Admin notifications** for new requests

### ✅ Analytics & Metrics
- **Portfolio performance** tracking
- **Lead quality analysis** by company/role
- **Conversion rate** monitoring
- **Time-based trends** and insights

### ✅ Security & Performance
- **JWT authentication** for admin access
- **Rate limiting** (3 requests/hour per IP)
- **Input validation** and sanitization
- **Structured logging** with correlation IDs

## 🔧 API Endpoints

### Public Endpoints
- `POST /api/request-cv` - Submit CV request
- `GET /health` - Health check
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe

### Admin Endpoints (🔒 Authentication Required)
- `POST /api/admin/login` - Admin authentication
- `GET /api/admin/me` - Current admin info
- `GET /api/admin/leads` - List leads (paginated)
- `GET /api/admin/leads/{id}` - Get lead details
- `PUT /api/admin/leads/{id}` - Update lead
- `DELETE /api/admin/leads/{id}` - Delete lead (GDPR)

### Analytics Endpoints (🔒 Authentication Required)
- `GET /api/analytics/dashboard` - Comprehensive dashboard
- `GET /api/analytics/leads/summary` - Lead summary stats
- `GET /api/analytics/performance` - System performance

## 📊 Database Schema

### Core Tables
```sql
-- Leads table for CV requests and contacts
leads (id, name, email, phone, company, role, purpose, source, status, ...)

-- Admin users for dashboard access  
admins (id, email, username, full_name, hashed_password, ...)

-- Email delivery tracking
email_logs (id, lead_id, recipient_email, status, sent_at, ...)

-- Analytics events
analytics_events (id, event_type, event_data, ip_address, ...)
```

### Lead Lifecycle
```
new → contacted → qualified → proposal_sent → closed_won/closed_lost
```

## 🔐 Security Features

### Input Protection
- **Honeypot spam detection**
- **Rate limiting** (3/hour per IP)
- **Input validation** and sanitization
- **SQL injection** prevention

### Authentication
- **JWT tokens** with expiration
- **Bcrypt password** hashing
- **Admin role verification**
- **Session management**

### Data Privacy
- **GDPR compliance** with consent tracking
- **Data deletion** endpoints
- **No sensitive data** in logs
- **Encrypted database** connections

## 📧 Email Configuration

### SMTP Setup (Gmail/Outlook)
```env
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### AWS SES Setup
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## 🚢 Deployment

### Railway (Recommended)
```bash
# Connect to Railway
railway login
railway link

# Deploy
railway up
```

### Docker Production
```bash
# Build image
docker build -t portfolio-api .

# Run container
docker run -p 8000:8000 --env-file .env portfolio-api
```

### Environment Variables
```env
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=your-super-secret-key
EMAIL_SMTP_USER=your-email@domain.com
EMAIL_SMTP_PASSWORD=your-password

# Optional
SENTRY_DSN=your-sentry-dsn
CORS_ORIGINS=["https://charles-ai.up.railway.app"]
```

## 📈 Monitoring

### Health Checks
- **Database connectivity** monitoring
- **Redis connection** status  
- **Email service** health
- **API response times**

### Logging
- **Structured JSON** logging
- **Request correlation** IDs
- **Error tracking** with Sentry
- **Performance metrics**

### Alerts
- **High error rates**
- **Database connection** failures
- **Email delivery** issues
- **Unusual traffic** patterns

## 🧪 Testing

### Run Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# All tests with coverage
pytest --cov=app tests/
```

### Test Coverage
- **Unit tests** for services and utilities
- **Integration tests** for API endpoints
- **Database tests** with test fixtures
- **Email delivery** mocking

## 📝 API Documentation

### Interactive Docs
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI schema**: `/openapi.json`

### Example Requests

**CV Request:**
```bash
curl -X POST "http://localhost:8000/api/request-cv" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Smith",
       "email": "john@company.com", 
       "phone": "+1-555-0123",
       "company": "Tech Corp",
       "role": "CTO",
       "purpose": "AI consulting inquiry",
       "consent": true,
       "website": ""
     }'
```

**Admin Login:**
```bash
curl -X POST "http://localhost:8000/api/admin/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "your-password"
     }'
```

## 🔧 Configuration

### Feature Flags
- **Email delivery** enable/disable
- **Admin registration** open/closed
- **Analytics collection** on/off
- **Rate limiting** adjustments

### Performance Tuning
- **Database connection** pooling
- **Redis caching** for analytics
- **Email queue** processing
- **Response compression**

## 🚀 Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring and alerts setup
- [ ] Backup strategy implemented
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Admin user created
- [ ] CV file uploaded

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with precision for Charles Nwankpa's AI Product Engineer Portfolio**  
🚀 **Production-ready** • 🔒 **Secure by design** • 📊 **Analytics-driven**