"""Emergency contact models for the mental health coach application.

This module defines the database models for storing user emergency contacts.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.mental_health_coach.database import Base


class EmergencyContact(Base):
    """Model for storing user emergency contacts for crisis intervention.
    
    This model stores emergency contact information for a user that can be
    used during crisis situations.
    
    Attributes:
        id: Unique identifier for the emergency contact.
        user_id: ID of the user this contact belongs to.
        name: Name of the emergency contact.
        relationship_type: Relationship to the user (e.g., family, friend, doctor).
        phone_number: Phone number for contacting in emergencies.
        email: Email address for non-urgent communication.
        is_primary: Whether this is the primary emergency contact.
        created_at: When the contact was created.
        updated_at: When the contact was last updated.
    """
    
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="emergency_contacts") 