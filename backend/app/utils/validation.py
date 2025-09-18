"""Validation utilities for input sanitization and security."""

import re
from typing import Dict, Any
from fastapi import HTTPException

from app.schemas.cv_request import CVRequest


def validate_honeypot(honeypot_value: str) -> bool:
    """
    Validate honeypot field for spam protection.
    
    Args:
        honeypot_value: Value from the hidden honeypot field
        
    Returns:
        bool: True if valid (empty), False if spam detected
    """
    return honeypot_value == "" or honeypot_value is None


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_format(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid format
    """
    # Remove common separators
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check if it's a reasonable length (10-15 digits, possibly with country code)
    if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
        return False
    
    # Basic pattern check (starts with + or digit)
    pattern = r'^(\+?\d{10,15})$'
    return re.match(pattern, cleaned_phone) is not None


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input by trimming and limiting length.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized string
    """
    if not value:
        return ""
    
    # Trim whitespace and limit length
    sanitized = value.strip()[:max_length]
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    return sanitized


def validate_request_data(cv_request: CVRequest) -> None:
    """
    Comprehensive validation of CV request data.
    
    Args:
        cv_request: CV request object to validate
        
    Raises:
        HTTPException: If validation fails
    """
    
    # Validate required fields
    if not cv_request.name or len(cv_request.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters long")
    
    if not cv_request.email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    if not validate_email_format(cv_request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if not cv_request.phone:
        raise HTTPException(status_code=400, detail="Phone number is required")
    
    if not validate_phone_format(cv_request.phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Validate optional fields
    if cv_request.purpose and len(cv_request.purpose) > 500:
        raise HTTPException(status_code=400, detail="Purpose must be less than 500 characters")
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'data:text/html',  # Data URLs
        r'<iframe.*?>.*?</iframe>',  # Iframe tags
    ]
    
    all_text = f"{cv_request.name} {cv_request.email} {cv_request.phone} {cv_request.company or ''} {cv_request.role or ''} {cv_request.purpose or ''}"
    
    for pattern in suspicious_patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            raise HTTPException(status_code=400, detail="Invalid characters detected")


def validate_admin_data(admin_data: Dict[str, Any]) -> None:
    """
    Validate admin user data.
    
    Args:
        admin_data: Admin data to validate
        
    Raises:
        HTTPException: If validation fails
    """
    
    if 'email' in admin_data:
        if not validate_email_format(admin_data['email']):
            raise HTTPException(status_code=400, detail="Invalid email format")
    
    if 'username' in admin_data:
        username = admin_data['username']
        if not username or len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")
        
        # Check for valid username pattern (alphanumeric and underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, and underscores")
    
    if 'password' in admin_data:
        password = admin_data['password']
        if not password or len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Check for password complexity
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise HTTPException(status_code=400, detail="Password must contain both letters and numbers")


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if string is a valid UUID.
    
    Args:
        uuid_string: String to validate
        
    Returns:
        bool: True if valid UUID format
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(uuid_pattern, uuid_string.lower()) is not None