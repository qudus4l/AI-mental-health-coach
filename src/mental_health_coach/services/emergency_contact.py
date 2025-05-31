"""Emergency contact service for crisis situations.

This module provides functionality for managing emergency contacts and
sending notifications during crisis situations.
"""

from typing import Dict, List, Optional, Any, Tuple
import datetime
from sqlalchemy.orm import Session

from src.mental_health_coach.models.user import User
from src.mental_health_coach.models.conversation import Conversation, Message


class EmergencyContact:
    """Emergency contact information.
    
    Attributes:
        name: Name of the emergency contact.
        relationship: Relationship to the user.
        phone: Phone number for SMS or voice contact.
        email: Email address for email contact.
        is_primary: Whether this is the primary emergency contact.
    """
    
    def __init__(
        self,
        name: str,
        relationship: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        is_primary: bool = False,
    ) -> None:
        """Initialize an emergency contact.
        
        Args:
            name: Name of the emergency contact.
            relationship: Relationship to the user.
            phone: Phone number for SMS or voice contact.
            email: Email address for email contact.
            is_primary: Whether this is the primary emergency contact.
        """
        self.name = name
        self.relationship = relationship
        self.phone = phone
        self.email = email
        self.is_primary = is_primary


class EmergencyContactService:
    """Service for managing emergency contacts and crisis notifications.
    
    This service provides functionality for storing and retrieving
    emergency contacts and sending notifications during crisis situations.
    
    Attributes:
        db: Database session.
        user: User to manage emergency contacts for.
    """
    
    def __init__(self, db: Session, user: User) -> None:
        """Initialize the emergency contact service.
        
        Args:
            db: Database session.
            user: User to manage emergency contacts for.
        """
        self.db = db
        self.user = user
        
    def get_emergency_contacts(self) -> List[Dict[str, Any]]:
        """Get all emergency contacts for the user.
        
        Returns:
            List of emergency contacts as dictionaries.
        """
        # In a real implementation, this would query from a database table
        # For now, we'll return mock data for demonstration
        
        # Mock data - in a real app, this would come from a database table
        mock_contacts = [
            EmergencyContact(
                name="Jane Doe",
                relationship="Partner",
                phone="+1234567890",
                email="jane@example.com",
                is_primary=True,
            ),
            EmergencyContact(
                name="John Smith",
                relationship="Therapist",
                phone="+1987654321",
                email="john@therapy.example.com",
                is_primary=False,
            ),
        ]
        
        # Convert to dictionaries
        contacts = []
        for contact in mock_contacts:
            contacts.append({
                "name": contact.name,
                "relationship": contact.relationship,
                "phone": contact.phone,
                "email": contact.email,
                "is_primary": contact.is_primary,
            })
        
        return contacts
    
    def add_emergency_contact(
        self,
        name: str,
        relationship: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        is_primary: bool = False,
    ) -> Dict[str, Any]:
        """Add a new emergency contact for the user.
        
        Args:
            name: Name of the emergency contact.
            relationship: Relationship to the user.
            phone: Phone number for SMS or voice contact.
            email: Email address for email contact.
            is_primary: Whether this is the primary emergency contact.
            
        Returns:
            Dictionary containing the added contact information.
            
        Raises:
            ValueError: If neither phone nor email is provided.
        """
        # Validate that at least one contact method is provided
        if not phone and not email:
            raise ValueError("At least one contact method (phone or email) must be provided")
        
        # In a real implementation, this would add to a database table
        # For now, we'll return a mock response for demonstration
        
        return {
            "name": name,
            "relationship": relationship,
            "phone": phone,
            "email": email,
            "is_primary": is_primary,
        }
    
    def send_crisis_notification(
        self,
        crisis_level: str,
        message: str,
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a notification to emergency contacts during crisis.
        
        Args:
            crisis_level: Severity of the crisis (low, medium, high).
            message: Message to send to the emergency contact.
            contact_id: Optional specific contact to notify. If None, notifies primary.
            
        Returns:
            Dictionary containing the notification status.
        """
        # In a real implementation, this would send an actual notification
        # For now, we'll log the notification and return a mock response
        
        # Get contacts
        contacts = self.get_emergency_contacts()
        
        # Determine which contact to notify
        contact_to_notify = None
        if contact_id:
            # Find the specific contact (mock implementation)
            contact_to_notify = next((c for c in contacts if c["name"] == contact_id), None)
        else:
            # Use primary contact
            contact_to_notify = next((c for c in contacts if c["is_primary"]), None)
        
        if not contact_to_notify:
            return {
                "status": "error",
                "message": "No emergency contact available",
            }
        
        # Log the notification (in a real implementation, this would send the notification)
        print(f"EMERGENCY NOTIFICATION: {crisis_level} crisis")
        print(f"To: {contact_to_notify['name']} ({contact_to_notify['relationship']})")
        print(f"Message: {message}")
        
        # Return success response
        return {
            "status": "success",
            "contact": contact_to_notify["name"],
            "method": "phone" if contact_to_notify["phone"] else "email",
            "timestamp": datetime.datetime.utcnow(),
        }
    
    def record_crisis_event(
        self,
        crisis_level: str,
        conversation_id: int,
        message_id: int,
        action_taken: str,
    ) -> Dict[str, Any]:
        """Record a crisis event for future reference and follow-up.
        
        Args:
            crisis_level: Severity of the crisis (low, medium, high).
            conversation_id: ID of the conversation containing the crisis.
            message_id: ID of the specific message indicating crisis.
            action_taken: Description of the intervention taken.
            
        Returns:
            Dictionary containing the recorded crisis event.
        """
        # In a real implementation, this would add to a database table
        # For now, we'll return a mock response for demonstration
        
        return {
            "id": "mock-crisis-event-id",
            "user_id": self.user.id,
            "crisis_level": crisis_level,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "action_taken": action_taken,
            "timestamp": datetime.datetime.utcnow(),
            "requires_followup": crisis_level in ["medium", "high"],
            "followup_scheduled": None,
        } 