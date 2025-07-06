import re
from typing import Dict, List, Any

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def validate_time_format(time_str: str) -> bool:
    """Validate time format (HH:MM)"""
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))

def validate_course_code(code: str) -> bool:
    """Validate course code format"""
    # Allow alphanumeric codes with optional dashes/spaces
    pattern = r'^[A-Z0-9\-\s]{2,20}$'
    return bool(re.match(pattern, code.upper()))

def validate_room_capacity(capacity: Any) -> bool:
    """Validate room capacity"""
    try:
        cap = int(capacity)
        return cap > 0 and cap <= 1000
    except (ValueError, TypeError):
        return False

def validate_required_fields(data: Dict, required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty"""
    errors = []
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            errors.append(f"{field.replace('_', ' ').title()} is required")
    return errors

def sanitize_input(text: str) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(text))
    return sanitized.strip()
