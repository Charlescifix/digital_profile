"""Lead management service."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID
import structlog

from app.models.leads import LeadStatus, LeadSource

logger = structlog.get_logger(__name__)


class LeadService:
    """Service for managing leads and CV requests."""
    
    def __init__(self, database):
        self.db = database
    
    async def create_lead(self, lead_data: Dict) -> str:
        """Create a new lead record."""
        try:
            query = """
                INSERT INTO leads (
                    id, name, email, phone, company, role, purpose, source,
                    ip_address, user_agent, consent_given, consent_timestamp,
                    status, created_at, updated_at
                ) VALUES (
                    :id, :name, :email, :phone, :company, :role, :purpose, :source,
                    :ip_address, :user_agent, :consent_given, :consent_timestamp,
                    :status, :created_at, :updated_at
                )
                RETURNING id
            """
            
            values = {
                **lead_data,
                "status": LeadStatus.NEW.value,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.db.execute(query=query, values=values)
            
            logger.info("Lead created successfully", lead_id=lead_data["id"])
            return lead_data["id"]
            
        except Exception as e:
            logger.error("Error creating lead", error=str(e), lead_data=lead_data)
            raise
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict]:
        """Get lead by ID."""
        try:
            query = "SELECT * FROM leads WHERE id = :lead_id"
            result = await self.db.fetch_one(query=query, values={"lead_id": lead_id})
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error("Error fetching lead", error=str(e), lead_id=lead_id)
            raise
    
    async def get_lead_by_email(self, email: str) -> Optional[Dict]:
        """Get lead by email address."""
        try:
            query = "SELECT * FROM leads WHERE email = :email ORDER BY created_at DESC LIMIT 1"
            result = await self.db.fetch_one(query=query, values={"email": email})
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error("Error fetching lead by email", error=str(e), email=email)
            raise
    
    async def update_lead_status(self, lead_id: str, status: LeadStatus, notes: Optional[str] = None) -> bool:
        """Update lead status and notes."""
        try:
            query = """
                UPDATE leads 
                SET status = :status, notes = :notes, updated_at = :updated_at
                WHERE id = :lead_id
            """
            
            values = {
                "lead_id": lead_id,
                "status": status.value,
                "notes": notes,
                "updated_at": datetime.utcnow()
            }
            
            await self.db.execute(query=query, values=values)
            
            logger.info("Lead status updated", lead_id=lead_id, status=status.value)
            return True
            
        except Exception as e:
            logger.error("Error updating lead status", error=str(e), lead_id=lead_id)
            raise
    
    async def get_leads(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None
    ) -> Dict:
        """Get paginated list of leads with filters."""
        try:
            # Build WHERE clause
            where_conditions = []
            values = {"skip": skip, "limit": limit}
            
            if status:
                where_conditions.append("status = :status")
                values["status"] = status.value
            
            if source:
                where_conditions.append("source = :source")
                values["source"] = source.value
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM leads {where_clause}"
            total_result = await self.db.fetch_one(query=count_query, values=values)
            total = total_result["total"] if total_result else 0
            
            # Get leads
            query = f"""
                SELECT * FROM leads {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """
            
            results = await self.db.fetch_all(query=query, values=values)
            leads = [dict(row) for row in results]
            
            return {
                "leads": leads,
                "total": total,
                "page": (skip // limit) + 1,
                "size": limit,
                "pages": (total + limit - 1) // limit
            }
            
        except Exception as e:
            logger.error("Error fetching leads", error=str(e))
            raise
    
    async def get_lead_analytics(self, days: int = 30) -> Dict:
        """Get lead analytics for the specified number of days."""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status = 'qualified' THEN 1 END) as qualified_leads,
                    COUNT(CASE WHEN source = 'cv_request' THEN 1 END) as cv_requests,
                    COUNT(CASE WHEN source = 'calendly' THEN 1 END) as calendly_bookings,
                    COUNT(CASE WHEN company IS NOT NULL THEN 1 END) as with_company,
                    AVG(CASE WHEN created_at >= NOW() - INTERVAL '%s days' THEN 1 ELSE 0 END) as recent_rate
                FROM leads 
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """ % (days, days)
            
            result = await self.db.fetch_one(query=query)
            
            if result:
                return dict(result)
            return {}
            
        except Exception as e:
            logger.error("Error fetching lead analytics", error=str(e))
            raise