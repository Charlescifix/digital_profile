"""Analytics and metrics endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any

from app.schemas.common import AnalyticsResponse
from app.api.endpoints.admin import get_current_admin
from app.core.database import get_database

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """
    Get comprehensive dashboard analytics for the specified time period.
    
    **Metrics included:**
    - CV request statistics
    - Lead conversion rates  
    - Source attribution
    - Company and role analysis
    - Time-based trends
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Portfolio metrics query
        portfolio_query = """
            SELECT 
                COUNT(*) as total_requests,
                COUNT(CASE WHEN created_at >= :start_date THEN 1 END) as period_requests,
                COUNT(CASE WHEN status = 'qualified' THEN 1 END) as qualified_leads,
                COUNT(CASE WHEN status IN ('proposal_sent', 'closed_won') THEN 1 END) as converted_leads,
                COUNT(CASE WHEN source = 'cv_request' THEN 1 END) as cv_requests,
                COUNT(CASE WHEN source = 'calendly' THEN 1 END) as calendly_bookings,
                COUNT(CASE WHEN source = 'linkedin' THEN 1 END) as linkedin_leads,
                COUNT(DISTINCT email) as unique_contacts,
                COUNT(CASE WHEN company IS NOT NULL AND company != '' THEN 1 END) as with_company
            FROM leads 
            WHERE created_at >= :start_date
        """
        
        portfolio_result = await db.fetch_one(
            query=portfolio_query,
            values={"start_date": start_date}
        )
        
        # Lead quality analysis
        quality_query = """
            SELECT 
                company,
                role,
                status,
                COUNT(*) as count
            FROM leads 
            WHERE created_at >= :start_date
                AND company IS NOT NULL 
                AND company != ''
            GROUP BY company, role, status
            ORDER BY count DESC
        """
        
        quality_results = await db.fetch_all(
            query=quality_query,
            values={"start_date": start_date}
        )
        
        # Time-based trends
        trends_query = """
            SELECT 
                DATE_TRUNC('day', created_at) as date,
                COUNT(*) as daily_requests,
                COUNT(CASE WHEN source = 'cv_request' THEN 1 END) as cv_requests,
                COUNT(CASE WHEN source = 'calendly' THEN 1 END) as calendly_bookings
            FROM leads 
            WHERE created_at >= :start_date
            GROUP BY DATE_TRUNC('day', created_at)
            ORDER BY date DESC
            LIMIT 30
        """
        
        trends_results = await db.fetch_all(
            query=trends_query,
            values={"start_date": start_date}
        )
        
        # Source attribution
        source_query = """
            SELECT 
                source,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM leads 
            WHERE created_at >= :start_date
            GROUP BY source
            ORDER BY count DESC
        """
        
        source_results = await db.fetch_all(
            query=source_query,
            values={"start_date": start_date}
        )
        
        # Company types analysis
        company_types_query = """
            SELECT 
                CASE 
                    WHEN LOWER(company) LIKE '%startup%' OR LOWER(company) LIKE '%inc%' THEN 'startup'
                    WHEN LOWER(company) LIKE '%corp%' OR LOWER(company) LIKE '%ltd%' OR LOWER(company) LIKE '%llc%' THEN 'corporate'
                    WHEN LOWER(company) LIKE '%consulting%' OR LOWER(company) LIKE '%advisory%' THEN 'consulting'
                    WHEN LOWER(company) LIKE '%university%' OR LOWER(company) LIKE '%education%' THEN 'education'
                    ELSE 'other'
                END as company_type,
                COUNT(*) as count
            FROM leads 
            WHERE created_at >= :start_date
                AND company IS NOT NULL 
                AND company != ''
            GROUP BY company_type
            ORDER BY count DESC
        """
        
        company_types_results = await db.fetch_all(
            query=company_types_query,
            values={"start_date": start_date}
        )
        
        # Role analysis
        role_query = """
            SELECT 
                CASE 
                    WHEN LOWER(role) LIKE '%founder%' OR LOWER(role) LIKE '%ceo%' THEN 'founder'
                    WHEN LOWER(role) LIKE '%cto%' OR LOWER(role) LIKE '%technical%' THEN 'cto'
                    WHEN LOWER(role) LIKE '%recruiter%' OR LOWER(role) LIKE '%hr%' THEN 'recruiter'
                    WHEN LOWER(role) LIKE '%manager%' OR LOWER(role) LIKE '%director%' THEN 'management'
                    WHEN LOWER(role) LIKE '%engineer%' OR LOWER(role) LIKE '%developer%' THEN 'engineering'
                    ELSE 'other'
                END as role_category,
                COUNT(*) as count
            FROM leads 
            WHERE created_at >= :start_date
                AND role IS NOT NULL 
                AND role != ''
            GROUP BY role_category
            ORDER BY count DESC
        """
        
        role_results = await db.fetch_all(
            query=role_query,
            values={"start_date": start_date}
        )
        
        # Calculate conversion rates
        total_requests = portfolio_result["period_requests"] or 0
        qualified_leads = portfolio_result["qualified_leads"] or 0
        converted_leads = portfolio_result["converted_leads"] or 0
        
        qualification_rate = (qualified_leads / total_requests * 100) if total_requests > 0 else 0
        conversion_rate = (converted_leads / total_requests * 100) if total_requests > 0 else 0
        
        # Build response
        portfolio_metrics = {
            "cv_requests": {
                "total": portfolio_result["total_requests"],
                "this_period": portfolio_result["period_requests"],
                "qualification_rate": round(qualification_rate, 2),
                "conversion_rate": round(conversion_rate, 2)
            },
            "contact_sources": {
                source["source"]: source["count"] 
                for source in source_results
            },
            "unique_contacts": portfolio_result["unique_contacts"],
            "daily_trends": [
                {
                    "date": trend["date"].isoformat(),
                    "requests": trend["daily_requests"],
                    "cv_requests": trend["cv_requests"],
                    "calendly_bookings": trend["calendly_bookings"]
                }
                for trend in trends_results
            ]
        }
        
        lead_quality = {
            "by_company_type": {
                company_type["company_type"]: company_type["count"]
                for company_type in company_types_results
            },
            "by_role": {
                role["role_category"]: role["count"]
                for role in role_results
            },
            "top_companies": [
                {"company": item["company"], "count": item["count"], "status": item["status"]}
                for item in quality_results[:10]
            ]
        }
        
        return AnalyticsResponse(
            portfolio_metrics=portfolio_metrics,
            lead_quality=lead_quality,
            time_period=f"{days} days",
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )


@router.get("/leads/summary")
async def get_leads_summary(
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Get high-level lead summary statistics."""
    try:
        query = """
            SELECT 
                COUNT(*) as total_leads,
                COUNT(CASE WHEN status = 'new' THEN 1 END) as new_leads,
                COUNT(CASE WHEN status = 'qualified' THEN 1 END) as qualified_leads,
                COUNT(CASE WHEN status = 'closed_won' THEN 1 END) as won_leads,
                COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as this_week,
                COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as this_month
            FROM leads
        """
        
        result = await db.fetch_one(query=query)
        
        return {
            "summary": dict(result),
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate leads summary"
        )


@router.get("/performance")
async def get_performance_metrics(
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Get system performance and health metrics."""
    try:
        # Email delivery stats
        email_query = """
            SELECT 
                COUNT(*) as total_emails,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_emails,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_emails,
                AVG(CASE WHEN status = 'sent' THEN 1.0 ELSE 0.0 END) as delivery_rate
            FROM email_logs
            WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        
        email_result = await db.fetch_one(query=email_query)
        
        # Response time simulation (in production, you'd collect real metrics)
        performance_metrics = {
            "email_delivery": {
                "total_sent": email_result["total_emails"] or 0,
                "success_rate": round(float(email_result["delivery_rate"] or 0) * 100, 2),
                "failed_count": email_result["failed_emails"] or 0
            },
            "api_performance": {
                "avg_response_time": "150ms",  # This would come from monitoring
                "uptime": "99.9%",
                "error_rate": "0.1%"
            },
            "database": {
                "connection_pool": "healthy",
                "query_performance": "optimal"
            }
        }
        
        return {
            "performance": performance_metrics,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate performance metrics"
        )