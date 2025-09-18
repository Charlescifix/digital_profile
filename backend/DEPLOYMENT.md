# 🚀 Production Deployment Guide

Complete deployment guide for Charles Nwankpa Portfolio Backend API.

## 🎯 Quick Deploy to Railway

### 1. Prerequisites
- Railway CLI installed: `npm install -g @railway/cli`
- GitHub repository with your backend code
- CV PDF file ready for upload

### 2. Deploy Steps

```bash
# 1. Login to Railway
railway login

# 2. Create new project
railway init

# 3. Add PostgreSQL database
railway add postgresql

# 4. Deploy the API
railway up

# 5. Set environment variables (see section below)
railway variables set JWT_SECRET=your-super-secret-key

# 6. Run database migrations
railway run psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

### 3. Required Environment Variables

Set these in Railway dashboard or via CLI:

```bash
# Security (REQUIRED)
railway variables set JWT_SECRET="your-super-secret-key-256-bits"

# Email Configuration (REQUIRED)
railway variables set EMAIL_SMTP_USER="your-email@gmail.com"
railway variables set EMAIL_SMTP_PASSWORD="your-app-password"
railway variables set EMAIL_FROM="your-email@gmail.com"
railway variables set EMAIL_FROM_NAME="Charles Nwankpa"

# Application Settings
railway variables set CORS_ORIGINS='["https://charles-ai.up.railway.app"]'
railway variables set DEBUG="false"

# External Services
railway variables set CALENDLY_URL="https://calendly.com/charles-nwankpa/intro-call"
railway variables set LINKEDIN_URL="https://www.linkedin.com/in/charles-nwankpa"

# Optional: Monitoring
railway variables set SENTRY_DSN="your-sentry-dsn"
```

### 4. Upload CV File

```bash
# Connect to Railway service
railway shell

# Create CV directory and upload
mkdir -p static/cv
# Upload your CV as charles_nwankpa_cv.pdf
```

## 🐳 Docker Deployment

### Local Docker Setup

```bash
# 1. Build the image
docker build -t portfolio-api .

# 2. Run with docker-compose
docker-compose up -d

# 3. Check logs
docker-compose logs -f api

# 4. Access API
curl http://localhost:8000/health
```

### Production Docker

```bash
# 1. Build production image
docker build -t portfolio-api:prod .

# 2. Run with environment file
docker run -d \
  --name portfolio-api \
  --env-file .env.production \
  -p 8000:8000 \
  portfolio-api:prod

# 3. Run migrations
docker exec portfolio-api \
  psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

## ☁️ AWS ECS Deployment

### 1. Build and Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name portfolio-api

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t portfolio-api .
docker tag portfolio-api:latest \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/portfolio-api:latest

# Push to ECR
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/portfolio-api:latest
```

### 2. ECS Task Definition

```json
{
  "family": "portfolio-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "portfolio-api",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/portfolio-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/portfolio"
        }
      ],
      "secrets": [
        {
          "name": "JWT_SECRET",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:portfolio-jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/portfolio-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

## 🔧 Environment Configuration

### Production .env Template

```env
# Application
APP_NAME=Charles Nwankpa Portfolio API
DEBUG=false
API_PREFIX=/api

# Database (Auto-configured by Railway)
DATABASE_URL=postgresql://user:pass@host:5432/portfolio_db

# Security - GENERATE STRONG KEYS!
JWT_SECRET=your-256-bit-secret-key-change-this-immediately
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Required for CV delivery)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Charles Nwankpa

# CORS (Update with your domain)
CORS_ORIGINS=["https://charles-ai.up.railway.app","https://api.charles-ai.up.railway.app"]

# External Services
CALENDLY_URL=https://calendly.com/charles-nwankpa/intro-call
LINKEDIN_URL=https://www.linkedin.com/in/charles-nwankpa

# Files
CV_FILE_PATH=./static/cv/charles_nwankpa_cv.pdf

# Optional: Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

### Security Checklist

- [ ] **Strong JWT secret** (256-bit random string)
- [ ] **Email app passwords** (not regular password)
- [ ] **Database SSL** enabled
- [ ] **HTTPS only** in production
- [ ] **CORS origins** restricted to your domains
- [ ] **Rate limiting** enabled (3/hour default)
- [ ] **Admin password** changed from default
- [ ] **Sentry DSN** configured for error tracking

## 📊 Database Setup

### 1. Manual Migration

```bash
# Connect to database
psql $DATABASE_URL

# Run initial schema
\i migrations/001_initial_schema.sql

# Verify tables
\dt

# Check admin user
SELECT * FROM admins;
```

### 2. Default Admin User

The migration creates a default admin user:
- **Username**: `admin`
- **Password**: `admin123` ⚠️ **CHANGE IMMEDIATELY**
- **Email**: `admin@charles-ai.com`

**Change the password:**
```sql
UPDATE admins 
SET hashed_password = '$2b$12$NEW_HASHED_PASSWORD'
WHERE username = 'admin';
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoints

```bash
# Basic health
curl https://your-api-domain.railway.app/health

# Readiness (Kubernetes)
curl https://your-api-domain.railway.app/ready

# Liveness (Kubernetes)  
curl https://your-api-domain.railway.app/live
```

### Expected Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": true,
  "redis": true,
  "version": "1.0.0"
}
```

## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

**2. Email Delivery Issues**
```bash
# Test SMTP settings
railway logs --tail 100 | grep email

# Check email logs in database
railway run psql $DATABASE_URL -c "SELECT * FROM email_logs ORDER BY sent_at DESC LIMIT 10;"
```

**3. JWT Authentication Errors**
```bash
# Verify JWT_SECRET is set
railway variables get JWT_SECRET

# Check admin user exists
railway run psql $DATABASE_URL -c "SELECT username, is_active FROM admins;"
```

**4. CORS Issues**
```bash
# Check CORS_ORIGINS setting
railway variables get CORS_ORIGINS

# Verify frontend domain is included
```

### Debug Mode

Enable debug logging temporarily:
```bash
railway variables set DEBUG=true
railway logs --tail 100
```

## 📈 Performance Optimization

### Production Settings

```env
# Database
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Workers (Railway auto-scales)
WORKERS=2

# Caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Monitoring Recommendations

1. **Sentry** for error tracking
2. **DataDog/New Relic** for APM
3. **Railway Metrics** for infrastructure
4. **Custom dashboard** for business metrics

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        uses: railway/cli@v2
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service backend
```

## 🎯 Post-Deployment Checklist

- [ ] Health checks passing
- [ ] Database migrations completed
- [ ] Admin user password changed
- [ ] CV file uploaded
- [ ] Email delivery tested
- [ ] CORS configured correctly
- [ ] SSL certificate active
- [ ] Monitoring configured
- [ ] Rate limiting tested
- [ ] Backup strategy implemented

## 📞 Support

For deployment issues:

1. Check Railway logs: `railway logs --tail 100`
2. Verify environment variables: `railway variables`
3. Test database connection: `railway run psql $DATABASE_URL -c "SELECT version();"`
4. Monitor health endpoint: `curl https://your-domain/health`

---

**🚀 Ready for production** • **🔒 Secure by design** • **📊 Monitored & scalable**