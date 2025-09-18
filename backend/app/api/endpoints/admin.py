"""Admin endpoints for managing leads and system."""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.schemas.admin import LoginRequest, TokenResponse, AdminResponse
from app.schemas.leads import LeadListResponse, LeadResponse, LeadUpdate
from app.schemas.common import ResponseMessage
from app.services.lead_service import LeadService
from app.core.security import create_access_token, decode_access_token
from app.core.database import get_database
from app.models.leads import LeadStatus, LeadSource

router = APIRouter()
security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
):
    """Get current authenticated admin user."""
    try:
        payload = decode_access_token(credentials.credentials)
        admin_id = payload.get("sub")
        
        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Verify admin exists and is active
        query = "SELECT * FROM admins WHERE id = :admin_id AND is_active = true"
        admin = await db.fetch_one(query=query, values={"admin_id": admin_id})
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin user not found or inactive"
            )
        
        return dict(admin)
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.post("/login", response_model=TokenResponse)
async def admin_login(
    login_data: LoginRequest,
    db = Depends(get_database)
):
    """Admin login endpoint."""
    try:
        # Get admin by username
        query = "SELECT * FROM admins WHERE username = :username AND is_active = true"
        admin = await db.fetch_one(query=query, values={"username": login_data.username})
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password (you would implement password verification here)
        # For now, we'll use a simple check - implement proper bcrypt verification
        from app.core.security import verify_password
        
        if not verify_password(login_data.password, admin["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last login
        await db.execute(
            "UPDATE admins SET last_login = CURRENT_TIMESTAMP WHERE id = :admin_id",
            values={"admin_id": admin["id"]}
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(admin["id"])})
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin = Depends(get_current_admin)
):
    """Get current admin user information."""
    return AdminResponse(**current_admin)


@router.get("/leads", response_model=LeadListResponse)
async def get_leads(
    skip: int = 0,
    limit: int = 50,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Get paginated list of leads with optional filters."""
    try:
        lead_service = LeadService(db)
        result = await lead_service.get_leads(
            skip=skip,
            limit=min(limit, 100),  # Cap at 100 per page
            status=status,
            source=source
        )
        
        return LeadListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch leads"
        )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Get individual lead details."""
    try:
        lead_service = LeadService(db)
        lead = await lead_service.get_lead_by_id(lead_id)
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return LeadResponse(**lead)
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lead"
        )


@router.put("/leads/{lead_id}", response_model=ResponseMessage)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Update lead information."""
    try:
        lead_service = LeadService(db)
        
        # Check if lead exists
        existing_lead = await lead_service.get_lead_by_id(lead_id)
        if not existing_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Build update query dynamically
        update_fields = []
        values = {"lead_id": lead_id, "updated_at": "CURRENT_TIMESTAMP"}
        
        if lead_update.name is not None:
            update_fields.append("name = :name")
            values["name"] = lead_update.name
        
        if lead_update.email is not None:
            update_fields.append("email = :email")
            values["email"] = lead_update.email
        
        if lead_update.phone is not None:
            update_fields.append("phone = :phone")
            values["phone"] = lead_update.phone
        
        if lead_update.company is not None:
            update_fields.append("company = :company")
            values["company"] = lead_update.company
        
        if lead_update.role is not None:
            update_fields.append("role = :role")
            values["role"] = lead_update.role
        
        if lead_update.purpose is not None:
            update_fields.append("purpose = :purpose")
            values["purpose"] = lead_update.purpose
        
        if lead_update.status is not None:
            update_fields.append("status = :status")
            values["status"] = lead_update.status.value
        
        if lead_update.notes is not None:
            update_fields.append("notes = :notes")
            values["notes"] = lead_update.notes
        
        if not update_fields:
            return ResponseMessage(
                success=True,
                message="No changes to update"
            )
        
        update_query = f"""
            UPDATE leads 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :lead_id
        """
        
        await db.execute(query=update_query, values=values)
        
        return ResponseMessage(
            success=True,
            message="Lead updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lead"
        )


@router.delete("/leads/{lead_id}", response_model=ResponseMessage)
async def delete_lead(
    lead_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_database)
):
    """Delete a lead (GDPR compliance)."""
    try:
        # Check if lead exists
        lead_service = LeadService(db)
        existing_lead = await lead_service.get_lead_by_id(lead_id)
        
        if not existing_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Delete lead and related data
        await db.execute(
            "DELETE FROM leads WHERE id = :lead_id",
            values={"lead_id": lead_id}
        )
        
        return ResponseMessage(
            success=True,
            message="Lead deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete lead"
        )