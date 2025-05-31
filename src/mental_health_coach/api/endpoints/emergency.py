"""API endpoints for emergency contact management and crisis notifications."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.mental_health_coach.auth.security import get_current_active_user
from src.mental_health_coach.database import get_db
from src.mental_health_coach.models.user import User
from src.mental_health_coach.services.emergency_contact import EmergencyContactService

router = APIRouter()


class EmergencyContactCreate(BaseModel):
    """Schema for creating a new emergency contact."""
    
    name: str
    relationship: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False


class CrisisNotificationCreate(BaseModel):
    """Schema for creating a crisis notification."""
    
    crisis_level: str
    message: str
    contact_id: Optional[str] = None


class CrisisEventCreate(BaseModel):
    """Schema for recording a crisis event."""
    
    crisis_level: str
    conversation_id: int
    message_id: int
    action_taken: str


@router.get("/contacts")
def get_emergency_contacts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all emergency contacts for the current user.
    
    Args:
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        List: Contains emergency contacts.
    """
    emergency_service = EmergencyContactService(db=db, user=current_user)
    return emergency_service.get_emergency_contacts()


@router.post("/contacts", status_code=status.HTTP_201_CREATED)
def add_emergency_contact(
    contact_in: EmergencyContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Add a new emergency contact for the current user.
    
    Args:
        contact_in: Emergency contact creation data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: The added emergency contact.
        
    Raises:
        HTTPException: If required fields are missing.
    """
    emergency_service = EmergencyContactService(db=db, user=current_user)
    
    try:
        return emergency_service.add_emergency_contact(
            name=contact_in.name,
            relationship=contact_in.relationship,
            phone=contact_in.phone,
            email=contact_in.email,
            is_primary=contact_in.is_primary,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/notify")
def send_crisis_notification(
    notification_in: CrisisNotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Send a notification to emergency contacts during crisis.
    
    Args:
        notification_in: Crisis notification data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: Notification status.
        
    Raises:
        HTTPException: If notification fails.
    """
    emergency_service = EmergencyContactService(db=db, user=current_user)
    
    result = emergency_service.send_crisis_notification(
        crisis_level=notification_in.crisis_level,
        message=notification_in.message,
        contact_id=notification_in.contact_id,
    )
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to send notification"),
        )
    
    return result


@router.post("/events", status_code=status.HTTP_201_CREATED)
def record_crisis_event(
    event_in: CrisisEventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Record a crisis event for future reference and follow-up.
    
    Args:
        event_in: Crisis event data.
        current_user: The current authenticated user.
        db: Database session.
        
    Returns:
        Dict: The recorded crisis event.
    """
    emergency_service = EmergencyContactService(db=db, user=current_user)
    
    return emergency_service.record_crisis_event(
        crisis_level=event_in.crisis_level,
        conversation_id=event_in.conversation_id,
        message_id=event_in.message_id,
        action_taken=event_in.action_taken,
    ) 